import os
import json
import re
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from google import genai
import PyPDF2

# ==============================
# CONFIG
# ==============================
app = Flask(__name__, template_folder="templates")
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Use the environment-supported model
MODEL_ID = "gemini-2.5-flash"
client = genai.Client(api_key="YOUR_GEMINI_API_KEY") 

# ==============================
# 1. PDF PARSING
# ==============================
def pdf_parsing(pdf_path):
    """Extracts raw text from a PDF file."""
    text = ""
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

# ==============================
# 2. RESUME PARSING
# ==============================
def resume_parsing(resume_text):
    """Formats raw extracted text into a structured resume profile using AI."""
    prompt = f"""
    Analyze the following raw resume text and extract the key profile details.
    Organize it into:
    - Core Skills
    - Professional Experience Highlights
    - Education
    - Technical Tools

    Resume Text:
    {resume_text}
    """
    try:
        response = client.models.generate_content(model=MODEL_ID, contents=prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Resume Parsing Error: {e}")
        return resume_text

# ==============================
# 3. JD PARSING
# ==============================
def jd_parsing(jd_text):
    """Extracts job details, requirements, and keywords from the description."""
    prompt = f"""
    Analyze the following Job Description and extract the critical requirements.
    Focus on:
    - Essential Technical Skills
    - Soft Skills & Leadership
    - Primary Responsibilities
    - Minimum Qualifications

    Job Description:
    {jd_text}
    """
    try:
        response = client.models.generate_content(model=MODEL_ID, contents=prompt)
        return response.text.strip()
    except Exception as e:
        print(f"JD Parsing Error: {e}")
        return jd_text

# ==============================
# 4. ATS CHECKER (Robust JSON Extraction)
# ==============================
def ats_checker(parsed_resume, parsed_jd):
    """
    Compares the processed resume and job description.
    Uses Regex to find the JSON block to avoid errors from conversational AI text.
    """
    prompt = f"""
    You are an expert ATS (Applicant Tracking System). 
    Compare the following Parsed Resume and Parsed Job Description.

    PARSED RESUME:
    {parsed_resume}

    PARSED JOB DESCRIPTION:
    {parsed_jd}

    TASK:
    Return a JSON object ONLY. 
    
    REQUIRED JSON STRUCTURE (Ensure these exact keys):
    {{
        "score": 85,
        "summary": "Executive summary of the match.",
        "pros": ["Point 1", "Point 2"],
        "cons": ["Gap 1", "Gap 2"],
        "improvements": ["Action 1", "Action 2"]
    }}
    """
    try:
        response = client.models.generate_content(model=MODEL_ID, contents=prompt)
        raw_text = response.text.strip()
        
        # FIND THE JSON BLOCK: Look for the first '{' and the last '}'
        # This is more reliable than split("```")
        start_idx = raw_text.find('{')
        end_idx = raw_text.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
            json_string = raw_text[start_idx:end_idx + 1]
            return json.loads(json_string)
        else:
            # If no brackets found, try parsing the raw text directly
            return json.loads(raw_text)

    except Exception as e:
        print(f"ATS Checker Error: {e}")
        # Return a valid JSON response so the frontend doesn't crash
        return {
            "score": 0,
            "summary": "The AI failed to generate a structured response. Please try again.",
            "pros": ["Error parsing response"],
            "cons": ["Internal AI error"],
            "improvements": ["Try simplifying the job description"]
        }

# ==============================
# ROUTES
# ==============================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    if "resume" not in request.files:
        return jsonify({"error": "No resume file uploaded"}), 400

    resume_file = request.files["resume"]
    raw_jd_text = request.form.get("job_description", "").strip()

    if not resume_file or not raw_jd_text:
        return jsonify({"error": "Both resume and job description are required"}), 400

    try:
        # Save and extract raw text
        pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], resume_file.filename)
        resume_file.save(pdf_path)
        
        # 1. PDF Parsing
        raw_resume_text = pdf_parsing(pdf_path)
        
        # Clean up the file immediately after extraction
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

        if not raw_resume_text.strip():
            return jsonify({"error": "Empty or unreadable PDF"}), 400

        # 2. Resume Parsing (LLM Step 1)
        formatted_resume = resume_parsing(raw_resume_text)

        # 3. JD Parsing (LLM Step 2)
        formatted_jd = jd_parsing(raw_jd_text)

        # 4. ATS Checker (LLM Step 3 - Final JSON)
        final_results = ats_checker(formatted_resume, formatted_jd)

        # Return the JSON object to the frontend
        return jsonify(final_results)

    except Exception as e:
        print(f"Route Error: {e}")
        return jsonify({"error": "A server error occurred during analysis"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=8080)