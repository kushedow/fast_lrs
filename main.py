import os
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from loguru import logger
from src.models.statement import Statement
from src.classes.chmanager import ClickhouseManager

ch_manager = ClickhouseManager()

# VALID_VERBS = {
#     'initialized', 'launched', 'terminated', 'completed', 'passed',
#     'failed', 'satisfied', 'waived', 'abandoned', 'progressed',
#     'voided', 'attempted', 'interacted', 'experienced', 'answered',
#     'hintrequested'
# }

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Async context manager for application lifecycle with pre-start validation"""

    try:
        # Настраиваем асинхронный клиент ClickHouse
        await ch_manager.set_client()
        # Проверяем наличие необходимых переменных окружения
        ch_manager.check_environment()
        # Создаем таблицу в LRS если ее еще нет
        await ch_manager.check_and_create_table()
        logger.info("Database connection established")
        yield
    finally:
        logger.info("Shutting down application")

app = FastAPI(lifespan=lifespan)


@app.post("/simple/statement/")
async def create_statement(statement: Statement) -> dict:
    logger.info(f"Received statement: {statement.model_dump()}")

    try:
        result = await ch_manager.insert_statement(statement)
        logger.success("Statement saved successfully")
        return result
    except Exception as e:
        logger.error(f"Error saving statement: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


if (__name__ == "__main__"):
    uvicorn.run(app, host="0.0.0.0", port=8001)
