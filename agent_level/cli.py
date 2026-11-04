"""CLI for the Agent Level Calculator.

Usage:
    python3 -m agent_level.cli profile.json
    python3 -m agent_level.cli < profile.json
"""

import json
import sys

from .core import calculate


def main(argv):
    if len(argv) > 1:
        with open(argv[1], encoding="utf-8") as handle:
            profile = json.load(handle)
    else:
        profile = json.load(sys.stdin)
    result = calculate(profile)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
