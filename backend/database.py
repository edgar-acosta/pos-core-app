from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

engine = create_engine(f"sqlite:///{os.path.join(os.path.dirname(__file__), 'core.db')}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def create_tables():
    """Import models and create DB tables. Safe to call on startup."""
    # import here to avoid circular imports at module import time
    import backend.models as models  # noqa: F401

    Base.metadata.create_all(bind=engine)

    # ensure columns exist in usuarios (SQLite simple migration)
    with engine.begin() as conn:
        cols = conn.exec_driver_sql("PRAGMA table_info('usuarios')").fetchall()
        colnames = [c[1] for c in cols]
        migrations = {
            'empleado_id': "ALTER TABLE usuarios ADD COLUMN empleado_id INTEGER",
            'status': "ALTER TABLE usuarios ADD COLUMN status VARCHAR DEFAULT 'activo'",
            'must_change_password': "ALTER TABLE usuarios ADD COLUMN must_change_password BOOLEAN DEFAULT 0",
            'failed_login_attempts': "ALTER TABLE usuarios ADD COLUMN failed_login_attempts INTEGER DEFAULT 0",
            'locked_until': "ALTER TABLE usuarios ADD COLUMN locked_until DATETIME",
            'created_at': "ALTER TABLE usuarios ADD COLUMN created_at DATETIME",
            'updated_at': "ALTER TABLE usuarios ADD COLUMN updated_at DATETIME",
            'last_login_at': "ALTER TABLE usuarios ADD COLUMN last_login_at DATETIME",
            'password_changed_at': "ALTER TABLE usuarios ADD COLUMN password_changed_at DATETIME",
            'created_by': "ALTER TABLE usuarios ADD COLUMN created_by VARCHAR",
        }
        for column_name, sql in migrations.items():
            if column_name not in colnames:
                conn.exec_driver_sql(sql)

        conn.exec_driver_sql("UPDATE usuarios SET status = COALESCE(status, 'activo')")
        conn.exec_driver_sql("UPDATE usuarios SET must_change_password = COALESCE(must_change_password, 0)")
        conn.exec_driver_sql("UPDATE usuarios SET failed_login_attempts = COALESCE(failed_login_attempts, 0)")
        conn.exec_driver_sql("UPDATE usuarios SET must_change_password = 1 WHERE password_changed_at IS NULL")


# Create tables immediately on import to preserve previous behavior.
create_tables()