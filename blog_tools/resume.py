"""Build a resume body locally; private source data is never bundled into Git."""

import argparse
from html import escape
import json
from pathlib import Path
import re

from . import configure_console


def render_resume(data):
    esc = lambda value: escape(str(value), quote=True)
    download = data['download']
    if not download.startswith('/') or download.startswith('//') or any(c in download for c in '\r\n<>\\'):
        raise ValueError('Resume attachment must be a same-origin path')
    email = data['email']
    phone = data['phone']
    if not re.fullmatch(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', email):
        raise ValueError('Invalid contact email')
    if not re.fullmatch(r'\+?[0-9 -]+', phone):
        raise ValueError('Invalid contact phone')
    parts = [f'<h2>{esc(data["name"])}</h2>', f'<p>{esc(data["affiliation"])}</p>',
             f'<p><a href="mailto:{esc(email)}">{esc(email)}</a> · '
             f'<a href="tel:{esc(phone.replace(" ", "").replace("-", ""))}">{esc(phone)}</a></p>',
             f'<p><a href="{esc(download)}">下载简历（{ "PDF" if download.endswith(".pdf") else "DOCX" }）</a></p>']
    education = data['education']
    parts.extend(['<h2>教育经历</h2>',
                  f'<h3>{esc(education["school"])}</h3>',
                  f'<p><strong>{esc(education["period"])}</strong></p>',
                  f'<p>{esc(education["courses"])}</p>', f'<p>{esc(education["performance"])}</p>',
                  '<h2>项目经历</h2>'])
    for project in data['projects']:
        parts.extend([f'<h3>{esc(project["title"])}</h3>', f'<p><strong>{esc(project["role"])}</strong></p>'])
        parts.append('<ul>' + ''.join(f'<li><strong>{label}：</strong>{esc(project[key])}</li>'
                                     for key, label in [('summary', '项目内容'), ('work', '主要工作'), ('results', '主要成果')]) + '</ul>')
    for key, title in [('research', '科研经历'), ('leadership', '在校工作经历')]:
        parts.append(f'<h2>{title}</h2>')
        for item in data[key]:
            parts.extend([f'<h3>{esc(item["title"])}</h3>', f'<p><strong>{esc(item["period"])}</strong></p>',
                          f'<p>{esc(item["description"])}</p>'])
    parts.extend(['<h2>荣誉奖项</h2>', '<ul>' + ''.join(f'<li>{esc(item)}</li>' for item in data['awards']) + '</ul>'])
    return '\n'.join(parts) + '\n'


def render_pdf(data, output):
    """Optional PDF export, run with the bundled document runtime."""
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether, PageBreak
    font_dir = Path('C:/Windows/Fonts')
    pdfmetrics.registerFont(TTFont('ResumeCN', str(font_dir / 'msyh.ttc'), subfontIndex=0))
    pdfmetrics.registerFont(TTFont('ResumeBold', str(font_dir / 'msyhbd.ttc'), subfontIndex=0))
    pdfmetrics.registerFontFamily('ResumeCN', normal='ResumeCN', bold='ResumeBold')
    base = ParagraphStyle('body', fontName='ResumeCN', fontSize=9, leading=14, textColor=colors.HexColor('#222b36'), spaceAfter=5, alignment=TA_LEFT)
    heading = ParagraphStyle('section', parent=base, fontName='ResumeBold', fontSize=12, leading=18, spaceBefore=12, spaceAfter=7, keepWithNext=True)
    item = ParagraphStyle('item', parent=base, fontName='ResumeBold', fontSize=9.5, leading=15, spaceAfter=4, keepWithNext=True)
    title = ParagraphStyle('title', parent=base, fontName='ResumeBold', fontSize=25, leading=34, spaceAfter=4)
    esc = lambda value: escape(str(value), quote=True)
    story = [Paragraph(esc(data['name']), title), Paragraph(esc(data['affiliation']), base),
             Paragraph(esc(data['email']) + ' | ' + esc(data['phone']), base), Spacer(1, 5)]
    edu = data['education']
    story.extend([Paragraph('教育经历', heading), Paragraph(esc(edu['school']) + ' | ' + esc(edu['period']), item),
                  Paragraph(esc(edu['courses']), base), Paragraph(esc(edu['performance']), base), Paragraph('项目经历', heading)])
    for project in data['projects']:
        block = [Paragraph(esc(project['title']) + ' | ' + esc(project['role']), item)]
        for key, label in [('summary', '项目内容'), ('work', '主要工作'), ('results', '主要成果')]:
            block.append(Paragraph('<b>' + label + '：</b>' + esc(project[key]), base))
        story.extend([KeepTogether(block), Spacer(1, 5)])
    for key, label in [('research', '科研经历'), ('leadership', '在校工作经历')]:
        if key == 'leadership':
            story.append(PageBreak())
        story.append(Paragraph(label, heading))
        for entry in data[key]:
            story.append(KeepTogether([Paragraph(esc(entry['title']) + ' | ' + esc(entry['period']), item), Paragraph(esc(entry['description']), base)]))
    story.append(Paragraph('荣誉奖项', heading))
    story.extend(Paragraph('• ' + esc(award), base) for award in data['awards'])
    output = Path(output);output.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(str(output), pagesize=A4, rightMargin=42, leftMargin=42, topMargin=34, bottomMargin=34,
                                 title=data['name'] + ' 个人简历', author=data['name'])
    def footer(canvas, doc):
        canvas.setFont('ResumeCN', 8);canvas.setFillColor(colors.HexColor('#7b8290'))
        canvas.drawRightString(A4[0] - 42, 20, str(doc.page))
    document.build(story, onFirstPage=footer, onLaterPages=footer)


def main():
    configure_console()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True, help='Private JSON, kept outside tracked source')
    parser.add_argument('--output', type=Path, required=True, help='Local HTML for Halo rich-text paste')
    parser.add_argument('--pdf', type=Path, help='Optional print PDF, using bundled reportlab and Windows fonts')
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding='utf-8-sig'))
    html = render_resume(data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html, encoding='utf-8')
    if args.pdf:
        render_pdf(data, args.pdf)
    print(json.dumps({'html': str(args.output.resolve()), 'bytes': len(html.encode('utf-8'))}))


if __name__ == '__main__':
    main()
