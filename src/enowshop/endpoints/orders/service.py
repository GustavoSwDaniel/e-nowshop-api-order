import base64
import datetime
import io
from typing import Dict, List
from uuid import uuid4

import pyqrcode

from enowshop.endpoints.orders.repository import OrdersRepository, ProductsRepository, OrderItemsRepository
from enowshop_payment.orders.build import BuildPayment


class OrdersService:
    def __init__(self, orders_repository: OrdersRepository, products_repository: ProductsRepository,
                 order_items_repository: OrderItemsRepository):
        self.orders_repository = orders_repository
        self.products_repository = products_repository
        self.order_items_repository = order_items_repository

    @staticmethod
    def __build_order_items(products_id: List[int], order_id: int) -> List[Dict]:
        order_items = []
        for product_id in products_id:
            order_items.append({'product_id': product_id, 'order_id': order_id})

        return order_items

    @staticmethod
    def __pix_payment(self, value: int):
        qrcode_data = {'type': 'pix', 'value': {value}}
        code = pyqrcode.create(str(qrcode_data))
        file = io.BytesIO()
        code.png(file, scale=6)
        encoded = base64.b64encode(file.getvalue()).decode("ascii")
        return {
            'value': value,
            'base64': 'data:image/png;base64,' + encoded,
            'expiration_date': datetime.datetime.now()
        }

    @staticmethod
    def build_pix_payload():
        return {
            'total_value': 4,
            'user_info': {
                'email': 'gustavodanieldetoledo@gmail.com',
                'first_name': 'gustavo',
                'last_name': 'daniel'
            }
        }

    async def create_order(self, order_data: Dict, user_id: int = 1) -> Dict:
        products_data = order_data.pop('items')
        order_uuid = str(uuid4())

        order_data['user_id'] = user_id
        order_data['uuid'] = order_uuid

        order = await self.orders_repository.create(order_data)
        payment = BuildPayment(payment_type='PIX').build_payment()
        payment_info = payment.create_order(order_data=self.build_pix_payload())

        products_uuid = [product_uuid['uuid'] for product_uuid in products_data]
        products = await self.products_repository.get_products_by_list_uuid(uuids=products_uuid)
        products_id = [product_id.id for product_id in products]

        order_items = self.__build_order_items(products_id=products_id, order_id=order.id)

        await self.order_items_repository.create_order_items(order_items=order_items)

        return {'uuid': order_uuid, 'payment_info': {'total_value':order.total_amount ,'qrcode': payment_info.qrcode, 'qrcode_text': payment_info.qrcode_text}}

    async def get_order_by_uuid(self, order_uuid: str):
        ...

    async def get_all_orders(self, params: Dict) -> List:
        ...

    async def update_order_status(self, order_uuid: str):
        ...
