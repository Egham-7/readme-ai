"""add_fulltext_search_indexes

Revision ID: 56490874b868
Revises: 9a18bfb2d396
Create Date: 2025-03-05 16:53:30.560315

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "56490874b868"
down_revision: Union[str, None] = "9a18bfb2d396"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create GIN index on readmes.title
    op.execute(
        "CREATE INDEX idx_readmes_title_fts ON readmes USING GIN (to_tsvector('english', title))"
    )

    # Create GIN index on readmes.repository_url
    op.execute(
        "CREATE INDEX idx_readmes_repo_url_fts ON readmes USING GIN (to_tsvector('english', repository_url))"
    )

    # Create GIN index on readme_versions.content
    op.execute(
        "CREATE INDEX idx_readme_versions_content_fts ON readme_versions USING GIN (to_tsvector('english', content))"
    )


def downgrade():
    # Drop the indexes we created
    op.execute("DROP INDEX IF EXISTS idx_readmes_title_fts")
    op.execute("DROP INDEX IF EXISTS idx_readmes_repo_url_fts")
    op.execute("DROP INDEX IF EXISTS idx_readme_versions_content_fts")
