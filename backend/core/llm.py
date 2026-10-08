import os
from typing import List
from langchain_groq import ChatGroq

GROQ_MODELS = [
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b",
    "qwen/qwen3.8-27b",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
]


def get_groq_llm(temperature: float = 0.1, model_kwargs: dict = None) -> ChatGroq:
    """
    Attempts to initialize ChatGroq using preferred active model list.
    Returns ChatGroq instance for the first model in the configuration.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set")

    kwargs = {"temperature": temperature, "groq_api_key": api_key}
    if model_kwargs:
        kwargs["model_kwargs"] = model_kwargs

    # Use primary working model openai/gpt-oss-20b
    return ChatGroq(model=GROQ_MODELS[0], **kwargs)

