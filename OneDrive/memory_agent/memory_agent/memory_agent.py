"""
Memory AI Agent - single-file Streamlit demo.

Shows an AI agent with and without persistent memory:
- Without Memory: Groq answers using only the current message.
- With Hindsight Memory: Hindsight recalls relevant past facts first,
  and those facts are given to Groq so it can personalize its answer.

All app logic (UI, Groq calls, Hindsight calls) lives in this one file
to keep the project simple for a beginner demo.
"""

import os

import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from hindsight_client import Hindsight

# ---------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------

# Load GROQ_API_KEY, HINDSIGHT_API_URL, HINDSIGHT_API_KEY from .env
load_dotenv()

# A fast, currently-available Groq model - good for quick demo responses.
GROQ_MODEL = "openai/gpt-oss-120b"

# A single fixed "bank" (memory space) for this simple single-user prototype.
# Hindsight creates the bank automatically the first time you retain to it,
# so no separate setup step is needed.
HINDSIGHT_BANK_ID = "memory-agent-demo"


# ---------------------------------------------------------------------
# Hindsight memory functions
# ---------------------------------------------------------------------

def get_hindsight_client():
    """
    Create a Hindsight client connected to Hindsight Cloud.

    Reads the API URL and API key from environment variables so no
    secrets are ever hard-coded in the source file.
    """
    api_url = os.environ.get("HINDSIGHT_API_URL")
    api_key = os.environ.get("HINDSIGHT_API_KEY")

    if not api_url or not api_key:
        raise RuntimeError(
            "Missing HINDSIGHT_API_URL or HINDSIGHT_API_KEY. "
            "Check your .env file."
        )

    return Hindsight(base_url=api_url, api_key=api_key)


def store_memory(text: str):
    """
    Save a fact to Hindsight (the "retain" operation).

    Returns a (success, message) tuple so the UI can show what happened
    without the whole app crashing if something goes wrong.
    """
    if not text or not text.strip():
        return False, "Nothing to store - please enter a fact first."

    try:
        client = get_hindsight_client()
        client.retain(bank_id=HINDSIGHT_BANK_ID, content=text.strip())
        return True, "Memory stored successfully."
    except Exception as e:
        return False, f"Failed to store memory: {e}"


def recall_memories(query: str) -> str:
    """
    Search Hindsight for facts relevant to the given query
    (the "recall" operation).

    Returns a single string combining the relevant memories, ready to
    be inserted into a prompt sent to the LLM. Returns an empty string
    if nothing is found or if an error occurs, so the calling code can
    fall back to a "no memory" behavior gracefully.
    """
    if not query or not query.strip():
        return ""

    try:
        client = get_hindsight_client()
        results = client.recall(bank_id=HINDSIGHT_BANK_ID, query=query.strip())

        # results.results is a list of recalled facts; each has a .text field
        facts = [r.text for r in results.results]

        if not facts:
            return ""

        return "\n".join(f"- {fact}" for fact in facts)

    except Exception as e:
        st.warning(f"Could not recall memories: {e}")
        return ""


# ---------------------------------------------------------------------
# Groq LLM function
# ---------------------------------------------------------------------

def get_response(user_message: str, memory_context: str = "") -> str:
    """
    Send a message to Groq and return the model's text reply.

    If memory_context is provided, it's added as a system message so
    the model can personalize its answer. If it's empty, the model
    only sees the user's message (a plain, generic answer).
    """
    if not user_message or not user_message.strip():
        return "Please enter a message."

    try:
        # Groq() automatically reads the GROQ_API_KEY environment variable.
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

        messages = []

        # Only add a system message when we actually have memory to use.
        if memory_context:
            messages.append({
                "role": "system",
                "content": (
                    "You are a helpful assistant. Use the following known "
                    "facts about the user, if relevant, to personalize your "
                    "answer:\n" + memory_context
                ),
            })

        messages.append({"role": "user", "content": user_message.strip()})

        chat_completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
        )

        return chat_completion.choices[0].message.content

    except Exception as e:
        return f"Error contacting Groq: {e}"


# ---------------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------------

st.set_page_config(page_title="Memory AI Agent", page_icon="🧠")
st.title("🧠 Memory AI Agent")
st.caption(
    "A simple demo of an AI agent that can remember facts across "
    "conversations using Hindsight, and answer questions using Groq."
)

# --- Section 0: Remember something ---
st.header("💾 Remember something")
st.write(
    "Teach the agent a fact about you. Example: "
    "\"My name is Rahul. I am a CSE student learning Python.\""
)

fact_input = st.text_input("Fact to remember", key="fact_input")

if st.button("Save to memory"):
    success, message = store_memory(fact_input)
    if success:
        st.success(message)
    else:
        st.error(message)

st.divider()

# --- Section A: Without Memory ---
st.header("❌ Without Memory")
st.write("This sends your message straight to Groq. Hindsight is not used here.")

no_memory_question = st.text_input("Ask something", key="no_memory_question")

if st.button("Get answer (Without Memory)"):
    if no_memory_question.strip():
        with st.spinner("Thinking..."):
            answer = get_response(no_memory_question)
        st.markdown("**AI response:**")
        st.write(answer)
    else:
        st.warning("Please enter a question first.")

st.divider()

# --- Section B: With Hindsight Memory ---
st.header("✅ With Hindsight Memory")
st.write(
    "This first recalls relevant facts from Hindsight, then gives them "
    "to Groq so the answer can be personalized."
)

memory_question = st.text_input("Ask something", key="memory_question")

if st.button("Get answer (With Hindsight Memory)"):
    if memory_question.strip():
        with st.spinner("Recalling memories..."):
            memory_context = recall_memories(memory_question)

        with st.spinner("Thinking..."):
            answer = get_response(memory_question, memory_context=memory_context)

        st.markdown("**AI response:**")
        st.write(answer)

        with st.expander("🔍 Memories retrieved from Hindsight"):
            if memory_context:
                st.text(memory_context)
            else:
                st.write("No relevant memories were found.")
    else:
        st.warning("Please enter a question first.")
