import base64
import datetime
import io
import json
from typing import Dict, List
from uuid import uuid4

from enowshop.endpoints.paginate import paginate
from enowshop.endpoints.quotes.service import QuotesService
from decimal import Decimal
import pyqrcode

from enowshop.endpoints.orders.repository import OrdersRepository, ProductsRepository, OrderItemsRepository
from enowshop.endpoints.cars.repository import UserRepository
from enowshop.endpoints.quotes.repository import UsersAddressRepository
from enowshop_payment.orders.build import BuildPayment
from pubnub.pubnub import PubNub


class OrdersService:
    def __init__(self, orders_repository: OrdersRepository, products_repository: ProductsRepository,
                 order_items_repository: OrderItemsRepository, user_reponsitory: UserRepository,
                 user_address_repository: UsersAddressRepository,
                 quotes_service: QuotesService, payment_access_token: Dict,
                 pubnub_client: PubNub):
        self.orders_repository = orders_repository
        self.products_repository = products_repository
        self.order_items_repository = order_items_repository
        self.user_reponsitory = user_reponsitory
        self.user_address_repository = user_address_repository
        self.quotes_service = quotes_service
        self.payment_access_token = payment_access_token
        self.pubnub_client = pubnub_client

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
    
    async def sum_products(self, products: List[Dict]) -> float:
        total = 0
        for product in products:
            product_data = await self.products_repository.get_products_by_uuid(uuid=product['uuid'])
            total += (product_data.price / 100) * product['quantity']

        return total

    async def build_pix_payload(self, products: List, quote_value: float):
        return {
            'total_value': 100,
            'user_info': { # round(Decimal(payload_payment.get("total_value")), 2)
                'email': 'gustavodanieldetoledo@gmail.com',
                'first_name': 'gustavo',
                'last_name': 'daniel'
            }
        }
    
    async def get_user_data(self, user_uuid_keycloak: str):
        return await self.user_reponsitory.filter_by    ({'keycloak_uuid': user_uuid_keycloak})
    
    async def calc_quotes(self, address_id, products, type_quote):
       quote_value = await self.quotes_service.calc_quote(products={"products": products}, 
                                                    uuid_address=address_id, 
                                                    type_quote=type_quote)
       return quote_value

    def build_payload_topic(self, payment_id: str, order_uuid: str) -> Dict:
        return {
            'payment_id': payment_id,
            'order_uuid': order_uuid
        }


    async def create_order(self, order_data: Dict, user_uuid_keycloak: str) -> Dict:
        products_data = order_data.pop('items')
        order_uuid = str(uuid4())

        user_data = await self.get_user_data(user_uuid_keycloak=user_uuid_keycloak)

        quote_info = await self.calc_quotes(address_id=order_data.pop('address_id'), 
                                       products=products_data, 
                                       type_quote=order_data.pop('quote_type'))
        quote_value = float(quote_info.get('quotes')[0]['valor'].replace(',', '.'))
        order_data['user_id'] = user_data.id
        order_data['uuid'] = order_uuid

        order = await self.orders_repository.create(order_data)
        payload_payment = await self.build_pix_payload(products=products_data, quote_value=quote_value)
        payment = BuildPayment(payment_type='PIX').build_payment()
        payment_info = payment.create_order(order_data=payload_payment, access_key=self.payment_access_token['PIX'])

        channel_uuid = str(uuid4())

        update_order = await self.orders_repository.update(pk=order.id, values={
            'total_amount': int(payload_payment['total_value'] * 100),
            'installments': 1,
            'meta_data': {'pubnub': {'status': 'active', 'uuid': channel_uuid}, 'payment': payment_info.__dict__}
        })

        products_uuid = [product_uuid['uuid'] for product_uuid in products_data]
        products = await self.products_repository.get_products_by_list_uuid(uuids=products_uuid)
        products_id = [product_id.id for product_id in products]

        order_items = self.__build_order_items(products_id=products_id, order_id=order.id)

        await self.order_items_repository.create_order_items(order_items=order_items)
        

        r = {'uuid': order_uuid, 'channel_uuid': channel_uuid, 'payment_info': {'total_value': payload_payment['total_value'] , 'qrcode': payment_info.qrcode,
                                                     'qrcode_text': payment_info.qrcode_text}, 'quote_info': quote_info}

        return r

    async def get_order_by_uuid(self, order_uuid: str):
        ...

    async def get_all_orders(self, params: Dict) -> List:
        results, total =  await self.orders_repository.get_all_order_with_parans(params=params)
        return paginate(results, params.get('offset'), total)

    async def update_order_status(self, order_uuid: str, status: str) -> None:
        self.orders_repository.update(pk=order_uuid, values={'status': status})
    
    async def check_and_update_orders(self, data: Dict) -> None:
        payment = BuildPayment(payment_type='PIX').build_payment()
        # payment_info = payment.get_order(access_key=self.payment_access_token['PIX'], order_id=data['data']['id'])

        order = await self.orders_repository.filter_by_json_order_mp_id(id=data['data']['id'])
        if order:
            self.pubnub_client.publish().channel(order.meta_data['pubnub']['uuid']).message({'status': 'approved'}).sync()
            await self.orders_repository.update(pk=order.id, values={'status': 'approved', 'payment_date': datetime.datetime.now(),
                                                                     'payment_id': data['id']})



        