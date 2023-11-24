import asyncpg
from loguru import logger
from typing import List

import config as cfg


class DictRecord(asyncpg.Record):
    def __getitem__(self, key):
        value = super().__getitem__(key)
        if isinstance(value, asyncpg.Record):
            return DictRecord(value)
        return value

    def to_dict(self):
        return self._convert_records_to_dicts(dict(super().items()))

    def _convert_records_to_dicts(self, obj):
        if isinstance(obj, dict):
            return {k: self._convert_records_to_dicts(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_records_to_dicts(item) for item in obj]
        elif isinstance(obj, asyncpg.Record):
            return dict(obj)
        else:
            return obj

    def __repr__(self):
        return str(self.to_dict())


class DB:
    db: asyncpg.Connection

    async def close(self) -> None:
        await self.db.close()

    async def init_database(self) -> None:
        self.db = await asyncpg.connect(
            host=cfg.db_host,
            port=cfg.db_port,
            user=cfg.db_user,
            password=cfg.db_password,
            database=cfg.db_name,
            record_class=DictRecord
        )

        await self._setup()
        logger.success("База данных инициализирована успешно!")

    async def _setup(self) -> None:
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id SERIAL NOT NULL PRIMARY KEY,
                date TIMESTAMP DEFAULT now(),
                who TEXT CHECK (who IN ('user', 'ai')) NOT NULL,
                status BOOLEAN NOT NULL
            );
        """)
        await self.db.execute('SET TIME ZONE "Europe/Moscow"')

    async def add_history(self, who: str, status: bool) -> None:
        await self.db.execute("INSERT INTO history(who, status) VALUES($1, $2)", who, status)

    async def get_history(self) -> List[DictRecord]:
        response = await self.db.fetch("SELECT * FROM history ORDER BY date DESC LIMIT 20")
        return response
