# 修复验证记录（2026-10-29）

## 故障复现

对原 `.make-posts.py` 的真实发布循环注入一个返回 500 的正文接口，验证其随后仍调用 `/publish`。最小复现命令返回 `FAILED (failures=1)`，错误为 `content failed but publish was still called`。

手机侧栏检查发现 `/projects`、`/archives`、`/about` 等主菜单入口缺失。实际点击显示模式产生 `ReferenceError: rm is not defined`，Escape 曾触发缺失加载框的 `classList` 错误。

## 已通过

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m blog_tools.check_navigation
.\.venv\Scripts\python.exe -m blog_tools.audit --output reports/live-audit.json
node --check customization/mobile-navigation.js
```

- 36 项离线测试通过，包含真实回环 HTTP 传输与完整发布调用链；没有向正式站点创建测试文章。
- Edge 中的七个导航与组件兼容场景通过：混合菜单、重复 Pjax、导航更新、原生菜单恢复、模式切换、关闭组件和保留原生加载行为。
- 七篇文章从旧脚本迁移后，正文逐一与 Git 中原始版本比对一致，仅补充文件末尾换行。
- 部署前检查了首页、文章页的 390/1366px 视口和项目、关于的 390px 视口；长链接、长代码、宽表格与减弱动效测试页通过。
- 线上五个 HTML 页面以及 RSS、Sitemap 检查通过。CSS 和脚本检查同时验证标识、版本属性与实际内容 SHA256，能够发现截断或版本不符。
- 线上手机菜单包含十个主导航链接，项目跳转成功，搜索 ROS2 返回已有文章；模式可从深色切换到浅色再返回深色，Escape 没有新增控制台错误。

本地截图和 JSON 报告位于被忽略的 `reports/`；历史 `phase7-*` 截图保持原样。

## 验证边界

未执行真实文章创建/发布、评论提交、用户权限变更、服务器重启或完整站点恢复。没有新增真实项目案例、实验数字或未经确认的个人信息。服务端备份已生成，本地完整备份下载和恢复演练尚未完成。
