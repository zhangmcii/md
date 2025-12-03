
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