import os
import time
import json
import shutil
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
IMAGE_FOLDER = os.getenv("IMAGE_FOLDER")
ARCHIVE_FOLDER = os.getenv("ARCHIVE_FOLDER")
UPLOAD_INTERVAL = int(os.getenv("UPLOAD_INTERVAL"))

# Database file
DB_FILE = "database.json"

# Load posted images
def load_posted_images():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump([], f)
    with open(DB_FILE, "r") as f:
        return json.load(f)

# Save posted images
def save_posted_images(posted_images):
    with open(DB_FILE, "w") as f:
        json.dump(posted_images, f)

# Get next image to post in order
def get_next_image():
    posted_images = load_posted_images()
    all_images = sorted(img for img in os.listdir(IMAGE_FOLDER) if img not in posted_images)
    return all_images[0] if all_images else None

# Send image to Discord
def send_image(image_path):
    url = f"https://discord.com/api/v9/channels/{CHANNEL_ID}/messages"
    headers = {"Authorization": f"Bot {TOKEN}"}

    with open(image_path, "rb") as file:
        response = requests.post(url, headers=headers, data={"content": "Here's an image!"}, files={"file": file})

    return response.status_code == 200

# Main loop to post images
def run_bot():
    while True:
        next_image = get_next_image()
        if not next_image:
            print("No new images to post. Waiting...")
        else:
            image_path = os.path.join(IMAGE_FOLDER, next_image)
            if send_image(image_path):
                print(f"Posted {next_image}")
                posted_images = load_posted_images()
                if isinstance(posted_images, list):
                    posted_images.append(next_image)
                else:
                    posted_images = [next_image]
                save_posted_images(posted_images)
                shutil.move(image_path, os.path.join(ARCHIVE_FOLDER, next_image))
            else:
                print(f"Failed to post {next_image}")
        time.sleep(UPLOAD_INTERVAL)

if __name__ == "__main__":
    run_bot()
