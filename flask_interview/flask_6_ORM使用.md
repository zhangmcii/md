
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
假设你有一个 User 表和一个 Post 表： 
一个用户有多个帖子（1-N）
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
Session = SQL 操作的暂存区（Unit of Work）
负责追踪对象状态（new / dirty / deleted）
直到 commit 才真正写入数据库

② 什么时候需要 add()？
当对象第一次被加入会话时需要 add（new state）
修改已有对象不需要 add（dirty state 自动追踪）

③ commit / flush / rollback 的区别
flush
将 SQL 语句发送到数据库，但不提交事务
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
flush：发 SQL，不提交  
commit：提交（会自动 flush）  
rollback：撤销未提交的事务  
