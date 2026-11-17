"""Deploy three prepared Hao files over an existing SSH alias, with guarded rollback."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import subprocess
import uuid

ROOT = Path(__file__).resolve().parents[1]
THEME = '/opt/halo/halo2/themes/theme-hao/templates'
BACKUP_ROOT = '/opt/halo/maintenance-backups/'
ALLOWED = {'modules/head.html', 'modules/layouts/layout.html', 'modules/ab-page-metadata.html'}

REMOTE = r'''
import base64, hashlib, json, os, shutil, stat, tempfile
from pathlib import Path
p = json.loads(base64.b64decode(PAYLOAD))
root = Path(p['root']).resolve(strict=True)
backup = Path(p['backup'])
assert backup.parent == Path('/opt/halo/maintenance-backups')
assert backup.name.startswith('seo-20261116-')
def digest(data): return hashlib.sha256(data).hexdigest()
def atomic(target, data, original=None):
    fd, tmp = tempfile.mkstemp(prefix='.ab-meta-', dir=target.parent)
    with os.fdopen(fd, 'wb') as stream: stream.write(data)
    os.chmod(tmp, stat.S_IMODE(original.st_mode) if original else 0o644)
    if original: os.chown(tmp, original.st_uid, original.st_gid)
    os.replace(tmp, target)
files = p['files']
assert set(files) == {'modules/head.html', 'modules/layouts/layout.html', 'modules/ab-page-metadata.html'}
for relative in files:
    target = root / relative
    assert root in target.resolve().parents and not target.is_symlink()
if p['mode'] == 'apply':
    for relative, record in files.items():
        target = root / relative
        actual = digest(target.read_bytes()) if target.exists() else None
        assert actual == record['before'], 'Source changed: ' + relative
        assert digest(base64.b64decode(record['data'])) == record['after']
    backup.mkdir(parents=True, mode=0o700, exist_ok=False)
    for relative, record in files.items():
        target = root / relative
        if target.exists():
            saved = backup / relative
            saved.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
            shutil.copy2(target, saved)
    # Install the fragment before anything references it.
    order = ['modules/ab-page-metadata.html', 'modules/head.html', 'modules/layouts/layout.html']
    changed = []
    try:
        for relative in order:
            target = root / relative
            atomic(target, base64.b64decode(files[relative]['data']), target.stat() if target.exists() else None)
            changed.append(relative)
    except Exception:
        for relative in reversed(changed):
            target = root / relative
            if files[relative]['before']:
                atomic(target, (backup / relative).read_bytes(), (backup / relative).stat())
            else:
                os.replace(target, backup / 'withdrawn-ab-page-metadata.html')
        raise
else:
    # Refuse to overwrite any intervening edits. Rollback is an explicit action.
    for relative, record in files.items():
        assert digest((root / relative).read_bytes()) == record['after'], 'Deployed file changed: ' + relative
        if record['before']:
            assert digest((backup / relative).read_bytes()) == record['before']
    for relative, record in files.items():
        target = root / relative
        if record['before']:
            atomic(target, (backup / relative).read_bytes(), (backup / relative).stat())
        else:
            # Preserve the added fragment outside the served theme instead of deleting it.
            os.replace(target, backup / 'withdrawn-ab-page-metadata.html')
print(json.dumps({'mode': p['mode'], 'backup': str(backup), 'hashes': {
    relative: digest((root / relative).read_bytes()) if (root / relative).exists() else None for relative in files}}))
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='aerospaceboy')
    parser.add_argument('--bind-address', required=True)
    parser.add_argument('--receipt', type=Path, default=ROOT / 'backups/seo-20261116/receipt.json')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--rollback', action='store_true')
    parser.add_argument('--sudo', action='store_true', help='Use existing noninteractive sudo; never change directory permissions')
    args = parser.parse_args()
    if args.apply == args.rollback or not re.fullmatch(r'[A-Za-z0-9_-]+', args.host):
        parser.error('Choose exactly one action and use a simple SSH alias')
    if args.apply:
        output = ROOT / 'build/theme-metadata'
        hashes = json.loads((output / 'manifest.json').read_text(encoding='utf-8'))
        if set(hashes) != ALLOWED:
            raise ValueError('Unexpected deployment files')
        before = {'modules/head.html': 'head-before.html', 'modules/layouts/layout.html': 'layout-before.html'}
        records = {}
        for relative, expected in hashes.items():
            data = (output / relative).read_bytes()
            if hashlib.sha256(data).hexdigest() != expected:
                raise ValueError('Build changed: ' + relative)
            original = (ROOT / 'backups/seo-20261116' / before[relative]).read_bytes() if relative in before else None
            records[relative] = {'before': hashlib.sha256(original).hexdigest() if original is not None else None,
                                 'after': expected, 'data': base64.b64encode(data).decode('ascii')}
        payload = {'root': THEME, 'backup': BACKUP_ROOT + 'seo-20261116-' + uuid.uuid4().hex[:10], 'files': records}
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        # A rejected retry must not erase the receipt for a successful deployment.
        with args.receipt.open('x', encoding='utf-8') as receipt:
            receipt.write(json.dumps(payload, indent=2) + '\n')
    else:
        payload = json.loads(args.receipt.read_text(encoding='utf-8'))
        if payload['root'] != THEME or set(payload['files']) != ALLOWED:
            raise ValueError('Unexpected receipt target')
    payload['mode'] = 'apply' if args.apply else 'rollback'
    encoded = base64.b64encode(json.dumps(payload).encode('utf-8')).decode('ascii')
    script = REMOTE.replace('PAYLOAD', repr(encoded))
    result = subprocess.run(['ssh', '-b', args.bind_address, '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10',
                             args.host, 'sudo -n python3 -' if args.sudo else 'python3 -'], input=script.encode('utf-8'), capture_output=True, timeout=40)
    print(result.stdout.decode('utf-8'), end='')
    if result.returncode:
        raise RuntimeError(result.stderr.decode('utf-8'))


if __name__ == '__main__':
    main()
