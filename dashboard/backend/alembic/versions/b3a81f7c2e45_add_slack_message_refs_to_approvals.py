"""add slack message refs to approval_requests

Revision ID: b3a81f7c2e45
Revises: d9f4c501aded
Create Date: 2026-10-16 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b3a81f7c2e45"
down_revision: str | Sequence[str] | None = "d9f4c501aded"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("approval_requests") as batch_op:
        batch_op.add_column(
            sa.Column("slack_channel", sa.String(length=64), nullable=True)
        )
        batch_op.add_column(
            sa.Column("slack_message_ts", sa.String(length=64), nullable=True)
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("approval_requests") as batch_op:
        batch_op.drop_column("slack_message_ts")
        batch_op.drop_column("slack_channel")