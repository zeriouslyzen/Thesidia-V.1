# Fixing Import Errors

## Error: ModuleNotFoundError: No module named 'ollama'

### Solution

The virtual environment needs all dependencies. Updated `requirements.txt` includes:
- flask>=3.0.0
- flask-cors>=4.0.0
- ollama>=0.1.0
- chromadb>=0.4.0
- requests>=2.31.0
- beautifulsoup4>=4.12.0
- lxml>=4.9.0

### To Fix

1. Delete the venv and recreate:
```bash
cd webapp
rm -rf venv
./start.sh
```

2. Or manually install:
```bash
cd webapp
source venv/bin/activate
pip install -r requirements.txt
pip install -r ../requirements.txt
```

### Updated Files

- `requirements.txt` - Added all Thesidia dependencies
- `start.sh` - Now installs main project requirements too
- `server.py` - Fixed path imports

### Test

After fixing, run:
```bash
cd webapp
./start.sh
```

Should start without errors on http://127.0.0.1:5000

