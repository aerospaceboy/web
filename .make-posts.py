"""Create one starter post per category via Halo API."""
import json, subprocess, sys, os, re, time, html as htmlmod

BASE = "https://aerospaceboy.site"
TOK = os.environ["HALO_PAT"]

def req(method, path, data=None):
    for attempt in range(4):
        cmd = ["curl", "-s", "-m", "40", "-X", method, "-H", f"Authorization: Bearer {TOK}"]
        if data is not None:
            cmd += ["-H", "Content-Type: application/json", "--data-binary", data]
        cmd += ["-w", "\n%{http_code}", BASE + path]
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        body, _, code = p.stdout.rpartition("\n")
        code = code.strip()
        if code in ("200", "201", "204"):
            return code, body
        if code == "000" or code.startswith("5"):
            time.sleep(3)
            continue
        return code, body
    return code, body

# ---------- minimal markdown -> html ----------
def inline(s):
    s = re.sub(r"`([^`]+)`", lambda m: "<code>" + htmlmod.escape(m.group(1)) + "</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    return s

def md2html(md):
    lines = md.split("\n")
    out = []
    i = 0
    para = []

    def flush():
        nonlocal para
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para = []

    while i < len(lines):
        ln = lines[i]
        if ln.startswith("```"):
            flush()
            lang = ln[3:].strip()
            i += 1
            buf = []
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(lines[i]); i += 1
            i += 1
            out.append('<pre><code class="language-%s">%s</code></pre>' % (lang, htmlmod.escape("\n".join(buf))))
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", ln)
        if m:
            flush()
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
            i += 1
            continue
        if re.match(r"^\s*[-*]\s+", ln):
            flush()
            items = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                items.append(re.sub(r"^\s*[-*]\s+", "", lines[i]))
                i += 1
            out.append("<ul>" + "".join("<li>%s</li>" % inline(x) for x in items) + "</ul>")
            continue
        if re.match(r"^\s*\d+\.\s+", ln):
            flush()
            items = []
            while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
                items.append(re.sub(r"^\s*\d+\.\s+", "", lines[i]))
                i += 1
            out.append("<ol>" + "".join("<li>%s</li>" % inline(x) for x in items) + "</ol>")
            continue
        if ln.startswith(">"):
            flush()
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(lines[i].lstrip("> ").strip()); i += 1
            out.append("<blockquote>" + "".join("<p>%s</p>" % inline(x) for x in buf if x) + "</blockquote>")
            continue
        if ln.strip() == "":
            flush()
            i += 1
            continue
        para.append(ln.strip())
        i += 1
    flush()
    return "\n".join(out)

# ---------- categories ----------
CAT = {
    "embedded":   "category-zlj7y2cg",
    "ai":         "category-b1j3ylp1",
    "robotics":   "category-3qhiwy0m",
    "automation": "category-3wsnikoe",
    "project-log":"category-juf9hr3i",
    "study-notes":"category-cp1j2nsd",
    "contest-log":"category-4int68u1",
}
TAG = {
    "stm32": "tag-gymzce33", "51": "tag-iyki5jdb", "esp32": "tag-fsns39re",
    "linux": "tag-4b91oayt", "orange-pi": "tag-qrn4nasu", "rk3588": "tag-hgnskdtz",
    "ros2": "tag-btydzbj6", "yolo": "tag-x8ld6baw", "fpga": "tag-nprcotyq",
    "python": "tag-aga0pold", "c-cpp": "tag-jcypifb2", "docker": "tag-uyvkrptl",
    "ai": "tag-covlogfy", "computer-vision": "tag-dixccbqi",
}

POSTS = [
    dict(
        cat="embedded", slug="stm32-dev-env",
        title="STM32 开发环境搭建与最小工程思路",
        tags=["stm32", "c-cpp"],
        md="""# STM32 开发环境搭建与最小工程思路

这是嵌入式分类的第一篇记录，先把开发环境与最小工程跑通，后面每个外设的调试过程才有稳定的基础。

## 工具链怎么选

- **STM32CubeIDE**：一站式（编辑器 + CubeMX + 调试器），新手起步最快
- **CLion / VS Code + CMake**：工程结构清晰，适合长期维护
- **Keil MDK**：老项目常见，库生态稳定

选一个用到底，比来回切换工具链省很多时间。

## 最小工程的结构

1. 用 CubeMX 配置时钟树、调试接口（SWD）和需要用到的外设引脚
2. 生成工程后先只保留 `main()` 里的初始化与空循环
3. 编译、烧录、确认程序真的跑起来了（比如翻转一个 LED 或用串口打印一行文字）

## 调试手段

- **SWD + 调试器**：打断点、看寄存器，比串口打印更适合定位时序问题
- **串口打印**：验证流程走向最快的手段
- **逻辑分析仪**：协议调试（I2C / SPI / UART）时几乎是必需品

## 这个分类后续会记录什么

- 外设驱动开发（GPIO / UART / I2C / SPI / ADC / 定时器）
- 中断与 DMA 的使用方式
- 常见通信协议的调试记录
- 工程实践中的踩坑与解决方案

> 先把环境跑通，再谈性能与架构。""",
    ),
    dict(
        cat="ai", slug="yolo-training-to-edge",
        title="YOLO 模型从训练到边缘部署的流程梳理",
        tags=["yolo", "python", "computer-vision"],
        md="""# YOLO 模型从训练到边缘部署的流程梳理

这是一份通用的流程梳理，用来在动手之前想清楚每一步的输入输出和验证方式，避免"训练完直接用"。

## 流程总览

1. **数据集准备**：明确标注规范（框的边界、类别定义），按场景划分训练集与验证集
2. **模型训练**：选定框架与预训练权重，跟踪损失与 mAP 曲线，先确认过拟合/欠拟合的方向
3. **导出中间格式**：通常先导出 ONNX，作为跨平台部署的公共中间层
4. **边缘转换**：按目标硬件选择 RKNN / TensorRT / NCNN 等，注意算子支持与量化策略
5. **推理封装**：预处理、推理、后处理（NMS）三步要成对校准，保证 PC 端与设备端结果一致

## 每一步都需要一个验证手段

- 数据：抽样可视化，确认标注框与坐标顺序（xywh / xyxy）正确
- 训练：验证集指标 + 少量图片的实际推理可视化
- 导出：ONNX 用 onnxruntime 跑一遍，与训练框架输出对比
- 转换：设备端跑固定测试图，与 PC 端结果逐框对比
- 封装：把整条链路的效果录屏存档，便于回归对比

## 容易踩的坑

- 预处理不一致：归一化方式、通道顺序（RGB / BGR）、letterbox 参数
- 量化后精度下降：先定位是哪个阶段掉点，再决定是否混精度
- 后处理阈值不同：置信度阈值与 NMS 阈值要按实际场景调，而不是照抄默认值

> 部署能不能成功，往往取决于每一步"有没有对齐验证"，而不是模型本身多新。""",
    ),
    dict(
        cat="robotics", slug="ros2-basics",
        title="ROS2 入门笔记：节点、话题、服务与动作",
        tags=["ros2", "linux", "python"],
        md="""# ROS2 入门笔记：节点、话题、服务与动作

机器人分类的第一篇，先把 ROS2 的通信骨架理清楚，后面再谈感知、控制与导航。

## 四种通信方式

- **Topic（话题）**：发布订阅，适合作高频数据流（传感器、里程计）
- **Service（服务）**：请求响应，适合短小的确定性调用
- **Action（动作）**：长任务 + 进度反馈 + 可取消，适合导航这类耗时操作
- **Parameter（参数）**：节点运行时可调配置

## 几个基础概念

- **Node（节点）**：最小功能单元，职责尽量单一
- **DDS 与 QoS**：ROS2 的底层通信中间件；可靠性、历史深度、丢弃策略都会影响实际行为
- **工作空间与 colcon**：`colcon build` 构建，`source install/setup.bash` 后使用
- **launch 文件**：把多节点、参数、命名空间组织成一次启动
- **tf2**：坐标系之间的变换树，机器人开发里绕不开
- **rosbag2**：录制与回放数据，调试和复现问题的利器

## 最小验证方式

```bash
ros2 run demo_nodes_cpp talker
ros2 run demo_nodes_py listener
ros2 topic list
ros2 topic echo /chatter
```

能跑通一组 talker / listener，再去看具体的传感器驱动与算法包。

## 后续记录方向

- 传感器接入（相机、激光雷达、IMU）
- 坐标变换与建图定位
- 导航栈配置与调参
- 多节点架构与工程化""",
    ),
    dict(
        cat="automation", slug="pid-control-intro",
        title="PID 控制入门笔记：从公式到代码",
        tags=["python"],
        md="""# PID 控制入门笔记：从公式到代码

自动化分类开篇。PID 是最基础也最常被低估的控制器，理解每一项的作用比背公式更重要。

## 三项分别做什么

- **P（比例）**：按当前误差出力，越大响应越快，但过大容易振荡
- **I（积分）**：累积历史误差，消除稳态误差，过大容易超调
- **D（微分）**：按误差变化率抑制突变，能改善稳定度，但对噪声敏感

## 离散实现

```python
# 位置式 PID 伪代码：注意采样周期 dt 必须固定
integral = 0.0
prev_error = 0.0

def pid(setpoint, measured, dt, kp, ki, kd):
    global integral, prev_error
    error = setpoint - measured
    integral += error * dt
    derivative = (error - prev_error) / dt
    prev_error = error
    return kp * error + ki * integral + kd * derivative
```

## 调参顺序

1. 先把 I 和 D 置零，只调 P 到"响应够快但不持续振荡"
2. 加 I 消除稳态误差，注意积分饱和
3. 最后微调 D 抑制超调，同时注意引入的噪声

## 工程上的关键细节

- **采样周期**要稳定，抖动会让微分项失真
- 加**抗积分饱和**（积分限幅或条件积分）
- 输出要**限幅**，并和保护逻辑配合
- 记录阶跃响应曲线：超调量、上升时间、稳态误差，调参才有依据

> 调参不是玄学，是记录与对比。""",
    ),
    dict(
        cat="project-log", slug="project-log-template",
        title="项目记录模板：从立项到复盘",
        tags=[],
        md="""# 项目记录模板：从立项到复盘

这个分类用来沉淀项目的原始记录。先用一个固定模板把结构定下来，后面每个项目都按它写。

## 记录模板

**背景与目标**：为什么要做、做完算成功的标准是什么

**需求拆解**：把大目标拆成可验证的小任务清单

**硬件与软件清单**：器材型号、软件版本、工具链，避免"环境不一致"复现困难

**关键决策与踩坑**：为什么选这个方案、试过哪些死路，这往往是以后最有价值的部分

**进度日志**：按时间记录做了什么、卡在哪、怎么解决的

**复盘**：
- 做对了什么（值得保留的）
- 哪里浪费时间（下次避免的）
- 如果重来会怎么安排

## 为什么值得认真写

- 项目做完后记忆会迅速衰减，记录是唯一的补偿手段
- 复盘时能看出自己重复踩的坑，这些坑会变成经验
- 长期积累后，能清晰地看到自己的能力边界在往外扩

> 项目记录不是交作业，是给未来的自己留线索。""",
    ),
    dict(
        cat="study-notes", slug="study-roadmap",
        title="从嵌入式到 AI：一条可执行的学习路线索引",
        tags=["c-cpp", "python"],
        md="""# 从嵌入式到 AI：一条可执行的学习路线索引

学习笔记分类开篇。这里不给"刷完多少课程"的目标，而是给每个阶段一个**可验收的能力**。

## 阶段划分

1. **C / C++ 与计算机基础**：指针、内存、结构体、编译链接；能独立写小工具
2. **单片机与外设**：GPIO / UART / I2C / SPI / 定时器；能让板子按预期工作
3. **嵌入式 Linux**：shell、文件系统、交叉编译；能在目标板上跑通程序
4. **Python 与数据处理**：脚本化、数据清洗、可视化；能写数据处理流水线
5. **深度学习基础**：张量、损失、反向传播；能训练并评估一个小模型
6. **视觉任务与部署**：检测/分类流程，模型转换与推理封装
7. **机器人与工程化**：ROS2、通信架构、并行与模块化

## 每个阶段的验收方式

- 不是"看完了"，而是"能独立复现 + 能解释为什么"
- 每阶段留一份可运行的最小工程
- 把卡住的问题写进学习笔记，而不是只记结论

## 怎么用这份索引

按当前在折腾的方向挑阶段深入，不必线性走完；但每往前一步，都尽量回头把上一阶段的不懂补上。

> 路线的价值不是限制顺序，而是让"我现在在哪个位置"变得清楚。""",
    ),
    dict(
        cat="contest-log", slug="contest-prep-template",
        title="竞赛备赛流程模板",
        tags=[],
        md="""# 竞赛备赛流程模板

比赛记录分类开篇。这里只放通用的备赛流程与交付物清单，不涉及具体赛事与结果。

## 流程

1. **规则研读**：拆解评分表，明确哪些指标占比最高
2. **时间倒排**：从比赛日往前排里程碑，给联调留出足够余量
3. **角色分工**：硬件、软件、报告、答辩各自的责任人
4. **技术预研与选型**：先做最小可行性验证，再接整机
5. **场地与器材准备**：电源、线材、备件、工具，提前列出清单
6. **交付物清单**：代码仓库、设计文档、演示材料、答辩稿

## 复盘模板

- 哪些环节按计划完成，哪些严重超时
- 现场出了什么意外，预案是否有效
- 技术选型在真实条件下是否够用
- 下次备赛应该在哪个阶段加时间

## 备赛期的三条经验

- 联调时间永远比预期多一倍，倒排时就要包含
- 每完成一个模块就做一次端到端验证，别等到最后
- 文档与代码同步写，赛后几乎没时间补

> 比赛的价值在于过程可复盘，而不是一次性成绩。""",
    ),
]

created = []
for meta in POSTS:
    body = {
        "apiVersion": "content.halo.run/v1alpha1",
        "kind": "Post",
        "metadata": {"generateName": "post-"},
        "spec": {
            "title": meta["title"],
            "slug": meta["slug"],
            "owner": "aerospaceboy",
            "publish": False,
            "pinned": False,
            "allowComment": True,
            "visible": "PUBLIC",
            "priority": 0,
            "deleted": False,
            "excerpt": {"autoGenerate": True, "raw": ""},
            "cover": "",
            "categories": [CAT[meta["cat"]]],
            "tags": [TAG[t] for t in meta["tags"]],
        },
    }
    c, b = req("POST", "/apis/content.halo.run/v1alpha1/posts", json.dumps(body, ensure_ascii=False))
    if c not in ("200", "201"):
        print("CREATE_FAIL", meta["slug"], c, b[:200])
        continue
    name = json.loads(b)["metadata"]["name"]
    html = md2html(meta["md"])
    c1, _ = req("PUT", f"/apis/api.console.halo.run/v1alpha1/posts/{name}/content",
                json.dumps({"raw": meta["md"], "content": html, "rawType": "MARKDOWN"}, ensure_ascii=False))
    c2, _ = req("PUT", f"/apis/api.console.halo.run/v1alpha1/posts/{name}/publish", "")
    print("POST", meta["slug"], "->", name, "| content:", c1, "| publish:", c2)
    created.append((meta["slug"], name))

print("\ncreated:", len(created), "of", len(POSTS))
