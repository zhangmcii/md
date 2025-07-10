flask 0.1

> v0.1中 只有请求上下文，没有应用上下文

引入了Werkzeug的LocalStack类，并未直接用Werkzeug的Local类。

# 请求上下文

    class _RequestContext(object):
        def __init__(self, app, environ):
            self.app = app
            self.url_adapter = app.url_map.bind_to_environ(environ)
            self.request = app.request_class(environ)
            self.session = app.open_session(self.request)
            self.g = _RequestGlobals()
            self.flashes = None
    
        def __enter__(self):
            _request_ctx_stack.push(self)
    
        def __exit__(self, exc_type, exc_value, tb):
            if tb is None or not self.app.debug:
                _request_ctx_stack.pop()

请求上下文类，包含了所有请求相关信息。他被创建于请求的开始，然后被压入’_request_ctx_stack‘的栈中，在请求的结束被移除。

比如当前线程号为th_123， 此时LocalStack中的Local数据大致为： 

```
'__storage__' ：{
    'th_123': {'stack': [ <__main__._RequestContext object at 0x103342780> ]}
}
```

Flask类中的请求上下文函数

    class Flask(object):
        def request_context(self, environ):
            return _RequestContext(self, environ)

从被给的环境中创建一个请求上下文，然后把它绑定到当前上下文。需要用`with`代码块包裹。

### 解释

请求上下文在请求期间跟踪请求级数据。不是将请求对象传递给请求期间运行的每个函数，而是访问request和session代理。 推送请求上下文时会推送相应的应用上下文。

因为 *工作者* （取决于服务器的线程，进 程或协程）一次只能处理一个请求，所以在该请求期间请求数据可被认为是该工作者的全局数据。

### 用途

当Flask应用处理请求时，它会根据从WSGI服务器收到的环境创建一个Request对象。

处理请求时，Flask自动推送请求上下文。在请求期间运行的视图函数，错误处理器和其他函数将有权访问request代理，该请求代理指向当前请求的请求对象。

### 生命周期

当 Flask 应用开始处理请求时，它会推送请求上下文，这也会推送应用上下文。当请求结束时，它会弹出请求上下文，然后弹出应用程序上下文。

#### 顺序总结

1. **创建请求上下文**（但未入栈）。
2. **检查应用上下文**：
   - 若不存在，则创建应用上下文并**压入应用栈**。
3. **压入请求上下文**到请求栈。
4. **处理请求**（执行视图函数等）。
5. **弹出请求上下文**。
6. **弹出应用上下文**（如果是隐式创建的）。

应用上下文入栈 → 请求上下文入栈 → 请求上下文弹出 → 应用上下文弹出

`所以，栈顶元素是该线程当前处理的请求上下文`

上下文对于每个线程时唯一的。request不能传递给另外一个线程，另一个线程将拥有不同的上下文堆栈，并且不会知道父线程指向的请求。

### 手动推送上下文

如果尝试在请求上下文之外访问request或任何使用它的东西，那么会 收到这个错误消息：

    RuntimeError: Working outside of request context.

这通常表示您试图使用功能需要一个活动的 HTTP 请求。

通常只有在测试代码期望活动请求时才会发生这种情况。一种选择是使用 [`测试客户端`](https://dormousehole.readthedocs.io/en/latest/api.html#flask.Flask.test_client "flask.Flask.test_client") 来模拟完整的请求。或者，可以在 `with` 块中使用 [`test_request_context()`](https://dormousehole.readthedocs.io/en/latest/api.html#flask.Flask.test_request_context "flask.Flask.test_request_context") ，块中运行的所 有内容都可以访问请求，并填充测试数据：

    def generate_report(year):
     format = request.args.get("format")
     ...
    
    with app.test_request_context(
     "/make_report/2017", query_string={"format": "short"}
    ):
     generate_report()

### 上下文是如何工作的？

处理每个请求时都会调用Flask.wsgi_app()方法，他在请求期间管理上下文。当上下文被压入堆栈时，依赖它们的代理是可用的，并指向堆栈顶部项目的信息。

当请求开始时，将创建并推送Request Context，如果该应用 程序的上下文尚不是顶级上下文，则该请求会首先创建并推送 AppContext 。在推送这些上下文时，current_app、g、request和session代理可用于处理请求的 原始线程。

在分派请求并生成和发送响应之后，会弹出请求上下文，然后弹出应用上下文。在 紧临弹出之前，会执行 [`teardown_request()`](https://dormousehole.readthedocs.io/en/latest/api.html#flask.Flask.teardown_request "flask.Flask.teardown_request") 和 [`teardown_appcontext()`](https://dormousehole.readthedocs.io/en/latest/api.html#flask.Flask.teardown_appcontext "flask.Flask.teardown_appcontext") 函数。即使在调度期间发生未处理的异 常，也会执行这些函数。

### 关于代理

Flask 提供的一些对象是其他对象的代理。每个工作线程都能以相同的方式访问代理，但是在后台每个工作线程绑定了唯一对象。

如果您需要访问被代理的源对象，请使用 `_get_current_object()` 方法:

    app = current_app._get_current_object()
    my_signal.send(app)

# 应用程序生命周期

WSGI =  WSGI 服务器 + WSGI 应用框架 ， Flask 是一个 WSGI 应用框架。

1. 浏览器或其他客户端发出 HTTP 请求。

2. WSGI 服务器接收请求。

3. WSGI 服务器将 HTTP 数据转换为 WSGI `environ` 字典。

4. WSGI服务器使用 `environ` 调用 WSGI 应用程序。

5. Flask ,即 WSGI 应用程序，执行其所有内部处理来路由请求到视图函数， 处理错误等。

6. Flask 将视图函数返回转换为 WSGI 响应数据，并将其传递给 WSGI 服务器。

7. WSGI 服务器创建并发送 HTTP 响应。

8. 客户端接收 HTTP 响应。
   
   

步骤4,5,6就是对应Flask.wsgi_app()函数



# 中间件

 WSGI 应用(Flask)是以某种方式运行的可调用对象。

中间件是一个 WSGI 应用程序，它包装了另一个 WSGI 应用程序，它类似于 Python 装饰器。最外层的中间件将由服务器调用。它可以修改传递给它的数据，然后调用被它包装 WSGI 应用程序（或进一步的中间件），以此类推。它可以获取该调用的返回值并进一步修改它。

从 WSGI 服务器的角度来看，只有一个直接调用的 WSGI 应用程序。通常， Flask 是中间件链末端的“真正”应用程序。但即使是 Flask 也可以调用进一 步的 WSGI 应用程序，尽管这是一个高级、不常见的用例。

# 应用上下文：

### 目的：

Flask应用对象具有诸如config之类的属性，这些 属性对于在视图和 CLI commands中访问很有用。但是，

1. 在项目中的模块内导入 `app` 实例容易导致循环导入问题。

2. 当使用 [应用程序工厂方案](https://dormousehole.readthedocs.io/en/latest/patterns/appfactories.html)或编写可重用的 [blueprints](https://dormousehole.readthedocs.io/en/latest/blueprints.html) 或 [extensions](https://dormousehole.readthedocs.io/en/latest/extensions.html) 时， 根本不会有应用程序实例导入。

Flask 通过 *应用上下文* 解决了这个问题。不是直接引用一个 `app` ，而是使用 [`current_app`](https://dormousehole.readthedocs.io/en/latest/api.html#flask.current_app "flask.current_app") 代理，该代理指向处理当前活动的应用。

处理请求时， Flask 自动 *推送* 应用上下文。在请求期间运行的视图函数、错误 处理器和其他函数将有权访问 [`current_app`](https://dormousehole.readthedocs.io/en/latest/api.html#flask.current_app "flask.current_app") 。

## 生命周期：

当 Flask 应用开始处理请求时，它会推送应用上下文和 请求上下文。当请求结束时，它会在请求上下文中弹 出，然后在应用上下文中弹出。通常，应用上下文将具有与请求相同的生命周期。

## 手动推送上下文：

如果尝试在应用上下文之外访问 [`current_app`](https://dormousehole.readthedocs.io/en/latest/api.html#flask.current_app "flask.current_app") ，或其他任何使用它的东西，则会看到以下错误消息：

    RuntimeError: Working outside of application context.

这通常意味着您试图使用功能需要以某种方式与当前的应用程序对象进行交
互。要解决这个问题，请使用 app.app_context()设置应用上下文。

比如：使用flask_mail扩展来发送邮件，执行mail.send(msg)时，需要使用

`with app.app_context()`来包裹。因为send函数内用到了current_app

如果在配置应用时发现错误（例如初始化扩展时），那么可以手动推送上下文。 因为你可以直接访问 `app` 。在 `with` 块中使用 [`app_context()`](https://dormousehole.readthedocs.io/en/latest/api.html#flask.Flask.app_context "flask.Flask.app_context") ，块中运行的所有内容都可以访问 [`current_app`](https://dormousehole.readthedocs.io/en/latest/api.html#flask.current_app "flask.current_app") 。

    def create_app():
        app = Flask(__name__)
    
        with app.app_context():
            init_db()
    
        return app

> with app.app_context():做了什么？
> 
> 实例化了一个AppContext类，__enter__入栈，__exit__出栈

### 存储数据：

应用上下文是在请求和CLI命令期间存储公共数据的好地方（比如在app变量中存储数据），FLask提供类g对象，与应用上下文具有相同的生命周期。

> `g` 中的数据在应用上下文结束后丢失，因此它不是在请求之间存储数据的恰当位置。使用 [`session`](https://dormousehole.readthedocs.io/en/latest/api.html#flask.session "flask.session") 或数据库跨请求存储数据。

##### 用法：

1. `get_X()` 创建资源 `X` （如果它不存在），将其缓存为 `g.X` 。

2. `teardown_X()` 关闭或以其他方式解除分配资源（如果存在）。它被注 册为 [`teardown_appcontext()`](https://dormousehole.readthedocs.io/en/latest/api.html#flask.Flask.teardown_appcontext "flask.Flask.teardown_appcontext") 处理器。
   
    from flask import g
   
    def get_db():
   
        if 'db' not in g:
            g.db = connect_to_database()
       
        return g.db
   
    @app.teardown_appcontext
    def teardown_db(exception):
   
        db = g.pop('db', None)
       
        if db is not None:
            db.close()

>  注释： `当应用上下文被弹出时，应用将调用 teardown_appcontext()注册的函数。`
> 
> @app.teardown_appcontext装饰器，是把`被装饰函数`添加到Flask类的teardown_appcontext_funcs列表变量中，在应用上下文弹出前，会倒序遍历该列表，执行每个函数。

总结： 1.应用上下文有两个变量，current_app和g 

2.应用上下文具有与请求相同的生命周期。

    

### 综合实战问题： 多线程场景下的上下文管理

假设有 4 个工作线程处理 10 个请求，流程是什么？

答： 4个线程处理4个请求，剩余6个请求等待线程空闲。

其中，每个线程在处理请求时，创建独立的上下文，将上下文压入当前线程的栈。此时内存中的栈结构： 

    '__storage__' : {'线程1': {'stack': [AppCtx_A, RequestCtx_A]},
                     '线程2': {'stack': [AppCtx_B, RequestCtx_B]},
                     '线程3': {'stack': [AppCtx_C, RequestCtx_C]},
                     '线程4': {'stack': [AppCtx_D, RequestCtx_D]}
                    }

代理对象的指向堆栈顶部项目的信息：线程1中的request指向RequestCtx_A，线程2中的request指向RequestCtx_B，以此类推。

> 注意，在Flask中，Local类的实例是全局共享的，它内部维护的存储是**按线程 / 协程隔离**的。这是理解上下文机制的关键。
> 
> **源码证据**：
> 
> - `_request_ctx_stack` 和 `_app_ctx_stack` 都是全局单例。
> - 这些栈内部使用同一个 `Local` 实例来存储数据。

### 原始疑问：

假设同一刻来了10个请求，只有4个工作线程，那么有4个上下文被压入栈，这时候每个工作线程都指向堆栈顶部的元素吗？

错误分析：

1.每个线程都有自己独立的栈实例，互不干扰。

2.每个线程中的 `request` 代理对象指向该线程上下文栈的栈顶元素，互不干扰

3.线程 1 无法访问线程 2 的上下文，确保了请求数据的隔离性。

4.当线程处理完请求后，上下文栈弹出，线程可以被复用处理其他请求（此时会创建新的上下文）。

| 上下文   | 用途                                          | 针对的问题                                            | 生命周期                                | 可访问的代理对象         | 上下文外访问代理对象                                                    | 手动推送上下文                                                  |
| ----- | ------------------------------------------- | ------------------------------------------------ | ----------------------------------- | ---------------- | ------------------------------------------------------------- | -------------------------------------------------------- |
| 请求上下文 | 将request代理作为全局变量，供请求期间运行的视图函数，错误处理器，其他函数访问。 | 1.避免将请求对象作为函数参数，传递给请求期间运行的每个函数。                  | 与单个 HTTP 请求绑定，请求开始时创建，请求结束时销毁。      | request, session | 会收到错误消息：RuntimeError: Working outside of request context.     | 1.使用 `测试客户端`来模拟完整的请求.      2.with test_request_context() |
| 应用上下文 | 使用current_app代理，供请求期间运行的视图函数，错误处理器，其他函数访问。  | 1.在模块中导入app实例导致的循环引入问题。2.在使用应用工厂方案时根本就没有app实例导入。 | 隐式创建（伴随请求上下文）。通常应用上下文将具有与请求相同的生命周期。 | current_app, g   | 会收到错误消息：RuntimeError: Working outside of application context. | with app.app_context():                                  |

当flask应用接受到一个请求时，请求上下文和应用上下文创建的顺序是什么？

1. **创建请求上下文**（但未入栈）。
2. **检查应用上下文**：
   - 若不存在，则创建应用上下文并**压入应用栈**。
3. **压入请求上下文**到请求栈。
4. **处理请求**（执行视图函数等）。
5. **弹出请求上下文**。
6. **弹出应用上下文**（如果是隐式创建的）。

综上： 应用上下文入栈 → 请求上下文入栈 → 请求上下文弹出 → 应用上下文弹出

# 蓝图

### 错误处理器：

- @蓝图.errorhandler()
  作用范围：仅处理当前蓝图中发生的错误  
  应用场景：当错误发生在蓝图的路由函数中时，才会触发该错误处理函数。  

- @蓝图.app_errorhandler()
  作用范围：处理整个应用的错误，无论错误发生在哪个蓝图或路由中。  
  应用场景：当需要在蓝图中注册一个全局错误处理函数时使用。

### 为什么要使用蓝图？

用途：

- 把一个应用分解为一套蓝图。这是针对大型应用的理想方案：一个项目可以实 例化一个应用，初始化多个扩展，并注册许多蓝图。

- 在一个应用的 URL 前缀和（或）子域上注册一个蓝图。 URL 前缀和（或）子 域的参数成为蓝图中所有视图的通用视图参数（缺省情况下）。

- 使用不同的 URL 规则在应用中多次注册蓝图。

- 通过蓝图提供模板过滤器、静态文件、模板和其他工具。蓝图不必执行应用或视图函数。

- 当初始化一个 Flask 扩展时，为以上任意一种用途注册一个蓝图。

Flask 中的蓝图不是一个可插拨的应用，因为它不是一个真正的应用，而是一套可以注册在应用中的操作，并且可以注册多次

缺点： 一旦应用被创建后，只有销毁整个应用对象才能注销蓝图。

#### 基本概念：

在蓝图被注册到应用之后，所要执行的操作的集合。当分配请求时， Flask 会把蓝图和视图函数关联起来，并生成两个端点之间的 URL。

### 操作实例

    # 创建蓝图
    from flask import Blueprint
    
    simple_page = Blueprint('simple_page', __name__,
                            template_folder='templates')
    
    @simple_page.route('/<page>')
    def show(page):
        return 2
    
    
    # 注册蓝图
    from flask import Flask
    from yourapplication.simple_page import simple_page
    
    app = Flask(__name__)
    app.register_blueprint(simple_page, url_prefix='main')

### 蓝图资源

蓝图还可以用于提供资源。有时候，我们仅仅是为了使用一些资源而使用蓝图。

### 蓝图资源文件夹

和普通应用一样，蓝图一般都放在一个文件夹中。虽然多个蓝图可以共存于同一 个文件夹中，但是最好不要这样做。







### 综合实战问题：从程序开始运行，第一个请求进入，再到返回生成的响应的过程



当WSGI服务器接收到请求时，会调用Flask程序实例app。Flask类实现了__call__()方法，当程序实例被调用时会执行这个方法，而这个方法内部调用了Flask.wsgi_app()方法

> 这里将WSGI程序实现在单独的方法中，而不是直接实现在__call__()方法中，主要是为了在方便附加中间件的同时保留对程序实例的引用。

```python
  def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)
  
  
  def wsgi_app(self, environ, start_response):
        ctx = self.request_context(environ)
        error = None
        try:
            try:
                ctx.push()
                response = self.full_dispatch_request()
            except Exception as e:
                error = e
                response = self.handle_exception(e)
            except:
                error = sys.exc_info()[1]
                raise
            return response(environ, start_response)
        finally:
            if self.should_ignore_error(error):
                error = None
            ctx.auto_pop(error)
```

  wsgi_app()方法中的try...except...语句是重点。它首先尝试从Flask.full_dispatch_request()方法获取响应，如果出错那么就根据错误类型来生成错误响应。

#### 请求进入

Flask.full_dispatch_request()负责`完整地请求调度`。

```python
 def full_dispatch_request(self):
        self.try_trigger_before_first_request_functions()
        try:
            request_started.send(self)
            rv = self.preprocess_request()
            if rv is None:
                rv = self.dispatch_request()
        except Exception as e:
            rv = self.handle_user_exception(e)
        return self.finalize_request(rv)
```

1.preprocess_request()方法对请求进行预处理(request preprocessing)，这会执行所有使用before_request钩子注册的函数。

2.接着，请求分发的工作会进一步交给dispatch_request()方法，它会匹配并调用对应的视图函数，获取其返回值，在这里赋值给rv，

3.最后，接收视图函数返回值的finalize_request()会使用这个值来生成响应。



#### 响应返回

接收到视图函数返回值的finalize_request()函数负责生成响应，即请求的最终处理

```python
    def finalize_request(self, rv, from_error_handler=False):
        response = self.make_response(rv)
        try:
            response = self.process_response(response)
            request_finished.send(self, response=response)
        except Exception:
            if not from_error_handler:
                raise
            self.logger.exception('Request finalizing failed with an '
                                  'error while handling an error')
        return response
```



1.这里使用Flask类中的make_response()方法生成响应对象，但这个make_response并不是我们从flask导入并在视图函数中生成响应对象的make_response 。

> 我们平时使用的make_response是helpers模块中的make_response()函数，它对传入的参数进行简单处理，然后把参数传递给Flask类的make_response方法并返回

2.除了创建响应对象，这段代码主要调用了process_response()方法处理响应。这个响应处理方法会在把响应发送给WSGI服务器前执行所有使用after_request钩子注册的函数。另外，这个方法还会根据session对象来设置cookie

3.返回作为响应的response后，代码执行流程就回到了wsgi_app()方法，最后返回响应对象，WSGI服务器接收这个响应对象，并把它转换成HTTP响应报文发送给客户端。



总结上面：请求进入，wsgi服务器调用应用程序实例app。Flask类实现了__call__()方法，当程序实例app被调用时会执行这个方法，而这个方法内部调用了wsgi_app()方法。

推送请求上下文，接着执行full_dispatch_request()，它负责`完整地请求调度`，包括请求的预处理，分配到视图函数，将视图函数返回转换为 WSGI 响应数据。最后wgsi_app()函数将响应对象传递给 WSGI 服务器生产成响应，WSGI 服务器创建并发送 HTTP 响应到客户端。





详情： 路由处理、请求和响应对象的封装
