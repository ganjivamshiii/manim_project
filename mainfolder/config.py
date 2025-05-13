import os

# Application configuration
UPLOAD_FOLDER = "temp_scenes"
VIDEO_FOLDER = os.path.join("static", "videos")

# Hugging Face API configuration
HF_API_KEY = os.getenv("HF_API_KEY")
HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

def configure_app(app):
    """Configure the Flask application with necessary settings"""
    # Create required directories
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(VIDEO_FOLDER, exist_ok=True)