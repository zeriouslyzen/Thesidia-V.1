# Sensor and Activity Data Report
Generated: January 22, 2026

## Executive Summary

**Status**: macOS is actively collecting and storing sensor/activity data in multiple databases. These databases are growing and contain detailed activity tracking.

## Active Data Collection Systems

### 1. CoreDuet (Activity Tracking)
**Status**: ✅ **ACTIVE AND RUNNING**

**Processes**:
- `/usr/libexec/coreduetd` (running as root)
- `ContextStoreAgent` (running as user)
- `contextstored` (running as root)

**Configuration**:
- Location: `~/Library/Preferences/com.apple.CoreDuet.plist`
- Sync Status: ScreenTime sync disabled for cloud/rapport
- Purpose: Tracks device usage, app activity, location patterns

**What It Tracks**:
- App usage patterns
- Location history
- Device interaction timing
- Activity correlations

### 2. Knowledge Database (Intelligence Platform)
**Status**: ✅ **ACTIVE AND ACCUMULATING DATA**

**Location**: `~/Library/Application Support/Knowledge/knowledgeC.db`

**Size**: 18 MB (main database) + 2.3 MB (write-ahead log)

**Tables Found**:
- `Z_4EVENT` - Event tracking
- `ZADDITIONCHANGESET` - Change tracking
- `ZCONTEXTUALCHANGEREGISTRATION` - Context changes
- `ZCONTEXTUALKEYPATH` - Contextual key paths
- `ZCUSTOMMETADATA` - Custom metadata
- `ZDELETIONCHANGESET` - Deletion tracking
- `ZHISTOGRAM` - Activity histograms
- `ZHISTOGRAMVALUE` - Histogram values
- `ZKEYVALUE` - Key-value storage
- `ZSOURCE` - Data sources

**Purpose**: macOS Intelligence Platform - learns user patterns, app usage, contextual information

**Data Types**:
- App usage patterns
- Document access patterns
- Time-based activity patterns
- Contextual correlations

### 3. Biome Databases (Intelligence Platform Entity)
**Status**: ✅ **ACTIVE AND ACCUMULATING DATA**

**Location**: `~/Library/Biome/databases/IntelligencePlatform.Entity/`

**Size**: 9.3 MB (main database)

**Purpose**: Entity tracking and relationship mapping for intelligence features

**What It Tracks**:
- Entity relationships
- Activity patterns
- Contextual associations
- User behavior patterns

### 4. CoreMotion Framework
**Status**: ✅ **AVAILABLE BUT NOT ACTIVELY COLLECTED BY THESIDIA**

**System Framework**: `/System/Library/Frameworks/CoreMotion.framework`

**Available Sensors**:
- Accelerometer (3-axis motion)
- Gyroscope (3-axis rotation)
- Magnetometer (3-axis magnetic field)
- Device Motion (combined motion data)

**Thesidia Status**: 
- Code exists for sensor integration (`docs/TELEMETRY_INTEGRATION_PLAN.md`)
- **NOT CURRENTLY IMPLEMENTED** in active codebase
- Plans exist but not executed

**Note**: Thesidia has documentation for sensor fusion but does NOT currently access these sensors.

## Data Accumulation Analysis

### Growing Databases

1. **Knowledge Database**: 18 MB + 2.3 MB WAL = **20.3 MB total**
   - Actively being written to (WAL file updated Jan 22, 2026)
   - Contains event tracking and contextual data

2. **Biome Intelligence Platform**: **9.3 MB**
   - Entity relationship tracking
   - Activity pattern analysis

3. **CoreDuet**: Configuration exists, processes running
   - Data location: System-managed (not directly accessible)
   - Tracks activity patterns across devices

### Other Activity Tracking

**SharedFileList**: 472 KB
- Recent documents tracking
- Application usage patterns
- File access history

**Biome Games Database**: 3.8 MB WAL
- Game activity tracking
- Recently played games

## What Data Is Being Collected

### By macOS System (Not Thesidia)

1. **App Usage**: Which apps you use, when, how long
2. **Location Patterns**: Where you use your device (if location services enabled)
3. **Activity Timing**: When you're active, patterns of use
4. **Contextual Correlations**: Relationships between activities
5. **Document Access**: Which files you open, when
6. **Interaction Patterns**: How you interact with the system

### By Thesidia

**Status**: ❌ **NO SENSOR DATA COLLECTION**

- Thesidia does NOT access CoreMotion sensors
- Thesidia does NOT access health/medical data
- Thesidia does NOT access physiological sensors
- Thesidia only processes text input and stores conversations

**Note**: Thesidia has PLANS for sensor integration (documented) but these are NOT implemented.

## Data Storage Locations

### System Databases (macOS)

```
~/Library/Application Support/Knowledge/
  └── knowledgeC.db (18 MB) - Intelligence Platform

~/Library/Biome/databases/
  └── IntelligencePlatform.Entity/ (9.3 MB)
  └── Games.RecentlyPlayed/ (3.8 MB WAL)

~/Library/Application Support/com.apple.sharedfilelist/
  └── Recent documents/applications tracking (472 KB)

System-managed CoreDuet data (not directly accessible)
```

### Thesidia Project

```
/Users/deshonjackson/thesidia ice/data/
  └── conversations.sqlite3 (76 KB) - Only conversation text
  └── users/ - User profiles (text only)
  └── No sensor data
  └── No activity tracking
```

## Privacy Implications

### macOS System Tracking

**What's Being Tracked**:
- ✅ App usage patterns
- ✅ Activity timing
- ✅ Document access
- ✅ Contextual correlations
- ⚠️ Location (if enabled)
- ⚠️ Device motion (if apps request it)

**Where Data Goes**:
- Local databases (Knowledge, Biome)
- System Intelligence Platform
- Potentially synced to iCloud (if enabled)
- Used for Siri suggestions, Spotlight, etc.

### Thesidia Tracking

**What's Being Tracked**:
- ✅ Conversation text only
- ✅ User interactions (clicks, navigation) - if Supabase enabled
- ❌ NO sensor data
- ❌ NO physiological data
- ❌ NO motion data
- ❌ NO health data

## How to Reduce/Disable Data Collection

### Disable macOS Intelligence Features

1. **Disable Siri Suggestions**:
   ```bash
   # System Settings > Siri & Spotlight
   # Turn off "Siri Suggestions"
   ```

2. **Disable Location Services** (if desired):
   ```bash
   # System Settings > Privacy & Security > Location Services
   # Turn off location services
   ```

3. **Clear Knowledge Database** (if desired):
   ```bash
   # WARNING: This will reset Siri suggestions and intelligence features
   rm ~/Library/Application\ Support/Knowledge/knowledgeC.db*
   ```

4. **Disable CoreDuet Sync** (already partially disabled):
   - Current config shows ScreenTime sync disabled
   - Can disable more via System Settings

### Thesidia Data

**Already Minimal**:
- Only stores conversation text
- No sensor access
- Supabase can be disabled (see previous report)

## Recommendations

### If You Want to Minimize Data Collection

1. **Review System Settings**:
   - Privacy & Security > Analytics & Improvements
   - Privacy & Security > Location Services
   - Siri & Spotlight > Siri Suggestions

2. **Clear Existing Databases** (if desired):
   ```bash
   # Clear Knowledge database (resets intelligence features)
   rm ~/Library/Application\ Support/Knowledge/knowledgeC.db*
   
   # Clear Biome databases (resets entity tracking)
   rm -rf ~/Library/Biome/databases/*
   ```

3. **Disable Thesidia Cloud Sync** (if not already):
   ```bash
   # Edit .env file
   USE_SUPABASE=false
   ```

### Current Status Summary

- **macOS System**: Actively collecting activity/sensor data (20+ MB)
- **Thesidia**: NO sensor data collection (only text conversations)
- **CoreMotion Sensors**: Available but NOT accessed by Thesidia
- **Health/Medical Data**: NOT being collected by Thesidia

## Action Items

1. ✅ **Confirmed**: Thesidia does NOT collect sensor/physiological data
2. ⚠️ **Found**: macOS system databases accumulating activity data (20+ MB)
3. 📋 **Optional**: Review and disable macOS intelligence features if desired
4. 📋 **Optional**: Clear existing activity databases if desired
