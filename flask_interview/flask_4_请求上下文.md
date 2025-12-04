1.（简单）Flask 中有哪些常见的上下文对象？它们分别在什么时候可用？
2.Flask 为什么需要 “请求上下文（Request Context）”？ 如果没有请求上下文，request、session 为什么不能直接作为全局变量使用？
3.它们的生命周期顺序是什么？为什么 Flask 需要区分这两种上下文？
4.（困难）
请解释：
current_app 是如何从应用上下文中获取当前应用实例的？
Flask 是如何通过 Local / LocalStack 实现上下文对象的线程隔离？
在 WSGI 流程中，上下文的 push / pop 发生在什么时候？
（提示：需要提到 _request_ctx_stack / _app_ctx_stack 的角色或概念）


解答1:
请求上下文和应用上下文。
请求上下文包含请求相关的信息。同时提供request, session对象。需要在请求上下文中使用，比如视图函数中调用。如果在请求上下文外，需要在with app.test_request_contex()代码块使用 
应用上下文包含应用数据。同时提供current_app，g对象（保存用户自定义数据），需要在应用上下文中使用，比如视图函数中使用，如果在应用上下文外，，需要在with app.app_context()代码块使用 
评分：7.5 / 10


Flask 有两种主要的上下文：
(1) 请求上下文（RequestContext）
封装一次 HTTP 请求相关的数据，如 request、session。它在 WSGI 请求到来时创建并 push，整个请求结束时 pop。

(2) 应用上下文（AppContext）
封装应用级对象，例如 current_app、g。当 RequestContext push 时会自动 push AppContext。

Flask 通过 Local 和 LocalProxy 将这些对象暴露为“伪全局变量”，实现线程隔离。
如果要在请求/视图之外使用它们，需要用 app.app_context() 或 test_request_context() 手动创建上下文。

解答2:
视图函数中会用到请求相关的信息，请求上下文避免了往每个视图函数中注入参数的做法。
request,session是Localproxy，会在请求上下文中去local中寻找对应的真实对象，请求上下文内部使用了Local,LocalProxy实现了每个请求独立，
如果没有请求上下文，request,session在请求并发时拿到其他请求的数据。
评分：8 / 10。 已经达到“中级工程师”水准。 
但
① 少了对 “Local 是怎么隔离线程/协程” 的一句话说明 
② 没说明 request/session 是如何“懒加载”真实对象的（在属性访问时，通过 _get_current_object() 动态定位当前上下文的真实对象。）
③ 没提到 request/session 在请求开始时由 RequestContext 绑定

Flask 使用请求上下文是为了让 request、session 能够在全局直接使用，但又保证每个请求的数据相互隔离。
若没有请求上下文，它们只能是全局变量，在多线程/协程并发时会互相覆盖数据。

Flask 使用 Local 存储真实对象，LocalProxy 在访问属性时根据线程/协程 ID 动态查找当前请求对应的对象。
RequestContext.push() 会把 request/session 绑定到 Local，这样视图函数里可以直接访问，而不会出现数据串请求问题。

解答3:
生命周期上 Flask 会先 push 应用上下文，再 push 请求上下文，请求结束后按相反顺序弹出，两者通过 LocalStack 保证每个请求独立。
因为两者对应不同的生命周期，属于两个过程。
评分：5.5 / 10。 但整体内容太少，缺少面试官最看重的解释性内容（为什么区分、两者解耦了什么、底层是如何关联的、为什么不能合并等），显得非常不够深入。


Flask 把上下文分成应用上下文（AppContext）和请求上下文（RequestContext）。  
AppContext 封装应用级对象（current_app、g），RequestContext 封装请求级对象（request、session）。  [① 定义和作用]

RequestContext 内部持有 AppContext 的引用，因此 push RequestContext 时 Flask 会确保先 push AppContext。  [② 关系：谁包含谁？]
完整流程是：push AppContext → push RequestContext，结束时按相反顺序 pop。 [③ 生命周期顺序（含关键函数）]

之所以要区分两种上下文，是因为应用资源和请求资源的生命周期不同：应用上下文可用于 CLI 或后台任务，而请求上下文只存在于一次 HTTP 请求期间。 [④ 设计原因：为什么要分开？（最高频考点！）]
Local/LocalProxy 再结合 LocalStack 让这些对象在并发环境下保持隔离。

解答4:
current_app时Localproxy, 通过 _get_current_object() 动态定位当前上下文的真实对象。
Local 内部根据线程或协程 ID 存储不同请求的数据，保证互不干扰。
在请求进入flask中，执行push,载请求结束时，执行pop
评分：4.5 / 10。 整体 过于片段化，缺少关键流程、关键类之间的关系、LocalProxy 如何取值、LocalStack 如何工作、为什么需要这一整套设计等。


current_app 是一个 LocalProxy，它并不存储真实对象，而是持有一个取值函数，例如 lambda: _app_ctx_stack.top.app。
每次访问 current_app 时，LocalProxy 都会调用这个函数，从 LocalStack 的顶部取出当前请求对应的 AppContext 实例。 [① current_app 是 LocalProxy：动态属性访问器]

Flask 使用 Local 和 LocalStack 来保证并发隔离。Local 内部基于 contextvars（或线程局部变量）为每个请求维护独立的数据空间，而 LocalStack 在此基础上提供 push/pop，用于管理上下文栈。 [② LocalStack + Local 的并发隔离机制]

当请求进入 Flask 时，会创建 RequestContext；如果当前没有 AppContext，则自动创建一个。push 的过程分别将 AppContext 与 RequestContext 压入它们各自的 LocalStack；
pop 则反向弹出。这样，current_app、request、session 等 LocalProxy 才能通过 LocalStack.top 找到属于当前请求的正确对象。 [③ push/pop 的完整流程]

通过 Local/LocalStack/LocalProxy 的组合，Flask 实现了无需显式传参却又线程安全的上下文管理。 [④ 为什么 Flask 要设计 Local/LocalProxy]