import json
import os
from typing import Dict, Any

from clickhouse_connect import get_async_client
from clickhouse_connect.driver.exceptions import ClickHouseError
from loguru import logger

from src.exceptions import EnvironmentConfigError
from src.models.statement import Statement


class ClickhouseManager:

    def __init__(self):
        self.client = None

    async def set_client(self):
        self.client = await get_async_client(
            port=8443,
            host=os.getenv('CLICKHOUSE_HOST'),
            username=os.getenv('CLICKHOUSE_USERNAME'),
            password=os.getenv('CLICKHOUSE_PASSWORD'),
            database=os.getenv('CLICKHOUSE_DB'),
            secure=False, verify=False
        )

    @staticmethod
    def check_environment():
        """Проверяет наличие необходимых переменных окружения"""
        required_vars: list = ['CLICKHOUSE_HOST', 'CLICKHOUSE_USERNAME', 'CLICKHOUSE_PASSWORD', 'CLICKHOUSE_DB']
        missing_vars: list = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            raise EnvironmentConfigError(missing_vars)

    async def check_and_create_table(self):
        """Проверяет существование таблицы и создает ее при необходимости"""
        db_name = os.getenv('CLICKHOUSE_DB')
        table_name = 'statements'

        # Проверка существования таблицы
        check_query = f"""SELECT count() FROM system.tables WHERE database = '{db_name}' AND name = '{table_name}'"""

        try:
            result = await self.client.query(check_query)
            if result.result_set[0][0] == 0:
                logger.info("Table 'statements' not found, creating...")
                await self._create_table()
            else:
                logger.info("Table 'statements' already exists")
        except Exception as e:
            logger.error(f"Error checking table existence: {str(e)}")
            raise

    async def _create_table(self):
        """Создает таблицу statements в ClickHouse"""
        create_query = """
            CREATE TABLE statements (
                platform_id String,
                activity_id String,
                activity_type String,
                verb_id String,
                actor_id String,
                
                timestamp DateTime DEFAULT NOW(),
                context String DEFAULT '{}'
            ) ENGINE = MergeTree()
            PRIMARY KEY (timestamp, activity_id, activity_type, verb_id ,actor_id)
            ORDER BY (timestamp, activity_id, activity_type, verb_id ,actor_id)
            """
        try:
            await self.client.command(create_query)
            logger.success("Table 'statements' created successfully")
        except Exception as e:
            logger.error(f"Error creating table: {str(e)}")
            raise

    async def get_tables(self):
        """Возвращает список таблиц в текущей базе данных"""
        db_name = os.getenv('CLICKHOUSE_DB')
        query = f""" SELECT name FROM system.tables WHERE database = '{db_name}'"""
        result = await self.client.query(query)
        return [row[0] for row in result.result_set]

    async def insert_statement(self, statement: Statement) -> dict[str, int]:
        data = {
            "platform_id": statement.platform_id,
            "activity_id": statement.activity_id,
            "activity_type": statement.activity_type,
            "verb_id": statement.verb_id,
            "actor_id": statement.actor_id,
            "context": json.dumps(statement.context) if statement.context else "{}"
        }

        try:
            result = await self.client.insert(
                table='statements',
                data=[list(data.values())],
                column_names=list(data.keys()),
                settings={'input_format_allow_errors_num': 0}
            )

            logger.debug(f"Inserted {result.written_rows} rows")
            return {"inserted" : result.written_rows}

        except ClickHouseError as e:
            logger.error(f"Insert failed: {str(e)} | Data: {data}")
            raise RuntimeError(f"Database operation failed: {str(e)}") from e
        except ValueError as e:
            logger.warning(f"Invalid data format: {str(e)}")
            raise
