import os
import json
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

# Initialize Gemini Client
client = genai.Client(api_key="GEMINI_API_KEY_PLACEHOLDER")

# ==============================
# PDF PARSING
# ==============================
def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file using PyPDF2."""
    extracted_text = ""
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_text += page_text
    except Exception as e:
        print(f"Error parsing PDF: {e}")
    return extracted_text

# ==============================
# ROUTES
# ==============================

@app.route("/")
def index():
    """Renders the frontend template."""
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    """API endpoint to analyze resume compatibility."""
    if "resume" not in request.files:
        return jsonify({"error": "Resume PDF is required"}), 400
    
    resume_file = request.files["resume"]
    jd_text = request.form.get("job_description", "").strip()

    if resume_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Save PDF
        pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], resume_file.filename)
        resume_file.save(pdf_path)
        
        # Extract text
        resume_content = extract_text_from_pdf(pdf_path)
        
        if not resume_content.strip():
            return jsonify({"error": "Could not read PDF text. Ensure it's not an image scan."}), 400

        # Structured Prompt for specific sections
        target_context = f"against this target Job Description: {jd_text}" if jd_text else "based on general industry standards for high-performing resumes"
        
        prompt = f"""
        Act as a professional ATS (Applicant Tracking System) Checker.
        Analyze the following resume {target_context}.

        Resume Content: 
        {resume_content}

        Please provide your analysis in a structured JSON format with the following keys:
        1. "score": An integer from 0-100.
        2. "pros": A list of strings identifying strong points.
        3. "cons": A list of strings identifying weaknesses or missing elements.
        4. "improvements": A list of specific actionable suggestions.
        5. "summary": A brief 2-sentence professional overview.

        Ensure the response is valid JSON only.
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json"
            }
        )

        # Cleanup
        os.remove(pdf_path)

        # Parse JSON response from LLM
        analysis_data = json.loads(response.text)
        return jsonify(analysis_data)

    except Exception as e:
        print(f"Server Error: {str(e)}")
        return jsonify({"error": "Failed to process the analysis. Please try again."}), 500

if __name__ == "__main__":
    app.run(debug=True, port=8080)