from pydantic import BaseModel, EmailStr

# Kullanıcı kaydı için (Şifre var)
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# Kullanıcıyı geri döndürürken (Şifre YOK, güvenlik kuralı)
class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True # ORM modunu açar

# Token dönüş şeması
class Token(BaseModel):
    access_token: str
    token_type: str