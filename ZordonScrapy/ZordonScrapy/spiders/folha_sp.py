import csv
import os
from datetime import datetime
from time import sleep

import requests
import scrapy
from bs4 import BeautifulSoup
from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager


class FolhaSpSpider(scrapy.Spider):
    name = "folha_sp"
    allowed_domains = ["www1.folha.uol.com.br"]
    start_urls = [
        "https://www1.folha.uol.com.br/maispopulares/#educacao/mais-lidas"]

    SPIDER_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_DIR = os.path.dirname(SPIDER_DIR)
    ROOT_DIR = os.path.dirname(PROJECT_DIR)
    DATA_DIR = os.path.join(ROOT_DIR, 'data')
    DATA_COLETA = datetime.now().strftime('%d-%m-%Y')

    path_file = os.path.join(DATA_DIR, 'folha_sp.csv')

    categorias = ['agora', 'ciencia', 'cotidiano', 'colunas-e-blogs',
                  'educacao', 'equilibrio', 'esporte', 'ilustrada',
                  'ilustrissima', 'mercado', 'mundo', 'opiniao',
                  'poder', 'saude', 'tec', 'turismo'
                  ]

    def parse(self, response):

        my_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'

        options = webdriver.ChromeOptions()
        options.add_argument(f"user-agent={my_agent}")

        service = Service(ChromeDriverManager().install())

        driver = webdriver.Chrome(options=options, service=service)

        for categoria in self.categorias:

            url = f'https://www1.folha.uol.com.br/maispopulares/#{categoria}/mais-lidas'

            page_content = self.get_url(driver, url)

            soup = BeautifulSoup(page_content, 'html.parser')

            noticias = soup.find_all(
                'li', attrs={'class': 'c-most-popular__item'})

            for index, noticia in enumerate(noticias):

                item = {}

                tag = noticia.find(
                    'a',
                    attrs={'class': 'c-kicker c-most-popular__kicker'})

                if tag is None:
                    tag = noticia.find(
                        'span',
                        attrs={'class': 'c-kicker c-most-popular__kicker'})

                div = noticia.find('div', 'c-most-popular__content')

                item['data'] = self.DATA_COLETA
                item['index'] = index + 1
                item['categoria'] = categoria
                item['tag'] = tag.text.strip()
                item['manchete'] = div.find('a').text

                self.write_row(item)

    def get_url(self, driver, url):

        driver.get(url)
        sleep(3)
        driver.refresh()
        sleep(10)

        page_content = driver.page_source

        return page_content

    def write_row(self, item):

        file_exists = os.path.isfile(self.path_file)

        with open(self.path_file, 'a',
                  newline='', encoding='utf-8') as file:

            keys = ['data', 'index', 'categoria', 'tag', 'manchete']
            writer = csv.DictWriter(file, fieldnames=keys)
            if not file_exists:
                writer.writeheader()

            writer = csv.writer(file)
            writer.writerow([
                item.get('data', ''),
                item.get('index', ''),
                item.get('categoria', ''),
                item.get('tag', ''),
                item.get('manchete', ''),
            ])
