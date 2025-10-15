from http import HTTPStatus
from typing import Annotated
from fastapi import APIRouter
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from mars_probe_api.database import get_session
from mars_probe_api.models import Probe
from mars_probe_api.schemas import ProbeCreate, ProbeResponse

router = APIRouter(prefix='/probes', tags=['probes'])

Session = Annotated[AsyncSession, Depends(get_session)]

VALID_DIRECTIONS = ["NORTH", "SOUTH", "EAST", "WEST"]


@router.post("/", status_code=HTTPStatus.CREATED, response_model=ProbeResponse)
async def create_probe(probe_data: ProbeCreate, session: Session):
    if not isinstance(probe_data.x, int) or probe_data.x < 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="X must be a non-negative integer"
        )

    if not isinstance(probe_data.y, int) or probe_data.y < 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Y must be a non-negative integer"
        )

    if probe_data.direction not in VALID_DIRECTIONS:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Direction must be one of {VALID_DIRECTIONS}"
        )

    probe = Probe(
        size_x=probe_data.x,
        size_y=probe_data.y,
        x=0,
        y=0,
        direction=probe_data.direction
    )

    session.add(probe)
    await session.commit()
    await session.refresh(probe)

    return ProbeResponse.model_validate(probe)
