import time
import datetime
import streamlit as st

def to_wib(dt: datetime.datetime) -> datetime.datetime:
    """
    Converts a UTC naive datetime to Waktu Indonesia Barat (WIB) which is UTC+7.
    """
    if dt is None:
        return None
    return dt + datetime.timedelta(hours=7)

# Store the global start time of the server process
APP_START_TIME = time.time()

def get_uptime_string() -> str:
    """
    Calculates the server uptime since startup and returns a formatted string.
    """
    uptime_seconds = int(time.time() - APP_START_TIME)
    
    days = uptime_seconds // 86400
    hours = (uptime_seconds % 86400) // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    
    return " ".join(parts)

def get_client_info() -> tuple[str, str]:
    """
    Safely retrieves User-Agent and IP address from Streamlit headers context.
    
    Returns:
        tuple[str, str]: (user_agent, ip_address)
    """
    user_agent = "Streamlit Client"
    ip_address = "127.0.0.1"
    
    try:
        # st.context is available in newer Streamlit versions (1.33.0+)
        if hasattr(st, "context") and hasattr(st.context, "headers"):
            headers = st.context.headers
            user_agent = headers.get("User-Agent", "Streamlit Client")
            
            # Extract client IP, checking standard proxy headers first
            ip = headers.get("X-Forwarded-For") or headers.get("X-Real-IP") or "127.0.0.1"
            # If multiple IPs exist in X-Forwarded-For, take the client IP (first one)
            if "," in ip:
                ip = ip.split(",")[0].strip()
            ip_address = ip
    except Exception:
        pass
        
    return user_agent, ip_address
