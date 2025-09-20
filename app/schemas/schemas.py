from pydantic import BaseModel, Field, validator
from typing import List, Optional
from enum import Enum

class PartType(str, Enum):
    RAW = "RAW"
    ASSEMBLED = "ASSEMBLED"

class ComponentEntry(BaseModel):
    id: str = Field(..., description="Part id of the constituent part")
    quantity: int = Field(..., gt=0)

class CreatePartRequest(BaseModel):
    name: str
    type: PartType
    parts: Optional[List[ComponentEntry]] = None

    @validator("parts", always=True)
    def parts_required_for_assembled(cls, v, values):
        if values.get("type") == PartType.ASSEMBLED:
            if not v or len(v) == 0:
                raise ValueError("Assembled parts must include a non-empty parts list")
        return v

class CreatePartResponse(BaseModel):
    id: str
    name: str
    type: PartType
    parts: Optional[List[ComponentEntry]] = None

class AddInventoryRequest(BaseModel):
    quantity: int = Field(..., gt=0)

class AddInventoryResponse(BaseModel):
    status: str
    message: Optional[str] = None

class TokenRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"