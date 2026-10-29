# 关于页面内容（粘贴到 Halo Console）

## 创建页面步骤

1. Console → 页面 → 新建
2. 标题：`关于`，别名/slug：`about`（路径即 `/about`）
3. 自定义模板选择：**关于页面模版（about.html）**
   - 用模板则内容主要由 主题设置 → 关于 分组驱动（见下方"Hao 关于模板字段"）
   - 不用模板则直接把下方 Markdown 放进正文（通用版）
4. 发布后：外观 → 菜单 → 主菜单添加"关于 → /about"

## 通用 Markdown 版（直接粘贴正文）

```markdown
## 关于我

你好，这里是半截的诗。

这里记录我在嵌入式、人工智能、机器人、自动化以及项目开发中的学习、实践与思考。
比起把这里做成一个单纯的笔记仓库，我更希望它最终成为一份长期更新的技术档案。

## 技术方向

- Embedded（STM32 / 51 / ESP32 / Renesas）
- AI（YOLO / Computer Vision）
- Robotics（ROS2）
- Automation（自动化与控制）
- FPGA（数字系统）

## 正在做的项目

见 [Projects](/projects) 页面（持续更新中）。

## 技术栈

- C / C++
- Python
- Linux
- Docker
- STM32
- Orange Pi
- ROS2
- YOLO
- FPGA

## 博客建立目的

把零散的学习笔记沉淀成一份长期维护的技术档案，
顺便把踩过的坑写下来，给同样在折腾硬件和 AI 的人少绕一点路。

## 联系方式

（待补充：由站长本人确认后再填写）

## 更新记录

- 2026-10-24：博客建立，完成基础环境与主题部署。
```

## Hao 关于模板字段（若用 about.html 模板，填 主题设置 → 关于 分组）

| 字段 | 建议值 |
|---|---|
| content（我的介绍，HTML） | `<div class="title1">你好，很高兴认识你👋</div> <div class="title2">我叫 <span class="inline-word">半截的诗</span></div> <div class="title1">是一名折腾 嵌入式、人工智能与机器人的开发者</div>` |
| idea（我的想法，HTML） | `<div class="author-content-item-tips">一定</div> <h2>记得<br>持续<span class="inline-word">记录</span> <div class="mask"> <span class="first-tips">每一次调试</span> <span>每一次踩坑</span> <span>每一次点亮</span> <span>每一次起飞</span> </div> </h2>` |
| helloAbout（我的问候） | Hello there! |
| authorCareers.authorCareersTitle | 在代码、硬件与星空之间 |
| authorCareersTags | 自定义标签：Embedded / AI / Robotics / FPGA / ROS2（每项配背景色） |
| personalities | 自选（16 型人格，非必填） |
| textarea（座右铭 2 行 ×2 块） | 第一块：标题"座右铭"，上行"把笔记写成长期档案，"，下行"把兴趣跑成专业技能。"；第二块自定义 |
| like（关注偏好） | like_title: 嵌入式与边缘 AI；like_bottom: STM32、Orange Pi、YOLO；like_bg 上传自己的图 |
| xjlc（心路历程） | 把"为什么建站？"写成上面"博客建立目的"的 HTML 版 |
| tenyear | 十年之约可保留：start_time 2026-10-24，end_time 2036-10-24，content 自定义 |
| author_info_left_tags / right_tags | 左：半截的诗 / AerospaceBoy；右：Embedded / AI / Robotics |
| aboutAuthorImage / authorCareersPhoto | 上传自己的图（替换默认 liuzhihang.com 图） |

> 注意：`about` 分组默认值里有大量"程序员小航/困困鱼"占位 HTML，用模板就必须逐项替换，
> 否则关于页会保留主题作者文案。若暂时没时间逐项填，可先用通用 Markdown 版（不选模板）。
