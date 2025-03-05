"""merge migration heads

Revision ID: 9a18bfb2d396
Revises: 0642892cc0ab, 1bcbfdc08dac
Create Date: 2025-03-05 14:49:52.380670

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a18bfb2d396'
down_revision: Union[str, None] = ('0642892cc0ab', '1bcbfdc08dac')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
