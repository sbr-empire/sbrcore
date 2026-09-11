# ============================================================================
# API Utilities
# Common functions for API operations
# ============================================================================

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import uuid
import bcrypt
import re
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from ..config import Config
from ..logging import get_logger

logger = get_logger(__name__)

def generate_id() -> str:
    """
    Generate unique ID for records
    """
    return str(uuid.uuid4())

def hash_password(password: str) -> str:
    """
    Hash password using bcrypt
    
    Args:
        password: Plain text password
    
    Returns:
        Hashed password
    """
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify password against hash
    
    Args:
        password: Plain text password
        password_hash: Hashed password
    
    Returns:
        True if password matches
    """
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def validate_email(email: str) -> bool:
    """
    Validate email format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """
    Validate phone number format
    """
    pattern = r'^\+?1?\d{9,15}$'
    return re.match(pattern, phone.replace('-', '').replace(' ', '')) is not None

async def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    plain_text: Optional[str] = None
) -> bool:
    """
    Send email
    
    Args:
        to_email: Recipient email
        subject: Email subject
        html_content: HTML email body
        plain_text: Plain text alternative
    
    Returns:
        True if sent successfully
    """
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = Config.SMTP_FROM_EMAIL
        msg['To'] = to_email
        
        if plain_text:
            part1 = MIMEText(plain_text, 'plain')
            msg.attach(part1)
        
        part2 = MIMEText(html_content, 'html')
        msg.attach(part2)
        
        # Note: This is synchronous; use async SMTP library for production
        server = smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT)
        server.starttls()
        server.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Email sent to {to_email}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False

def format_error_response(
    message: str,
    code: str = 'ERROR',
    status_code: int = 400,
    details: Optional[Dict] = None
) -> Tuple[Dict, int]:
    """
    Format error response
    
    Returns:
        (response_dict, status_code)
    """
    return {
        'success': False,
        'error': {
            'message': message,
            'code': code,
            'details': details or {}
        },
        'timestamp': datetime.utcnow().isoformat()
    }, status_code

def format_success_response(
    data: Any = None,
    message: str = 'Success',
    status_code: int = 200,
    metadata: Optional[Dict] = None
) -> Tuple[Dict, int]:
    """
    Format success response
    
    Returns:
        (response_dict, status_code)
    """
    response = {
        'success': True,
        'message': message,
        'data': data,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if metadata:
        response['metadata'] = metadata
    
    return response, status_code

def paginate_query(
    query,
    page: int = 1,
    per_page: int = 20
) -> Tuple[List, Dict]:
    """
    Paginate database query
    
    Args:
        query: SQLAlchemy query object
        page: Page number (1-indexed)
        per_page: Items per page
    
    Returns:
        (items, pagination_metadata)
    """
    if page < 1:
        page = 1
    
    if per_page < 1 or per_page > 100:
        per_page = 20
    
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    
    total_pages = (total + per_page - 1) // per_page
    
    metadata = {
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': total_pages,
        'has_next': page < total_pages,
        'has_prev': page > 1
    }
    
    return items, metadata
