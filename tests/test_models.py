import pytest
from dataclasses import asdict
from sqlalchemy import select

from mars_probe_api.models import Probe

@pytest.mark.asyncio
async def test_create_probe(db_session):
    probe = Probe(size_x=5, size_y=5)
    db_session.add(probe)
    await db_session.commit()

    db_probe = await db_session.scalar(select(Probe).where(Probe.id == probe.id))

    assert asdict(db_probe) == {
        "id": probe.id,
        "size_x": 5,
        "size_y": 5,
        "x": 0,
        "y": 0,
        "direction": "NORTH",
    }
