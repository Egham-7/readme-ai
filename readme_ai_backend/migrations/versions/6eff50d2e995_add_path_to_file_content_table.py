"""Add path to file content table

Revision ID: 6eff50d2e995
Revises: cc86e6320c64
Create Date: 2025-04-04 18:28:52.852246

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6eff50d2e995"
down_revision: Union[str, None] = "cc86e6320c64"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("file_contents", sa.Column("path", sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("file_contents", "path")
    # ### end Alembic commands ###
