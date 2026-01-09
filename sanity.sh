#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
PY="${PY:-python3}"

echo "== health =="
curl -s "$BASE_URL/health" | $PY -m json.tool

echo "== metrics (before) =="
curl -s "$BASE_URL/metrics" | $PY -m json.tool

echo "== positive test =="
curl -s -X POST "$BASE_URL/analyze" -H 'Content-Type: application/json' -d '{"text":"this is excellent and I love it"}' | $PY -m json.tool

echo "== mixed test =="
curl -s -X POST "$BASE_URL/analyze" -H 'Content-Type: application/json' -d '{"text":"I love this but it is awful"}' | $PY -m json.tool

echo "== negative test (should escalate) =="
curl -s -X POST "$BASE_URL/analyze" -H 'Content-Type: application/json' -d '{"text":"this is terrible"}' | $PY -m json.tool

echo "== metrics (after) =="
curl -s "$BASE_URL/metrics" | $PY -m json.tool

echo "✅ sanity tests complete"
