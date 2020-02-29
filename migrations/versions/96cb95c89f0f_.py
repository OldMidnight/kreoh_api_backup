"""empty message

Revision ID: 96cb95c89f0f
Revises: 
Create Date: 2020-02-29 09:50:41.584188

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '96cb95c89f0f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('mailing_list',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('domain', sa.String(length=20), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('email_confirmed', sa.Boolean(), nullable=False),
    sa.Column('skip_tutorial', sa.Boolean(), nullable=False),
    sa.Column('creation_date', sa.DateTime(), nullable=False),
    sa.Column('f_name', sa.String(), nullable=False),
    sa.Column('s_name', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('account_type', sa.Integer(), nullable=False),
    sa.Column('storage_space', sa.Integer(), nullable=False),
    sa.Column('dark_mode', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('domain'),
    sa.UniqueConstraint('email')
    )
    op.create_table('support_message',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('subject', sa.String(), nullable=False),
    sa.Column('body', sa.String(), nullable=False),
    sa.Column('time_sent', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('temp_website',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('domain', sa.String(), nullable=False),
    sa.Column('activation_date', sa.DateTime(), nullable=True),
    sa.Column('created_date', sa.DateTime(), nullable=False),
    sa.Column('expiration_date', sa.DateTime(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('site_props', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['domain'], ['user.domain'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('domain'),
    sa.UniqueConstraint('user_id')
    )
    op.create_table('upload',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('url', sa.String(), nullable=False),
    sa.Column('size', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('upload_date', sa.DateTime(), nullable=False),
    sa.Column('ext', sa.String(), nullable=True),
    sa.Column('label', sa.String(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('website',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('domain', sa.String(), nullable=False),
    sa.Column('activation_date', sa.DateTime(), nullable=True),
    sa.Column('created_date', sa.DateTime(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('site_props', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['domain'], ['user.domain'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('domain'),
    sa.UniqueConstraint('user_id')
    )
    op.create_table('message',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('support_ticket_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('sender_name', sa.String(), nullable=False),
    sa.Column('sender_address', sa.String(), nullable=False),
    sa.Column('subject', sa.String(), nullable=False),
    sa.Column('body', sa.String(), nullable=False),
    sa.Column('read', sa.Boolean(), nullable=False),
    sa.Column('user_sent', sa.Boolean(), nullable=True),
    sa.Column('time_sent', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['support_ticket_id'], ['support_message.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('website_stats',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('domain', sa.String(), nullable=False),
    sa.Column('cta_inter', sa.Boolean(), nullable=True),
    sa.Column('visit_date_time', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['domain'], ['website.domain'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('website_stats')
    op.drop_table('message')
    op.drop_table('website')
    op.drop_table('upload')
    op.drop_table('temp_website')
    op.drop_table('support_message')
    op.drop_table('user')
    op.drop_table('mailing_list')
    # ### end Alembic commands ###
