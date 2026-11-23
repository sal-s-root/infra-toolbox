#!/usr/bin/env python3
"""Split an explicit registry image reference into repository, tag, and digest fields."""
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
    reference = data['reference']
    if '://' in reference or any(c.isspace() for c in reference):
        raise ValueError('use an image reference without a URL scheme or whitespace')
    name,separator,digest = reference.partition('@')
    last = name.rsplit('/',1)[-1]
    tag = last.rsplit(':',1)[1] if ':' in last else None
    repository = name.rsplit(':',1)[0] if tag is not None else name
    if not repository or (separator and re.fullmatch(r'sha256:[0-9a-f]{64}',digest) is None):
        raise ValueError('invalid repository or digest')
    return {'repository':repository,'tag':tag,'digest':digest if separator else None}


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
