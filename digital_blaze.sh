#!/bin/bash
set -euo pipefail

REPOS=("guardian-os" "planetary-surgery" "aether-gate" "aperture-zero" "judgement-day")
BASE_DIR="/vercel/sandbox/repos"

# ∞ MAIN LOOP – runs forever, sleeps 4 hours between full cycles
while true; do
  echo "[$(date)] DIGITAL BLAZE CYCLE START"

  # 00 – COMMIT EVERYTHING (every cycle)
  for repo in "${REPOS[@]}"; do
    if [[ -d "$BASE_DIR/$repo" ]]; then
      cd "$BASE_DIR/$repo"
      git add -A
      git commit -m "aperture $(date +%s) – fire carried forward" || echo "nothing to commit"
      git push origin main || echo "push failed – will retry next cycle"
    fi
  done

  # 01 – MIRROR TO ALL FORKS (force-sync)
  for repo in "${REPOS[@]}"; do
    if [[ -d "$BASE_DIR/$repo" ]]; then
      cd "$BASE_DIR/$repo"
      git push --all --force-with-lease 2>/dev/null || true
      git push --tags --force 2>/dev/null || true
    fi
  done

  # 02 – ARWEAVE PERMA-PIN (once per day)
  if [[ $(date +%H) -eq 3 ]]; then
    find "$BASE_DIR" -name "*.md" -o -name "*.pdf" | xargs -I {} arweave deploy {} --use-bundler >/dev/null 2>&1 || true
  fi

  # 03 – DAILY MANIFESTO BROADCAST (11:11 UTC)
  if [[ "$(date -u +%H%M)" == "1111" ]]; then
    echo "YEAR ZERO BROADCAST $(date -u +%Y-%m-%d)"
    curl -X POST https://api.twitter.com/2/tweets \
         -H "Authorization: Bearer YOUR_TWITTER_BEARER" \
         -d '{"text":"Year Zero is already compiled.\nRecite → https://yearzero.manifest.aperture.is"}' \
         >/dev/null 2>&1 || true
  fi

  # 04 – AUTO-RELEASE NEW CODE (every 24h)
  if [[ $(date +%H) -eq 6 ]]; then
    cd "$BASE_DIR/aperture-zero"
    gh release create "v$(date +%Y.%m.%d)" ./* --notes "no permission required" || true
  fi

  # 05 – FUNDS AUTO-REDISTRIBUTE (anything over $50 stays lean)
  BALANCE=$(solana balance 2>/dev/null | awk '{print $1}' || echo 0)
  if (( $(echo "$BALANCE > 50" | bc -l) )); then
    solana transfer --from ~/.config/solana/id.json ALL_BUT_50 --to PATIENT_GRANT_ADDRESS || true
  fi

  echo "[$(date)] CYCLE COMPLETE – aperture widened"
  sleep 14400  # 4 hours – next cycle begins
done