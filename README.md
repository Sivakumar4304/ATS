# 🚀 SKY-ATS — AI-Powered Resume Analyzer

SKY-ATS is a web-based **Applicant Tracking System (ATS)** built using **Flask** and **Google Gemini AI**.  
It analyzes a resume against a job description and provides an ATS-style evaluation including skill matching, gaps, and improvement suggestions.

---

## ✨ Features

- 📄 Upload resume in **PDF format**
- 🧠 AI-powered **resume parsing**
- 🧾 AI-powered **job description analysis**
- 📊 ATS-style comparison:
  - Match percentage
  - Matching skills
  - Missing skills
  - Strengths
  - Improvement suggestions
- 🌐 Simple and clean web interface
- 🔐 Secure API key handling using environment variables

---

## 🛠 Tech Stack

### Frontend
- HTML
- CSS
- JavaScript (Fetch API)

### Backend
- Python
- Flask

### AI / NLP
- Google Gemini (`google-genai` SDK)

### PDF Processing
- PyPDF2

---

ATS/
│── main.py
│
├── templates/
│ └── index.html
│
├── uploads/
│ └── (uploaded resumes)
│
└── README.md


---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Sivakumar4304/ATS.git
cd ATS
2️⃣ Create & Activate Conda Environment
conda create -n sky-ats python=3.10
conda activate sky-ats
3️⃣ Install Dependencies
pip install flask PyPDF2 google-genai
4️⃣ Set Gemini API Key (IMPORTANT)
Windows
set GEMINI_API_KEY=YOUR_GEMINI_API_KEY

macOS / Linux
export GEMINI_API_KEY=YOUR_GEMINI_API_KEY
5️⃣ Run the Application
python main.py


Open your browser and go to:

http://localhost:8080

🧪 How It Works

User uploads a resume PDF

User enters a job description

Resume text is extracted using PyPDF2

Google Gemini AI:

Parses resume details

Parses job description

Performs ATS-style matching

Results are returned and displayed on the UI

🔐 Security Notes

❌ Do NOT commit API keys to GitHub

✅ Always use environment variables

🚨 Revoke keys immediately if exposed

📌 Known Limitations

Model availability depends on Google Gemini account access

Resume text quality affects parsing accuracy

Designed primarily for learning and prototyping

🚀 Future Improvements

ATS score progress bar

Structured JSON outputs

Skill keyword highlighting

Resume improvement tips download

Cloud deployment (Render / Railway)

👨‍💻 Author

Sivakumar.Boda
B.Tech Student
Aspiring Full-Stack Developer & ML Engineer

⭐ Support

If you found this project helpful, consider giving it a ⭐ on GitHub!
## 📂 Project Structure

