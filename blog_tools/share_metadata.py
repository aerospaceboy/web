"""Build a guarded Hao Open Graph URL fix from an exact local backup."""
import argparse
import hashlib
import json
from pathlib import Path
import re

from .publish import ROOT

OPEN = '<th:block th:fragment="open-graph(_title,_permalink,_cover,_excerpt,_type)">'
URL = 'th:content="|${site.url}${_permalink}|"'
IMAGE = "image=${not #strings.isEmpty(_cover) ? _cover : not #strings.isEmpty(site.logo) ? site.logo :'null'}"
VARIABLES = '''<th:block th:fragment="open-graph(_title,_permalink,_cover,_excerpt,_type)"
          th:with="abShareBase=${#strings.endsWith(site.url, '/') ? #strings.substring(site.url, 0, #strings.length(site.url)-1) : site.url},
                   abShareUrl=${#strings.isEmpty(_permalink) ? abShareBase + '/' : ((#strings.startsWith(_permalink, 'https://') or #strings.startsWith(_permalink, 'http://')) ? _permalink : abShareBase + (#strings.startsWith(_permalink, '/') ? '' : '/') + _permalink)}">'''


def patch_share_metadata(source, default_cover):
    if not re.fullmatch(r'/upload/[A-Za-z0-9._/-]+', default_cover):
        raise ValueError('Default share cover must be a plain local upload path')
    if source.count(OPEN) != 1 or source.count(URL) != 2 or source.count(IMAGE) != 2:
        raise ValueError('Share template changed or is already patched; review the source')
    image = ("rawImage=${not #strings.isEmpty(_cover) ? _cover : not #strings.isEmpty(site.logo) ? site.logo : '" + default_cover + "'},\n"
             "                     image=${#strings.startsWith(rawImage, '//') ? 'https:' + rawImage : (#strings.startsWith(rawImage, '/') ? abShareBase + rawImage : rawImage)}")
    return source.replace(OPEN, VARIABLES, 1).replace(URL, 'th:content="${abShareUrl}"').replace(IMAGE, image)


def build_share_metadata(backup, output=ROOT / 'build/share-metadata'):
    config = json.loads((ROOT / 'config/site.json').read_text(encoding='utf-8'))
    source = (Path(backup) / 'open-graph-before.html').read_text(encoding='utf-8')
    result = patch_share_metadata(source, config['default_cover_path'])
    relative = 'modules/common/open-graph.html'
    target = Path(output) / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(result, encoding='utf-8', newline='\n')
    manifest = {relative: hashlib.sha256(target.read_bytes()).hexdigest()}
    (Path(output) / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--backup', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build_share_metadata(args.backup), indent=2))
