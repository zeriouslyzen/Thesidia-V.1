#!/bin/bash
# Comprehensive cleanup script for Thesidia Ice project
# Safely removes cache files while preserving all import files and virtual environments

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=== Thesidia Ice System Cleanup ==="
echo "Project: $PROJECT_ROOT"
echo ""

# Track space freed
SPACE_BEFORE=$(du -sh "$PROJECT_ROOT" 2>/dev/null | cut -f1)
echo "Space before cleanup: $SPACE_BEFORE"
echo ""

# 1. Python cache directories (excluding venv - these are needed for imports)
echo "[1/7] Clearing Python __pycache__ directories..."
CACHE_DIRS=$(find . -type d -name "__pycache__" ! -path "*/venv/*" ! -path "*/node_modules/*" 2>/dev/null | wc -l | tr -d ' ')
if [ "$CACHE_DIRS" -gt 0 ]; then
    find . -type d -name "__pycache__" ! -path "*/venv/*" ! -path "*/node_modules/*" -exec rm -rf {} + 2>/dev/null
    echo "  ✓ Removed $CACHE_DIRS __pycache__ directories"
else
    echo "  ✓ No cache directories found"
fi

# 2. Python compiled files (excluding venv)
echo "[2/7] Clearing .pyc and .pyo files..."
PYC_FILES=$(find . -type f \( -name "*.pyc" -o -name "*.pyo" \) ! -path "*/venv/*" ! -path "*/node_modules/*" 2>/dev/null | wc -l | tr -d ' ')
if [ "$PYC_FILES" -gt 0 ]; then
    find . -type f \( -name "*.pyc" -o -name "*.pyo" \) ! -path "*/venv/*" ! -path "*/node_modules/*" -delete 2>/dev/null
    echo "  ✓ Removed $PYC_FILES compiled Python files"
else
    echo "  ✓ No compiled files found"
fi

# 3. Pytest cache
echo "[3/7] Clearing pytest cache..."
if [ -d ".pytest_cache" ]; then
    rm -rf .pytest_cache
    echo "  ✓ Pytest cache cleared"
else
    echo "  ✓ No pytest cache found"
fi

# 4. Mypy cache
echo "[4/7] Clearing mypy cache..."
if [ -d ".mypy_cache" ]; then
    rm -rf .mypy_cache
    echo "  ✓ Mypy cache cleared"
else
    echo "  ✓ No mypy cache found"
fi

# 5. .cache directories (excluding venv)
echo "[5/7] Clearing .cache directories..."
CACHE_DIRS=$(find . -type d -name ".cache" ! -path "*/venv/*" ! -path "*/node_modules/*" 2>/dev/null | wc -l | tr -d ' ')
if [ "$CACHE_DIRS" -gt 0 ]; then
    find . -type d -name ".cache" ! -path "*/venv/*" ! -path "*/node_modules/*" -exec rm -rf {} + 2>/dev/null
    echo "  ✓ Removed $CACHE_DIRS .cache directories"
else
    echo "  ✓ No .cache directories found"
fi

# 6. macOS system files
echo "[6/7] Clearing .DS_Store files..."
DS_FILES=$(find . -type f -name ".DS_Store" ! -path "*/venv/*" ! -path "*/node_modules/*" 2>/dev/null | wc -l | tr -d ' ')
if [ "$DS_FILES" -gt 0 ]; then
    find . -type f -name ".DS_Store" ! -path "*/venv/*" ! -path "*/node_modules/*" -delete 2>/dev/null
    echo "  ✓ Removed $DS_FILES .DS_Store files"
else
    echo "  ✓ No .DS_Store files found"
fi

# 7. Temporary files
echo "[7/7] Clearing temporary files..."
TMP_FILES=$(find . -type f \( -name "*.tmp" -o -name "*.swp" -o -name "*.swo" -o -name "*~" \) ! -path "*/venv/*" ! -path "*/node_modules/*" 2>/dev/null | wc -l | tr -d ' ')
if [ "$TMP_FILES" -gt 0 ]; then
    find . -type f \( -name "*.tmp" -o -name "*.swp" -o -name "*.swo" -o -name "*~" \) ! -path "*/venv/*" ! -path "*/node_modules/*" -delete 2>/dev/null
    echo "  ✓ Removed $TMP_FILES temporary files"
else
    echo "  ✓ No temporary files found"
fi

# Calculate space after
SPACE_AFTER=$(du -sh "$PROJECT_ROOT" 2>/dev/null | cut -f1)

echo ""
echo "=== Cleanup Complete ==="
echo "Space before: $SPACE_BEFORE"
echo "Space after:  $SPACE_AFTER"
echo ""
echo "PRESERVED:"
echo "  ✓ All virtual environments (venv/, webapp/venv/)"
echo "  ✓ All Python source files (.py)"
echo "  ✓ All import modules and packages"
echo "  ✓ All data files and configurations"
echo "  ✓ All log files (preserved for debugging)"
echo ""
