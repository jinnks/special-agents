# Copyright (c) 2025 Special Agents
# Licensed under MIT License - See LICENSE file for details

"""
Unit tests for security module
Fast, isolated tests for validators and encryption
"""
import pytest
from unittest.mock import patch
from app.security import (
    InputValidator,
    APIKeyEncryption,
    SQLInjectionPrevention,
    FileUploadSecurity
)


class TestInputValidator:
    """Test input validation functions"""

    # Username validation tests
    def test_validate_username_valid(self):
        valid, error = InputValidator.validate_username("testuser")
        assert valid is True
        assert error == ""

    def test_validate_username_too_short(self):
        valid, error = InputValidator.validate_username("ab")
        assert valid is False
        assert "at least 3 characters" in error

    def test_validate_username_too_long(self):
        valid, error = InputValidator.validate_username("a" * 81)
        assert valid is False
        assert "less than 80 characters" in error

    def test_validate_username_invalid_chars(self):
        valid, error = InputValidator.validate_username("test@user")
        assert valid is False
        assert "letters, numbers, underscores" in error

    def test_validate_username_empty(self):
        valid, error = InputValidator.validate_username("")
        assert valid is False
        assert "required" in error

    def test_validate_username_with_underscore(self):
        valid, error = InputValidator.validate_username("test_user")
        assert valid is True

    def test_validate_username_with_hyphen(self):
        valid, error = InputValidator.validate_username("test-user")
        assert valid is True

    # Email validation tests
    def test_validate_email_valid(self):
        valid, error = InputValidator.validate_email_address("test@example.com")
        assert valid is True
        assert error == ""

    def test_validate_email_invalid_format(self):
        valid, error = InputValidator.validate_email_address("notanemail")
        assert valid is False

    def test_validate_email_empty(self):
        valid, error = InputValidator.validate_email_address("")
        assert valid is False
        assert "required" in error

    def test_validate_email_with_subdomain(self):
        valid, error = InputValidator.validate_email_address("user@mail.example.com")
        assert valid is True

    # Password validation tests
    def test_validate_password_valid(self):
        valid, error = InputValidator.validate_password("Password123")
        assert valid is True
        assert error == ""

    def test_validate_password_too_short(self):
        valid, error = InputValidator.validate_password("Pass1")
        assert valid is False
        assert "at least 8 characters" in error

    def test_validate_password_no_number(self):
        valid, error = InputValidator.validate_password("PasswordOnly")
        assert valid is False
        assert "letters and numbers" in error

    def test_validate_password_no_letter(self):
        valid, error = InputValidator.validate_password("12345678")
        assert valid is False
        assert "letters and numbers" in error

    def test_validate_password_too_long(self):
        valid, error = InputValidator.validate_password("a" * 129)
        assert valid is False
        assert "less than 128 characters" in error

    def test_validate_password_empty(self):
        valid, error = InputValidator.validate_password("")
        assert valid is False
        assert "required" in error

    # Agent name validation tests
    def test_validate_agent_name_valid(self):
        valid, error = InputValidator.validate_agent_name("Holiday Planner")
        assert valid is True

    def test_validate_agent_name_too_short(self):
        valid, error = InputValidator.validate_agent_name("AI")
        assert valid is False
        assert "at least 3 characters" in error

    def test_validate_agent_name_too_long(self):
        valid, error = InputValidator.validate_agent_name("a" * 201)
        assert valid is False
        assert "less than 200 characters" in error

    def test_validate_agent_name_empty(self):
        valid, error = InputValidator.validate_agent_name("")
        assert valid is False

    # Price validation tests
    def test_validate_price_valid(self):
        valid, error = InputValidator.validate_price(9.99)
        assert valid is True

    def test_validate_price_zero(self):
        valid, error = InputValidator.validate_price(0.0)
        assert valid is True

    def test_validate_price_negative(self):
        valid, error = InputValidator.validate_price(-1.0)
        assert valid is False
        assert "cannot be negative" in error

    def test_validate_price_too_high(self):
        valid, error = InputValidator.validate_price(10000.0)
        assert valid is False
        assert "cannot exceed" in error

    def test_validate_price_invalid_format(self):
        valid, error = InputValidator.validate_price("invalid")
        assert valid is False
        assert "Invalid price format" in error

    # Category validation tests
    def test_validate_category_valid(self):
        valid, error = InputValidator.validate_category("education")
        assert valid is True

    def test_validate_category_invalid(self):
        valid, error = InputValidator.validate_category("invalid")
        assert valid is False
        assert "Invalid category" in error

    # Rating validation tests
    def test_validate_rating_valid(self):
        valid, error = InputValidator.validate_rating(5)
        assert valid is True

    def test_validate_rating_too_low(self):
        valid, error = InputValidator.validate_rating(0)
        assert valid is False
        assert "between 1 and 5" in error

    def test_validate_rating_too_high(self):
        valid, error = InputValidator.validate_rating(6)
        assert valid is False
        assert "between 1 and 5" in error

    def test_validate_rating_invalid_format(self):
        valid, error = InputValidator.validate_rating("invalid")
        assert valid is False
        assert "Invalid rating format" in error

    # Sanitization tests
    def test_sanitize_html_removes_script(self):
        html = '<script>alert("xss")</script><p>Hello</p>'
        result = InputValidator.sanitize_html(html)
        assert '<script>' not in result
        assert '<p>Hello</p>' in result

    def test_sanitize_html_empty(self):
        result = InputValidator.sanitize_html("")
        assert result == ""

    def test_sanitize_html_none(self):
        result = InputValidator.sanitize_html(None)
        assert result == ""

    def test_sanitize_text_removes_null_bytes(self):
        text = "hello\x00world"
        result = InputValidator.sanitize_text(text)
        assert '\x00' not in result

    def test_sanitize_text_limits_length(self):
        text = "a" * 20000
        result = InputValidator.sanitize_text(text, max_length=100)
        assert len(result) == 100

    def test_sanitize_text_removes_control_chars(self):
        text = "hello\x01\x02world"
        result = InputValidator.sanitize_text(text)
        assert '\x01' not in result
        assert '\x02' not in result

    def test_sanitize_text_keeps_newlines(self):
        text = "hello\nworld"
        result = InputValidator.sanitize_text(text)
        assert '\n' in result

    def test_sanitize_text_empty(self):
        result = InputValidator.sanitize_text("")
        assert result == ""


class TestAPIKeyEncryption:
    """Test API key encryption/decryption"""

    def test_encrypt_decrypt_roundtrip(self, app):
        with app.app_context():
            original = "sk-ant-api03-test123"
            encrypted = APIKeyEncryption.encrypt(original)
            decrypted = APIKeyEncryption.decrypt(encrypted)
            assert decrypted == original

    def test_encrypt_empty_string(self, app):
        with app.app_context():
            result = APIKeyEncryption.encrypt("")
            assert result == ""

    def test_decrypt_empty_string(self, app):
        with app.app_context():
            result = APIKeyEncryption.decrypt("")
            assert result == ""

    def test_decrypt_invalid_data(self, app):
        with app.app_context():
            result = APIKeyEncryption.decrypt("invalid-encrypted-data")
            assert result == ""

    def test_encrypt_exception_handling(self, app):
        with app.app_context():
            # Test with invalid Fernet key to trigger exception
            with patch('app.security.APIKeyEncryption._get_key', return_value=b'short'):
                result = APIKeyEncryption.encrypt('sk-ant-test123')
                # Should handle exception and return empty string
                assert result == ''


class TestSQLInjectionPrevention:
    """Test SQL injection prevention utilities"""

    def test_is_safe_order_by_valid(self):
        assert SQLInjectionPrevention.is_safe_order_by("created_at") is True
        assert SQLInjectionPrevention.is_safe_order_by("user_id") is True

    def test_is_safe_order_by_invalid(self):
        assert SQLInjectionPrevention.is_safe_order_by("name; DROP TABLE") is False
        assert SQLInjectionPrevention.is_safe_order_by("name OR 1=1") is False

    def test_is_safe_limit_valid(self):
        assert SQLInjectionPrevention.is_safe_limit(10) is True
        assert SQLInjectionPrevention.is_safe_limit("50") is True

    def test_is_safe_limit_invalid(self):
        assert SQLInjectionPrevention.is_safe_limit(0) is False
        assert SQLInjectionPrevention.is_safe_limit(1001) is False
        assert SQLInjectionPrevention.is_safe_limit("invalid") is False


class TestFileUploadSecurity:
    """Test file upload security checks"""

    def test_is_allowed_extension_valid(self):
        allowed = {'sagent', 'zip'}
        assert FileUploadSecurity.is_allowed_extension("file.sagent", allowed) is True
        assert FileUploadSecurity.is_allowed_extension("file.zip", allowed) is True

    def test_is_allowed_extension_invalid(self):
        allowed = {'sagent', 'zip'}
        assert FileUploadSecurity.is_allowed_extension("file.exe", allowed) is False
        assert FileUploadSecurity.is_allowed_extension("file.sh", allowed) is False

    def test_is_allowed_extension_dangerous(self):
        allowed = {'exe'}  # Even if allowed, dangerous extensions are blocked
        assert FileUploadSecurity.is_allowed_extension("file.exe", allowed) is False

    def test_is_allowed_extension_no_extension(self):
        allowed = {'sagent'}
        assert FileUploadSecurity.is_allowed_extension("noextension", allowed) is False

    def test_sanitize_filename_removes_path(self):
        result = FileUploadSecurity.sanitize_filename("../../etc/passwd")
        assert '/' not in result
        assert '..' not in result

    def test_sanitize_filename_removes_dangerous_chars(self):
        result = FileUploadSecurity.sanitize_filename("file<>:name.txt")
        assert '<' not in result
        assert '>' not in result
        assert ':' not in result

    def test_sanitize_filename_limits_length(self):
        long_name = "a" * 300 + ".txt"
        result = FileUploadSecurity.sanitize_filename(long_name)
        assert len(result) <= 255

    def test_validate_file_size_valid(self):
        valid, error = FileUploadSecurity.validate_file_size(1024 * 1024)  # 1MB
        assert valid is True

    def test_validate_file_size_too_large(self):
        valid, error = FileUploadSecurity.validate_file_size(100 * 1024 * 1024)  # 100MB
        assert valid is False
        assert "exceeds" in error

    def test_validate_file_size_empty(self):
        valid, error = FileUploadSecurity.validate_file_size(0)
        assert valid is False
        assert "empty" in error
