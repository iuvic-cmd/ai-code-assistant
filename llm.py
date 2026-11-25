import streamlit as st
from openai import OpenAI

MODEL = "gpt-4o-mini"

def _client():
    # ключ берём из Secrets (Streamlit Cloud)
    api_key = st.secrets.get("OPENAI_API_KEY") if hasattr(st, "secrets") else None
    return OpenAI(api_key=api_key)

def stream_chat(system: str, messages: list):
    """messages: список {"role": "user"/"assistant", "content": str}"""
    client = _client()
    stream = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system}] + messages,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
