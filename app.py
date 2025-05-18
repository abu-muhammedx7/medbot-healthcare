from flask import Flask, request, jsonify, render_template
from difflib import get_close_matches
import json
import os

app = Flask(__name__)

# ===== Enhanced Medical Knowledge =====
def load_medical_knowledge():
    try:
        # Load the comprehensive medical data
        with open('medical_qa.json') as f:
            data = json.load(f)
            
            # Transform the symptom array into a Q&A dictionary
            qa_dict = {}
            for symptom in data["symptoms"]:
                # Create multiple query variations for each symptom
                queries = [
                    symptom["name"],
                    f"what is {symptom['name']}",
                    f"how to treat {symptom['name']}",
                    f"causes of {symptom['name']}",
                    f"symptoms of {symptom['name']}"
                ]
                
                # Build a detailed response
                response = (
                    f"**{symptom['name'].title()}**\n"
                    f"Definition: {symptom['definition']}\n"
                    f"Common Causes: {', '.join(symptom['causes'])}\n"
                    f"Examples: {', '.join(symptom['examples'])}\n"
                    f"Advice: {symptom['advice']}"
                )
                
                for query in queries:
                    qa_dict[query] = response
            
            # Add emergency responses
            qa_dict.update({
                "chest pain": "🆘 EMERGENCY: May indicate heart attack. Call 911 immediately.",
                "can't breathe": "🆘 EMERGENCY: Seek immediate medical attention.",
                "severe bleeding": "🆘 Apply direct pressure to wound and call emergency services."
            })
            
            return qa_dict
            
    except Exception as e:
        print(f"Error loading medical data: {str(e)}")
        return {
            "headache": "Common causes include tension or dehydration. Try rest and hydration.",
            "fever": "Normal body temperature is 98.6°F (37°C). Seek care if high or persistent."
        }

MEDICAL_QA = load_medical_knowledge()

# ===== Smart Response System =====
def get_medical_response(query):
    query = query.lower().strip()
    
    # 1. Check for exact match
    if query in MEDICAL_QA:
        return MEDICAL_QA[query]
    
    # 2. Check for partial matches in keys
    for key in MEDICAL_QA.keys():
        if query in key or any(word in key for word in query.split()):
            return MEDICAL_QA[key]
    
    # 3. Fuzzy matching with close matches
    matches = get_close_matches(query, MEDICAL_QA.keys(), n=3, cutoff=0.6)
    if matches:
        return MEDICAL_QA[matches[0]]
    
    # 4. Try to find related topics
    query_words = set(query.split())
    related = [q for q in MEDICAL_QA.keys() if any(word in q for word in query_words)][:3]
    
    if related:
        return f"I can help with: {', '.join(related)}. Could you be more specific?"
    
    return "For personalized medical advice, please consult a healthcare professional."

# ===== API Endpoints =====
@app.route("/ask", methods=["POST"])
def ask_medibot():
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json()
        query = data.get("query", "").strip()
        
        if not query:
            return jsonify({"error": "Empty query"}), 400
        
        response = get_medical_response(query)
        return jsonify({
            "response": response,
            "suggestions": get_suggestions(query)
        })
    
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

def get_suggestions(query):
    """Return 3 most relevant suggestions"""
    query = query.lower()
    return [q for q in MEDICAL_QA.keys() if query in q][:3]

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)