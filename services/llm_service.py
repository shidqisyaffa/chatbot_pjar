import time
import requests
import logging
from openai import OpenAI

import config

logger = logging.getLogger(__name__)

def get_openai_client() -> OpenAI:
    """
    Dynamically initializes and returns an OpenAI client pointing to the
    configured LM Studio / ngrok base URL.
    """
    return OpenAI(
        base_url=config.LLM_BASE_URL,
        api_key=config.API_KEY
    )

def check_llm_status() -> tuple[bool, str]:
    """
    Checks the status of the LM Studio API endpoint.
    
    Returns:
        (bool, str): (True, model_name) if connected, (False, error_message) if disconnected.
    """
    if not config.LLM_BASE_URL:
        return False, "LLM_BASE_URL is not configured"
        
    try:
        # Strip trailing slashes and append /models endpoint
        base_url = config.LLM_BASE_URL.rstrip('/')
        url = f"{base_url}/models"
        
        # Perform health check
        response = requests.get(url, timeout=4)
        if response.status_code == 200:
            data = response.json()
            model_name = config.MODEL_NAME
            # Attempt to retrieve model ID from the endpoint payload
            if "data" in data and isinstance(data["data"], list) and len(data["data"]) > 0:
                model_name = data["data"][0].get("id", config.MODEL_NAME)
            return True, model_name
        else:
            return False, f"HTTP Error {response.status_code}"
    except requests.exceptions.RequestException as e:
        logger.error(f"LM Studio health check failed: {e}")
        return False, "Disconnected (check ngrok or LM studio)"
    except Exception as e:
        logger.error(f"Unexpected health check error: {e}")
        return False, f"Disconnected ({str(e)})"

def stream_chat_completion(messages: list[dict], max_retries: int = 2, delay: float = 1.5):
    """
    Streams responses from the OpenAI-compatible LM Studio backend.
    Includes a simple retry mechanism.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys.
        max_retries: Maximum number of retries if connection drops.
        delay: Time to wait (in seconds) between retries.
    """
    client = get_openai_client()
    
    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=config.MODEL_NAME,
                messages=messages,
                temperature=config.TEMPERATURE,
                max_tokens=config.MAX_TOKENS,
                stream=True
            )
            
            for chunk in response:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, "content") and delta.content is not None:
                        yield delta.content
            return # Successfully complete streaming
            
        except Exception as e:
            logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries:
                time.sleep(delay)
            else:
                logger.error(f"All connection attempts to LLM failed: {e}")
                raise e
