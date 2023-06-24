from selenium import webdriver

from scraper_ancine_regional import scraper_regiao

centro_oeste = {
    "CENTRO-OESTE":
        ["GOIÁS", "DISTRITO FEDERAL",
         "MATO GROSSO", "MATO GROSSO DO SUL"]
}

nordeste = {
    "NORDESTE":
        ["ALAGOAS", "BAHIA", "CEARÁ", "MARANHÃO",
         "PARAÍBA", "PERNAMBUCO", "PIAUÍ",
         "RIO GRANDE DO NORTE", "SERGIPE"]
}
norte = {
    "NORTE":
        ["ACRE", "AMAPÁ", "AMAZONAS", "PARÁ",
         "RONDÔNIA", "RORAIMA", "TOCANTINS"]
}
sudeste = {
    "SUDESTE":
        ["ESPÍRITO SANTO", "MINAS GERAIS",
         "RIO DE JANEIRO", "SÃO PAULO"]
}
sul = {
    "SUL":
        ["PARANÁ", "RIO GRANDE DO SUL", "SANTA CATARINA"]
}


if __name__ == '__main__':
    regioes = [
        nordeste, centro_oeste,
        norte, sudeste, sul
    ]

    while True:
        try:
            semana_select = int(input(
                'Digite o número da semana que você deseja obter os dados: '))
            break
        except Exception:
            print('')

    for regiao in regioes:
        scraper_regiao(regiao, semana_select)
