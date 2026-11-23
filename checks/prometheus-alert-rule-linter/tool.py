#!/usr/bin/env python3
"""Review normalized alert rules for names, expressions, ownership, and a hold duration."""
import argparse
import collections
import configparser
import datetime
import fnmatch
import hashlib
import ipaddress
import itertools
import json
import math
import re
import statistics
import sys
import urllib.parse


def evaluate(data):
    """Evaluate supplied infrastructure metadata without changing remote systems."""
    if not isinstance(data, dict):
        raise ValueError("input must be a JSON object")
    findings = []
    seen = set()
    for rule in data['rules']:
        name = rule.get('alert','')
        issues = []
        if not name or name in seen:
            issues.append('missing-or-duplicate-alert-name')
        seen.add(name)
        if not str(rule.get('expr','')).strip():
            issues.append('missing-expression')
        if re.fullmatch(r'[1-9][0-9]*[smhdw]',str(rule.get('for',''))) is None:
            issues.append('missing-or-unsupported-hold-duration')
        if not rule.get('labels',{}).get('team'):
            issues.append('missing-team-label')
        if issues:
            findings.append({'alert':name,'issues':issues})
    return {'findings':findings,'valid':not findings}


def _check_finite(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("numeric input must be finite")
    if isinstance(value, dict):
        for child in value.values():
            _check_finite(child)
    elif isinstance(value, list):
        for child in value:
            _check_finite(child)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", default="-", help="JSON input file, or - for stdin")
    args = parser.parse_args(argv)
    try:
        if args.input == "-":
            data = json.load(sys.stdin)
        else:
            with open(args.input, encoding="utf-8") as source:
                data = json.load(source)
        _check_finite(data)
        result = evaluate(data)
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
        return 0
    except (OSError, ValueError, TypeError, KeyError, OverflowError, configparser.Error) as error:
        print("Input error: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
