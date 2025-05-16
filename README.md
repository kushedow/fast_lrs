# FastLRS - Lightweight Learning Record Store

A high-performance Learning Record Store (LRS) implementation supporting xAPI and cmi5 specifications, built with FastAPI and ClickHouse.

## Features

- 📝 xAPI/cmi5 statement validation and storage
- 🚀 FastAPI-powered REST API endpoints
- 🐘 ClickHouse cloud database integration
- 📊 Automatic table schema management
- 📊 Loguru-based logging system

## Installation

1. Clone repository:
```bash
git clone https://github.com/kushedow/fast_lrs.git
cd fast_lrs
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set environment

```
CLICKHOUSE_HOST=your.clickhouse.host
CLICKHOUSE_USERNAME=your_username
CLICKHOUSE_PASSWORD=your_password
CLICKHOUSE_DB=lrs_prod
```

4. Run

```bash
uvicorn main:app --host 0.0.0.0 --port 10000 --reload
```

## API Docs

```bash
/docs
```

