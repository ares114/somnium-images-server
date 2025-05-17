from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from flask_cors import CORS
import base64
import requests
import json

# Load environment variables
load_dotenv()

# Get Together API key from environment
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "2fe622d88e8c8c3ebb51a96188f6e65ae0ab1e584ee9e3ef3e736a8cd85296d1")

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Token validation - simple security measure
VALID_TOKEN = "3aff4c3a-83a4-4000-9ce1-5449c4ce0216"

@app.before_request
def validate_token():
    # Skip token validation for health check
    if request.path == '/health':
        return None
        
    # Check for token in query params or headers
    token = request.args.get('token')
    if not token or token != VALID_TOKEN:
        return jsonify({"success": False, "error": "Invalid or missing token"}), 403

@app.route('/generate-image', methods=['POST'])
def generate_image():
    try:
        # Get data from request
        data = request.json
        prompt = data.get('prompt', '')
        gender = data.get('gender', 'male')
        title = data.get('title', '')
        
        # Enhance the prompt
        dreamer = "a woman" if gender.lower() == "female" else "a man"
        
        # Combine title and content if title exists
        if title:
            content = f"{title}: {prompt}"
        else:
            content = prompt
            
        # Truncate to 500 chars if needed
        if len(content) > 500:
            content = content[:500]
        
        # Create enhanced prompt
        enhanced_prompt = f"A vivid, detailed dreamscape where {dreamer} experiences: {content}. Ethereal, surreal, cinematic quality."
        
        print(f"Generating image with prompt: {enhanced_prompt[:100]}...")
        
        # Call Together API directly using requests
        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "black-forest-labs/FLUX.1-schnell-Free",
            "prompt": enhanced_prompt,
            "steps": 10,
            "n": 1
        }
        
        response = requests.post(
            "https://api.together.xyz/v1/images/generations",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            print(f"API Error: {response.status_code}, {response.text}")
            return jsonify({
                "success": False,
                "error": f"Together API error: {response.status_code}"
            }), 500
        
        # Parse the response
        response_data = response.json()
        print(f"API response: {json.dumps(response_data)[:100]}...")
        
        # Get the image data
        image_data = response_data.get("data", [])[0]
        image_url = image_data.get("url", "")
        image_b64 = image_data.get("b64_json", "")
        
        # Return both URL and base64 data
        return jsonify({
            "success": True,
            "image_url": image_url,
            "image_b64": image_b64
        })
    
    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    # Get port from environment or use 5000
    port = int(os.environ.get('PORT', 5000))
    # Run with debug=True for development
    app.run(host='0.0.0.0', port=port)
