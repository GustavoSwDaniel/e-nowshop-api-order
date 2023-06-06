
from typing import List

from sqlalchemy import select
from enowshop.domain.noql_models import Cars
from enowshop_models.models.users import Users
from enowshop.infrastructure.repositories.nosql_repository import NosqlRepository
from enowshop.infrastructure.repositories.repository import SqlRepository
from enowshop_models.models.users_address import UserAddress
from sqlalchemy.orm import selectinload

from exception import RepositoryException

class UserRepository(SqlRepository):
    model = Users

    async def filter_by_with_address(self, user_keycloack_uuid):
        async with self.session_factory() as session:
            result = await session.execute(
                select(self.model).options(selectinload(Users.user_address))
                .where(self.model.keycloak_uuid == user_keycloack_uuid)
                .where(self.model.user_address.any(UserAddress.main== True)))
            user = result.scalars().first()
            if not user:
                raise RepositoryException('User does not found')
            return user
        


class CarsRepository(NosqlRepository):
    model = Cars

    async def save_if_not_exists(self, data):
        with self.session_factory() as session:
            result = await session.find(self.model, self.model.user_uuid == data.user_uuid)
            if result:
                raise RepositoryException('User already has car')
            return await session.save(data)

    async def get_car_by_user_uuid(self, user_uuid: str) -> Cars:
        with self.session_factory() as session:
            result = await session.find_one(self.model, self.model.user_uuid == user_uuid)
            if not result:
                raise RepositoryException('Car does not found')
            return result

    async def add_item_in_car(self, user_uuid: str, new_item: dict):
        car = await self.get_car_by_user_uuid(user_uuid=user_uuid)
        for item in car.items:
            if item.product_uuid == new_item.get('product_uuid'):
                raise RepositoryException('Item already in car')
        with self.session_factory() as session:
            car.items.append(new_item)
            await session.save(car)
        

    async def remove_item_of_car(self, user_uuid: str, item_uuid):
        car = await self.get_car_by_user_uuid(user_uuid=user_uuid)
        for item in car.items:
            if item.product_uuid == item_uuid:
                car.items.remove(item)

        with self.session_factory() as session:
            await session.save(car)

    async def change_quantity_item_in_car(self, item_uuid: str, user_uuid: str, new_quantity: int):
        car = await self.get_car_by_user_uuid(user_uuid=user_uuid)
        if new_quantity > 0:
            for item in car.items:
                if item.product_uuid == item_uuid:
                    car.items.remove(item)
                    item.quantity = new_quantity
                    car.items.append(item)

            with self.session_factory() as session:
                await session.save(car)
        else:
            await self.remove_item_of_car(user_uuid=user_uuid, item_uuid=item_uuid)

    async def clean_car(self, user_uuid: str):
        car = await self.get_car_by_user_uuid(user_uuid=user_uuid)
        print(car.items)
        car.items = []
        print(car.items)
        with self.session_factory() as session:
            await session.save(car)