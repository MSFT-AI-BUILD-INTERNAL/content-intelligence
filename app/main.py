#!/usr/bin/env python3
"""
Azure AI Foundry — Content Understanding & Document Intelligence Sample

Integrates both services using Azure Managed Identity (no API keys).
Run: python main.py [web | content-understanding | document-intelligence | all]
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
    from samples.content_understanding import main as cu_main
    print("[NOTE] content-understanding now uses Document Intelligence service")
    cu_main()


def run_document_intelligence() -> None:
    from samples.document_intelligence import main as di_main
    di_main()


def run_web() -> None:
    import uvicorn
    print("Starting web server at http://0.0.0.0:8000 ...")
    uvicorn.run("web.app:app", host="0.0.0.0", port=8000, reload=True)


def main() -> None:
    _banner()

    commands = {
        "web": run_web,
        "content-understanding": run_content_understanding,
        "document-intelligence": run_document_intelligence,
        "all": lambda: (run_content_understanding(), print(), run_document_intelligence()),
    }

    choice = sys.argv[1] if len(sys.argv) > 1 else "web"

    if choice in ("-h", "--help"):
        print("Usage: python main.py [web | content-understanding | document-intelligence | all]")
        print()
        print("  web                     Start the web application (default)")
        print("  content-understanding   Run Content Understanding samples only")
        print("  document-intelligence   Run Document Intelligence samples only")
        print("  all                     Run both CLI samples")
        return

    runner = commands.get(choice)
    if not runner:
        print(f"Unknown command: {choice}")
        print(f"Valid options: {', '.join(commands)}")
        sys.exit(1)

    runner()


if __name__ == "__main__":
    main()
