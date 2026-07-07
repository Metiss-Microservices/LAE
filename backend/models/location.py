from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from database import Base


class Location(Base):
    __tablename__ = "locations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String, nullable=False)

    type = Column(String)  # country / province / city / district

    parent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("locations.id"),
        nullable=True
    )

    children = relationship("Location")