
1.（简单）Flask 中配置项通常存放在哪里？你常用的加载配置的方式有哪些？
2.app.config.from_object()、from_pyfile()、from_mapping() 各自适用于什么场景？
3.请解释 Flask 中配置加载顺序（例如默认配置、环境变量、实例配置）。如果多处同时定义了同一个配置项，最终采用哪一个？
4.（困难）在使用应用工厂模式（Application Factory）时，你如何组织配置文件？
请解释：
- 工厂模式中配置加载的推荐方式
- 在不同环境（dev/test/prod）中如何优雅切换配置
- 如何避免循环引用与可维护性问题

解答1:
配置项通常放在app.config中。 
两种加载配置的方式
1.将配置变量作为类属性，然后在工厂函数中调用app.config.from_object(config)
2.使用.env配置文件，在启动文件中使用load_dotenv()加载配置

得分：6 / 10。  存在不少遗漏与不准确之处，因此只能给中等分。

配置项最终存放在 app.config 中，它是一个 dict-like 的 Config 对象。
Flask 提供多种加载方式，包括：from_pyfile() 从 Python 文件加载，from_object() 从类加载，from_mapping() 从字典加载，以及 from_envvar() 用环境变量指定配置文件。
另外，也可以使用 python-dotenv 加载 .env 到环境变量，再通过 os.getenv() 或 from_envvar() 注入配置。


解答2:
app.config.from_object()适用于类配置
from_pyfile()适用于从其他格式的文件来加载配置
from_mapping()适用于从字典加载

评分：7 / 10 。  方向基本正确，但表达太简略，也有两处不准确点。遗漏了优缺点，也没有提到加载原理

from_object() 用于基于类的配置结构，尤其适合 dev/test/prod 多环境继承。
from_pyfile() 用于从 Python 文件加载配置，是实际项目中最常见的方式，适合保存密钥与生产配置。
from_mapping() 用于从字典加载配置，常用于测试或动态构造配置。



解答3:
依次加载默认配置、环境变量、实例配置。多处同时定义了同一个配置项，采用最后一个定义的 
评分：5 / 10 。 你答对了“后加载会覆盖先加载的”，但整体 过于简单、不准确，也遗漏了多个关键点。


Flask 会先加载框架内置的默认配置， 再加载应用代码显式加载的配置，包括from_object()，from_pyfile()，from_mapping()，from_envvar()。
如果你从实例目录加载配置（通过 Flask(__name__, instance_relative_config=True))， 实例目录中的配置文件会覆盖前面的配置。
覆盖原则（重要） ：Flask 的配置是一个 dict-like 对象，配置项 后加载的值会覆盖先加载的值。
注意 ：Flask 不会自动读取环境变量进 config，除非使用 from_envvar() 或手动读取。

第4题：
在应用工厂模式中，配置通常使用“类配置 + 多环境继承”的方式组织：
一个默认配置类作为基础，development、production、testing 等配置类通过继承来扩展。
在 create_app() 中，通过 app.config.from_object() 根据环境变量动态加载对应的配置类，并使用 instance folder 的 config.py 进一步覆盖敏感配置。
这样既可实现环境切换，又能避免配置与 app 之间的循环引用，同时保持代码结构清晰、可维护。