#!/usr/bin/env bash
set -euo pipefail

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  Content Intelligence — VM Init Script                   ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# --- 1. Azure CLI ---
echo "[1/4] Installing Azure CLI..."
if command -v az &>/dev/null; then
    echo "  -> Already installed: $(az --version 2>&1 | head -1)"
else
    curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
    echo "  -> Done: $(az --version 2>&1 | head -1)"
fi

# --- 2. uv (Python package manager) ---
echo ""
echo "[2/4] Installing uv..."
if command -v uv &>/dev/null; then
    echo "  -> Already installed: $(uv --version)"
else
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "  -> Done."
fi
export PATH="$HOME/.local/bin:$PATH"

# Persist PATH for future shell sessions
if ! grep -q '.local/bin' "$HOME/.bashrc" 2>/dev/null; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    echo "  -> Added ~/.local/bin to ~/.bashrc"
fi
echo "  -> uv version: $(uv --version)"

# --- 3. Python dependencies ---
echo ""
echo "[3/4] Installing Python dependencies..."
cd "$(dirname "$0")/app"
uv sync
echo "  -> Done."

# --- 4. Environment file ---
echo ""
echo "[4/4] Checking .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "  -> Created .env from .env.example. Please review and update endpoints."
else
    echo "  -> .env already exists. Skipping."
fi

echo ""
echo "=== Setup complete ==="
echo ""
echo "Next steps:"
echo "  1. Ensure Managed Identity is configured (Cognitive Services User + Storage Blob Data Reader)"
echo "  2. Review app/.env and update endpoints if needed"
echo "  3. Run the web app:  cd app && uv run python main.py web"
echo ""
