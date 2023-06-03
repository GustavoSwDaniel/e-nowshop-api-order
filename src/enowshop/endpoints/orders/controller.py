from fastapi import APIRouter, Depends, Request, FastAPI, status

from config import Config
from enowshop.endpoints.orders.schema import CreateOrderSchema, OrderCreatedSchema, UpdateStatusSchema, OrdersPaginateSchema
from enowshop.endpoints.orders.service import OrdersService
from dependency_injector.wiring import inject, Provide
from enowshop.endpoints.dependecies import verify_jwt
from distutils.util import strtobool


from enowshop.infrastructure.container import Container

router = APIRouter()


@router.post('/orders', status_code=status.HTTP_201_CREATED, response_model=OrderCreatedSchema)
@inject
async def create_order(request: Request, order_data: CreateOrderSchema,
                       user_data_auth=Depends(verify_jwt),
                       orders_service: OrdersService = Depends(Provide(Container.orders_service))):
    order = await orders_service.create_order(order_data=order_data.dict(), 
                                              user_uuid_keycloak=user_data_auth.get('sub'))
    return order

@router.post('/orders/calc')
@inject
async def calc_order(request: Request, order_data: CreateOrderSchema,
                       orders_service: OrdersService = Depends(Provide(Container.orders_service))):
    order = await orders_service.calc_order(order_data=order_data.dict())
    return order

@router.get('/orders/{order_uuid}')
async def get_order_by_uuid(request: Request, order_uuid: str):
    ...


@router.get('/orders')
@inject
async def get_orders(request: Request, 
                     orders_service: OrdersService = Depends(Provide(Container.orders_service))):
    params = request.query_params
    params = {
        'expirate': bool(strtobool(params.get('expirate', 'False'))),
        'status': params.get('status', None),
        'limit': int(params.get('limit', 12)),
        'offset': int(params.get('offset', 0)),
    }
    orders = await orders_service.get_all_orders(params=params)
    return orders

@router.get('/order/user', response_model=OrdersPaginateSchema)
@inject
async def get_orders_by_user(request: Request,
                             orders_service: OrdersService = Depends(Provide(Container.orders_service))):
    params = request.query_params
    params = {
        'limit': int(params.get('limit', 12)),
        'offset': int(params.get('offset', 0)),
    }
    orders = await orders_service.get_orders_by_user(user_uuid='628c4b78-37ad-4047-8411-e12fd1ad6b69', params=params)
    return orders
                                  


@router.patch('/orders/{order_uuid}/status', status_code=status.HTTP_204_NO_CONTENT)
@inject
async def update_order_status(request: Request, order_uuid: str, update_status: UpdateStatusSchema,
                              orders_service: OrdersService = Depends(Provide(Container.orders_service))):
    await orders_service.update_order_status(order_uuid=order_uuid, status=update_status.status)
    return 


@router.post('/orders/webhook', status_code=status.HTTP_200_OK)
@inject
async def order_webhook(request: Request, orders_service: OrdersService = Depends(Provide(Container.orders_service))):
    data = await request.json()
    await orders_service.check_and_update_orders(data=data)
    return

@router.patch('/orders/{order_id}/products/decrement', status_code=status.HTTP_204_NO_CONTENT)
@inject
async def decrement_product_quantity(request: Request, order_id: str,
                                        orders_service: OrdersService = Depends(Provide(Container.orders_service))):
    await orders_service.decrement_products_quantity(order_id=order_id)
    return 

@router.get('/orders/{order_uuid}/products', status_code=status.HTTP_200_OK)
@inject
async def get_products_by_order_uuid(request: Request, order_uuid: str,
                                    orders_service: OrdersService = Depends(Provide(Container.orders_service))):
    products = await orders_service.get_products_by_order_id(order_uuid=order_uuid)
    return products


def configure(app: FastAPI):
    app.include_router(router)
