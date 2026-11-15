#!/usr/bin/env bash
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
has_hybrid_flag=0
for arg in "$@"; do
  case "$arg" in
    --with-hybrid|--with-hybrid=*) has_hybrid_flag=1 ;;
  esac
done
if [[ "$has_hybrid_flag" -eq 0 ]]; then
  exec python3 "$REPO/scripts/harness.py" install --disable-mcp hybrid-sage "$@"
fi
exec python3 "$REPO/scripts/harness.py" install "$@"
