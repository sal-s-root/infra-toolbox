#!/usr/bin/env python3
"""Evaluate paired error-ratio windows against one burn-rate threshold."""
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
    objective = float(data['objective_percent'])
    threshold = float(data['burn_threshold'])
    if not 0<objective<100 or threshold<=0:
        raise ValueError('objective must be between 0 and 100 and threshold positive')
    budget_ratio = (100-objective)/100
    windows = []
    for row in data['windows']:
        requests,errors = int(row['requests']),int(row['errors'])
        if requests<=0 or not 0<=errors<=requests:
            raise ValueError('each window requires valid nonzero traffic')
        burn = errors/requests/budget_ratio
        windows.append({'name':row['name'],'burn_rate':round(burn,6),'above_threshold':burn>=threshold-1e-9})
    return {'windows':windows,'alert':len(windows)>=2 and all(x['above_threshold'] for x in windows)}


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
