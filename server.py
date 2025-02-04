from flask import Flask, render_template_string, request, redirect, send_from_directory
import os
import json

app = Flask(__name__)

IMAGE_FOLDER = "IMAGES/IMAGE_FOLDER"
ARCHIVE_FOLDER = "IMAGES/ARCHIVE_FOLDER"
DB_FILE = "database.json"

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
        .image-list li { margin: 10px; }
        img { width: 100px; height: auto; }
    </style>
</head>
<body>
    <h1>Upcoming Images</h1>
    <ul class="image-list">
        {% for image in images %}
            <li>
                <img src="/static/{{ image }}" alt="{{ image }}">
                <b>{{ image }}</b>
                <form action="/move" method="post" style="display:inline;">
                    <input type="hidden" name="image" value="{{ image }}">
                    <button type="submit">Move to Top</button>
                </form>
                <form action="/delete" method="post" style="display:inline;">
                    <input type="hidden" name="image" value="{{ image }}">
                    <button type="submit">Delete Permanently</button>
                </form>
            </li>
        {% endfor %}
    </ul>
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
    images = load_posted_images() + get_upcoming_images()
    return render_template_string(HTML_TEMPLATE, images=images)

# Move image to the top of the list
@app.route("/move", methods=["POST"])
def move_to_top():
    image = request.form["image"]
    posted_images = load_posted_images()
    if image in posted_images:
        posted_images.remove(image)
    posted_images.insert(0, image)
    save_posted_images(posted_images)
    return redirect("/")

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
