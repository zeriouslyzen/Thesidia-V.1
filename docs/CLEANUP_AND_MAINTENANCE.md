# Cleanup and Maintenance Guide

## System Cleanup

### Automated Cleanup Script

Run the comprehensive cleanup script to safely remove cache files while preserving all Thesidia imports and virtual environments:

```bash
./scripts/cleanup_system.sh
```

This script removes:
- Python `__pycache__` directories (excluding venv)
- Compiled `.pyc` and `.pyo` files (excluding venv)
- Pytest and Mypy cache directories
- `.cache` directories (excluding venv)
- macOS `.DS_Store` files
- Temporary files (`.tmp`, `.swp`, `.swo`, `*~`)

**Preserved:**
- All virtual environments (`venv/`, `webapp/venv/`)
- All Python source files and imports
- All data files and configurations
- All log files

### Manual Cache Cleanup

For development cache only (preserves venv):

```bash
./scripts/clear_dev_cache.sh
```

## Virtual Environment Management

### Virtual Environment Structure

The project uses two virtual environments:

1. **Main `venv/`** (420MB)
   - Location: Project root
   - Used by: `start_server.sh`, root-level scripts
   - Requirements: `requirements.txt` (root)
   - Last updated: November 18, 2024

2. **Webapp `webapp/venv/`** (577MB)
   - Location: `webapp/` directory
   - Used by: `webapp/start.sh`, `webapp/dev-server.sh`
   - Requirements: `webapp/requirements.txt`
   - Last updated: November 15, 2024

### Why Two Virtual Environments?

- **Main venv**: Used for root-level scripts and API server
- **Webapp venv**: Used for webapp-specific dependencies (includes MLX, transformers, etc.)

Both are needed because:
- Webapp imports from `src/` (project root)
- Different dependency sets (webapp has MLX/transformers, main has basic Flask)
- Scripts activate the appropriate venv based on context

### Recreating Virtual Environments

If you need to recreate a virtual environment:

**Main venv:**
```bash
cd "/Users/deshonjackson/thesidia ice"
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Webapp venv:**
```bash
cd "/Users/deshonjackson/thesidia ice/webapp"
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r ../requirements.txt  # Also install main requirements
```

## Process Management

### Checking Running Processes

**Python processes:**
```bash
ps aux | grep python | grep -v grep
```

**Port usage:**
```bash
lsof -i -P -n | grep LISTEN
```

### Stopping Thesidia Servers

**Using management script:**
```bash
./scripts/manage_server.sh stop
```

**Manual stop:**
```bash
pkill -f "python.*server.py"
```

**Stop by port:**
```bash
lsof -ti:5000 | xargs kill -9  # Main server port
```

### Long-Running HTTP Servers

If you see generic `python3 -m http.server` processes running:
- These are not Thesidia servers
- They're simple file servers (often left running from testing)
- Safe to stop: `kill <PID>`

## Storage Analysis

### Project Directory Sizes

- `webapp/`: 719MB
  - `webapp/venv/`: 577MB
  - `webapp/assets/videos/`: 137MB
- `venv/`: 420MB
- `data/`: 43MB
- `analysis_output/`: 17MB

### Cache Locations

**Project cache:**
- Python cache: `__pycache__/` directories (~9MB total)
- Virtual environments: `venv/` and `webapp/venv/` (~997MB total)

**System cache (Mac):**
- pip cache: `~/Library/Caches/pip` (~1.1GB)
- Playwright: `~/Library/Caches/ms-playwright` (~1.0GB)
- Cursor: `~/Library/Caches/Cursor` (~142MB)

### Cleaning System Cache

**pip cache:**
```bash
pip cache purge
```

**Playwright cache:**
```bash
# Only if not using Playwright
rm -rf ~/Library/Caches/ms-playwright
```

## Log File Management

Log files are preserved by default. To clean logs:

```bash
# Review log sizes first
du -sh logs/*.log webapp/*.log

# Archive old logs (optional)
mkdir -p logs/archive
mv logs/*.log logs/archive/ 2>/dev/null || true
```

## Maintenance Schedule

**Weekly:**
- Run `./scripts/cleanup_system.sh`
- Check for long-running processes
- Review log file sizes

**Monthly:**
- Review virtual environment sizes
- Update dependencies: `pip install --upgrade -r requirements.txt`
- Clean system cache if needed

**As needed:**
- Recreate virtual environments if corrupted
- Clean large log files
- Archive old data files
