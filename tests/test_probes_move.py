import pytest
import uuid
from sqlalchemy import select
from mars_probe_api.models import Probe


@pytest.mark.asyncio
class TestProbeMove:
    async def test_move_probe_success(self, app_client, db_session, probe_a):
        response = app_client.post(f"/probes/{probe_a.id}/move", json={"commands": "LRMRMMRRM"})
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(probe_a.id)
        assert data["x"] == 1
        assert data["y"] == 1
        assert data["direction"] == "WEST"

        db_probe = await db_session.scalar(select(Probe).where(Probe.id == probe_a.id))
        assert db_probe.x == 1
        assert db_probe.y == 1
        assert db_probe.direction == "WEST"

    async def test_move_probe_only_turns(self, app_client, db_session, probe_a):
        response = app_client.post(f"/probes/{probe_a.id}/move", json={"commands": "LLRR"})
        assert response.status_code == 200
        data = response.json()
        assert data["x"] == 0 and data["y"] == 0

    async def test_move_probe_invalid_uuid(self, app_client):
        response = app_client.post(f"/probes/bla-bla/move", json={"commands": "M"})
        assert response.status_code == 400
        assert "Invalid probe ID format" in response.text

    async def test_move_probe_not_found(self, app_client):
        fake_id = uuid.uuid4()
        response = app_client.post(f"/probes/{fake_id}/move", json={"commands": "MRM"})
        assert response.status_code == 404
        assert "Probe not found" in response.text

    async def test_move_probe_out_of_bounds(self, app_client, db_session, probe_a):
        probe_a.direction = "SOUTH"
        await db_session.commit()

        response = app_client.post(f"/probes/{probe_a.id}/move", json={"commands": "M"})
        assert response.status_code == 400
        assert "exceed grid limits" in response.text
    
    async def test_move_probe_partial_sequence_not_applied(self, app_client, db_session, probe_b):
        response = app_client.post(f"/probes/{probe_b.id}/move", json={"commands": "MMMMM"})
        assert response.status_code == 400
        assert "exceed grid limits" in response.text

        db_probe = await db_session.scalar(select(Probe).where(Probe.id == probe_b.id))
        assert db_probe.x == 0
        assert db_probe.y == 0
        assert db_probe.direction == "EAST"

    @pytest.mark.parametrize(
        "payload, expected_detail",
        [
            ({"commands": "MXR"}, "Invalid command sequence. Allowed commands: 'M', 'L', 'R'."),
            ({"commands": ""}, "Field 'commands' is required and must be a non-empty string."),
        ]
    )
    async def test_move_probe_with_invalid_commands(self, app_client, probe_a, payload, expected_detail):
        response = app_client.post(f"/probes/{probe_a.id}/move", json=payload)
        assert response.status_code == 400
        assert expected_detail in response.text

    @pytest.mark.parametrize(
        "payload, expected_detail",
        [
            ({}, "Field required"),
            ({"commands": ["M", "R"]}, "Input should be a valid string"),
        ]
    )
    async def test_move_probe_with_schema_validation_error(self, app_client, probe_a, payload, expected_detail):
        response = app_client.post(f"/probes/{probe_a.id}/move", json=payload)
        assert response.status_code == 422

        resp_json = response.json()
        assert any(expected_detail in err.get("msg", "") for err in resp_json["detail"])
