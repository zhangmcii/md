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

当 Flask 应用开始处理请求时，它会推送请求上下文，这也会推送应用上下文。当请求结束时，它会弹出请求上下文，然后弹出应用上下文。

### 开始与结束

请求上下文在Flask类的wsgi_app方法的开头创建，结尾调用了auto_pop()方法来移除。也就是说，请求上下文的生命周期开始于请求进入调用wsgi_app()时，结束于响应生成后。

```python
 def wsgi_app(self, environ, start_response):
        ctx = self.request_context(environ)
        error = None
        try:
           ...
        finally:
            if self.should_ignore_error(error):
                error = None
            ctx.auto_pop(error)
```

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

在分派请求并生成和发送响应之后，会弹出请求上下文，然后弹出应用上下文。在 紧临弹出之前(在pop()方法中调用的)，会执行 [`teardown_request()`](https://dormousehole.readthedocs.io/en/latest/api.html#flask.Flask.teardown_request "flask.Flask.teardown_request") 和 [`teardown_appcontext()`](https://dormousehole.readthedocs.io/en/latest/api.html#flask.Flask.teardown_appcontext "flask.Flask.teardown_appcontext") 函数。即使在调度期间发生未处理的异 常，也会执行这些函数。

### 关于代理

Flask 提供的一些对象是其他对象的代理。每个工作线程都能以相同的方式访问代理，但是在后台每个工作线程绑定了唯一对象。

如果您需要访问被代理的源对象，请使用 `_get_current_object()` 方法:

    app = current_app._get_current_object()
    my_signal.send(app)

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

# 应用程序生命周期

WSGI = WSGI 服务器 + WSGI 应用框架 ， Flask 是一个 WSGI 应用框架。

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

这个特性经常被用来解耦程序的功能，这样可以将不同功能分开维护，达到分层的目的

#### 中间件实战：

使用类定义的中间件必须实现__call__方法，接收environ和start_response对象作为参数，最后调用传入的可调用对象，并传递这两个参数。如下样板代码：

```python
class MyMiddleware(object):
    def __call__(self, environ, start_response):
        pass

app = Flask(__name__)
# 如果我们自己实现了中间件，那么最佳的方式是嵌套在FLask的wsgi_app对象上
app.wsgi_app = MyMiddleware(app.wsgi_app)
```

下面这个MyMiddleware中间件其实并没有做什么，只是向首部添加了一个无意义的自定义字段。最后传入可调用对象hello函数来实例化这个中间件（这里的hello函数相当于Flask的可调用对象wsgi_app），获得包装后的程序实例wrapped_app。

```python
from wsgiref.simple_server import make_server

def hello(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/html')]
    start_response(status, response_headers)
    return [b'<h1>Hello, web!</h1>']

class MyMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        def custom_start_response(status, headers, exc_info=None):
            headers.append(('A-CUSTOM-HEADER', 'Nothing'))
            return start_response(status, headers)

        return self.app(environ, custom_start_response)

wrapped_app = MyMiddleware(hello)
server = make_server('localhost', 5000, wrapped_app)
server.serve_forever()
```

注意：

- socketio.run(wrapped_app, host=os.getenv('FLASK_RUN_HOST'), port=os.getenv('FLASK_RUN_PORT') ) 会报错。

- 用 socketio.run() 时，传入 app，不要传入中间件对象。

- 如需中间件和 socketio 共存，请考虑用 Flask 的 before_request/after_request 钩子 或 Flask 插件 实现你的功能。

- 需要中间件时，建议用专业 WSGI 服务器部署

# 扩展

扩展和我们编写的程序很相似。事实上，Flask扩展就是Python库，只不过它使用“Flask的语言”说话。比如，它也像我们的程序一样使用Flask提供的诸多功能：它们可以创建蓝本，获取配置，加载静态文件，使用上下文全局变量

Flask扩展通常分为两类：一类是纯功能的实现，比如提供用户认证功能的Flask-Login；另一类是对已有的库和工具的包装，比如Flask-SQLAlchemy就包装了SQLAlchemy

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



### 问题

每一个蓝本都是一个休眠的操作子集，只有注册到程序上才会获得生命。那么，这种休眠状态是如何实现的呢？

- **定义蓝图时**：不直接注册路由到应用，而是记录 “如何注册”。
- **注册蓝图时**：执行之前记录的所有 “注册操作”。



当你使用 `@bp.route` 等装饰器时，蓝图实际上将注册逻辑封装为函数：

```python
def route(self, rule, **options):
    def decorator(f):
        endpoint = options.pop("endpoint", f.__name__)
        
        # 定义一个延迟执行的函数
        def register(state):
            state.app.add_url_rule(
                rule,
                f"{self.name}.{endpoint}",  # 添加蓝图前缀
                f,
                **options
            )
            
        # 将延迟函数记录到列表中
        self.record(register)
        return f
    return decorator
```

当蓝图被注册到应用时（`app.register_blueprint(bp)`），Flask 会执行所有记录的延迟函数，即此时将蓝图中定义的路由、错误处理、模板过滤器等信息合并到应用实例中。：

```python
def register(self, app, options, first_registration=False):
    # 创建包含应用上下文的状态对象
    state = self.make_setup_state(app, options, first_registration)
    
    # 执行所有延迟函数
    for deferred in self.deferred_functions:
        deferred(state)  # 传入应用上下文
```

这里的 `state` 对象包含了应用实例（`state.app`），因此延迟函数可以通过它访问应用并注册路由：

```python
# 回顾之前的延迟函数示例
def register(state):
    state.app.add_url_rule(
        rule='/users/<id>',
        endpoint='user.get_user',  # 蓝图名称.端点名
        view_func=get_user
    )
```

#### 延迟函数执行的时序：

定义蓝图时：

1. 用户调用 @bp.route('/users/')
2. 蓝图将注册逻辑封装为 register(state) 函数
3. 将 register 函数添加到 deferred_functions 列表

注册蓝图时（app.register_blueprint(bp)）：

1. Flask 创建包含应用信息的 state 对象
2. 遍历 deferred_functions 列表
3. 依次执行每个函数：register(state)
4. 在函数内部，通过 state.app 访问应用并注册路由



### 综合实战问题：从程序开始运行，第一个请求进入，再到返回生成的响应的过程

当WSGI服务器接收到请求时，会调用Flask应用程序实例app。Flask类实现了__call__()方法，当程序实例被调用时会执行这个方法，而这个方法内部调用了Flask.wsgi_app()方法

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

>  总结上面：
> 
> 请求进入，wsgi服务器调用应用程序实例app。Flask类实现了__call__()方法，当程序实例app被调用时会执行这个方法，而这个方法内部调用了wsgi_app()方法。推送请求上下文，接着执行full_dispatch_request()，它负责`完整地请求调度`，包括请求的预处理，分配到视图函数，将视图函数返回转换为 WSGI 响应数据。最后wgsi_app()函数将响应对象传递给 WSGI 服务器生成响应。

### 详情： 路由处理、请求和响应对象的封装

#### 路由：

url规则--端点--视图函数

##### 注册路由：

route装饰器的内部调用了add_url_rule()来添加URL规则，所以注册路由也可以直接使用add_url_rule实现。

```python
    def add_url_rule(self, rule, endpoint=None, view_func=None,
                     provide_automatic_options=None, **options):
        # 设置方法和端点
        ...
        ...
        rule = self.url_rule_class(rule, methods=methods, **options)
        rule.provide_automatic_options = provide_automatic_options

        self.url_map.add(rule)
        if view_func is not None:
            old_func = self.view_functions.get(endpoint)
            if old_func is not None and old_func != view_func:
                raise AssertionError('View function mapping is overwriting an '
                                     'existing endpoint function: %s' % endpoint)
            self.view_functions[endpoint] = view_func
```

重点在于这两行：

self.url_map.add(rule)
self.view_functions[endpoint] = view_func

url_map是Werkzeug的Map类实例，它存储了URL规则和相关配置

rule是Werkzeug提供的Rule实例，其中保存了端点和URL规则的映射关系。

view_functions则是Flask类中定义的一个字典，它存储了端点和视图函数的映射关系

你可以发现端点是如何作为中间人连接起URL规则和视图函数的。前者存储了URL到端点的映射关系，后者则存储了端点和视图函数的映射关系

##### url匹配：

在Werkzeug中进行URL匹配

Map.bind()方法和Map.bind_to_environ()都会返回一个MapAdapter对象，它负责匹配和构建URL。

MapAdapter类的match()方法用来判断传入的URL是否匹配Map对象中存储的路由规则, 匹配成功后会返回一个包含URL端点和URL变量的元组。

> 设置return_rule=True可以在匹配成功后返回表示URL规则的Rule类实例。这个Rule实例包含endpoint属性，存储着匹配成功的端点值。

MapAdapter类的build()方法用于创建URL，我们用来生成URL的url_for()函数内部就是通过build()方法实现的。

**实际问题**：客户端发送请求时，Flask是如何根据请求的URL找到对应的视图函数的？

在上一节分析Flask中的请求响应循环时，我们曾说过，请求的处理最终交给了dispatch_request()方法。

```python
 def dispatch_request(self):
        req = _request_ctx_stack.top.request
        if req.routing_exception is not None:
            self.raise_routing_exception(req)
        rule = req.url_rule

        if getattr(rule, 'provide_automatic_options', False) \
           and req.method == 'OPTIONS':
            return self.make_default_options_response()

        return self.view_functions[rule.endpoint](**req.view_args)
```

dispatch_request()： 实现了从请求的URL找到端点，再从端点找到对应的视图函数并调用的过程

在注册路由时，由Rule类表示的rule对象由route()装饰器传入的参数创建。而这里则直接从请求上下文对象(_request_ctx_stack.top.request)的url_rule属性获取。可以得知，URL的匹配工作在请求上下文对象中实现。

> 创建请求上下文时，会将rule对象保存在 req.rule_map属性中，rule实例保存着该请求对应的端点。

```python
class RequestContext(object):

    def __init__(self, app, environ, request=None):
        self.app = app
        if request is None:
            request = app.request_class(environ)
        self.request = request
        self.url_adapter = app.create_url_adapter(self.request)
        ...
        # 匹配请求到对应的视图函数
        self.match_request()  

    def match_request(self):
        try:
            url_rule, self.request.view_args = \
                self.url_adapter.match(return_rule=True)
            self.request.url_rule = url_rule
        except HTTPException as e:
            self.request.routing_exception = e
```

可以看到url_rule属性就在这个方法中创建。match_request()方法调用了self.url_adapter.match(return_rule=True)来获取url_rule和view_args

```python
class Flask(_PackageBoundObject):
    ...
    def create_url_adapter(self, request):
        if request is not None:
            # 如果子域名匹配处于关闭状态（默认值）
            # 就在各处使用默认的子域名
            subdomain = ((self.url_map.default_subdomain or None)
                         if not self.subdomain_matching else None)
            return self.url_map.bind_to_environ(
                request.environ,
                server_name=self.config['SERVER_NAME'],
                subdomain=subdomain)

        if self.config['SERVER_NAME'] is not None:
            return self.url_map.bind(
                self.config['SERVER_NAME'],
                script_name=self.config['APPLICATION_ROOT'],
                url_scheme=self.config['PREFERRED_URL_SCHEME'])
```

我们知道url_map属性是一个Map对象，可以看出它最后调用了bind()或bind_to_environ()方法，最终会返回一个MapAdapter类实例。

match_request()方法通过调用MapAdapter.match()方法来匹配请求URL，设置return_rule=True可以在匹配成功后返回表示URL规则的Rule类实例。这个Rule实例包含endpoint属性，存储着匹配成功的端点值。

在dispatch_request()最后这一行代码中，通过在view_functions字典中根据端点作为键即可找到对应的视图函数对象，并调用它：

```Python
self.view_functions[rule.endpoint](**req.view_args)
```

这时代码执行流程才终于走到视图函数中。

> `总结`：
> 
> 所以，当你启动Flask应用程序时，会将route装饰器修饰的视图函数,放在url_map的Map实例中，保存着url规则和端点的对应关系，view_functions变量保存着端点和视图函数的对应关系。
> 
> 当请求进入时，在创建请求上下文过程中，会通过Flask.create_url_adapter()方法调用bind()或bind_to_environ()方法，返回一个MapAdapter类实例;最后调用match_request()返回表示URL规则的Rule类实例, 这个Rule实例包含endpoint属性，存储着匹配成功的端点值，最终保存在请求上下文的RequestContext.request.url_rule变量中。
> 
> 在dispatch_request()函数中顺利通过当前请求上下文变量 req获得该请求对应的端点，再从view_functions字典中以端点为键找到对应的视图函数并调用。
> 
> 至此，Flask完成了根据请求的URL找到对应的视图函数，并调用该视图函数的过程。

# 这一系列事物为什么会存在？

请求上下文，程序上下文，Local（本地线程），LocalStack（本地堆栈），LocalProxy（本地代理）？

1)需要保存请求相关的信息——有了请求上下文。

2)为了更好地分离程序的状态，应用起来更加灵活——有了程序上下文。

3)为了让上下文对象可以在全局动态访问，而不用显式地传入视图函数，同时确保线程安全——有了Local（本地线程）​。

4)为了支持多个程序——有了LocalStack（本地堆栈）​。

5)为了支持动态获取上下文对象——有了LocalProxy（本地代理）​。

6)……

7)为了让这一切愉快的工作在一起——有了Flask。
