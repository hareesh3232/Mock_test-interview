"""
User-related Pydantic schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, validator
from uuid import UUID


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    """Schema for user creation"""
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v
    
    @validator('full_name')
    def validate_full_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Full name must be at least 2 characters long')
        return v.strip()


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema for user updates"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    
    @validator('full_name')
    def validate_full_name(cls, v):
        if v and len(v.strip()) < 2:
            raise ValueError('Full name must be at least 2 characters long')
        return v.strip() if v else v


class UserResponse(UserBase):
    """Schema for user response"""
    id: UUID
    is_active: bool
    is_verified: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    total_interviews: int = 0
    completed_interviews: int = 0
    
    class Config:
        orm_mode = True


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse


class TokenData(BaseModel):
    """Schema for token data"""
    email: Optional[str] = None








