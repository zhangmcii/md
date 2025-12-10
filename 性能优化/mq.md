# 如何利用Celery来解耦消息通知逻辑？


点赞API流程长这样：既要写点赞记录(Praise表)，又要写Notification表，又要发socketio。
```
praise API
 ├─ 写点赞记录（事务内）
 ├─ 生成通知记录
 ├─ 写通知记录
 ├─ 提交成功（commit）
 └─ 发socketio
```
通知和点赞耦合严重，带来的问题是每个API（评论，发帖，私信API都会触发通知）又慢又长，通知系统无法独立扩展，并且没法进行异步处理。


现在改为数据库事务里只做点赞入库，通知相关的逻辑全部交给 Celery Worker。新的架构变成这样
```
praise API
 ├─ 写点赞记录（事务内）
 ├─ 提交成功
 └─ push Celery 任务：send_like_notification(task)
```

下面是代码的重构：
我们不能简单地将flask应用中的socketio实例引入到Celery的异步任务，这样异步任务中socketio并不会生效，比如下面这样：
```
app/__init__.py

socketio = SocketIO()
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    ...
    socketio.init_app(app, cors_allowed_origins="*")
 
 
app/mycelery/notification_task.py

from celery import shared_task
from .. import socketio
@shared_task(ignore_result=True)
def create_like_notifications(post_id, comment_id, liker_id, receiver_id):
    """创建点赞通知"""
    
    ...
    socketio.emit("new_notification", notification_data[i], to=str(notification.receiver_id))
```


当 Celery Worker 与 Flask 进程独立运行时，直接导入 Socket.IO 实例无法跨进程广播消息，必须通过 message_queue（消息队列，如 Redis）实现多进程通信。
让Celery把通知push进消息队列， Flask-SocketIO 在内部已经实现了订阅 Redis 消息通道（Redis pub/sub）,会自动取消息、解析事件并广播到 WebSocket 客户端，
所以我们不用在Flask应用中实现 “从 Redis 取通知”的逻辑。


下面是实例代码:
第一步，安装所需要的库
```
pip3 install flask-cors  
pip3 install flask-socketio  
pip3 install celery
```
flask-cors库是用来规避浏览器同源策略的库，flask-socketio用来建立全双工websocket链接，celery承担异步任务队列的职责。

实例化app对象
config.py
````
import os
class Config:
    # Flask 基础配置
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    DEBUG = True

    # Redis 核心配置
    REDIS_URL = "redis://localhost:6379/0"

    # Celery 配置
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL

    # Socket.IO 
    SOCKETIO_MESSAGE_QUEUE = REDIS_URL
````

app/__init__.py
```
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from celery import Celery
from config import Config

db = SQLAlchemy()
socketio = SocketIO()

# 初始化 Celery
def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config["CELERY_BROKER_URL"],
        backend=app.config["CELERY_RESULT_BACKEND"]
    )
    celery.conf.update(app.config)
    return celery

# 工厂函数
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化Celery
    celery = make_celery(app)
    app.celery = celery
    
    db.init_app(app)
    
    # message_queue 指向 Redis，让多进程共享消息通道
    socketio.init_app(
        app,
        cors_allowed_origins="*",
        message_queue=app.SOCKETIO_MESSAGE_QUEUE 
    )
    
    # 注册路由
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app, celery
```


app/mycelery/notification_task.py（Celery 任务)
```
import logging

from celery import shared_task
from .. import db, socketio
from ..models import Notification, NotificationType

# -------------------------- 异步任务（主动触发）--------------------------
@shared_task(ignore_result=True)
def create_like_notifications(post_id, comment_id, liker_id, receiver_id):
    """创建点赞通知

    Args:
        post_id: 文章ID (评论点赞时传入评论所在文章ID)
        comment_id: 评论ID (文章点赞时传入None)
        liker_id: 点赞者ID
        receiver_id: 接收者ID (文章作者或评论作者)
    """
    try:
        if receiver_id is None:
            return

        notification = Notification(
            receiver_id=receiver_id,
            trigger_user_id=liker_id,
            post_id=post_id,
            comment_id=comment_id,
            type=NotificationType.LIKE,
        )

        _create_and_emit_notifications([notification])
        logging.info(f"点赞通知任务完成: post_id={post_id}, comment_id={comment_id}")

    except Exception as e:
        db.session.rollback()
        logging.error(f"点赞通知任务失败: {str(e)}", exc_info=True)
        
def _create_and_emit_notifications(notifications):
    """创建通知并推送给用户"""
    if not notifications:
        return

    db.session.add_all(notifications)
    db.session.flush()

    # 批量推送通知
    notification_data = [notification.to_json() for notification in notifications]
    for i, notification in enumerate(notifications):
        socketio.emit(
            "new_notification",
            notification_data[i],
            to=str(notification.receiver_id),
        )

    db.session.commit()

```
这里注意，此时socketio已配置message_queue，跨进程可用，可以直接从flask应用中引入socketio实例。

在Flask项目的目录下，分别开启两个命令行， 
启动Flask应用：
```
python manage.py
```

和celery服务： 
```
mac端：
celery -A app.make_celery worker -B --loglevel INFO

windows端：（这里celery服务还是基于协程库eventlet）
celery -A app.make_celery worker -B --loglevel INFO -P eventlet
```

可能遇到的问题：
启动Flask应用控制台显示：
```
RuntimeError: Redis requires a monkey patched socket library to work with eventlet
```
报错原因是因为eventlet 是异步 IO 库，它通过替换 Python 标准库中的 socket、threading 等模块实现协程异步；
但 Redis 的 Python 客户端（redis-py）依赖原生 socket，若不提前给 eventlet 打猴子补丁，会导致 Redis 连接与 eventlet 异步引擎冲突，触发 RuntimeError。

我们在在**所有代码执行前**，先执行 eventlet.monkey_patch()，覆盖原生 socket 库。
```
import eventlet
# 关键：提前打猴子补丁，覆盖socket/threading等模块
eventlet.monkey_patch()

from app import create_app

# 创建Flask应用并获取Celery实例
app, celery = create_app()

# 激活Flask应用上下文
app.app_context().push()

# 注册定时任务
from app.tasks import register_scheduled_tasks
register_scheduled_tasks(celery)

```

总结：
1.若需要在跨进程使用Flask应用中的socketio,需要在实例化SocketIO时提供message_queue字段指定redis地址。
2.控制台摆报错"Redis requires a monkey patched socket library to work with eventlet",在Flask应用所有代码执行前执行猴子补丁