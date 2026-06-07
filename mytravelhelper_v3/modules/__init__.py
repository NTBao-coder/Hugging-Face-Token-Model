"""Core modules for the MyTravelHelper Streamlit application."""

import os
from pathlib import Path
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def load_environment() -> None:
    """Load the .env file from project root."""
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        load_dotenv(env_path)

def get_hf_token() -> str | None:
    """Retrieve the Hugging Face token from environment variables."""
    load_environment()
    return os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN")

def get_inference_client() -> InferenceClient | None:
    """Instantiate a Hugging Face InferenceClient if a token is present."""
    token = get_hf_token()
    if token:
        return InferenceClient(token=token)
    return None
