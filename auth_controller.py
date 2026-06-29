# controller/auth_controller.py
"""认证控制器"""
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from service import auth_service
from config.app_config import ResponseModel

router = APIRouter(prefix="/api/auth", tags=["认证"])

class LoginRequest(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    phone: Optional[str] = Field(None, pattern=r'^1[3-9]\d{9}$')
    password: str = Field(..., min_length=6)

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    phone: Optional[str] = Field(None, pattern=r'^1[3-9]\d{9}$')
    display_name: Optional[str] = Field(None, max_length=100)

@router.post("/login", response_model=ResponseModel)
async def login(request: LoginRequest):
    """用户登录 - 支持用户名或手机号"""
    try:
        result, error = auth_service.login_service(
            username=request.username, 
            phone=request.phone, 
            password=request.password
        )
        if error:
            return ResponseModel(code=400, message=error)
        return ResponseModel(code=200, message="登录成功", data=result)
    except Exception as e:
        return ResponseModel(code=500, message=f"登录失败: {str(e)}")

@router.post("/register", response_model=ResponseModel)
async def register(request: RegisterRequest):
    """用户注册"""
    try:
        result, error = auth_service.register_service(
            username=request.username,
            password=request.password,
            phone=request.phone,
            display_name=request.display_name
        )
        if error:
            return ResponseModel(code=400, message=error)
        return ResponseModel(code=200, message="注册成功", data=result)
    except Exception as e:
        return ResponseModel(code=500, message=f"注册失败: {str(e)}")

@router.get("/me", response_model=ResponseModel)
async def get_me(token: str = Query(..., description="认证Token")):
    """获取当前用户信息"""
    try:
        user = auth_service.verify_token_service(token)
        return ResponseModel(code=200, message="success", data=user)
    except ValueError as e:
        return ResponseModel(code=401, message=str(e))
    except Exception as e:
        return ResponseModel(code=500, message=str(e))

@router.post("/logout", response_model=ResponseModel)
async def logout(token: str = Query(..., description="认证Token")):
    """用户登出"""
    try:
        auth_service.logout_service(token)
        return ResponseModel(code=200, message="登出成功")
    except Exception as e:
        return ResponseModel(code=500, message=str(e))