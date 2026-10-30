# 全站样式与 SEO 部署

本仓库包含修复后的代码和可生成的部署文件。GitHub 推送不会自动修改 Halo 数据；后台保存和公网验收是独立步骤。

## 生成可检查文件

在仓库根目录执行：

```powershell
.\.venv\Scripts\python.exe -m blog_tools.build
```

输出 `build/global-head.html`、`build/site-description.txt`、`build/about-excerpt.txt` 和带 CSS、导航脚本校验值的 `build/manifest.json`。该命令不联网。

## 保存前留档

1. 在 Halo 控制台生成完整备份并下载到仓库外或被忽略的 `backups/`。
2. 复制当前“全局 head 标签”、首页 Banner 大标题 HTML、站点描述和关于页手写摘要到本地私有文件。
3. 保留现有追踪代码、其他注入代码、图片配置和 Banner 品牌 HTML。

## 全站 CSS

进入 **设置 → 代码注入 → 全局 head 标签**，把 `build/global-head.html` 的完整内容合并到已有代码中并保存。

- 首次部署时追加到已有代码之后，不覆盖其他代码。
- 后续更新时替换 `id="aerospaceboy-global-style"` 的 `<style>` 和 `id="aerospaceboy-mobile-navigation-script"` 的 `<script>` 块，各保留一份；保留其他所有注入内容。
- 随后进入 Hao 主题设置 → 顶部 → Banner → 大标题，从 HTML 中删除包含 `--ab-radius` 的旧 `<style>` 块，保留其他品牌内容。
- 首页、归档、项目、关于和文章页都应出现同一个带版本校验值的样式块。
- 不修改主题发行文件；主题升级后仍需重新检查选择器和页面显示。

新 CSS 为亮色模式增加独立变量，处理长链接、代码块和宽表格；首页空状态与移动端品牌文字限定在含 `#home_top` 的页面。它不再通过给整个页面添加 `overflow-x:hidden` 来掩盖溢出。

导航脚本从现有主导航同步手机侧栏缺失的链接，支持重复执行和 Pjax 页面切换；原生侧栏已存在的链接不会重复添加。它还兼容 Hao 在关闭右键菜单或加载框后仍调用相应对象的模式切换和 Escape 行为，保留原有主题切换函数。

## SEO

进入 **设置 → SEO 设置**，将站点描述设为 `build/site-description.txt` 内容。保留当前搜索引擎可见性，不为了本次修复切换索引开关。

从页面列表中打开 slug 为 `about` 的行操作菜单 → 设置，关闭摘要自动生成，手写摘要为 `build/about-excerpt.txt` 内容并保存。现有已发布页面的摘要保存后需检查公网更新；仅修改元数据时无需打开正文编辑器。

当前后台未安装支持 MARKDOWN 格式的正文编辑器，直接点页面标题会报编辑器缺失。本次使用列表的设置面板完成摘要修复；没有安装新插件或转换现有正文格式。

验收要同时读取 `description` 与 `og:description`。若 Hao 的 Open Graph 仍沿用旧值，应检查主题和页面摘要缓存，不能只凭后台“保存成功”认定修复完成。不要用浏览器 JavaScript 修改 meta 作为 SEO 修复。

## 验收

```powershell
.\.venv\Scripts\python.exe -m blog_tools.audit --output reports/live-audit.json
.\.venv\Scripts\python.exe .cdp.py https://aerospaceboy.site/ 390 844 --check
.\.venv\Scripts\python.exe .cdp.py https://aerospaceboy.site/archives/pid-control-intro 390 844 --check
```

`audit` 会检查服务端输出的 CSS 标识、版本、摘要和 XML 入口；仍有问题时返回非零退出码。CDP 检查布局宽度，不代替菜单、搜索、评论和深色切换的人工交互验收。

检查实际导航脚本可运行 `python -m blog_tools.check_navigation`。它在隔离浏览器的本地测试页检查平铺菜单、重复 Pjax、菜单更新、原生菜单恢复、明暗切换与关闭组件兼容，不访问 Halo 管理 API。

也可先用 `--inject-css customization/aerospaceboy-custom.css` 做隔离浏览器预览；它只修改本地浏览器文档，**不代表线上已经部署**。预览会移除当前页面中包含 `--ab-radius` 的旧定制样式，模拟实际迁移。

## 回退

恢复保存前的全局 head、Banner HTML、站点描述与关于页摘要，再重新执行公网检查。完整站点恢复步骤见 `recovery.md`。

## 官方依据

- [Halo 代码注入和 SEO 设置](https://docs.halo.run/guide/use/settings)：全局 head 作用于所有页面，SEO 站点描述作用于首页。
- [Halo 2.27.1 PostEndpoint](https://github.com/halo-dev/halo/blob/v2.27.1/application/src/main/java/run/halo/app/core/endpoint/console/PostEndpoint.java)：草稿正文回读使用 `head-content`，发布正文回读使用 `release-content`；`content` GET 另需 snapshotName，不能用于无参数回读。
- [Hao 侧栏模板](https://github.com/chengzhongxue/halo-theme-hao/blob/3afd1752d97d57dbd00f51a6ebc0dbc35ce1ac5a/templates/modules/sidebar.html)：主菜单项被限制为含子菜单才渲染，与本站一级主菜单结构不符。

## 封面与链接兼容部署

1. 上传 `customization/assets/covers/*.webp` 到 Halo 附件库。SVG 保留为编辑源，不为上传它而放宽服务端附件安全策略。
2. 在文章列表的行操作 → 设置 → 封面图中选择对应附件并保存；这不需要打开缺失的 Markdown 编辑器，也不修改正文。
3. Hao 主题设置 → 布局 → 随机封面改为 `https://aerospaceboy.site/upload/ab-cover-default-v1.webp?v=1`。保留查询参数，主题会追加 `&文章标题`，避免追加到文件路径导致 404。
4. 在文章版权设置中使用 `customization/copyright.html`，保持原有许可名称。
5. `config/site.json` 中的 `privacy_policy_path` 和 `default_cover_path` 会写入构建脚本并纳入哈希校验。重新生成、更新全局注入后，实际检查隐私入口和图片回退。
6. 更新 `config/covers.json` 的实际上传 URL、字节数、SHA256，以及文章清单的封面路径。修改后的新素材必须重新上传；Git 推送不会更新附件。

隐私修复限于评论区链接入口：Hao 1.7.3 固定的 `/privacy` 由兼容脚本改为 `/privacy-policy`。关闭 JavaScript 或直接请求旧路径仍会 404，正式主题修订或服务器重定向可以后续替代此兼容代码。当前隐私正文仍待根据实际服务完善。

回退本轮时恢复 `backups/optimization-20261029/` 中全局注入、版权与随机封面值，将七篇文章封面还原为空；不必删除已上传附件。该私有目录未提交到 Git，不能替代完整 Halo 备份。

## 轨道首页与动效

`blog_tools.build` 将 `mobile-navigation.js` 和 `space-effects.js` 合并到同一个带 SHA256 的脚本块。更新 CSS 或任一脚本都应重新构建并完整替换两个标识块，保留其他注入代码。仅检查单个源脚本哈希不能代表组合文件已部署。

增强区只在存在 `#home_top` 时创建，复制已有品牌名和描述文本；不修改原始 Banner 配置。手机、浅色和减弱动效规则均在统一 CSS 中。若 Halo 更换主题结构，应先检查选择器；脚本未成功生成新品牌区时旧 Banner 保持可见。

本轮回退：恢复私有 `backups/orbit-20261029/global-head.html`，再刷新页面确认原首页和既有封面恢复。该文件只是本轮代码注入备份，不是数据库或完整站点备份。

## 当前星云素材部署

先上传 `customization/assets/nebula/ab-nebula-night-v1.webp` 到 Halo 附件库，确认实际 URL、大小与 SHA256，再更新 `config/site.json` 的 `nebula_background_path` 和 `config/visual-assets.json`。PNG 保留为编辑源，线上不引用 PNG。

重新构建并更新全局 CSS/组合脚本。背景路径会编译到运行时配置并纳入脚本哈希。公网审计会下载封面与视觉素材逐一核验；浏览器还须确认 `.ab-nebula-image` 加载成功、标题与按钮可读、手机未横向溢出。

浅色模式的主视觉有意保留深色夜空与白字；其余区域仍随主题切换。切勿仅把主视觉文字变黑而沿用深色图片。

本轮回退恢复 `backups/nebula-20261029/global-head.html`。已上传但不再引用的背景可保留，不必为回退删除附件。

## 鼠标光效

组合脚本还包含 `pointer-effects.js`。更新后运行构建并替换同一全局脚本与 CSS；无需安装插件或上传新素材。桌面细指针、无减弱动效且未开启节省流量时才启用，浅色使用独立混合配色。

验收应实际移动鼠标并点击底层按钮，检查重复 Pjax 后仅一层、固定 12 个尾迹节点，触屏与减弱动效时没有该层。仅把视口缩到手机宽度不等于模拟触屏，本仓库另行启用触摸模拟后验证。

回退恢复 `backups/pointer-20261029/global-head.html`，刷新页面即可。

## 简历页面部署

1. 保留原始简历到私有 `backups/resume-20261029/`，从已经核对的内容生成 `build/resume-body.html` 与 PDF。不要把联系信息和源文件加入 Git。
2. Halo 本地存储原先只允许图片、视频、音频。用户在本次任务中明确授权启用“文档”分类后，才新增该项；无需启用“无限制”、SVG 或压缩包，文件大小设置保持原样。
3. 上传 PDF，回读检查 MIME、大小及 SHA256。更新 `config/resume-deployment.json`；该清单只含部署路径、页数和文件校验值，不包含简历正文。
4. 在现有 `/resume` 独立页面用富文本编辑器保存内容，别名固定为 `resume`，摘要单独填写，评论关闭。必须重新打开编辑器检查正文，并核对 PDF 链接后再发布。
5. 在主菜单添加“简历”入口。构建全局注入后，`resume-enhancement.js` 还会提供首页入口、页内目录和分组卡片；原始章节和链接保留在服务端 HTML，脚本只调整布局。
6. 检查 `/resume`、首页导航、PDF 下载和触屏布局。`audit` 不把空正文或仅页面标题的 HTTP 200 视作通过。

2026-10-30 已按以上顺序完成上线。保存后重开编辑器及公网服务端正文均核对全部 44 个源字段；导航、首页入口、CSS/JS 和 PDF 已验收。该轮回退配置位于私有 `backups/resume-20261030/`；验证边界见 `docs/resume-recovery-20261030.md`。
