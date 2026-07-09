import logging
from datetime import datetime
from sqlalchemy import desc

from database import get_db_session
from models import ChatSession, ChatMessage

logger = logging.getLogger(__name__)

def create_session(session_uuid: str, user_agent: str = None, ip_address: str = None) -> bool:
    """
    Creates a new chat session in the database if it doesn't already exist.
    """
    try:
        with get_db_session() as session:
            # Check if session already exists
            existing = session.query(ChatSession).filter_by(session_uuid=session_uuid).first()
            if existing:
                return True
                
            new_sess = ChatSession(
                session_uuid=session_uuid,
                user_agent=user_agent,
                ip_address=ip_address,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(new_sess)
            logger.info(f"Created chat session: {session_uuid}")
            return True
    except Exception as e:
        logger.error(f"Error creating session {session_uuid}: {e}")
        return False

def list_sessions() -> list[dict]:
    """
    Retrieves chat sessions that have at least one message, ordered by updated_at descending.
    Returns a list of dicts.
    """
    try:
        with get_db_session() as session:
            # Perform join with ChatMessage to filter out empty sessions
            sessions = session.query(ChatSession)\
                .join(ChatMessage)\
                .group_by(ChatSession.id)\
                .order_by(desc(ChatSession.updated_at))\
                .all()
            return [
                {
                    "session_uuid": s.session_uuid,
                    "created_at": s.created_at,
                    "updated_at": s.updated_at,
                    "user_agent": s.user_agent,
                    "ip_address": s.ip_address
                } for s in sessions
            ]
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        return []

def delete_session(session_uuid: str) -> bool:
    """
    Deletes a specific chat session and all its associated messages.
    """
    try:
        with get_db_session() as session:
            sess = session.query(ChatSession).filter_by(session_uuid=session_uuid).first()
            if sess:
                session.delete(sess)
                logger.info(f"Deleted chat session: {session_uuid}")
                return True
            return False
    except Exception as e:
        logger.error(f"Error deleting session {session_uuid}: {e}")
        return False

def delete_all_sessions() -> bool:
    """
    Deletes all chat sessions and cascade deletes messages.
    """
    try:
        with get_db_session() as session:
            session.query(ChatSession).delete()
            logger.info("Deleted all chat sessions.")
            return True
    except Exception as e:
        logger.error(f"Error deleting all sessions: {e}")
        return False

def get_messages(session_uuid: str) -> list[dict]:
    """
    Retrieves all messages for a specific session, ordered by created_at ascending.
    """
    try:
        with get_db_session() as session:
            messages = session.query(ChatMessage).filter_by(session_uuid=session_uuid).order_by(ChatMessage.created_at).all()
            return [
                {
                    "role": m.role,
                    "message": m.message,
                    "token_usage": m.token_usage,
                    "response_time": m.response_time,
                    "created_at": m.created_at
                } for m in messages
            ]
    except Exception as e:
        logger.error(f"Error getting messages for session {session_uuid}: {e}")
        return []

def save_message(session_uuid: str, role: str, message: str, token_usage: int = 0, response_time: float = 0.0) -> bool:
    """
    Saves a message to the database and updates the parent session's updated_at timestamp.
    """
    try:
        with get_db_session() as session:
            # Save the message
            new_msg = ChatMessage(
                session_uuid=session_uuid,
                role=role,
                message=message,
                token_usage=token_usage,
                response_time=response_time,
                created_at=datetime.utcnow()
            )
            session.add(new_msg)
            
            # Update session's updated_at
            sess = session.query(ChatSession).filter_by(session_uuid=session_uuid).first()
            if sess:
                sess.updated_at = datetime.utcnow()
                
            return True
    except Exception as e:
        logger.error(f"Error saving message for session {session_uuid}: {e}")
        return False
