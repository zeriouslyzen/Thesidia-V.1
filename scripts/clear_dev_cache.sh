#!/bin/bash
# Clear development cache files safely

echo "=== Clearing Development Cache ==="
echo ""

# Python cache directories
echo "Clearing Python cache (__pycache__)..."
find . -type d -name "__pycache__" ! -path "*/venv/*" ! -path "*/node_modules/*" -exec rm -rf {} + 2>/dev/null
echo "✓ Python cache cleared"

# Python compiled files
echo "Clearing .pyc files..."
find . -type f -name "*.pyc" ! -path "*/venv/*" ! -path "*/node_modules/*" -delete 2>/dev/null
find . -type f -name "*.pyo" ! -path "*/venv/*" ! -path "*/node_modules/*" -delete 2>/dev/null
echo "✓ Compiled Python files cleared"

# Pytest cache
if [ -d ".pytest_cache" ]; then
    echo "Clearing pytest cache..."
    rm -rf .pytest_cache
    echo "✓ Pytest cache cleared"
fi

# Mypy cache
if [ -d ".mypy_cache" ]; then
    echo "Clearing mypy cache..."
    rm -rf .mypy_cache
    echo "✓ Mypy cache cleared"
fi

# .cache directories (excluding venv)
echo "Clearing .cache directories..."
find . -type d -name ".cache" ! -path "*/venv/*" ! -path "*/node_modules/*" -exec rm -rf {} + 2>/dev/null
echo "✓ .cache directories cleared"

# .DS_Store files (macOS)
echo "Clearing .DS_Store files..."
find . -type f -name ".DS_Store" ! -path "*/venv/*" ! -path "*/node_modules/*" -delete 2>/dev/null
echo "✓ .DS_Store files cleared"

# Temporary files
echo "Clearing temporary files..."
find . -type f -name "*.tmp" ! -path "*/venv/*" ! -path "*/node_modules/*" -delete 2>/dev/null
find . -type f -name "*.swp" ! -path "*/venv/*" ! -path "*/node_modules/*" -delete 2>/dev/null
find . -type f -name "*.swo" ! -path "*/venv/*" ! -path "*/node_modules/*" -delete 2>/dev/null
find . -type f -name "*~" ! -path "*/venv/*" ! -path "*/node_modules/*" -delete 2>/dev/null
echo "✓ Temporary files cleared"

# Log files (optional - uncomment if you want to clear logs)
# echo "Clearing log files..."
# find . -type f -name "*.log" ! -path "*/venv/*" ! -path "*/node_modules/*" ! -name "genesis_test_run.log" -delete 2>/dev/null
# echo "✓ Log files cleared"

echo ""
echo "=== Cache Clear Complete ==="
echo ""
echo "Note: venv/ and node_modules/ were excluded from cleanup"
echo "Note: Log files were NOT cleared (uncomment in script if needed)"

