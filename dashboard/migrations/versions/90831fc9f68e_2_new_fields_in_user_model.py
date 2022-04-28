"""2 new fields in user model

Revision ID: 90831fc9f68e
Revises: 8b04663e5817
Create Date: 2022-04-01 09:49:39.095797

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '90831fc9f68e'
down_revision = '8b04663e5817'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_server_name'), 'server', ['name'], unique=False)
    op.create_index(op.f('ix_server_user'), 'server', ['user'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_server_user'), table_name='server')
    op.drop_index(op.f('ix_server_name'), table_name='server')
    # ### end Alembic commands ###
