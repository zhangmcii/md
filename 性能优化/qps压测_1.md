由于Flask项目中引入了websocket,所以在gunicorn的工作进程类型改为了eventlet。 现在的诉求是，能不能把websocket与Flask主应用分离，
使得主应用使用gunicorn -b :5000  -w 8 - - flasky:app 启动， websocket使用gunicorn -b :5001 --worker-class eventlet -w 4 - - …. 启动
这样，主应用专注于接受http请求，socket应用接受websocket请求，以此提高项目的QPS。
先请告诉上面的诉求能否实现？ 如果可以，下面是我的整个流程规划，分为核心流程和具体流程，你看看能在生产环境正确运行起来吗，是否存在什么问题。
如果你有更好的办法实现上面的诉求，你也可以提出来，不要增加新的技术栈和工具

核心流程：
前端：以域名为基准连接 WS，token 放入 query 参数，强制websocket传输协议，配置重连策略，路径固定为/socket.io；
Nginx：HTTP 请求转发至宿主机 4289 端口（映射容器 5000，主应用），/socket.io路径转发至宿主机 4290 端口（映射容器 5001，WS 应用），WS 请求需配置 HTTP1.1 升级头及匹配 SocketIO 的超时；
后端：全局共享db/jwt单例，主应用 / WS 应用分别初始化；WS 事件中 DB 操作异步化（避免阻塞），搭配事务 + 应用上下文绑定；Celery 通过 Redis 消息队列推送 WS 事件；
容器部署：宿主机 4289→容器 5000、4290→容器 5001 做端口映射；boot.sh创建日志目录，用&启动主应用 / WS/Celery 多进程，阻塞脚本防止容器退出；


具体流程
1.前端: 
```
import { io } from "socket.io-client";
this.socket = io(import.meta.env.DEV ? "": import.meta.env.VITE_DOMIN, {
          path: "/socket.io",
          transports: ["websocket"],
          query: { token: this.token },
}
```

2.Nginx :
```
    # http服务
    location / {
        proxy_pass http://localhost:4289;
        ...
    }
    
    # websocket服务
    location /socket.io {
        proxy_pass http://localhost:4290;
        ...
    }
```


3.后端：
db共享实例，socket事件同步查询改为异步
```
# app/__init__.py       
db = SQLAlchemy()
jwt = JWTManager()
socketio = SocketIO()

def create_main_app():
	app = Flask(__name__)
	db.init_app(app)
    jwt.init_app(app)
    # 主应用无需初始化SocketIO
	...
	return app


def create_ws_app():
    app = Flask(__name__)
    db.init_app(app)
    jwt.init_app(app)
    socketio_ws.init_app(
        app,
        cors_allowed_origins=os.getenv("FRONTEND_DOMAIN"),
        ping_timeout=30,
        ping_interval=60,
        message_queue=app.config["SOCKETIO_MESSAGE_QUEUE"]
    )
	...
    return app


# app/event.py
WS连接，断开，聊天
from app import db  # 导入全局db
def register_ws_events(socketio, app):
	...


# app/celery_task.py
from flask_socketio import SocketIO
# 只负责向 Redis 发布消息。
celery_socketio = SocketIO(message_queue=os.getenv("SOCKETIO_MESSAGE_QUEUE"))

@shared_task(ignore_result=True)
def send_notification(user_id, message):
    celery_socketio.emit(
        'notification',
        {'user_id': user_id, 'message': message},
        room=f"user_{user_id}"
    )
    

# flasky.py
from app import create_main_app
app = create_main_app()


# flasky_ws.py
# 必须放在第一行！
import eventlet
eventlet.monkey_patch()

from app import create_ws_app
app = create_ws_app()
```

4.Docker容器 映射两个端口：  docker run -p 4289: 5000  -p 4290:5001 flasky
```
# boot.sh脚本

# 主应用进程
gunicorn -b :5000  -w 8 --access-logfile - --error-logfile - flasky:app &

# WS服务进程
gunicorn -b :5001 --worker-class eventlet -w 4 --access-logfile - --error-logfile - flasky_ws:app &

# Celery进程
celery -A app.make_celery worker --loglevel INFO -P eventlet --logfile=logs/celery_worker.log &
celery -A app.make_celery beat --loglevel INFO --logfile=logs/celery_beat.log --schedule=logs/celerybeat-schedule &
```



验证宿主机端口可访问：
**在宿主机(云服务器)执行**：
```
# 测试主应用（HTTP）
curl http://localhost:4289/api/v1/posts  # 应返回正常结果

# 测试WS应用（仅验证端口监听，无需建立连接）
telnet localhost 4290  # 应返回「Connected to localhost」（按Ctrl+]退出）
```


用 curl 模拟 WS 握手，验证应用层是否正常（核心验证）
```
# 宿主机执行，模拟WS握手请求（替换你的域名/IP）
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" -H "Host: 191718.com" -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" -H "Sec-WebSocket-Version: 13" http://localhost:4290/socket.io/?EIO=4&transport=websocket

# 或者
curl -i -N \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Host: 191718.com" \
  -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Origin: https://191718.com" \
  "http://localhost:4290/socket.io/?EIO=4&transport=websocket"
```
正常结果：返回 101 Switching Protocols（即使后续断开，只要有此响应，说明 WS 服务正常）；
异常结果：返回 404/500 → 说明 WS 服务未正确启动或路由匹配失败。




我们之前说过，WS 的聊天事件中，会执行celery异步任务发通知，而我的项目中Celery中是这样写的
```
# app/__init__.py
def create_app():
	...
	celery_init_app(app)
	return app
	

# app/make_celery.py
flask_app = create_app(os.getenv("FLASK_CONFIG") or "default")
celery_app = flask_app.extensions["celery"]
```
celery是用主应用实例来实例化的，而我们又在WS的注册事件中引入了celery，主应用和WS服务是两个独立的进程，这样执行celery任务正确吗


完结。已解决主应用与socketio分离