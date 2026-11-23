#!/usr/bin/env python3
"""Browse and run small offline infrastructure checks."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent

def main():
    catalog = json.loads((ROOT / 'catalog.json').read_text())
    names = {item['name'] for item in catalog}
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    listing = sub.add_parser('list')
    listing.add_argument('--area', choices=sorted({item['area'] for item in catalog}))
    run = sub.add_parser('run')
    run.add_argument('name', choices=sorted(names))
    run.add_argument('input', nargs='?', default='-')
    args = parser.parse_args()
    if args.command == 'list':
        for item in catalog:
            if not args.area or item['area'] == args.area:
                print(item['name'] + ': ' + item['purpose'])
        return 0
    return subprocess.run([sys.executable, str(ROOT / 'checks' / args.name / 'tool.py'), args.input]).returncode

if __name__ == '__main__':
    raise SystemExit(main())
