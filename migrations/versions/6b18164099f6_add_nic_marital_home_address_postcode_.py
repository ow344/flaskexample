"""Add nic marital home_address postcode email to staff

Revision ID: 6b18164099f6
Revises: 4afcd9968119
Create Date: 2023-11-16 15:41:50.156102

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6b18164099f6'
down_revision = '4afcd9968119'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('staff', schema=None) as batch_op:
        batch_op.add_column(sa.Column('nic', sa.String(length=12), nullable=True))
        batch_op.add_column(sa.Column('marital', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('home_address', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('postcode', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('email', sa.String(length=80), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('staff', schema=None) as batch_op:
        batch_op.drop_column('email')
        batch_op.drop_column('postcode')
        batch_op.drop_column('home_address')
        batch_op.drop_column('marital')
        batch_op.drop_column('nic')

    # ### end Alembic commands ###
