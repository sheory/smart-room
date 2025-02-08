"""Create Room and Reservation table

Revision ID: 978fe1140e6e
Revises: 7cf4bd760b8a
Create Date: 2025-02-06 01:22:50.003326

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "978fe1140e6e"
down_revision: Union[str, None] = "7cf4bd760b8a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SEQUENCE room_id_seq START WITH 1 INCREMENT BY 1;")

    op.create_table(
        "room",
        sa.Column(
            "id",
            sa.INTEGER(),
            primary_key=True,
            autoincrement=True,
            server_default=sa.text("nextval('room_id_seq')"),
        ),
        sa.Column("name", sa.VARCHAR(length=50), nullable=False),
        sa.Column(
            "location", sa.VARCHAR(length=100), autoincrement=False, nullable=False
        ),
        sa.Column("capacity", sa.INTEGER(), nullable=False),
    )

    op.execute("CREATE SEQUENCE reservation_id_seq START WITH 1 INCREMENT BY 1;")
    op.create_table(
        "reservation",
        sa.Column(
            "id",
            sa.INTEGER(),
            autoincrement=True,
            primary_key=True,
            server_default=sa.text("nextval('room_id_seq')"),
        ),  # TODO - precisa mesmo dessa coluna
        sa.Column(
            "user_name", sa.VARCHAR(length=50), nullable=False
        ),  # TODO - relacionar user_id a tabela user, se for relacionar copm nome usa unique
        sa.Column("start_time", sa.TIMESTAMP(), nullable=False),
        sa.Column("end_time", sa.TIMESTAMP(), nullable=False),
        sa.Column(
            "room_id",
            sa.INTEGER(),
            sa.ForeignKey("room.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("reservation")
    op.drop_table("room")
    op.execute("DROP SEQUENCE reservation_id_seq;")
    op.execute("DROP SEQUENCE room_id_seq;")
