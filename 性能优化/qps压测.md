背景： 云服务器是4核，内存4GB，带宽是3Mbps
网站： vue+flask,   nginx已开启Nginx + gzip 
	   启动gunicorn -b :5000 --worker-class eventlet -w 4 - - flasky:app

测试工具1：apiPost，开启8个进程，持续时间10s,压测生产环境，总请求数为89， 每秒请求数：8.88r/s
测试工具2：  wrk -t4 -c50 -d10s https://191718.com/api/api/v1/posts

那么qps约等于9了，结果的qps正常吗，是否可以提高呢，给我优化的办法。


是我的数据库查询太慢导致的阻塞？


不是 Flask 不行，是瓶颈不在你以为的地方。


为什么QPS这么低？
**真正的第一瓶劲：3Mbps带宽**
我们先算一个“物理上限”。
带宽换算:
```
3 Mbps ≈ 0.375 MB/s ≈ 375 KB/s
```

我的接口返回 JSON：
```
{
  "code": 0,
  "message": "success",
  "data": {...}
}
```
即便 只有 10 KB / 请求：
```
375 KB/s ÷ 10 KB ≈ 37 QPS（理论上限）
```
如果是：
- 返回用户信息
- 返回文章列表
- 带头像 URL
- Header 较多

现实场景中请求返回20~30 KB 是非常常见的:
```
375 ÷ 30 ≈ 12 QPS
```
所以：带宽已经在卡你


换压测工具wrk
测试命令： wrk -t4 -c50 -d10s https://191718.com/api/api/v1/posts
结果
```
Running 10s test @ https://xxx.com/api/api/v1/posts
  4 threads and 50 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     1.06s   300.33ms   2.00s    85.04%
    Req/Sec    14.03     11.06    50.00     76.80%
  377 requests in 10.08s, 101.25KB read
  Socket errors: connect 0, read 0, write 0, timeout 16
Requests/sec:     37.41
Transfer/sec:     10.05KB
```
这次 QPS 不低，是真实能力

延迟分析:
```aiignore
Latency Avg: 1.06s
Max: 2.00s
timeout: 16
```



这说明：
- 平均一个请求要 1 秒
- 有请求超过 wrk 默认 timeout（2s）
- 并发 50 时已经开始“扛不住”
这不是带宽问题，是后端处理慢

真正的瓶颈在哪里？（结论）

核心瓶颈不是带宽，而是：
「Flask + eventlet + 同步 IO」模型不匹配

接口包含：
- SQLAlchemy 查询（同步）
- ORM 序列化
- JSON dumps
- JWT / 鉴权
- 可能还有 Redis

⚠️ eventlet 只有在 IO 全异步时才有优势

问题不在“QPS 太低”，而在“模型选择不匹配”。
首先，将gunicorn中的eventlet进行"角色拆分"，让http服务在gunicorn中接受，Websocket在gunicorn (eventlet/gevent)中接受。
因为eventlet专为异步设计，而我的接口中包含大量同步操作，比如差数据库，ORM 会阻塞整个 greenlet，并且eventlet 对 CPU 任务极其不友好。
拆分后有助于提高接口响应速度
官方推荐模式本质上是：
```
        ┌──────────────┐
        │  Nginx       │
        │              │
        ├──── HTTP ────┼──▶ gunicorn (sync workers)
        │              │
        └─ WebSocket ──┼──▶ gunicorn (eventlet/gevent)
                       └── Redis (message_queue)
```
原来的启动脚本boot.sh
```aiignore
...
exec gunicorn -b :5000 --worker-class eventlet -w 4 --access-logfile - --error-logfile - flasky:app
```

修改后的boot.sh
```
# 主应用服务
gunicorn -b :5000 -w 8 --access-logfile - --error-logfile - flasky:app &

# WebSocket 服务
gunicorn -b :5001 -w 1 --worker-class eventlet --access-logfile - --error-logfile - flasky:app &
```

后端应用是docker部署的，所以需要映射两个端口
```
# 4289 → 容器 5000（HTTP）
# 4290 → 容器 5001（WebSocket）
docker run --name flasky_backend -d -p 4289:5000 -p 4290:5001 flasky_backend:latest;
```
再修改nginx：
```
# HTTP API
location / {
    proxy_pass http://localhost:4289;
}

# WebSocket
location /socket.io/ {
    proxy_pass http://localhost:4290;
}
```

别忘了将新增的入口文件页也拷贝到容器中，否则gunicorn将找不到该文件报错
```dockerfile
...
COPY flasky_socketio.py ./
...
```

wrk -t4 -c50 -d30s https://191718.com/api/api/v1/posts
Running 30s test @ https://191718.com/api/api/v1/posts
  4 threads and 50 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   967.50ms  215.21ms   1.98s    88.27%
    Req/Sec    13.32      9.68    60.00     81.62%
  1282 requests in 30.03s, 344.29KB read
  Socket errors: connect 0, read 0, write 0, timeout 20
Requests/sec:     42.70
Transfer/sec:     11.47KB

