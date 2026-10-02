import os
from typing import List
from langchain_groq import ChatGroq

GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "llama-3.1-8b-instant",
    "llama3-70b-8192",
]


def get_groq_llm(temperature: float = 0.1, model_kwargs: dict = None) -> ChatGroq:
    """
    Attempts to initialize ChatGroq using preferred model list.
    Returns ChatGroq instance for the first available model.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set")

    kwargs = {"temperature": temperature, "groq_api_key": api_key}
    if model_kwargs:
        kwargs["model_kwargs"] = model_kwargs

    last_err = None
    for model_name in GROQ_MODELS:
        try:
            return ChatGroq(model=model_name, **kwargs)
        except Exception as e:
            last_err = e
            continue

    # Fallback to default if loop completes
    return ChatGroq(model="llama-3.1-8b-instant", **kwargs)
