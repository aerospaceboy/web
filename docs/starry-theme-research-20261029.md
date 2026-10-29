# 星空主题调研（2026-10-29）

目标是夜空、星点、银河与安静的阅读层次，而不只是航天名称、霓虹按钮或轨道线框。以下区分“适合参考的视觉”与“能够直接安装到 Halo 的主题”。网站当前环境按本项目既有验收记录为 Halo 2.27.1 / Hao 1.7.3；本次调研没有安装或切换任何主题。

## 候选比较

| 候选与官方预览 | 已核实的星空/视觉依据 | 平台与许可 | 对本站的意义 |
| --- | --- | --- | --- |
| [Astra 官方目录](https://astro.build/themes/details/astro-blog-template-astra/) / [演示](https://astro-template-blog-astra.vercel.app/) | 官方明确描述交互银河、Canvas 星空、随鼠标和滚动变化的纵深、减弱动效支持；星空视觉与编辑排版是完整方向 | **Astro，付费**；本次未购买，未取得授权源码或完整授权条款 | 最值得优先查看的视觉参考；不能把 Astro 模板 ZIP 当作 Halo 主题安装。只借鉴构图思路，自行实现，不拷贝付费代码或素材 |
| [ParticleXF 源码](https://github.com/FloranceYeh/hexo-theme-particlexf) / [官方目录所列演示](https://particlexf-demo.florance.top/) | README 明确有动态星空、深浅模式配色；`stellars.enable` 控制 Canvas 星场，`stellars.seedChanger.enable` 控制星场种子输入 | **Hexo**；[package.json](https://github.com/FloranceYeh/hexo-theme-particlexf/blob/main/package.json) 和 README 声明 MIT | 适合参考轻量动态星场与柔和配色。直接采用需要迁移 Hexo 的内容生成、评论和部署方式；不是本站的直接替换包 |
| [Dream2.0 Plus 源码](https://github.com/hcjike/halo-theme-dream2.0-plus) / [作者演示](https://www.hcjike.com/) | [设置源码](https://github.com/hcjike/halo-theme-dream2.0-plus/blob/master/settings.yaml) 实有 `effects_universe_mode`（宇宙星空，none/day/night/all）；另有明暗、PC/手机背景图，以及海报图片/视频和全屏海报设置 | **Halo 2**；[MIT](https://github.com/hcjike/halo-theme-dream2.0-plus/blob/master/LICENSE)。当前 master [theme.yaml](https://github.com/hcjike/halo-theme-dream2.0-plus/blob/master/theme.yaml) 要求 Halo ≥2.26.0；README 的 1.24.0+ 对应表也为 ≥2.26.0 | 如果确定要换 Halo 原生主题，这是本轮较贴近“星空”的候选。2.27.1 满足声明门槛，但未在本站安装验证；页面模板、菜单、插件表现与旧选择器仍需逐项迁移 |
| [Halo Aurora 源码](https://github.com/Roozenlz/halo-theme-aurora) / [作者预览](https://roozen.top/?preview-theme=theme-aurora) | Halo 移植版有作者提供的深浅截图与预览；上游 [Hexo Aurora](https://github.com/auroral-ui/hexo-theme-aurora) 的核心是极光流彩与未来感，不能据主题名称称其为密集星空 | **Halo 2.x**；[MIT](https://github.com/Roozenlz/halo-theme-aurora/blob/main/LICENSE)，README 要求 ≥2.8.0 | 适合“极光”偏好；与本次明确的夜空方向匹配度次于前三者。后台设置、页面结构和现有 Hao 定制仍需重做 |
| [Starry 源码](https://github.com/meethigher/hexo-theme-starry) / [作者介绍](https://meethigher.top/blog/2020/starry2-0/) | [Hexo 官方目录](https://hexo.io/themes/) 将其描述为 starry theme；作者仓库保留星空主题源码与预览图 | **Hexo，GPL-3.0**；作者 README 快速开始仍建议旧 Hexo 3.9–4.2 / Node 12 环境 | 可以参考传统星空背景和简洁阅读布局，**不推荐为此迁入旧运行环境**。旧依赖说明不等于本次完成了安全审计 |

## 建议

本轮优先保留 Hao，参考 Astra 的“星空主视觉 + 干净内容区”和 ParticleXF 的动态星场层次，自行实现夜空背景、柔和星云、少量星点和克制流星。这样可以继续使用现有文章、菜单、搜索和附件映射，沿用全局注入的可回退流程。这是针对本站现有定制成本的工程判断，不是对其他主题质量的排名。

如果后续需要更换主题，先对 Dream2.0 Plus 做隔离预览；不要在正式站点直接启用一个未核验页面与插件的主题。Hexo/Astro 候选只能作为视觉来源，迁移平台需要另行规划。Hao 本身也由 Hexo Heo/Butterfly 体系移植而来，来源可见 [Halo 生态清单](https://github.com/halo-sigs/awesome-halo)。

设计约束：星空装饰放在文字后方，正文使用有对比度的实色/半透明面板；手机降低星点数量；减弱动态偏好下静止；离屏暂停；保留键盘焦点和原导航。这里没有主题速度实测，不能从截图或星星数量推导性能结论。

## 核验范围与限制

- 依据是作者仓库、设置源码、平台主题目录和作者列出的预览入口，未采用二手“最好看主题”排行。
- 搜索工具对部分演示入口（ParticleXF、Astra、Starry）返回不可访问，对 Dream 作者首页返回超时；这只能说明本次工具读取未成功，不能断言站点已下线。Aurora 预览的 HTML 可读；动态视觉仍应在真实浏览器查看。
- Dream 的网页搜索缓存曾显示旧门槛 ≥2.24.2；本次直接 GET master 原始 README 与 theme.yaml 后均核实为 ≥2.26.0，采用较新的实时源码结果。实际安装时应再次核验所下载 release 包。
- “好看”是视觉取舍。本文件确认的是候选方向、来源和迁移边界；不表示五个演示都完成了截图验收，也不表示任何新主题已在本站上线。
