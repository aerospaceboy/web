# 导航结构规划（Console 手工执行清单）

> Hao 的主导航属于 **Halo Core 菜单系统**（不是主题 settings.yaml 字段），
> 必须在 Console 中操作，服务器端无法在不绕过认证的情况下代改。

## 操作路径：Console → 外观 → 菜单

### 主菜单（新建或编辑现有"主菜单"分组，共 9 项，按此顺序）

| 序号 | 菜单名 | 链接 | 状态 |
|---|---|---|---|
| 1 | 首页 | `/` | 已存在 |
| 2 | 文章 | `/archives` | 已可用 |
| 3 | 分类 | `/categories` | 已可用 |
| 4 | 标签 | `/tags` | 已可用 |
| 5 | 项目 | `/projects` | **待创建页面后添加** |
| 6 | 瞬间 | `/moments` | 已可用（插件已启用） |
| 7 | 图库 | `/photos` | 已可用（插件已启用） |
| 8 | 友链 | `/links` | 已可用（插件已启用） |
| 9 | 关于 | `/about` | **待创建页面后添加** |

注意：
- `/projects` 与 `/about` 页面创建好之前**不要**先加入菜单（避免死链）。
  页面创建方法见 about.md / projects.md。
- 不保留"默认分类"作为主导航项。
- 搜索按钮、深色模式按钮是主题自带（PluginSearchWidget + nav.right.darkMode），
  不需要进菜单，保持开启即可。

### 菜单建好后的主题设置（Console → 外观 → 主题 → Hao → 主题设置 → 导航）

| 字段 | 建议值 | 说明 |
|---|---|---|
| menus.pc_leftMenu | true | PC 左侧菜单（显示主菜单） |
| menus.phone_leftMenu | true | 移动端左侧菜单 |
| menus.phone_menu | true | 移动端主菜单（手机端可用性） |
| leftMenu（站点名左侧菜单） | 选"主菜单" | 或留空只用顶部菜单 |
| right.darkMode | true | 保留深色切换 |
| right.travelling / article | 按喜好 | "开往"按钮可关，随机文章可留 |

### 页脚相关链接（可选）

主题设置 → 页脚 → `menu`（menuRadio 字段）：可选择一个菜单组显示在页脚，
可选主菜单或之后新建一个精简版"页脚菜单"（关于 / 友链 / RSS）。

## 手机端验收点

- 左上角汉堡菜单可展开主菜单
- 菜单项点击无死链（/projects /about 建好前不加）
- 深色切换按钮在手机端可用
