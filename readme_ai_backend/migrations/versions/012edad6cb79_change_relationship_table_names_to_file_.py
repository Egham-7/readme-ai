"""Change relationship table names to file_contents

Revision ID: 012edad6cb79
Revises: cc86e6320c64
Create Date: 2025-04-04 16:04:14.185558

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '012edad6cb79'
down_revision: Union[str, None] = 'cc86e6320c64'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
