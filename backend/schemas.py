from pydantic import BaseModel, EmailStr, Field, ValidationError, ConfigDict

class RegisterSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    firstName: str = Field(min_length=1, max_length=50)
    lastName: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)
    password: str = Field(min_length=6, max_length=128)

class LoginSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr
    password: str = Field(min_length=6)