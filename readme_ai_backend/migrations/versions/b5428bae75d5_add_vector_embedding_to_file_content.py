"""Add vector embedding to file content

Revision ID: b5428bae75d5
Revises: a324a4a963e8
Create Date: 2025-04-04 13:46:57.250814
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import VECTOR  # type: ignore

# revision identifiers, used by Alembic.
revision: str = "b5428bae75d5"
down_revision: Union[str, None] = "a324a4a963e8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.add_column(
        "file_analyses",
        sa.Column("content_embedding", VECTOR(), nullable=False),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("file_analyses", "content_embedding")
    # ### end Alembic commands ###
