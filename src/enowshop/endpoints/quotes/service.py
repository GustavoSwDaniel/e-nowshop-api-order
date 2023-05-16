from typing import List, Union
from enowshop.endpoints.quotes.repository import UsersAddressRepository
from enowshop.endpoints.orders.repository import ProductsRepository
from enowshop.domain.correios.client import CorreiosClient

class QuotesService:
    def __init__(self, correios_client: CorreiosClient, products_repository: ProductsRepository,
                 user_address_repository: UsersAddressRepository, origin_cep: str):
        self.correios_client = correios_client
        self.products_repository = products_repository
        self.user_address_repository = user_address_repository
        self.origin_cep = origin_cep
    
    async def __get_user_address(self, uuid_address):
        return await self.user_address_repository.filter_by({'id': int(uuid_address)})

    
    def get_tipo_embalagem(self, peso, comprimento, altura, largura):
        if peso <= 0.5 and comprimento <= 35 and altura <= 25 and largura <= 2:
            return 'envelope'
        else:
            return 'caixa'

    def calc_sedex(self, origin_cep, destination_cep, peso, comprimento, altura, largura, diametro):
        return self.correios_client.calc_quotes_sedex(origin_cep, destination_cep, peso, comprimento, altura, largura, diametro)
    
    def calc_pac(self, origin_cep, destination_cep, peso, comprimento, altura, largura, diametro):
        return self.correios_client.calc_quotes_pac(origin_cep, destination_cep, peso, comprimento, altura, largura, diametro)
    
    def calc_transportadora(self, peso, address):
        return {
            "name": "Transportadora",
            "valor": str(2.00 * peso).replace('.', ','),
            "prazo": 10,
            "cep": address.cep
        }


    def type_quote(self, type_quote):
        if type_quote == 'pac':
            return self.calc_pac
        elif type_quote == 'sedex':
            return self.calc_sedex
        return self.calc_transportadora

    async def calc_quotes(self, products, uuid_address, type_quote: Union[str, None] = None) -> List:
        address = await self.__get_user_address(uuid_address)
        peso = 0
        comprimento = 0
        altura = 0
        largura = 0
        diametro = 0
        
        for product_item in products.get('products'):
            product = await self.products_repository.get_products_by_uuid(uuid=product_item.get('uuid'))
            physical_characteristics = product.infos['dimensions']
            for _ in range(product_item.get('quantity')):
                peso += float(physical_characteristics['weight']) 
                comprimento += float(physical_characteristics['length']) if float(physical_characteristics['length']) >= 15 else 15
                altura += float(physical_characteristics['height']) if float(physical_characteristics['height']) > 1 else 1
                largura += float(physical_characteristics['width']) if float(physical_characteristics['width']) >= 10 else 10
        
        quotes = {'quotes': []}
        if not type_quote:
            sedex = self.calc_sedex(self.origin_cep, address.cep, peso, comprimento, 
                    altura, largura, diametro)
            pac = self.calc_pac(self.origin_cep, address.cep, peso, comprimento, 
                altura, largura, diametro)
            

            if sedex.get('valor') != '0,00' and pac.get('valor') != '0,00':
                quotes.get('quotes').append(sedex)
                quotes.get('quotes').append(pac)

            quotes.get('quotes').append(self.calc_transportadora(peso, address))
            return quotes
        
        quotes.get('quotes').append(self.type_quote(type_quote)(self.origin_cep, address.cep, peso, comprimento, 
                    altura, largura, diametro))
        return quotes
        
    
    async def calc_quote(self, products, uuid_address, type_quote):
        quote = await self.calc_quotes(products, uuid_address, type_quote)
        return quote
        
   
