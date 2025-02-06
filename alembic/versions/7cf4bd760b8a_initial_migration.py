""" Create users table

Revision ID: 7cf4bd760b8a
Revises: 
Create Date: 2025-02-06 00:35:42.180126

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import INTEGER, VARCHAR, Column


revision: str = '7cf4bd760b8a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        Column("id", INTEGER, primary_key=True),
        Column("username", VARCHAR(50), nullable=False),
        Column("hashed_password", VARCHAR(200)),
    )


def downgrade() -> None:
    op.drop_table("users")