# Hao 主题只读审计报告（Phase 4 / 2026-10-24）

## 基本信息

| 项目 | 值 |
|---|---|
| 主题 | Hao（theme-hao） |
| 版本 | 1.7.3 |
| 要求 Halo 版本 | >=2.22.1（当前 Halo 2.27，满足） |
| 作者 | 程序员小航 & 困困鱼 & Carol |
| Setting 定义名 | `theme-hao-setting` |
| 配置存储名 | `theme-hao-configMap`（保存在数据库中，文件侧只有表单默认值） |
| 主题目录 | `/opt/halo/halo2/themes/theme-hao/` |
| 备用主题 | theme-earth（默认主题，未启用） |

## theme.yaml 自定义页面模板（Console → 页面 → 新建页面时可选）

| 模板 | 文件 | 用途 |
|---|---|---|
| 友情链接页面模版 | page_links.html | 友链预设文本版 |
| 关于页面模版 | about.html | 关于页（配合主题"关于"分组设置） |
| 音乐页面模版 | music.html | 音乐页 |
| 留言板页面模版 | comments.html | 留言板 |
| 待办清单页面模版 | todolist.html | 待办清单 |
| 相册页面模版 | album.html | 图库分组页 |
| 最近评论页面模版 | new_comment.html | 最近评论 |

## settings.yaml 设置分组（共 21 组）

basics(基础) / nav(导航) / top(顶部) / layout(布局) / sidebar(侧栏) / footer(页脚) /
post(文章) / categories(分类) / moment(瞬间) / link(友链) / photos(图库) / todo(待办清单) /
equipment(我的装备) / envelope_comment(留言板) / about(关于) / aboutReward(关于-打赏) /
comments(评论) / style(样式) / code(代码块) / tool(小部件) / other(其他设置)

详细字段见 `hao-settings-plan.md`。

## 已安装插件（/opt/halo/halo2/plugins/，13 个 jar）

| 插件 | 版本 | 页面验证 |
|---|---|---|
| PluginSearchWidget（搜索） | 1.7.1 | 前台搜索按钮可用 |
| PluginMoments（瞬间） | 1.19.0 | /moments → 200 |
| PluginPhotos（图库） | 2.1.2 | /photos → 200 |
| PluginLinks（友链） | 2.5.0 | /links → 200 |
| PluginCommentWidget（评论组件） | 3.3.2 | 已安装 |
| PluginFeed（RSS） | 1.5.0 | /rss.xml → 200 |
| PluginSitemap（站点地图） | 1.3.0 | /sitemap.xml → 200 |
| app-store-integration | 1.19.0 | 应用商店 |
| editor-hyperlink-card | 1.9.2 | 编辑器超链接卡片 |
| shiki（代码高亮） | 1.5.1 | 与主题自带代码块二选一 |
| ai-foundation | 1.1.1 | AI 基础 |
| ai-page-builder | 1.1.0 | AI 页面构建 |
| mcp-server | 1.3.1 | MCP 服务 |

`disabled.txt` 为空文件，未见禁用清单；各插件页面返回 200，判定均已启用。

## 页面验收（2026-10-24，经 HTTPS）

| 路径 | 状态 |
|---|---|
| / | 200（title: 半截的诗） |
| /archives | 200 |
| /categories | 200 |
| /tags | 200 |
| /moments | 200 |
| /photos | 200 |
| /links | 200 |
| /console | 302（跳登录，正常） |
| /sitemap.xml | 200 |
| /rss.xml | 200 |

Halo 日志近 4 小时 ERROR 数：0。

## 重要说明

1. `settings.yaml` 是设置**表单定义**，文件中看到的 `value` 是**表单默认值**；
   实际生效的主题配置保存在数据库 `theme-hao-configMap` 中，
   以 Console → 外观 → 主题 → Hao → 主题设置 里显示的为准。
2. 本次审计未修改任何文件、数据库、配置。
3. 备份位置：`/opt/halo/backups/hao-phase4-20261024-212806/`
   （theme-hao 完整目录 + docker-compose.yaml + nginx 站点配置副本，共 8.4M）。
