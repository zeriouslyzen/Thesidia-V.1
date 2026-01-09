#!/usr/bin/env python3
"""
Phone Number Authentication
SMS verification using Twilio or similar service
"""

import os
import secrets
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
import requests


class PhoneAuthManager:
    """Manages phone number authentication with SMS verification"""
    
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or Path(".")
        self.verifications_file = self.base_dir / "data" / "auth" / "phone_verifications.json"
        # Try to create directory, but handle read-only filesystem (e.g., Vercel)
        try:
            self.verifications_file.parent.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            # On read-only filesystem (Vercel), use in-memory storage
            print(f"Warning: Cannot create data directory (read-only filesystem): {e}")
            print("Using in-memory verification storage (not persistent)")
        
        # SMS provider configuration
        self.twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')
        
        # Alternative: Use a simpler service like Textbelt (free tier)
        self.use_twilio = bool(self.twilio_account_sid and self.twilio_auth_token)
        
        self.verifications = {}
        self._load_verifications()
    
    def _load_verifications(self):
        """Load verification codes from disk"""
        if self.verifications_file.exists():
            try:
                with open(self.verifications_file, 'r', encoding='utf-8') as f:
                    self.verifications = json.load(f)
            except Exception:
                self.verifications = {}
    
    def _save_verifications(self):
        """Save verification codes to disk"""
        try:
            with open(self.verifications_file, 'w', encoding='utf-8') as f:
                json.dump(self.verifications, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save verifications: {e}")
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number to E.164 format"""
        # Remove all non-digit characters
        digits = ''.join(filter(str.isdigit, phone))
        
        # Add country code if missing (default to US +1)
        if not digits.startswith('1') and len(digits) == 10:
            digits = '1' + digits
        
        return f"+{digits}"
    
    def _generate_verification_code(self) -> str:
        """Generate 6-digit verification code"""
        return f"{secrets.randbelow(900000) + 100000:06d}"
    
    def send_verification_code(self, phone: str) -> Dict[str, Any]:
        """
        Send SMS verification code to phone number
        
        Args:
            phone: Phone number (any format)
            
        Returns:
            Dictionary with verification_id and status
        """
        normalized_phone = self._normalize_phone(phone)
        code = self._generate_verification_code()
        verification_id = secrets.token_urlsafe(16)
        
        # Store verification
        self.verifications[verification_id] = {
            'phone': normalized_phone,
            'code': code,
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(minutes=10)).isoformat(),
            'verified': False,
            'attempts': 0
        }
        self._save_verifications()
        
        # Send SMS
        success = self._send_sms(normalized_phone, f"Your Thesidia verification code is: {code}")
        
        if not success:
            # Remove failed verification
            self.verifications.pop(verification_id, None)
            self._save_verifications()
            return {
                'success': False,
                'error': 'Failed to send SMS. Please check your phone number and try again.'
            }
        
        result = {
            'success': True,
            'verification_id': verification_id,
            'message': 'Verification code sent'
        }
        
        # In dev/mock mode, include the code in response
        if not self.use_twilio:
            result['mock_code'] = code
            print(f"\n{'='*60}")
            print(f"📱 MOCK SMS VERIFICATION CODE")
            print(f"Phone: {normalized_phone}")
            print(f"Code: {code}")
            print(f"Verification ID: {verification_id}")
            print(f"{'='*60}\n")
        
        return result
    
    def _send_sms(self, phone: str, message: str) -> bool:
        """Send SMS using Twilio or fallback service"""
        if self.use_twilio:
            return self._send_sms_twilio(phone, message)
        else:
            # Fallback: Use a free SMS service or log for development
            print(f"[DEV MODE] SMS to {phone}: {message}")
            return True  # In dev, always succeed
    
    def _send_sms_twilio(self, phone: str, message: str) -> bool:
        """Send SMS using Twilio"""
        try:
            url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_account_sid}/Messages.json"
            data = {
                'From': self.twilio_phone_number,
                'To': phone,
                'Body': message
            }
            response = requests.post(
                url,
                data=data,
                auth=(self.twilio_account_sid, self.twilio_auth_token)
            )
            return response.status_code == 201
        except Exception as e:
            print(f"Error sending SMS via Twilio: {e}")
            return False
    
    def verify_code(self, verification_id: str, code: str) -> Dict[str, Any]:
        """
        Verify SMS code
        
        Args:
            verification_id: Verification ID from send_verification_code
            code: 6-digit verification code
            
        Returns:
            Dictionary with success status and phone number if verified
        """
        if verification_id not in self.verifications:
            return {
                'success': False,
                'error': 'Invalid verification ID'
            }
        
        verification = self.verifications[verification_id]
        
        # Check expiration
        expires_at = datetime.fromisoformat(verification['expires_at'])
        if datetime.now() > expires_at:
            self.verifications.pop(verification_id, None)
            self._save_verifications()
            return {
                'success': False,
                'error': 'Verification code expired'
            }
        
        # Check attempts
        verification['attempts'] += 1
        if verification['attempts'] > 5:
            self.verifications.pop(verification_id, None)
            self._save_verifications()
            return {
                'success': False,
                'error': 'Too many attempts. Please request a new code.'
            }
        
        # Verify code
        if verification['code'] != code:
            self._save_verifications()
            return {
                'success': False,
                'error': 'Invalid verification code',
                'attempts_remaining': 5 - verification['attempts']
            }
        
        # Mark as verified
        verification['verified'] = True
        verification['verified_at'] = datetime.now().isoformat()
        self._save_verifications()
        
        return {
            'success': True,
            'phone': verification['phone'],
            'verified_at': verification['verified_at']
        }
    
    def get_verified_phone(self, verification_id: str) -> Optional[str]:
        """Get verified phone number from verification ID"""
        verification = self.verifications.get(verification_id)
        if verification and verification.get('verified'):
            return verification['phone']
        return None
    
    def cleanup_expired(self):
        """Clean up expired verifications"""
        now = datetime.now()
        expired_ids = [
            vid for vid, v in self.verifications.items()
            if datetime.fromisoformat(v['expires_at']) < now
        ]
        for vid in expired_ids:
            self.verifications.pop(vid, None)
        if expired_ids:
            self._save_verifications()

