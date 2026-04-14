from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.models.user import UserCreate, UserDB
from app.database.mongo import users_collection
from app.utils.auth import get_password_hash, verify_password, create_access_token
from bson import ObjectId

router = APIRouter(prefix="/auth", tags=["Auth"])

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/signup")
async def signup(payload: UserCreate):
    existing_user = await users_collection.find_one({"email": payload.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    hashed_pw = get_password_hash(payload.password)
    
    # Create DB model mapping
    user_db = UserDB(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        password=hashed_pw,
        role=payload.role,
        language=payload.language,
        location=payload.location
    )
    
    result = await users_collection.insert_one(user_db.model_dump(by_alias=True))
    return {"status": "success", "user_id": str(result.inserted_id)}


@router.post("/login")
async def login(payload: LoginRequest):
    user = await users_collection.find_one({"email": payload.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    if not verify_password(payload.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    access_token = create_access_token(user_id=str(user["_id"]), role=user["role"])
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user["role"],
        "user_id": str(user["_id"])
    }
