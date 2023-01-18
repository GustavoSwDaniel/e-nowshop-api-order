import uvicorn

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()
    from enowshop.infrastructure.container import Container
    container = Container()

    from enowshop.endpoints.orders import controller as orders_module
    orders_module.configure(app)

    container.wire(modules=[orders_module])

    return app


api_app = create_app()

if __name__ == '__main__':
    uvicorn.run(api_app, host='0.0.0.0', port=8082)
