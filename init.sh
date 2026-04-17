#!/usr/bin/env bash
set -euo pipefail

echo "=== Installing uv (Python package manager) ==="
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
uv --version

echo ""
echo "[1/4] Installing GitHub Copilot CLI..."
npm install -g @github/copilot
echo "  -> Done."

echo ""
echo "=== Installing Azure CLI ==="
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
az --version

echo ""
echo "=== All installations complete ==="
