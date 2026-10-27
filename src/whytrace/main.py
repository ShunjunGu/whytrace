from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parents[2]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

load_dotenv(_ROOT / ".env")

from whytrace.agent import WhyTraceAgent  # noqa: E402
from whytrace.demo_questions import DEMO_QUESTIONS, format_catalog, get_demo  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="whytrace", description="WhyTrace CLI — Track 02 MVP")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="Show Zetaris / Meterless mode")
    sub.add_parser("ping", help="Connectivity check (mock always OK; live hits Zetaris)")
    sub.add_parser("demos", help="List curated demo questions")

    p_ask = sub.add_parser("ask", help="Investigate a question with evidence")
    p_ask.add_argument("question", nargs="*", help="Natural language question")
    p_ask.add_argument(
        "--demo",
        metavar="ID",
        help="Use a curated demo question id (see `whytrace demos`)",
    )

    p_audit = sub.add_parser("audit", help="Show Meterless trust ledger")
    p_audit.add_argument("--limit", type=int, default=30)
    p_audit.add_argument(
        "--memory",
        metavar="ID",
        help="Filter ledger events to one memory id (ev-…)",
    )

    p_rem = sub.add_parser("remember", help="Store a user note in H-MEM")
    p_rem.add_argument("text", nargs="+")

    args = parser.parse_args(argv)
    agent = WhyTraceAgent()

    if args.cmd == "status":
        print(json.dumps(agent.status(), indent=2))
        return 0

    if args.cmd == "ping":
        result = agent.ping()
        print(json.dumps(result, indent=2))
        ok = bool(result.get("zetaris", {}).get("ok"))
        return 0 if ok else 2

    if args.cmd == "demos":
        print(format_catalog())
        return 0

    if args.cmd == "ask":
        if args.demo:
            try:
                demo = get_demo(args.demo)
            except KeyError as exc:
                print(str(exc), file=sys.stderr)
                return 2
            question = demo["question"]
            print(f"# demo [{demo['id']}] {demo['title']}\n")
        else:
            if not args.question:
                print(
                    "Provide a question or --demo ID. Try: python -m whytrace demos",
                    file=sys.stderr,
                )
                return 2
            question = " ".join(args.question)
        result = agent.ask(question)
        print("=== WhyTrace ===")
        print(
            json.dumps(
                {"mode": result["mode"], "warning": result.get("warning")},
                indent=2,
            )
        )
        print()
        print(result["answer"])
        print()
        print("--- findings ---")
        for f in result.get("findings") or []:
            print(f"[{f['id']}] {f['claim']}")
        if result.get("warning") == "zetaris_error":
            return 2
        return 0

    if args.cmd == "audit":
        events = agent.audit(limit=args.limit)
        if args.memory:
            events = [e for e in events if e.get("memory_id") == args.memory]
        print(json.dumps(events, indent=2))
        return 0

    if args.cmd == "remember":
        text = " ".join(args.text)
        print(json.dumps(agent.remember(text), indent=2))
        return 0

    # silence unused in type checkers
    _ = DEMO_QUESTIONS
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
