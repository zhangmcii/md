pandas

### 希望处理年龄已知的乘客数据。

> 获取非空元素使用notna()函数。     !='NaN'没有用
> 
> 获取空值元素使用isna()函数

     age_no_na = titanic[titanic["Age"].notna()]

### 获取A列非空并且B列空值的

    not_nan_ner_back = d[(d['A'].notna())&(d['B'].isna())]

### 输出结果不展示行索引？

    # r是Series或DataFrame
    print(r.to_string(index=False))

### 改变行索引起始值？

    df.index = range(1,len(df)+1)



### 对A列的元素执行自定义函数，但是这个自定义函数中需要用到该元素同一行B列的元素，再将结果写到C列同行的元素，最后将新的datafame修改写会原文件，该怎么做？

- 定义自定义函数custom_func()

- 应用函数并写入C列：用`apply`按行应用函数结果写入C列

- 将新文件写入原文件或新文件
  
      import pandas as pd
      
      df = pd.read_excel('file_path','Sheet1')
      
      def custom_func(row):
      
          a_value = row['A']
      
          b_value = row['B']
      
          return a_value + b_value
      
      
      # 这里每行的计算结果会直接赋值给df['C']的同行位置。
      df['C'] = df.apply(custom_func, axis=1)
      
      
      df.to_excel('new_excel.xlsx', index=False)
      



### 将修改的df写进excel。

> 建议另存为新文件。
> 
> 如果选择覆盖原文件，原文件的格式会被清除，仅保留数据内容。

    # 建议设置index=False，否则第一列是序号。而一般Excel序号是在侧边栏自动显示的
    d.to_excel('result.xlsx', index=False)


