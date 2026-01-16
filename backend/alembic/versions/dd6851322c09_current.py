"""current

Revision ID: dd6851322c09
Revises: 71fed11a91d2
Create Date: 2026-01-16 23:37:43.654339

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dd6851322c09'
down_revision: Union[str, Sequence[str], None] = '71fed11a91d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
