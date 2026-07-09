import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class ChatSession(Base):
    __tablename__ = 'chat_sessions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_uuid = Column(String(36), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    user_agent = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)

    # Relationships
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ChatSession(session_uuid='{self.session_uuid}', created_at='{self.created_at}')>"


class ChatMessage(Base):
    __tablename__ = 'chat_messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_uuid = Column(String(36), ForeignKey('chat_sessions.session_uuid', ondelete='CASCADE'), nullable=False, index=True)
    role = Column(String(20), nullable=False) # 'user' or 'assistant'
    message = Column(Text, nullable=False)
    token_usage = Column(Integer, default=0, nullable=False)
    response_time = Column(Float, default=0.0, nullable=False) # latency in seconds
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")

    def __repr__(self):
        return f"<ChatMessage(session_uuid='{self.session_uuid}', role='{self.role}', created_at='{self.created_at}')>"


class RequestLog(Base):
    __tablename__ = 'request_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_uuid = Column(String(36), nullable=False, index=True)
    request = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    latency_ms = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False) # 'success', 'failed', 'rejected'
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<RequestLog(session_uuid='{self.session_uuid}', status='{self.status}', latency_ms={self.latency_ms})>"
