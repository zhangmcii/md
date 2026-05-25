---
name: third-party-api-batch-probe
description: 当用户需要"批量调第三方/竞品 API、跑离线评测集、对比多个 provider、压测某类 AI/风控接口"时使用。本 skill 不是"默认最重方案"，而是帮 AI 在工程质量与实现复杂度之间做动态平衡——根据规模、风险、是否评测/压测，自动匹配 Level 0~2 的合适形态。优先减少无效调用、避免过早框架化。
allowed-tools: Read, Write, Edit, Bash
triggers:
  - 帮我写脚本调一下 xxx 接口跑批
  - 批量调第三方/竞品 API
  - 跑一批样本过 xx 模型/风控/审核接口
  - 多个 provider 横向对比 / 评测
  - 压测某类 AI 接口
  - 用 xx API 给一批数据打标
non-triggers:
  - 单次/少量调用验证 → 直接写最简 demo，不用本 skill
  - 在线实时服务 / websocket / 强事务 → 不适用
  - UI 流式应用 → 不适用
---

# 第三方 API 批量调用类脚本的工程范式

> 本 skill 是**默认参考**，不是必须模板。当任务的特殊性与本 skill 的某条规则冲突时，**优先服从任务**。生成的脚本不必把所有章节都用上，也不必长得像同一套脚手架——保留 AI 的判断力比保持风格统一重要。

---

## 核心决策优先级（规则冲突时按这个序）

当本 skill 不同章节的建议互相打架，或某条建议会让代码变笨，按下面顺序取舍：

1. **不要丢数据** — raw response、中间结果、日志要落盘可追溯
2. **不要拖垮对端接口** — 限流、超时、错误分类
3. **不要浪费调用成本** — dry-run、去重、提前过滤、快速失败
4. **不要让单任务拖垮整批** — 异常隔离、结构化 fail
5. **不要过度工程化** — 没用上的机制就删掉
6. **代码应容易人工修改与调试** — 线性、可 grep、能 rerun 单条
7. **架构优雅排在最后** — 美观让位于以上六条

> 规则太多时，记住前三条就够。后面的章节都是在这三条之上展开。

---

## 0. 先判等级（Complexity Tiering）

生成代码前先在脑内做这道题：

| 维度 | 取值 |
|---|---|
| 任务数 | <50 / 50~5k / >5k |
| provider 数 | 1 / 多 / 用户明确说要扩展 |
| 运行时长 | 几分钟 / 小时级 / 跨天 |
| 用途 | 临时验证 / 标准批跑 / 评测对比 / 压测 |
| 接口计费？ | 否 / 是 |

按下表选 **Level**，不要无脑套最重方案：

### Level 0 — 临时验证 / 一次性脚本
触发条件（任一即可）：任务数 < 50，单 provider，跑一次就丢，或用户明确说"简单点 / 快速验证"。

**核心目标是降低理解成本**，不是保持架构一致性。`async` 不等于专业；同步代码够用就用同步。

可选最简形态（按场景挑一个）：
- 同步 `requests` / `httpx` + 普通 `for` 循环 + `time.sleep` 做退避（任务少、耗时短时**首选**）
- 同步 + `concurrent.futures.ThreadPoolExecutor`（需要点并发但不想引 async）
- `asyncio` + `gather`（IO 密集、任务多、耗时长时再考虑）

需要的只有：
- 单请求 timeout
- 朴素 retry（2~3 次足够，可不写退避）
- `print` 即可，不必上 logging

**不要**默认引入：provider 抽象、checkpoint、shard、metrics、tracing、熔断、限速、payload 预览、流水号 CSV、独立 config 模块、目录拆分、`logging.basicConfig` + 文件日志。

形态偏好：**单文件、≤150 行、线性流程**。配置直接写常量在文件顶部，需要时用户自己改。

### Level 1 — 标准批跑（默认大多数评测/打标场景落这里）
触发条件：50~5k 任务，单/少量 provider，需要复跑/抽检结果。

在 Level 0 基础上启用：
- 配置化（关键参数走 env / CLI，启动 fail-fast 校验）
- 边跑边落 JSONL（断点可续：跳过已存在 task_id）。**写文件时启用行缓冲**：`open(path, 'a', encoding='utf-8', buffering=1)`，或每次 `write()` 后 `f.flush()`，确保 OOM / kill -9 时已跑完的数据不会卡在 OS buffer 里丢失。
- 错误分类：网络/5xx 重试，4xx 直接 fail，不无脑重试
- 结构化日志：`[ok]/[hit]/[fail]/[timeout] task_id ...`，可 grep
- payload 预览 + dry-run 开关（接口计费时强烈推荐）
- 输入去重（按内容 hash 跳过重复样本）

仍**不需要**：tracing、adaptive concurrency、shard、熔断、Provider 抽象类。

### Level 2 — 长跑 / 压测 / 多 provider 评测 / 生产级
触发条件：>5k 任务、跨天、压测、多 provider 对比、接口高额计费。

再加：
- shard / range 续跑（`--shard i/N` 或按 id 区间）
- 自适应并发（连续 429/5xx 自动降并发，恢复后回升）
- 熔断（连续失败 N 次暂停 M 秒）
- 令牌桶 QPS 限速；压测时统计 P50/P95/P99
- graceful shutdown：捕获 SIGINT，停止派发新任务，等已发出的任务收尾或超时。**注意跨平台**：`loop.add_signal_handler` 在 Windows 下不可用（会抛 `NotImplementedError`），优先用 `try / except KeyboardInterrupt` 包住主调度循环；需要信号支持时按 `sys.platform` 分支处理，避免脚本在 Windows 上启动即崩。
- 简单 tracing：每 task 携带 `trace_id`，记录每次重试的耗时、错误码
- metrics 汇总：成功率、错误分布、延迟分位、各 provider 横向对比表

只有此层才考虑引入 Provider 抽象 / 多文件结构。

---

## 1. 避免过早框架化

**只在以下情况**引入 Provider 抽象类 / `providers/` 目录 / registry：
- 当前就要接 ≥2 个 provider，或
- 用户明确说"以后会加更多 provider"。

否则优先：
- 单文件、函数式：`build_payload()` / `call_api()` / `parse_result()` 三个函数足够。
- 清晰的分区注释代替目录拆分。
- 不写抽象基类，不写注册表，不为"未来可能"预留。

判断标准：**如果删掉抽象后代码更短更清楚，就不要那个抽象。**

### 1.1 依赖极简化

Level 0/1 阶段，除核心出网库（`httpx` / `requests` / `aiohttp`）外，**优先用标准库手写几行**，不要为了一个小功能引第三方包：

- 重试 / 退避 → 自己写 `for + sleep`，不要 `tenacity`。
- 限速 / 并发 → `asyncio.Semaphore` 或简易令牌桶，不要 `ratelimit` / `aiolimiter`。
- 进度 → `print` 或一行计数日志，不要默认 `tqdm`（在文件日志里是乱码）。
- 配置 → `os.getenv` + 顶部常量，不要 `pydantic-settings` / `dynaconf`。
- 重试装饰器、retry policy DSL、AOP 风格的拦截器 → 一律不要。

理由：脚本生命周期短，依赖越少 → 别人接手越快、环境问题越少、版本坑越浅。Level 2 才考虑视情况引入。

---

## 2. 默认机制（适用于 Level 1+，Level 0 按需裁剪）

下面写"推荐"而非"必须"。Level 0 可全部跳过。

- **并发限流**：`asyncio.Semaphore`，并发数从 env 读，默认保守。
- **统一 POST 包装**：所有出网走同一函数，集中处理 timeout / 重试 / 错误分类。
- **重试**：指数退避（如 2/4/8s），区分错误类型；耗尽不抛，而是返回 `{"error": ..., "attempts": N}`。
- **超时**：单请求 timeout 必显式设置；异步长任务另设总 deadline。
- **失败隔离**：单 task 异常用 try/except 包成 fail 结果，不拖垮整批。
- **进度可见**：每个 task 完成打一行带状态标签的日志。

---

## 3. 输出策略（按场景挑，不要全开）

**默认只输出当前用途真正需要的文件。** 不要无脑三件套。

| 用途 | 推荐输出 |
|---|---|
| 人工抽检 / 给业务看 | 一份 CSV（聚合摘要，utf-8-sig） |
| 程序后处理 / 复跑 / 二次分析 | JSONL（每行全量结果，含 raw_response、payload 脱敏后、耗时、error） |
| 找厂商排障 | trace/requestId 精简 CSV |
| 评测 / badcase 复盘 | badcase JSONL + 标签分布统计文本 |
| 压测 | metrics 汇总（json 或 markdown 表）|

文件名带时间戳避免覆盖。Level 0 通常**只写一份 JSONL 或一份 CSV** 就够。

---

## 4. 成本与流量控制（优先于稳定性）

写代码前先想：**怎么少打、不重复打、错了快停**。

推荐手段（按风险逐级启用）：
- **dry-run**：只生成并打印 payload，不发请求；接口计费时默认提供。
- **sample mode**：`--sample N` 或 `--head N`，先小流量预跑确认参数与解析逻辑。
- **输入去重**：相同内容只调一次，结果按 hash 复用（也是天然幂等）。
- **非法输入提前过滤**：空内容、超长、格式错的样本在调用前剔除并记录。
- **预算守卫**：启动时打印"预计调用次数 × 单价 ≈ 成本"，可要求 `--confirm`。
- **快速失败**：连续 N 次同类业务错（如 401/403/配额耗尽）→ 立即停批，不要把额度耗光。

---

## 5. 评测范式（任务用途偏"评测/对比/验证"时启用）

普通批跑只关心"跑完了"，评测还要关心"结果有多大用"。推荐补充：

- **统一归一化 schema**：不同 provider 的输出落到同一字段（label / score / risk_level / raw），下游对比才可行。
- **Badcase 导出**：单独文件保存命中、误判、与人工标注不一致的样本，便于人看。
- **Provider diff**：多 provider 时输出宽表（每行一个样本，每 provider 一列结论），并标注 disagreement 行。
- **Error bucket**：把 fail 按错误类型分桶（网络 / 4xx / 5xx / 解析失败 / 业务错误），分别给数量与样例。
- **标签分布**：输出每个 label 的命中数 / 占比；如有 ground truth，附 precision/recall/F1。
- **Sample review 集**：对正常通过样本随机抽 K 条，单独导出供人工抽检。

如果是纯打标/调用、用户没说"评测"，这部分**不要默认启用**。

---

## 6. AI / LLM 接口的特殊处理

调用 LLM / 多模态生成类 API 时，在通用范式之上额外注意：

- **Token 计量**：记录每条的 `prompt_tokens / completion_tokens / total_tokens` 与累计成本。
- **Context overflow**：调用前估算 token 数，超限时按策略处理。**关键区分**：
  - 普通打标 / 生产调用 → 可按既定策略截断头/尾、滑窗、切片聚合。
  - **评测 / 对比场景下严禁隐式截断 prompt**：擅自改输入会破坏评测变量、让 provider 之间不可比。超限的样本应直接归入 error bucket，标记 `CONTEXT_EXCEEDED` 并记录原 token 数，由人决定怎么处理。
- **长文本切片聚合**：超长输入按段处理，再用稳定规则聚合（取最严 / 投票 / 拼接）。
- **Streaming**：批跑场景默认非 streaming（更易超时控制）；只有要看首 token 延迟或省内存时才用，需处理中途断流。
- **Prompt 版本化**：`PROMPT_VERSION` 写进每条结果，prompt 改了 → 输出文件名带版本号，避免新旧结果混。
- **Model fallback**：主模型 5xx/超时 → 可降级到备选模型，记录 `actual_model` 字段。
- **采样不确定性**：评测时把 `temperature / top_p / seed` 写进结果；需要可复现时强制 `temperature=0` 或固定 seed。
- **结构化输出健壮解析**：JSON 模式下对截断/多余文本宽容（提取首个合法 JSON 块），解析失败计入 error bucket 而非整批崩。

---

## 7. 非目标 / 不适合套用本 skill 的场景

明确划线，避免泛化：

- **单次或十几条以内的临时调用** → 直接写最简代码，不要套这套范式。
- **在线实时服务、低延迟接口** → 关注点完全不同（QPS、热路径、连接池、SLA），不在本 skill 范围。
- **WebSocket / 长连接 / 推送** → 工程模式不同。
- **强事务 / 需要 exactly-once 写库** → 本 skill 假设的是"调外部接口 + 落文件"。
- **流式 UI 应用** → 关注前端体验而非批处理。
- **企业级数据管道** → 应使用 Airflow / Dagster / Spark，而非本类脚本。

---

## 8. 反模式（无论哪个 Level 都别犯）

- 同步串行硬跑几千条
- 异常直接 `raise` 拖垮整批
- 不限并发的 `gather`
- 无超时
- 对所有错误无脑重试（含 4xx）
- 中途崩了全丢的"跑完才写"
- API key / URL / 阈值硬编码
- 跑完没有任何统计输出
- 计费接口直接全量打、没有 dry-run / sample
- **异步流里混用同步阻塞调用**：一旦进入 `asyncio` 路线，出网必须用 `httpx.AsyncClient` / `aiohttp`，延时必须用 `await asyncio.sleep()`。在 `async` 函数里调 `requests.post()` / `time.sleep()` / 同步文件大读写，会让事件循环整体阻塞，并发立即退化为单线程串行——这是最常见且最难发现的"性能假象"。需要同步代码就走 Level 0 同步路线，不要混。

---

## 9. Logging 规范（脚本型，不要往服务化方向写）

这是批处理脚本，不是常驻服务。Logging 默认这样：

- 用 Python 标准 `logging` 模块，不要引第三方框架。
- **同时输出到控制台 + 文件**，文件路径默认 `logs/run_YYYYMMDD_HHMMSS.log`。
- 每次运行生成独立日志文件，**禁止覆盖、禁止 rotation**（rotation 会让一次性脚本的现场更难追）。
- 日志格式简洁可 grep，推荐：
  ```
  %(asctime)s | %(levelname)s | task=%(task_id)s | %(provider)s | %(message)s
  ```
  没有 task 上下文的日志（启动/统计）省略 task 字段即可。
- INFO 给进度与状态，WARNING 给重试与降级，ERROR 给最终失败；DEBUG 默认关闭，由 env / `--debug` 打开。
- 不要把超长 JSON / base64 直接打到日志；超过阈值（如 500 字符）截断带 `<len=N>` 标记。
- **不要**默认引入：`TimedRotatingFileHandler`、ELK、structlog/loguru、JSON logging、远程 sink。

最小骨架（参考即可，不强制）：

```python
import logging, os, time
os.makedirs("logs", exist_ok=True)
log_path = f"logs/run_{time.strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.FileHandler(log_path, encoding="utf-8"),
              logging.StreamHandler()],
)
```

---

## 10. 输出文件默认带时间戳（不只是日志）

所有产物默认 `*_YYYYMMDD_HHMMSS.*`，**禁止覆盖写**：

```
logs/run_20260521_153000.log
output/result_20260521_153000.jsonl
output/summary_20260521_153000.csv
output/badcase_20260521_153000.jsonl
output/metrics_20260521_153000.json
output/trace_20260521_153000.csv
```

理由：批跑/评测经常多次复跑对比；覆盖写会让历史结果丢失、问题无法回溯。
续跑场景用"读取最近一份 JSONL 的 task_id 做 skip"实现，而**不是**覆盖同名文件。

---

## 11. JSONL 默认保留原始接口返回

JSONL 是排障的最后一道防线，**默认必须**保留：

- 原始 response body（厂商返回的完整 JSON）
- HTTP `status_code`
- `request_id / trace_id / btId` 等厂商流水号
- 请求耗时、重试次数、最终错误（若有）
- 请求 payload（脱敏后：去掉大字段如 base64 图片、长 prompt 文本、token）

CSV 可以精简聚合，但 JSONL 不能。批量接口脚本最常见的事故就是"出问题才发现没存原始返回"。

裁剪开关（按需启用，不默认开）：
- `--no-raw`：不写 raw response（响应巨大或敏感场景）。
- `--keep-raw-fields a,b,c`：只保留指定字段。
- payload 脱敏函数 `sanitize_payload()`：剔除 `text/img/audio/prompt/messages` 等大字段，保留参数骨架。

---

## 12. 默认生成 `.gitignore`（小而实用）

新建项目骨架时默认写一份，至少包含：

```gitignore
# 运行产物
logs/
output/
tmp/
cache/
checkpoints/

# Python
__pycache__/
*.pyc
*.pyo
.venv/
venv/

# 配置
.env
.env.local

# 大文件 / 媒体样本
*.mp4
*.mov
*.avi
*.mkv
*.wav
*.mp3
*.flac
*.zip
*.tar.gz
*.7z

# 编辑器
.idea/
.vscode/
.DS_Store
```

不要扩展成企业级 monorepo 模板。原则是"挡住 AI 脚本最常见的污染"，到此为止。

**不要自作主张做这些事**：
- 不要 `git init`
- 不要 `git add .` / `git commit`
- 不要建立远程仓库
- 不要在不必要时创建 `README.md`、`LICENSE`、`pyproject.toml`

只生成"用户跑批所必需的最少文件"。git 操作交给用户。

---

## 13. 可修改性优先（人类视角）

批处理脚本的生命周期通常很短，**容易被人接手改**比"架构优雅"重要得多。

推荐：
- **线性主流程**：`load → preview → loop → write` 一眼看完，不要让人来回跳。
- 配置常量直接放文件顶部，用户改值不用读完整个项目。
- 函数粒度别太细：3 行的 helper 不如就地写。能就地写明白就别抽。
- 业务关键逻辑（payload 构造 / 结果解析）放在主流程附近，便于 grep。
- 命名贴近业务词汇，不要为了"通用"起 `BaseHandler`、`AbstractRunner`。

避免：
- helper / wrapper / decorator 满天飞
- 200 行脚本拆成 15 个文件、20 个函数
- 抽象基类 + 注册表 + 配置驱动 + 工厂方法的"四件套"

判定：**删掉这层封装后代码更短更清楚？删。**

---

## 14. 调试优先（debugability first）

真实跑批中，"出问题能多快定位"比"代码看起来高级"重要。默认让脚本好调：

- **支持 rerun 单条**：`--task-id xxx` / `--filter content=...` 只跑一条样本，便于复现。
- **`--debug` 模式**：打开后保留全量 raw、打印完整 request/response、关闭并发（变成串行 1 个 task）。
- **`--dump <task_id>`**：把指定任务的 request payload + response 落到独立 JSON 文件，方便贴给厂商或人工检查。
- **错误日志包含完整上下文**：task_id、provider、URL、http status、response 摘要、重试次数，一行能看全。
- **失败结果保留 payload**：fail 的 task 在 JSONL 里也带上其请求 payload（脱敏后），不要只留 error 字符串。
- **种子 / 时间戳 / 版本写进结果**：评测时同一份输入应能精确复跑。

原则：**让"再跑一次定位问题"成本接近零**。

---

## 15. Raw response 大响应保护

JSONL 默认保留 raw 是对的，但对超大响应要有保护，避免 JSONL 单行几 MB、文件几十 GB：

- 设阈值（默认 100KB / 行可调）。
- 超阈值时 JSONL 中保留：
  - 摘要（前 N 字符 + 关键字段如 `code/message/requestId`）
  - 内容 `sha256`
  - 完整 raw 单独写到 `output/raw/<task_id>_<sha>.json`
  - 一个 `raw_path` 字段指向外部文件
- 典型触发场景：embedding 数组、长 LLM 输出、视频 metadata、base64 回显、超大 frameDetail。
- 二进制 / base64 字段直接 hash + 长度，不入 JSONL。

这样 JSONL 仍可用 `jq` 流式读，需要细看时再按 `raw_path` 取。

---

## 16. 本 skill 是参考，不是模板（最重要）

强 skill 有副作用：所有脚本越长越像、AI 思维僵化、对特殊任务的适配能力下降。请记住：

- **优先适应当前任务**，而不是套全本 skill 的章节结构。
- 任务的特殊性 > 本 skill 的"推荐"。如果某条建议在当前场景下无意义，直接跳过，不要为了完整性硬塞。
- 不必每次都生成完全一样的目录布局、命名风格、函数划分。
- 对话中已经明确不需要的机制（如用户说"不要日志文件"），就别加，也别提示"建议加上"。
- skill 的目标是让 AI **更稳健**，不是让 AI **更整齐划一**。

如果你发现自己在生成"和上次一样的脚手架" → 停下来，重新看任务本身。

---

## 17. AI 生成代码前的自检（精简版）

在动笔前回答三个问题：

1. **这是 Level 几？** Level 0 时同步代码也行，不要无脑 async。
2. **真的需要 Provider 抽象吗？** 单 provider → 不要。
3. **输出哪几份就够了？** 不要默认三件套；不要默认初始化 git。

代码写完前再核对（按当前 Level 取相关项即可，不必全勾）：
- [ ] 决策符合"核心优先级"前三条（不丢数据 / 不打挂对端 / 不浪费成本）
- [ ] 主流程线性、≤一屏可读完
- [ ] 没有为"显得专业"加抽象层 / 多余 helper
- [ ] 计费/高风险接口有 dry-run 或 sample 入口
- [ ] 错误分类清晰，4xx 不重试
- [ ] 失败任务结构化返回，不抛断主循环
- [ ] 支持 `--task-id` / `--debug` 单条复现（Level 1+）
- [ ] Level 1+ 有 checkpoint 续跑（边写边落）
- [ ] 进度日志可 grep
- [ ] 评测场景才补 badcase / diff / 分布统计
- [ ] LLM 场景才补 token / 切片 / prompt 版本
- [ ] 日志同时落控制台 + `logs/run_<ts>.log`，不覆盖（Level 1+）
- [ ] 所有产物文件名带时间戳，没有覆盖写
- [ ] JSONL 保留 raw response / status / requestId，超大响应外置
- [ ] 项目根有 `.gitignore`，但**没有**自动 `git init`/`git add`
- [ ] 没有照搬上一版脚本的目录结构，是为当前任务量身写的

冗余项 → 删掉，而不是补全。**少即是多，活即是真**。
