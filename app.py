from flask import Flask, request, jsonify, render_template
from difflib import get_close_matches
import json
import os

app = Flask(__name__)

# ===== Comprehensive Medical Knowledge =====
def load_medical_knowledge():
    # Load from external JSON file with error handling
    try:
        with open('medical_qa.json') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: medical_qa.json not found. Using fallback data.")
        return {
            "headache": "Common causes include tension or dehydration. Try rest and hydration.",
            "fever": "Normal body temperature is 98.6°F (37°C). Seek care if high or persistent."
        }

MEDICAL_QA = load_medical_knowledge()

# ===== Enhanced Response System =====
def get_medical_response(query):
    query = query.lower().strip()
    
    # 1. Emergency detection (expanded list)
    EMERGENCIES = {
        "chest pain": "🆘 EMERGENCY: May indicate heart attack. Call 911 immediately.",
        "can't breathe": "🆘 EMERGENCY: Seek immediate medical attention.",
        "severe bleeding": "🆘 Apply direct pressure to wound and call emergency services.",
        "stroke symptoms": "🆘 Remember FAST: Face drooping, Arm weakness, Speech difficulty - Time to call 911.",
        "unconscious": "🆘 Check for breathing and pulse. Call 911 immediately.",
        "suicidal thoughts": "🆘 Please call the National Suicide Prevention Lifeline at 988",
        "severe allergic reaction": "🆘 Use epinephrine if available and call 911 immediately."
    }
    
    for phrase, response in EMERGENCIES.items():
        if phrase in query:
            return response
    
    # 2. Exact match (with spelling correction)
    if query in MEDICAL_QA:
        return MEDICAL_QA[query]
    
    # 3. Fuzzy match (improved with plural/synonym handling)
    matches = get_close_matches(query, MEDICAL_QA.keys(), n=3, cutoff=0.5)
    for match in matches:
        if match in MEDICAL_QA:
            return MEDICAL_QA[match]
    
    # 4. Try partial matches
    for question in MEDICAL_QA.keys():
        if query in question or any(word in question for word in query.split()[:3]):
            return MEDICAL_QA[question]
    
    # 5. Related topics (dynamic based on query words)
    query_words = set(query.split())
    related = [q for q in MEDICAL_QA.keys() if any(word in q for word in query_words)][:3]
    
    if related:
        return f"I can help with: {', '.join(related)}. Could you be more specific?"
    return "For personalized medical advice, please consult a healthcare professional."

# ===== Flask Routes =====
@app.route("/ask", methods=["POST"])
def ask_medibot():
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json()
        query = data.get("query", "").strip()
        
        if not query:
            return jsonify({"error": "Empty query"}), 400
        if len(query) > 500:
            return jsonify({"error": "Query too long (max 500 chars)"}), 400
        
        response = get_medical_response(query)
        return jsonify({"response": response})
    
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)