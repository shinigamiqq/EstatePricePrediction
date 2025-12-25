"""создание таблицы request_history

Revision ID: 001
Revises: 
Create Date: 2024-12-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # создаем таблицу для хранения истории запросов
    op.create_table(
        'request_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('input_data', sa.Text(), nullable=False),
        sa.Column('input_length', sa.Integer(), nullable=False),
        sa.Column('prediction', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('processing_time_ms', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    # индексы для быстрого поиска
    op.create_index(op.f('ix_request_history_id'), 'request_history', ['id'], unique=False)
    op.create_index(op.f('ix_request_history_timestamp'), 'request_history', ['timestamp'], unique=False)


def downgrade() -> None:
    # откат - удаляем всё что создали
    op.drop_index(op.f('ix_request_history_timestamp'), table_name='request_history')
    op.drop_index(op.f('ix_request_history_id'), table_name='request_history')
    op.drop_table('request_history')
