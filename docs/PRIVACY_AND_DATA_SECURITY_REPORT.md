# Privacy and Data Security Report
Generated: January 22, 2026

## Executive Summary

**Status**: Data is being sent to Supabase cloud service. Thesidia project is NOT syncing to iCloud. No biometric data collection detected.

## iCloud Sync Status

### Thesidia Project Location
- **Path**: `/Users/deshonjackson/thesidia ice`
- **iCloud Sync**: ❌ **NOT SYNCING**
- **Evidence**: No `@` extended attribute, no iCloud metadata
- **Status**: Project is stored locally only, not in iCloud Drive

### iCloud Drive Active Services
- iCloud Drive is running (system service)
- Desktop and Documents folders are synced to iCloud (standard macOS behavior)
- **Thesidia project is NOT in these synced locations**

## Cloud Data Transmission

### Supabase Cloud Service
**Status**: ⚠️ **ACTIVE AND SENDING DATA**

**Configuration Found**:
```
SUPABASE_URL=https://ksutnytaqspwdvqkeapk.supabase.co
USE_SUPABASE=true
```

**What Data is Being Sent**:
1. **Conversations**: All conversation messages and metadata
2. **User Interactions**: Event tracking data (clicks, navigation, etc.)
3. **User IDs**: Associated with conversations and interactions

**Storage Location**: PostgreSQL database on Supabase servers (cloud)

**Code Locations**:
- `webapp/conversations/supabase_storage.py` - Conversation storage
- `webapp/server.py` (line 648-655) - User interaction events
- `webapp/routes/events_routes.py` (line 59-64) - Event tracking

**Data Flow**:
```
Local Thesidia → Supabase Cloud Database
- Conversations (messages, titles, previews)
- User interactions (events, timestamps)
- User IDs (for conversation ownership)
```

### How to Disable Supabase Sync

**Option 1: Disable via Environment Variable**
```bash
cd "/Users/deshonjackson/thesidia ice"
# Edit .env file
# Change: USE_SUPABASE=true
# To: USE_SUPABASE=false
```

**Option 2: Remove Supabase Credentials**
```bash
# Comment out or remove Supabase lines in .env:
# SUPABASE_URL=...
# SUPABASE_ANON_KEY=...
# SUPABASE_SERVICE_KEY=...
```

**After disabling**: System will automatically fall back to local SQLite storage (`data/conversations.sqlite3`)

## Biometric Data

### Search Results
- ❌ **No biometric data collection found**
- ❌ **No TouchID/FaceID data storage**
- ❌ **No fingerprint data in Thesidia project**

### What Was Found
- Only **text mentions** of "biometric" in training datasets (conversation examples)
- These are fictional/conceptual references, not actual biometric data collection
- No code that collects or processes biometric data

### System-Level Biometric Data
- macOS stores biometric data in Secure Enclave (hardware-encrypted)
- Not accessible to applications
- Thesidia has no access to this data

## Network Connections

### Active External Connections (Non-Thesidia)
- **Cursor IDE**: Connecting to AWS/Cloudflare (for IDE features)
- **Spotify**: Music streaming service
- **System Services**: iCloud, identity services (local network)

### Thesidia-Related Connections
- **Supabase**: HTTPS connections to `ksutnytaqspwdvqkeapk.supabase.co` (when active)
- **Ollama**: Local only (`127.0.0.1:11434`)
- **No other external connections** from Thesidia code

## Data Storage Locations

### Local Storage (Private)
```
/Users/deshonjackson/thesidia ice/data/
├── conversations.sqlite3    # Local conversations (if Supabase disabled)
├── users/                    # User profiles (local JSON files)
├── kim/                      # KIM messages (encrypted, local)
├── uploads/                  # User-uploaded files (local)
└── ...                       # All other data (local)
```

### Cloud Storage (Supabase)
- PostgreSQL database on Supabase servers
- Conversations table
- Messages table
- User interactions table

## Privacy Recommendations

### If You Want Complete Local-Only Storage

1. **Disable Supabase**:
   ```bash
   # Edit .env file
   USE_SUPABASE=false
   ```

2. **Verify Local Storage**:
   ```bash
   # Check that conversations.sqlite3 is being used
   ls -lh data/conversations.sqlite3
   ```

3. **Monitor Network Traffic** (optional):
   ```bash
   # Check for Supabase connections
   lsof -i -P -n | grep supabase
   ```

### If You Want to Keep Supabase

- Data is encrypted in transit (HTTPS)
- Supabase uses Row Level Security (RLS)
- Your service key is stored in `.env` (keep this file secure)
- Consider reviewing Supabase privacy policy

## Security Checklist

- ✅ Thesidia project NOT in iCloud Drive
- ✅ No biometric data collection
- ⚠️ Supabase cloud sync is ACTIVE
- ✅ Local data stored in `data/` directory
- ✅ No other cloud services detected
- ✅ Ollama runs locally only
- ⚠️ `.env` file contains Supabase credentials (keep secure)

## Action Items

1. **Decide on Supabase**: Keep cloud sync or disable for local-only?
2. **Secure .env file**: Ensure `.env` is in `.gitignore` (already is)
3. **Review Supabase data**: Check what's stored in your Supabase dashboard
4. **Monitor connections**: Periodically check network connections

## How to Check Current Status

```bash
# Check if Supabase is active
cd "/Users/deshonjackson/thesidia ice"
grep USE_SUPABASE .env

# Check for active Supabase connections
lsof -i -P -n | grep supabase

# Check local SQLite database
ls -lh data/conversations.sqlite3
```

## Summary

**Current State**:
- Thesidia project: ✅ Local only (not in iCloud)
- Supabase: ⚠️ Active (sending conversations to cloud)
- Biometric data: ✅ None collected
- Other cloud services: ✅ None detected

**Your Data**:
- Conversations: Stored in Supabase cloud (if enabled) OR local SQLite (if disabled)
- User profiles: Local JSON files only
- Uploads: Local files only
- No biometric data: Confirmed
