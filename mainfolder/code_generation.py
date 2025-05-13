import re
import json
import requests
from requests.exceptions import RequestException, Timeout, HTTPError
from config import HF_API_URL, HEADERS

def clean_manim_code(code):
    """
    Thoroughly clean and reformat Manim code to ensure proper Python syntax and indentation.
    This function completely rebuilds the code structure based on Python syntax rules.
    """
    # Remove non-ASCII characters
    cleaned = re.sub(r'[^\x00-\x7F]+', '', code)
    
    # Extract code between triple backticks if present
    code_match = re.search(r'```(?:python)?\s*(.*?)\s*```', cleaned, re.DOTALL)
    if code_match:
        cleaned = code_match.group(1)
    
    # Split into lines and process
    lines = cleaned.split('\n')
    result = []
    
    # Keep track of whether we've already added the import
    import_added = False
    
    # Track indentation levels
    in_class = False
    in_method = False
    
    for line in lines:
        stripped = line.strip()
        
        # Skip empty lines but preserve them
        if not stripped:
            result.append('')
            continue
            
        # Process imports - should be at the beginning with no indentation
        if stripped.lower().startswith('from manim import') or stripped.lower() == 'from manim import *':
            # Skip duplicate imports
            if not import_added:
                result.append('from manim import *')
                result.append('import numpy as np')
                result.append('from math import pi as PI')
                import_added = True
            continue
            
        # Process class definitions - should have no indentation
        if stripped.startswith('class') and '(' in stripped and ')' in stripped and ':' in stripped:
            in_class = True
            in_method = False
            
            # Ensure class doesn't conflict with Manim classes
            if any(conflict in stripped for conflict in ['class Square(', 'class Circle(', 'class Text(']):
                # Extract class name and add "Animation" to it
                class_name = re.search(r'class\s+(\w+)\(', stripped).group(1)
                stripped = stripped.replace(f'class {class_name}(', f'class {class_name}Animation(')
                
            result.append(stripped)
            continue
            
        # Process method definitions - should be indented under class
        if in_class and stripped.startswith('def') and ':' in stripped:
            in_method = True
            result.append(' ' * 4 + stripped)  # 4 spaces indentation
            continue
            
        # Everything inside a method gets 8-space indentation
        if in_method:
            result.append(' ' * 8 + stripped)
        # Everything directly inside a class (but not in a method) gets 4-space indentation
        elif in_class:
            result.append(' ' * 4 + stripped)
        # Everything else gets no indentation
        else:
            result.append(stripped)
    
    final_code = '\n'.join(result)
    
    # Make sure code starts with the import
    if not import_added:
        final_code = 'from manim import *\nimport numpy as np\nfrom math import pi as PI\n\n' + final_code
        
    # Remove incompatible parameters that cause errors
    final_code = re.sub(r'axis_color\s*=\s*[^,\)]+,?', '', final_code)
    final_code = re.sub(r',\s*\)', ')', final_code)  # Clean up trailing commas
    
    # Fix common compatibility issues
    final_code = re.sub(r'tip_length\s*=\s*[^,\)]+,?', '', final_code)
    final_code = re.sub(r'add_coordinates\(\s*\)', 'add_coordinates()', final_code)
    
    # Check if there's a Scene class
    if 'class' not in final_code or 'Scene' not in final_code:
        # If no proper scene class found, use a default one
        final_code = """from manim import *
import numpy as np
from math import pi as PI

class DefaultScene(Scene):
    def construct(self):
        circle = Circle(color=BLUE)
        self.play(Create(circle))
        text = Text("Animation Example").next_to(circle, UP)
        self.play(Write(text))
"""
    
    return final_code

def generate_with_hf(prompt):
    try:
        payload = {
            "inputs": f"<s>[INST] Generate ONLY Manim code for: {prompt}\nRules:\n1. Use basic shapes\n2. Max 3 animations\n3. No explanations\n4. Include 'from manim import *'\n5. Make sure to use proper Python indentation\n6. Don't use the name 'Square' for a Scene class as it's already defined in Manim\n7. Don't use parameters like 'axis_color' or 'tip_length' which may be incompatible with recent Manim versions\n8. Use manim 0.17.2 compatible syntax only [/INST]",
            "parameters": {"max_new_tokens": 500, "temperature": 0.3, "return_full_text": False}
        }
        
        # Add error handling and retrying
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(HF_API_URL, headers=HEADERS, json=payload, timeout=60)
                response.raise_for_status()
                
                # Handle different response formats
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    code = result[0].get('generated_text', str(result[0]))
                elif isinstance(result, dict) and 'generated_text' in result:
                    code = result['generated_text']
                else:
                    print(f"Unexpected response format: {result}")
                    code = str(result)
                
                # Extract code between ```python and ``` if they exist
                code_match = re.search(r'```python\s*(.*?)\s*```', code, re.DOTALL)
                if code_match:
                    code = code_match.group(1)
                
                # Clean and format the code
                return clean_manim_code(code)
            except (RequestException, Timeout, HTTPError) as e:
                if attempt < max_retries - 1:
                    print(f"Attempt {attempt + 1} failed: {str(e)}. Retrying...")
                    continue
                else:
                    print(f"Max retries reached: {str(e)}")
                    raise RuntimeError(f"API request failed after {max_retries} attempts: {str(e)}")
    except Exception as e:
        print(f"Error in generate_with_hf: {str(e)}")
        # Fallback to a simple example if API fails
        return get_fallback_animation()

def get_fallback_animation():
    """Return a fallback animation code when the main one fails"""
    return """from manim import *
import numpy as np
from math import pi as PI

class FallbackScene(Scene):
    def construct(self):
        title = Text("Animation Example", color=BLUE)
        self.play(Write(title))
        self.wait(0.5)
        
        circle = Circle(color=RED, fill_opacity=0.5)
        self.play(Create(circle))
        
        text = Text("Fallback Animation").scale(0.5).next_to(circle, DOWN)
        self.play(FadeIn(text))
"""
