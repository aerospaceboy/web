"""Create small, deterministic SVG covers without external images or fonts."""

import argparse
from html import escape
import json
from pathlib import Path

from . import configure_console
from .publish import ROOT

DESIGNS = {
    "stm32-dev-env": ("STM32", "嵌入式开发 · 从最小工程开始", "#64d6ba", "chip"),
    "yolo-training-to-edge": ("YOLO", "模型训练 · 边缘部署", "#a998ff", "vision"),
    "ros2-basics": ("ROS2", "节点 · 话题 · 服务 · 动作", "#71b9ff", "network"),
    "pid-control-intro": ("PID", "从控制公式到可运行代码", "#f4be65", "wave"),
    "project-log-template": ("PROJECT", "从立项到复盘", "#ef9b86", "steps"),
    "study-roadmap": ("ROADMAP", "一条可执行的学习路线", "#a7d47e", "route"),
    "contest-prep-template": ("CONTEST", "规则 · 联调 · 交付 · 复盘", "#f1a0cd", "orbit"),
    "default": ("AEROSPACEBOY", "在代码、硬件与星空之间", "#89b8e8", "orbit"),
}


def illustration(kind):
    if kind == "chip":
        pins = ''.join(f'<path d="M{p} 154v36 M{p} 390v36 M154 {p}h36 M390 {p}h36"/>'
                       for p in (226, 290, 354))
        return '<rect x="190" y="190" width="200" height="200" rx="24"/><rect x="238" y="238" width="104" height="104" rx="12"/>' + pins
    if kind == "vision":
        return ('<path d="M170 235v-65h65 M345 170h65v65 M410 345v65h-65 M235 410h-65v-65"/>'
                '<rect x="217" y="217" width="146" height="146" rx="26"/><circle cx="290" cy="290" r="42"/>'
                '<path d="M160 290h50 M370 290h50 M290 160v50 M290 370v50"/>')
    if kind == "network":
        return ('<path d="M184 210l212 0-106 182z M184 210l106 68 106-68 M290 278v114"/>'
                '<circle cx="184" cy="210" r="24"/><circle cx="396" cy="210" r="24"/>'
                '<circle cx="290" cy="278" r="24"/><circle cx="290" cy="392" r="24"/>')
    if kind == "wave":
        return ('<path opacity=".35" d="M150 410V170 M150 320h280"/>'
                '<path d="M160 370c22 0 28-155 68-155s34 145 72 112 37-41 64-25 38 21 66 18"/>'
                '<path stroke-dasharray="7 10" opacity=".5" d="M160 280h270"/>')
    if kind == "steps":
        return ('<path d="M182 208h76v76h76v76h76"/><path opacity=".4" d="M182 392h228"/>'
                '<rect x="160" y="186" width="44" height="44" rx="10"/>'
                '<rect x="236" y="262" width="44" height="44" rx="10"/>'
                '<rect x="312" y="338" width="44" height="44" rx="10"/>')
    if kind == "route":
        return ('<path d="M180 390v-55c0-50 220 10 220-75s-170-15-170-85"/>'
                '<circle cx="180" cy="390" r="20"/><circle cx="230" cy="175" r="20"/>'
                '<circle cx="400" cy="260" r="14"/>')
    return ('<ellipse cx="290" cy="290" rx="160" ry="75" transform="rotate(-30 290 290)"/>'
            '<ellipse cx="290" cy="290" rx="75" ry="160" transform="rotate(-30 290 290)" opacity=".5"/>'
            '<circle cx="290" cy="290" r="26"/><circle cx="417" cy="217" r="12"/>')


def render_cover(slug):
    title, subtitle, color, kind = DESIGNS[slug]
    title_size = 64 if slug == "default" else 86
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="675" viewBox="0 0 1200 675" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)} · 半截的诗</title>
<desc id="desc">{escape(subtitle)}。AerospaceBoy 技术记录封面。</desc>
<defs>
  <linearGradient id="bg" x2="1" y2="1"><stop stop-color="#121b2a"/><stop offset="1" stop-color="#0c111b"/></linearGradient>
  <radialGradient id="glow"><stop stop-color="{color}" stop-opacity=".18"/><stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>
  <pattern id="grid" width="44" height="44" patternUnits="userSpaceOnUse"><path d="M44 0H0V44" fill="none" stroke="#ffffff" stroke-opacity=".035"/></pattern>
</defs>
<rect width="1200" height="675" fill="url(#bg)"/>
<rect width="1200" height="675" fill="url(#grid)"/>
<ellipse cx="950" cy="290" rx="390" ry="350" fill="url(#glow)"/>
<rect x="34" y="34" width="1132" height="607" rx="26" fill="none" stroke="#ffffff" stroke-opacity=".1"/>
<g transform="translate(650 35)" fill="none" stroke="{color}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" opacity=".65">{illustration(kind)}</g>
<g font-family="Segoe UI,Microsoft YaHei,sans-serif">
  <text x="84" y="117" fill="{color}" font-size="19" letter-spacing="5">ENGINEERING NOTES</text>
  <path d="M84 158h54" stroke="{color}" stroke-width="4"/>
  <text x="80" y="319" fill="#eef3fa" font-weight="700" font-size="{title_size}" letter-spacing="1">{escape(title)}</text>
  <text x="84" y="405" fill="#c6d0dd" font-size="30">{escape(subtitle)}</text>
  <text x="84" y="574" fill="#f1f4f8" font-size="27" font-weight="600">半截的诗</text>
  <text x="84" y="610" fill="#8797ad" font-size="17" letter-spacing="3">AEROSPACEBOY</text>
</g>
</svg>
'''


def generate(output=ROOT / "customization/assets/covers"):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    records = []
    for slug in DESIGNS:
        target = output / f"ab-cover-{slug}-v1.svg"
        target.write_text(render_cover(slug), encoding="utf-8", newline="\n")
        records.append({"slug": slug, "file": target.name, "bytes": target.stat().st_size})
    return records


def export_webp(output=ROOT / "customization/assets/covers"):
    from .browser import Browser
    output = Path(output)
    records = generate(output)
    with Browser(1200, 675) as browser:
        for record in records:
            source = output / record["file"]
            target = source.with_suffix('.webp')
            browser.navigate(source.resolve().as_uri())
            browser.screenshot(target)
            header = target.read_bytes()[:12]
            if header[:4] != b'RIFF' or header[8:] != b'WEBP':
                raise ValueError("Edge did not return a WebP image")
            record['webp_file'] = target.name
            record['webp_bytes'] = target.stat().st_size
    return records


def main():
    configure_console()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "customization/assets/covers")
    parser.add_argument("--webp", action="store_true", help="Render uploadable WebP files with Edge")
    args = parser.parse_args()
    print(json.dumps(export_webp(args.output) if args.webp else generate(args.output), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
