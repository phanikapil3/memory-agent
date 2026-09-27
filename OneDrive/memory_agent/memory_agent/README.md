# Memory AI Agent

A simple, beginner-friendly demo of an AI agent that can **remember facts across conversations** and use them to give personalized answers — built with Python, Groq, Hindsight, and Streamlit.

## Overview

This project is a single-file Streamlit application that demonstrates the difference between a stateless AI conversation and one backed by persistent memory. You teach the agent a fact once, then ask it a question two different ways — with and without that memory — so you can see the difference directly.

## The Problem

Normal AI conversations are stateless. Every time you send a message to an LLM, it only sees what's in that single request. If you tell it your name and what you're learning today, and come back later with a new question, it has no idea who you are or what you told it before — unless you repeat everything yourself.

## The Solution

This project combines two separate pieces:

- **Hindsight** — a persistent memory service. It stores facts you tell it (`retain`) and can search them later (`recall`), independent of any particular LLM or conversation.
- **Groq** — a fast LLM API. It answers questions, but has no memory of its own between calls.

The app sits in between: it fetches relevant facts from Hindsight and hands them to Groq as context before asking it to answer. Groq itself never "remembers" anything — the app re-supplies the right memories on every request.

## Architecture / Data Flow

```
User
  │
  ▼
Streamlit UI (memory_agent.py)
  │
  ├── Save a fact ──────────────► Hindsight Cloud (retain)
  │
  └── Ask a question
        │
        ├── (With Memory) ──► Hindsight Cloud (recall) ──► relevant facts
        │                                                        │
        └──────────────────────────────────────────────────────►│
                                                                  ▼
                                                             Groq API
                                                          (chat completion)
                                                                  │
                                                                  ▼
                                                             Answer shown
                                                             in Streamlit
```

Hindsight Cloud is where memories are actually stored and recorded — nothing is saved locally on your machine. The app only ever holds memories temporarily, in memory (RAM), while building a prompt for Groq.

## Technologies

- **Python 3.10+**
- **Streamlit** — web UI
- **Groq API** — LLM responses (`llama-3.3-70b-versatile`)
- **Hindsight Cloud** — persistent memory storage and retrieval
- **python-dotenv** — loads API keys from a local `.env` file

## The Two Demonstrations

**❌ Without Memory**
Your message goes straight to Groq with no extra context. Since Groq knows nothing about you beyond that one message, the answer is generic.

**✅ With Hindsight Memory**
The app first calls Hindsight's `recall` to search for facts relevant to your question. Those facts are shown to you in an expandable section, and are also passed to Groq as background context, so the answer can be personalized.

## Project Structure

```
memory-agent-demo/
├── memory_agent.py      # Everything: Streamlit UI, Groq calls, Hindsight calls
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Requirements

- Python 3.10 or newer
- A Groq API key (free at [console.groq.com/keys](https://console.groq.com/keys))
- A Hindsight Cloud account and API key (free at [hindsight.vectorize.io](https://hindsight.vectorize.io))

## Setup on Windows

1. **Open PowerShell (or Command Prompt) and navigate to the project folder:**

   ```powershell
   cd path\to\memory-agent-demo
   ```

2. **Create and activate a virtual environment:**

   ```powershell
   python -m venv venv
   venv\Scripts\activate
   ```

   If PowerShell blocks script execution, run this once first:
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   ```

3. **Install the required packages:**

   ```powershell
   pip install -r requirements.txt
   ```

## Configure the .env File

1. Copy `.env.example` to a new file named `.env`:

   ```powershell
   copy .env.example .env
   ```

2. Open `.env` in a text editor and fill in your real keys:

   ```
   GROQ_API_KEY=your_actual_groq_key
   HINDSIGHT_API_URL=https://api.hindsight.vectorize.io
   HINDSIGHT_API_KEY=your_actual_hindsight_key
   ```

3. Save the file. `.env` is already listed in `.gitignore`, so it will never be committed to version control.

## Running the Application

```powershell
streamlit run memory_agent.py
```

This opens the app in your browser, usually at `http://localhost:8501`.

## Demo Walkthrough

1. In the **"Remember something"** box, enter:
   ```
   My name is Rahul. I am a CSE student learning Python.
   ```
   Click **"Save to memory"**.

2. In the **"Without Memory"** section, ask:
   ```
   What should I practice today?
   ```
   You'll get a generic study suggestion — the AI doesn't know anything about you.

3. In the **"With Hindsight Memory"** section, ask the same question:
   ```
   What should I practice today?
   ```
   This time, the app first recalls your saved fact ("Rahul, CSE student learning Python") and passes it to Groq, so the suggestion is tailored to a Python beginner. You can see exactly what was recalled in the expandable "Memories retrieved from Hindsight" section.

## Troubleshooting

**"Missing HINDSIGHT_API_URL or HINDSIGHT_API_KEY" / "Error contacting Groq"**
- Make sure you created `.env` (not just `.env.example`) in the project's root folder.
- Double-check there are no extra spaces or quotes around your keys in `.env`.
- Restart the Streamlit app after editing `.env` — environment variables are only loaded on startup.

**No memories are being recalled even after saving a fact**
- Make sure the "Save to memory" step actually returned a success message before asking a related question.
- Try asking a question that's clearly related in wording to the fact you saved.

**Connection errors to Hindsight or Groq**
- Check your internet connection.
- Confirm your API keys are valid and haven't expired or been revoked in the Groq / Hindsight dashboards.
- Confirm `HINDSIGHT_API_URL` is exactly `https://api.hindsight.vectorize.io` (no trailing slash typos).

**`streamlit`, `groq`, or `hindsight_client` module not found**
- Make sure your virtual environment is activated (`venv\Scripts\activate`) before running `pip install` or `streamlit run`.
- Confirm the install completed without errors: `pip install -r requirements.txt`.
