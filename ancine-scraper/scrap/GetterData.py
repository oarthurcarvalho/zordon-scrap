import csv
import os
import re
import sys


class GetterData():

    def __init__(self, url: str, scraptype: str = 'nacional') -> None:
        self.url = url
        self.scraptype = scraptype
        self.header = ['num_semana', 'name_semana', 'rank', 'titulo',
                       'publico', 'sessoes', 'nacionalidade', 'regiao', 'uf',
                       'renda', 'preco_medio']

    def getweek(self) -> int:
        while True:
            try:
                semana_select = int(
                    input('Digite o número da semana que você deseja obter os dados ou digite 0 para sair: '))
                break
            except ValueError:
                print('Digite apenas o número da semana')

        if semana_select != 0:
            return semana_select

        sys.exit()

    def get_data(self, card):

        padroes = {
            'filme': r"^(.*?)\. Público",
            'rank_position': r"(\d+) of \d+",
            'publico': r"Público (\d+.\d+)",
            'sessoes': r"Sessões (\d+)",
            'renda': r"Renda R\$(.*?)\.",
            'preco_medio': r"Preço Médio do Ingresso R\$(.*?)\."
        }

        info = card.get_attribute('aria-label')

        resultados = []

        for padrao in padroes.values():

            correspondencias = re.findall(padrao, info)
            if correspondencias:
                resultados.append(correspondencias[0])

        return resultados

    def write_csv(self, path, data):

        if not os.path.exists(path):
            with open(path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(self.header)

        with open(path, 'a', newline='', encoding='utf-8') as file:

            writer = csv.writer(file)

            for line in data.values():
                linha = [str(value) for value in line]
                writer.writerow(linha)


if __name__ == '__main__':
    url = 'https://app.powerbi.com/view?r=eyJrIjoiM2ViZGRmMjctYjZlNC00NjI4LWFiZDEtMDAzZjk2OTU2OGYyIiwidCI6ImIwYThiNWFkLTU5MGQtNGZiYS1hZmY4LWUzMDc0YWI0MzVhNyJ9&pageName=ReportSectiona448b45fb6e3695eb8ba'

    ancine = AncineScraper(url, 'nacional')
    semana = ancine.getweek()
    print(semana)
