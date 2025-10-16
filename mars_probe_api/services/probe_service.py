from fastapi import HTTPException
from http import HTTPStatus
from mars_probe_api.models import Probe
from copy import deepcopy

DIRECTIONS = ["NORTH", "EAST", "SOUTH", "WEST"]

class ProbeService:
    VALID_COMMANDS = {"M", "L", "R"}

    @staticmethod
    def validate_commands(commands: str) -> None:
        if not commands.strip():
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Field 'commands' is required and must be a non-empty string.",
            )

        invalid = [c for c in commands if c not in ProbeService.VALID_COMMANDS]
        if invalid:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Invalid command sequence. Allowed commands: 'M', 'L', 'R'.",
            )

    @staticmethod
    def execute_commands(probe: Probe, commands: str) -> Probe:
        """Executa os comandos sequenciais de rotação e movimento."""

        ProbeService.validate_commands(commands)

        # Cria uma cópia temporária para validar toda a sequência
        temp_probe = deepcopy(probe)

        try:
            for command in commands:
                if command == "L":
                    temp_probe.direction = ProbeService._turn(temp_probe.direction, left=True)
                elif command == "R":
                    temp_probe.direction = ProbeService._turn(temp_probe.direction, left=False)
                elif command == "M":
                    ProbeService._move(temp_probe)  # _move levanta HTTPException se inválido
        except HTTPException as e:
            # Nenhum comando é aplicado ao probe real
            raise e

        # Aplica a sequência completa ao probe real somente se tudo passar
        probe.x, probe.y, probe.direction = temp_probe.x, temp_probe.y, temp_probe.direction
        return probe

    # --- Métodos internos privados ---
    @staticmethod
    def _turn(direction: str, left: bool) -> str:
        idx = DIRECTIONS.index(direction)
        return DIRECTIONS[(idx - 1) % 4] if left else DIRECTIONS[(idx + 1) % 4]

    @staticmethod
    def _move(probe: Probe) -> None:
        x, y = probe.x, probe.y
        match probe.direction:
            case "NORTH":
                y += 1
            case "SOUTH":
                y -= 1
            case "EAST":
                x += 1
            case "WEST":
                x -= 1

        if not (0 <= x <= probe.size_x and 0 <= y <= probe.size_y):
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Invalid move: probe would exceed grid limits."
            )

        probe.x, probe.y = x, y
