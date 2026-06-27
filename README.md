# 🎓 College Assistant Chatbot using LLM & FAQ

An AI-powered College Assistant Chatbot that provides instant responses to students' queries regarding admissions, courses, fees, placements, library, timetable, and other college-related information.

The chatbot first searches a predefined FAQ knowledge base for accurate answers. If no relevant answer is found, it uses a Large Language Model (LLM) to generate a helpful response.

---

## 🚀 Features

* 📚 College FAQ Knowledge Base
* 🤖 AI-powered responses using LLM
* 🔍 Semantic search using embeddings
* 💬 Interactive Streamlit interface
* ⚡ FastAPI backend
* 🛡️ Environment variable support using `.env`
* 📂 Easy-to-update FAQ dataset

---

## 🏗️ Project Structure

```text
.
├── admin_app.py          # Admin interface
├── client_app.py         # Streamlit chatbot UI
├── server.py             # FastAPI backend
├── faqs.json             # FAQ knowledge base
├── requirements.txt      # Python dependencies
├── .env                  # API keys (not included in public repositories)
├── README.md
└── venv/
```

---

## 🛠️ Technologies Used

* Python
* FastAPI
* Streamlit
* OpenAI / Gemini API
* JSON
* FAISS / Vector Search (if used)
* Sentence Embeddings
* dotenv

---

## 📋 Prerequisites

* Python 3.10+
* pip
* Virtual Environment (recommended)

---

## ⚙️ Installation

### Clone the repository

```bash
git clone https://github.com/AkashVH5500/<repository-name>.git

cd <repository-name>
```

### Create Virtual Environment

Windows

```bash
python -m venv venv
venv\Scripts\activate
```

Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create a `.env` file in the project root.

Example:

```env
OPENAI_API_KEY=your_api_key
```

or

```env
GEMINI_API_KEY=your_api_key
```

---

## ▶️ Run the Backend

```bash
uvicorn server:app --reload
```

Backend URL:

```
http://127.0.0.1:8000
```

---

## ▶️ Run the Chatbot

```bash
streamlit run client_app.py
```

The Streamlit application will open automatically in your browser.

---

## 📂 FAQ Dataset

The chatbot reads data from:

```text
faqs.json
```

You can add new categories and questions by editing this file.

Example:

```json
{
  "admission": [
    {
      "question": "What is the admission process?",
      "answer": "Admissions are based on..."
    }
  ]
}
```

---

## 📸 Screenshots

Add screenshots of:

* Home Page
* Chat Interface
* Admin Dashboard

Example:

```text
images/chatbot.png
images/admin.png
```

---

## Future Improvements

* Student Login
* Voice Assistant
* Multi-language Support
* PDF Document Search
* Database Integration
* RAG (Retrieval-Augmented Generation)
* Chat History
* Authentication

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch

```bash
git checkout -b feature-name
```

3. Commit changes

```bash
git commit -m "Added new feature"
```

4. Push to GitHub

```bash
git push origin feature-name
```

5. Open a Pull Request

---

## 📄 License

This project is intended for educational and learning purposes.

---

## 👨‍💻 Author

**Akash V Hiremath**

* GitHub: https://github.com/AkashVH5500

---
