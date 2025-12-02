#!/usr/bin/env bash
# Audit + lightweight pattern scan for all repos under GH_OWNER.
# Usage:
#   GH_OWNER=your-org ./scripts/audit_and_scan.sh [--shallow] [--no-clone]
# Requirements:
#   - gh (GitHub CLI) logged in (gh auth login or GH_TOKEN in env)
#   - jq
#   - git
#   - Optional: trufflehog (for deeper secret scans) in PATH
#
# Outputs to ./audit-output:
#   - inventory.json  (detailed per-repo JSON array)
#   - inventory.csv   (summary CSV)
#   - urgent-top20.json (top 20 prioritized repos and reasons)
#
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTDIR="$PWD/audit-output"
mkdir -p "$OUTDIR"
GH_OWNER="${GH_OWNER:-}"
if [ -z "$GH_OWNER" ]; then
  echo "Error: set GH_OWNER environment variable (e.g. GH_OWNER=HeavenzFire)"
  exit 2
fi
CLONE_REPOS=true
SHALLOW=true
NO_CLONE=false
# Parse args
for arg in "$@"; do
  case "$arg" in
    --no-clone) NO_CLONE=true; shift ;;
    --shallow) SHALLOW=true; shift ;;
    --deep) SHALLOW=false; shift ;;
    -h|--help) echo "Usage: GH_OWNER=owner $0 [--no-clone] [--shallow|--deep]"; exit 0;;
  esac
done
if [ "$NO_CLONE" = true ]; then CLONE_REPOS=false; fi

echo "Starting audit for owner: $GH_OWNER"
echo "Output directory: $OUTDIR"
echo

# Helper: list repos (org or user)
list_repos() {
  if gh api --paginate "orgs/$GH_OWNER/repos?per_page=100" >/dev/null 2>&1; then
    gh api --paginate "orgs/$GH_OWNER/repos?per_page=100"
  else
    gh api --paginate "users/$GH_OWNER/repos?per_page=100"
  fi
}

repos_json=$(list_repos)

# Patterns to flag (editable)
declare -a PATTERNS=(
  'AWS_ACCESS_KEY_ID'
  'AWS_SECRET_ACCESS_KEY'
  'PRIVATE_KEY'
  '-----BEGIN PRIVATE KEY-----'
  '-----BEGIN RSA PRIVATE KEY-----'
  'api_key'
  'API_KEY'
  'password'
  'passwd'
  'eval('
  'base64_decode('
  'child (abuse|porn|explo)'
  'sex' # keep broad; flagged for human review
)

# Per-repo processing
tmpfile="$(mktemp)"
echo "[" > "$OUTDIR/inventory.json"
first=true

echo "Scanning $(echo "$repos_json" | jq 'length') repositories..."

echo "repo,owner,visibility,archived,default_branch,has_readme,has_license,has_codeowners,has_dependabot,yaml_workflows,last_commit_iso,open_issues,open_prs,topics,score" > "$OUTDIR/inventory.csv"

echo "$repos_json" | jq -r '.[] | @base64' | while read -r repo64; do
  repo=$(echo "$repo64" | base64 --decode | jq -r '.name')
  visibility=$(echo "$repo64" | base64 --decode | jq -r '.visibility // "public"')
  archived=$(echo "$repo64" | base64 --decode | jq -r '.archived')
  default_branch=$(echo "$repo64" | base64 --decode | jq -r '.default_branch // ""')
  description=$(echo "$repo64" | base64 --decode | jq -r '.description // ""' | sed 's/"/\"/g')

  # Checks
  has_readme=$(gh api repos/"$GH_OWNER"/"$repo"/readme --silent >/dev/null 2>&1 && echo true || echo false)
  has_license=$(gh api repos/"$GH_OWNER"/"$repo"/license --silent >/dev/null 2>&1 && echo true || echo false)
  has_codeowners=$(gh api repos/"$GH_OWNER"/"$repo"/contents/.github/CODEOWNERS --silent >/dev/null 2>&1 && echo true || echo false)
  has_dependabot=$(gh api repos/"$GH_OWNER"/"$repo"/contents/.github/dependabot.yml --silent >/dev/null 2>&1 && echo true || echo false)
  yaml_workflows=$(gh api repos/"$GH_OWNER"/"$repo"/actions/workflows --silent 2>/dev/null | jq -r '.workflows | length // 0' 2>/dev/null || echo 0)
  last_commit_iso=$(gh api repos/"$GH_OWNER"/"$repo"/commits --jq '.[0].commit.author.date' --silent 2>/dev/null || echo "")
  open_issues=$(gh api repos/"$GH_OWNER"/"$repo" --jq '.open_issues_count' --silent 2>/dev/null || echo "0")
  open_prs=$(gh api search/issues -f q="repo:$GH_OWNER/$repo is:open is:pr" --jq '.total_count' --silent 2>/dev/null || echo "0")
  topics=$(gh api repos/"$GH_OWNER"/"$repo"/topics -H "Accept: application/vnd.github.mercy-preview+json" --silent 2>/dev/null | jq -r '.names | join(";")' 2>/dev/null || echo "")

  # Score heuristic (simple)
  score=0
  if [ -n "$last_commit_iso" ]; then
    if date -d "$last_commit_iso" >/dev/null 2>&1; then
      last_ts=$(date -d "$last_commit_iso" +%s)
    else
      last_ts=0
    fi
    now_ts=$(date +%s)
    days=$(( (now_ts - last_ts) / 86400 ))
    if [ "$days" -lt 7 ]; then score=$((score+5))
    elif [ "$days" -lt 30 ]; then score=$((score+4))
    elif [ "$days" -lt 90 ]; then score=$((score+3))
    elif [ "$days" -lt 365 ]; then score=$((score+1)); fi
  fi
  if [ "$open_prs" -gt 5 ] || [ "$open_issues" -gt 50 ]; then score=$((score+0)); else score=$((score+2)); fi
  if [ "$has_dependabot" = "true" ]; then score=$((score+2)); fi

  # Prepare repo directory if cloning
  workdir="$OUTDIR/repos/$repo"
  rm -rf "$workdir"
  mkdir -p "$workdir"

  # Clone (shallow) to run pattern scans if allowed
  findings_json="[]"
  findings_summary=""
  if [ "$CLONE_REPOS" = true ] && [ "$NO_CLONE" = false ]; then
    set +e
    if [ "$SHALLOW" = true ]; then
      git -c advice.detachedHead=false clone --depth 1 "https://github.com/$GH_OWNER/$repo.git" "$workdir" >/dev/null 2>&1
      rc=$?
      # For private repos, try using gh git clone if https failed
      if [ $rc -ne 0 ]; then
        if command -v gh >/dev/null 2>&1; then
          gh repo clone "$GH_OWNER/$repo" "$workdir" >/dev/null 2>&1 || true
        fi
      fi
    else
      gh repo clone "$GH_OWNER/$repo" "$workdir" -- --depth=1 >/dev/null 2>&1 || true
    fi
    set -e

    # Run basic grep-based pattern scans (fast)
    declare -a FND=()
    for p in "${PATTERNS[@]}"; do
      # use grep -I (ignore binary), -R -n --exclude-dir=.git
      out=$(grep -I -nR --exclude-dir=.git -E "$p" "$workdir" 2>/dev/null || true)
      if [ -n "$out" ]; then
        FND+=("{\"pattern\":\"$p\",\"matches\":$(echo "$out" | wc -l)}")
      fi
    done

    # Optional: trufflehog (if installed) for deep secret detection
    if command -v trufflehog >/dev/null 2>&1; then
      set +e
      th_out=$(trufflehog filesystem --json "$workdir" 2>/dev/null || true)
      set -e
      if [ -n "$th_out" ]; then
        # compact to a simple count (the detailed trufflehog output will be available in artifacts)
        th_count=$(echo "$th_out" | jq -r '. | length' 2>/dev/null || echo 0)
        if [ "$th_count" -gt 0 ]; then
          FND+=("{\"pattern\":\"trufflehog\",\"matches\":$th_count}")
        fi
        # Save raw trufflehog output
        echo "$th_out" > "$workdir/trufflehog.json"
      fi
    fi

    if [ ${#FND[@]} -gt 0 ]; then
      findings_json=$(printf '[%s]' "$(IFS=,; echo "${FND[*]}")")
      findings_summary=$(printf "%s" "$(IFS=,; echo "${FND[*]}")")
    fi
  fi

  # Build repo JSON object
  repo_obj=$(jq -n \
    --arg name "$repo" --arg owner "$GH_OWNER" --arg visibility "$visibility" \
    --arg archived "$archived" --arg default_branch "$default_branch" --arg description "$description" \
    --arg last_commit_iso "$last_commit_iso" --arg open_issues "$open_issues" --arg open_prs "$open_prs" \
    --arg has_readme "$has_readme" --arg has_license "$has_license" --arg has_codeowners "$has_codeowners" \
    --arg has_dependabot "$has_dependabot" --arg yaml_workflows "$yaml_workflows" --arg topics "$topics" \
    --argjson score "$score" \
    --argjson findings "$(jq -c -n "$findings_json")" \
    '{
      name: $name,
      owner: $owner,
      visibility: $visibility,
      archived: ($archived == "true"),
      default_branch: $default_branch,
      description: $description,
      last_commit_iso: $last_commit_iso,
      open_issues: ($open_issues | tonumber),
      open_prs: ($open_prs | tonumber),
      has_readme: ($has_readme == "true"),
      has_license: ($has_license == "true"),
      has_codeowners: ($has_codeowners == "true"),
      has_dependabot: ($has_dependabot == "true"),
      yaml_workflows: ($yaml_workflows | tonumber),
      topics: ($topics | split(\";\") | map(select(. != \"\"))),
      score: $score,
      findings: $findings
    }')

  # Append to inventory.json
  if [ "$first" = true ]; then
    first=false
    echo "$repo_obj" >> "$OUTDIR/inventory.json"
  else
    echo "," >> "$OUTDIR/inventory.json"
    echo "$repo_obj" >> "$OUTDIR/inventory.json"
  fi

  # CSV row (topics quoted)
  topics_safe=$(printf '%s' "$topics" | sed 's/"/""/g')
  printf '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"%s",%s\n' \
    "$repo" "$GH_OWNER" "$visibility" "$archived" "$default_branch" "$has_readme" "$has_license" "$has_codeowners" "$has_dependabot" \
    "$yaml_workflows" "$last_commit_iso" "$open_issues" "$open_prs" "$topics_safe" "$score" >> "$OUTDIR/inventory.csv"

  echo "Processed: $repo (score=$score) $( [ -n "$findings_summary" ] && echo '⚠ findings' || echo '')"
done

# close JSON array
echo "]" >> "$OUTDIR/inventory.json"

# Generate urgent top-20: sort by score descending, then include those with findings first
jq -r '
  . as $arr |
  ($arr | map(.score = (.score|tonumber)) | sort_by(-.score)) as $sorted |
  ($sorted | map(select(.findings | length > 0))) as $with_findings |
  ($sorted | map(select(.findings | length == 0))) as $without_findings |
  ($with_findings + $without_findings)[:20]
' "$OUTDIR/inventory.json" > "$OUTDIR/urgent-top20.json"

echo
echo "Audit complete."
echo "Artifacts:"
echo " - $OUTDIR/inventory.json"
echo " - $OUTDIR/inventory.csv"
echo " - $OUTDIR/urgent-top20.json"
echo
echo "Next recommended actions:"
echo " - Inspect urgent-top20.json and prioritize human review for repos with findings."
echo " - For any repo with 'trufflehog' findings, secure secrets immediately (rotate keys) and consult legal/IR."
echo " - For low-risk fixes (missing README/LICENSE/CODEOWNERS), create automated PRs from a bot account."
echo
echo "If you want, paste the urgent-top20.json contents here and I will produce per-repo remediation playbooks (PR content, issue templates, and exact commands)."