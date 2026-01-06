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












ORM-Session
1.是什么：
Session对象负责构建Insert构造，并在正在进行的事务中将其作为INSERT语句发出

2.flush
Session.flush() 用于手动将挂起的更改推送到当前事务。
当调用时候，它创建了一个新事务并为这两个对象发出了适当的 INSERT 语句，事务现在保持打开状态，直到我们调用 Session.commit(), Session.rollback(), 或 Session.close() 方法中的任何一个 Session。

一旦插入行，我们创建的两个 Python 对象就处于称为持久化的状态，并且ORM 检索了每个新对象的新主键标识符

autoflush –当 True 时，所有select查询操作将在继续之前为此 Session 发出 Session.flush() 调用。


3.有关session的操作：
session.add()
session.flush()
session.commit()
session.rollback()
session.close()

session.new        # 挂起状态的集合
session.dirty      # 脏数据集合


4.从 Identity Map 中按主键获取对象
我们可以通过使用 Session.get() 方法检索对象，如果本地存在，它将从 identity map 返回一个条目，否则发出一个 SELECT
```
>>> some_squidward = session.get(User, 4)
>>> some_squidward

User(id=4, name='squidward', fullname='Squidward Tentacles')
```

5.回滚 Session.rollback()
不仅会回滚事务，还会使当前与此 Session 关联的所有对象过期, 
这将导致在下次使用延迟加载（lazy loading）过程访问这些对象时，它们会自动刷新。

6.关闭session.close()
它完成了以下事情：
- 它释放所有连接资源到连接池，取消（例如，回滚）任何正在进行的事务
- 它从 Session 中删除所有对象




7.加载关系：
relationship.backref - 旧版形式，允许更简洁的配置，但不支持显式类型提示
relationship.back_populates - 新版形式。允许每个 relationship() 两侧的对象同步 Python 状态更改
简单来说，对一个类进行的修改，在关联的另外的类上会自动同步更新。
```
class User(Base):
    __tablename__ = "user_account"

    addresses: Mapped[List["Address"]] = relationship(back_populates="user")


class Address(Base):
    __tablename__ = "address"

    user: Mapped["User"] = relationship(back_populates="addresses")
```

现做如下操作：
```
>>> u1 = User(name="pkrabs", fullname="Pearl Krabs")
>>> u1.addresses
[]

a1 = Address(email_address="pearl.krabs@gmail.com")
>>> u1.addresses.append(a1)

# 此时，u1.addresses 集合如预期的那样包含新的 Address 对象
>>> u1.addresses
[Address(id=None, email_address='pearl.krabs@gmail.com')]

# 还发生了另一个行为，即 User.addresses 关系与 Address.user 关系同步
>>> a1.user
User(id=None, name='pkrabs', fullname='Pearl Krabs')
```


下述行为，其中 Session 接收到 User 对象，并沿着 User.addresses 关系找到相关的 Address 对象，被称为**保存-更新级联**：
```
>>> session.add(u1)
>>> u1 in session
True
>>> a1 in session
True
>>> a2 in session
True
```



8.加载器策略
延迟加载是最著名的 ORM 模式之一，也是最具争议的模式之一。
当内存中的几十个 ORM 对象各自引用少量未加载的属性时，对这些对象进行常规操作可能会引发许多额外的查询，这些查询可能会累积起来（也称为 N+1 问题），更糟糕的是，它们是隐式发出的
如何能够控制和优化此加载行为？
有效使用 ORM 延迟加载的第一步是测试应用程序，打开 SQL 回显，并观察发出的 SQL 语句，如果出现大量看似可以更有效地合并为一个的冗余 SELECT 语句，那么就应该考虑使用加载器策略。

8.1 现代 SQLAlchemy 中最有用的加载器是 `selectinload()` 加载器选项。此选项解决了最常见的 “N+1” 问题形式。
selectinload()函数会确保使用单个查询预先加载一系列对象的特定集合。
它通过使用 SELECT 形式来实现这一点，在大多数情况下，SELECT 形式可以针对相关表单独发出，而无需引入 JOIN 或子查询，并且仅查询那些集合尚未加载的父对象
```
from sqlalchemy.orm import selectinload
stmt = select(User).options(selectinload(User.addresses)).order_by(User.id)
for row in session.execute(stmt):
    print(
        f"{row.User.name}  ({', '.join(a.email_address for a in row.User.addresses)})"
    )
    
```

8.2 `joinedload()` 预先加载策略是 SQLAlchemy 中最旧的预先加载器，它使用 JOIN（可能是外连接或内连接，具体取决于选项）增强传递到数据库的 SELECT 语句，然后可以加载相关对象。该策略最适合加载相关的多对一对象，

# 延迟加载
from sqlalchemy import select
[user.posts for user in db.session.execute(select(User)).scalars()]

8.3 显式 Join + 预先加载

8.4 `raiseload()`此选项用于完全阻止应用程序出现 N+1 问题，方法是使通常是延迟加载的操作改为引发错误。方法是将 relationship.lazy 设置为值 "raise_on_sql"，这样对于特定的映射，某个关系将永远不会尝试发出 SQL
```
class User(Base):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True)
    addresses: Mapped[List["Address"]] = relationship(
        back_populates="user", lazy="raise_on_sql"
    )

class Address(Base):
    __tablename__ = "address"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    user: Mapped["User"] = relationship(back_populates="addresses", lazy="raise_on_sql"
    )


>>> u1 = session.execute(select(User)).scalars().first()

# 报错了
>>> u1.addresses
Traceback (most recent call last):
...
sqlalchemy.exc.InvalidRequestError: 'User.addresses' is not available due to lazy='raise_on_sql'

```


from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload

[user.posts for user in db.session.execute(select(User).options(selectinload(User.posts))).scalars()]


由文章到作者
[post.author for post in db.session.execute(select(Post)).scalars()]

多对一 使用joinedload
[post.author for post in db.session.execute(Post.query.options(joinedload(Post.author))).scalars()]


Post.query.options(
                joinedload(Post.author).load_only(
                    User.id, User.username, User.nickname, User.image
                )
            )
            .fi




用法：
1. “AND” 和 “OR” 连接词都可以直接使用 and_() 和 or_() 函数
```
from sqlalchemy import and_, or_

print(
    select(Address.email_address).where(
        and_(
            or_(User.name == "squidward", User.name == "sandy"),
            Address.user_id == User.id,
        )
    )
)

结果：
SELECT address.email_address
FROM address, user_account
WHERE (user_account.name = :name_1 OR user_account.name = :name_2)
AND address.user_id = user_account.id
```


2. 针对单个实体的简单“相等”比较，还有一种流行的方法称为 Select.filter_by()，它接受与列键或 ORM 属性名称匹配的关键字参数
```
print(select(User).filter_by(name="spongebob", fullname="Spongebob Squarepants"))

结果：
SELECT user_account.id, user_account.name, user_account.fullname
FROM user_account
WHERE user_account.name = :name_1 AND user_account.fullname = :fullname_1
```

3. 显式的from和join
3.1 Select.join_from() 方法，它允许我们显式指示 JOIN 的左侧和右侧
```
print(
    select(user_table.c.name, address_table.c.email_address).join_from(
        user_table, address_table
    )
)

结果：
SELECT user_account.name, address.email_address
FROM user_account JOIN address ON user_account.id = address.user_id
```

3.2  Select.join() 方法，它仅指示 JOIN 的右侧，左侧是推断出来的
```
print(select(user_table.c.name, address_table.c.email_address).join(address_table))

结果：
SELECT user_account.name, address.email_address
FROM user_account JOIN address ON user_account.id = address.user_id
```

ON 子句是推断出来的
当使用 join_from() 或 join() 时，我们可能会观察到，在简单的外键情况下，join 的 ON 子句也会为我们推断出来。

显式的from
3.3 如果 FROM 子句不是我们希望从列子句中推断出来的方式, 我们使用 Select.select_from() 显式地向其中添加元素
```
print(select(address_table.c.email_address).select_from(user_table).join(address_table))

结果：
SELECT address.email_address
FROM user_account JOIN address ON user_account.id = address.user_id
```


3.4 我们可能想要使用 Select.select_from() 的另一个示例是，如果我们的列子句没有足够的信息来提供 FROM 子句
例如：从常见的 SQL 表达式 count(*) 中进行 SELECT, 我们使用一个名为 func 来生成 SQL count() 函数
```
from sqlalchemy import func
print(select(func.count("*")).select_from(user_table))

结果：
SELECT count(:count_2) AS count_1
FROM user_account
```

4. 设置 ON 子句
join() 和 join_from() 都接受 ON 子句的附加参数
```
.join(address_table, user_table.c.id == address_table.c.user_id)

```


5.ORDER BY 
Select.order_by() 方法接受一个或多个位置表达式,
升序/降序可从 ColumnElement.asc() 和 ColumnElement.desc() 
修饰符从 ORM 绑定的属性中获得

```
print(select(User).order_by(User.fullname.desc()))

```
将产生按 user_account.fullname 列降序排序的行




