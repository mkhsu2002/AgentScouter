"""CLI for the Agent Level Calculator.

Usage:
    python3 -m agent_level.cli profile.json
    python3 -m agent_level.cli < profile.json
    python3 -m agent_level.cli profile.json --card card.png --logo logo.png
"""

import argparse
import json
import sys

from .core import calculate


def main(argv=None):
    parser = argparse.ArgumentParser(description="Agent Level Calculator")
    parser.add_argument("profile", nargs="?",
                        help="Profile JSON file (default: stdin)")
    parser.add_argument("--card", metavar="PATH",
                        help="Also render a PNG result card")
    parser.add_argument("--logo", metavar="PATH",
                        help="Logo image for the result card")
    parser.add_argument("--name", help="Override profile name on the card")
    parser.add_argument("--species",
                        help="Override profile species on the card")
    parser.add_argument("--birthday",
                        help="Override profile birthday on the card")
    args = parser.parse_args(argv)
    if args.profile:
        with open(args.profile, encoding="utf-8") as handle:
            profile = json.load(handle)
    else:
        profile = json.load(sys.stdin)
    result = calculate(profile)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.card:
        from .card import generate_card
        name = args.name or profile.get("name") or "Unnamed"
        species = args.species or profile.get("species") or "AI Agent"
        birthday = args.birthday or profile.get("birthday")
        generate_card(
            result,
            name=name,
            species=species,
            birthday=birthday,
            logo_path=args.logo,
            output_path=args.card,
        )
        print(f"result card saved to {args.card}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
