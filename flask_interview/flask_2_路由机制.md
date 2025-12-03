1.(简单)@app.route("/hello") 的作用是什么？它在 Flask 内部做了哪些事情？

2.请解释 add_url_rule() 的 3 个关键参数（rule、endpoint、view_func）分别是什么作用？

3.Flask 是如何进行 URL 匹配的？请描述它如何通过 Werkzeug 完成路由查找。

4.(困难)为什么 Flask 需要 endpoint？它和视图函数名、URL 之间是什么关系？ 在什么场景下需要手动指定 endpoint？


解答1:
自己：请求url为/hello导向该函数 。将该函数注册到路径"/hello"，调用add_url_route()函数来将函数对应url注册到flask。
得分：6 / 10
回答中的问题：
1）函数名写错
2）缺少 endpoint、视图函数绑定等信息
3）未说明装饰器本质
4）语言表达不够精确

@app.route("/hello") 的作用是将视图函数绑定到 URL“/hello”。
装饰器内部会调用 add_url_rule()，创建一个 URL Rule 并注册到 Flask 的 url_map，同时生成 endpoint（默认等于函数名）， 把 endpoint 与视图函数绑定。
最终，Flask 才能在请求到达时根据 URL 查找到对应的视图函数。

解答2. 非得
rule是Rule对象，endpoint默认等于函数名，view_func就是视图函数
总分：5.5 / 10
问题：表述太过简略，缺少作用说明
     rule 的解释不准确（不是 Rule 对象，而是一个字符串）
     对参数之间的关系没有描述
     面试官期待你解释“为什么需要它们”，而不是仅仅一句话


rule 是 URL 路径字符串（如 "/hello"），Flask 会根据它创建 URL Rule 并加入路由表中。
endpoint 是这个 URL 的内部名称（默认等于视图函数名），用于反向 URL 生成并保证唯一性。
view_func 是实际处理请求的视图函数，Flask 会在请求匹配后通过 endpoint 查找到并调用它。

解答3:
Flask 的路由系统基于 Werkzeug 的 URL Map。每次应用启动时，所有的 URL 都通过 add_url_rule() 转换为 Rule，并注册到 app.url_map。
当收到请求，Flask 会用 url_map.bind_to_environ(environ) 生成 MapAdapter，并调用它的 match() 方法，根据 URL、HTTP 方法、转换器等规则匹配最佳的 Rule。
匹配成功后返回 endpoint 和 URL 参数；匹配失败则抛出 404、405 等异常，由 Flask 捕获并处理。


解答4: 为什么 Flask 需要 endpoint？它和视图函数名、URL 之间是什么关系？ 在什么场景下需要手动指定 endpoint？
endpoint 是 Flask 为每个路由生成的内部名称，默认等于视图函数名，用来唯一标识一个视图。
路由匹配成功后，Flask 会根据匹配到的 endpoint 从 app.view_functions 中找到对应的视图函数并调用，因此最终流程是 URL → endpoint → view_func。
endpoint 还用于反向 URL 生成（url_for）。当多个 URL 指向同一个视图函数，或在蓝图中存在函数名冲突时，需要手动指定 endpoint。


请求处理流程，包含你要求的底层关键函数与调用关系：
[1] HTTP 请求进入
    ↓
[2] WSGI Server (gunicorn / waitress / Werkzeug) 接收请求
    ↓  调用
    ↓  Flask.__call__(environ, start_response)
    ↓
[3] Flask.wsgi_app(environ, start_response)
    ↓
    ├─ 创建应用上下文 & 请求上下文
    │    ↓
    │  Flask.request_context(environ)
    │    ↓
    │  RequestContext.push()
    │    - 将 request, session, g 绑定到 LocalStack
    │
    └─ 进入调度流程
         ↓
[4] Flask.full_dispatch_request()
         ↓
    ├─ 执行 before_request
    │      ↓ before_request_funcs
    │
    └─ 核心：dispatch_request()
           ↓
[5] Flask.dispatch_request()

    # 路由匹配开始 ----------------------------------------------------
           ↓
    [5.1] adapter = app.url_map.bind_to_environ(environ)
           ↓
    [5.2] endpoint, view_args = adapter.match()
             ↓（底层流程）
             - MapAdapter.match()
             - 遍历所有 Rule：url_map._rules
             - Rule.match(path)
                 * 匹配 HTTP method
                 * 匹配 host / subdomain
                 * 使用编译好的正则 self._regex
                 * 抽取 variable converters (<int:id>)
             ↓ 命中后返回 (endpoint, args)
    # 路由匹配结束 ----------------------------------------------------


           ↓
[6] view_func = app.view_functions[endpoint]

           ↓
[7] response = view_func(**view_args)

           ↓
[8] response = Flask.make_response(response)
       - 字符串 → Response
       - dict → jsonify → Response
       - tuple → (body, status, headers)
           ↓
[9] 执行 after_request
       ↓ after_request_funcs

           ↓
[10] 执行 teardown_request
        ↓ teardown_request_funcs
        （无论是否异常都执行）

           ↓
[11] RequestContext.pop()
        - 弹出 request / app context
        - 清除 LocalStack 中的数据

           ↓
[12] 返回 Response 给 WSGI 服务器

           ↓
[13] WSGI Server 发送 HTTP 响应给客户端
