"""Record the current reproduction environment without replacing original metadata."""
import datetime
import json
import platform
import sys
from importlib.metadata import version, PackageNotFoundError
from pathlib import Path
from scripts.shared.common import sha256, load_json
from scripts.shared.paths import generated_path

ROOT = Path(__file__).resolve().parents[2]

def main():
    cfg = load_json(ROOT / 'config/experiment.json')
    files = {ROOT / 'config/experiment.json', ROOT / 'config/criteria.json',
             ROOT / cfg['ground_truth_csv'], ROOT / 'requirements.txt',
             ROOT / 'prompts/system.txt'}
    files.update((ROOT / 'scripts').rglob('*.py'))
    files.update((ROOT / 'prompts').rglob('*.txt'))
    files.update((ROOT / 'prompts').rglob('*.json'))
    files.update((ROOT / 'data/processed').glob('*'))
    files = {p for p in files if p.is_file()}
    dependencies = {}
    for package in ('requests', 'nltk', 'yattag', 'numpy', 'pandas', 'scipy'):
        try:
            dependencies[package] = version(package)
        except PackageNotFoundError:
            dependencies[package] = 'not installed'
    manifest = {
        'scope': 'Current reproduction environment; not original execution metadata',
        'created_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'python': sys.version, 'platform': platform.platform(),
        'dependencies': dependencies, 'config': cfg,
        'sha256': {p.relative_to(ROOT).as_posix(): sha256(p) for p in sorted(files)},
    }
    out = generated_path('reproduction_manifest.json')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(out)

if __name__ == '__main__':
    main()
