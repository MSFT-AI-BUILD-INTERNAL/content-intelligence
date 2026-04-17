#!/usr/bin/env python3
"""
Azure AI Foundry — Content Understanding & Document Intelligence Sample

Integrates both services using Azure Managed Identity (no API keys).
Run: python main.py [content-understanding | document-intelligence | all]
"""

from __future__ import annotations

import sys


def _banner() -> None:
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  Azure AI Foundry — Content Intelligence Sample         ║")
    print("║  Auth: Managed Identity (DefaultAzureCredential)        ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()


def run_content_understanding() -> None:
    from content_understanding_sample import main as cu_main
    cu_main()


def run_document_intelligence() -> None:
    from document_intelligence_sample import main as di_main
    di_main()


def main() -> None:
    _banner()

    commands = {
        "content-understanding": run_content_understanding,
        "document-intelligence": run_document_intelligence,
        "all": lambda: (run_content_understanding(), print(), run_document_intelligence()),
    }

    choice = sys.argv[1] if len(sys.argv) > 1 else "all"

    if choice in ("-h", "--help"):
        print("Usage: python main.py [content-understanding | document-intelligence | all]")
        print()
        print("  content-understanding   Run Content Understanding samples only")
        print("  document-intelligence   Run Document Intelligence samples only")
        print("  all                     Run both (default)")
        return

    runner = commands.get(choice)
    if not runner:
        print(f"Unknown command: {choice}")
        print(f"Valid options: {', '.join(commands)}")
        sys.exit(1)

    runner()


if __name__ == "__main__":
    main()
