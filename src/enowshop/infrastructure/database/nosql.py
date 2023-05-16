import logging
from contextlib import contextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine
from enowshop.infrastructure.database.idatabase import IDatabase

logger = logging.getLogger(__name__)


class MongoDatabase(IDatabase):
    def __init__(self, database: str, host: str, port: str, user: str, password: str,
                 authentication_source: str) -> None:
        self.database = database
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.authentication_source = authentication_source

        connection_string = f'mongodb://{self.host}:{self.port}'
        if self.user and self.password:
            connection_string = f'mongodb://{self.user}:{self.password}@{self.host}:{self.port}/' \
                                f'{self.database}?authSource={self.authentication_source}'

        self.motor_client = AsyncIOMotorClient(connection_string)
        if self.database:
            self._session_factory = AIOEngine(client=self.motor_client, database=self.database)
        else:
            self._session_factory = AIOEngine(client=self.motor_client)

    @contextmanager
    def session(self):
        session = self._session_factory
        try:
            yield session
        except Exception:
            logger.exception('Mongo Session exception')
            raise

