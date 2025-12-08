
1.（简单）在 Flask 中如何初始化 SQLAlchemy？请写出标准的初始化方式（不需要真实数据库连接串）。
2.请解释 会话（session）是如何工作的：
    什么时候需要 db.session.add()？
    db.session.commit()、db.session.flush()、db.session.rollback() 的区别是什么？
3.请解释 ORM 中的 延迟加载（lazy loading）和预加载（eager loading），并举例说明何时会导致 N+1 查询问题。
4.请说明 Flask-SQLAlchemy 中的 查询链式调用 Query 对象是如何构建 SQL 的，
    并解释：
    Query 何时执行 SQL？
    调用了哪些关键方法？
5.（困难 + 设计题）
假设你有一个 User 表和一个 Post 表： 一个用户有多个帖子（1-N）
你要设计一个 API：返回某个用户的所有帖子，并要求只执行 1 次 SQL 查询（不能 N+1）
同时要求：必须能分页帖子，并在 JSON 中返回用户与帖子信息
请说明你会如何设计 模型、查询方式、序列化方式。


解答1:
假设flask应用使用工厂模式创建app实例, 从类中导入配置。

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    return app

解答2:
当对模型类属性做了修改时，需要db.session.add()
db.session.commit()会提交更改到数据库，无法回滚。
db.session.flush()会立刻刷新
db.session.rollback()是回滚操作

评分：4.5 / 10

① ORM Session 的本质（非常加分）
Session = SQL 操作的暂存区
负责追踪对象状态（new / dirty / deleted）
直到 commit 才真正写入数据库

② 什么时候需要 add()？
- 当对象第一次被加入会话时需要 add（new state）
> 比如：新建对象（transient）
        c = Comment(text="hi")
        db.session.add(c)

- 修改已有对象不需要 add（dirty state 自动追踪）
> 不需要 add 的情况:
    1.查询得到的对象
    2.修改任何字段
    3.删除对象（使用 delete）
        post = Post.query.get(3)
        db.session.delete(post)
        db.session.commit()      
    4.批量更新中被加载的对象
    5.flush / commit 中自动处理关系，不需要 add
        user = User.query.get(1)        # persistent
        new_post = Post(title="Hello")  # transient
        user.posts.append(new_post)     # new_post 自动加入 session
        db.session.commit()             # 自动 INSERT user + post

③ commit / flush / rollback 的区别
flush： 获该行数据得数据库生成的主键（比如自增 id）。
执行 SQL 语句， 但不提交
可能自动触发（执行 query 时）
rollback 依然有效

commit
提交事务，数据持久化
触发自动 flush
创建新的事务

rollback
回滚未提交的事务
所有 pending 的 SQL、对象状态恢复到上一个稳定点

🎯 ④ 一句话总结（强记）
add：把对象纳入会话  
flush：执行 SQL，不提交   
commit：提交（会自动 flush）  
rollback：撤销未提交的事务

解答3:
延迟加载：指的是某个属性在对象首次加载时不包含其数据库端的值。相反，该属性会被 缓存，使其在首次使用时才从数据库加载数据
预加载：指的是在从数据库加载对象本身的同时，将某个属性的数据库端值也填充进去

N+1问题是延迟加载模式常见的副作用。最终结果是，首先会发出一个SELECT语句来加载父对象的初始结果集；然后，当应用程序遍历每个成员时，
会为每个成员发出一个额外的SELECT语句来加载该成员的相关属性或集合。最终结果是，对于包含N个父对象的结果集，将会发出N+1个SELECT语句。
利用预加载可以缓解 N+1 问题。


① 延迟加载（Lazy Loading）
- 默认 lazy='select'
- 在访问 relationship 属性时才发送 SQL
- 会导致每访问一次属性执行一次 SELECT
- 适用于 infrequently-used relationships
```
users = User.query.all()
for u in users:
    print(u.posts)   # 每次访问都会触发 SELECT
```

② 预加载（Eager Loading）
- 在加载主对象时就预先加载关联对象
- 不等到访问属性才查询
常见方式：
- joinedload()：JOIN 一条大 SQL
- subqueryload()：两个 SQL
- selectinload()：IN 查询，最推荐
```
User.query.options(joinedload(User.posts)).all()
```
仅执行 1 条 SQL（大幅减少 N+1）。

③ N+1 查询问题
现象：加载父对象时只执行 1 条 SQL，
访问每个子对象又额外执行 1 条 SQL
最终执行 N + 1 条 SQL
示例：
```
users = User.query.all()     # 1 条 SQL
for u in users:
    u.posts                  # N 条 SQL
```
④ 如何解决
使用 eager loading：
- selectinload（推荐）
- joinedload
- subqueryload

第4题：
Query 对象本身从不执行 SQL。
SQLAlchemy 只在你“需要结果”的那一刻执行 SQL： .all(), .first(), .one(), .count(), .scalar(), .get(), 遍历 Query，访问 lazy 属性。


第5题：
User表：
    id = db.Column(db.Integer, primary_key=True)
    posts = db.relationship("Post", backref="author", lazy="dynamic")
Post表：
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))

查询：
def get_posts_by_user_id(user_id):
    query = User.query.options(joinload(User.posts)).filter_by(id=user_id)
    paginate = query.paginate(page=1, per_page=10, error_out=False)
    users = paginate.items
    return jsonify(posts = [post.to_json() for post in users.posts])

得分：3 / 10

```
def get_posts_by_user_id(user_id):
    page = 1
    per_page = 10

    # 一次性 JOIN 查询 + 分页
    pagination = (
        db.session.query(Post, User)
        .join(User, User.id == Post.author_id)  # JOIN
        .filter(Post.author_id == user_id)
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    posts_with_user = pagination.items  # 每项是 (Post, User)

    return jsonify(
        posts=[
            {
                "post": post.to_json(),
                "user": user.to_json(),
            }
            for post, user in posts_with_user
        ]
    )

```





优化示例：
1.
```
u = User(
    email=current_app.config["FLASKY_ADMIN"],
    username="zmc",
    password="zmc",
    name="追梦少年",
    location="上海",
    about_me="随便说点啥...",
)
db.session.add(u)     // 改为db.session.flush()
db.session.commit()

# 添加管理员的文章到post表
u1 = User.query.filter_by(username="zmc").first()    // 删除
p = Post(body=fake.text(), timestamp=fake.past_date(), author=u1)
db.session.add(p)       // 删除
db.session.commit()
```


1.第一处commit改为db.session.flush()，并且去掉后面的User.query.xxxxx
    为什么可以一次 commit？
    因为：
    ✔ flush() 会执行 SQL
    让 u 获得数据库生成的主键（比如自增 id）。
    ✔ 事务仍然开启
    flush() 不会提交，只会把 pending 对象写入数据库。
    ✔ 你已经有了 u 对象
    没必要再 User.query.xxxxx 去查一次。
2.去掉第二处的db.session.add()
    在 SQLAlchemy 中：
    当你创建一个对象 p = Post(..., author=u)，并把它关联到一个已经在 session 中的对象 u 时：  等价于你写了 u.posts.append(p)
    ✔ SQLAlchemy 会自动把 p 视为“脏对象”
    也就是自动加入 session。

    满足自动加入 session 的条件:
    1.u 已在 session 中
    2.你创建 p 时设置了 relationship 字段 author=u