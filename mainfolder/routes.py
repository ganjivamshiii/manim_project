from flask import request, jsonify, render_template
import uuid
import threading
import re
import os
import shutil
import subprocess
from code_generation import generate_with_hf, get_fallback_animation
from config import UPLOAD_FOLDER, VIDEO_FOLDER

# Task tracking
active_tasks = {}

def register_routes(app):
    """Register all routes with the Flask app"""
    
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/render", methods=["POST"])
    def render_video():
        data = request.get_json()
        user_prompt = data.get("prompt", "").strip()
        if not user_prompt:
            return jsonify({"error": "No prompt provided"}), 400

        # Start async processing
        task_id = str(uuid.uuid4())
        active_tasks[task_id] = {"status": "processing", "prompt": user_prompt}
        threading.Thread(target=async_render, args=(task_id, user_prompt)).start()
        return jsonify({"status": "processing", "task_id": task_id})

    @app.route("/check-result", methods=["GET"])
    def check_result():
        task_id = request.args.get("task_id")
        if not task_id or task_id not in active_tasks:
            return jsonify({"status": "error", "message": "Invalid task ID"}), 404
        
        task = active_tasks[task_id]
        if task["status"] == "complete":
            return jsonify({
                "status": "complete",
                "video_path": task.get("video_path"),
                "manim_code": task.get("code")
            })
        elif task["status"] == "error":
            return jsonify({"status": "error", "message": task.get("message")}), 400
        else:
            return jsonify({"status": "processing"})

def async_render(task_id, prompt):
    try:
        # Generate code using Hugging Face API
        manim_code = generate_with_hf(prompt)
        
        # Process the Manim code
        scene_id = str(uuid.uuid4())
        filename = f"{scene_id}.py"
        filepath = os.path.abspath(os.path.join(UPLOAD_FOLDER, filename))
        
        # Save the code and log it for debugging
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(manim_code)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Failed to save file: {filepath}")
        print(f"Generated code saved to {filepath}:")
        print("-"*40)
        print(manim_code)
        print("-"*40)

        # Extract scene class name
        scene_match = re.search(r"class\s+(\w+)\(Scene\)", manim_code)
        if not scene_match:
            raise ValueError("No valid Scene class found in the generated code")
        scene_name = scene_match.group(1)
        
        # Validate Scene name doesn't conflict with Manim's own classes
        if scene_name in ["Circle", "Square", "Rectangle", "Line", "Text"]:
            # Rename the class
            new_scene_name = f"{scene_name}Animation"
            manim_code = manim_code.replace(f"class {scene_name}(Scene)", f"class {new_scene_name}(Scene)")
            # Save the updated code
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(manim_code)
            scene_name = new_scene_name

        video_found = render_animation(filepath, scene_id, scene_name, manim_code)
        
        # If the primary animation failed, try the fallback
        if not video_found:
            print("Using fallback animation...")
            fallback_code = get_fallback_animation()
            video_found = render_fallback_animation(scene_id, fallback_code)
            if video_found:
                manim_code = fallback_code  # Use fallback code for display
        
        if video_found:
            rel_path = f"/static/videos/{scene_id}.mp4"
            active_tasks[task_id] = {
                "status": "complete",
                "video_path": rel_path,
                "code": manim_code
            }
        else:
            raise FileNotFoundError("Could not create any video")
            
    except Exception as e:
        error_message = str(e)
        print(f"Error in async render: {error_message}")
        active_tasks[task_id] = {
            "status": "error",
            "message": error_message
        }

def render_animation(filepath, scene_id, scene_name, manim_code):
    """Render the animation using manim"""
    media_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "media")
    os.makedirs(media_dir, exist_ok=True)
    
    video_found = False
    
    try:
        print(f"Rendering animation for scene: {scene_name}")
        print(f"Running Manim with:\n - File: {filepath}\n - Scene: {scene_name}\n - File exists? {os.path.exists(filepath)}\n")
        result = subprocess.run(
            ["manim", "-ql", "--media_dir", media_dir, filepath, scene_name],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__)))  # Use absolute path
        
        if result.returncode != 0:
            raise RuntimeError(f"Manim error: {result.stderr}")
            
        # Try to find the video file
        for root, _, files in os.walk(media_dir):
            for file in files:
                if file.endswith(".mp4") and scene_name in file:
                    video_path = os.path.join(VIDEO_FOLDER, f"{scene_id}.mp4")
                    os.makedirs(os.path.dirname(video_path), exist_ok=True)
                    shutil.move(os.path.join(root, file), video_path)
                    video_found = True
                    print(f"Video successfully created: {video_path}")
                    break
            if video_found:
                break
    except Exception as e:
        print(f"Primary animation failed: {str(e)}")
    
    return video_found

def render_fallback_animation(scene_id, fallback_code):
    """Render the fallback animation when main animation fails"""
    media_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "media")
    abs_path = os.path.abspath(os.path.dirname(__file__))
    fallback_file = os.path.abspath(os.path.join(UPLOAD_FOLDER, f"fallback_{scene_id}.py"))
    
    # Make sure directory exists
    os.makedirs(os.path.dirname(fallback_file), exist_ok=True)
    video_found = False
    
    try:
        with open(fallback_file, "w", encoding="utf-8") as f:
            f.write(fallback_code)
            
        # Run with absolute paths
        result = subprocess.run(
            ["manim", "-ql", "--media_dir", media_dir, fallback_file, "FallbackScene"],
            capture_output=True,
            text=True,
            cwd=abs_path)
            
        if result.returncode != 0:
            # If everything fails, handle the error
            raise RuntimeError(f"Fallback animation also failed. Error: {result.stderr}")
        
        # Find the fallback video
        for root, _, files in os.walk(media_dir):
            for file in files:
                if file.endswith(".mp4") and "FallbackScene" in file:
                    video_path = os.path.join(VIDEO_FOLDER, f"{scene_id}.mp4")
                    os.makedirs(os.path.dirname(video_path), exist_ok=True)
                    shutil.move(os.path.join(root, file), video_path)
                    video_found = True
                    print(f"Fallback video created: {video_path}")
                    break
            if video_found:
                break
    except Exception as e:
        print(f"Fallback animation failed: {str(e)}")
    
    return video_found