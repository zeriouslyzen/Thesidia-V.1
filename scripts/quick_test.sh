#!/bin/bash
# Quick test - run a single category or all tests

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

CATEGORY="${1:-all}"
MODEL="${2:-clean-mistral:latest}"

echo "Running $CATEGORY tests with model: $MODEL"
echo ""

cd "$PROJECT_ROOT"
python3 scripts/test_thesidia_comprehensive.py --model "$MODEL" --category "$CATEGORY"

