from flask import Flask, request, jsonify, render_template
import requests
import os
import time

app = Flask(__name__)

# Ollama configuration
OLLAMA_CONFIG = {
    "base_url": "http://localhost:11434/api",
    "model": "tinyllama",
    "temperature": 0.3,
    "max_tokens": 200,
    "timeout": 45
}

def generate_prompt(user_query: str) -> str:
    """Generate prompt that forces ONLY health responses"""
    return f"""<|im_start|>system
You are a medical assistant. Respond to health questions with:
- Only factual health information
- No guidelines/rules about how to respond
- No lists of instructions
- Just 1-3 sentences of medical advice
Example response to "headache":
"Common causes include stress or dehydration. Try resting and drinking water. See a doctor if severe."<|im_end|>
<|im_start|>user
{user_query}<|im_end|>
<|im_start|>assistant
"""
def get_ai_response(prompt: str) -> str:
    """Get response with guaranteed no instruction leakage"""
    try:
        response = requests.post(
            f"{OLLAMA_CONFIG['base_url']}/generate",
            json={
                "model": OLLAMA_CONFIG["model"],
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 150,
                    "repeat_penalty": 1.5
                }
            },
            timeout=OLLAMA_CONFIG["timeout"]
        )
        response.raise_for_status()
        
        raw_response = response.json().get("response", "")
        
        # Get only text before any template markers
        clean_response = raw_response.split("<|im_end|>")[0].strip()
        
        # Final cleanup
        clean_response = clean_response.replace("MediAI:", "").replace("ASSISTANT:", "").strip()
        
        # Emergency detection
        if any(phrase in clean_response.lower() for phrase in [
            "chest pain", "can't breathe", "severe pain",
            "unconscious", "heavy bleeding", "stroke"
        ]):
            return "🆘 EMERGENCY! Seek immediate medical care!"
            
        # Only reject empty responses or extremely short ones
        if not clean_response or len(clean_response) < 10:
            return "Could you describe your symptoms in more detail?"
            
        return clean_response
    
    except Exception:
        return "Please consult a healthcare professional for medical advice."

@app.route("/ask", methods=["POST"])
def ask_medibot():
    """Handle medical queries"""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    query = request.json.get("query", "").strip()
    if not query or len(query) > 500:
        return jsonify({"error": "Invalid query (1-500 chars required)"}), 400

    try:
        prompt = generate_prompt(query)
        response = get_ai_response(prompt)
        return jsonify({"response": response})
        
    except Exception:
        return jsonify({"response": "System busy. Please try again later."}), 500

@app.route("/")
def home():
    """Render chat interface"""
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)