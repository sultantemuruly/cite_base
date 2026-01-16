"""renames document_uuid to document_uuids in Docs model

Revision ID: 71fed11a91d2
Revises: e1c94591b778
Create Date: 2026-01-16 23:24:58.737610

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '71fed11a91d2'
down_revision: Union[str, Sequence[str], None] = 'e1c94591b778'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
