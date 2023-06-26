from sqlalchemy import (BigInteger, Column, Integer, MetaData, String, Table,
                        create_engine, exc)

from config import POSTGRES_URI

meta = MetaData()
users = Table(
    "Users",
    meta,
    Column("id", Integer, primary_key=True),
    Column("telegram_id", BigInteger),
    Column("balance", Integer)
)

applications = Table(
    "Applications",
    meta,
    Column("id", Integer, primary_key=True),
    Column("business", String),
    Column("platform", String),
    Column("budget_start", Integer),
    Column("budget_finish", Integer),
    Column("number", BigInteger, unique=True)
)
engine = create_engine(POSTGRES_URI)
connect = engine.connect()
meta.create_all(engine)
