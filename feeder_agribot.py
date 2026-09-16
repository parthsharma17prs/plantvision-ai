#!/usr/bin/env python3
import os
import sys
import time
import random
import pickle
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

ROOT_DIR = Path(__file__).parent.resolve()
DATASET_DIR = ROOT_DIR / "plant_dashboard" / "model_training" / "tea_dataset"
INTERVAL_SECONDS = 10
FOLDER_ID = "1nRLc9j0Fb3XoYu1WzeeknM1acwdzAndE"

def get_tea_images():
    images = []
    if not DATASET_DIR.exists():
        return []
    for class_folder in DATASET_DIR.iterdir():
        if class_folder.is_dir():
            for p in class_folder.iterdir():
                if p.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                    images.append((class_folder.name, p))
    return images

def main():
    images = get_tea_images()
    if not images:
        print("❌ No images found in dataset!")
        sys.exit(1)

    os.chdir("Agribot")
    with open("token.pickle", "rb") as token:
        creds = pickle.load(token)
    service = build("drive", "v3", credentials=creds)

    print("🚀 Starting Live Agribot Feeder...")
    
    counter = 1
    while True:
        chosen_class, img_path = random.choice(images)
        ts = time.strftime("%Y%m%d_%H%M%S")
        dest_filename = f"live_feed_{ts}.jpg"

        file_metadata = {"name": dest_filename, "parents": [FOLDER_ID]}
        media = MediaFileUpload(str(img_path), mimetype="image/jpeg")

        try:
            uploaded = service.files().create(body=file_metadata, media_body=media, fields="id, name").execute()
            print(f"📸 [{counter:03d}] Uploaded {dest_filename} (Expected: {chosen_class})", flush=True)
        except Exception as e:
            print(f"❌ Error uploading: {e}", flush=True)

        counter += 1
        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
