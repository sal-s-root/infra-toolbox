#!/usr/bin/env python3
"""Check selected sshd directives against an explicit expected policy."""
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
    values = {}
    for line in data['config'].splitlines():
        line = line.split('#',1)[0].strip()
        if not line:
            continue
        fields = line.split(None,1)
        if fields[0].lower() in ('match','include'):
            raise ValueError('Match and Include require effective-configuration inspection')
        if len(fields)==2 and fields[0].lower() not in values:
            values[fields[0].lower()] = fields[1].strip()
    findings = [{'directive':key,'expected':value,'observed':values.get(key.lower())}
                for key,value in sorted(data['expected'].items()) if values.get(key.lower())!=value]
    return {'findings':findings,'matches_policy':not findings}


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
