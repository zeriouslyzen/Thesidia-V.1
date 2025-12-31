import os
import json

TARGET_DIR = 'data'
BROKEN_URLS = [
    "https://videos.pexels.com/video-files/3045163/3045163-hd_1920_1080_30fps.mp4",
    "https://videos.pexels.com/video-files/2491284/2491284-hd_1920_1080_30fps.mp4"
]
BROKEN_THUMBS = [
    "https://videos.pexels.com/video-files/3045163/3045163-hd_1920_1080_30fps.jpg",
    "https://images.pexels.com/videos/2491284/pexels-photo-2491284.jpeg?auto=compress&cs=tinysrgb&dpr=1&w=500",
    "https://videos.pexels.com/video-files/2491284/2491284-hd_1920_1080_30fps.jpg"
]

NEW_VIDEO = "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"
NEW_THUMB = "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/images/ForBiggerBlazes.jpg"

def fix_links(directory):
    count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r') as f:
                        content = f.read()
                    
                    new_content = content
                    for url in BROKEN_URLS:
                        new_content = new_content.replace(url, NEW_VIDEO)
                    for thumb in BROKEN_THUMBS:
                        new_content = new_content.replace(thumb, NEW_THUMB)
                        
                    if new_content != content:
                        with open(path, 'w') as f:
                            f.write(new_content)
                        print(f"Fixed {path}")
                        count += 1
                except Exception as e:
                    print(f"Error processing {path}: {e}")
    print(f"Total files fixed: {count}")

if __name__ == "__main__":
    fix_links(TARGET_DIR)
