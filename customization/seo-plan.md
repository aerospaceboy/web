# SEO 基础配置方案（Console 手工执行清单）

> 站点级标题/Logo/Favicon 属于 Halo Core 系统设置，不是主题文件，必须在 Console 改。
> 本文件只给建议值，不写数据库。

## 1. Console → 设置 → 基本设置

| 设置项 | 当前值 | 建议值 | 状态 |
|---|---|---|---|
| 站点标题 | 半截的诗 | 半截的诗 | ✅ 已设置 |
| 副标题 | （待确认） | AerospaceBoy | 需确认/修改 |
| Logo | （待确认） | 上传自己的 logo 图 | 需上传 |
| Favicon | （待确认） | 上传自己的 favicon | 需上传 |

## 2. 站点描述与关键词

Halo 2.27 基本设置没有全局 description/keywords 输入框，
建议按以下方式落地（均为官方能力）：

| 内容 | 建议值 | 落地方式 |
|---|---|---|
| 站点描述 | 记录嵌入式、人工智能、机器人、自动化与项目开发。 | 1) 每篇文章写好摘要（excerpt），Feed/Sitemap 会输出；2) 主题设置 → 关于 → profileDesc / 首页 Banner 小标题承载展示层 |
| Keywords | 嵌入式, AI, 人工智能, ROS2, FPGA, YOLO, Orange Pi, 自动化, 机器人 | 用**文章标签**承载（见 tags 清单），搜索引擎通过 /tags 与标签页聚合收录 |
| Open Graph 默认图 | 一张 16:9 星空/科技图 | 主题设置 → 其他设置 → Open Graph → image |
| Sitemap | 已启用 | PluginSitemap → /sitemap.xml（已验证 200） |
| RSS | 已启用 | PluginFeed → /rss.xml（已验证 200） |

## 3. 文章写作 SEO 习惯（后续）

- 文章设置封面图（避免落到随机图源）
- 设置分类（嵌入式/AI/机器人/自动化/项目记录/学习笔记/比赛记录）+ 2~5 个标签
- 摘要（excerpt）手写一两句，Feed 和分享卡片质量更高
- 自定义别名 slug 用英文（如 `stm32-uart-dma`），URL 更友好

## 4. 无需购买/安装的东西

- 不需要额外 SEO 插件：Sitemap + Feed 已覆盖搜索引擎抓取入口
- 不需要统计平台（性能约束）：如后续要统计，主题支持 51la（about.LingQueMonitorID），体量轻
