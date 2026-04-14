from pydantic import BaseModel
from typing import Literal
from .common import MongoBaseModel


class Location(BaseModel):
    lat: float
    lng: float


class UserCreate(BaseModel):
    name: str
    email: str
    phone: str
    password: str
    role: Literal["client", "worker"]
    language: str = "en"
    location: Location


class UserDB(MongoBaseModel):
    name: str
    email: str
    phone: str
    password: str
    role: str
    language: str
    location: Location