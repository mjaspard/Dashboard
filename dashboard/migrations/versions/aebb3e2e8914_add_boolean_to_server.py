"""add boolean to server

Revision ID: aebb3e2e8914
Revises: 45f4ce49ab0a
Create Date: 2022-04-21 17:13:20.203845

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aebb3e2e8914'
down_revision = '45f4ce49ab0a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('server', sa.Column('public_server', sa.Boolean(), nullable=True))
    op.create_index(op.f('ix_server_public_server'), 'server', ['public_server'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_server_public_server'), table_name='server')
    op.drop_column('server', 'public_server')
    # ### end Alembic commands ###