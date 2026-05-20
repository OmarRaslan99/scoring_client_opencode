from __future__ import annotations

import sys

from app.main import cli


def main() -> int:
    args = sys.argv[1:]
    if args and args[0] == "evaluate":
        args = args[1:]
    return cli(args)


if __name__ == "__main__":
    raise SystemExit(main())