import csv
import json
import os
import re
import sys
from datetime import datetime, timedelta
from html import unescape

import scrapy

SPIDER_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SPIDER_DIR)
ROOT_DIR = os.path.dirname(PROJECT_DIR)
DATA_DIR = os.path.join(ROOT_DIR, 'data')


class ImdbSpider(scrapy.Spider):
    name = "imdb"
    start_urls = ["https://imdb.com/title/"]

    def __init__(self):
        self.re_ano = r"\((.*?)\)"
        self.path_file = os.path.join(DATA_DIR, 'imdb.csv')
        self.keys = [
            'cod_imdb', 'title', 'original_title', 'type',
            'parental_rating', 'duration', 'imdb_rating',
            'imdb_num_votes', 'genre_1', 'genre_2', 'genre_3',
            'budget', 'budget', 'cumulativeworld',
            'cumulativeworldwidegross', 'grossdomestic',
            'openingweekenddomestic', 'writer_1', 'writer_2',
            'writer_3', 'director_1', 'director_2', 'director_3',
            'start_year', 'end_year', 'storyline', 'country_1',
            'country_2', 'language_1', 'language_2', 'language_3',
            'actor_1', 'actor_2', 'actor_3', 'actor_4', 'actor_5',
            'actor_6', 'actor_7', 'actor_8', 'actor_9', 'actor_10'
        ]

    def start_requests(self):
        headers = {
            'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
                (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
            'Accept-Language': 'pt-BR'}

        movie_codes = self.get_imdb_codes()

        for code in movie_codes:
            search_url = self.start_urls[0] + code

            yield scrapy.Request(
                url=search_url,
                callback=self.parse,
                headers=headers,
                meta={"code": code})

    def parse(self, response):
        item = {}

        dados = response.xpath(
            './/script[@type="application/ld+json"]/text()').get()
        dados = json.loads(dados)

        item['cod_imdb'] = dados['url'].split('/')[-2]

        if 'alternateName' in dados.keys():
            item['title'] = unescape(dados['alternateName'])
            item['original_title'] = unescape(dados['name'])
        else:
            item['title'] = unescape(dados['name'])
            item['original_title'] = '-'

        item['type'] = dados['@type']

        item['parental_rating'] = dados['contentRating'] \
            if 'contentRating' in dados.keys() else '-'
        item['duration'] = response.xpath(
            '//*[@id="__next"]/main/div/section[1]/section/div[3]/\
                section/section/div[2]/div[1]/ul/li[3]/text()').get()
        if 'aggregateRating' in dados.keys():
            item['imdb_rating'] = dados['aggregateRating']['ratingValue']
            item['imdb_num_votes'] = dados['aggregateRating']['ratingCount']
        else:
            item['imdb_rating'] = '-'
            item['imdb_num_votes'] = '-'

        for i in range(len(dados['genre'])):
            item[f'genre_{i+1}'] = dados['genre'][i]

        if 'creator' in dados.keys():
            creators = dados['creator']
            i = 1
            for creator in creators:
                if creator['@type'] == 'Person':
                    item[f'writer_{i}'] = creator['name']
                    i += 1
                    if i > 3:
                        break

        if 'creator' in dados.keys() or 'director' in dados.keys():
            directors = dados['director'] if 'director' in dados.keys(
            ) else dados['creator']
            i = 1
            for director in directors:
                if director['@type'] == 'Person':
                    item[f'director_{i}'] = director['name']
                    i += 1
                    if i > 3:
                        break

        texto_filme = response.xpath('.//title/text()').extract_first()
        ano_lancamento = re.findall(self.re_ano, texto_filme)[0].split()[-1]

        if '–' in ano_lancamento:
            item['start_year'], item['end_year'] = ano_lancamento.split('–')
        else:
            item['start_year'], item['end_year'] = ano_lancamento, '-'

        item['storyline'] = response.xpath(
            './/span[@data-testid="plot-xl"]/text()').get()

        contries = response.xpath(
            './/li[@data-testid="title-details-origin"]/div/ul/li')

        i = 1
        for country in contries:
            item[f'country_{i}'] = country.xpath('.//a/text()').get()
            i += 1
            if i > 2:
                break

        languages = response.xpath(
            './/li[@data-testid="title-details-languages"]/div/ul/li')
        i = 1
        for language in languages:
            item[f'language_{i}'] = language.xpath('.//a/text()').get()
            i += 1
            if i > 3:
                break

        if response.xpath('.//div[@data-testid="title-boxoffice-section"]'):

            item['budget'] = response.xpath(
                './/li[@data-testid="title-boxoffice-budget"]/div/ul/li/\
                    span/text()').get()
            item['grossdomestic'] = response.xpath(
                './/li[@data-testid="title-boxoffice-grossdomestic"]/div/\
                    ul/li/span/text()').get()
            item['openingweekenddomestic'] = response.xpath(
                './/li[@data-testid="title-boxoffice-openingweekenddomestic"]\
                    /div/ul/li/span/text()').get()
            item['cumulativeworldwidegross'] = response.xpath(
                './/li[@data-testid="title-boxoffice-cumulativeworldwidegross"]\
                    /div/ul/li/span/text()').get()

        actors = response.xpath(
            './/a[@data-testid="title-cast-item__actor"]/text()').getall()

        i = 1
        for actor in actors:
            item[f'actor_{i}'] = actor
            i += 1
            if i > 10:
                break

        self.generate_csv_file(item)

    def generate_csv_file(self, item):

        file_exists = os.path.isfile(self.path_file)

        with open(self.path_file, 'a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=self.keys)

            if not file_exists:
                writer.writeheader()

            writer.writerow(item)

    def converter_tempo(self, string):
        horas, minutos = map(int, string.split('h'))

        tempo = timedelta(hours=horas, minutes=minutos)
        tempo_formatado = (datetime.min + tempo).time().strftime('%H:%M:%S')

        return tempo_formatado

    def get_imdb_codes(self):
        imdb_codes = []
        csv_path = 'data/imdb_input.csv'
        try:
            with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
                leitor_csv = csv.reader(csvfile)
                for linha in leitor_csv:
                    if linha:
                        imdb_codes.append(linha[0])

            return imdb_codes
        except FileNotFoundError as e:
            print(e)
            sys.exit()
