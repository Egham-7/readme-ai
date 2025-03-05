"""Full text search for templates

Revision ID: 0642892cc0ab
Revises: b49aa35a941b
Create Date: 2025-03-05 14:12:33.524599

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0642892cc0ab"
down_revision: Union[str, None] = "b49aa35a941b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create GIN indexes for full-text search on title and content
    op.create_index(
        "idx_template_title_tsv",
        "templates",
        [sa.text("to_tsvector('english', title)")],
        postgresql_using="gin",
    )

    op.create_index(
        "idx_template_content_tsv",
        "templates",
        [sa.text("to_tsvector('english', content)")],
        postgresql_using="gin",
    )

    op.create_index(
        "idx_template_title_content_tsv",
        "templates",
        [sa.text("to_tsvector('english', title || ' ' || content)")],
        postgresql_using="gin",
    )


def downgrade() -> None:
    # Drop the indexes if we need to roll back
    op.drop_index("idx_template_title_tsv", table_name="templates")
    op.drop_index("idx_template_content_tsv", table_name="templates")
    op.drop_index("idx_template_title_content_tsv", table_name="templates")
