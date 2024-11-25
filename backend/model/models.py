from pydantic import BaseModel, Field

class LoginForm(BaseModel):
    username: str
    password: str

class SignupForm(BaseModel):
    name: str
    email: str
    password: str

class Patient(BaseModel):
    name: str
    gender: str
    age: int
    email: str
    notes: str
    result: str = Field(default="Pending...")