# This file is a part of MediaDrop (https://www.mediadrop.video),
# Copyright 2009-2018 MediaDrop contributors
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.
"""add podcast sort order

Podcasts are listed in an order chosen by the admins instead of alphabetically.
Existing podcasts keep their current (alphabetical) order. This migration can
not be run offline.

added: 2026-09-30 (v0.11dev)

Revision ID: 3e45a8d8745c
Revises: 4979e106cad8
Create Date: 2026-09-30 06:31:35.541758
"""

# revision identifiers, used by Alembic.
revision = '3e45a8d8745c'
down_revision = '4979e106cad8'

from alembic import context
from alembic.op import add_column, drop_column
from sqlalchemy import Integer, Unicode
from sqlalchemy import Column, MetaData, Table, sql

# -- table definition ---------------------------------------------------------
metadata = MetaData()
podcasts = Table('podcasts', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('title', Unicode(50), nullable=False),
    Column('sort_order', Integer, nullable=False, server_default=sql.text('0')),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)
# -----------------------------------------------------------------------------

def upgrade():
    if context.is_offline_mode():
        raise AssertionError('This migration can not be run in offline mode.')
    add_column('podcasts',
        Column('sort_order', Integer, nullable=False, server_default=sql.text('0')))

    # Keep listing the existing podcasts in their current (alphabetical) order.
    connection = context.get_context().connection
    query = sql.select([podcasts.c.id]).order_by(podcasts.c.title, podcasts.c.id)
    podcast_ids = [row.id for row in connection.execute(query)]
    for sort_order, podcast_id in enumerate(podcast_ids, 1):
        connection.execute(
            podcasts.update().\
                where(podcasts.c.id == podcast_id).\
                values(sort_order=sort_order)
        )

def downgrade():
    drop_column('podcasts', 'sort_order')
