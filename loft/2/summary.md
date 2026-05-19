API层：就是接请求、做鉴权、读参数、调 service、返回统一响应。接口层主要在 `app/api` 和 `app/auth`。
Services层： 负责业务编排。这一层最像 Clean Architecture 里的 use case。解决“一个需求如何串起权限、事务、仓储、通知”的问题
domain层：负责业务规则与抽象，解决“规则本身是什么、依赖应该长什么样”的问题。这里放了几类关键内容。第一类是 policies，也就是业务规则，比如发帖内容怎么校验、帖子类型怎么归一化、摘要怎么生成。第二类是 repository interface，也就是业务需要什么数据访问能力，但不关心怎么实现。第三类是 ports，比如 JWT、通知、存储、配置、在线状态这些外部能力接口。第四类是 unit of work 抽象，用来表达事务边界。
		policies：业务规则，比如发帖内容怎么校验、帖子类型怎么归一化、摘要怎么生成	
		repository interface:  也就是业务需要什么数据访问能力，但不关心怎么实现
		ports: 比如 JWT、通知、存储、配置、在线状态这些外部能力接口
		 unit of work 抽象:  用来表达事务边界。
	
infrastructure层：这里去实现前面那些抽象，包括 SQLAlchemy 仓储实现、JWT 适配器、Redis 适配器、Qiniu 存储、Celery 通知派发、SocketIO 服务等。也就是说，高层定义规则和接口，低层负责接真实世界。


DTO/Schema层：校验输入，避免业务层直接处理脏数据。
Repository层：定义数据访问能力，而不是数据访问细节。
presenters层 ：负责出参组装，解决“ORM对象/领域对象如何变成前端需要的 JSON 结构”的问题。

UnitOfWork 负责事务提交、回滚、flush。 `Service -> UnitOfWork -> Repository -> ORM` 的链路

ports，比如 JWT、通知、存储、配置、在线状态这些外部能力接口