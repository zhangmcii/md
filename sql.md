# LIKE

转义字符：
若要匹配一个包含通配符（例如 10%）的字符串，你需要指示 LIKE 运算符将 10% 中的 % 视为普通字符。
为此，你需要在 `ESCAPE` 子句后明确指定一个转义符
～～～
value LIKE '%10!%%' ESCAPE '!'
～～～

在此示例中，! 是一个转义字符。它指示 LIKE 运算符将 10% 中的 % 视为一个普通字符。

# NULL

NULL在 SQL 中是特殊的。NULL表示数据未知、不适用，甚至不存在。换言之，NULL表示数据库中的缺失数据。

NULL是特殊的，因为任何与 NULL 的比较永远不会导致真或假，而是第三个逻辑结果：未知。
以下语句返回 NULL
~~~
SELECT NULL = 5;
~~~


要确定表达式或列是否为 NULL，请使用 IS NULL 运算符
~~~
expression IS NULL
~~~


# 别名

## 列别名

以下示例展示了如何使用列别名
~~~
SELECT
	inv_no AS invoice_no,
	amount,
	due_date AS 'Due date',
	cust_no 'Customer No'
FROM
	invoices;
~~~
此查询有多个列别名

invoice_no 是 inv_no 列的列别名。
'Due date' 是 due_date 列的列别名。由于别名包含空格，因此你必须将其放在单引号 (') 或双引号 (") 中。
'Customer no' 是 cust_no 列的别名。请注意，它没有 AS 关键字。


列别名常见的错误
由于你在 SELECT 子句中给列分配别名，因此你只能在执行 SELECT 子句后计算的子句中引用别名。
以下查询将导致错误
~~~
SELECT 
    first_name, 
    last_name, 
    salary * 1.1 AS new_salary
FROM
    employees
WHERE new_salary > 5000
~~~~
错误
```
Unknown column 'new_salary' in 'where clause'
```
原因：在此 SELECT 语句中，数据库按以下顺序计算子句：  FROM > WHERE > SELECT
当它计算 WHERE 子句时，数据库没有关于 new_salary 列别名的信息。所以它发出一个错误。


不过，以下查询可以正常运行
```
SELECT 
    first_name, 
    last_name, 
    salary * 1.1 AS new_salary
FROM
    employees
ORDER BY new_salary;
Code language: SQL (Structured Query Language) (sql)
```
在此示例中，数据库按以下顺序计算查询的子句： FROM > SELECT > ORDER BY


# JOIN
## inner join 
当表 A 使用内连接与表 B 连接时
对于表 A 中的每一行，内联接子句都会在表 B 中查找匹配行。如果找到匹配项，则会将其包含在最终结果集中。

## left join



## right join
左连接将返回来自左表的全部行，无论在右表中是否存在匹配行。

## self join


## full (outer) join


# 子查询
置于括号内的查询称为子查询。包含子查询的查询称为外部查询或外部选择。
要执行查询，首先，数据库系统必须执行子查询，并将括号内的子查询替换为子查询的结果

可以在许多地方使用子查询，例如

- 与IN或NOT IN运算符一起使用
- 与比较运算符一起使用
- 与EXISTS或NOT EXISTS运算符一起使用
- 与ANY或ALL运算符一起使用
- 在FROM子句中
- 在SELECT子句中


## 普通子查询
外部查询的价值取决于子查询。但是，子查询并不依赖于外部查询

找到薪水高于所有员工平均薪水的员工
~~~
SELECT 
    employee_id, 
    first_name, 
    last_name, 
    salary
FROM
    employees
WHERE
    salary > (SELECT 
            AVG(salary)
        FROM
            employees);
~~~

## 相关子查询
使用外部查询中的值执行的子查询。
此外，对于外部查询选择的每一行，相关子查询可能被评估一次。因此，使用相关子查询的查询可能很慢。

找到工资高于其所在部门员工平均工资的所有员工
~~~
SELECT 
    employee_id, 
    first_name, 
    last_name, 
    salary, 
    department_id
FROM
    employees e
WHERE
    salary > (SELECT 
            AVG(salary)
        FROM
            employees
        WHERE
            department_id = e.department_id)
ORDER BY 
    department_id , 
    first_name , 
    last_name;

~~~

这里的相关子查询为：
~~~~
SELECT
    AVG( list_price )
FROM
    products
WHERE
    category_id = p.category_id
~~~~
对于每个员工，数据库系统必须执行一次相关子查询，以计算当前员工所在部门员工的平均工资。


# ALL
ALL 操作符是一个 逻辑操作符，用于将单个值与 子查询返回的单列值集合进行比较.
ALL 操作符必须位于 比较操作符（如 >、>=、<、<=、<>、=）前面，后面跟着 子查询。一些数据库系统（如 Oracle）允许用字面值列表代替子查询。
x ≤ ALL(S)  ⇔  x ≤ MIN(S)


# ANY
定义同ALL
集合里只要有一个值满足 x <= 这个值，就返回 TRUE。不要求每个值都满足。
x ≤ ANY(S)  ⇔  x ≤ MAX(S)

x <= ANY (…)	 列 c 中的值必须小于或等于集合中的最大值才能评估为 true 
为什么不是小于或等于集合中的最小值？

为什么最大值是“关键”
注意观察：
当 x 比 最大值 还大时 → 不可能有值满足
当 x ≤ 最大值时 → 至少能找到 那个最大值 来满足比较

所以：x ≤ ANY(S)  ⇔  x ≤ MAX(S)


# EXISTS
EXISTS运算符允许您指定一个子查询来测试行的存在性
~~~
EXISTS (subquery)
~~~
如果子查询包含任何行，EXISTS运算符将返回真。否则，它将返回假。

EXISTS运算符一旦找到一行将会立即终止查询处理，因此，您可以利用EXISTS运算符这一特性来提高查询性能。

## EXISTS和NULL
如果子查询返回NULL，EXISTS运算符仍然将返回结果集。这是因为EXISTS运算符只检查子查询返回的行是否存在。该行是否为NULL并不重要。


# UNION
将两个或多个 SELECT 语句的结果集合并为单个结果集(没有重复)

要保留结果集中的重复行，可以使用 UNION ALL 运算符。


# INTERSECT
获取两个或多个查询的交集。
与 UNION 运算符 一样，INTERSECT 运算符会从最终结果集中移除重复行。


以下语句说明了如何使用 INTERSECT 运算符查找两个结果集的交集。
~~~
SELECT
	id
FROM
	a 
INTERSECT
SELECT
	id
FROM
	b;
~~~

(MySQL不提供 INTERSECT 运算符)
可哟使用 INNER JOIN 子句模拟 SQL INTERSECT 运算符
~~~
SELECT
	a.id
FROM
	a
INNER JOIN b ON b.id = a.id
~~~

# MINUS
从一个结果集中减去另一个结果集。返回第一个查询而不具有第二个查询产生但唯一的行。

下面说明了减号运算符的语法。
~~~
SELECT
	id
FROM
	A 
MINUS 
SELECT
	id
FROM
	B;
~~~