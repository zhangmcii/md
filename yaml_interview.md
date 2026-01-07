## YAML 的基本语法:
理解这些就够了：
(要能 看懂 + 手写：)
- 缩进表示层级（空格，不是 tab）
- key: value
- 列表用 -

YAML 最终会被解析成 Python dict / list

## 在 Python 里读取 YAML
```
import yaml

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

db_host = config["database"]["host"]

```

面试问： 
1.你在项目中是怎么用 YAML 的？
我们用 YAML 管理工具配置，启动时读取成 dict，代码根据配置决定执行逻辑。

2.为什么用 safe_load？
safe_load 不会执行任意对象反序列化，更安全，适合读配置文件。 [一句就够，别展开。]

## YAML 的典型使用场景(能随口举 2–3 个场景：)
`这比语法重要得多`
- 工具参数配置（路径、开关、阈值）
- 多环境配置（dev / test / prod）
- 控制工具行为（是否启用某功能）
- 任务编排或执行顺序描述