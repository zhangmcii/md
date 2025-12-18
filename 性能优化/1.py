a= '\\n# 为什么你需要 Celery + Redis + Flask-SocketIO？因为同步太慢了\\n\\n在开发社交类 API 时，我们经常遇到一个痛点：**“接口太慢了”**。\\n\\n比如一个简单的“点赞”操作，后台不仅要写入点赞记录，还要生成通知、写入通知表、通过 WebSocket 推送给用户... 这一系列操作挤在一个数据库事务里，导致 API 响应迟缓，**耦合严重**。\\n'

lines = a.splitlines()
print(len(lines))
print(len(a))