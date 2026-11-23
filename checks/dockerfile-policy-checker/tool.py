#!/usr/bin/env python3
"""Review a Dockerfile for an explicit runtime user, health check, and base image tag."""
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
    lines = [line.strip() for line in data['dockerfile'].splitlines() if line.strip() and not line.lstrip().startswith('#')]
    users = [line.split(None,1)[1] for line in lines if line.upper().startswith('USER ')]
    images = [line.split()[1] for line in lines if line.upper().startswith('FROM ')]
    issues = []
    if not users or users[-1].split(':')[0] in ('root','0'):
        issues.append('missing-nonroot-final-user')
    if not any(line.upper().startswith('HEALTHCHECK ') and not line.upper().startswith('HEALTHCHECK NONE') for line in lines):
        issues.append('missing-healthcheck')
    for image in images:
        if '@sha256:' not in image and (':' not in image.rsplit('/',1)[-1] or image.endswith(':latest')):
            issues.append('mutable-default-base:'+image)
    return {'issues':issues}


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
