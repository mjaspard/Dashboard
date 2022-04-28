"""add device in Post table

Revision ID: 2d26e09b5316
Revises: f689a1f2f1a6
Create Date: 2022-04-12 10:01:48.336571

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2d26e09b5316'
down_revision = 'f689a1f2f1a6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('post', sa.Column('device', sa.String(length=30), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('post', 'device')
    # ### end Alembic commands ###
