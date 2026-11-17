"""Render the public project index from the same catalogue used by the homepage."""
from html import escape
import re


def validate_projects(items):
    if not isinstance(items, list) or len(items) > 8:
        raise ValueError('Featured projects must be a bounded list')
    paths = set()
    for item in items:
        for key in ('title', 'label', 'summary', 'focus', 'scope', 'version'):
            if not isinstance(item.get(key), str) or not item[key].strip():
                raise ValueError(f'Project {key} is required')
        for key, prefix in (('path', '/archives/'), ('image', '/upload/')):
            value = item.get(key, '')
            if not isinstance(value, str) or not value.startswith(prefix) or any(c in value for c in '\r\n<>"\\?#'):
                raise ValueError(f'Project {key} must be a public site path')
        if item['path'] in paths:
            raise ValueError('Project paths must be unique')
        paths.add(item['path'])
        if not isinstance(item.get('tags'), list) or not all(isinstance(t, str) and t.strip() for t in item['tags']):
            raise ValueError('Project tags must be strings')
        if item.get('github') and not re.fullmatch(r'https://github\.com/[A-Za-z0-9-]+/[A-Za-z0-9_.-]+', item['github']):
            raise ValueError('Project GitHub destination must be a repository on github.com')
    return items


def render_projects(items):
    cards = []
    for item in validate_projects(items):
        e = {k: escape(v, quote=True) for k, v in item.items() if isinstance(v, str)}
        tags = ''.join(f'<span>{escape(tag)}</span>' for tag in item['tags'])
        github = (f'<a href="{e["github"]}" target="_blank" rel="noopener noreferrer">GitHub ↗</a>' if item.get('github') else '')
        cards.append(f'''<div class="ab-project-card" role="article">
<a class="ab-project-cover" href="{e['path']}" aria-label="查看{e['title']}"><img src="{e['image']}" alt="{e['title']}项目展示" width="640" height="360" loading="lazy"></a>
<div class="ab-project-body"><p class="ab-project-kicker">{e['label']}</p><h2><a href="{e['path']}">{e['title']}</a></h2>
<p class="ab-project-summary">{e['summary']}</p><div class="ab-project-tags">{tags}</div>
<dl class="ab-project-facts"><div><dt>实现重点</dt><dd>{e['focus']}</dd></div><div><dt>验证范围</dt><dd>{e['scope']}</dd></div></dl>
<div class="ab-project-actions"><a href="{e['path']}">项目介绍与展示图 →</a>{github}</div></div></div>''')
    return '''<h1>项目与实践</h1>
<p class="ab-project-intro">从通信协议、机器人到 AI 资料工具，记录设计、调试与验证中的实际工作。</p>
<div class="ab-project-grid ab-project-index">\n''' + '\n'.join(cards) + '''\n</div>
<div class="ab-project-directions"><h2>持续探索的方向</h2>
<p><strong>Edge AI</strong> · Orange Pi / RK3588 上的边缘推理与视频流处理。</p>
<p><strong>Embedded</strong> · STM32 / 51 / ESP32 与嵌入式 Linux 的驱动与外设实践。</p>
<p><strong>Robotics</strong> · ROS2 机器人软件架构、感知与控制。</p>
<p><strong>FPGA</strong> · 数字逻辑、通信接口与 HDL 工程实现。</p>
<p><strong>Automation</strong> · 自动控制、工业自动化与智能产线。</p>
<p>项目内容持续更新，具体链接与进展在对应文章里展开。</p></div>\n'''
