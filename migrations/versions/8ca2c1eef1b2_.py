"""empty message

Revision ID: 8ca2c1eef1b2
Revises: 
Create Date: 2017-07-21 01:38:29.276014

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '8ca2c1eef1b2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('tg_id', sa.BigInteger(), nullable=True),
                    sa.Column('first_name', sa.String(length=255), nullable=True),
                    sa.Column('last_name', sa.String(length=255), nullable=True),
                    sa.Column('username', sa.String(length=100), nullable=True),
                    sa.Column('auth', sa.String(length=255), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('tg_id')
                    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    # ### end Alembic commands ###
