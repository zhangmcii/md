
Flask 面试高频 10 大主题（1–3 年）
1. Flask 请求处理流程（Request Lifecycle）
从请求进入到响应返回的执行流程。

2. 路由机制（Routing）
URL 映射、动态路由、蓝图拆分。

3. Flask 配置管理（Config）
多环境配置与加载方式。

4. Flask 中的上下文（Application / Request Context）
应用上下文与请求上下文的原理和作用。

5. 中间件与钩子（Before/After Request）
请求前后处理，如鉴权、日志。

6. ORM 使用（SQLAlchemy / Flask-SQLAlchemy）
模型定义、会话管理、事务。

7. 表单与数据验证（WTForms / pydantic）
表单验证或请求体校验。

8. Session 与 Cookie 机制
Session 存储、签名、Cookie 原理。

9. Flask 扩展机制（Flask Extensions）
插件系统、常用扩展的加载方式。

10. 部署与生产环境（Gunicorn + Nginx）
常见部署方式与多进程模型。



Flask 请求处理流程 — 10 个由易到难的面试问题
1️⃣ （简单）Flask 的请求生命周期大致分为哪些阶段？
2️⃣ （简单）request 对象是如何在视图函数中被访问到的？为什么不用全局变量？
3️⃣ （简单）Flask 中 g 和 request 的区别是什么？分别适用于什么场景？
4️⃣ （中等）什么是应用上下文（Application Context）？它和请求上下文（Request Context）的核心区别是什么？
5️⃣ （中等）解释 Flask 是如何确保每个请求的上下文彼此隔离的？（关键词：Local / LocalStack）
6️⃣ （中等）讲一下 before_request、after_request、teardown_request 的执行顺序和触发时机。
7️⃣ （中等偏难）Flask 如何把视图函数的返回值（字符串 / dict / tuple）转换成 Response 对象？大致流程是什么？
8️⃣ （较难）Flask 是如何进行路由匹配和请求分发的？内部主要经历了哪些步骤？
9️⃣ （困难）讲一下 Flask 的整个请求流程，从 WSGI 服务器接收到请求开始，到返回响应结束，尽量按顺序描述。
🔟 （高难）解释 Flask 的 wsgi_app 和 dispatch_request 在请求处理流程中的角色、调用顺序和作用。


解答1️⃣: 
1. WSGI 服务器接收请求并交给 Flask 处理。
例如 gunicorn/uWSGI 调用 Flask 的 wsgi_app。

2. Flask 创建并推入应用上下文与请求上下文。
提供 current_app、g、request 等对象的隔离环境。

3. 进行路由匹配并执行请求钩子。
按顺序执行 before_request → 视图函数 → after_request。

4. 将视图函数的返回值转换为 Response 对象。
字符串、字典、元组都会被标准化为 Response。

5. 执行 teardown 钩子并弹出上下文。
teardown_request → teardown_appcontext。

6. WSGI 将 Response 数据返回给客户端。