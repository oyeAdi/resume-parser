from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import os
import fitz  # PyMuPDF
import docx
import google.generativeai as genai

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load Gemini model
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# Sample job description
JOB_DESCRIPTION = """
We are looking for a backend Java developer with at least 3 years of experience in Spring Boot microservices,
RESTful APIs, PostgreSQL, and Kafka. Experience with CI/CD pipelines and knowledge of Docker is a plus.
"""

# Utility to extract text
def extract_text(file):
    filename = file.filename
    if filename.endswith(".pdf"):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        return "\n".join(page.get_text() for page in doc)
    elif filename.endswith(".docx"):
        doc = docx.Document(file)
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)
    elif filename.endswith(".txt"):
        return file.read().decode("utf-8")
    else:
        return ""

# Route to handle file upload and Gemini check
@app.route("/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        resume_text = extract_text(file)

        prompt = f"""Compare the following resume with the job description below. 
If the resume aligns well with the requirements, respond ONLY with: "Shortlisted". 
Otherwise, respond ONLY with: "Rejected".

Job Description:
{JOB_DESCRIPTION}

Resume:
{resume_text}
"""
        response = model.generate_content(prompt)
        result = response.text.strip()
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run app
if __name__ == "__main__":
    app.run(debug=True)
