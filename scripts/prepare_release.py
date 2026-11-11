#!/usr/bin/env python3
"""Stage a reviewed commit; fail closed on stale or uncommitted source."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
PUBLIC_DIRS = {'compare', 'data', 'ev-cost', 'ev-vs-gas', 'guides', 'tesla'}
PUBLIC_EXTENSIONS = {'.html', '.css', '.js', '.svg', '.json', '.xml', '.txt'}


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args]).decode().strip()


def prepare(output, approved_commit):
    if output.exists() and any(output.iterdir()):
        raise ValueError('Output must be empty; existing files will not be removed.')
    subprocess.run(['git', '-C', str(ROOT), 'fetch', 'origin', 'main'], check=True)
    head = git('rev-parse', 'HEAD')
    main = git('rev-parse', 'FETCH_HEAD')
    if approved_commit != head:
        raise ValueError('Pass the full, directly approved HEAD SHA as --approved-commit.')
    if git('status', '--porcelain', '--untracked-files=all'):
        raise ValueError('Commit reviewed data and code first; working tree must be clean.')
    if subprocess.run(['git', '-C', str(ROOT), 'merge-base', '--is-ancestor', main, head]).returncode:
        raise ValueError('HEAD does not contain latest GitHub main. Reconcile without discarding data.')
    subprocess.run([sys.executable, str(ROOT / 'scripts/check_routes.py')], check=True)
    files = git('ls-files', '-z').split('\0')
    output.mkdir(parents=True, exist_ok=True)
    hashes = {}
    for name in files:
        path = Path(name)
        if not name or (len(path.parts) > 1 and path.parts[0] not in PUBLIC_DIRS):
            continue
        if path.suffix not in PUBLIC_EXTENSIONS and name != '_headers':
            continue
        if name.startswith('.') or any(part.startswith('.') for part in path.parts):
            continue
        data = subprocess.check_output(['git', '-C', str(ROOT), 'show', f'{head}:{name}'])
        target = output / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        hashes[name] = hashlib.sha256(data).hexdigest()
    digests = json.loads((output / 'data/digests.json').read_text(encoding='utf-8'))
    release = {
        'source_commit': head, 'github_main_at_build': main,
        'built_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'newest_digest': max(d['date'] for d in digests),
        'digest_count': len(digests), 'sha256': hashes,
    }
    (output / 'release.json').write_text(json.dumps(release, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in release.items() if k != 'sha256'}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--approved-commit', required=True)
    args = parser.parse_args()
    prepare(args.output.resolve(), args.approved_commit)
