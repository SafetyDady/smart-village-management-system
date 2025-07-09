"""
LINE Service - Smart Village Management System
"""

import httpx
import json
from typing import Optional, Dict, Any, List
from app.core.config import settings


class LineService:
    """LINE integration service"""
    
    def __init__(self):
        self.channel_id = settings.LINE_CHANNEL_ID
        self.channel_secret = settings.LINE_CHANNEL_SECRET
        self.channel_access_token = settings.LINE_CHANNEL_ACCESS_TOKEN
    
    async def verify_id_token(self, id_token: str) -> Optional[Dict[str, Any]]:
        """
        Verify LINE ID Token and return user profile
        """
        if not self.channel_id:
            raise ValueError("LINE Channel ID not configured")
        
        url = "https://api.line.me/oauth2/v2.1/verify"
        data = {
            "id_token": id_token,
            "client_id": self.channel_id
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, data=data)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return None
                    
        except Exception as e:
            print(f"Error verifying LINE ID token: {e}")
            return None
    
    async def get_profile(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        Get LINE user profile using access token
        """
        url = "https://api.line.me/v2/profile"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return None
                    
        except Exception as e:
            print(f"Error getting LINE profile: {e}")
            return None
    
    async def send_push_message(self, user_id: str, message: str) -> bool:
        """
        Send push message to LINE user
        """
        if not self.channel_access_token:
            print("LINE Channel Access Token not configured")
            return False
        
        url = "https://api.line.me/v2/bot/message/push"
        headers = {
            "Authorization": f"Bearer {self.channel_access_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "to": user_id,
            "messages": [
                {
                    "type": "text",
                    "text": message
                }
            ]
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=data)
                return response.status_code == 200
                
        except Exception as e:
            print(f"Error sending LINE push message: {e}")
            return False
    
    async def send_flex_message(self, user_id: str, alt_text: str, flex_content: Dict[str, Any]) -> bool:
        """
        Send flex message to LINE user
        """
        if not self.channel_access_token:
            print("LINE Channel Access Token not configured")
            return False
        
        url = "https://api.line.me/v2/bot/message/push"
        headers = {
            "Authorization": f"Bearer {self.channel_access_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "to": user_id,
            "messages": [
                {
                    "type": "flex",
                    "altText": alt_text,
                    "contents": flex_content
                }
            ]
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=data)
                return response.status_code == 200
                
        except Exception as e:
            print(f"Error sending LINE flex message: {e}")
            return False
    
    async def send_notify(self, token: str, message: str) -> bool:
        """
        Send LINE Notify message
        """
        url = "https://notify-api.line.me/api/notify"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {"message": message}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, data=data)
                return response.status_code == 200
                
        except Exception as e:
            print(f"Error sending LINE Notify: {e}")
            return False
    
    async def get_liff_apps(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get list of LIFF apps
        """
        if not self.channel_access_token:
            print("LINE Channel Access Token not configured")
            return None
        
        url = "https://api.line.me/liff/v1/apps"
        headers = {"Authorization": f"Bearer {self.channel_access_token}"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    return response.json().get("apps", [])
                else:
                    return None
                    
        except Exception as e:
            print(f"Error getting LIFF apps: {e}")
            return None

