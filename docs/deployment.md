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
