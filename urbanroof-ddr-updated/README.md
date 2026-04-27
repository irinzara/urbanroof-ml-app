# 🏠 UrbanRoof DDR Report Generator
**AI-Powered Detailed Diagnostic Report System**

---

## 📌 What This Does
This system reads two PDF documents:
1. **Inspection Report** — site visual observations
2. **Thermal Images Report** — IR camera temperature readings

And automatically generates a **professional DDR (Detailed Diagnostic Report)** with:
- Property Issue Summary
- Area-wise Observations (with image references)
- Probable Root Cause
- Severity Assessment
- Recommended Actions
- Missing/Unclear Information

---

## 🛠️ Tech Stack (100% Free)
| Tool | Purpose |
|------|---------|
| Python 3.10+ | Core language |
| PyMuPDF (fitz) | PDF text + image extraction |
| Google Gemini 1.5 Flash | AI report generation (FREE: 1500/day) |
| Streamlit | Web app interface |
| Streamlit Community Cloud | FREE live hosting |
| GitHub | Code storage |

---

## 🚀 Setup Instructions

### Step 1: Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/urbanroof-ddr.git
cd urbanroof-ddr
```

### Step 2: Create virtual environment
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### Step 3: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Get FREE Gemini API Key
1. Go to https://aistudio.google.com
2. Sign in with Google
3. Click **Get API Key** → **Create API Key**
4. Copy the key

### Step 5: Run locally
```bash
streamlit run app.py
```
Opens at: http://localhost:8501

---

## 🌐 Deploy to Streamlit Cloud (Get Live Link)

1. Push code to GitHub
2. Go to https://share.streamlit.io
3. Click **New App**
4. Select your GitHub repo
5. Main file: `app.py`
6. Click **Deploy**
7. Your live link will be: `https://YOUR_APP.streamlit.app`

**Note:** Enter your Gemini API key in the app sidebar (not hardcoded for security).

---

## 📁 Project Structure
```
urbanroof-ddr/
├── app.py              ← Main web application (run this)
├── extractor.py        ← PDF text + image extraction
├── generator.py        ← Gemini AI report generation
├── requirements.txt    ← Python dependencies
├── README.md           ← This file
├── .gitignore          ← Files to exclude from git
├── uploads/            ← Temp storage for uploaded PDFs
└── output/
    └── images/         ← Extracted images stored here
```

---

## ⚠️ Important Notes
- API key is entered in the UI — never hardcoded in files
- System works on any similar inspection + thermal PDF pair
- If Gemini is busy, wait 30 seconds and try again
- Free tier: 1500 requests/day (more than enough for this)

---

## 👨‍💻 Built For
UrbanRoof Pvt Ltd — AI/ML Engineer Assignment  
*Demonstrates: AI workflow design, PDF processing, prompt engineering, web deployment*
