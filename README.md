# College Assistant Chatbot

A local college-information chatbot built with FastAPI, Streamlit and the Gemini API. It retrieves semantically similar entries from a JSON FAQ knowledge base and supplies those entries as context to Gemini when composing a response.

This repository is an educational prototype. Verify the FAQ content against current official college sources before using it to answer real student questions.

## Features

- FAQ knowledge base stored in faqs.json
- Semantic FAQ retrieval using Gemini embeddings
- Gemini-generated responses using retrieved FAQ context
- FastAPI endpoints for chat and FAQ management
- Streamlit student chat interface
- Optional Streamlit admin interface for adding, editing and deleting FAQs
- Environment-based API key and admin password configuration

## Stack

- Python
- FastAPI and Uvicorn
- Streamlit
- Google Generative AI Python SDK
- NumPy
- Requests
- python-dotenv

## Project structure

~~~text
ai-college-chatbot/
├── admin_app.py
├── client_app.py
├── server.py
├── faqs.json
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
~~~

## Setup

Use Python 3.10 or later.

~~~bash
git clone https://github.com/AkashVH5500/ai-college-chatbot.git
cd ai-college-chatbot

python -m venv .venv
~~~

Activate the environment:

- macOS / Linux: source .venv/bin/activate
- Windows PowerShell: .venv\Scripts\Activate.ps1

Install dependencies:

~~~bash
python -m pip install --upgrade pip
pip install -r requirements.txt
~~~

Create your local environment file:

~~~bash
cp .env.example .env
~~~

Edit .env and set your own Gemini API key. Set a strong ADMIN_PASSWORD only if you plan to run the admin interface. Never commit .env.

## Run the application

Start the backend in terminal 1:

~~~bash
uvicorn server:app --reload
~~~

The API is available at http://127.0.0.1:8000; interactive API documentation is at http://127.0.0.1:8000/docs.

Start the student interface in terminal 2:

~~~bash
streamlit run client_app.py
~~~

Start the admin interface in a separate terminal only after setting ADMIN_PASSWORD:

~~~bash
streamlit run admin_app.py
~~~

## API endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | /health | Basic service health |
| GET | /faqs | List FAQ entries |
| POST | /faqs | Add an FAQ |
| PUT | /faqs/{faq_id} | Update an FAQ |
| DELETE | /faqs/{faq_id} | Delete an FAQ |
| POST | /chat | Retrieve FAQ context and generate a response |

## FAQ data

The knowledge base is stored in faqs.json as a JSON object containing a faqs array. Each entry has a question and answer. The API assigns an ID when loading entries that do not already have one.

Keep this content accurate and current. Replace sample or placeholder contact details, fees, placement statistics and schedules with verified official information before sharing the chatbot with students.

## Design notes and limitations

- FAQ entries and embeddings are held in process memory; this is a small local prototype, not a multi-user production service.
- Gemini is called for embeddings and response generation, so an API key and network connection are required.
- The admin password is a basic local safeguard, not a substitute for production authentication, authorisation, rate limiting or audit logging.
- Review generated responses against official college information. Do not treat model output as an authoritative college announcement.
- The current CORS and local service configuration should be reviewed before any public deployment.

## Author

Akash V Hiremath — [GitHub](https://github.com/AkashVH5500)


## Security notes

- The Gemini integration uses the supported Google GenAI Python SDK (`google-genai`) and the current stable model identifiers configured through environment variables. Google marks the previous `google-generativeai` Python package as deprecated and recommends migrating to `google-genai`. See the [official migration guide](https://ai.google.dev/gemini-api/docs/migrate).
- FAQ create, update and delete endpoints require an `Authorization: Bearer` token configured as `ADMIN_API_TOKEN`. The Streamlit admin interface reads the token from the server-side `.env`; it is not sent to the student interface.
- The separate `ADMIN_PASSWORD` only gates the local Streamlit admin screen. Do not deploy this prototype publicly without stronger authentication, HTTPS, rate limiting, audit logs and protected secret storage.
- The FAQ dataset contains sample content. Placement statistics, contact details and hostel fees are intentionally not stated as verified facts; confirm all college information through official channels.
