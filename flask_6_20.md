Flask

在并发程序中每个视图函数都会看到属于自己的上下文，而不会出现混乱。

源码实现：

上下文的实现就比较清晰了：每次有请求过来的时候，flask 会先创建当前线程或者进程需要处理的两个重要上下文对象，把它们保存到隔离的栈里面，这样视图函数进行处理的时候就能直接从栈上获取这些信息

# 1.Flask 中请求上下文和应用上下文的区别和作用？

**两者区别：**  
请求上下文：保存了客户端和服务器交互的数据。  
应用上下文：flask 应用程序运行过程中，保存的一些配置信息，比如程序名、数据库连接、应用信息等。

两者作用：

请求上下文(request context)：

Flask从客户端收到请求时，要让视图函数能访问一些对象，这样才能处理请求。请求对象是一个很好的例子，它封装了客户端发送的HTTP请求。

要想让视图函数能够访问请求对象，一个显而易见的方式是将其作为参数传入视图函数，不过这会导致程序中的每个视图函数都增加一个参数，除了访问请求对象,如果视图函数在处理请求时还要访问其他对象，情况会变得更糟。为了避免大量可有可无的参数把视图函数弄得一团糟，flask使用上下文临时把某些对象变为全局可访问。

应用上下文(application context)：

它不是一直存在的，它只是request context 中的一个对 app 的代理(人)，所谓local proxy。它的作用主要是帮助 request 获取当前的应用，它是伴 request 而生，随 request 而灭的。

> 其他：

current_app、g 是应用上下文。  
request、session 是请求上下文。

手动创建上下文的两种方法：

1. with app.app_context() 

2. app = current_app._get_current_object()

# 2.Flask中数据库设置？

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:mysql@127.0.0.1:3306/test'

查询时会显示原始SQL语句

app.config['SQLALCHEMY_ECHO'] = True

# 3.常用的SQLAlchemy查询过滤器？

# 4.Flask中请求钩子的理解和应用？

请求钩子是通过装饰器的形式实现的，支持以下四种：  
1，before_first_request 在处理第一个请求前运行  
2，before_request:在每次请求前运行  
3，after_request:如果没有未处理的异常抛出，在每次请求后运行  
4，teardown_request:即使有未处理的异常抛出，在每次请求后运行  
应用：  
请求钩子

1. @api.after_request  

2. def after_request(response): 

3.    """设置默认的响应报文格式为 application/json""" 

4.    # 如果响应报文 response 的 Content-Type 是以 text 开头，则将其改为 

5.    # 默认的 json 类型 

6.    if response.headers.get("Content-Type").startswith("text"): 

7.     response.headers["Content-Type"] = "application/json" 

8.    return respon

# 5.__name__是什么？

**在Python中，__name__是一个内置变量，他的值取决于代码的运行方式。**

**当模块直接运行时，__name__的值为__main__.**

**当模块被导入时，__name__的值为模块的文件名(不含.py的后缀)**

# 6.Flask(_*name_*)中的__name__可以传入哪些值？

第一个参数是应用模块或者包的名称。 __name__ 是一个适用于大多数情况的快捷方式。有了这个参数， Flask 才能知道在哪里可以找到模板和静态文件等东西。

可以传入的参数：  
1，字符串：‘hello’,  
但是‘abc’,不行，因为abc是python内置的模块  
2，_*name*_，约定俗成  
不可以插入的参数  
1，python内置的模块，re,urllib,abc等  
2，数字

# 7.Flask 中的 g 的作用?

**主要用于在一次请求的处理过程临时存储数据**

**1跨函数共享数据**

**比如从路由函数到试图函数，中间件或自定义工具函数，如果传递临时数据，可通过g实现，避免参数层层传递。**

**2.临时存储请求相关数据**

**如存储数据库连接，确保同一请求内多次使用无需重复创建资源。**

**3.避免全局变量污染**

**g的生命周期仅限当前请求，请求结束后数据自动销毁，不会造成全局状态污染。**

**8. Flask 中上下文管理主要涉及到了那些相关的类?并 述类主要作用?**

RequestContext  #封装进来的请求（赋值给ctx）

AppContext      #封装app_ctx

LocalStack      #将local对象中的数据维护成一个栈（先进后出）

Local           #保存请求上下文对象和app上下文对象

**9. 在Flask中实现WebSocket需要什么组件?**

# gevent-websocket

flask-socketio

eventlet

**10. 解释Flask框架中的Local对象和threadinglocal对象的区别?**

# a.threading.local

作用：为每个线程开辟一块空间进行[数据存储](https://zhida.zhihu.com/search?content_id=195900705&content_type=Article&match_order=1&q=%E6%95%B0%E6%8D%AE%E5%AD%98%E5%82%A8&zhida_source=entity)(数据隔离)。

问题：自己通过字典创建一个类似于threading.local的东西。

storage = {

   4740: {val: 0},

   4732: {val: 1},

   4731: {val: 3},

   }

**11. SQLAlchemy 如何执行原生 SQL?**

使用execute方法直接操作SQL语句(导入create_engin、sessionmaker)

engine=create_engine('mysql://root:*****@127.0.0.1/database?charset=utf8')

DB_Session = sessionmaker(bind=engine)

session = DB_Session()

session.execute('alter table mytablename drop column mycolumn ;')

**12. 解释在 Flask 中如何处理路由。**

- 使用 @app.route("/") 装饰器来告诉 Flask URL "/" 匹配哪个函数
- 加入可变路径, 使用 < 和 > 表示
- 加入方法，使用 keyword parameters, 即 methods=["GET", "POST"]
13. 如何在 Flask 应用中实现数据库集成的？

pip install Flask-SQLAlchemy

**定义表**

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(80), unique=True, nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

shell种执行

*db.create_all()*

db.session.add(new_user)

db.session.commit()

User.query.all()

User.query.filter_by(username="xxx").first()

User.query.filter_by(username="xxx").order_by(model.Entry.amount.desc())

User.get([pk])

select(user_table).where(user_table.c.name == "spongebob")

db.session.delete(user)

db.session.commit()

**14.**如何使用 Flask-Migration

flask db migrate -m "Initial migration."

flask db upgrade

flask db downgrade

15. Flask 的蓝图（Blueprints）是什么，以及为什么要使用它们？

在 Flask 中，蓝图（Blueprints）是一种组织和重用代码的方式。

蓝图允许你将应用分割成不同的组件，每个组件都有自己的视图函数、模板、静态文件等。这种划分可以帮助你构建大型的、模块化的应用，并且保持代码的清晰和可维护性。

它能够帮助我们把最相关的代码模块化，并且模块与模块之间是相互调用。对于可能出现重复的路由，我们可以注册的过程中提供 prefix_url 的方式为每个模块提供独特的 url 地址。

这能帮助我们简化大型应用代码的管理成本。

**16**.解释 Flask 中的请求和响应对象

在 Flask 中，请求和响应对象是处理 HTTP 请求和生成 HTTP 响应的核心部分。Flask 使用 Werkzeug 库来提供请求和响应对象

flask.Request

- 请求方法: 可以通过 request.method 访问请求的方法，例如 GET, POST, PUT, DELETE 等。
- URL: request.path 返回请求的路径，而 request.url 返回包括查询字符串在内的完整 URL。
- 表单数据: 对于 POST 或 PUT 请求，表单数据可以通过 request.form 来访问。
- 查询字符串: 查询字符串可以通过 request.args 来访问。
- JSON 数据: 如果请求是一个 JSON 请求，那么可以通过 request.json 来访问 JSON 数据。
- 文件: 上传的文件可以通过 request.files 来访问。
- Cookies: 可以通过 request.cookies 来读取请求中发送的 cookies。
- Headers: 请求头可以通过 request.headers 来访问。
- query_string

flask.Response 响应对象代表服务器返回给客户端的 HTTP 响应。它包括状态码、响应头、响应体等信息。

- 字符串: Flask 会将字符串包装成一个带有 200 OK 状态码和 text/htmlMIME 类型的响应对象。
- 响应对象: 如果你创建了一个 Response 对象，可以直接返回它。这在需要更复杂的响应时非常有用。
- 元组: 你可以返回一个包含响应体、状态码和头部信息的元组。例如：return 'Hello World!', 200, {'Content-Type': 'text/plain'}。

**17、Flask 中 url_for 函数**作用,**和 redirect 区别？**

**通过视图函数的名称或蓝图名称来动态获取对应的URL，避免硬编码URL路径，提升代码的可维护性**

**若URL属于某个蓝图，需在函数名前加蓝图名称，假设蓝图名为api, 则url_for(‘api.index’)**

redirect 是重定向函数，输入一个 URL 后，自动跳转到另一个 URL 所在的地址。想跳转到另外一个试图函数，可以使用redirect(url_for('.user'))

**18.Flask中如何处理错误和异常？**

- **使用 try-except 语句**：  
  在视图函数中，可以使用 Python 的 try-except 语句来捕获可能发生的异常。

- **定义错误处理器**：  
  使用 @app.errorhandler() 装饰器来注册一个错误处理器函数，该函数负责处理特定类型的错误。当对应的错误发生时，Flask 会调用相应的错误处理器。

@app.errorhandler(404)

def page_not_found(error):

    return render_template('404.html'), 404

- **全局错误处理器**：  
  如果希望统一处理所有未知错误，可以使用 app.register_error_handler() 方法注册一个全局错误处理器。

@app.register_error_handler(Exception)

def handle_unhandled_exception(e):

    return 'An unexpected error occurred', 500

# 19.jwt结构:

JWT（JSON Web Token）由三部分组成，通过 . 分隔，结构如下：

- 头部（Header）：通常包含两部分信息，一是声明类型（即JWT），二是所使用的签名算法（如HMAC SHA256或RSA等），会被Base64Url编码。

- 载荷（Payload）：存放有效信息，即用户声明（如用户ID、角色等），同样会被Base64Url编码。

- 签名（Signature）：由头部、载荷的编码值，加上指定的密钥，通过头部声明的算法加密生成，用于验证令牌的完整性和真实性。

# 20.base64与base64url编码区别

**base64编码结果中会有+、/、=三个特殊字符，它们在url中属于特殊字符是直接无法传递的；**

**base64url其实就是把字符中的'+'和'/'分别替换成'-'和'_'，另外把末尾填充的‘=’去掉;其他都一样。**

# 21.为什么需要jwt?

使用Cookie的前提是需要同源，也就是渲染页面的域名必须和当前请求的域名相同，否则Cookie是不会生效的，举个例子，从百度服务器获取的Cookie，浏览器是不会提交到腾讯服务器的。

传统的网页，使用Cookie是没有问题的，但是如果开发前后端分离项目，就会有一些问题了。前后端分离项目在开发和生产环境中，极大可能是部署在不同的服务器上，也就是域名都不一样，这时候用Cookie就不太合适。为了解决同源策略的问题，我们就需要使用JWT

# 22.在flask种怎么使用jwt的？

Flask中，我们可以通过Flask-JWT-Extended来实现JWT功能**，**因为他封装了PyJWT库的使用方式，以及一些属性和装饰器，用起来更爽。

## 22.1 生成jwt：

我们可以使用create_access_token来创建一个token，在创建的时候，需要传入能识别此用户的identity

## 22.3. 验证jwt：

如果某个视图函数必须要验证完jwt后才能访问，那么可以使用jwt_required装饰器。然后在视图函数中，使用get_jwt_identity获取之前创建jwt时候传入的identity参数

## 22.4. 过期时间：

默认flask-jwt-extended的过期时间是15分钟，如果想要自己设置过期时间，那么可以在app.config中设置JWT_ACCESS_TOKEN_EXPIRES，比如设置30分钟，那么可以如下代码实现：

app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(minutes=30)

## 22.5 自动加载用户

在大多数 Web 应用程序中，获取受保护路由的访问用户信息是非常重要的。flask-jwt-extended 提供了一些回调函数，使得在使用 JWT 时可以实现无缝对接。

第一个是 @jwt.user_identity_loader ，在运行 create_access_token(identity=user) 创建 access_token 时会将 identity 的值回调到 user_identity_loader 函数内部，需要返回一个唯一值回来用作身份标识。 它将把用于创建 jwt 的 User 对象转换为 JSON 可序列化格式。

另一方面，当请求中出现 jwt 时，可以使用 @jwt.user_lookup_loader() 自动加载 User 对象。加载的用户可以通过 current_user 在受保护的路由中使用。

## 

原始手动加载的用户信息前，是传入username进行jwt编码的，传入的是一个字符串或者数字，并不是一个实例对象。

现在自动加载表面上看是传入User对象，背后实际上将User.id编码到jwt中，还是一个字符串或者数字。

## 22.6 部分保护路由

在某些情况下，无论请求中是否存在 JWT，你都希望使用相同的路由。在这些情况下，你可以将 `jwt_required()` 与 `optional=True` 参数一起使用

如果不存在 JWT，`get_jwt_identity()`、`current_user` 和 `get_current_user()` 将返回 `None`。如果请求中包含过期或无法验证的 JWT，仍会像往常一样返回错误。

**12. Flask的中间件是什么？如何使用中间件？**

**7. Flask 框架的优势?**

1.轻巧

2.简洁

3.扩展性强（个人认为最重要的特点）

4.核心（werkzeug和jinja2）jinja2就是指模板引擎。

浅拷贝和深拷贝的区别

主要区别在于对嵌套对象的复制方式，比如列表中的列表

浅拷贝：仅复制顶层对象，嵌套对象会共享内存地址

深拷贝：递归的复制所有层级的对象。新对象与原对象完全独立，不共享任何内存地址

在python中，浅拷贝通过copy.copy()或切片，字典.copy()等方式实现。深拷贝通过copy.deepcopy()实现

# 高阶函数

指输入的参数是函数，返回的结果也是函数

内置函数： map(), reduce()

列表的内置函数：

reverse()

sort()

字符串的内置函数： replace()

正则替换的内置函数：re.sub(匹配字符，替换字符，目标字符串，替换次数)



r、r+、rb、rb+文件打开模式的区别



1.r

r模式是只读模式，以该模式打开文件，只能从文件中读取内容，不能向文件中写入内容，文件的指针默认在文件的开始位置，一般用于文本类型的文件

2.r+

r+模式是追加模式，以该模式打开文件，既可以从文件中读取内容，也可以向文件中写入内容，文件的指针默认在文件的结束位置，一般用于文本类型的文件。

3.rb

rb模式是二进制形式的只读模式，以该模式打开文件，只能从文件中读取内容，不能向文件中写入内容。文件的指针默认在文件的开始位置，一般用于非文本类型的文件，如图片、视频、音频等。

4.rb+

rb+模式是二进制形式的追加模式，以该模式打开文件，既可以从文件中读取内容，也可以向文件中写入内容，文件的指针默认在文件的结束位置，一般用于非文本类型的文件。
