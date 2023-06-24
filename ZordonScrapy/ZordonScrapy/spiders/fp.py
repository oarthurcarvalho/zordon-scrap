import csv
import json
import os
from datetime import datetime

import scrapy

DIA_COLETA = datetime.now().strftime('Dia %d/%m')
DATA_COLETA = datetime.now().strftime('%d/%m/%Y')

name_month = {
    '01': 'Janeiro', '02': 'Fevereiro', '03': 'Março',
    '04': 'Abril', '05': 'Maio', '06': 'Junho',
    '07': 'Julho', '08': 'Agosto', '09': 'Setembro',
    '10': 'Outubro', '11': 'Novembro', '12': 'Dezembro',
}

SPIDER_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SPIDER_DIR)
ROOT_DIR = os.path.dirname(PROJECT_DIR)
DATA_DIR = os.path.join(ROOT_DIR, 'data')


class FpSpider(scrapy.Spider):
    name = "fp"
    allowed_domains = ["flixpatrol.com"]
    start_urls = ["https://flixpatrol.com/top10/streaming/brazil/"]
    path_file = os.path.join(DATA_DIR, 'flixPatrol.csv')

    def parse(self, response):

        self.verifica_arquivo()

        maior_data_arquivo = self.verificar_maior_data()
        if maior_data_arquivo == DATA_COLETA:
            return None

        cards = response.xpath('//div[@class="content mb-14"]')

        for card in cards:

            plataforma = card.xpath('.//h2[@class="mb-3"]//text()').get()
            i_str_plataforma = plataforma.find('TOP') - 1
            categorias = card.xpath('.//div[@class="w-3/4"]')

            for categoria in categorias:

                tipo = categoria.xpath(
                    './/h3[@class="table-th text-gray-400 text-center"]\
                        //text()').get()

                lista = categoria.xpath('.//tr[@class="table-group"]')

                pontos = len(lista)

                for titulo in lista:

                    item = {}
                    item['Dia'] = DATA_COLETA
                    item['Mês'] = name_month[DATA_COLETA.split('/')[1]]
                    item['Título'] = titulo.xpath(
                        './/a[@class="hover:underline"]//text()').get()
                    item['Pontos'] = pontos
                    item['Categoria'] = tipo[7:]
                    item['Canal'] = plataforma[:i_str_plataforma]

                    link = titulo.xpath(
                        './/a[@class="hover:underline"]'
                    ).attrib["href"]

                    link = 'https://flixpatrol.com' + link

                    yield scrapy.Request(
                        url=link,
                        callback=self.parse_titulo,
                        meta=dict(item=item)
                    )

                    pontos -= 1

    def parse_titulo(self, response):
        item = response.meta['item']

        info = response.xpath(
            './/script[@type="application/ld+json"]//text()').get()

        dicionario = json.loads(info)
        list_info = dicionario["sameAs"] if "sameAs" in dicionario else '-'
        item['IMDB_cod'] = self.get_cod(list_info, 'imdb.com')
        item['TMDB_cod'] = self.get_cod(list_info, 'themoviedb.org')

        with open(self.path_file, 'a', newline='',
                  encoding='utf-8') as csvfile:
            writer = csv.DictWriter(
                csvfile,
                fieldnames=[
                    'Dia', 'Mês', 'Título',
                    'Pontos', 'Categoria', 'Canal',
                    'IMDB_cod', 'TMDB_cod'
                ]
            )
            writer.writerow(item)

    def get_cod(self, lista, site):

        num = -2 if site == 'imdb.com' else -1

        imdb_url = next((url for url in lista if site in url), '-')
        return imdb_url.split('/')[num] if imdb_url != '-' else imdb_url

    def verifica_arquivo(self):
        if not os.path.isfile(self.path_file):
            with open(self.path_file, mode='w', newline='',
                      encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        'Dia', 'Mês', 'Título',
                        'Pontos', 'Categoria', 'Canal',
                        'IMDB_cod', 'TMDB_cod'
                    ]
                )

    def verificar_maior_data(self):
        maior_data = None

        with open(self.path_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)

            # Verificar se há mais de uma linha no leitor
            if sum(1 for _ in reader) <= 1:
                return None

            # Voltar para o início do arquivo
            file.seek(0)

            # Pular a primeira linha, se houver
            next(reader, None)

            for row in reader:
                data_str = row[0]
                data = datetime.strptime(data_str, '%d/%m/%Y')

                if maior_data is None or data > maior_data:
                    maior_data = data

        return maior_data.strftime('%d/%m/%Y') \
            if maior_data is not None else None
