from dependency_injector import containers, providers

from config import Config
from enowshop.endpoints.orders.repository import OrdersRepository, ProductsRepository, OrderItemsRepository
from enowshop.endpoints.orders.service import OrdersService
from enowshop.infrastructure.database.database_sql import PostgresDatabase


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    postgres_db = providers.Singleton(PostgresDatabase, database_url=Config.DATABASE_URL)

    # repository
    orders_repository = providers.Factory(OrdersRepository, session_factory=postgres_db.provided.session)
    order_items_repository = providers.Factory(OrderItemsRepository, session_factory=postgres_db.provided.session)
    products_repository = providers.Factory(ProductsRepository, session_factory=postgres_db.provided.session)

    # services
    orders_service = providers.Factory(OrdersService, orders_repository=orders_repository, products_repository=products_repository,
                                       order_items_repository=order_items_repository)
