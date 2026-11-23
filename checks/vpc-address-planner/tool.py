#!/usr/bin/env python3
"""Allocate a bounded number of equal-size subnets from a parent IPv4 network."""
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
    parent = ipaddress.ip_network(data['parent_cidr'], strict=True)
    prefix,count = int(data['subnet_prefix']),int(data['count'])
    if parent.version!=4 or not parent.prefixlen<=prefix<=32 or not 1<=count<=256:
        raise ValueError('use IPv4, a valid child prefix, and count 1-256')
    capacity = 2**(prefix-parent.prefixlen)
    if count>capacity:
        raise ValueError('requested subnets exceed parent capacity')
    return {'subnets':[str(x) for x in itertools.islice(parent.subnets(new_prefix=prefix),count)],'remaining_subnets':capacity-count}


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
