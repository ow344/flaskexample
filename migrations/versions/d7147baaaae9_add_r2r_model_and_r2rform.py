"""Add R2R model and R2RForm

Revision ID: d7147baaaae9
Revises: 6b18164099f6
Create Date: 2023-11-16 17:30:05.202915

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd7147baaaae9'
down_revision = '6b18164099f6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('r2_r',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('request_date', sa.Date(), nullable=True),
    sa.Column('approved', sa.Boolean(), nullable=True),
    sa.Column('department_id', sa.Integer(), nullable=True),
    sa.Column('role', sa.String(length=120), nullable=True),
    sa.Column('salary', sa.Float(), nullable=True),
    sa.Column('pension', sa.String(length=12), nullable=True),
    sa.Column('ftpt', sa.String(length=20), nullable=True),
    sa.Column('weekhours', sa.Float(), nullable=True),
    sa.Column('contract', sa.String(length=80), nullable=True),
    sa.Column('holiday', sa.String(length=80), nullable=True),
    sa.Column('notice', sa.String(length=20), nullable=True),
    sa.Column('justification', sa.Text(), nullable=True),
    sa.Column('budgeted', sa.Boolean(), nullable=True),
    sa.Column('effect_date', sa.Date(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['department_id'], ['department.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('r2_r')
    # ### end Alembic commands ###
