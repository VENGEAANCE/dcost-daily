"""Exercise release safeguards against real local Git repositories."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('release', Path(__file__).with_name('prepare_release.py'))
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class ReleaseTests(unittest.TestCase):
    def test_provenance_and_fail_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            remote, checkout = root / 'remote', root / 'checkout'

            def run(*args, cwd=None):
                return subprocess.check_output(['git', *args], cwd=cwd, stderr=subprocess.DEVNULL).decode().strip()

            run('init', '--bare', str(remote))
            run('clone', str(remote), str(checkout))
            run('config', 'user.name', 'Release Test', cwd=checkout)
            run('config', 'user.email', 'test@example.invalid', cwd=checkout)
            run('checkout', '-b', 'main', cwd=checkout)
            (checkout / 'scripts').mkdir()
            (checkout / 'scripts/check_routes.py').write_text('print("fixture routes checked")')
            (checkout / 'data').mkdir()
            (checkout / 'data/digests.json').write_text('[{"date":"2026-11-09"}]')
            (checkout / 'index.html').write_text('reviewed design')
            (checkout / 'docs').mkdir()
            (checkout / 'docs/private.json').write_text('{"private":true}')
            (checkout / '.env').write_text('TEST_ONLY=not-a-secret')
            run('add', '.', cwd=checkout)
            run('commit', '-m', 'fixture', cwd=checkout)
            run('push', 'origin', 'main', cwd=checkout)
            head = run('rev-parse', 'HEAD', cwd=checkout)
            original = release.ROOT
            release.ROOT = checkout
            try:
                with self.assertRaisesRegex(ValueError, 'approved HEAD'):
                    release.prepare(root / 'wrong', '0' * 40)
                (checkout / 'uncommitted.txt').write_text('preserve me')
                with self.assertRaisesRegex(ValueError, 'clean'):
                    release.prepare(root / 'dirty', head)
                (checkout / 'uncommitted.txt').unlink()
                release.prepare(root / 'stage', head)
                stage = root / 'stage'
                self.assertEqual((stage / 'index.html').read_text(), 'reviewed design')
                self.assertFalse((stage / '.env').exists())
                self.assertFalse((stage / 'docs').exists())
                self.assertFalse((stage / 'scripts').exists())
                provenance = json.loads((stage / 'release.json').read_text())
                self.assertEqual(provenance['source_commit'], head)
                self.assertEqual(provenance['newest_digest'], '2026-11-09')
                with self.assertRaisesRegex(ValueError, 'empty'):
                    release.prepare(stage, head)
                (checkout / 'index.html').write_text('new upstream')
                run('add', '.', cwd=checkout)
                run('commit', '-m', 'advance upstream', cwd=checkout)
                run('push', 'origin', 'main', cwd=checkout)
                run('checkout', '--detach', head, cwd=checkout)
                with self.assertRaisesRegex(ValueError, 'latest GitHub main'):
                    release.prepare(root / 'stale', head)
            finally:
                release.ROOT = original


if __name__ == '__main__':
    unittest.main()
