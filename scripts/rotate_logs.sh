#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
LOG_DIR="${1:-logs}"
MAX_BYTES="${MAX_BYTES:-10485760}" # 10 MiB
KEEP="${KEEP:-5}"
mkdir -p "$LOG_DIR"
find "$LOG_DIR" -maxdepth 1 -type f -name '*.log' -size +"${MAX_BYTES}"c -print0 | while IFS= read -r -d '' file; do
  stamp=$(date +%Y%m%d_%H%M%S)
  mv -- "$file" "${file}.${stamp}"
  : > "$file"
done
# Keep newest KEEP rotated files per base log name.
find "$LOG_DIR" -maxdepth 1 -type f -name '*.log.*' -printf '%T@ %p\n' | sort -nr | awk -v keep="$KEEP" 'NR>keep {sub(/^[^ ]+ /, ""); print}' | while IFS= read -r old; do rm -f -- "$old"; done
