# Supabase Setup Guide

## Phase 1: Initial Setup (Complete This First)

### 1. Create Supabase Project

1. Go to https://supabase.com/dashboard
2. Click "New Project"
3. Fill in:
   - **Name**: Thesidia Production (or your choice)
   - **Database Password**: Generate a strong password (save it!)
   - **Region**: Choose closest to your users
4. Click "Create new project"
5. Wait 2-3 minutes for setup to complete

### 2. Get API Keys

1. In your Supabase project dashboard, go to **Settings** → **API**
2. Copy these values:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public**: The `anon` key (safe for client-side)
   - **service_role**: The `service_role` key (⚠️ SECRET - never expose!)

### 3. Configure Environment

```bash
# 1. Copy the example file
cp .env.example .env

# 2. Edit .env and paste your keys
nano .env  # or use your editor

# 3. Verify .env is in .gitignore (already done ✓)
cat .gitignore | grep .env
```

### 4. Install Dependencies

```bash
# Install new Supabase dependencies
pip install -r requirements.txt

# Verify installation
python -c "import supabase; print('✅ Supabase client installed')"
python -c "from dotenv import load_dotenv; print('✅ python-dotenv installed')"
```

### 5. Test Connection (Optional)

```python
# test_supabase.py
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")

if not url or not key:
    print("❌ Environment variables not set!")
    exit(1)

try:
    supabase = create_client(url, key)
    print("✅ Supabase connection successful!")
    print(f"   Connected to: {url}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

Run test:
```bash
python test_supabase.py
```

---

## Next: Phase 2 - Database Schema

Once Phase 1 is complete, proceed to Phase 2:
1. Run the SQL schema from `supabase_readiness.md`
2. Test with sample data
3. Verify Row Level Security (RLS) policies

---

## Quick Reference

**Environment Variables**: `.env` (not committed to git)  
**Template**: `.env.example` (committed to git)  
**Supabase Dashboard**: https://supabase.com/dashboard  
**Documentation**: https://supabase.com/docs/reference/python/introduction

---

## Troubleshooting

**Error: "Module not found: supabase"**
```bash
pip install supabase python-dotenv
```

**Error: "SUPABASE_URL not set"**
```bash
# Check .env file exists and has correct values
cat .env | grep SUPABASE_URL
```

**Connection timeout**
- Check project is not paused in Supabase dashboard
- Verify URL is correct (includes `https://`)
- Check firewall/VPN settings
