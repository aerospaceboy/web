"""Render an original, explicitly labelled architecture illustration; needs Pillow."""
from html import escape
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'customization/assets/projects/video2ai'


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    image = Image.new('RGB', (1600, 900), '#101524')
    draw = ImageDraw.Draw(image)
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900" role="img" aria-labelledby="title desc">',
           '<title id="title">Video2AI 项目流程示意</title><desc id="desc">本地视频经过语音和视觉证据提取、时间轴融合，生成可回查的 AI 资料包。根据源码整理，并非运行截图。</desc>',
           '<rect width="1600" height="900" fill="#101524"/>']
    def rect(box, fill, outline=None, radius=0):
        draw.rounded_rectangle(box, radius, fill=fill, outline=outline, width=2)
        x,y,r,b = box
        svg.append(f'<rect x="{x}" y="{y}" width="{r-x}" height="{b-y}" rx="{radius}" fill="{fill}" stroke="{outline or "none"}" stroke-width="2"/>')
    def line(points, fill, width=2):
        draw.line(points, fill=fill, width=width)
        svg.append(f'<polyline points="{" ".join(f"{x},{y}" for x,y in points)}" fill="none" stroke="{fill}" stroke-width="{width}"/>')
    def text(x,y,value,size=28,fill='#eaf0ff',bold=False):
        font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc' if bold else 'C:/Windows/Fonts/msyh.ttc',size)
        draw.text((x,y),value,font=font,fill=fill,anchor='lt')
        svg.append(f'<text x="{x}" y="{y}" dominant-baseline="text-before-edge" font-family="Microsoft YaHei,sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{fill}">{escape(value)}</text>')
    for x in range(60,1600,100): line([(x,0),(x,900)],'#192034',1)
    for y in range(60,900,100): line([(0,y),(1600,y)],'#192034',1)
    rect((80,65,492,109),'#202742','#4c5076',22)
    text(102,74,'AEROSPACEBOY  /  PROJECT 03',20,'#c3b1ee',True)
    text(80,147,'Video → AI',84,bold=True)
    text(83,257,'让视频成为可回查的证据资料包',38,'#c4cfe3')
    text(83,324,'本地处理  ·  时间戳回查  ·  Agent 接手',24,'#90a3c2')
    cards=[(80,'01','读取视频','单视频 / 文件夹批处理','本地媒体与音轨'),
           (570,'02','提取与融合','字幕 / 关键帧 / 可选 OCR','时间轴与阶段缓存'),
           (1060,'03','交付资料包','离线报告 / Markdown','联系表与精简上传包')]
    for x,num,title,first,second in cards:
        rect((x,435,x+460,704),'#171f32','#35435d',24)
        text(x+30,463,num,28,'#bca5e6',True)
        text(x+30,519,title,36,bold=True)
        text(x+30,588,first,25,'#cad4e7')
        text(x+30,634,second,24,'#94a6c2')
    for x in (546,1036):
        line([(x,567),(x+18,567)],'#c0a9ed',3)
        line([(x+11,560),(x+18,567),(x+11,574)],'#c0a9ed',3)
    text(83,763,'可选云端 AI：字幕与屏幕文字用于总结；关键帧用于画面理解',25,'#c5d3e7')
    text(83,820,'项目流程示意 · 根据源码整理，非运行截图 / 非识别效果实测',21,'#90a3c2')
    svg.append('</svg>')
    (DEST/'overview.svg').write_text('\n'.join(svg)+'\n',encoding='utf-8')
    image.save(DEST/'ab-video2ai-overview-v1.webp',quality=90,method=6)


if __name__ == '__main__':
    main()
