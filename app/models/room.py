from sqlalchemy import String, text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.models import Base


class Room(Base):
    __tablename__ = "room"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True, server_default=text("nextval('room_id_seq')"))
    name: Mapped[str] = mapped_column(String(30))
    capacity: Mapped[int]
    location: Mapped[str] = mapped_column(String(100))
