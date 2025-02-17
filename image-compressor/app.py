import os
import io
import time
from flask import Flask, request, jsonify, send_file, render_template
from PIL import Image

app = Flask(__name__, static_folder="static", template_folder="templates")

UPLOAD_FOLDER = "uploads"
COMPRESSED_FOLDER = "compressed"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def get_image_size(image):
    img_io = io.BytesIO()
    image.save(img_io, format=image.format)
    return len(img_io.getvalue()) / 1024  # Convert bytes to KB

def compress_image(image, size_limit_kb, timestamp):
    quality = 95
    width, height = image.size
    img_format = image.format if image.format else "JPEG"

    while True:
        img_io = io.BytesIO()
        image.save(img_io, format=img_format, quality=quality)
        img_size_kb = len(img_io.getvalue()) / 1024

        if img_size_kb <= size_limit_kb or quality <= 10:
            break

        quality -= 5
        width = int(width * 0.95)
        height = int(height * 0.95)
        image = image.resize((width, height))

    compressed_path = os.path.join(COMPRESSED_FOLDER, f"compressed_{timestamp}.jpg")
    image.save(compressed_path, format="JPEG", quality=quality)

    return compressed_path, img_size_kb

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "image" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["image"]

    if file and allowed_file(file.filename):
        image = Image.open(file)
        original_size_kb = get_image_size(image)

        timestamp = str(int(time.time()))
        original_path = os.path.join(UPLOAD_FOLDER, f"original_{timestamp}.jpg")
        image.save(original_path)

        return jsonify({
            "original_size": round(original_size_kb, 2),
            "image_url": f"/original_image/{timestamp}",
            "timestamp": timestamp
        })

    return jsonify({"error": "Invalid file format"}), 400

@app.route("/compress", methods=["POST"])
def compress():
    if "size_limit" not in request.form or "timestamp" not in request.form:
        return jsonify({"error": "Invalid request"}), 400

    size_limit_kb = int(request.form["size_limit"])
    timestamp = request.form["timestamp"]
    original_path = os.path.join(UPLOAD_FOLDER, f"original_{timestamp}.jpg")

    if not os.path.exists(original_path):
        return jsonify({"error": "No image uploaded"}), 400

    image = Image.open(original_path)
    compressed_path, compressed_size_kb = compress_image(image, size_limit_kb, timestamp)

    return jsonify({
        "compressed_size": round(compressed_size_kb, 2),
        "image_url": f"/compressed_image/{timestamp}",
        "timestamp": timestamp
    })

@app.route("/original_image/<timestamp>")
def get_original_image(timestamp):
    original_path = os.path.join(UPLOAD_FOLDER, f"original_{timestamp}.jpg")
    if not os.path.exists(original_path):
        return jsonify({"error": "Original image not found"}), 404
    return send_file(original_path, mimetype="image/jpeg")

@app.route("/compressed_image/<timestamp>")
def get_compressed_image(timestamp):
    compressed_path = os.path.join(COMPRESSED_FOLDER, f"compressed_{timestamp}.jpg")
    if not os.path.exists(compressed_path):
        return jsonify({"error": "Compressed image not found"}), 404
    return send_file(compressed_path, mimetype="image/jpeg")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
