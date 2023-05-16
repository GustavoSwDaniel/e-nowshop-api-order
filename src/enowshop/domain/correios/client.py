class CorreiosClient:
    def __init__(self, client_soap):
        self.__client = client_soap
    
    def __calcFrete(self, cep_origem, cep_destino, peso, comprimento, altura, largura, diametro, servico):
        return self.__client.service.CalcPrecoPrazo(
            nCdEmpresa='',
            sDsSenha='',
            nCdServico=servico,
            sCepOrigem=cep_origem,
            sCepDestino=cep_destino,
            nVlPeso=peso,
            nCdFormato=1,
            nVlComprimento=comprimento,
            nVlAltura=altura,
            nVlLargura=largura,
            nVlDiametro=diametro,
            sCdMaoPropria='N',
            nVlValorDeclarado=0,
            sCdAvisoRecebimento='N'
        )

    def calc_quotes_pac(self, cep_origem, cep_destino, peso, comprimento, altura, largura, diametro):
        print('pac')
        print(cep_origem, cep_destino, peso, comprimento, altura, largura, diametro)
        response = self.__calcFrete(cep_origem, cep_destino, peso, comprimento, altura, largura, diametro, '41106')
        return  {
                'name': 'PAC',
                'valor': str(response.cServico[0].Valor).replace('.', ','),
                'prazo': response.cServico[0].PrazoEntrega,
                'cep': cep_destino
            }
    
    def calc_quotes_sedex(self, cep_origem, cep_destino, peso, comprimento, altura, largura, diametro):
        print('sedex')
        print(cep_origem, cep_destino, peso, comprimento, altura, largura, diametro)
        response =  self.__calcFrete(cep_origem, cep_destino, peso, comprimento, altura, largura, diametro, '40010')
        return {
                'name': 'Sedex',
                'valor': str(response.cServico[0].Valor).replace('.', ','),
                'prazo': response.cServico[0].PrazoEntrega,
                'cep': cep_destino
            }

    