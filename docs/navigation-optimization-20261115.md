# 第二批优化：导航、键盘与站点身份

2026-11-15 已通过 Halo 后台保存、重开回读和公网检查；Git 推送不作为上线依据。

## 已上线

- 顶部主导航依次为首页、项目、文章、关于我、简历，其余六项放入点击展开的“更多”。保留 CMS 原生链接节点和目标，未更改后台菜单数据。关闭 JavaScript 时仍使用原有平铺菜单。
- 窄屏侧栏按同样顺序呈现主要入口，其余放在“发现与交流”下。当前页面有背景与底线提示，并输出 `aria-current`。
- 添加跳到主要内容、可聚焦的菜单开关和关闭按钮。Enter/空格打开，Esc 关闭，关闭后返回开关；侧栏打开期间背景 `inert`，Tab/Shift+Tab 在侧栏中循环。收起的侧栏保持 `inert` 和 `aria-hidden`。
- 使用原生 `details/summary` 实现更多菜单，支持键盘展开、Esc 收起、焦点移出和点击外部收起。处理 Hao 全局 details 样式带来的绝对定位、裁切和 74px 内容外边距冲突。
- 服务端全局 head 新增一份 `WebSite` / `Person` JSON-LD，只描述已有站点与公开作者资料，关联关于页及 GitHub。未添加不存在的站内搜索接口、个人履历或奖项。普通 HTTP 请求即可读到，不依赖客户端修改 meta。

## 实施与核对

- `customization/navigation-accessibility.js` 加入现有组合脚本，具有重复安装保护，并在 `pjax:complete` 后重新整理菜单。
- `blog_tools/seo.py` 生成站点身份数据；脚本上下文转义防止关闭标签注入。现有 Thymeleaf 内联开头保护保留。
- `blog_tools.audit` 检查 JSON 可解析、内容与配置一致、只有一份身份脚本；新增两篇精选项目文章到审计范围。
- 67 项单元测试通过，新增检查覆盖 JSON 转义、作者外链限制、重复/损坏/错误的服务端 JSON-LD；JS 语法检查与构建通过。
- 公网审计：17 个页面及 XML 入口、10 个既有附件通过，issues 与 warnings 均为空，见私有 `reports/navigation-20261115/live-audit.json`。
- Edge 实际 CSS 宽度 2042px 与 344px 下检查。窄屏无全页横向溢出，侧栏全部 11 个导航链接保留。Enter、空格、Esc、Shift+Tab 循环及鼠标关闭通过；动画完成后点击关闭按钮有效。
- 浅色菜单为白底深字，检查后恢复原有深色偏好。项目页与首页 Pjax 往返后，更多菜单、关闭按钮、跳过链接各一份，导航仍为 11 条；当前页提示更新正确。跳过链接把焦点放到正文，滚动后正文距离顶部 88px。
- 保存后重新打开后台，复制全局 head 回读，与部署内容按换行归一化后完全一致；只替换自有 CSS/JS 块并添加身份块，保留其他注入。

## 边界与回退

这不是 Lighthouse、真实用户 Core Web Vitals、实际手机或读屏器验收；窄屏重排检查也不声称已完成浏览器 200% 缩放的完整矩阵。未承诺搜索排名或富结果。

本轮没有部署逐页 canonical 或 `BlogPosting`。共享全局注入不应把所有页面指定为首页 canonical；后续需要适配服务端主题或适用的元数据扩展，核对页面 URL、标题、日期和作者后再做。参考 [Google canonical 指南](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)、[Article 结构化数据](https://developers.google.com/search/docs/appearance/structured-data/article)、[Halo 模板与注入扩展点](https://docs.halo.run/developer-guide/theme/template-tag)。

部署前完整注入在私有 `backups/navigation-20261115/global-head.html`；需要回退时在后台恢复该内容，重开核对并重新检查公网。不要直接运行新版审计并期待旧版本通过新的身份数据与哈希要求。没有改动文章正文、简历附件、主题安装包或登录流程。

当前 CSS SHA256：`0dee09232a2508f62c7dea72d2447db909f7d953b2565d0b81c2b33bdde9b016`。

组合 JS SHA256：`dca5818aa0c3554cffb9edc590c96720976611cf36daae6820ded3dbb1057f6e`。
