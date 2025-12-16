# Copyright (c) 2025 Special Agents
# Licensed under MIT License - See LICENSE file for details

"""
Security utilities for input validation, sanitization, and encryption
"""
import re
import bleach
from cryptography.fernet import Fernet
from flask import current_app
from email_validator import validate_email, EmailNotValidError
import base64
import hashlib


class InputValidator:
    """Validates and sanitizes user input"""

    # Allowed HTML tags for user content (very restrictive)
    ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'a']
    ALLOWED_ATTRIBUTES = {'a': ['href', 'title']}

    @staticmethod
    def sanitize_html(text: str) -> str:
        """Remove malicious HTML/JavaScript from user input"""
        if not text:
            return ''
        return bleach.clean(
            text,
            tags=InputValidator.ALLOWED_TAGS,
            attributes=InputValidator.ALLOWED_ATTRIBUTES,
            strip=True
        )

    @staticmethod
    def sanitize_text(text: str, max_length: int = 10000) -> str:
        """Sanitize plain text input"""
        if not text:
            return ''

        # Remove null bytes
        text = text.replace('\x00', '')

        # Limit length
        text = text[:max_length]

        # Remove control characters except newlines and tabs
        text = ''.join(char for char in text if char == '\n' or char == '\t' or ord(char) >= 32)

        return text.strip()

    @staticmethod
    def validate_username(username: str) -> tuple[bool, str]:
        """
        Validate username format
        Returns: (is_valid, error_message)
        """
        if not username:
            return False, "Username is required"

        if len(username) < 3:
            return False, "Username must be at least 3 characters"

        if len(username) > 80:
            return False, "Username must be less than 80 characters"

        # Allow alphanumeric, underscore, hyphen
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return False, "Username can only contain letters, numbers, underscores, and hyphens"

        return True, ""

    @staticmethod
    def validate_email_address(email: str) -> tuple[bool, str]:
        """
        Validate email format
        Returns: (is_valid, error_message)
        """
        if not email:
            return False, "Email is required"

        try:
            # Validate and normalize
            valid = validate_email(email, check_deliverability=False)
            return True, ""
        except EmailNotValidError as e:
            return False, str(e)

    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """
        Validate password strength
        Returns: (is_valid, error_message)
        """
        if not password:
            return False, "Password is required"

        if len(password) < 8:
            return False, "Password must be at least 8 characters"

        if len(password) > 128:
            return False, "Password must be less than 128 characters"

        # Check for at least one letter and one number
        has_letter = bool(re.search(r'[a-zA-Z]', password))
        has_number = bool(re.search(r'[0-9]', password))

        if not (has_letter and has_number):
            return False, "Password must contain both letters and numbers"

        return True, ""

    @staticmethod
    def validate_agent_name(name: str) -> tuple[bool, str]:
        """Validate agent name"""
        if not name:
            return False, "Agent name is required"

        if len(name) < 3:
            return False, "Agent name must be at least 3 characters"

        if len(name) > 200:
            return False, "Agent name must be less than 200 characters"

        return True, ""

    @staticmethod
    def validate_price(price: float) -> tuple[bool, str]:
        """Validate pricing"""
        try:
            price_float = float(price)
            if price_float < 0:
                return False, "Price cannot be negative"
            if price_float > 9999.99:
                return False, "Price cannot exceed $9999.99"
            return True, ""
        except (ValueError, TypeError):
            return False, "Invalid price format"

    @staticmethod
    def validate_category(category: str) -> tuple[bool, str]:
        """Validate agent category"""
        allowed_categories = ['productivity', 'education', 'travel', 'health', 'finance', 'creative']
        if category not in allowed_categories:
            return False, f"Invalid category. Must be one of: {', '.join(allowed_categories)}"
        return True, ""

    @staticmethod
    def validate_rating(rating: int) -> tuple[bool, str]:
        """Validate review rating"""
        try:
            rating_int = int(rating)
            if rating_int < 1 or rating_int > 5:
                return False, "Rating must be between 1 and 5"
            return True, ""
        except (ValueError, TypeError):
            return False, "Invalid rating format"


class APIKeyEncryption:
    """Encrypt/decrypt API keys for session storage"""

    @staticmethod
    def _get_key() -> bytes:
        """Get encryption key from app secret"""
        secret = current_app.config['SECRET_KEY']
        # Derive a consistent key from SECRET_KEY
        key = hashlib.sha256(secret.encode()).digest()
        return base64.urlsafe_b64encode(key)

    @staticmethod
    def encrypt(api_key: str) -> str:
        """Encrypt API key for session storage"""
        if not api_key:
            return ''

        try:
            f = Fernet(APIKeyEncryption._get_key())
            encrypted = f.encrypt(api_key.encode())
            return encrypted.decode()
        except Exception as e:
            current_app.logger.error(f"Failed to encrypt API key: {e}")
            return ''

    @staticmethod
    def decrypt(encrypted_key: str) -> str:
        """Decrypt API key from session"""
        if not encrypted_key:
            return ''

        try:
            f = Fernet(APIKeyEncryption._get_key())
            decrypted = f.decrypt(encrypted_key.encode())
            return decrypted.decode()
        except Exception as e:
            current_app.logger.error(f"Failed to decrypt API key: {e}")
            return ''


class SQLInjectionPrevention:
    """SQL injection prevention utilities"""

    @staticmethod
    def is_safe_order_by(field: str) -> bool:
        """Check if order by field is safe (prevent SQL injection in ORDER BY)"""
        # Only allow alphanumeric and underscore
        return bool(re.match(r'^[a-zA-Z0-9_]+$', field))

    @staticmethod
    def is_safe_limit(limit: any) -> bool:
        """Check if LIMIT value is safe"""
        try:
            limit_int = int(limit)
            return 0 < limit_int <= 1000
        except (ValueError, TypeError):
            return False


class FileUploadSecurity:
    """File upload security checks"""

    # Dangerous file extensions
    DANGEROUS_EXTENSIONS = {
        'exe', 'bat', 'cmd', 'com', 'pif', 'scr', 'vbs', 'js', 'jar',
        'msi', 'dll', 'so', 'dylib', 'sh', 'bash', 'ps1', 'app', 'deb', 'rpm'
    }

    @staticmethod
    def is_allowed_extension(filename: str, allowed: set) -> bool:
        """Check if file extension is allowed"""
        if '.' not in filename:
            return False

        ext = filename.rsplit('.', 1)[1].lower()

        # Block dangerous extensions
        if ext in FileUploadSecurity.DANGEROUS_EXTENSIONS:
            return False

        return ext in allowed

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize uploaded filename"""
        # Remove path components
        filename = filename.split('/')[-1].split('\\')[-1]

        # Remove dangerous characters
        filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)

        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:250] + ('.' + ext if ext else '')

        return filename

    @staticmethod
    def validate_file_size(size: int, max_size: int = 50 * 1024 * 1024) -> tuple[bool, str]:
        """Validate file size (default 50MB)"""
        if size <= 0:
            return False, "File is empty"

        if size > max_size:
            max_mb = max_size / (1024 * 1024)
            return False, f"File size exceeds {max_mb}MB limit"

        return True, ""
