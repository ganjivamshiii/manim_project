# manim_project
A web application that generates mathematical animations using Manim (Mathematical Animation Engine) based on user prompts, powered by Hugging Face's Mixtral 8x7B model.

## 🌟 Features

- **AI-Powered Animation Generation**: Utilizes Hugging Face's Mixtral 8x7B model to convert natural language prompts into Manim code
- **Real-Time Rendering Pipeline**: Asynchronous video processing with Flask backend
- **Code Sanitization Engine**: Robust code cleaning and validation system
- **Fallback Mechanism**: Graceful degradation with default animations when generation fails
- **Task Management System**: Background job tracking with UUID-based task identification

## 🛠️ Technology Stack

### Backend
- **Python 3** with **Flask** web framework
- **Manim** (Mathematical Animation Engine) for vector graphics rendering
- **Hugging Face Inference API** (Mixtral 8x7B model)
- **Subprocess Management** for Manim CLI execution
- **Thread-based Asynchronous Processing**
- **UUID-based Task Tracking**

### Frontend
- **HTML5** semantic markup
- **CSS3** with responsive design principles
- **JavaScript ES6+** with Fetch API for asynchronous operations
- **AJAX-based Status Polling**

### Infrastructure
- **File System Management** for temporary storage and video output
- **Environment Variable Configuration** for API keys
- **Cross-Platform Path Handling**

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- Manim Community Edition (`pip install manim`)
- FFmpeg
- Hugging Face API key (set as `HF_API_KEY` environment variable)

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/manim-generator.git
cd manim-generator

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Configuration
```bash
# Set your Hugging Face API key
export HF_API_KEY="your_api_key_here"  # Linux/Mac
set HF_API_KEY="your_api_key_here"     # Windows
```

## 🏗️ Project Structure

```
Gradientlearning/
|__Authentication
   |__app.py 
|               # Flask application entry point
├── static/
│   ├── videos/           # Rendered animation storage
│   └── css/              # Static CSS files
├── templates/
│   └── index.html        # Frontend interface
└── temp_scenes/          # Temporary Manim script storage
```

## 🧠 Technical Implementation Details

### Core Components

1. **AI Integration Layer**
   - Utilizes Hugging Face's inference API with Mixtral 8x7B model
   - Implements prompt engineering with specific constraints for Manim code generation
   - Includes retry mechanism (3 attempts) with exponential backoff

2. **Code Processing Engine**
   - AST-based code sanitization
   - Syntax validation and automatic indentation correction
   - Class name collision avoidance system
   - Fallback code generation subsystem

3. **Rendering Pipeline**
   - Subprocess-based Manim execution
   - Media file management with automatic cleanup
   - Quality level configuration (currently set to low quality `-ql`)

4. **Asynchronous Task Management**
   - Thread-based parallel processing
   - UUID-based task tracking
   - Status polling endpoint with JSON responses

## 🎛️ API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serves the frontend interface |
| `/render` | POST | Initiates animation generation (accepts JSON with `prompt`) |
| `/check-result` | GET | Checks task status (requires `task_id` parameter) |

## 🏃‍♂️ Running the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 📈 Performance Considerations

- Video rendering is CPU-intensive - consider queue systems for production
- Temporary files are automatically managed but not auto-purged
- Low-quality rendering (`-ql` flag) balances speed and quality

## 🛡️ Security Notes

- API keys are loaded from environment variables
- Input sanitization is performed on generated code
- UUIDs prevent predictable resource access

## 📚 Learning Resources

- [Manim Documentation](https://docs.manim.community/)
- [Hugging Face Inference API](https://huggingface.co/docs/api-inference/index)
- [Flask Best Practices](https://flask.palletsprojects.com/en/2.3.x/)

## 🐛 Known Issues

- Complex prompts may generate invalid Manim code
- Rendering times vary significantly based on scene complexity
- No built-in user session management

## 📜 License

MIT License - See LICENSE file for details

---

This project demonstrates advanced integration of modern AI capabilities with mathematical visualization tools, creating a pipeline from natural language to animated mathematical concepts.