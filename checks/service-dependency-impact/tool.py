#!/usr/bin/env python3
"""Find services transitively dependent on a failed component."""
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
    graph = data['dependencies']
    failed = data['failed_service']
    if failed not in graph:
        raise ValueError('failed service is not in the dependency inventory')
    reverse = collections.defaultdict(set)
    for service,dependencies in graph.items():
        for dependency in dependencies:
            if dependency not in graph:
                raise ValueError('unknown dependency '+dependency)
            reverse[dependency].add(service)
    seen = {failed}
    queue = collections.deque([failed])
    while queue:
        for dependent in sorted(reverse[queue.popleft()]):
            if dependent not in seen:
                seen.add(dependent)
                queue.append(dependent)
    return {'failed_service':failed,'potentially_affected':sorted(seen-{failed})}


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
