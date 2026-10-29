# 站点图片素材需求清单（Phase 6 / 2026-10-25）

> 以下是历史素材需求。2026-10-29 已完成七篇文章与默认封面的本站 WebP 替换，源文件位于 `assets/covers/`；其余图片是否仍引用外部资源需按当前页面重新核对。
> 素材准备好后：Console → 附件库 上传，再在对应设置处替换。

## 1. Logo（站点 Logo）

- 用途：Console → 设置 → 基本设置 → Logo；页脚中栏（主题设置 → 页脚 → social_media.centerImg）
- 规格：**PNG 或 WebP，512×512，透明背景**
- 设计方向：`A / Aerospace / Rocket / Orbit` 字母或轨道元素，单色或双色，深浅色背景都要能看清
- 文件大小：< 100 KB

## 2. Favicon

- 用途：Console → 设置 → 基本设置 → Favicon
- 规格：**512×512 原图**（浏览器自动缩到 16-48px），与 Logo 同源
- 要求：极简、少细节（缩到 16px 仍可辨认），建议实底圆形/圆角方形

## 3. Avatar（头像，个人卡片用）

- 用途：主题设置 → 侧栏 → 个人卡片 profile.backgroundImg（或后续头像位）
- 规格：**512×512 或 1024×1024，1:1**
- 风格：与站点星空/航天主题一致

## 4. Homepage Background（首页第一屏背景，可选）

- 用途：主题设置 → 顶部 → 首页第一屏 above.index_img / phone_index_img（仅当开启第一屏时需要）
- 规格：**WebP，1920×1080 或更高（手机版可另备 1080×1920）**
- 内容：深色星空 / 航天，避免大面积纯黑（会淹没星空粒子效果）
- 文件大小：**< 500 KB**

## 5. Moment / Photos / Equipment 页头背景（当前使用主题作者图，待替换）

- 用途：主题设置 → 瞬间 / 图库 / 我的装备 → backgroundImg
- 规格：**1920×600，WebP**
- 内容：深色星空 / 城市夜景 / 电路板纹理均可，文字区域留白（左下角有标题叠加）
- 文件大小：< 400 KB 每张
- 注意：三处可共用一张，也可各用一张

## 6. About Background（仅当启用"关于页面模版"时需要）

- 用途：主题设置 → 关于 → authorCareers.authorCareersBackground / like_bg / music_bg 等
- 规格：**1920×600 或 1200×800，WebP**，深色航天 / 星空风格
- 文件大小：< 400 KB 每张

## 替换位置速查（当前仍引用主题作者图床的配置）

| 配置项 | 当前值 | 替换优先级 |
|---|---|---|
| moment.backgroundImg | liuzhihang.com/upload/moments.png | 高（/moments 页头可见） |
| photos.backgroundImg | liuzhihang.com/upload/moments.png | 高（/photos 页头可见） |
| equipment.backgroundImg | liuzhihang.com/upload/moments.png | 低（装备页未启用） |
| about.*（8 处图片） | liuzhihang/zhheo/dusays 图床 | 低（默认模板下不渲染，启用 Hao 关于模板前必须替换） |
| sidebar.music.*（4 处） | card-music.yyds.pink 占位 | 低（音乐卡片未加入侧栏） |
| top.climb.climbImg | imgapi.yyds.pink 宠物随机图 | 低（宠物挂件未开启） |
