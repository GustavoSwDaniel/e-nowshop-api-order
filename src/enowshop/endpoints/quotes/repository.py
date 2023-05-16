from enowshop_models.models.users_address import UserAddress

from enowshop.infrastructure.repositories.repository import SqlRepository


class UsersAddressRepository(SqlRepository):
    model = UserAddress
