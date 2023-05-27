from fastapi import APIRouter, Depends, Request, FastAPI, status

from config import Config
from enowshop.endpoints.orders.schema import CreateOrderSchema, OrderCreatedSchema, UpdateStatusSchema
from enowshop.endpoints.orders.service import OrdersService
from dependency_injector.wiring import inject, Provide
from enowshop.endpoints.dependecies import verify_jwt


from enowshop.infrastructure.container import Container

router = APIRouter()


@router.post('/orders', status_code=status.HTTP_201_CREATED, response_model=OrderCreatedSchema)
@inject
async def create_order(request: Request, order_data: CreateOrderSchema,
                       # user_data_auth=Depends(verify_jwt),
                       orders_service: OrdersService = Depends(Provide(Container.orders_service))):
    order = await orders_service.create_order(order_data=order_data.dict())
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
        'status': params.get('status', None),
        'limit': int(params.get('limit', 12)),
        'offset': int(params.get('offset', 0)),
    }
    orders = await orders_service.get_all_orders(params=params)
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


def configure(app: FastAPI):
    app.include_router(router)
