

flask 0.1

> v0.1中 只有请求上下文，没有应用上下文

引入了Werkzeug的LocalStack类，并未直接用Werkzeug的Local类。



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





WSGI =  WSGI 服务器 + WSGI 应用框架 ， Flask 是一个 WSGI 应用框架。

1. 浏览器或其他客户端发出 HTTP 请求。

2. WSGI 服务器接收请求。

3. WSGI 服务器将 HTTP 数据转换为 WSGI `environ` 字典。

4. WSGI服务器使用 `environ` 调用 WSGI 应用程序。

5. Flask ,即 WSGI 应用程序，执行其所有内部处理来路由请求到视图函数， 处理错误等。

6. Flask 将视图函数返回转换为 WSGI 响应数据，并将其传递给 WSGI 服务 器。

7. WSGI 服务器创建并发送 HTTP 响应。

8. 客户端接收 HTTP 响应。





### 中间件

 WSGI 应用(Flask)是以某种方式运行的可调用对象。

中间件是一个 WSGI 应用程序，它包装了另一个 WSGI 应用程序，它类似于 Python 装饰器。最外层的中间件将由服务器调用。它可以修改传递给它的数据，然后调用被它包装 WSGI 应用程序（或进一步的中间件），以此类推。它可以获取该调用的返回值并进一步修改它。

从 WSGI 服务器的角度来看，只有一个直接调用的 WSGI 应用程序。通常， Flask 是中间件链末端的“真正”应用程序。但即使是 Flask 也可以调用进一 步的 WSGI 应用程序，尽管这是一个高级、不常见的用例。



# 应用上下文：

目的：

Flask应用对象具有诸如config之类的属性，这些 属性对于在视图和 CLI commands中访问很有用。但是，

1. 在项目中的模块内导入 `app` 实例容易导致循环导入问题。

2. 当使用 [应用程序工厂方案](https://dormousehole.readthedocs.io/en/latest/patterns/appfactories.html)或编写可重用的 [blueprints](https://dormousehole.readthedocs.io/en/latest/blueprints.html) 或 [extensions](https://dormousehole.readthedocs.io/en/latest/extensions.html) 时， 根本不会有应用程序实例导入。



Flask 通过 *应用上下文* 解决了这个问题。不是直接引用一个 `app` ，而是使用 [`current_app`](https://dormousehole.readthedocs.io/en/latest/api.html#flask.current_app "flask.current_app") 代理，该代理指向处理当前活动的应用。



处理请求时， Flask 自动 *推送* 应用情境。在请求期间运行的视图函数、错误 处理器和其他函数将有权访问 [`current_app`](https://dormousehole.readthedocs.io/en/latest/api.html#flask.current_app "flask.current_app") 。

## 生命周期：

当 Flask 应用开始处理请求时，它会推送应用上下文和 请求上下文。当请求结束时，它会在请求上下文中弹 出，然后在应用上下文中弹出。通常，应用上下文将具有与请求相同的生命周期。

## 手动推送情境：

如果在配置应用时发现错误（例如初始化扩展时），那么可以手动推送上下文。 因为你可以直接访问 `app` 。在 `with` 块中使用 [`app_context()`](https://dormousehole.readthedocs.io/en/latest/api.html#flask.Flask.app_context "flask.Flask.app_context") ，块中运行的所有内容都可以访问 [`current_app`](https://dormousehole.readthedocs.io/en/latest/api.html#flask.current_app "flask.current_app") 。



    def create_app():
        app = Flask(__name__)
    
        with app.app_context():
            init_db()
    
        return app
