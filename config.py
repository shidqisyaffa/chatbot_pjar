import os
import streamlit as st
from dotenv import load_dotenv

# Try to load local .env file (for local development)
load_dotenv()

def get_env_or_secret(key: str, default: str = None) -> str:
    """
    Get a configuration value from environment variables (os.environ)
    or Streamlit Secrets (st.secrets). If not found, returns the default.
    """
    # 1. Check OS environment variables
    val = os.getenv(key)
    if val is not None:
        return val

    # 2. Check Streamlit secrets
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        # st.secrets might raise an exception if it's not initialized
        pass

    return default

# App Settings
APP_TITLE = get_env_or_secret("APP_TITLE", "Chatbot Pemrograman Jaringan")
LOG_LEVEL = get_env_or_secret("LOG_LEVEL", "INFO")

raw_debug = get_env_or_secret("DEBUG", "False")
if isinstance(raw_debug, bool):
    DEBUG = raw_debug
else:
    DEBUG = str(raw_debug).lower() in ("true", "1", "yes")

# Database Settings
DATABASE_URL = get_env_or_secret("DATABASE_URL")

# LLM Backend Settings
LLM_BASE_URL = get_env_or_secret("LLM_BASE_URL", "http://127.0.0.1:1234/v1")
MODEL_NAME = get_env_or_secret("MODEL_NAME", "gemma-4-e2b")
API_KEY = get_env_or_secret("API_KEY", "lm-studio")

raw_temp = get_env_or_secret("TEMPERATURE", 0.3)
try:
    TEMPERATURE = float(raw_temp)
except (ValueError, TypeError):
    TEMPERATURE = 0.3

raw_tokens = get_env_or_secret("MAX_TOKENS", 4096)
try:
    MAX_TOKENS = int(raw_tokens)
except (ValueError, TypeError):
    MAX_TOKENS = 4096

def validate_config():
    """
    Validates essential configurations.
    Returns a dictionary of error messages if validation fails, or empty dict if OK.
    """
    errors = {}
    if not DATABASE_URL:
        errors["DATABASE_URL"] = "DATABASE_URL is not set. Please specify it in .env or Streamlit Secrets."
    if not LLM_BASE_URL:
        errors["LLM_BASE_URL"] = "LLM_BASE_URL is not set. Please specify it in .env or Streamlit Secrets."
    return errors
