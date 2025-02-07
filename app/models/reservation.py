from datetime import datetime
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.models import Base


class Reservation(Base):
    __tablename__ = "reservation"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_name: Mapped[str] = mapped_column(String(30))
    start_time: Mapped[datetime]
    end_time: Mapped[datetime]
    room_id: Mapped[int] = mapped_column(ForeignKey("room.id", ondelete="CASCADE"))
