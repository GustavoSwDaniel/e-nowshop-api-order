import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from enowshop.middlewares.exception_handler import generic_request_exception_handler
from exception import ValidationException, RepositoryException


def create_app() -> FastAPI:
    app = FastAPI()
    from enowshop.infrastructure.container import Container
    container = Container()

    from enowshop.endpoints.orders import controller as orders_module
    orders_module.configure(app)

    from enowshop.endpoints.cars import controller as cars_module
    cars_module.configure(app)

    from enowshop.endpoints.quotes import controller as quotes_module
    quotes_module.configure(app)

    container.wire(modules=[orders_module, cars_module, quotes_module])

    app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'],
                       allow_headers=['*'])

    app.add_exception_handler(ValidationException, handler=generic_request_exception_handler)
    app.add_exception_handler(RepositoryException, handler=generic_request_exception_handler)

    return app


api_app = create_app()

if __name__ == '__main__':
    uvicorn.run(api_app, host='0.0.0.0', port=8082)
