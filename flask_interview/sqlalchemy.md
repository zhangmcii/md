重要度从高到低:

1.Session 与事务管理
提交、回滚、生命周期

2.ORM 映射与模型设计
表结构与类关系

3.查询构造与性能
filter、join、索引意识

4.关系类型与加载策略
一对多、懒加载

5.级联与删除策略
cascade、软删除

6.flush 与 commit 区别
写入时机差异

7.SQLAlchemy Core vs ORM
适用场景区别



数据库方言（dialect）是什么？

抛开数据库，生活中的方言是什么？方言就是某个地方的特色语言，是一种区别于其它地方的语言，只有你们这一小块地方能听懂，出了这个地方又是另一种方言。
数据库方言也是如此，MySQL 是一种方言，Oracle 也是一种方言，MSSQL 也是一种方言，他们之间在遵循 SQL 规范的前提下，都有各自的扩展特性。
这对于 ORM 框架来说，为了在上层的ORM层做了无差别调用，比如分页，对使用者来说，不管你底层用的是MySQL还是Oracle，他们用的都是一样的接口，
但是底层需要根据你使用的数据库方言不同而调用不同的DBAPI。用户只需要在初始化的时候指定用哪种方言就好，其它的事情ORM框架帮你完成了


使用 ORM 时, 基本的事务/数据库交互对象称为 Session



## （基础）SQLAlchemy 里的 Session 是做什么的？ 它和数据库连接（connection）是不是一回事？
## 一次典型的请求中，Session 的生命周期应该是怎样的？ 在 Flask 里一般如何管理？
## commit()、rollback()、flush() 分别做了什么？flush() 会提交事务吗？什么时候必须用？
## （难）如果在一次事务中，前面已经 flush 了多条数据，后面发生异常并 rollback()，数据库中会发生什么？为什么？

解答1:

Session是基本的事务或者数据库交互对象。事实上，当使用Session时，它在内部引用connection, 并使用它来发出sql。

当 Session 与非 ORM 构造一起使用时，它会传递我们给它的 SQL 语句，并且通常与 Connection 直接执行的方式没有太大区别。
比如
```
from sqlalchemy.orm import Session

stmt = text("SELECT x, y FROM some_table WHERE y > :y ORDER BY x, y")
with Session(engine) as session:
     result = session.execute(stmt, {"y": 6})
     for row in result:
         print(f"x: {row.x}  y: {row.y}")
```

在ORM中，Session对象负责构建Insert构造，并在正在进行的事务中将其作为INSERT语句发出

解答2：
Session生命周期:请求进入时，flask会把该请求分配到对应的视图函数中，视图函数需要加载数据库数据时，会创建数据库连接请求或者从数据库连接池获取连接，
这时Session建立了，直到归还连接到连接池，Session结束。

解答3：commit()提交事务；rollback()回滚事务；flush()提交sql语句到数据库，但不提交事务；
如果在session期间需要访问未提交对象的待生成的id，需要使用flush()


解答4:发生异常并 rollback()，发送到数据库的sql语句会执行回滚，数据库不会做任何更新。因为flush并未提交事务。


Session 本质上是 SQLAlchemy 的 Unit of Work，
用于管理 ORM 对象状态和数据库事务。
它不是数据库连接，而是对 connection 的高层封装。

在一次请求中，通常会创建一个 Session，
在请求内完成所有数据库操作，
最后根据是否异常选择 commit 或 rollback，
并在结束时关闭 Session。

flush() 的作用是把 Session 中的变更同步为 SQL 语句发送到数据库，
但仍然处于当前事务中，并不会提交事务。
commit() 才会真正提交事务，
rollback() 会回滚当前事务中的所有操作。

因此，即使已经执行过 flush，
只要还没 commit，
一旦发生异常并调用 rollback，
数据库中的数据都会被完整回滚，
flush 产生的变更也不会被持久化。


## 什么是 SQLAlchemy 的 ORM 映射？ Table、Mapper、模型类三者之间是什么关系？
## 在设计一个常见的用户–文章模型时，你通常会如何定义主键、外键和唯一约束？为什么？
## relationship() 是做什么的？它和 ForeignKey 的职责有什么区别？
## 如果一个模型字段既要支持 NULL，又要在业务上区分“未设置”和“设置为空”，你在 ORM 设计上会怎么处理？为什么？

解答1: 
ORM 映射指 把数据库表的列用Python的类属性来表示，一个类实例就是数据库表某行的代理。
Table是命令式创建，模型类是申明式创建，Mapper是属性列的类型提示。模型类基于Table之上，Mapper可用在模型类中。

解答2:
用户-文章模型是一对多关系，用户是"一"的侧，文章是"多"的侧。
用户，文章的id列设置为主键，因为每个实体都有对应唯一的编号的。
在多的一侧设置外键，也就是在文章表中设置外键，因为每个文章都对应唯一的用户，需要用外键来关联这个用户。
用户表中的邮箱等设置成唯一约束，因为不可能一个邮箱对应多个用户。


