from enowshop.infrastructure.container import Container
from fastapi import APIRouter, Depends, Request, FastAPI, status
from dependency_injector.wiring import inject, Provide
from enowshop.endpoints.dependecies import verify_jwt


from enowshop.endpoints.cars.schema import CarItems, CarSchema, ChangeQuantity
from enowshop.endpoints.cars.service import CarsService

router = APIRouter()


@router.post("/car/{uuid}", status_code=status.HTTP_201_CREATED)
@inject
async def create_car(request: Request, uuid: str,
                     cars_service: CarsService = Depends(Provide(Container.cars_service))):
    await cars_service.create_cars(uuid=uuid)
    return 


@router.get("/car", status_code=status.HTTP_200_OK, response_model=CarSchema)
@inject
async def get_car(request: Request,
                  user_data_auth=Depends(verify_jwt),
                  cars_service: CarsService = Depends(Provide(Container.cars_service))):
    params = request.query_params
    send_type = params.get('type_send', None)
    return await cars_service.get_car_with_user_uuid(user_uuid=user_data_auth.get('sub'), send_type=send_type)


@router.put('/car')
@inject
async def add_item_car(request: Request, new_item: CarItems,
                       user_data_auth=Depends(verify_jwt),
                       cars_service: CarsService = Depends(Provide(Container.cars_service))):
    await cars_service.add_item_in_car(data=new_item.dict(), user_uuid=user_data_auth.get('sub'))
    return {'deu': 'boa'}


@router.delete('/car/item/{item_uuid}', status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_car(request: Request, item_uuid: str,
                     user_data_auth=Depends(verify_jwt),
                     cars_service: CarsService = Depends(Provide(Container.cars_service))):
    await cars_service.remove_item_in_car(user_uuid=user_data_auth.get('sub'), item_uuid=item_uuid)
    return {}


@router.put('/car/item/{item_uuid}', status_code=status.HTTP_204_NO_CONTENT)
@inject
async def update_quantity(request: Request, item_uuid: str,
                          new_quantity: ChangeQuantity,
                          user_data_auth=Depends(verify_jwt),
                          cars_service: CarsService = Depends(Provide(Container.cars_service))):
    await cars_service.change_quantity_item_in_car(user_uuid=user_data_auth.get('sub'), item_uuid=item_uuid,
                                                   new_quantity=new_quantity.dict()['quantity'])
    return {}


@router.get("/car/lenght", status_code=status.HTTP_200_OK)
@inject
async def get_car_lenght(request: Request,
                         user_data_auth=Depends(verify_jwt),
                         cars_service: CarsService = Depends(Provide(Container.cars_service))):
    car_lenght =  await cars_service.get_car_lenght(user_uuid=user_data_auth.get('sub'))
    return {'lenght': car_lenght}

def configure(app: FastAPI):
    app.include_router(router)
