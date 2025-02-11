"""Add featured tag to boolean so in the future we can separate featured templates

Revision ID: b7a404ea711a
Revises: baa9640e39e4
Create Date: 2025-02-08 20:20:31.690612

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b7a404ea711a"
down_revision: Union[str, None] = "baa9640e39e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # First add the column as nullable
    op.add_column("templates", sa.Column("featured", sa.Boolean(), nullable=True))

    # Update existing records to have featured=False
    op.execute("UPDATE templates SET featured = FALSE WHERE featured IS NULL")

    # Then make it non-nullable
    op.alter_column("templates", "featured", existing_type=sa.Boolean(), nullable=False)


def downgrade() -> None:
    op.drop_column("templates", "featured")
