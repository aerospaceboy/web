"""Read-only Halo evidence export and local HTML report; never installs a plugin."""

import argparse
from datetime import datetime, timedelta, timezone
import gzip
from html import escape
import json
from pathlib import Path
import re
import subprocess


QUERY = """SELECT json_build_object(
'users',(SELECT json_agg(json_build_object('account',j#>>'{metadata,name}',
 'display_name',j#>>'{spec,displayName}','disabled',j#>'{spec,disabled}'))
 FROM (SELECT convert_from(data,'UTF8')::jsonb j FROM extensions
 WHERE name LIKE '/registry/users/%') s),
'devices',(SELECT json_agg(json_build_object('account',j#>>'{spec,principalName}',
 'ip',j#>>'{spec,ipAddress}','last_authenticated',j#>>'{spec,lastAuthenticatedTime}',
 'last_accessed',j#>>'{spec,lastAccessedTime}','created_at',j#>>'{metadata,creationTimestamp}',
 'os',j#>>'{status,os}','browser',j#>>'{status,browser}'))
 FROM (SELECT convert_from(data,'UTF8')::jsonb j FROM extensions
 WHERE name LIKE '/registry/security.halo.run/devices/%') s),
'notifications',(SELECT json_agg(json_build_object('recipient',j#>>'{spec,recipient}',
 'created_at',j#>>'{metadata,creationTimestamp}','text',j#>>'{spec,rawContent}',
 'title',j#>>'{spec,title}'))
 FROM (SELECT convert_from(data,'UTF8')::jsonb j FROM extensions
 WHERE name LIKE '/registry/notification.halo.run/notifications/%') s)
);"""


def read_lines(path):
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rt', encoding='utf-8', errors='replace') as stream:
        return stream.read().splitlines()


def collect(database_container, halo_logs, nginx_logs):
    # PostgreSQL enforces a read-only transaction, and SQL projects only allowed fields.
    result = subprocess.run([
        'sudo', '-n', 'docker', 'exec', database_container, 'sh', '-c',
        'PGOPTIONS="-c default_transaction_read_only=on" '
        'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -X -A -t -c "$1"',
        'sh', QUERY,
    ], capture_output=True, text=True, encoding='utf-8', check=True)
    data = json.loads(result.stdout)
    notifications = []
    for item in data['notifications'] or []:
        # Notification bodies stay in memory and are discarded after extracting time/IP.
        text = item.pop('text', '') or ''
        title = item.pop('title', '') or ''
        stamp = re.search(r'20\d\d-\d\d-\d\d \d\d:\d\d:\d\d(?: GMT[+-]\d+)?', text)
        ip = re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', text)
        # The known Halo new-device template includes both fields. Other notifications
        # must not be classified as authentication events just because they exist.
        if stamp and ip and '账号被用于' in title and '登录' in title:
            item.update(login_time=stamp.group(), ip=ip.group(), result='success',
                        evidence='new-device-notification')
            notifications.append(item)
    data['notifications'] = notifications
    requests = []
    nginx_inventory = []
    for path in sorted(nginx_logs.glob('access.log*')):
        lines = read_lines(path)
        nginx_inventory.append({'file': path.name, 'lines': len(lines)})
        for number, line in enumerate(lines, 1):
            match = re.match(r'(\S+) .*?\[([^]]+)\] "(\S+) ([^ ]+) [^"]+" (\d+)', line)
            if not match:
                continue
            ip, stamp, method, url, status = match.groups()
            if method == 'POST' and url.split('?')[0] == '/login':
                requests.append({'time': stamp, 'ip': ip, 'http_status': int(status),
                                 'account': None, 'result': 'unknown',
                                 'source_file': path.name, 'source_line': number})
    data['login_requests'] = requests
    strict = re.compile(r'AuthenticationSuccessEvent|AuthenticationFailureEvent|'
                        r'AbstractAuthenticationFailureEvent|BadCredentialsException|'
                        r'登录成功|登录失败|login (?:success|fail)|authentication (?:success|fail)', re.I)
    data['halo_log_inventory'] = [
        {'file': path.name, 'lines': len(lines),
         'strict_auth_matches': sum(bool(strict.search(line)) for line in lines)}
        for path in sorted(halo_logs.glob('halo.log*')) for lines in [read_lines(path)]
    ]
    data.update(schema_version=1, collected_at=datetime.now(timezone.utc).isoformat(),
                site='https://aerospaceboy.site', halo_version='2.27.1',
                nginx_log_inventory=nginx_inventory,
                coverage='Historical evidence snapshot, not complete per-login audit.',
                ip_trust='Recorded values; client-supplied forwarding headers were not yet hardened.')
    return data


def render_report(data):
    def beijing(value):
        if not value:
            return None
        return datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(
            timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')

    def cell(value):
        return '<td>' + escape(str(value if value is not None else '—')) + '</td>'

    def table(headers, rows):
        return '<div class="scroll"><table><thead><tr>' + ''.join(
            '<th>' + escape(h) + '</th>' for h in headers
        ) + '</tr></thead><tbody>' + ''.join(
            '<tr>' + ''.join(cell(value) for value in row) + '</tr>' for row in rows
        ) + '</tbody></table></div>'

    actual_users = [u for u in data['users'] if u['account'] not in {'ghost', 'anonymousUser'}]
    notices = data.get('notifications') or []
    devices = data.get('devices') or []
    blocks = []
    for user in actual_users:
        account = user['account']
        own_notices = [n for n in notices if n['recipient'] == account]
        own_devices = [d for d in devices if d['account'] == account]
        blocks.append('<section><h2>' + escape(account) + '</h2>')
        blocks.append('<h3>确认的新设备登录事件</h3>')
        if own_notices:
            blocks.append(table(['时间（北京时间）', '记录中的 IP', '结果', '来源'], [
                [n['login_time'], n['ip'], '成功', 'Halo 新设备登录通知'] for n in own_notices]))
        else:
            blocks.append('<p>未找到该账号的新设备登录通知；不表示该账号从未登录。</p>')
        blocks.append('<h3>设备当前状态</h3><p>时间均为北京时间；最近访问时间不是登录时间。'
                      '设备 IP 不保证随重复登录更新，不能与最近认证时间直接配对为一次登录事件。</p>')
        if own_devices:
            blocks.append(table(['系统 / 浏览器', '设备记录 IP', '最近认证', '最近访问'], [
                [f"{d['os']} / {d['browser']}", d['ip'], beijing(d['last_authenticated']), beijing(d['last_accessed'])]
                for d in own_devices]))
        else:
            blocks.append('<p>未找到当前设备记录；不能据此判断是否曾登录。</p>')
        blocks.append('</section>')
    request_table = table(['时间（日志时区 +0800）', '来源 IP', 'HTTP 状态', '账号 / 认证结果', '来源'], [
        [r['time'], r['ip'], r['http_status'], '未知 / 未知', f"{r['source_file']}:{r['source_line']}"]
        for r in data.get('login_requests', [])])
    return ('''<!doctype html><html lang="zh-CN"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="referrer" content="no-referrer"><title>Halo 登录记录核查</title>
<style>body{font:16px/1.7 system-ui,sans-serif;margin:0;background:#f4f6fa;color:#202a3a}
main{max-width:1100px;margin:auto;padding:28px}section,.note{background:white;border:1px solid #dbe1eb;
border-radius:12px;padding:22px;margin:20px 0}h1{font-size:30px}h2{font-size:23px}h3{font-size:18px}
.scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:14px}td,th{border-bottom:1px solid #dbe1eb;
padding:10px;text-align:left;vertical-align:top}th{background:#eef1f8}small{color:#536175}p{margin:10px 0}
@media(max-width:600px){main{padding:14px}section,.note{padding:14px}}
</style><main><h1>Halo 登录记录核查</h1><p>历史证据快照 · ''' + escape(data['collected_at']) + '''</p>
<div class="note"><strong>当前不是完整逐次登录日志。</strong><p>下列记录来自服务器只读查询。
新设备通知可确认部分成功登录，设备表只表示当前状态；未留存的失败事件无法补回。
代理头尚未加固，IP 以“当时记录值”展示，不宣称已经验证真实来源。</p>
<p>未导出密码、令牌、Cookie、会话 ID 或记住我标识。本文件包含账号/IP，仅保存在本机。</p></div>
''' + ''.join(blocks) + '<section><h2>无法归属账号的 POST /login 请求</h2><p>HTTP 302 既可能表示成功，'
    '也可能重定向到错误页面，不能单独判定认证结果；不得按 IP 猜测账号。</p>' + request_table + '''</section>
<section><h2>下一步</h2><p>若需从今后每一次登录开始记录，需要在服务端认证结果处新增审计采集，
并提供仅管理员可见的查询入口。当前尚未安装新插件或启用新采集。</p></section></main></html>''')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='mode', required=True)
    exporter = sub.add_parser('collect')
    exporter.add_argument('--database-container', default='halo-halodb-1')
    exporter.add_argument('--halo-logs', type=Path, default=Path('/opt/halo/halo2/logs'))
    exporter.add_argument('--nginx-logs', type=Path, default=Path('/var/log/nginx'))
    renderer = sub.add_parser('report')
    renderer.add_argument('--input', type=Path, required=True)
    renderer.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.mode == 'collect':
        # ASCII JSON avoids Windows SSH/PowerShell code-page corruption.
        print(json.dumps(collect(args.database_container, args.halo_logs, args.nginx_logs),
                         ensure_ascii=True, indent=2))
    else:
        data = json.loads(args.input.read_text(encoding='utf-8-sig'))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(render_report(data), encoding='utf-8')
        print(str(args.output.resolve()))


if __name__ == '__main__':
    main()
