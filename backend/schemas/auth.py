from pydantic import BaseModel, EmailStr, Field

class SignUpStart(BaseModel):
    student_id : str = Field(... , min_length=9, max_length=9)
    email : EmailStr
    password : str = Field(... , min_length=6)
    password_confirm : str = Field(... , min_length=6)

class VerifyOtp(BaseModel):
    student_id : str
    otp_code : str

class SignIn(BaseModel):
    student_id : str
    password : str

class TokenResponse(BaseModel):
    access_token : str
    token_type : str = "bearer"
    user_uuid : str