from fastapi import APIRouter, Depends, Request, FastAPI, status

from config import Config
from enowshop.endpoints.orders.schema import CreateOrderSchema, OrderCreatedSchema
from enowshop.endpoints.orders.service import OrdersService
from dependency_injector.wiring import inject, Provide

from enowshop.infrastructure.container import Container

router = APIRouter()


@router.post('/orders', status_code=status.HTTP_201_CREATED, response_model=OrderCreatedSchema)
@inject
async def create_order(request: Request, order_data: CreateOrderSchema, orders_service: OrdersService = Depends(Provide(Container.orders_service))):
    print(order_data)
    order = await orders_service.create_order(order_data=order_data.dict())
    return order


@router.get('/orders/{order_uuid}')
async def get_order_by_uuid(request: Request, order_uuid: str):
    ...


@router.get('/orders')
async def get_orders(request: Request):
    ...


@router.patch('/orders/{order_uuid}/status')
async def update_order_status(request: Request, order_uuid: str):
    ...


def configure(app: FastAPI):
    app.include_router(router)
