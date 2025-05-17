from flask import Flask, request, jsonify
from together import Together
import os
from dotenv import load_dotenv
from flask_cors import CORS
import base64

# Load environment variables
load_dotenv()

# Get Together API key from environment
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "2fe622d88e8c8c3ebb51a96188f6e65ae0ab1e584ee9e3ef3e736a8cd85296d1")

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Together client
client = Together(api_key=TOGETHER_API_KEY)

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
        
        # Generate image using Together API
        response = client.images.generate(
            prompt=enhanced_prompt,
            model="black-forest-labs/FLUX.1-schnell-Free",
            steps=10,
            n=1
        )
        
        # Get image data
        image_url = response.data[0].url
        image_b64 = response.data[0].b64_json
        
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
