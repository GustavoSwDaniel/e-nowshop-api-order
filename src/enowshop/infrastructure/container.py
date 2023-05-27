from dependency_injector import containers, providers

from config import Config
from enowshop.endpoints.cars.repository import CarsRepository, UserRepository
from enowshop.endpoints.cars.service import CarsService
from enowshop.endpoints.orders.repository import OrdersRepository, ProductsRepository, OrderItemsRepository
from enowshop.endpoints.orders.service import OrdersService
from enowshop.endpoints.quotes.service import QuotesService
from enowshop.endpoints.quotes.repository import UsersAddressRepository
from enowshop.infrastructure.database.database_sql import PostgresDatabase
from enowshop.infrastructure.database.nosql import MongoDatabase
from enowshop.infrastructure.cache.redis import RedisCache
from enowshop.domain.correios.client import CorreiosClient
from zeep import Client as SoapClient
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    # Config database
    postgres_db = providers.Singleton(PostgresDatabase, database_url=Config.DATABASE_URL)

    # Config database
    mongo_database = providers.Singleton(MongoDatabase, database=Config.MONGO_DATABASE_DB,
                                         host=Config.MONGO_DATABASE_HOST, port=Config.MONGO_DATABASE_PORT,
                                         user=Config.MONGO_DATABASE_USER, password=Config.MONGO_DATABASE_PASSWORD,
                                         authentication_source=Config.MONGO_DATABASE_AUTH_SOURCE)
    
    # zeep client soap
    zeep_client = providers.Singleton(SoapClient, wsdl=Config.URL_CORREIOS)

    # correios
    correios = providers.Singleton(CorreiosClient, client_soap=zeep_client)

    # redis cache
    # redis_cache = providers.Singleton(RedisCache, host=Config.REDIS_CACHE_HOST, password=Config.REDIS_CACHE_PASSWORD)

    # repository
    orders_repository = providers.Factory(OrdersRepository, session_factory=postgres_db.provided.session)
    order_items_repository = providers.Factory(OrderItemsRepository, session_factory=postgres_db.provided.session)
    products_repository = providers.Factory(ProductsRepository, session_factory=postgres_db.provided.session)
    cars_repository = providers.Factory(CarsRepository, session_factory=mongo_database.provided.session)
    user_address_repository = providers.Factory(UsersAddressRepository, session_factory=postgres_db.provided.session)
    user_repository = providers.Factory(UserRepository, session_factory=postgres_db.provided.session)


    #pubnub
    pnconfig = PNConfiguration()
    pnconfig.subscribe_key =  Config.PUBNUB_SUBSCRIBE_KEY
    pnconfig.publish_key = Config.PUBNUB_PUBLISH_KEY
    pnconfig.ssl = False
    pnconfig.user_id = "payment-agent"
    pn = providers.Factory(PubNub, pnconfig)


    # services
    quotes_service = providers.Factory(QuotesService, correios_client=correios, 
                                       products_repository=products_repository,
                                       user_address_repository=user_address_repository,
                                       origin_cep=Config.ORIGIN_CEP)
    cars_service = providers.Factory(CarsService, cars_repository=cars_repository,
                                     products_repository=products_repository,
                                     user_repository=user_repository,
                                     quotes_service=quotes_service)
    orders_service = providers.Factory(OrdersService, orders_repository=orders_repository,
                                   products_repository=products_repository,
                                   order_items_repository=order_items_repository,
                                   user_reponsitory=user_repository,
                                   user_address_repository=user_address_repository,
                                   quotes_service=quotes_service, 
                                   payment_access_token=Config.PAYMENT_ACCESS,
                                   pubnub_client=pn)