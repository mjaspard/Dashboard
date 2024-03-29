"""add ssh_connection to server models/form

Revision ID: 0a57e7aad453
Revises: 74f1bb721968
Create Date: 2022-05-24 11:33:28.686486

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0a57e7aad453'
down_revision = '74f1bb721968'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('server', sa.Column('ssh_connection', sa.Boolean(), nullable=True))
    op.create_index(op.f('ix_server_ssh_connection'), 'server', ['ssh_connection'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_server_ssh_connection'), table_name='server')
    op.drop_column('server', 'ssh_connection')
    # ### end Alembic commands ###
