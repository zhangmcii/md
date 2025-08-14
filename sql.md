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


# GROUP BY
根据一列或多列的值对行进行分组。它为每组返回一行。
## 对一列进行分组
~~~
SELECT 
    department_id
FROM 
    employees
GROUP BY 
    department_id;
~~~
本例中
首先，SELECT 从句返回 employees 表的 department_id 列中的所有值。
其次，GROUP BY 从句将所有值分组到各组中。

employees 表的 department_id 列有 40 行，包括重复的 department_id 值。然而，GROUP BY 将这些值分组到各组中。

## 多列进行分组
如何根据 department_id 和 job_id 列中的值对员工进行分组？
~~~
GROUP BY department_id, job_id
~~~
此子句将按 department_id 和 job_id 列中具有相同值的全部员工分到一组中。

下面的语句按 department_id 和 job_id 列中具有相同值的全部行分到同一组中，然后返回这些组中每个组的行。
~~~
SELECT 
    department_name,
    job_title,
    COUNT(employee_id)
FROM
    employees e
        INNER JOIN
    departments d ON d.department_id = e.department_id
        INNER JOIN
    jobs j ON j.job_id = e.job_id
GROUP BY department_name , 
         job_title;
Code language: SQL (Structured Query Language) (sql)
~~~
结果：
~~~
+------------------+---------------------------------+--------------------+
| department_name  | job_title                       | COUNT(employee_id) |
+------------------+---------------------------------+--------------------+
| Accounting       | Accounting Manager              |                  1 |
| Accounting       | Public Accountant               |                  1 |
| Administration   | Administration Assistant        |                  1 |
| Executive        | Administration Vice President   |                  2 |
| Executive        | President                       |                  1 |
| Finance          | Accountant                      |                  5 |
| Finance          | Finance Manager                 |                  1 |
| Human Resources  | Human Resources Representative  |                  1 |
| IT               | Programmer                      |                  5 |
| Marketing        | Marketing Manager               |                  1 |
| Marketing        | Marketing Representative        |                  1 |
| Public Relations | Public Relations Representative |                  1 |
| Purchasing       | Purchasing Clerk                |                  5 |
| Purchasing       | Purchasing Manager              |                  1 |
| Sales            | Sales Manager                   |                  2 |
| Sales            | Sales Representative            |                  4 |
| Shipping         | Shipping Clerk                  |                  2 |
| Shipping         | Stock Clerk                     |                  1 |
| Shipping         | Stock Manager                   |                  4 |
+------------------+---------------------------------+--------------------+
19 rows in set (0.00 sec)
~~~


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


# INSERT 
从其他表复制行
可以使用 INSERT 语句从一张或多张表中查询数据，并将其插入到另一张表中，如下所示
~~~
INSERT INTO table1 (column1, column2) 
SELECT
	column1,
	column2
FROM
	table2
WHERE
	condition1;
~~~

有一个名为 dependents_archive 的表，其结构与 dependents 表的结构相同。将从 dependents 表中复制所有行到 dependents_archive 表中
~~~
INSERT INTO dependents_archive 
SELECT
	*
FROM
	dependents;
~~~

# CASE
允许你向 SQL 语句添加 IF THEN ELSE 逻辑。
## 简单case表达式
~~~
CASE expression
WHEN when_expression_1 THEN
	result_1
WHEN when_expression_2 THEN
	result_2
WHEN when_expression_3 THEN
	result_3
...
ELSE
	else_result
END
~~~
CASE 表达式使用相等运算符 (=) 将表达式与表达式集（when_expression_1、when_expression_2、when_expression_3、…）进行比较


## 搜索表达式
~~~
CASE
WHEN boolean_expression_1 THEN
	result_1
WHEN boolean_expression_2 THEN
	result_2
WHEN boolean_expression_3 THEN
	result_3
ELSE
	else_result
END;
~~~
使用其他比较运算符（例如大于 (>)、小于 (<) 等）


例子：
~~~
SELECT 
    first_name,
    last_name,
    CASE
        WHEN salary < 3000 THEN 'Low'
        WHEN salary >= 3000 AND salary <= 5000 THEN 'Average'
        WHEN salary > 5000 THEN 'High'
    END evaluation
FROM
    employees;
~~~
如果工资低于 3000，CASE 表达式返回“低”。如果工资在 3000 到 5000 之间，则返回“一般”。如果工资大于 5000，CASE 表达式返回“高”。


# 视图
视图如同通过执行查询而生成的虚拟表格。关系数据库管理系统 (RDBMS) 将视图作为命名的 SELECT 存储在数据库目录中。
无论何时发出包含视图名称的 SELECT 语句，RDBMS 都将执行视图定义查询以创建虚拟表格。然后该虚拟表格用作查询的源表格。

为什么要使用视图？
1.允许您将复杂查询存储在数据库中。
2.帮助您为特定用户组打包数据。例如，您可以创建财务部门员工工资数据的视图。
3.帮助维护数据库安全性。您可以创建视图仅显示必要数据，并授予用户访问该视图的权限，而不必向用户授予访问数据库表格的权限。

创建视图,请如下使用 CREATE VIEW 语句
~~~
CREATE VIEW view_name 
AS
SELECT-statement
~~~
默认情况下，视图中列的名称与 SELECT 语句中指定的列相同。 如果您想在视图中重命名列，请如下在 CREATE VIEW 子句后包含新列名称。
~~~
CREATE VIEW view_name(new_column_list) 
AS
SELECT-statement;
~~~



从视图中查询数据
从视图中查询数据与从表格中查询数据相同。以下语句从 employee_contacts 视图中选择数据。
~~~
SELECT 
    *
FROM
    employee_contacts;
~~~

修改视图
如果视图不存在，该语句将创建该视图，如果视图已存在，该语句将更改当前视图。
~~~
CREATE OR REPLACE view_name AS
SELECT-statement;
~~~


移除 SQL 视图
`DROP VIEW` 语句仅删除视图，而不删除基准表。
~~~
DROP VIEW view_name;
~~~

在mysql使用delete删除视图某个行，会影响源数据表吗？
简单视图（由单个表的查询创建，不包含聚合函数、DISTINCT、GROUP BY、HAVING 等）：
执行 DELETE 操作会直接删除源数据表中对应的数据
例如：DELETE FROM view_name WHERE id = 1 会删除源表中 id=1 的记录

复杂视图（包含多个表连接、聚合函数、DISTINCT 等）：
MySQL 不允许执行 DELETE 操作，会直接报错
因为这类视图的数据来自多个表或经过计算处理，无法明确确定应该删除哪些源数据


# 触发器
触发器是在数据库表中发生特定事件后自动执行的一段代码。
触发器始终与特定表关联。如果删除表，则所有关联的触发器也会自动删除。

触发器要么在以下事件之前要么之后调用：
INSERT – 插入新行时
UPDATE – 更新现有行时
DELETE – 删除行时。


## 两种类型的触发器：行级触发器和语句级触发器。
- 行级触发器在UPDATE语句影响行时每次执行。如果UPDATE语句影响 10 行，则行级触发器将执行 10 次，每次针对一行。如果UPDATE语句不影响任何行，则行级触发器根本不会执行。
- 语句级触发器会被调用一次，无论UPDATE语句影响多少行。请注意，如果UPDATE语句未影响任何行，则触发器仍将执行。

创建触发器时，可以使用 FOR EACH ROW 或 FOR EACH STATEMENT 分别指定触发器是行级别还是语句级别。

## 应用场景
- 记录表修改。 某些表具有敏感数据，如客户电子邮件、员工薪资等，您需要记录所有更改。
- 实施复杂数据完整性。在此场景中，您可以定义触发器，验证数据并在必要时重新设置数据格式。例如，可以使用 BEFORE INSERT 或 BEFORE UPDATE 触发器，在插入或更新前转换数据。

创建触发器
~~~
CREATE TRIGGER trigger_name [BEFORE|AFTER] event
ON table_name trigger_type
BEGIN
  -- trigger_logic
END;
~~~

# 函数

## 字符串函数
### CONCAT: 将两个或多个字符串串联成一个字符串
~~~
CONCAT(string1,string2,..);
~~~
如果参数中有一个为 NULL，则返回 NULL

示例：
~~~
SELECT CONCAT('SQL CONCAT function', ' demo');

        concat
----------------------
 SQL CONCAT function demo
(1 row)
~~~

使用 MySQL 或 PostgreSQL，您可以使用 CONCAT_WS 函数使用分隔符串联字符串。
~~~
CONCAT_WS(separator,string1,string2,...);
~~~
使用 CONCAT_WS 函数如下构建员工全名
~~~
SELECT 
    CONCAT_WS(' ',first_name,last_name) AS name
FROM
    employees
ORDER BY name;
~~~

