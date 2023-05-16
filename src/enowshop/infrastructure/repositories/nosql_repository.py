from odmantic import Model
from enowshop.infrastructure.repositories.base_repository import IRepository


class NosqlRepository(IRepository):
    model = Model

    async def save(self, data):
        with self.session_factory() as session:
            return await session.save(data)

    async def get_all(self, filter: dict = None, sort=None):
        with self.session_factory() as session:
            return await session.find(self.model, filter, sort=sort)

    async def get_all_paginated(self, filter: dict = None, sort=None, offset: int = 0, limit: int = 500):
        with self.session_factory() as session:
            return await session.find(self.model, filter, sort=sort, skip=offset, limit=limit)

    async def get_count(self, filter: dict):
        with self.session_factory() as session:
            return await session.count(self.model, filter)

    async def aggregate(self, group: dict, filters: dict):
        with self.session_factory() as session:
            collection = session.get_collection(self.model)
            return await collection.aggregate([filters, group]).to_list(length=None)

    async def update_one(self, values: dict, filters: dict):
        with self.session_factory() as session:
            collection = session.get_collection(self.model)
            return await collection.update_one(filters, {'$set': values})