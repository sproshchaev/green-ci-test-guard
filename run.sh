#!/usr/bin/env bash
# Rebuilds everything from scratch and compares the summary with expected.txt.
# Exit code 1 if anything differs.
#
#   ./run.sh                    # full check, about a minute and a half on 8 cores
#   cat target/results.txt      # one line per answer after the run
set -euo pipefail
cd "$(dirname "$0")"

# prompts/ must be exactly what the scenarios produce
python3 tools/make_prompts.py check

# both scenarios start red, otherwise there is nothing to repair
for app in app app-conflict; do
  if (cd "$app" && mvn -q -B test > /dev/null 2>&1); then
    echo "$app: expected red build, got green" >&2
    exit 1
  fi
done

mkdir -p target
python3 tools/evaluate.py | tee target/summary.txt

if diff -u expected.txt target/summary.txt; then
  echo "OK: summary matches expected.txt"
else
  echo "FAIL: summary differs from expected.txt" >&2
  exit 1
fi
