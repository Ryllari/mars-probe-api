import uuid

from sqlalchemy import Column, Integer, String, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from mars_probe_api.models import table_registry


@table_registry.mapped_as_dataclass
class Probe:
    __tablename__ = "probes"
    __table_args__ = (
        CheckConstraint(
            "direction IN ('NORTH', 'SOUTH', 'EAST', 'WEST')",
            name="check_direction_valid"
        ),
        CheckConstraint("size_x >= 0", name="check_size_x_non_negative"),
        CheckConstraint("size_y >= 0", name="check_size_y_non_negative"),
        CheckConstraint("x >= 0", name="check_x_non_negative"),
        CheckConstraint("y >= 0", name="check_y_non_negative"),
    )

    size_x: Mapped[int] = mapped_column(Integer, nullable=False)
    size_y: Mapped[int] = mapped_column(Integer, nullable=False)
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default_factory=uuid.uuid4)
    x: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    y: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    direction: Mapped[str] = mapped_column(String(5), nullable=False, default="NORTH")

