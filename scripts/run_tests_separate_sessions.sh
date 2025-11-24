#!/bin/bash
# Run Thesidia tests in separate sessions to avoid strain

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=================================================================================="
echo "THESIDIA TESTING - SEPARATE SESSIONS"
echo "=================================================================================="
echo ""

# Test categories
CATEGORIES=("accuracy" "meditation" "chi_gong" "mind_body" "wellness" "stress")

# Model to use
MODEL="${1:-clean-mistral:latest}"

echo "Model: $MODEL"
echo "Running tests in separate sessions to avoid strain..."
echo ""

# Create results directory
RESULTS_DIR="$PROJECT_ROOT/analysis_output/test_sessions"
mkdir -p "$RESULTS_DIR"

# Run each category in a separate session
for category in "${CATEGORIES[@]}"; do
    echo "=================================================================================="
    echo "Running $category tests..."
    echo "=================================================================================="
    echo ""
    
    cd "$PROJECT_ROOT"
    python3 scripts/test_thesidia_comprehensive.py --model "$MODEL" --category "$category"
    
    # Wait between sessions
    if [ "$category" != "stress" ]; then
        echo ""
        echo "⏸️  Waiting 10 seconds before next session..."
        sleep 10
    else
        echo ""
        echo "⏸️  Waiting 30 seconds after stress tests..."
        sleep 30
    fi
    
    echo ""
done

echo "=================================================================================="
echo "✅ ALL TESTS COMPLETE"
echo "=================================================================================="
echo ""
echo "Results saved to: $RESULTS_DIR"
echo ""

