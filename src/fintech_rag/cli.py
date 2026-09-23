"""CLI entry point: python -m fintech_rag.cli <ingest|ask|eval> ..."""
from __future__ import annotations

import argparse

from .ingest import run_ingest
from .rag import ask


def main() -> None:
    parser = argparse.ArgumentParser(prog="fintech-rag")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("ingest", help="Chunk + embed data/docs/*.md into the vector store")

    ask_parser = sub.add_parser("ask", help="Ask a single question against the index")
    ask_parser.add_argument("question")

    sub.add_parser("eval", help="Run the eval set and write results/eval_report.md")

    args = parser.parse_args()

    if args.command == "ingest":
        run_ingest()
    elif args.command == "ask":
        result = ask(args.question)
        print(result.answer)
        if result.sources:
            print("\nZdroje:", ", ".join(result.sources))
    elif args.command == "eval":
        from fintech_eval.evaluate import run_evaluation

        run_evaluation()


if __name__ == "__main__":
    main()
