from typing import List, Dict
from enowshop_models.models.users import Users
from enowshop_models.models.orders import Orders
from enowshop_models.models.products import Products
from enowshop_models.models.order_items import OrderItems
from sqlalchemy import select, insert, func
from enowshop.infrastructure.repositories.repository import SqlRepository
from sqlalchemy import Unicode

class OrdersRepository(SqlRepository):
    model = Orders

    async def get_all_order_with_parans(self, params: Dict):
        async with self.session_factory() as session:
            query = select(self.model).limit(params.get('limit')).offset(params.get('offset'))
            if params.get('status'):
                query = query.where(self.model.status == params.get('status'))
            
            total = await session.execute(select([func.count(Products.id)]).select_from(Products))
            results = await session.execute(query)

            total = total.scalar()
            results = results.scalars().all()

            return results, total
    
    async def get_order_by_uuid(self, uuid: str):
        async with self.session_factory() as session:
            result = await session.execute(select(self.model).where(self.model.uuid == uuid))
            return result.scalars().first()
    
    async def filter_by_json_order_mp_id(self, id):
        async with self.session_factory() as session:
            result = await session.execute(select(self.model).where(self.model.meta_data['payment']['id'].astext == id))
            return result.scalars().first()

class OrderItemsRepository(SqlRepository):
    model = OrderItems

    async def create_order_items(self, order_items: List[Dict]):
        async with self.session_factory() as session:
            result = await session.execute(insert(self.model), order_items)
            await session.commit()
    
    async def get_order_items_by_order_id(self, order_id: str):
        async with self.session_factory() as session:
            result = await session.execute(select(self.model).where(self.model.order_id == order_id))
            return result.scalars().all()


class ProductsRepository(SqlRepository):
    model = Products

    async def get_products_by_list_uuid(self, uuids: List[str]) -> List[Products]:
        async with self.session_factory() as session:
            print(uuids)
            result = await session.execute(select(self.model).where(self.model.uuid.in_(uuids)))
            return result.scalars().all()
    
    async def get_products_by_uuid(self, uuid: str) -> Products:
        async with self.session_factory() as session:
            result = await session.execute(select(self.model).where(self.model.uuid == uuid))
            return result.scalars().first()
    
    async def get_products_by_id(self, id: str) -> Products:
        async with self.session_factory() as session:
            result = await session.execute(select(self.model).where(self.model.id == id))
            return result.scalars().first()

class UserRepository(SqlRepository):
    model = Users
