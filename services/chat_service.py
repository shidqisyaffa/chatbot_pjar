import time
import logging
from typing import Generator

from services.prompts import SYSTEM_PROMPT, REJECTION_MESSAGE
from services.validators import validate_domain_keyword
from services.llm_service import stream_chat_completion
from services.history_service import save_message
from services.logging_service import log_request

logger = logging.getLogger(__name__)

def estimate_tokens(text: str) -> int:
    """
    Rough estimate of tokens using word count (approx. 1.3 tokens per word).
    """
    if not text:
        return 0
    words = len(text.split())
    return int(words * 1.3) + 1

def handle_chat_message(
    session_uuid: str,
    prompt: str,
    history: list[dict]
) -> Generator[str, None, None]:
    """
    Handles a user's prompt by applying dual-domain validation,
    querying the LLM with streaming, persisting history, and logging latency.
    
    Args:
        session_uuid: Active chat session UUID.
        prompt: User's query.
        history: Existing messages list in the active session.
        
    Yields:
        str: Text chunks of the response.
    """
    start_time = time.time()
    
    # -------------------------------------------------------------
    # LAYER 1: Keyword Validation (Local Check)
    # -------------------------------------------------------------
    is_valid = validate_domain_keyword(prompt)
    
    if not is_valid:
        # Rejection is immediate. No request is sent to the LLM backend.
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Save both prompt and rejection message to history
        save_message(session_uuid=session_uuid, role="user", message=prompt, token_usage=estimate_tokens(prompt), response_time=0.0)
        save_message(session_uuid=session_uuid, role="assistant", message=REJECTION_MESSAGE, token_usage=estimate_tokens(REJECTION_MESSAGE), response_time=latency_ms / 1000.0)
        
        # Log request as rejected
        log_request(
            session_uuid=session_uuid,
            request=prompt,
            response=REJECTION_MESSAGE,
            latency_ms=latency_ms,
            status="rejected"
        )
        
        # Yield the rejection message slowly or at once
        yield REJECTION_MESSAGE
        return

    # -------------------------------------------------------------
    # LAYER 2: System Prompt & Chat Completion
    # -------------------------------------------------------------
    
    # Save the user's message to database first
    save_message(session_uuid=session_uuid, role="user", message=prompt, token_usage=estimate_tokens(prompt), response_time=0.0)
    
    # Format messages for the LLM
    llm_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Append chat history (only the last 20 messages to prevent context overflow)
    for msg in history[-20:]:
        llm_messages.append({"role": msg["role"], "content": msg["message"]})
        
    # Append the current prompt
    llm_messages.append({"role": "user", "content": prompt})
    
    full_response = ""
    status = "success"
    
    try:
        # Stream the completion from LLM service
        generator = stream_chat_completion(llm_messages)
        for chunk in generator:
            full_response += chunk
            yield chunk
            
    except Exception as e:
        status = "failed"
        error_message = "🔴 Maaf, terjadi kesalahan koneksi ke model AI. Pastikan server LM Studio atau terowongan ngrok Anda aktif."
        full_response = error_message
        yield error_message
        logger.error(f"Error during LLM streaming: {e}")
        
    # Calculate response metrics
    end_time = time.time()
    latency_ms = int((end_time - start_time) * 1000)
    response_time_sec = end_time - start_time
    
    # Save assistant message to database
    save_message(
        session_uuid=session_uuid,
        role="assistant",
        message=full_response,
        token_usage=estimate_tokens(full_response),
        response_time=response_time_sec
    )
    
    # Log request transaction to request_logs
    log_request(
        session_uuid=session_uuid,
        request=prompt,
        response=full_response,
        latency_ms=latency_ms,
        status=status
    )
