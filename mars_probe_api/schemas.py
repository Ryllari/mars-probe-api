import uuid
from pydantic import BaseModel
from typing import Literal


class ProbeCreate(BaseModel):
    x: int  
    y: int 
    direction: str


class ProbeResponse(BaseModel):
    id: uuid.UUID
    x: int
    y: int
    direction: str

    model_config = {
        "from_attributes": True
    }
