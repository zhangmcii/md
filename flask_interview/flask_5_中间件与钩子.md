
1.（简单）Flask 中有哪些常用的请求钩子（Request Hooks）？它们的执行时机是什么？
2.before_request 和 before_first_request 的区别是什么？在实际项目中分别适用于哪些场景？
3.Flask 中如何编写一个 WSGI 中间件？它与 Flask 的请求钩子有什么关键区别？
4.（困难）假设你要实现一个 统一的请求耗时统计系统，需满足以下要求：
- 不修改每个视图函数
- 统计整个请求生命周期的耗时
- 包含 WSGI 层与 Flask 内部处理的时间
- 能在高并发场景下保证正确性
你会选择钩子、中间件，还是二者结合？请说明具体实现方式与原因。



解答1:
before_request()： 视图函数之前
after_request()： 视图函数之后
teardown_request()：上下文销毁时
before_first_request()： 应用启动后接收到的第一个请求前

评分：7 / 10。 但你有一些不完整、不够精确甚至容易误导面试官追问的点，因此是中上水平。
① after_request 的时机描述不够准确 ② teardown_request 不是“上下文销毁时”这么简单 ③ before_first_request 并不是“应用启动后”

优秀答案：
① 列出每个钩子名 + 精确执行时机（要说明是否异常时执行、是否只执行一次）
② 说明调用顺序（很加分）
③ 简短说明一个关键差异（体现深度）

请求钩子包括：
before_request：每次请求在进入视图函数前执行，可提前返回响应。
before_first_request：应用第一次处理 HTTP 请求前执行一次（多进程下每个进程执行一次）。
after_request：视图函数正常返回后执行，用于修改响应，不在异常情况下执行。
teardown_request：请求结束、上下文弹出前执行，无论是否异常都会执行。
调用顺序为：before_first_request → before_request → 视图函数 → after_request → teardown_request。
（它们依赖请求上下文。 它们可以访问 request、session、g）

解答2:
before_request：每次请求在进入视图函数前执行，可提前返回响应，适用于对请求预处理。
before_first_request：应用第一次处理 HTTP 请求前执行一次（多进程下每个进程执行一次），适用于做初始化操作。
评分：6 / 10。 但仍然缺少关键点，难以满足“面试中等偏上”的要求。


before_request：在请求上下文建立后、路由匹配完成后、视图函数执行前运行。 可返回 Response 来中断请求流程，跳过视图函数。适用于鉴权、参数检查、全局前置处理。
before_first_request：在应用处理第一个请求之前运行一次。但在多进程部署（如 gunicorn 多 worker）下，每个进程都会执行一次，因此不适合作为全局共享初始化。适合做轻量的应用级初始化。
二者区别在于：before_request 每次请求都会触发，而 before_first_request 只在应用进程第一次请求前触发。



解答3: Flask 中如何编写一个 WSGI 中间件？它与 Flask 的请求钩子有什么关键区别？

WSGI 中间件是一个标准 WSGI 应用（callable），包装 Flask 应用本身。
它接受 (environ, start_response)，可以修改入站 environ、出站响应，并在 Flask 内部逻辑运行前后生效。它不依赖 Flask 的 request/g/session，
因此适用于处理跨应用级别的功能如代理头修正、GZip 压缩、全局日志等。

Flask 请求钩子（before_request / after_request / teardown_request）运行在 Flask 内部流程中，并依赖请求上下文。
它们可以访问 request、session、g，并允许提前返回 Response 来中断视图函数。适用于每次请求的预处理、鉴权和响应后清理。

核心区别：中间件工作在 WSGI 层，是整个应用的外层包装；钩子工作在 Flask 层，是框架处理流程中的局部扩展点。

解答4:
（困难）假设你要实现一个 统一的请求耗时统计系统，需满足以下要求：
- 不修改每个视图函数
- 统计整个请求生命周期的耗时
- 包含 WSGI 层与 Flask 内部处理的时间
- 能在高并发场景下保证正确性
你会选择钩子、中间件，还是二者结合？请说明具体实现方式与原因。



二者结合。WSGI 层处理时间： 需要中间件在flask内部逻辑运行前后统计，   Flask 内部处理时间：需要钩子函数操作
具体实现：
在请求进入中间件时，记录开始时间，出站时记录结束时间，这样得到请求的整个耗时t1
在before_request()中记录请求进入flask的开始时间，在teardown_request()中记录结束时间，这样得到flask内部处理时间t2
WSGI 层处理时间t3 = t1 - t2。
在高并发场景下使用请求id来标识每个请求的耗时。

评分：8.5 / 10



要同时测量 WSGI 层耗时与 Flask 内部处理耗时，需要使用“中间件 + 请求钩子”组合方案。
WSGI 中间件运行在 Flask 之前与之后，它能包裹整个应用，因此适合统计完整的请求耗时（t1）。
在 middleware.call 的开始和结束使用 time.perf_counter() 记录时间即可。

Flask 请求钩子运行在 Flask 内部的 RequestContext 中，因此 only 它能准确记录 Flask 内部处理耗时（t2）。
在 before_request 记录开始，在 teardown_request 记录结束时间。

最终：
total = t1
flask_time = t2
wsgi_overhead = total - flask_time


为了在高并发中追踪每个请求的耗时，可在中间件生成 X-Request-ID 并写入 environ，再在钩子函数中取出同一个 request-id 进行关联。
总结：
- 中间件 = 整体耗时，作用于 Flask 外层
- 钩子函数 = Flask 内部耗时，依赖请求上下文
- 差值即为 WSGI 层或代理层的额外开销
