# SEO 配置方案（2026-10-29 修订）

此前 Phase 4 文档将“基本设置里没有 description 输入框”误写成站点没有全局描述能力。Halo 的描述设置实际在 **设置 → SEO 设置**，本修订替代旧方案。

## 首页描述

在 `config/site.json` 维护 `site_description`，运行 `python -m blog_tools.build` 后，将 `build/site-description.txt` 内容保存到 Halo 设置 → SEO 设置 → 站点描述。

预期正文：记录嵌入式、人工智能、机器人、自动化与项目开发中的学习和实践。

SEO 描述作用于首页，其他页面根据各自内容和摘要生成。站点关键词字段可按实际需求填写，但主流搜索引擎不再把它作为主要关键词信号，无需为了本次修复新增插件。

## 关于页摘要

编辑 `/about` 页面，关闭摘要自动生成，改用 `build/about-excerpt.txt` 的手写描述并保存发布。保留现有正文。

必须核对服务端 HTML 的 `description` 和 `og:description` 都已更新，不能只检查页面可见正文。

## 分享图和文章

- Logo、Favicon、默认分享图仍按 `assets-needed.md` 准备，上传后填写真实附件地址。
- 每篇文章的分类、标签和封面应与实际内容匹配。
- 项目案例只添加已经核实的代码、演示和实测数据。
- RSS 与 Sitemap 保留现有插件，通过公网 XML 请求检查，不根据插件文件是否存在判断是否生效。

完整部署与回退步骤见 `../docs/deployment.md`。

[官方依据：Halo 站点设置](https://docs.halo.run/guide/use/settings)
