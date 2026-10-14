"""Command-line entry points for ArchGen."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from . import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="archgen",
        description="Generate system-design interview problems and rubrics.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "--fake", action="store_true", help="API 없이 고정 예시로 TUI 실행"
    )
    subcommands = parser.add_subparsers(dest="command")
    subcommands.add_parser("harnesses", help="List configured validation harnesses.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the requested command; open the TUI when no command is supplied."""
    args = build_parser().parse_args(argv)
    if args.command == "harnesses":
        print("No validation harnesses are configured yet.")
        return 0

    from .tui.app import ArchGenApp

    ArchGenApp(fake=args.fake).run()
    return 0
