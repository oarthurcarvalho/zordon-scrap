import csv
import os
from datetime import datetime

import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

DIA_COLETA = datetime.now().strftime('Dia %d/%m')
DATA_COLETA = datetime.now().strftime('%d/%m/%Y')

SPIDER_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SPIDER_DIR)
ROOT_DIR = os.path.dirname(PROJECT_DIR)
DATA_DIR = os.path.join(ROOT_DIR, 'data')


class CtSpider(scrapy.Spider):
    name = "ct"
    allowed_domains = ["www.chartable.com"]
    start_urls = ["https://google.com/"]
    path_file = os.path.join(DATA_DIR, 'chartable.csv')

    def parse(self, response):

        self.verifica_arquivo()

        maior_data_arquivo = self.verificar_maior_data()
        if maior_data_arquivo == DATA_COLETA:
            return None

        service = Service()
        chrome_options = Options()
        driver = webdriver.Chrome(options=chrome_options, service=service)
        driver.get('https://chartable.com/charts/spotify/brazil-top-podcasts/')

        top_podcasts = driver.find_elements(By.CSS_SELECTOR, 'tr')
        pontos = len(top_podcasts)
        for podcast in top_podcasts:
            item = {}
            item['Data'] = DATA_COLETA
            item['Título'] = podcast.find_elements(
                By.CSS_SELECTOR,
                '.title')[0].get_attribute('textContent')
            item['Pontos'] = pontos

            pontos -= 1

            self.escrever_arquivo(item)

    def verifica_arquivo(self):
        if not os.path.isfile(self.path_file):
            with open(self.path_file, mode='w', newline='',
                      encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        'Data', 'Título', 'Pontos'
                    ]
                )

    def escrever_arquivo(self, item):
        with open(self.path_file, 'a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    'Data', 'Título', 'Pontos'
                ]
            )
            writer.writerow(item)

    def verificar_maior_data(self):
        maior_data = None

        with open(self.path_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)

            for row in reader:
                data_str = row[0]
                data = datetime.strptime(data_str, '%d/%m/%Y')

                if maior_data is None or data > maior_data:
                    maior_data = data

        return maior_data.strftime('%d/%m/%Y') \
            if maior_data is not None else None
