# 服务端逐页元数据与首页图片预加载

2026-11-16 已部署；2026-11-17 恢复后核对服务器文件及公网审计。本文替代上一轮记录中“逐页 canonical、文章 Schema 尚未实施”的状态，但不把源码提交当作上线依据。

## 线上行为

- 已发布文章、独立页面和首页第一页，由服务端生成各自的 `rel=canonical`，URL 来自 Halo 内容的 permalink 与站点配置。带跟踪查询参数的文章仍指向原内容 URL。
- 每篇文章的服务端 JSON-LD 使用 `BlogPosting`，读取该文真实标题、作者、作者页、发布时间、发布快照修改时间与封面。没有将全部文章归给硬编码作者，也没有用部署时间冒充文章更新时间。
- 不为普通独立页面输出文章 Schema。归档集合、日期筛选及后续分页没有可靠逐页地址时不强行指向首页；这些路由的 canonical 仍需单独适配。
- 首页服务器 head 为已存在的星云 WebP 添加高优先级图片预加载。图片内容、原文件和用户的动效设置未改变。
- 原有 `WebSite` / `Person` 身份脚本和全局注入继续保留，本轮不替换其 CSS/JS。

## Pjax 切页

Hao 1.7.3 原有 Pjax 选择器只同步部分分享标签。新增稳定的 `meta#ab-page-metadata` 标记并让主题同步它，再由 `customization/page-metadata.js` 在切页后同步自有 canonical 和文章 Schema。初次请求中的真实服务端标签仍然存在；这段同步脚本不是用来伪装缺失的服务端 SEO。

没有把 JSON-LD script 本身直接添加到 Pjax 选择器：本站当前 Pjax 库会把根 script 作为 JavaScript 执行。通过 meta 传递经 Thymeleaf 转义的字段，客户端再使用 `JSON.stringify` 更新非执行脚本，避免这个兼容问题。

2026-11-16 已实际检查首页 → 项目 → FPGA 文章 → 归档 → 后退：项目/归档不残留文章 Schema，文章标题、作者与 canonical 一致，实例数各一份；项目到文章的导航保留同一文档的 Performance navigation 记录，确认至少该次使用了 Pjax。浏览器错误日志为空。主题某些跨布局链接仍可能按其原有机制回退为整页加载。

## 可复现文件与部署

源码为 `customization/theme/page-metadata.html`、`customization/page-metadata.js`；构建器只生成修改后的两个主题文件与一个新增片段，不自行部署：

```powershell
.venv/Scripts/python.exe -m blog_tools.theme_metadata --backup backups/seo-20261116
```

备份目录包含从服务器按原字节读取的 `head-before.html`、`layout-before.html`。完整主题不是本仓库维护对象，不能将当前生成结果无条件覆盖到其他主题版本。

`tools/deploy_theme_metadata.py` 使用已有 SSH 别名，不读取浏览器凭据。部署前校验三条固定目标路径、原文件 SHA256 与构建 SHA256；保留文件权限和属主，先安装新片段，再原子替换两个引用文件。异常时恢复已修改文件。生产目录属于服务运行用户，本轮使用服务器已配置的非交互 sudo，没有放宽目录权限。

工具必须显式选择 `--apply` 或 `--rollback`。部署回执以排他创建方式保存，重复尝试不会覆盖成功部署的回退记录；新增测试已验证已有回执逐字节保留，并且不发起 SSH。不要为重试删除旧回执；如另一次经过核对的部署确有必要，应使用新的 `--receipt` 路径。

本轮私有回执在 `backups/seo-20261116/receipt.json`，服务器原文件备份位于回执记载的 `maintenance-backups` 目录，处于公开主题路径之外。回退会先核对现网仍为本次部署版本，恢复两个原文件，并将新增片段移到备份目录，不永久删除它。

文件更改后须通过 Halo 的 **主题 → 详情区更多操作 → 清理模板缓存** 生效。它不同于重载主题配置或重置设置。本轮已在后台完成缓存刷新，无需重启应用。

公开的版本校验值见 `config/theme-metadata-deployment.json`。2026-11-17 通过 SSH 重新读取，三个现网文件的 SHA256 均与该清单和构建产物一致。

## 验证与性能边界

- Python 测试及 JS 语法检查通过；服务端审计验证 canonical、JSON 类型和字段、标题/作者/日期与页面标记一致、重复/缺失/错误标签，以及额外独立页面的 canonical。
- 2026-11-17 公网审计通过 17 个页面及 XML 入口、10 个既有附件，issues 与 warnings 为空，私有记录为 `reports/seo-20261117/live-audit.json`。
- 原始页面、加载样本与前后备份保存在被忽略的 `reports/seo-20261116/` 和 `backups/seo-20261116/`。没有提交账号、令牌或简历正文。
- 2026-11-16 同一 Edge 标签页、两次均禁用浏览器缓存、无网络/CPU 模拟的单次采样：图片请求从 4528.6ms 提前到 618.0ms，发起者从 `img` 变为 `link`，每次只有一个资源记录，传输均为 202912 字节。优化后在 DOMContentLoaded 之前完成图片请求。
- 同次 FCP 从 2512ms 变为 3120ms，load 从 6405.3ms 变为 6512ms，因此没有证据宣称整体首屏、LCP 或网站评分已提升。这个改动只确认提前发现图片，不代替多次性能测量或真实用户 Web Vitals。
- 浏览器实际 200% 缩放尚未完成验收。上一轮 Windows 原生窗口工具无法可靠识别当前网址而结束；页面内 Playwright 快捷键没有改变实际视口，不能当作浏览器缩放结果。此前的窄屏检查也不替代此项。

主题升级会覆盖本轮原生模板修改；升级前保留清单与备份，升级后重新核对锚点、变量、Pjax 行为及服务端输出，再决定是否重建补丁。

参考实现依据：[Halo Thymeleaf 模板](https://docs.halo.run/developer-guide/theme/thymeleaf)、[Google canonical 指南](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)、[Article 结构化数据](https://developers.google.com/search/docs/appearance/structured-data/article)。这些标签不保证索引、排名或富结果。
