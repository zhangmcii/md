# 排查N+1问题

每篇文章包含文字，图片，评论，点赞。首页会分页只返回10篇文章，之前存在你说的N+1问题，导致返回10篇文章查询51次sql，比如瞎下面这样查询：
```
posts = Post.query.order_by(Post.created_at.desc()).limit(20).all()
for post in posts:
    post.author.username
    post.comments.count()
    post.likes.count()
```
不过已经修改了查询方式，把 to_json 内部的数据库查询全部移除，将查询提前批量执行，然后给每个 Post 填入数据。目前的sql执行次数降到8。
2.函数已经加了@cache.cached(timeout=60)

不过上述所做的改进，请求依然很慢

这是首页第一页10条文章的时间：
浏览器显示请求的耗时： 1.16秒


日志记录的sql查询时间：
2025-12-18 11:12:11,946 [INFO] [decorators.py:158] - Total SQL    : 9
2025-12-18 11:12:11,946 [INFO] [decorators.py:159] - SQL Time     : 0.01 sec
2025-12-18 11:12:11,946 [INFO] [decorators.py:160] - Total Time   : 0.02 sec


排除sql引起的。

性能瓶颈分析
1. 外部 API 调用（最可能的瓶颈）
在 log_operate 装饰器中，每次请求都会调用外部 API：

python
# decorators.py:108-112
r = requests.get(f"https://ipapi.co/{client_ip}/json/")
local_data = r.json()
这个 HTTP 请求可能需要 1-2 秒，特别是当网络状况不好或外部 API 响应慢时。

3. 缓存配置问题
配置中使用的是 SimpleCache ：

python
# config.py:44
CACHE_TYPE = "SimpleCache"
这是内存缓存，不适合多进程部署。


根因：首页记录访客装饰器中存在外部ip查询，严重阻塞请求

措施：
1.log_operate的同步外部查询和数据库写入，改为异步任务执行
2.修改cache类型
CACHE_TYPE = "RedisCache"
CACHE_REDIS_URL = "redis://:1234@localhost:6379/5"


请求慢的根因：
1.数据库查询N+1问题
2.flask主应用与socketio服务分离
3.装饰器中含有外部请求查询
4.首页永远不返回全文（解决浏览器下载耗时久）

