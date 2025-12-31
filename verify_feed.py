
import requests
import json
import sys

BASE_URL = "http://localhost:5002"

print(f"Checking APIs at {BASE_URL}...")

s = requests.Session()

# 1. Create Session
print("\n1. Creating Session...")
try:
    resp = s.post(f"{BASE_URL}/api/user/session", json={})
    if resp.status_code != 200:
        print(f"Failed to create session: {resp.status_code} {resp.text}")
        sys.exit(1)
    
    session_data = resp.json()
    user_id = session_data.get('user_id')
    session_id = session_data.get('session_id')
    print(f"Session Created: User={user_id}")
except Exception as e:
    print(f"Exception creating session: {e}")
    sys.exit(1)

# 2. Get Feed
print(f"\n2. Fetching Feed for {user_id}...")
try:
    params = {
        'user_id': user_id,
        'session_id': session_id,
        'limit': 5,
        'filter': 'for-you'
    }
    resp = s.get(f"{BASE_URL}/api/feed", params=params)
    if resp.status_code == 200:
        data = resp.json()
        items = data.get('items', [])
        print(f"Feed Items returned: {len(items)}")
        if len(items) > 0:
            print("Item 1:", items[0].get('content', '')[:50])
        else:
            print("FEED IS EMPTY!")
    else:
        print(f"Feed Error: {resp.status_code} {resp.text}")

except Exception as e:
    print(f"Exception fetching feed: {e}")
