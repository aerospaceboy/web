import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import deploy_theme_metadata as deployment


class ThemeDeploymentTests(unittest.TestCase):
    def test_retry_keeps_existing_rollback_receipt_and_does_not_contact_ssh(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / 'build/theme-metadata'
            backup = root / 'backups/seo-20261116'
            backup.mkdir(parents=True)
            (backup / 'head-before.html').write_bytes(b'original head')
            (backup / 'layout-before.html').write_bytes(b'original layout')
            manifest = {}
            for relative in deployment.ALLOWED:
                target = output / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(b'prepared template')
                manifest[relative] = hashlib.sha256(target.read_bytes()).hexdigest()
            (output / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
            receipt = backup / 'receipt.json'
            original = b'{"backup":"successful deployment receipt"}\n'
            receipt.write_bytes(original)
            argv = ['deploy_theme_metadata.py', '--apply', '--bind-address', '127.0.0.1', '--receipt', str(receipt)]
            with patch.object(deployment, 'ROOT', root), patch('sys.argv', argv), patch.object(deployment.subprocess, 'run') as ssh:
                with self.assertRaises(FileExistsError):
                    deployment.main()
                ssh.assert_not_called()
            self.assertEqual(receipt.read_bytes(), original)
