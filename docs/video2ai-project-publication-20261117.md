# Video2AI 项目发布（2026-11-17）

已将用户指定的 `F:\video转换` 整理为 [Video2AI 项目文章](https://aerospaceboy.site/archives/video2ai-evidence-toolkit)，加入 [项目页](https://aerospaceboy.site/projects) 和首页精选项目。保留原有 AFDX、智巡未来及五个技术方向。

## 公开范围与来源

本轮公开项目介绍、原创流程示意图、人工构造数据的报告布局展示图，以及既有公开 GitHub 仓库链接。没有上传项目目录、安装包、个人视频、既有识别资料包、`.env` 或密钥文件。

已读取 README、使用说明、流水线、桌面入口、报告渲染器和相关测试。当前本地版本显示 0.11.0；项目 Git HEAD 为 `52c7253`。远端 `https://github.com/aerospaceboy/-AI-.git` 的 `ls-remote HEAD` 同为 `52c72533e336aad4c9a653ce9286f6cdcb89a09f`，确认已有公开源码。web 抓取的一个旧页面仍显示空仓库，未把该陈旧结果当作当前状态。

本地 `src/__init__.py`、`src/desktop.py`、`src/scenes.py`、`tests/test_desktop.py` 在操作前已有未提交改动，保持不变。本轮不替项目提交或推送这些改动，也不把本地未提交界面状态称为已发布源码。

正文说明字幕、关键帧、可选 OCR/VLM、时间轴、缓存恢复、批处理和交接文件，并区分本地处理与可选云端文本/关键帧发送。没有将 AI 输出或报告演示数字称作识别准确率。

## 展示图

- `customization/assets/projects/video2ai/ab-video2ai-overview-v1.webp`：1600×900、61,322 字节；由 `tools/render_video2ai_overview.py` 根据源码整理，明确标注流程示意、非运行截图。可编辑 SVG 保存在同目录，不上传 SVG 或放宽附件类型。
- `ab-video2ai-report-demo-v1.jpg`：1684×1006、99,623 字节；使用项目实际 `src.report.render_report` 和人工构造的两段文字渲染，在本地浏览器截取。顶部及正文标注“人工构造数据，非视频识别实测”；搜索 Agent 时为 1/2 章节，清空后为 2/2。
- 桌面程序曾打开并出现 0.11.0 窗口，但 Windows 捕获两次超时，未取得可验收的 GUI 截图，未把它列为完整 GUI 功能验证。未处理真实视频或调用云端模型。

图片 URL、MIME、大小、尺寸、SHA256 记录于 `config/video2ai-project-deployment.json`，同时加入现有资源审计清单 `config/visual-assets.json`。

## 图片部署方式

浏览器 `fileChooser.setFiles` 因扩展未允许访问 file URL 被拒绝，已按工具要求告知用户设置入口，没有修改扩展权限或浏览器安全设置。

使用已授权的既有 SSH 主机 `aerospaceboy` 传输这两张已检查的公开图片。先确认 `/opt/halo/halo2/attachments/upload/` 中两个目标不存在，再上传至独立暂存目录，通过既有 sudo 将文件按 0644 安装到该目录。没有覆盖旧文件、修改 Nginx、重启应用或修改父目录权限。

这些是直接部署到 Halo 既有静态资源目录的文件，**未通过附件库上传流程创建附件管理记录**；后续维护应依照本清单管理，不能误称已在附件库登记。两个 `/upload/ab-video2ai-*` 地址均已通过不带凭据的 HTTPS 下载与哈希校验。正常域名 SNI、证书校验保持；CLI 使用此前已核实的服务器地址与 WLAN 绑定绕开本机代理解析故障，未改变系统 DNS 或代理配置。

## CMS 保存与发布

- 使用已安装 ByteMD，资源名 `01a1e9cb-ff6f-76e4-94b8-9e1bfe252cc4`，固定链接 `video2ai-evidence-toolkit`；标题“Video2AI：让本地视频变成可回查的 AI 资料包”。分类“项目记录”“人工智能”，标签 Python、AI，手动摘要和流程图封面。
- 曾误把“发布”当作设置入口，短暂使用默认未命名标题上线；随后已修正同一资源的标题、别名与元信息，没有新建重复文章。最终公开地址、分类、标签和摘要已通过后台重开与公网首页核验。
- 正文保存并重开后，编辑器复制出的 Markdown 与 `content/projects/video2ai-evidence-toolkit.md` 规范化哈希一致。6 个章节、两张图、文件用途表和项目/GitHub 链接保留。
- 项目页改动前备份并与 Git 中上一版逐字规范化核对一致，再保存第三张卡片；重开读取一致后发布。原有内容保留。
- 首页配置追加同一项目目录；修改前实际 CSS/JS 内容哈希与上一轮一致，备份原全局 head，只更新两个自有块，保留其他注入与站点身份数据。保存后重开内容一致。

全局 CSS 哈希未变：`b8a4ae90c82883718eba0254d7049e898548250ddd2499ced3d5175df08c20b0`。

最终组合 JS 哈希：`2c584630b9471ca51fc8d5f8b9a5589e3b92b6ce7f2ace59776742f9ea34996f`。

私有备份在 `backups/video2ai-20261117/`。回退时恢复原项目页正文与全局注入，将本项目文章改为未发布即可；展示图可先保留，避免影响历史访问。无需修改已有两篇比赛文章。

## 验证与限制

- 已确认专用解释器为 `D:\anaconda\anaco\envs\video2ai\python.exe`、prefix 为相同环境；使用该解释器运行现有 pytest，64 项通过，未安装任何依赖，未使用 base/系统 Python 运行项目测试。
- 网站 84 项 Python + 11 项 Node 测试、构建、diff 检查通过。未为此次内容与目录变更增写镜像测试。
- 公网审计 18 个页面/XML 入口、12 个资源通过，issues/warnings 为空。包括两张新图的实际字节与 SHA256；不把 HTTP 200 单独作为正文或资源完整的证据。
- 公网项目页与首页均为三个项目，旧入口保留，GitHub 目标正确。新文章有一个速览、一套文章工具和 6 节目录，两张图已实际加载。
- 1359px 桌面、实际 312px CSS 窄视口下无全页横向溢出；窄屏首页、项目页、文章及浏览器后退/前进已检查，重入文章不重复挂载。新文章正文统计为 1,446 字/词、约 5 分钟；这与 ByteMD 自身计数口径不同。临时视口覆盖最后清除。
- 页面往返时捕获过一次 Halo 原生 `halo-tracker.js` 的 `Failed to fetch`，内容与导航仍正常。没有把该日志当作本次已经修复的统计问题，也不声称浏览器全过程零错误。
- 没有重跑真实视频全流程、OCR/VLM 或 GPU 性能，没有跨浏览器/真机触摸/新一轮原生 200% 缩放的完整验收。

私有审计及上线截图位于 `reports/video2ai-20261117/`；原始后台备份和本地检查资料不提交 Git。
