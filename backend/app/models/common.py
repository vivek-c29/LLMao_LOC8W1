from bson import ObjectId
from typing import Any, Annotated
from datetime import datetime
from pydantic import BaseModel, Field, BeforeValidator, PlainSerializer


def validate_object_id(v: Any) -> ObjectId:
    if isinstance(v, ObjectId):
        return v
    if isinstance(v, str) and ObjectId.is_valid(v):
        return ObjectId(v)
    raise ValueError("Invalid ObjectId")


# Using Any as the base type to avoid Pydantic trying to generate a schema for ObjectId
PyObjectId = Annotated[
    Any,
    BeforeValidator(validate_object_id),
    PlainSerializer(lambda v: str(v), return_type=str, when_used="json"),
]


class MongoBaseModel(BaseModel):
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }