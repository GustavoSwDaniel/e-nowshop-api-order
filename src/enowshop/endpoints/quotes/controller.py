from enowshop.endpoints.quotes.schema import ProductsListSchema, QuotesListSchema
from enowshop.infrastructure.container import Container
from fastapi import APIRouter, Depends, Request, FastAPI, status
from dependency_injector.wiring import inject, Provide
from enowshop.endpoints.quotes.service import QuotesService

router = APIRouter()

@router.post('/calc/frete/{uuid_address}', status_code=status.HTTP_200_OK, response_model=QuotesListSchema)
@inject
async def get_frete(request: Request, uuid_address: str, 
                    products_uuid: ProductsListSchema,
                    quates_service: QuotesService = Depends(Provide[Container.quotes_service])):
    print(products_uuid)
    quotes = await quates_service.calc_quotes(products_uuid.dict(), uuid_address)
    return quotes



def configure(app: FastAPI):
    app.include_router(router)