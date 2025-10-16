import uuid
from pydantic import BaseModel, Field
from typing import Literal, List


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


class ProbeListResponse(BaseModel):
    probes: List[ProbeResponse] = Field(default_factory=list)


class ProbeMoveRequest(BaseModel):
    commands: str
