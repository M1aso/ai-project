#!/usr/bin/env python3
"""
Authentication Flow Testing Script

This script tests the complete authentication flow including:
- Registration
- Email verification  
- Login
- Protected endpoints
- Session management
- Password reset
"""

import requests
import json
import time
import sys
import os
from typing import Dict, Optional

# Add the project root to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "SecurePass123!"

class AuthTester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.session_id: Optional[str] = None
        self.user_id: Optional[str] = None
        
    def log(self, message: str, data: Dict = None):
        """Log message with optional data."""
        print(f"🔄 {message}")
        if data:
            print(f"   📊 {json.dumps(data, indent=2)}")
        print()
    
    def error(self, message: str, response: requests.Response = None):
        """Log error message."""
        print(f"❌ {message}")
        if response:
            try:
                print(f"   Status: {response.status_code}")
                print(f"   Response: {json.dumps(response.json(), indent=2)}")
            except:
                print(f"   Response: {response.text}")
        print()
    
    def success(self, message: str, data: Dict = None):
        """Log success message."""
        print(f"✅ {message}")
        if data:
            print(f"   📊 {json.dumps(data, indent=2)}")
        print()
    
    def test_health_check(self):
        """Test service health."""
        self.log("Testing service health...")
        try:
            response = self.session.get(f"{self.base_url}/healthz")
            if response.status_code == 200:
                self.success("Service is healthy", response.json())
                return True
            else:
                self.error("Service health check failed", response)
                return False
        except Exception as e:
            self.error(f"Failed to connect to service: {e}")
            return False
    
    def test_registration(self, email: str = TEST_EMAIL, password: str = TEST_PASSWORD):
        """Test user registration."""
        self.log(f"Testing registration for {email}...")
        
        payload = {
            "email": email,
            "password": password,
            "device_info": {
                "platform": "test",
                "browser": "script",
                "version": "1.0"
            }
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/email/register",
                json=payload,
                headers={"User-Agent": "AuthTester/1.0"}
            )
            
            if response.status_code == 200:
                self.success("Registration successful", response.json())
                return True
            else:
                self.error("Registration failed", response)
                return False
                
        except Exception as e:
            self.error(f"Registration request failed: {e}")
            return False
    
    def get_verification_token_from_db(self):
        """Get verification token from database (for testing)."""
        try:
            # Import here to avoid dependency issues
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            from services.auth.app.db.models import EmailVerification
            
            # Use test database
            engine = create_engine("sqlite:///./auth.db")
            SessionLocal = sessionmaker(bind=engine)
            
            with SessionLocal() as db:
                verification = db.query(EmailVerification).order_by(EmailVerification.created_at.desc()).first()
                if verification:
                    return verification.token
                    
        except Exception as e:
            print(f"⚠️  Could not get token from database: {e}")
            
        return None
    
    def test_verification(self, token: str = None):
        """Test email verification."""
        if not token:
            token = self.get_verification_token_from_db()
            
        if not token:
            print("📧 Please check your email/MailHog for verification token")
            token = input("Enter verification token: ").strip()
        
        if not token:
            self.error("No verification token provided")
            return False
            
        self.log("Testing email verification...")
        
        payload = {"token": token}
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/email/verify",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                self.session_id = data.get("session_id")
                self.user_id = data.get("user_id")
                
                self.success("Email verification successful", {
                    "user_id": self.user_id,
                    "session_id": self.session_id,
                    "has_tokens": bool(self.access_token and self.refresh_token)
                })
                return True
            else:
                self.error("Email verification failed", response)
                return False
                
        except Exception as e:
            self.error(f"Verification request failed: {e}")
            return False
    
    def test_login(self, email: str = TEST_EMAIL, password: str = TEST_PASSWORD):
        """Test user login."""
        self.log(f"Testing login for {email}...")
        
        payload = {
            "email": email,
            "password": password,
            "remember_me": True,
            "device_info": {
                "platform": "test",
                "browser": "script",
                "version": "1.0"
            }
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                self.session_id = data.get("session_id")
                self.user_id = data.get("user_id")
                
                self.success("Login successful", {
                    "user_id": self.user_id,
                    "session_id": self.session_id
                })
                return True
            else:
                self.error("Login failed", response)
                return False
                
        except Exception as e:
            self.error(f"Login request failed: {e}")
            return False
    
    def test_protected_endpoint(self):
        """Test accessing protected endpoint."""
        if not self.access_token:
            self.error("No access token available for protected endpoint test")
            return False
            
        self.log("Testing protected endpoint access...")
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/auth/profile",
                headers=headers
            )
            
            if response.status_code == 200:
                self.success("Protected endpoint access successful", response.json())
                return True
            else:
                self.error("Protected endpoint access failed", response)
                return False
                
        except Exception as e:
            self.error(f"Protected endpoint request failed: {e}")
            return False
    
    def test_session_management(self):
        """Test session management endpoints."""
        if not self.access_token:
            self.error("No access token available for session management test")
            return False
            
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        # Get sessions
        self.log("Testing session listing...")
        try:
            response = self.session.get(
                f"{self.base_url}/api/auth/sessions",
                headers=headers
            )
            
            if response.status_code == 200:
                sessions = response.json().get("sessions", [])
                self.success(f"Found {len(sessions)} active sessions", {"sessions": sessions})
            else:
                self.error("Failed to get sessions", response)
                return False
                
        except Exception as e:
            self.error(f"Session listing request failed: {e}")
            return False
        
        return True
    
    def test_rate_limiting(self):
        """Test rate limiting with wrong credentials."""
        self.log("Testing rate limiting with wrong credentials...")
        
        payload = {
            "email": TEST_EMAIL,
            "password": "wrong_password"
        }
        
        attempts = 0
        max_attempts = 7  # Should be blocked after 5
        
        for i in range(max_attempts):
            try:
                response = self.session.post(
                    f"{self.base_url}/api/auth/login",
                    json=payload
                )
                
                attempts += 1
                
                if response.status_code == 429:
                    self.success(f"Rate limiting triggered after {attempts} attempts")
                    return True
                elif response.status_code == 401:
                    print(f"   Attempt {i+1}: Expected 401 Unauthorized")
                else:
                    print(f"   Attempt {i+1}: Unexpected status {response.status_code}")
                    
                time.sleep(0.5)  # Small delay between attempts
                
            except Exception as e:
                self.error(f"Rate limiting test request failed: {e}")
                return False
        
        self.error("Rate limiting was not triggered")
        return False
    
    def test_password_reset_flow(self, email: str = TEST_EMAIL):
        """Test password reset flow."""
        self.log(f"Testing password reset request for {email}...")
        
        payload = {"email": email}
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/password/reset/request",
                json=payload
            )
            
            if response.status_code == 200:
                self.success("Password reset request sent", response.json())
                return True
            else:
                self.error("Password reset request failed", response)
                return False
                
        except Exception as e:
            self.error(f"Password reset request failed: {e}")
            return False
    
    def run_complete_test(self):
        """Run the complete authentication flow test."""
        print("🚀 Starting Authentication Flow Tests")
        print("=" * 50)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Registration", self.test_registration),
            ("Email Verification", self.test_verification),
            ("Login", self.test_login),
            ("Protected Endpoint", self.test_protected_endpoint),
            ("Session Management", self.test_session_management),
            ("Rate Limiting", self.test_rate_limiting),
            ("Password Reset", self.test_password_reset_flow),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            print(f"\n🧪 Running: {test_name}")
            print("-" * 30)
            
            try:
                if test_func():
                    passed += 1
                    print(f"✅ {test_name} PASSED")
                else:
                    failed += 1
                    print(f"❌ {test_name} FAILED")
            except Exception as e:
                failed += 1
                print(f"💥 {test_name} CRASHED: {e}")
            
            print("-" * 30)
        
        print(f"\n📊 Test Results:")
        print(f"   ✅ Passed: {passed}")
        print(f"   ❌ Failed: {failed}")
        print(f"   📈 Success Rate: {passed/(passed+failed)*100:.1f}%")
        
        if failed == 0:
            print("\n🎉 All tests passed! Your auth service is working correctly.")
        else:
            print(f"\n⚠️  {failed} test(s) failed. Please check the logs above.")
        
        return failed == 0


def main():
    """Main function to run tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test authentication service")
    parser.add_argument("--url", default=BASE_URL, help="Base URL of the auth service")
    parser.add_argument("--email", default=TEST_EMAIL, help="Test email address")
    parser.add_argument("--password", default=TEST_PASSWORD, help="Test password")
    parser.add_argument("--test", choices=[
        "health", "register", "verify", "login", "profile", 
        "sessions", "rate-limit", "reset", "all"
    ], default="all", help="Specific test to run")
    
    args = parser.parse_args()
    
    tester = AuthTester(args.url)
    
    if args.test == "all":
        success = tester.run_complete_test()
        sys.exit(0 if success else 1)
    else:
        # Run specific test
        test_map = {
            "health": tester.test_health_check,
            "register": lambda: tester.test_registration(args.email, args.password),
            "verify": tester.test_verification,
            "login": lambda: tester.test_login(args.email, args.password),
            "profile": tester.test_protected_endpoint,
            "sessions": tester.test_session_management,
            "rate-limit": tester.test_rate_limiting,
            "reset": lambda: tester.test_password_reset_flow(args.email),
        }
        
        test_func = test_map.get(args.test)
        if test_func:
            success = test_func()
            sys.exit(0 if success else 1)
        else:
            print(f"Unknown test: {args.test}")
            sys.exit(1)


if __name__ == "__main__":
    main()
