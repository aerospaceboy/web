"""Build small, reviewable Hao template patches; never deploy from this module."""
import argparse
import hashlib
import html
import json
from pathlib import Path

from .publish import ROOT

HEAD_ANCHOR = '    <meta charset="UTF-8">'
HEAD_INCLUDE = '    <th:block th:replace="~{modules/ab-page-metadata :: metadata(htmlType=${htmlType})}"/>\n'
SELECTOR_ANCHOR = "let pjaxSelectors = ['title',"
SELECTOR_PATCH = "let pjaxSelectors = ['meta#ab-page-metadata', 'title',"


def patch_head(source):
    if 'modules/ab-page-metadata' in source:
        raise ValueError('Metadata fragment is already installed; inspect instead of duplicating it')
    if source.count(HEAD_ANCHOR) != 1:
        raise ValueError('Head anchor changed; theme must be reviewed')
    # Keep charset before other head metadata.
    return source.replace(HEAD_ANCHOR, HEAD_ANCHOR + '\n' + HEAD_INCLUDE, 1)


def patch_layout(source):
    if 'meta#ab-page-metadata' in source:
        raise ValueError('Metadata Pjax selector is already installed')
    if source.count(SELECTOR_ANCHOR) != 1:
        raise ValueError('Pjax anchor changed; theme must be reviewed')
    return source.replace(SELECTOR_ANCHOR, SELECTOR_PATCH, 1)


def build_theme_metadata(backup, output=ROOT / 'build/theme-metadata'):
    config = json.loads((ROOT / 'config/site.json').read_text(encoding='utf-8'))
    image = config['nebula_background_path']
    if not image.startswith('/upload/') or any(c in image for c in '<>"\r\n'):
        raise ValueError('Expected a local uploaded hero image')
    fragment = (ROOT / 'customization/theme/page-metadata.html').read_text(encoding='utf-8')
    script = (ROOT / 'customization/page-metadata.js').read_text(encoding='utf-8')
    if '</script' in script.lower() or '[[' in script or '[(' in script:
        raise ValueError('Unsafe inline script delimiter')
    fragment = fragment.replace('__AB_HERO_IMAGE__', html.escape(image, quote=True)).replace('__AB_METADATA_SYNC__', script)
    files = {'modules/head.html': patch_head((Path(backup) / 'head-before.html').read_text(encoding='utf-8')),
             'modules/layouts/layout.html': patch_layout((Path(backup) / 'layout-before.html').read_text(encoding='utf-8')),
             'modules/ab-page-metadata.html': fragment}
    manifest = {}
    for relative, source in files.items():
        target = Path(output) / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source, encoding='utf-8', newline='\n')
        manifest[relative] = hashlib.sha256(target.read_bytes()).hexdigest()
    (Path(output) / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--backup', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build_theme_metadata(args.backup), indent=2))
