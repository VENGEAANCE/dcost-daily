#!/usr/bin/env bash
# Canonical publisher. Credentials come from the environment or Wrangler login.
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-python3}"
STAGE="$(mktemp -d "${TMPDIR:-/tmp}/dcost-release.XXXXXXXX")"
trap 'rm -rf -- "$STAGE"' EXIT
"$PYTHON" "$ROOT/scripts/prepare_release.py" --output "$STAGE" "$@"
SHA="$(git -C "$ROOT" rev-parse HEAD)"
export WRANGLER_SEND_METRICS=false
wrangler pages deploy "$STAGE" --project-name dcost-daily --branch main \
  --commit-hash "$SHA" --commit-message "Synchronized release $SHA; see /release.json" --commit-dirty=false
