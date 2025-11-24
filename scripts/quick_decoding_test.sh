#!/bin/bash
# Quick test of decoding configuration on a few questions

cd "$(dirname "$0")/.."

echo "Testing decoding configuration..."
echo "Configuration: Regular Mode (spacious), clean-mistral:latest"
echo ""

python3 scripts/test_decoding_config.py --limit 5

echo ""
echo "Test complete! Check analysis_output/decoding_tests/ for results."

