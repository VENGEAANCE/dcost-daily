#!/usr/bin/env bash
# Deploy dcostdaily.com: stage everything except SETUP.md, scripts/, .wrangler/, then wrangler pages deploy.
set -euo pipefail
SRC=/workspace/dcost-daily; STAGE=/workspace/dcost-daily-stage
rm -rf "$STAGE"; mkdir -p "$STAGE"
cp -a "$SRC"/. "$STAGE"/ && rm -rf "$STAGE/SETUP.md" "$STAGE/scripts" "$STAGE/.wrangler" && find "$STAGE" -maxdepth 1 -name "*.md" -delete  # private notes (e.g. affiliate answers) never ship
export PATH=/workspace/tools/node22/bin:/workspace/tools/node_modules/.bin:$PATH
export WRANGLER_CACHE_DIR=/workspace/.wrangler-cache WRANGLER_SEND_METRICS=false
export CLOUDFLARE_API_TOKEN="$(cat /home/box/.secrets/cloudflare_token)"
cd "$STAGE" && wrangler pages deploy "$STAGE" --project-name dcost-daily --branch main --commit-dirty=true
