#!/usr/bin/env bash
# Install the Python dependencies needed to build the PDFs.
# Safe to re-run. Handles a known cffi/cryptography import quirk in some
# container images by ensuring cffi is present before fpdf2 is imported.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pip install --quiet --upgrade cffi >/dev/null 2>&1 || true
python3 -m pip install --quiet -r tools/requirements.txt
echo "Dependencies installed. Build with: python3 tools/build_pdfs.py"
