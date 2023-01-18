from typing import List, Dict
from enowshop_models.models.orders import Orders
from enowshop_models.models.products import Products
from enowshop_models.models.order_items import OrderItems
from sqlalchemy import select, insert
from enowshop.infrastructure.repositories.repository import SqlRepository


class OrdersRepository(SqlRepository):
    model = Orders


class OrderItemsRepository(SqlRepository):
    model = OrderItems

    async def create_order_items(self, order_items: List[Dict]):
        async with self.session_factory() as session:
            result = await session.execute(insert(self.model), order_items)
            await session.commit()



class ProductsRepository(SqlRepository):
    model = Products

    async def get_products_by_list_uuid(self, uuids: List[str]) -> List[Products]:
        async with self.session_factory() as session:
            result = await session.execute(select(self.model).where(self.model.uuid.in_(uuids)))
            return result.scalars().all()

