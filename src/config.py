import os

from dotenv import load_dotenv


class Config:
    load_dotenv()

    BROKER_URL = os.getenv('BROKER_URL', 'localhost:9092')

    DATABASE_URL = os.getenv(
        'A-POSTGRES_DATABASE_URL', 'postgresql+asyncpg://enowshop:enowshop@127.0.0.1:5432/enowshop')

    TEST = os.getenv('TEST')

