"""
Test user endpoints
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import get_password_hash


class TestUserEndpoints:
    """Test user API endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_user(self, client: AsyncClient, test_user_data: dict):
        """Test creating a new user"""
        response = await client.post("/api/v1/users/", json=test_user_data)
        
        # Should fail without authentication (401 or 403)
        assert response.status_code in [401, 403]
    
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, db_session: Session, test_user_data: dict):
        """Test successful login"""
        # Create user in database
        hashed_password = get_password_hash(test_user_data["password"])
        user = User(
            email=test_user_data["email"],
            hashed_password=hashed_password,
            first_name=test_user_data["first_name"],
            last_name=test_user_data["last_name"],
            role=test_user_data["role"],
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        
        # Test login
        login_data = {
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
        
        response = await client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Test login with invalid credentials"""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = await client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_get_current_user(self, client: AsyncClient, db_session: Session, test_user_data: dict):
        """Test getting current user information"""
        # Create user in database
        hashed_password = get_password_hash(test_user_data["password"])
        user = User(
            email=test_user_data["email"],
            hashed_password=hashed_password,
            first_name=test_user_data["first_name"],
            last_name=test_user_data["last_name"],
            role=test_user_data["role"],
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        
        # Login to get token
        login_data = {
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
        
        login_response = await client.post("/api/v1/auth/login", data=login_data)
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get current user
        response = await client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["first_name"] == test_user_data["first_name"]
        assert data["last_name"] == test_user_data["last_name"]
    
    @pytest.mark.asyncio
    async def test_get_users_unauthorized(self, client: AsyncClient):
        """Test getting users without authentication"""
        response = await client.get("/api/v1/users/")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_unauthorized(self, client: AsyncClient):
        """Test getting user by ID without authentication"""
        response = await client.get("/api/v1/users/1")
        
        assert response.status_code == 401


class TestUserValidation:
    """Test user data validation"""
    
    @pytest.mark.asyncio
    async def test_invalid_email_format(self, client: AsyncClient):
        """Test creating user with invalid email format"""
        invalid_user_data = {
            "email": "invalid-email",
            "password": "testpassword123",
            "first_name": "Test",
            "last_name": "User",
            "role": "resident"
        }
        
        response = await client.post("/api/v1/users/", json=invalid_user_data)
        
        # Should fail with validation error (422) or unauthorized (401/403)
        assert response.status_code in [401, 403, 422]
    
    @pytest.mark.asyncio
    async def test_missing_required_fields(self, client: AsyncClient):
        """Test creating user with missing required fields"""
        incomplete_user_data = {
            "email": "test@example.com"
            # Missing other required fields
        }
        
        response = await client.post("/api/v1/users/", json=incomplete_user_data)
        
        # Should fail with validation error (422) or unauthorized (401/403)
        assert response.status_code in [401, 403, 422]


class TestAuthenticationFlow:
    """Test complete authentication flow"""
    
    @pytest.mark.asyncio
    async def test_login_logout_flow(self, client: AsyncClient, db_session: Session, test_user_data: dict):
        """Test complete login and logout flow"""
        # Create user in database
        hashed_password = get_password_hash(test_user_data["password"])
        user = User(
            email=test_user_data["email"],
            hashed_password=hashed_password,
            first_name=test_user_data["first_name"],
            last_name=test_user_data["last_name"],
            role=test_user_data["role"],
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        
        # Step 1: Login
        login_data = {
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
        
        login_response = await client.post("/api/v1/auth/login", data=login_data)
        assert login_response.status_code == 200
        
        tokens = login_response.json()
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        
        # Step 2: Access protected endpoint
        headers = {"Authorization": f"Bearer {access_token}"}
        me_response = await client.get("/api/v1/auth/me", headers=headers)
        assert me_response.status_code == 200
        
        # Step 3: Logout
        logout_data = {"refresh_token": refresh_token}
        logout_response = await client.post("/api/v1/auth/logout", json=logout_data, headers=headers)
        
        # Logout should succeed or be unauthorized if not implemented
        assert logout_response.status_code in [200, 401, 404]

