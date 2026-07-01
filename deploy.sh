#!/usr/bin/env bash
# Rebuild Lectern's data + static site and deploy to production
# (lectern.wrootpress.com, Vercel project "lectern" under wilson-pruitts-projects).
# Static-export deploy of web/out — no server build, fully self-contained.
set -euo pipefail
cd "$(dirname "$0")"

echo "==> 1/3  baking the per-occasion contract (data/build)"
python3.11 src/build_occasion.py --all

echo "==> 2/3  building the static site (web/out)"
cd web && pnpm build

echo "==> 3/3  deploying to production"
cd out
npx vercel link --yes --project lectern --scope wilson-pruitts-projects >/dev/null
# --archive=tgz: upload as one tarball (per-file upload aborts with the many /api files)
npx vercel deploy --prod --yes --archive=tgz

echo "==> done — https://lectern.wrootpress.com"
