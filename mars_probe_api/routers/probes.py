import uuid

from fastapi import APIRouter
from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from mars_probe_api.database import get_session
from mars_probe_api.models.probe import Probe
from mars_probe_api.schemas.probe import (
    ProbeCreate,
    ProbeListResponse,
    ProbeMoveRequest,
    ProbeResponse
)
from mars_probe_api.services.probe_service import DIRECTIONS, ProbeService


router = APIRouter(prefix='/probes', tags=['probes'])
Session = Annotated[AsyncSession, Depends(get_session)]


@router.post(
    "/",
    status_code=HTTPStatus.CREATED,
    response_model=ProbeResponse,
    responses={
        400: {"description": "Bad Request"}
    }
)
async def create(probe_data: ProbeCreate, session: Session):
    """
    Launch a new Mars Probe and define the grid size.

    - **x**: Grid size in the X direction (integer >= 0)
    - **y**: Grid size in the Y direction (integer >= 0)
    - **direction**: Initial direction of the probe (NORTH, EAST, SOUTH, WEST)

    The probe always starts at position (0, 0).
    """
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
    """
    List all registered probes and their current positions.
    """
    result = await session.scalars(select(Probe))
    probes = result.all()
    
    probes_list = [ProbeResponse.model_validate(p) for p in probes]
    return ProbeListResponse(probes=probes_list)


@router.put(
    "/{probe_id}/move", 
    response_model=ProbeResponse,
    responses={
        400: {"description": "Bad Request"},
        404: {"description": "Not Foud"}
    }
)
async def move(
    probe_id: str,
    request: ProbeMoveRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Move an existing probe following a sequence of commands.

    - **probe_id**: UUID of the probe to move
    - **commands**: String of commands. Valid commands:
        - **M**: move forward one unit in the current direction
        - **L**: rotate left 90 degrees
        - **R**: rotate right 90 degrees
    """
    try:
        probe_id = uuid.UUID(probe_id)
    except ValueError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invalid probe ID format"
        )

    probe = await session.scalar(select(Probe).where(Probe.id == probe_id))
    if not probe:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Probe not found"
        )

    try:
        ProbeService.execute_commands(probe, request.commands)
    except HTTPException as e:
        raise e

    session.add(probe)
    await session.commit()
    await session.refresh(probe)

    return ProbeResponse.model_validate(probe)
