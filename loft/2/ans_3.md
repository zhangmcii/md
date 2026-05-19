# 面试前速记总纲

## 1. 项目一句话

这是一个把 Flask 单体后端，重构成接近 Clean Architecture 的项目。

核心目标：

- 控制器不写业务
- 业务不直接绑 ORM 和 Flask
- 基础设施可替换、可降级


## 2. 整体分层

| 层级 | 是什么 | 主要职责 | 位置 |
| --- | --- | --- | --- |
| API层 | 接口入口层 | 接请求、鉴权、调 service、返回响应 | `backend/app/api/` `backend/app/auth/views.py` |
| Service层 | UseCase / 应用层 | 编排完整业务流程 | `backend/app/services/` |
| Domain层 | 业务规则层 | 放规则、抽象接口、事务抽象 | `backend/app/domain/` |
| Repository层 | 数据访问抽象层 | 定义数据访问接口，隔离 ORM | 抽象：`backend/app/domain/*/repositories.py` 实现：`backend/app/infrastructure/repositories/sqlalchemy/` |
| Infrastructure层 | 技术实现层 | 实现数据库、Redis、JWT、Celery、Qiniu、SocketIO 等能力 | `backend/app/infrastructure/` |
| DTO / Schema层 | 数据传递与校验层 | Schema 校验输入，DTO 统一返回结构 | `backend/app/schemas/` `backend/app/application/dto/result.py` |
| Presenter层 | 输出映射层 | 把对象转成前端要的 JSON 结构 | `backend/app/presenters/api_assembler.py` |
| Policies | 规则函数 | 负责业务规则本身 | `backend/app/domain/*/policies.py` |
| Ports | 外部能力抽象 | 抽象 JWT、通知、存储、配置等能力 | `backend/app/domain/ports/` |
| Unit of Work | 事务边界抽象 | 统一控制 `flush / commit / rollback` | 抽象：`backend/app/domain/common/unit_of_work.py` 实现：`backend/app/infrastructure/repositories/sqlalchemy/unit_of_work.py` |


## 3. 一条主链路

```text
Request
-> API
-> Schema
-> Service
-> Policy / Domain
-> UnitOfWork
-> Repository
-> Infrastructure
-> Presenter
-> Response
```

发帖例子：

```text
POST /api/v1/posts
-> posts.py
-> PostService.create_post()
-> post policies
-> uow.posts
-> SqlAlchemyPostRepository
-> assembler
-> response
```


## 4. 最关键的架构点

- Blueprint 只做接口，不做业务中心
- Service 是 use case 编排层
- Domain 放规则和抽象
- Repository 隔离数据访问
- UoW 统一事务
- Port + Adapter 做依赖倒置
- Presenter 统一输出结构


## 5. capability / 降级 一句话

基础设施不是全有或全无，而是先探测 capability，再按状态决定正常运行还是降级运行。

核心文件：

- `backend/app/infrastructure/capabilities.py`
- `backend/app/infrastructure/startup_report.py`

典型降级：

- Redis 挂了 -> Cache 降级本地缓存
- Redis 挂了 -> Limiter 降级内存限流
- Redis 挂了 -> Celery 降级同步执行
- Redis 挂了 -> JWT 黑名单检查降级
- Qiniu 挂了 -> 上传/签名/删除能力降级


## 6. 一句话讲项目价值

这个项目真正的价值不是 CRUD，而是把一个 Flask 单体项目拆成清晰分层，并让外部依赖具备探测、降级和可替换能力。
