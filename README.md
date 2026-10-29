# 半截的诗 · AerospaceBoy

个人技术博客 [aerospaceboy.site](https://aerospaceboy.site/) 的主题定制、内容快照与页面检查资料。

记录方向包括嵌入式、人工智能、ROS2 与机器人、FPGA、自动化和项目实践。

## 仓库范围

本仓库保存建站和定制过程中产生的资料。Halo 核心源码、完整主题模板、数据库、附件库及服务器部署配置未包含在此仓库中，因此克隆后不能直接启动或完整恢复网站。

| 路径 | 内容 |
| --- | --- |
| `customization/` | 定制 CSS、主题审计、设置方案、页面文案与素材需求 |
| `phase4-audit/` | Hao 主题元信息、设置表单与注解设置定义 |
| `phase5-backup-20261024-215453/` | 分类、标签、菜单、系统基本设置和主题配置快照 |
| `phase6-backup/` | 文章、独立页面、菜单和主题配置的后续快照 |
| `phase7-before/` | 历史调整前截图及过程截图 |
| `phase7-after/` | 历史调整后截图 |
| `.make-posts.py` | 使用 Halo API 创建并发布七篇分类起始文章的脚本 |
| `.cdp.py` | Edge CDP 页面横向溢出测量工具 |
| `.cdp2.py` | Edge CDP 页面 JavaScript 检查工具 |
| `.cdp-shot.py` | 指定视口的 Edge CDP 截图工具 |
| `.shot*.sh` | Windows Git Bash 环境下的历史截图辅助脚本 |

浏览器配置目录、Cookie、缓存、环境变量文件及下载的临时 CSS 不纳入版本管理。

## 已核对的站点信息

2026-10-29 通过公网只读请求检查：

- 页面标识为 Halo **2.27.1**，主题资源版本为 Hao **1.7.3**。
- 首页、归档、项目、关于、RSS 和 Sitemap 的 GET 请求正常。
- 管理入口跳转登录页，健康检查返回 `UP`。
- RSS 包含七篇文章，与首页文章数量一致。

上述结果仅代表检查时刻的公网状态。历史部署文档记录了 Nginx、Docker 与 PostgreSQL，本次未登录服务器复核部署配置。

## 使用定制资料

主题方案从 `customization/hao-audit.md` 和 `customization/hao-settings-plan.md` 开始阅读。页面内容可参考 `about.md`、`projects.md`，图片规格见 `assets-needed.md`。

这些文件包含不同阶段的计划与历史状态。实际线上内容可能已更新，不应直接用旧快照覆盖线上配置。`settings.yaml` 是主题设置表单定义，其中的默认值不能代表实际生效配置。

`aerospaceboy-custom.css` 记录了通过首页 Banner HTML 注入样式的历史做法。公网检查发现对应样式块只出现在首页，项目页、关于页与抽查文章页未包含该块；后续应将需要全站生效的规则迁入统一加载入口。

## 检查脚本

CDP 工具需要 Windows、Microsoft Edge、Python 3 和提供 `websocket` 模块的 `websocket-client` 包。使用项目虚拟环境安装依赖：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install websocket-client
.\.venv\Scripts\python.exe .\.cdp.py https://aerospaceboy.site/ 390 844
.\.venv\Scripts\python.exe .\.cdp-shot.py https://aerospaceboy.site/ 390 844 home-390.png
```

脚本中的 Edge 路径、9333–9335 调试端口和启动方式来自原开发环境，运行前需要核对。截图脚本会启动独立的无头浏览器并在本地写入图片和配置目录。`.shot*.sh` 还包含原机器的绝对路径，不是通用启动器。

## 文章发布脚本的边界

`.make-posts.py` 从环境变量 `HALO_PAT` 读取凭据，并向线上站点发送创建、保存正文和发布请求。仓库不保存 PAT。

该脚本保留原始实现，尚缺少以下能力：

- 正文保存成功后才允许发布的严格判断。
- 按 slug 检查已有文章与重复执行保护。
- 对创建请求重试后的结果确认。
- 发布后回读验证和完整成功统计。
- 域名、作者、分类与标签 ID 的可移植配置。

不要把它作为只读检查脚本执行；修复这些问题并核对目标站点后，再用于实际发布。

## 验证与后续工作

入库前完成四个 Python 文件的语法解析、23 个 JSON 文件的可解析检查，以及待上传文本的常见凭据模式扫描。未执行文章发布脚本，未修改线上数据。历史截图不代表当前移动端交互或完整视觉验收。

建议后续完善全站样式加载、关于页 SEO 摘要、发布脚本可靠性、当前截图与服务器恢复文档，并持续补充带代码和实测结果的项目案例。

主题元信息及相关资源保留其原作者信息。原主题的许可证与使用条件以其上游项目为准。
