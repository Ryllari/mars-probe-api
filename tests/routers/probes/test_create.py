import pytest
import uuid

from sqlalchemy import select
from mars_probe_api.models.probe import Probe


@pytest.mark.asyncio
class TestProbeCreate:
    async def test_create_probe_success(self, app_client, db_session):
        payload = {
            "x": 5,
            "y": 5,
            "direction": "NORTH"
        }

        response = app_client.post("/probes", json=payload)
        assert response.status_code == 201

        data = response.json()
        assert set(data.keys()) == {"id", "x", "y", "direction"}
        assert data["x"] == 0
        assert data["y"] == 0
        assert data["direction"] == "NORTH"
        assert isinstance(data["id"], str)

        probe_id = uuid.UUID(data["id"])
        db_probe = await db_session.scalar(select(Probe).where(Probe.id == probe_id))
        assert db_probe is not None
        assert db_probe.size_x == 5
        assert db_probe.size_y == 5
        assert db_probe.x == 0
        assert db_probe.y == 0
        assert db_probe.direction == "NORTH"

    @pytest.mark.parametrize(
        "payload, expected_detail",
        [
            ({"x": -1, "y": 5, "direction": "NORTH"}, "X must be a non-negative integer"),
            ({"x": 5, "y": -2, "direction": "EAST"}, "Y must be a non-negative integer"),
            ({"x": 5, "y": 5, "direction": "UP"}, "Direction must be one of ['NORTH', 'EAST', 'SOUTH', 'WEST']"),
        ]
    )
    async def test_create_probe_with_invalid_values(self, app_client, payload, expected_detail):
        response = app_client.post("/probes", json=payload)
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == expected_detail

    @pytest.mark.parametrize(
        "payload, expected_msg",
        [
            ({"y": 5, "direction": "NORTH"}, "field required"),
            ({"x": 5, "direction": "NORTH"}, "field required"),
            ({"x": 5, "y": 5}, "field required"),

            ({"x": "five", "y": 5, "direction": "NORTH"}, "a valid integer"),
            ({"x": 5, "y": "five", "direction": "NORTH"}, "valid integer"),
        ]
    )
    async def test_create_probe_with_schema_validation_error(self, app_client, payload, expected_msg):
        response = app_client.post("/probes", json=payload)
        assert response.status_code == 422
        resp_json = response.json()
        assert any(expected_msg in err.get("msg", "").lower() for err in resp_json["detail"])
