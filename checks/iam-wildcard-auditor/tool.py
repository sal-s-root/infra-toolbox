#!/usr/bin/env python3
"""Identify wildcard Allow statements requiring an IAM policy review."""
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
    statements = data['policy'].get('Statement',[])
    if isinstance(statements,dict):
        statements = [statements]
    findings = []
    for index,statement in enumerate(statements):
        if statement.get('Effect')!='Allow':
            continue
        actions = statement.get('Action',[])
        resources = statement.get('Resource',[])
        actions = [actions] if isinstance(actions,str) else actions
        resources = [resources] if isinstance(resources,str) else resources
        if any('*' in action for action in actions) or '*' in resources:
            findings.append({'statement':statement.get('Sid',str(index)),'wildcard_actions':[a for a in actions if '*' in a],'all_resources':'*' in resources})
    return {'findings':findings}


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
