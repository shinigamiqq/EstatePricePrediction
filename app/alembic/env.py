from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

import sys
from pathlib import Path

# добавляем путь к проекту чтобы импортировать наши модели
sys.path.append(str(Path(__file__).resolve().parent.parent))

from database import Base
from models import RequestHistory

# конфиг алембика
config = context.config

# настройка логирования из ini файла
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# метадата для автогенерации миграций
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """оффлайн режим - генерит sql без подключения к бд"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """онлайн режим - применяет миграции к реальной бд"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


# запускаем нужный режим
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
