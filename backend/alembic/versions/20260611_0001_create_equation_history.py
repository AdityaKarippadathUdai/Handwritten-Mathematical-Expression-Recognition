"""create equation history table

Revision ID: 20260611_0001
Revises:
Create Date: 2026-06-11
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260611_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "equation_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("image_path", sa.String(length=500), nullable=False),
        sa.Column("latex_output", sa.String(length=2000), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_equation_history_created_at", "equation_history", ["created_at"])
    op.create_index("ix_equation_history_id", "equation_history", ["id"])


def downgrade() -> None:
    op.drop_index("ix_equation_history_id", table_name="equation_history")
    op.drop_index("ix_equation_history_created_at", table_name="equation_history")
    op.drop_table("equation_history")
