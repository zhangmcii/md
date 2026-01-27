# urllib.parse --- 将 URL 解析为组件
urllib.parse 模块定义的函数可分为两个主要门类: URL 解析和 URL 转码

##  URL 解析
URL 解析函数用于将一个 URL 字符串分割成其组成部分，或者将 URL 的多个部分组合成一个 URL 字符串。

### urlparse():
将一个 URL 解析为六个部分，返回一个包含 6 项的 named tuple

### parse_qs():
解析以字符串参数形式给出的查询字符串

## _replace()
将返回一个新的 ParseResult 对象来将指定字段替换为新的值。


## URL 转码
 URL 转码函数的功能是接收程序数据并通过对特殊字符进行转码并正确编码非 ASCII 文本来将其转为可以安全地用作 URL 组成部分的形式。



举例： 对查询参数进行ENCODE编码
```python
auth_url = "https://github.com/login/oauth/authorize?client_id=102823913&redirect_uri=http://172.18.66.166:8082/auth/oauth/callback/github&response_type=code&scope=get_user_info&state=38f78553-40a3-43d3-86ff-0f0254b71f34"

# 解析成组件部分
parsed = urlparse(auth_url)
# 对查询参数解析成字典
query_params = parse_qs(parsed.query, keep_blank_values=True)
# 对查询参数进行encode
encoded_query = urlencode(query_params, doseq=True)
# 用encode后的查询参数 替换 原查询参数
encoded_url = parsed._replace(query=encoded_query).geturl()
```

输出：
```
https://github.com/login/oauth/authorize?response_type=code&client_id=Ov23ctUlscDT8wuxPXX4&redirect_uri=http%3A%2F%2F172.18.66.166%3A8082%2Fauth%2Foauth%2Fcallback%2Fgithub&state=6f8a9645-e3f7-4004-bc28-0a54c6a51414&scope=user
```