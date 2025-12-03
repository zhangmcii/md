
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

解答2️⃣: 
1. 在视图函数中能直接访问 request，因为它是一个 LocalProxy，会根据当前上下文定位到对应的 request 对象
2. Flask 使用 Werkzeug 的 Local / LocalStack 实现请求隔离。
3. 不能使用全局变量的原因是：数据在并发下会被不同请求覆盖。


解答3️⃣:
1. request 和 g 都是绑定在请求上下文中的 LocalProxy，并且“每个请求独立”。
2. request 用于访问请求相关的数据，而 g 用于在同一请求的不同函数之间临时存放自定义数据。
3. 两者在请求结束后都会被清理掉，不会跨请求共享。


解答4️⃣：
（1）为什么 Flask 需要两个上下文？（动机）
    1.Flask 是延迟创建 app 的框架（工厂模式常用）。
    2.需要在没有请求的场景也访问 app（如 CLI、shell、初始化扩展）。
    3.request 和 app 属于两种不同生命周期的对象，不能混在一起。
（2）两者分别包含什么？（本质差异）
（3）生命周期与 push/pop 顺序（关键）

Flask 将应用相关的数据放在 Application Context，将与 HTTP 请求相关的数据放在 Request Context。
应用上下文提供 current_app 和 g，主要解决工厂模式下无法直接访问 app 的问题，并让扩展能独立于请求运行。 请求上下文提供 request、session 等请求信息。
生命周期上 Flask 会先 push 应用上下文，再 push 请求上下文，请求结束后按相反顺序弹出，两者通过 LocalStack 保证每个请求独立。

解答5️⃣：
自己：使用Local / LocalStack来确保。Local类的实例是全局共享的，它内部维护的存储是按线程 / 协程隔离的
点评： 得分：7 / 10。 但是回答仍然 过于简短，缺少结构化解释，也没有点出 LocalProxy 的角色，同时对 Local 的工作机制描述不够完整。

Flask 使用 Werkzeug 的 Local 和 LocalStack 来隔离每个请求的数据。 Local 内部根据线程或协程 ID 存储不同请求的数据，保证互不干扰。
request、g 等对象实际上是 LocalProxy，它会根据当前上下文在 Local 中查找对应的真实对象。
通过 push/pop 上下文栈，Flask 在请求开始和结束时自动创建和销毁这些数据，从而实现请求级隔离。

解答6️⃣： 讲一下 before_request、after_request、teardown_request 的执行顺序和触发时机。
执行顺序: before_request -> after_request -> teardown_request
before_request在每次路由到对应视图函数前执行
after_request在每次请求结束后执行
teardown_request在弹出请求上下文前执行

优化版 更专业：
| 钩子               | 什么时候执行 | 是否必须返回 response  | 是否一定执行    |
| ---------------- | ------ | ---------------- | --------- |
| before_request   | 视图函数之前 | ❌ 可以返回，返回则中断流程   | 是         |
| after_request    | 视图函数之后 | ✔️ 必须返回 response | 否（异常时不执行） |
| teardown_request | 上下文销毁时 | ❌ 返回值被忽略         | 是         |


解答7️⃣:
视图函数的返回值会被 make_response() 统一转换为 Response 对象。
1）返回字符串（str）
含义：字符串会被当作 响应体（body）

2）返回字典（dict）
含义：Flask 会自动调用 jsonify()，把字典转换为 JSON 格式的响应。

3）返回元组（tuple）
元组用于 同时指定：响应体、状态码、响应头。

4）返回 Response 对象
你也可以直接手动构造 Response：

解答8️⃣ : Flask 是如何进行路由匹配和请求分发的？内部主要经历了哪些步骤？
自己：route装饰器的内部调用了add_url_rule()来添加URL规则，在Werkzeug中进行URL匹配。
得分： 6 / 10。   回答仍然 太简略，缺少面试官期望的 清晰的流程 、核心概念关键点之间的因果关系

1. @app.route() 只是一个语法糖，它会把视图函数注册成一个 URL 规则，并最终调用 add_url_rule()。
2. add_url_rule() 会创建一个新的 Rule 对象，加入到 URL Map 中，同时将 endpoint（默认是函数名）绑定到该视图函数。
3. 请求到来时，Flask 使用 Werkzeug 的 URL Map 和 Rule 进行 URL 匹配，通过 MapAdapter.match() 找到对应的 endpoint，最终调用绑定的视图函数。

解答9️⃣ :讲一下 Flask 的整个请求流程，从 WSGI 服务器接收到请求开始，到返回响应结束，尽量按顺序描述。
WSGI 服务器接收 HTTP 请求并构造 environ，然后调用 Flask 应用。
Flask 创建应用上下文和请求上下文，并进行 URL 路由匹配。
Flask 按 before_request → 视图函数 → after_request 顺序处理请求。
处理结果被转换为 Response 对象，通过 start_response 返回给 WSGI 服务器。
WSGI 服务器将响应数据转成 HTTP，返回给客户端，Flask 最后清理上下文。


解答🔟 : 解释 Flask 的 wsgi_app 和 dispatch_request 在请求处理流程中的角色、调用顺序和作用。
wsgi_app 是 Flask 的 WSGI 入口，负责整个请求周期，
包括创建上下文、before_request、路由匹配、after_request 等。
dispatch_request 是 wsgi_app 调用的内部方法，
它只负责根据路由匹配结果执行视图函数并返回原始结果。

顺序是：wsgi_app → dispatch_request → make_response → 清理上下文。



