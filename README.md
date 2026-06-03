# CX Flow: Enterprise Customer Experience Automation 💬⚡

**CX Flow** is a robust, AI-powered customer support automation platform designed to ingest, analyze, and autonomously resolve enterprise support interactions. 

Moving beyond standard chatbots, this platform reads incoming customer emails, extracts deep intent and sentiment, securely scans multimodal attachments, and orchestrates specialized AI agents to handle the workload.

![Dashboard Preview](https://via.placeholder.com/1200x600?text=CX+Flow+Command+Center)

## 🚀 Key Features

*   **Live Email Ingestion (Gmail API):** Background asynchronous task that securely authenticates via OAuth2 and polls live inbox data without blocking the main event loop.
*   **LangGraph Orchestration Engine:** Multi-step agentic workflow that routes customer interactions dynamically based on LLM outputs (e.g., specific agents for Retention, Frustration, Security, and Billing).
*   **Gemini Vision & Multimodal Extraction:** Leverages Google's Gemini 2.5 Flash to extract high-fidelity JSON (intent, sentiment, priority) even from unstructured emails containing screenshots or PDFs.
*   **"Zero Trust" Secure Attachments:** Robust pre-filtering pipeline that checks file sizes, enforces MIME type allowlists, and inspects true "magic bytes". Valid attachments are securely stored in AWS S3 and analyzed by the AI.
*   **Human-in-the-Loop Gateway:** Low-confidence AI analyses or high-risk intents (legal, compliance) are securely halted in a "Draft Pending Approval" state for human review.
*   **Premium Web Command Center:** A modern React SPA utilizing a clean Glassmorphism aesthetic, custom typography, dynamic timeframe filtering, and color-coded SLA tracking.

## 🛠️ Tech Stack

*   **Backend:** Python 3, FastAPI, SQLAlchemy, Uvicorn
*   **AI & Graph:** LangGraph, Google Gemini API (`google-genai`), LangChain Core
*   **Frontend:** React, Vite, Vanilla CSS Modules
*   **Database:** SQLite (MVP) / Extensible to PostgreSQL
*   **Storage & Security:** AWS S3 (`boto3`), `python-magic`, PyJWT

## ⚙️ Local Development Setup

### 1. Prerequisites
*   Node.js (v18+)
*   Python 3.10+
*   AWS Free Tier Account (for S3 attachments)
*   Google Cloud Console Project (for Gmail API & Gemini AI credentials)

### 2. Backend Setup
1. Open a terminal and navigate to the `backend` directory.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up your `.env` file by copying the example:
   ```bash
   cp .env.example .env
   ```
   *Fill in your Gemini API Key, AWS Credentials, JWT Secret, etc.*
5. Initialize the SQLite Database:
   ```bash
   python -c "from models.database import engine; from models.interaction import Base; from models.attachment import Attachment; Base.metadata.create_all(bind=engine)"
   ```
6. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

### 3. Frontend Setup
1. Open a new terminal and navigate to the `frontend` directory.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```

### 4. Gmail Authentication (OAuth2)
To allow the backend to poll emails, you must generate a `token.json` file.
1. Ensure your Google Workspace credentials are saved as `credentials.json` in the `backend` directory.
2. Run the authentication script:
   ```bash
   python scripts/setup_gmail_auth.py
   ```
3. Complete the web flow to grant read/write access.

## 🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## 📄 License
[MIT](https://choosealicense.com/licenses/mit/)
