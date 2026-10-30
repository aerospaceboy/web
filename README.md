# 半截的诗 · AerospaceBoy

个人技术博客 [aerospaceboy.site](https://aerospaceboy.site/) 的主题定制、内容与维护工具。

仓库保存 Halo 博客的定制成果，未包含 Halo 核心源码、完整主题、数据库和完整附件库，克隆后不能直接启动或完整恢复网站。

## 快速开始

需要 Python 3.11 或更新版本。以下命令只创建项目环境，不修改系统 Python 或 PATH：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --cache-dir .cache/pip -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe .make-posts.py --dry-run
.\.venv\Scripts\python.exe -m blog_tools.build
```

Linux 对应使用 `.venv/bin/python`。浏览器检查另外需要 Microsoft Edge，可用 `EDGE_PATH` 指定路径。

## 目录

| 路径 | 内容 |
| --- | --- |
| `blog_tools/` | Halo 请求、文章发布、样式构建、公网审计和 CDP 浏览器工具 |
| `config/site.json` | 站点域名、作者、首页与关于页描述，不保存凭据 |
| `config/covers.json`、`customization/assets/covers/` | 已上线封面 URL、大小与 SHA256，以及可编辑 SVG 和 WebP 导出 |
| `content/posts.json`、`content/posts/` | 七篇分类起始文章的清单与独立 Markdown 正文 |
| `customization/` | 当前 CSS，以及历史定制方案、页面文案与素材需求 |
| `docs/` | 当前维护状态、部署步骤和备份恢复边界 |
| `tests/` | 失败发布、重复运行、断连、HTTP 传输、内容与构建回归检查 |
| `.github/workflows/checks.yml` | Windows/Linux、Python 3.11/3.12 的离线检查 |
| `phase4-audit/` | 原始主题元信息与设置表单定义 |
| `phase5-backup-*`、`phase6-backup/` | 历史配置与内容快照 |
| `phase7-before/`、`phase7-after/` | 历史截图，不代表当前页面状态 |

生成的 `build/`、`reports/`、浏览器临时配置、`.venv/`、私有备份和凭据文件均被 Git 忽略。

## 发布文章

默认调用与 `--dry-run` 均为离线计划，不读取 PAT、不访问站点、不发布内容。可以用 `--config` 和 `--manifest` 指定不同站点与文章清单。

实际发布需要在当前进程环境设置 `HALO_PAT`，再执行：

```powershell
.\.venv\Scripts\python.exe .make-posts.py --apply
```

请在本机私下设置凭据，不要提交到 Git 或粘贴进聊天。

发布工具先解析目标站点全部分类和标签，按 slug 找到资源 ID。所有清单和分类引用检查通过后才开始写入。已有文章会跳过；本工具创建但未完成的草稿可以恢复，其余草稿保持原样。

写请求不自动重试。创建响应丢失时按确定性名称回读；正文回读一致后才发布指定快照，发布后的正文再回读一致才计入成功。任何失败都会出现在 `failed` 中并使进程返回非零退出码。

这不等于数据库事务：正文失败可能留下未发布草稿；发布请求响应丢失或发布后验证失败时，文章可能已上线，需要核对报告。并发编辑和本工具之间不提供跨客户端锁，已有正式文章的更新仍应在 Halo 后台进行。

## 全站样式和 SEO

```powershell
.\.venv\Scripts\python.exe -m blog_tools.build
```

生成 `build/global-head.html` 和首页、关于页描述文件。全局文件包含 CSS、手机导航兼容脚本与轨道首页增强脚本，按 [部署步骤](docs/deployment.md) 合并到 Halo **设置 → 代码注入 → 全局 head 标签**，同时移除首页 Banner 中的旧定制样式块，并修正 SEO 与页面摘要。

GitHub 推送与生成文件不会自动修改线上配置。

```powershell
.\.venv\Scripts\python.exe -m blog_tools.audit --output reports/live-audit.json
```

公网审计会核对全站 CSS 和脚本的实际内容、首页及关于页描述、七篇文章封面、许可链接、RSS 和 Sitemap，并下载八张封面核对大小、MIME 与 SHA256。隐私页占位内容单独列为 warnings，技术检查通过不代表隐私内容已经完善。HTTP 200 但样式或摘要不正确时，仍然报告失败。

## 星空首页视觉

`customization/space-effects.js` 与 CSS 一起构建到全局注入中：首页采用原创深紫星云、简洁大标题和两个主要入口，星点轻微闪烁并低频出现流星。背景只在首页请求一张 202612 字节的站内 WebP，不加载第三方动效库。

Pjax 返回首页时恢复单一实例；不可见时暂停动态星点，系统减弱动效偏好下保留静态画面。手机减少一层星点并加深文字遮罩；浅色模式保留深色星空主视觉，正文和列表继续使用浅色配色。

素材、编辑源与 imagegen 提示词见 [素材说明](customization/assets/nebula/README.md)，背景 URL 和哈希位于 `config/visual-assets.json`。构图参考及平台适配调研见 [星空主题调研](docs/starry-theme-research-20261029.md)；未使用演示站图片或付费源码。

桌面还提供 `pointer-effects.js` 鼠标光晕与短星尘：保留原指针，不拦截点击，最多复用 12 个星尘节点，鼠标静止后没有持续 JS 动画循环。触屏、减弱动效和节省流量模式关闭该效果。

这是渐进增强：脚本不可用时展示 Hao 原始 Banner；背景文件失败时移除失效图片并保留暗色渐变、文字与入口。回退仅需恢复旧全局注入。

## 社交入口与阅读偏好

`customization/site-hub.js` 将 `config/site.json` 中的 `github_profile_url` 加到顶部工具栏、首页、作者卡片和手机菜单；GitHub 使用原生新标签页链接。首页和侧栏还提供已有 RSS 订阅入口。仅允许 HTTPS 的 GitHub 个人主页地址。

首页侧栏包含项目、简历、归档、留言四个快捷入口，以及三档文章字号和“减少装饰动效”开关。手机菜单也可设置；文章页只添加可折叠阅读设置，保留原来的目录位置。字号只应用于文章，简历及其他页面保持原排版。

偏好保存在当前浏览器的 `ab:reader:v1` 本地存储中，不记录阅读历史或发送统计请求；本地存储不可用时仍可在当前页面使用。系统减弱动效和节省流量的现有保护保持有效。本轮参考与验收见 [优化记录](docs/site-hub-20261030.md)。

## 动态特效

`customization/motion-effects.js` 提供默认开启的樱花飘落、可切换流萤光点、首页循环打字字幕，以及星云缓慢移动与品牌内容进入动画。首页右侧“阅读与特效”和手机菜单“阅读与动效设置”可调整；选择独立保存在本机 `ab:motion:v1`，不会覆盖原有字号与减少动效偏好。

飘落层不接收点击事件，桌面最多 22 个粒子，手机最多 10 个；动画由 CSS 驱动，没有持续运行的 JS 绘制循环。打字字幕只使用一个定时器，首页离开视口后停止；隐藏页面时粒子暂停。减少动效、系统减弱动效和节省流量模式下保留完整静态字幕并暂停这轮新增动画。未增加图片、视频、字体或第三方接口请求。

说明及验收见 [动态特效记录](docs/motion-effects-20261030.md)。`check_site_hub` 同时检查真实粒子/星云位置变化、字幕变化、链接可点击、模式保存、重复 Pjax、手机节点数量、暂停恢复与存储受限情况。

## 文章封面

七篇文章和默认占位图已使用本站附件，避免依赖随机图片服务。素材在 `customization/assets/covers/`，每张 WebP 约 19–26 KB，八张共 179088 字节。

```powershell
.\.venv\Scripts\python.exe -m blog_tools.cover_assets
.\.venv\Scripts\python.exe -m blog_tools.cover_assets --webp
```

第一条只生成 SVG，第二条使用 Edge 导出 WebP。SVG 源码可重复生成；不同平台字体和浏览器版本可能影响 WebP 导出的像素与哈希。更新图片后需上传 Halo、修改 URL/哈希清单并重新验收。现有文章通过后台元数据设置绑定封面；发布器只在新建草稿时使用清单中的 `cover`，不会覆盖已有正式文章。

## 浏览器检查

```powershell
.\.venv\Scripts\python.exe .cdp.py https://aerospaceboy.site/ 390 844 --check
.\.venv\Scripts\python.exe .cdp-shot.py https://aerospaceboy.site/ 390 844 reports/home-390.png
.\.venv\Scripts\python.exe .cdp.py https://aerospaceboy.site/archives/pid-control-intro 390 844 --inject-css customization/aerospaceboy-custom.css --check
.\.venv\Scripts\python.exe -m blog_tools.check_navigation
.\.venv\Scripts\python.exe -m blog_tools.check_header --local-bundle
.\.venv\Scripts\python.exe -m blog_tools.check_header
.\.venv\Scripts\python.exe -m blog_tools.check_header --train-hover
.\.venv\Scripts\python.exe -m blog_tools.check_site_hub --local-bundle
.\.venv\Scripts\python.exe -m blog_tools.check_site_hub
```

`--inject-css` 用于隔离浏览器预览，会在本地文档移除旧定制样式并添加新 CSS；不会修改服务器。桌面和移动视口分别设置设备参数，每次运行使用独立配置目录与动态调试端口，不复用个人浏览器登录状态。

`.cdp2.py` 保留页面表达式检查入口。`.shot*.sh` 保留 Git Bash 截图兼容入口，结果写到 `reports/screenshots/`，不覆盖历史截图；旧亮度阈值不再作为验收标准。

`check_header --local-bundle` 在本机快照中保持线上 CSS/脚本顺序，仅替换两个定制块，不修改服务器；不带该参数时直接检查公网。默认按 390–1920 CSS 像素缩小并重新放大，检查主菜单与站点名/完整工具区是否相撞、是否换行，以及收起后菜单入口是否完整。当前导航由 `header-layout.js` 观察实际占用空间，空间不足时使用原生侧栏，避免浏览器放大后互相覆盖。

`--train-hover` 额外检查 800、849、900、1100 和 1300 宽度下，小火车悬停不会移动按钮或切换导航模式。主题的悬停提示会临时隐藏菜单，宽度计算保留此前实际测量值；小火车外部随机跳转使用原生新标签页链接，保留本站页面。

`check_site_hub` 检查实际 GitHub/RSS 目标、重复 Pjax 下的单实例、浅色卡片对比、动效关闭、字号保存及刷新、简历字号不变和手机菜单。检查使用临时浏览器，不修改个人浏览器的阅读偏好。构建同时拒绝 Thymeleaf 内联表达式起始符，避免普通 JS 嵌套数组意外触发 Halo 服务端模板解析。

## 简历页面维护

简历文本使用 Halo 独立页面保存，PDF 放在本站附件库。当前下载采用用户在 2026-10-30 提供的一页 PDF 原件，部署校验值见 `config/resume-deployment.json`。生成工具 `blog_tools.resume` 从本机私有 JSON 生成 HTML；个人内容、原始文件和产物保持在被忽略的 `backups/`、`build/` 中，仓库只提交工具、样式、部署路径和附件校验值。

```powershell
.\.venv\Scripts\python.exe -m blog_tools.resume --input backups/resume-20261030/resume.json --output build/resume-body.html
```

可选的 `--pdf build/resume-derived-print.pdf` 会重新排版一个独立打印副本，需要文档运行时中的 ReportLab 和 Windows 微软雅黑字体；不要用此派生副本覆盖当前提供下载的用户 PDF 原件。网页结构与 PDF 原稿版式不同，事实内容仍须逐项核对。

发布时须保存后重新打开编辑器核对正文，再发布并直接检查 `/resume` 的服务端内容；不能凭粘贴后可见内容或 HTTP 200 认定保存成功。审计会检查五个主要章节、正文长度、PDF 下载链接和附件哈希。

## 状态与恢复

现有登录历史可使用只读核查工具 `tools/login_evidence.py` 整理。`collect` 必须在已授权的 Halo 服务器运行，通过只读 PostgreSQL 查询和日志读取输出 JSON；`report --input 私有数据.json --output reports/login-records.html` 在本机生成表格。该工具不安装插件、不记录未来事件，也不把设备状态或 HTTP 302 当作完整登录历史。个人账号/IP 数据留在被忽略的 `reports/`，核查结论见 [服务器核查](docs/login-evidence-20261030.md)。

当前维护情况见 [status.md](docs/status.md)。完整恢复需要 Halo 备份、数据库、附件及实际部署资料，见 [recovery.md](docs/recovery.md)；历史 JSON 不能代替恢复演练。

主题元信息和相关资料保留原作者信息，原主题使用条件以其上游项目为准。
