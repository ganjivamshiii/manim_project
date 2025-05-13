from flask import Flask
import os
from config import configure_app
from routes import register_routes

# Initialize Flask app
app = Flask(
    __name__,
    static_url_path="/static",
    static_folder=os.path.abspath("static"),
    template_folder="../templates"
)

# Configure app settings and create necessary directories
configure_app(app)

# Register all routes
register_routes(app)

if __name__ == "__main__":
    app.run(debug=True, threaded=True)