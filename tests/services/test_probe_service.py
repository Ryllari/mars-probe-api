import pytest
from fastapi import HTTPException

from mars_probe_api.models.probe import Probe
from mars_probe_api.services.probe_service import ProbeService, DIRECTIONS


class TestProbeService:
    @pytest.mark.parametrize(
        "initial_dir,left,expected",
        [
            ("NORTH", True, "WEST"),
            ("NORTH", False, "EAST"),
            ("EAST", True, "NORTH"),
            ("EAST", False, "SOUTH"),
            ("SOUTH", True, "EAST"),
            ("SOUTH", False, "WEST"),
            ("WEST", True, "SOUTH"),
            ("WEST", False, "NORTH"),
        ],
    )
    def test_turn_rotations(self, initial_dir, left, expected):
        result = ProbeService._turn(initial_dir, left)
        assert result == expected

    @pytest.mark.parametrize(
        "direction, initial_x, initial_y, expected_x, expected_y",
        [
            ("NORTH", 2, 2, 2, 3),
            ("EAST", 2, 2, 3, 2),
            ("SOUTH", 2, 2, 2, 1),
            ("WEST", 2, 2, 1, 2),
        ],
    )
    def test_move_valid_within_bounds(
        self, direction, initial_x, initial_y, expected_x, expected_y
    ):
        probe = Probe(
            x=initial_x, y=initial_y, direction=direction, size_x=5, size_y=5
        )
        
        ProbeService._move(probe)
        assert probe.x == expected_x
        assert probe.y == expected_y


    @pytest.mark.parametrize(
        "direction, initial_x, initial_y",
        [
            ("NORTH", 0, 5),
            ("EAST", 5, 0),
            ("SOUTH", 0, 0),
            ("WEST", 0, 0),
        ],
    )
    def test_move_out_of_bounds_raises(self, direction, initial_x, initial_y):
        probe = Probe(
            x=initial_x, y=initial_y, direction=direction, size_x=5, size_y=5
        )
        with pytest.raises(HTTPException) as exc:
            ProbeService._move(probe)
        assert "exceed grid limits" in str(exc.value.detail)

    @pytest.mark.parametrize("commands", ["", "  ", "MXR", "Q", "MMRQ1"])
    def test_validate_commands_invalid(self, commands):
        with pytest.raises(HTTPException):
            ProbeService.validate_commands(commands)

    @pytest.mark.parametrize("commands", ["M", "L", "R", "MLRM"])
    def test_validate_commands_valid(self, commands):
        ProbeService.validate_commands(commands)

    @pytest.mark.parametrize(
        "direction,commands,expected_x,expected_y,expected_direction",
        [
            ("NORTH", "M", 0, 1, "NORTH"),
            ("EAST", "M", 1, 0, "EAST"),
            ("NORTH", "RMM", 2, 0, "EAST"),
            ("WEST", "RR", 0, 0, "EAST"),
        ],
    )
    def test_execute_commands_valid(
        self, direction, commands, expected_x, expected_y, expected_direction
    ):
        probe = Probe(x=0, y=0, direction=direction, size_x=7, size_y=7)
        ProbeService.execute_commands(probe, commands)
        assert probe.x == expected_x
        assert probe.y == expected_y
        assert probe.direction == expected_direction


    def test_execute_commands_partial_sequence_rollback(self):
        probe = Probe(x=0, y=0, direction="EAST", size_x=2, size_y=2)
        commands = "MMM" 
        with pytest.raises(HTTPException):
            ProbeService.execute_commands(probe, commands)

        assert probe.x == 0
        assert probe.y == 0
        assert probe.direction == "EAST"
