import os

from dotenv import load_dotenv


class Config:
    load_dotenv()

    BROKER_URL = os.getenv('BROKER_URL', 'localhost:9092')

    DATABASE_URL = os.getenv(
        'A-POSTGRES_DATABASE_URL', 'postgresql+asyncpg://enowshop:enowshop@127.0.0.1:5432/enowshop')
    
    MONGO_DATABASE_DB = os.getenv('MONGO_DATABASE_DB', 'enowshop')
    MONGO_DATABASE_HOST = os.getenv('MONGO_DATABASE_HOST', 'localhost')
    MONGO_DATABASE_PORT = int(os.getenv('MONGO_DATABASE_PORT', 27017))
    MONGO_DATABASE_USER = os.getenv('MONGO_DATABASE_USER', 'enowshop')
    MONGO_DATABASE_PASSWORD = os.getenv('MONGO_DATABASE_PASSWORD', 'enowshop')
    MONGO_DATABASE_AUTH_SOURCE = os.getenv('MONGO_DATABASE_AUTH_SOURCE', 'admin')
    PAYMENT_ACCESS = {
        'PIX': 'APP_USR-8323930387031655-011018-9d10499319c25087b0d176c30307a38b-273630370'
    }
    URL_CORREIOS = os.getenv('URL_CORREIOS', 'http://ws.correios.com.br/calculador/CalcPrecoPrazo.asmx?WSDL')

    KEYCLOAK_PUBLIC_KEY = os.getenv('KEYCLOAK_PUBLIC_KEY')

    ORIGIN_CEP = os.getenv('ORIGIN_CEP', '01153000')
    
    PUBNUB_SUBSCRIBE_KEY = os.getenv('PUBNUB_SUBSCRIBE_KEY', 'sub-c-47cab205-d6cf-4e9f-91a7-bbb42cc8544c')
    PUBNUB_PUBLISH_KEY = os.getenv('PUBNUB_PUBLISH_KEY', 'pub-c-b572a862-efaa-4b28-9462-82d0cb72a57c')
