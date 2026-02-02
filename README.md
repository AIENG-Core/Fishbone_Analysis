# AI-Powered Fishbone Root Cause Analysis (RCA)

An **AI-assisted Root Cause Analysis system** that automatically suggests **Fishbone (Ishikawa) causes**, generates **neutral, explainable descriptions**, and **learns over time from human edits**.

This project is designed for **industrial safety, EHS, and incident investigation workflows**, where **human judgment is mandatory** and AI acts as a **decision-support system**, not a decision-maker.

---

## 🚀 Key Features

- 🧠 **AI-assisted cause identification**
  - Uses semantic similarity to suggest relevant Fishbone causes
- ✍️ **Automatic cause descriptions**
  - In-house LLM (Ollama) generates neutral, professional explanations
- 👨‍🔧 **Human-in-the-loop**
  - Users can add, remove, and edit causes & descriptions
- 📈 **Learning over time**
  - The system improves cause relevance based on user decisions
- 📊 **Fishbone (Ishikawa) diagram**
  - Live visual representation of selected causes
- 🏠 **Fully in-house**
  - No cloud APIs, no data leakage, CPU-only friendly
- 🧩 **Modular architecture**
  - Easy to extend (5-Why, dashboards, approvals, analytics)

---

## 🧠 How the AI Works (Important)

This system uses **two separate AI components**, each with a clear responsibility:

### 1️⃣ Cause Selection & Learning Model (Trainable)
- Sentence embeddings + similarity scoring
- Category thresholds
- Learns from user actions:
  - Accepted causes → reinforced
  - Removed causes → penalized
  - Manually added causes → promoted
- **This is the only part that trains over time**

### 2️⃣ Description Generator (LLM – NOT trained)
- Uses a local LLM via **Ollama** (e.g. Mistral 7B / Qwen 2.5)
- Generates short, neutral explanations for each cause
- Does **not** decide causes
- Does **not** learn from data
- Acts only as a writing assistant

👉 This separation ensures **accuracy, explainability, and audit safety**.

---

---

## 🖥️ Tech Stack

- **Python 3.10+**
- **Sentence Transformers** (`all-MiniLM-L6-v2`)
- **Scikit-learn**
- **Ollama** (local LLM runtime)
- **Mistral 7B / Qwen 2.5** (quantized, CPU-friendly)
- **FastAPI** (backend API)
- **Streamlit** (frontend / prototyping)
- **Graphviz** (Fishbone diagram)

---

## ⚙️ Setup Instructions

### 1️⃣ Create virtual environment

python -m venv .fishbone_env

source .fishbone_env/bin/activate  # Linux/Mac


.fishbone_env\Scripts\activate     # Windows


pip install -r requirements.txt


Install Ollama (Required)
ollama --version

 Pull an LLM model (choose one)
ollama pull qwen2.5:3b-instruct-q4_K_M

🔹 Run the frontend (local development)
streamlit run app.py


🔹 Run the backend API (production-ready)
uvicorn api:app --reload




