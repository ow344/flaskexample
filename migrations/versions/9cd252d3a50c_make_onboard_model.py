"""Make Onboard model

Revision ID: 9cd252d3a50c
Revises: f4fd98ac74c0
Create Date: 2023-11-27 16:27:58.719712

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9cd252d3a50c'
down_revision = 'f4fd98ac74c0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('onboard',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('firstname', sa.String(length=80), nullable=True),
    sa.Column('lastname', sa.String(length=80), nullable=True),
    sa.Column('dob', sa.Date(), nullable=True),
    sa.Column('gender', sa.String(length=20), nullable=True),
    sa.Column('nino', sa.String(length=12), nullable=True),
    sa.Column('nic', sa.String(length=12), nullable=True),
    sa.Column('marital', sa.String(length=20), nullable=True),
    sa.Column('home_address', sa.String(length=120), nullable=True),
    sa.Column('postcode', sa.String(length=20), nullable=True),
    sa.Column('email', sa.String(length=80), nullable=True),
    sa.Column('startdate', sa.Date(), nullable=True),
    sa.Column('approved', sa.Boolean(), nullable=True),
    sa.Column('r2r_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['r2r_id'], ['r2_r.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('onboard')
    # ### end Alembic commands ###
