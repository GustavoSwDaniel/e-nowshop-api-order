from typing import Dict, List

from enowshop_models.models.users import Users

from enowshop.endpoints.orders.repository import ProductsRepository

from enowshop.domain.noql_models import Cars, Items
from enowshop.endpoints.cars.repository import CarsRepository, UserRepository
from enowshop.endpoints.quotes.service import QuotesService


class CarsService:
    def __init__(self, cars_repository: CarsRepository,
                 products_repository: ProductsRepository,
                 user_repository: UserRepository,
                 quotes_service: QuotesService) -> None:
        self._cars_repository = cars_repository
        self._products_repository = products_repository
        self._users_repository = user_repository
        self._quotes_service = quotes_service
        

    async def create_cars(self, uuid: str):
        car = Cars(user_uuid=uuid, items=[])
        await self._cars_repository.save_if_not_exists(car)

    async def get_user_by_keycloak_uuid(self, user_uuid: str) -> Users:
        return await self._users_repository.filter_by_with_address(user_keycloack_uuid=user_uuid)

    @staticmethod
    def _build_payload_to_calc_quotes(products: Dict) -> List:
        products_cal = {'products': []}
        for product in products:
            products_cal['products'].append({
                'quantity': product.quantity_car,
                'uuid': product.uuid
            })
        return products_cal

    def define_type_send(self, type_send: str) -> int:
        type_send_dict = {
            'SEDEX': 0,
            'PAC': 1,
            'TRANSPORTADORA': 2
        }
        print(type_send)
        return type_send_dict[type_send]
    
    async def calcs_quotes(self, products: Dict, uuid_address: str) -> tuple:
        payload = self._build_payload_to_calc_quotes(products)
        quotes = await self._quotes_service.calc_quotes(products=payload, 
                                                        uuid_address=uuid_address)
        return quotes.get('quotes', [])
        

    async def get_select_quotes(self, quotes: Dict, send_type: str) -> tuple:
        type_send = self.define_type_send(send_type)
        quoet_valeu = quotes[type_send]
        quoet_valeu = float(quoet_valeu.get('valor', '0,0').replace(',', '.'))
        return quoet_valeu

    async def get_car_with_user_uuid(self, user_uuid: str, send_type: str) -> Dict:
        print(user_uuid)
        user = await self.get_user_by_keycloak_uuid(user_uuid=user_uuid)

        cart_porducts = await self._cars_repository.get_car_by_user_uuid(user_uuid=user.uuid)
        products_uuid = [item.product_uuid for item in cart_porducts.items]
        products = await self._products_repository.get_products_by_list_uuid(products_uuid)
        total  = 0
        for product in products:
            for item in cart_porducts.items:
                if product.uuid == item.product_uuid:
                    total += (product.price / 100) * item.quantity
                    setattr(product, 'quantity_car', item.quantity)

        quotes = await self.calcs_quotes(products=products, uuid_address=user.user_address[0].id)
        values =  {
            'user_uuid': cart_porducts.user_uuid,
            'items': products,
            'cart_total': f'{total:.2f}',
            'cart_total_term': f'{total:.2f}',
            'quoets': quotes,
            'cash': f'{total:.2f}'
        }
        print(send_type)
        if send_type:
            quoet_valeu = await self.get_select_quotes(quotes=quotes, send_type=send_type)
            values['quoet_value'] = f'{quoet_valeu:.2f}'
            values['cash'] = f'{total + quoet_valeu:.2f}'
            values['quoets'] = quotes

        return values

    async def add_item_in_car(self, data, user_uuid: str):
        user = await self.get_user_by_keycloak_uuid(user_uuid=user_uuid)
        data['quantity'] = 1
        car = await self._cars_repository.add_item_in_car(user_uuid=user.uuid, new_item=data)

    async def remove_item_in_car(self, item_uuid: str, user_uuid: str):
        user = await self.get_user_by_keycloak_uuid(user_uuid=user_uuid)
        await self._cars_repository.remove_item_of_car(user_uuid=user.uuid, item_uuid=item_uuid)

    async def change_quantity_item_in_car(self, item_uuid: str, user_uuid: str, new_quantity: int):
        await self._cars_repository.change_quantity_item_in_car(item_uuid=item_uuid, user_uuid=user_uuid,
                                                                new_quantity=new_quantity)