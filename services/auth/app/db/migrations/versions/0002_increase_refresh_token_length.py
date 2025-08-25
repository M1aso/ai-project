"""increase refresh token length

Revision ID: 0002_increase_refresh_token_length
Revises: 0001_initial
Create Date: 2025-08-25 09:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0002_increase_refresh_token_length'
down_revision = '0001_initial'
branch_labels = None
depends_on = None


def upgrade():
    """Increase refresh token column length to accommodate JWT tokens."""
    # Get database dialect to handle different database types
    connection = op.get_bind()
    dialect = connection.dialect.name
    
    if dialect == 'postgresql':
        # PostgreSQL supports ALTER COLUMN
        op.alter_column('refresh_tokens', 'token',
                       existing_type=sa.VARCHAR(length=64),
                       type_=sa.VARCHAR(length=512),
                       existing_nullable=False,
                       postgresql_using='token::varchar(512)')
    elif dialect == 'sqlite':
        # SQLite doesn't support ALTER COLUMN, so we need to recreate the table
        # First, check if the new table already exists (from previous failed runs)
        inspector = sa.inspect(connection)
        if 'refresh_tokens_new' in inspector.get_table_names():
            # Clean up from previous failed run
            op.drop_table('refresh_tokens_new')
        
        # Create new table with correct schema (family column already exists in initial migration)
        op.create_table('refresh_tokens_new',
                       sa.Column('token', sa.VARCHAR(length=512), nullable=False, primary_key=True),
                       sa.Column('user_id', sa.String(36), nullable=False),
                       sa.Column('family', sa.String(36), nullable=False),
                       sa.Column('expires_at', sa.DateTime(), nullable=False),
                       sa.Column('created_at', sa.DateTime(), nullable=False),
                       sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                       sa.UniqueConstraint('token')
                       )
        
        # Copy data from old table to new table
        op.execute('''
            INSERT INTO refresh_tokens_new (token, user_id, family, expires_at, created_at)
            SELECT token, user_id, family, expires_at, created_at 
            FROM refresh_tokens
        ''')
        
        # Drop old table
        op.drop_table('refresh_tokens')
        
        # Rename new table to original name
        op.rename_table('refresh_tokens_new', 'refresh_tokens')
        
        # Create the index (it should already exist but let's ensure it)
        op.create_index('ix_refresh_tokens_user_id_family', 'refresh_tokens', ['user_id', 'family'])
    else:
        # For other databases, try the standard approach
        op.alter_column('refresh_tokens', 'token',
                       existing_type=sa.VARCHAR(length=64),
                       type_=sa.VARCHAR(length=512),
                       existing_nullable=False)


def downgrade():
    """Revert refresh token column length back to 64 characters."""
    connection = op.get_bind()
    dialect = connection.dialect.name
    
    if dialect == 'postgresql':
        # PostgreSQL supports ALTER COLUMN
        op.alter_column('refresh_tokens', 'token',
                       existing_type=sa.VARCHAR(length=512),
                       type_=sa.VARCHAR(length=64),
                       existing_nullable=False,
                       postgresql_using='token::varchar(64)')
    elif dialect == 'sqlite':
        # SQLite requires table recreation
        # First, check if the old table already exists (from previous failed runs)
        inspector = sa.inspect(connection)
        if 'refresh_tokens_old' in inspector.get_table_names():
            # Clean up from previous failed run
            op.drop_table('refresh_tokens_old')
        
        op.create_table('refresh_tokens_old',
                       sa.Column('token', sa.VARCHAR(length=64), nullable=False, primary_key=True),
                       sa.Column('user_id', sa.String(36), nullable=False),
                       sa.Column('family', sa.String(36), nullable=False),
                       sa.Column('expires_at', sa.DateTime(), nullable=False),
                       sa.Column('created_at', sa.DateTime(), nullable=False),
                       sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                       sa.UniqueConstraint('token')
                       )
        
        # Copy data from current table to old table (truncating tokens > 64 chars)
        op.execute('''
            INSERT INTO refresh_tokens_old (token, user_id, family, expires_at, created_at)
            SELECT substr(token, 1, 64) as token, user_id, family, expires_at, created_at 
            FROM refresh_tokens
        ''')
        
        # Drop current table
        op.drop_table('refresh_tokens')
        
        # Rename old table to original name
        op.rename_table('refresh_tokens_old', 'refresh_tokens')
        
        # Create the index
        op.create_index('ix_refresh_tokens_user_id_family', 'refresh_tokens', ['user_id', 'family'])
    else:
        # For other databases, try the standard approach
        op.alter_column('refresh_tokens', 'token',
                       existing_type=sa.VARCHAR(length=512),
                       type_=sa.VARCHAR(length=64),
                       existing_nullable=False)
