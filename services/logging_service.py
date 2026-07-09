import logging
from datetime import datetime
from database import get_db_session
from models import RequestLog

logger = logging.getLogger(__name__)

def log_request(session_uuid: str, request: str, response: str, latency_ms: int, status: str) -> bool:
    """
    Logs a chat request-response cycle into the database.
    
    Args:
        session_uuid: The active chat session UUID.
        request: The user's prompt text.
        response: The bot's text response (or rejection message).
        latency_ms: The response latency in milliseconds.
        status: The transaction status ('success', 'failed', 'rejected').
        
    Returns:
        bool: True if logged successfully, False otherwise.
    """
    try:
        with get_db_session() as session:
            log_entry = RequestLog(
                session_uuid=session_uuid,
                request=request,
                response=response,
                latency_ms=latency_ms,
                status=status,
                created_at=datetime.utcnow()
            )
            session.add(log_entry)
            logger.info(f"Logged request for session {session_uuid} with status: {status}")
            return True
    except Exception as e:
        logger.error(f"Error creating request log: {e}")
        return False

def get_logs_summary() -> dict:
    """
    Retrieves network dashboard metrics directly from the logs.
    Returns:
        dict: Containing aggregated metrics.
    """
    try:
        with get_db_session() as session:
            from sqlalchemy import func
            
            total_requests = session.query(func.count(RequestLog.id)).scalar() or 0
            
            # Count success and failed requests
            success_count = session.query(func.count(RequestLog.id)).filter(RequestLog.status == 'success').scalar() or 0
            failed_count = session.query(func.count(RequestLog.id)).filter(RequestLog.status.in_(['failed', 'rejected'])).scalar() or 0
            
            # Total unique sessions
            from models import ChatSession
            total_sessions = session.query(func.count(ChatSession.id)).scalar() or 0
            
            # Average response time
            avg_latency = session.query(func.avg(RequestLog.latency_ms)).scalar() or 0.0
            
            # Today's chat messages count
            from models import ChatMessage
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_chats = session.query(func.count(ChatMessage.id)).filter(ChatMessage.created_at >= today_start).scalar() or 0
            
            return {
                "total_sessions": total_sessions,
                "total_requests": total_requests,
                "total_responses": total_requests, # every request has a logged response
                "avg_response_time_ms": int(avg_latency),
                "today_chats": today_chats,
                "request_success": success_count,
                "request_failed": failed_count
            }
    except Exception as e:
        logger.error(f"Error fetching logs summary: {e}")
        return {
            "total_sessions": 0,
            "total_requests": 0,
            "total_responses": 0,
            "avg_response_time_ms": 0,
            "today_chats": 0,
            "request_success": 0,
            "request_failed": 0
        }
