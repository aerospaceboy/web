# Hao 主题配置方案（Console 手工执行清单）

> 操作入口：Console → 外观 → 主题 → Hao → 主题设置
> 字段名全部来自 `settings.yaml` 真实定义，无虚构。
> "当前值"为主题表单默认值（若你已在 Console 改过，以 Console 为准）。
> 原则：优先用 Hao 默认暗色体系，只改文案与品牌，不动布局与配色骨架。

## P0 品牌去官方化（必改，否则首页仍是 Hao 演示内容）

### 分组：basics（基础）
| 字段 | 当前默认值 | 建议值 |
|---|---|---|
| siteStartTime | 2023-08-05 | 2026-10-24（你的实际建站日） |
| icp / gongan | 空 | 保持为空（香港服务器，无备案） |
| siteTitle | 空（HTML） | 可留空；站点标题建议用 Halo 系统设置（见 seo-plan.md） |

### 分组：top（顶部）→ Banner 左侧（recentTop 开启时显示）
| 字段 | 当前默认值 | 建议值 |
|---|---|---|
| bannersTitleBig | `<div class="banners-title-big">Halo Theme</div><div class="banners-title-big">Hao</div>` | `<div class="banners-title-big">半截的诗</div><div class="banners-title-big">AerospaceBoy</div>` |
| bannersTitleSmall | 更多信息请关注 GitHub | 在代码、硬件与星空之间，记录每一次探索。 |
| bannersBackground | default（默认技术栈图标） | 先保持 default；之后可切 techStack 上传 Embedded/AI/Robotics/ROS2/FPGA/YOLO/OrangePi 图标 |
| categoryGroup（最多 2 项） | 必看 → / 、热门 → / | 第 1 项：标题"项目"，url `/projects`（页面建好后再改）；第 2 项：标题"分类"，url `/categories`。图标可保留默认 haofont 图标，颜色保持 |

### 分组：top（顶部）→ Banner 右侧
| 字段 | 当前默认值 | 建议值 |
|---|---|---|
| todayRecommend | true | 二选一：① 改内容（见下）；② 直接关闭 |
| todayRecommendContent.todayRecommendUrl | / | 你的第一篇文章地址或 /projects |
| todayRecommendContent.todayRecommendTitle | Halo-Theme-Hao | 你的首个项目名（如 "Orange Pi 边缘 AI"） |
| todayRecommendContent.todayRecommendxTitle | 今日推荐 | 置顶项目 |
| todayRecommendContent.todayRecommendCover | liuzhihang.com 的 hao_dark.jpg | 上传一张自己的星空/电路板风格图（附件库） |
| recommendPost | latest | 保持 latest（自动展示最新文章） |

### 分组：top（顶部）→ 首页第一屏 above
| 字段 | 当前默认值 | 建议值 |
|---|---|---|
| enable_above | false | 保持 false（默认 Banner 已承载品牌；第一屏默认随机图 dmoe.cc 是二次元源，与科技博客不符。若要开启：typed 填自定义文字 + index_img/phone_index_img 必须换成自己的星空图） |

### 分组：sidebar（侧栏）→ 个人卡片 profile
| 字段 | 当前默认值 | 建议值 |
|---|---|---|
| helloText | 困困鱼默认文案（数码科技爱好者…） | 🛠️ 嵌入式开发, 🤖 人工智能, 🚀 机器人与ROS2, 🔧 FPGA与数字系统, 🍊 Orange Pi折腾者, 📝 项目与学习笔记（逗号分隔，随机轮播） |
| profileName | 空（默认站点名称） | 留空（显示"半截的诗"） |
| profileDesc | 空 | 记录嵌入式、人工智能、机器人、自动化与项目开发中的学习和实践。 |
| backgroundImg | 主题自带 profile.webp | 可保留（默认深色风格）或上传自己的图 |
| socialMedia | 空 | 保持为空（未经确认不加任何社交链接） |

### 分组：sidebar（侧栏）→ 侧边栏内容 widgetss（5 个列表都要看）
| 位置 | 当前默认 | 建议值 |
|---|---|---|
| indexWidget | profile, wechat, comments, recent-posts, categories | 删除 wechat（无公众号）；改为 profile, recent-posts, categories, tags-stat |
| postWidget | profile, wechat, toc, comments, recent-posts, categories | 删除 wechat；保留 profile, toc, comments, recent-posts, categories |
| tagWidget / categoryWidget | 含 wechat | 删除 wechat 项 |
| pageWidget | 空 | 保持空 |

### 分组：footer（页脚）
| 字段 | 当前默认值 | 建议值 |
|---|---|---|
| footer_bar_enable | false | 保持 false（避免"困困鱼"描述出现） |
| social_media.centerImg | liuzhihang.com 的 logo.png | 上传自己的 logo（Console → 附件） |
| socialMediaLeft / socialMediaRight | 空 | 保持为空（不加未经确认的社交链接） |
| footer_group.enable_footer_group | true, num=3 | 友链少于 3 个时可改 num 或关闭 |
| footerContent.style_one.runtime_enable | true（徽标是"困困鱼-下班啦"svg） | **改 false**（或上传自己的上班/下班徽标图 work_img / offduty_img） |
| footerContent.default_enable_group.yunzhichi | false | 保持 false |

### 分组：post（文章）
| 字段 | 当前默认值 | 建议值 |
|---|---|---|
| copyrights.content | …程序员小航… | 本文是原创文章，采用 <a target="_blank" href="/cc">CC BY-NC-ND 4.0</a> 协议，完整转载请注明来自 <a href="/" target="_blank">半截的诗</a> |
| copyrights.enable | true | 保持 true |
| aiDescription.aiDescriptionEnable | false | 保持 false（省内存，AI 摘要不需要） |

### 分组：other（其他设置）
| 字段 | 当前默认值 | 建议值 |
|---|---|---|
| loadingBoxs.loadingBoxImg | liuzhihang.com 的 logo.png | 上传自己的 logo；或 loadingBoxEnable=false |
| opengraph.image | 空 | 上传一张 16:9 星空/科技默认分享图 |
| error_404 / error_500.background | 主题自带 gif | 可保留 |

### 分组：moment / photos / equipment（背景图）
| 字段 | 当前默认值 | 建议值 |
|---|---|---|
| moment.backgroundImg | liuzhihang.com 的 moments.png | 上传自己的深色星空图 |
| photos.backgroundImg | liuzhihang.com 的 moments.png | 同上 |
| equipment.backgroundImg | liuzhihang.com 的 moments.png | 不用装备页可不管 |
| moment.bigTitle / smallTitle | 分享生活的小确幸 / 即刻短文 | 可保留 |
| moment.buttonTitle / buttonUrl | 部署瞬间 / GitHub 链接 | buttonTitle 改"查看瞬间"，buttonUrl 改 /moments |

## P1 风格（深色科技感）

### 分组：style（样式）
| 字段 | 当前默认值 | 建议值 |
|---|---|---|
| colorScheme | system | **dark**（你要深色科技感；右上角切换按钮仍保留，访客可手动切回） |
| universe | true | 保持 true（深色模式星空粒子，即"星空感"，性能开销小） |
| themeLightSkin | #425AEF | 保持 |
| themeDarkSkin | #f2b94b | 保持默认（不大量改色）；如想更"科技蓝"可改 #425AEF |
| fontFamily | 空 | 保持（系统字体，性能最好） |
| translate | 简体 + 允许切换 | 保持 |

### 分组：code（代码块）
| 字段 | 当前默认值 | 建议值 |
|---|---|---|
| code.enable | true | 二选一：已安装 shiki 代码高亮插件 → 建议 **false**（用 shiki）；否则保持 true。避免双重高亮 |
| 其余（标题/行号/复制/折叠） | true | 跟随上面开关 |

### 分组：layout（布局）
| 字段 | 当前默认值 | 建议值 |
|---|---|---|
| navs.nav | category | 保持（首页文章导航条显示分类） |
| post.cols | col2 | 保持两列（桌面 2 列 + 手机 1 列自适应） |
| post.postLocation | top | 保持 |
| postRandomImg | source.unsplash.com 随机图 | 建议改为国内可达图源，或以后每篇文章都设置封面 |
| articleCardPolish | false | 保持 false（少动效） |

## P2 可选（按需）

| 分组.字段 | 说明 |
|---|---|
| top.above.enable_above + typed | 第一屏打字机：typed 填「在代码、硬件与星空之间，记录每一次探索。」等；背景图必须换自己的星空图 |
| envelope_comment.message_list | 留言板信笺文案（默认 4 条可换成自己的） |
| other.greeting.enable_greeting | 首页问候语，默认关；可开 |
| tool.* | 右键菜单/右下角按钮/音乐/弹窗默认全关，保持（简洁不花哨） |
| aboutReward | 打赏默认开启赞赏名单区块；无收款码可把 aboutRewardEnable 改 false |

## 不建议动

- nav.menus / nav.leftMenu / nav.right：右侧按钮（开往、随机文章、切换模式）按喜好即可，darkMode 必须 true
- categories.use：分类页默认样式即可（3D 样式偏花哨）
- other.staticResource.use：保持 local（本地静态资源，最稳）
- other.vanillaLazyload.enable：保持 true（懒加载省流量）
