from flask import Flask, render_template_string, request, redirect, send_from_directory
import os
import json
import requests
from dotenv import load_dotenv
import shutil

app = Flask(__name__)

IMAGE_FOLDER = "IMAGES/IMAGE_FOLDER"
ARCHIVE_FOLDER = "IMAGES/ARCHIVE_FOLDER"
DB_FILE = "database.json"

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# Ensure folders exist
os.makedirs(IMAGE_FOLDER, exist_ok=True)
os.makedirs(ARCHIVE_FOLDER, exist_ok=True)

# Load posted images
def load_posted_images():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return []

# Save posted images
def save_posted_images(posted_images):
    with open(DB_FILE, "w") as f:
        json.dump(posted_images, f)

# Get upcoming images
def get_upcoming_images():
    posted_images = load_posted_images()
    all_images = [img for img in os.listdir(IMAGE_FOLDER) if img not in posted_images]
    return sorted(all_images)[:48]

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Image Upload Monitor</title>
    <style>
    body { font-family: Arial, sans-serif; }
    .image-list { display: flex; flex-wrap: wrap; list-style: none; padding: 0; }
    .image-list li { margin: 10px; cursor: pointer; }
    img { width: 100px; height: auto; transition: 0.3s; }

    /* Fullscreen overlay */
    .overlay {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.9); display: none;
        justify-content: center; align-items: center;
    }
    .overlay img {
        width: 100vw; 
        height: 100vh;
        object-fit: contain;
    }
    .close-btn {
        position: absolute; top: 20px; right: 30px;
        font-size: 40px; color: white; cursor: pointer;
        background: rgba(0, 0, 0, 0.6); padding: 10px;
        border-radius: 5px;
    }
</style>

</head>
<body>
    <h1>Upcoming Images</h1>
    <ul class="image-list">
        {% for image in images %}
            <li>
                <img src="/static/{{ image }}" alt="{{ image }}" onclick="openImage('/static/{{ image }}')">
                <b>{{ image }}</b>
                <form action="/post" method="post" style="display:inline;">
                    <input type="hidden" name="image" value="{{ image }}">
                    <button type="submit">Post Now</button>
                </form>
                <form action="/delete" method="post" style="display:inline;">
                    <input type="hidden" name="image" value="{{ image }}">
                    <button type="submit">Delete Permanently</button>
                </form>
            </li>
        {% endfor %}
    </ul>

 <!-- Fullscreen Image View -->
<div class="overlay" id="imageOverlay">
    <span class="close-btn" onclick="closeImage()">&times;</span>
    <img id="fullImage" src="" alt="Fullscreen Image">
</div>


<script>
    function openImage(src) {
        document.getElementById("fullImage").src = src;
        document.getElementById("imageOverlay").style.display = "flex";
    }

    function closeImage() {
        document.getElementById("imageOverlay").style.display = "none";
    }
</script>

</body>
</html>



"""

# Serve image
@app.route("/static/<filename>")
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

# Home route to show the images
@app.route("/")
def index():
    upcoming_images = get_upcoming_images()
    return render_template_string(HTML_TEMPLATE, images=upcoming_images)

# Post image now
@app.route("/post", methods=["POST"])
def post_now():
    image = request.form["image"]
    image_path = os.path.join(IMAGE_FOLDER, image)
    if send_image(image_path):
        posted_images = load_posted_images()
        posted_images.append(image)
        save_posted_images(posted_images)
        shutil.move(image_path, os.path.join(ARCHIVE_FOLDER, image))
        print(f"Posted {image}")
    else:
        print(f"Failed to post {image}")
    return redirect("/")

# Send image to Discord
def send_image(image_path):
    url = f"https://discord.com/api/v9/channels/{CHANNEL_ID}/messages"
    headers = {"Authorization": f"Bot {TOKEN}"}

    with open(image_path, "rb") as file:
        response = requests.post(url, headers=headers, data={"content": "Here's an image!"}, files={"file": file})

    return response.status_code == 200

# Delete image permanently
@app.route("/delete", methods=["POST"])
def delete_image():
    image = request.form["image"]
    # Remove from posted images
    posted_images = load_posted_images()
    if image in posted_images:
        posted_images.remove(image)
    save_posted_images(posted_images)
    # Delete file from folder
    os.remove(os.path.join(IMAGE_FOLDER, image))
    return redirect("/")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002, debug=True)
