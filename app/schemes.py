from pydantic import BaseModel, EmailStr, constr, validator


class UserLogin(BaseModel):
    gmail: EmailStr
    password: constr(min_length=6)

class UserCreate(BaseModel):
    gmail: EmailStr
    password: constr(min_length=6, max_length=50)
    confirm_password: constr(min_length=6, max_length=50)

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        if v != values.get("password"):
            raise ValueError("Parollar mos emas!")
        return v

