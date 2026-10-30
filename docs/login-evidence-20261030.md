# 登录历史服务器核查（2026-10-30）

## SSH 连接

本机已有 `aerospaceboy` SSH 别名和密钥。默认连接经过 Mihomo 虚拟网卡，在服务器版本交换前断开；单次 SSH 命令绑定 WLAN 当前 IPv4 地址后，成功校验已知主机密钥并完成 publickey 认证。后续多次只读命令均通过该路径成功。证据支持连接路径是关键因素，不将此前失败误报成密钥失效。未关闭代理、修改网络路由或放宽主机密钥校验。

绑定地址属于当前本机网卡，DHCP 变化后需要重新读取，不应把本次地址写死到永久 SSH 配置。

## 实际部署及读取范围

- `/opt/halo/docker-compose.yaml` 部署 Halo 2.27.1 与 PostgreSQL 15.4。
- Halo 数据位于 `/opt/halo/halo2`，应用仅绑定主机 `127.0.0.1:8090`，由 Nginx 代理公网请求。
- 检查 Halo 当天日志和 2026-10-24 至 10-29 的六份压缩归档；严格认证事件关键词没有命中。更宽泛的 security 等关键词仅找到初始化/异常链上下文，不能当作登录事件。
- 检查 Nginx 当前日志、前一日日志及四份压缩归档。找到五条 `POST /login`，均为 302。日志没有账号和认证结果，不能按 IP 猜测归属，也不能把 302 当作成功或失败。
- PostgreSQL 使用 `PGOPTIONS="-c default_transaction_read_only=on"`，只查询所需用户、设备和通知字段；没有选择密码、令牌、Cookie、会话 ID 或 remember-me 标识。

## 可确认的历史边界

数据库有两个实际账号，另有两个被禁用的内置身份。实际账号中，一个账号有两条设备状态和两条新设备登录通知，另一个没有这类留存记录。

两条通知可以确认两次新设备登录成功。设备的最近认证时间会被更新；其 IP 字段未必随重复认证更新，因此不能把设备表的一行视为完整登录事件，更不能把最近访问时间当成登录时间。未找到记录不证明账号从未登录，缺失的失败历史不能补回。

只读导出工具：`tools/login_evidence.py`。在已授权的服务器通过标准输入执行 `collect`，不写服务器文件、不安装插件；输出 ASCII JSON，避免 Windows SSH/PowerShell 编码损坏。随后本地使用 `report --input ... --output ...` 生成 HTML。

实际数据与页面位于被 Git 忽略的 `reports/login-records-20261030.json`、`reports/login-records-20261030.html`。只保存在本机，没有加入公开站点或 Git。页面展示两个账号的部分成功证据、设备状态和无法判定的请求，并明确区分证据类型。

验证：实际服务器导出后回读确认上述数量；浏览器检查 HTML 文字、两类证据表及北京时间转换，截图保存于私有 `reports/`。全部 58 项单元测试通过，包括输出中额外的秘密字段不会被渲染、账号字段 HTML 转义，以及未知重定向不会被当作认证成功/失败。

## 来源 IP 与后续采集

Nginx 当前设置 `X-Real-IP $remote_addr`、`X-Forwarded-For $proxy_add_x_forwarded_for`。当前 Halo 2.27.1 的 `IpAddressUtils` 优先取 `X-Forwarded-For` 第一个值。因此客户端提供的转发头可能影响应用记录值。没有在生产认证流程中注入伪造 IP 或修改现网配置；报告将 IP 标为记录值，不声称所有历史 IP 已验证可信。未来采集前应核实完整上游代理拓扑并限定可信来源，不能盲目信任任意转发头。

现有原生设备表与通知无法满足每个账号每次成功/失败的要求。未来完整记录需要在实际认证结果处增加服务端审计，覆盖本站启用的密码、验证码及二次认证流程，提供管理员专用查询和明确留存期限；不能仅根据 HTTP 状态生成结果。当前没有安装新认证插件、改变原登录方式或开始新的逐次采集。

参考当前版本拥有者源码：

- [设备记录更新](https://github.com/halo-dev/halo/blob/v2.27.1/application/src/main/java/run/halo/app/security/device/DeviceServiceImpl.java)
- [新设备通知](https://github.com/halo-dev/halo/blob/v2.27.1/application/src/main/java/run/halo/app/security/device/NewDeviceLoginListener.java)
- [客户端 IP 选择](https://github.com/halo-dev/halo/blob/v2.27.1/application/src/main/java/run/halo/app/infra/utils/IpAddressUtils.java)
- [登录结果增强机制](https://docs.halo.run/developer-guide/plugin/api-reference/server/login-handler-enhancer)
