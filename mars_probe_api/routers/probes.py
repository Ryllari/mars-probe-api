import uuid
from http import HTTPStatus
from typing import Annotated
from fastapi import APIRouter
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mars_probe_api.database import get_session
from mars_probe_api.models import Probe
from mars_probe_api.schemas import (
    ProbeCreate,
    ProbeListResponse,
    ProbeMoveRequest,
    ProbeResponse
)
from mars_probe_api.services.probe_service import DIRECTIONS, ProbeService

router = APIRouter(prefix='/probes', tags=['probes'])

Session = Annotated[AsyncSession, Depends(get_session)]


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

    if probe_data.direction not in DIRECTIONS:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Direction must be one of {DIRECTIONS}"
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


@router.get("/", response_model=ProbeListResponse)
async def list_probes(session: Session):
    result = await session.scalars(select(Probe))
    probes = result.all()
    
    probes_list = [ProbeResponse.model_validate(p) for p in probes]
    return ProbeListResponse(probes=probes_list)


@router.post("/{probe_id}/move", response_model=ProbeResponse)
async def move_probe(
    probe_id: str,
    request: ProbeMoveRequest,
    session: AsyncSession = Depends(get_session)
):
    try:
        probe_id = uuid.UUID(probe_id)
    except ValueError:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Invalid probe ID format")

    probe = await session.scalar(select(Probe).where(Probe.id == probe_id))
    if not probe:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Probe not found")

    try:
        ProbeService.execute_commands(probe, request.commands)
    except HTTPException as e:
        raise e

    session.add(probe)
    await session.commit()
    await session.refresh(probe)

    return ProbeResponse.model_validate(probe)
