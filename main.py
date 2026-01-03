from flask import render_template
import os
from flask import Flask, request, jsonify
from google import genai
import PyPDF2

# ==============================
# CONFIG
# ==============================
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Using environment variable for security, or replace with your key string
# Initialize the client. 
# NOTE: Ensure you have the 'google-genai' library installed: pip install google-genai
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    # Fallback or warning if key is missing
    print("WARNING: GOOGLE_API_KEY not found in environment variables.")
    # You can hardcode it here for testing: api_key = "YOUR_ACTUAL_KEY"

client = genai.Client(api_key=api_key)

# modified to look for templates in current directory
app = Flask(__name__, template_folder='.') 
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ==============================
# PDF PARSING
# ==============================

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

# ==============================
# RESUME PARSER (LLM)
# ==============================

def parse_resume(resume_text):
    try:
        prompt = f"""
You are a resume parser.

Extract:
- Skills
- Experience summary
- Education
- Tools & technologies

Resume:
{resume_text}

Return in bullet points.
"""
        # Changed to gemini-2.5-flash-preview-09-2025
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error parsing resume: {e}"


# ==============================
# JOB DESCRIPTION PARSER
# ==============================

def parse_job_description(jd_text):
    try:
        prompt = f"""
Extract:
- Required skills
- Responsibilities
- Preferred qualifications

Job Description:
{jd_text}

Return in bullet points.
"""
        # Changed to gemini-2.5-flash-preview-09-2025
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error parsing job description: {e}"


# ==============================
# ATS MATCHING
# ==============================

def ats_match(parsed_resume, parsed_jd):
    try:
        prompt = f"""
You are an Applicant Tracking System.

Compare the resume and job description.

Resume:
{parsed_resume}

Job Description:
{parsed_jd}

Provide:
1. Match percentage (0-100)
2. Matching skills
3. Missing skills
4. Strengths
5. Improvement suggestions
"""
        # Changed to gemini-2.5-flash-preview-09-2025
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"ATS matching error: {e}"


# ==============================
# API ROUTE (PDF UPLOAD)
# ==============================

@app.route("/analyze", methods=["POST"])
def analyze():
    if "resume" not in request.files:
        return jsonify({"error": "Resume PDF is required"}), 400

    resume_file = request.files["resume"]
    jd_text = request.form.get("job_description")

    if not jd_text:
        return jsonify({"error": "Job description is required"}), 400

    # Save PDF
    pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], resume_file.filename)
    resume_file.save(pdf_path)

    # Extract resume text
    resume_text = extract_text_from_pdf(pdf_path)

    # Parse using Gemini
    parsed_resume = parse_resume(resume_text)
    parsed_jd = parse_job_description(jd_text)

    # ATS Matching
    ats_result = ats_match(parsed_resume, parsed_jd)

    return jsonify({
        "parsed_resume": parsed_resume,
        "parsed_job_description": parsed_jd,
        "ats_result": ats_result
    })


@app.route("/")
def home():
    return render_template("index.html")


# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    app.run(debug=True, port=8080)