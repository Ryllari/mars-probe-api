import pytest

@pytest.mark.asyncio
async def test_list_probes_empty(app_client):
    response = app_client.get("/probes")
    assert response.status_code == 200

    data = response.json()
    assert "probes" in data
    assert isinstance(data["probes"], list)
    assert data["probes"] == []


@pytest.mark.asyncio
async def test_list_probes_with_single_data(app_client, probe_a):
    response = app_client.get("/probes")
    assert response.status_code == 200

    data = response.json()
    probes = data["probes"]

    assert isinstance(probes, list)
    assert len(probes) == 1

    probe = probes[0]
    assert probe["id"] == str(probe_a.id)
    assert probe["x"] == probe_a.x
    assert probe["y"] == probe_a.y
    assert probe["direction"] == probe_a.direction



@pytest.mark.asyncio
async def test_list_probes_with_multiple_data(app_client, probe_a, probe_b):
    response = app_client.get("/probes")
    assert response.status_code == 200

    data = response.json()
    probes = data["probes"]

    assert isinstance(probes, list)
    assert len(probes) == 2

    ids = [p["id"] for p in probes]
    assert str(probe_a.id) in ids
    assert str(probe_b.id) in ids

    for p in probes:
        assert set(p.keys()) == {"id", "x", "y", "direction"}
        assert isinstance(p["id"], str)
        assert isinstance(p["x"], int)
        assert isinstance(p["y"], int)
        assert p["direction"] in ["NORTH", "SOUTH", "EAST", "WEST"]
