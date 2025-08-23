import re
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, field_validator, Field
from fastapi import HTTPException


class SecureEmailRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    device_info: Optional[Dict[str, Any]] = None
    
    @field_validator('email')
    @classmethod
    def validate_email_domain(cls, v):
        """Additional email validation."""
        email_str = str(v)
        
        # Check for disposable email domains (basic list)
        disposable_domains = [
            '10minutemail.com', 'guerrillamail.com', 'mailinator.com',
            'tempmail.org', 'yopmail.com', 'throwaway.email'
        ]
        
        domain = email_str.split('@')[1].lower()
        if domain in disposable_domains:
            raise ValueError('Disposable email addresses are not allowed')
        
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if len(v) > 128:
            raise ValueError('Password must not exceed 128 characters')
        
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        # Check for at least one digit
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        
        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        # Check for common passwords
        common_passwords = [
            'password', '123456', 'qwerty', 'admin', 'letmein',
            'welcome', 'monkey', '1234567890', 'password123',
            'admin123', 'root', 'toor', 'pass', '123456789'
        ]
        
        if v.lower() in common_passwords:
            raise ValueError('Password is too common, please choose a stronger password')
        
        # Check for repetitive patterns
        if re.search(r'(.)\1{3,}', v):  # 4 or more consecutive identical characters
            raise ValueError('Password contains too many repetitive characters')
        
        # Check for simple sequences
        sequences = ['1234', 'abcd', 'qwer', 'asdf', 'zxcv']
        for seq in sequences:
            if seq in v.lower():
                raise ValueError('Password contains predictable sequences')
        
        return v
    
    @field_validator('device_info')
    @classmethod
    def validate_device_info(cls, v):
        """Validate and sanitize device info."""
        if v is None:
            return {}
        
        # Limit the size of device info
        if len(str(v)) > 1000:
            raise ValueError('Device info is too large')
        
        # Sanitize device info - only allow specific keys
        allowed_keys = {
            'user_agent', 'platform', 'browser', 'version', 
            'mobile', 'tablet', 'desktop', 'os'
        }
        
        sanitized = {}
        for key, value in v.items():
            if key in allowed_keys and isinstance(value, (str, bool, int, float)):
                # Truncate string values
                if isinstance(value, str):
                    sanitized[key] = value[:100]  # Limit string length
                else:
                    sanitized[key] = value
        
        return sanitized


class SecureEmailLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)
    remember_me: bool = False
    device_info: Optional[Dict[str, Any]] = None
    
    @field_validator('device_info')
    @classmethod
    def validate_device_info(cls, v):
        """Validate and sanitize device info."""
        if v is None:
            return {}
        
        # Same validation as registration
        if len(str(v)) > 1000:
            raise ValueError('Device info is too large')
        
        allowed_keys = {
            'user_agent', 'platform', 'browser', 'version', 
            'mobile', 'tablet', 'desktop', 'os'
        }
        
        sanitized = {}
        for key, value in v.items():
            if key in allowed_keys and isinstance(value, (str, bool, int, float)):
                if isinstance(value, str):
                    sanitized[key] = value[:100]
                else:
                    sanitized[key] = value
        
        return sanitized


class SecurePhoneRequest(BaseModel):
    phone: str = Field(..., min_length=7, max_length=20)
    
    @field_validator('phone')
    @classmethod
    def validate_phone_format(cls, v):
        """Validate phone number format."""
        # Remove all non-digits except +
        cleaned = re.sub(r'[^\d+]', '', v)
        
        # Must start with +
        if not cleaned.startswith('+'):
            raise ValueError('Phone number must start with country code (e.g., +1)')
        
        # Remove the + for digit counting
        digits_only = cleaned[1:]
        
        # Check length (7-15 digits for international numbers)
        if len(digits_only) < 7 or len(digits_only) > 15:
            raise ValueError('Phone number must contain 7-15 digits')
        
        # Check if all remaining characters are digits
        if not digits_only.isdigit():
            raise ValueError('Phone number contains invalid characters')
        
        # Basic validation for common country codes
        valid_country_codes = [
            '1',    # US, Canada
            '7',    # Russia, Kazakhstan
            '44',   # UK
            '33',   # France
            '49',   # Germany
            '39',   # Italy
            '34',   # Spain
            '86',   # China
            '81',   # Japan
            '82',   # South Korea
            '91',   # India
            '55',   # Brazil
            '52',   # Mexico
            '61',   # Australia
            '27',   # South Africa
        ]
        
        # Check if phone starts with a valid country code
        valid_code = False
        for code in sorted(valid_country_codes, key=len, reverse=True):
            if digits_only.startswith(code):
                valid_code = True
                break
        
        if not valid_code:
            raise ValueError('Phone number must include a valid country code')
        
        return cleaned


class EmailVerifyRequest(BaseModel):
    token: str = Field(..., min_length=32, max_length=256)
    
    @field_validator('token')
    @classmethod
    def validate_token_format(cls, v):
        """Validate token format."""
        # Remove any whitespace
        token = v.strip()
        
        # Basic format validation - should be alphanumeric or base64-like
        if not re.match(r'^[A-Za-z0-9+/=._-]+$', token):
            raise ValueError('Invalid token format')
        
        return token


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    token: str = Field(..., min_length=32, max_length=256)
    new_password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator('token')
    @classmethod
    def validate_token_format(cls, v):
        """Validate token format."""
        token = v.strip()
        if not re.match(r'^[A-Za-z0-9+/=._-]+$', token):
            raise ValueError('Invalid token format')
        return token
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password_strength(cls, v):
        """Validate new password strength - same as registration."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if len(v) > 128:
            raise ValueError('Password must not exceed 128 characters')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        common_passwords = [
            'password', '123456', 'qwerty', 'admin', 'letmein',
            'welcome', 'monkey', '1234567890', 'password123',
            'admin123', 'root', 'toor', 'pass', '123456789'
        ]
        
        if v.lower() in common_passwords:
            raise ValueError('Password is too common, please choose a stronger password')
        
        if re.search(r'(.)\1{3,}', v):
            raise ValueError('Password contains too many repetitive characters')
        
        sequences = ['1234', 'abcd', 'qwer', 'asdf', 'zxcv']
        for seq in sequences:
            if seq in v.lower():
                raise ValueError('Password contains predictable sequences')
        
        return v


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=32, max_length=512)
    
    @field_validator('refresh_token')
    @classmethod
    def validate_refresh_token_format(cls, v):
        """Validate refresh token format."""
        token = v.strip()
        # JWT tokens contain dots, allow them
        if not re.match(r'^[A-Za-z0-9+/=._-]+$', token):
            raise ValueError('Invalid refresh token format')
        return token


def validate_user_agent(user_agent: str) -> str:
    """Validate and sanitize user agent string."""
    if not user_agent:
        return "Unknown"
    
    # Truncate to reasonable length
    sanitized = user_agent[:500]
    
    # Remove potentially harmful characters
    sanitized = re.sub(r'[<>"\']', '', sanitized)
    
    return sanitized


def validate_ip_address(ip: str) -> bool:
    """Basic IP address validation."""
    if not ip:
        return False
    
    # IPv4 validation
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(ipv4_pattern, ip):
        parts = ip.split('.')
        return all(0 <= int(part) <= 255 for part in parts)
    
    # IPv6 basic validation (simplified)
    ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
    if re.match(ipv6_pattern, ip):
        return True
    
    return False