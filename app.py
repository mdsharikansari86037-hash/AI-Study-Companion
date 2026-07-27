from flask import Flask, request, jsonify
from flask_cors import CORS
import PyPDF2
import google.generativeai as genai
import os  # Ye library environment variables read karne ke kaam aati hai

app = Flask(__name__)
CORS(app)

# 🔒 SECURE WAY: Ab API key direct nahi likhenge, internet ke secure vault se lenge
API_KEY = os.environ.get("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("Warning: API Key not found in environment!")

model = genai.GenerativeModel('gemini-pro')

current_pdf_context = ""

@app.route('/analyze', methods=['POST'])
def analyze_pdf():
    global current_pdf_context
    
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded. Please select a document."}), 400
        
    file = request.files['file']
    
    try:
        pdf_text = ""
        pdf_reader = PyPDF2.PdfReader(file)
        
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                pdf_text += text
        
        current_pdf_context = pdf_text[:15000]
        
        ai_prompt = f"""
        Analyze the following text from a PDF document. 
        1. Extract all mathematical calculations or formulas.
        2. List the most important topics discussed.
        3. Provide a short, precise summary.
        Write everything in clean English and use basic HTML formatting (like <b>, <ul>, <li>) for presentation.
        
        Document Text:
        {current_pdf_context}
        """
        
        response = model.generate_content(ai_prompt)
        return jsonify({"analysis": response.text})
        
    except Exception as e:
        return jsonify({"error": f"Failed to process the PDF. Error details: {str(e)}"}), 500

@app.route('/chat', methods=['POST'])
def chat_assistant():
    global current_pdf_context
    user_data = request.json
    user_message = user_data.get("message", "")
    
    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400
        
    try:
        chat_prompt = f"""
        You are an AI Study Assistant for Sharique's website. 
        Here is the content of the uploaded document for your reference:
        {current_pdf_context}
        
        Student's Question: {user_message}
        
        Provide a direct, helpful, and correct answer based ONLY on the document provided above. 
        If it's a general study question not related to the document, answer it normally in English.
        """
        
        response = model.generate_content(chat_prompt)
        return jsonify({"reply": response.text})
        
    except Exception as e:
        return jsonify({"error": f"Failed to generate a response. Error details: {str(e)}"}), 500

if __name__ == '__main__':
    print("Server initialized successfully. Running Premium AI Backend...")
    app.run(debug=True, port=5000)