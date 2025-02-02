"""add is_subscribed to student_groups table

Revision ID: 3b7b8c08923a
Revises: 8b41cbe8b875
Create Date: 2024-12-02 19:10:37.900652

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b7b8c08923a'
down_revision: Union[str, None] = '8b41cbe8b875'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('student_groups', sa.Column('is_subscribed', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('student_groups', 'is_subscribed')
    # ### end Alembic commands ###
