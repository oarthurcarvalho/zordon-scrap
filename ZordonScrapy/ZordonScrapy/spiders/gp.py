import csv
import os
from datetime import datetime

import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

DIA_COLETA = datetime.now().strftime('Dia %d/%m')
DATA_COLETA = datetime.now().strftime('%d/%m/%Y')

SPIDER_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SPIDER_DIR)
ROOT_DIR = os.path.dirname(PROJECT_DIR)
DATA_DIR = os.path.join(ROOT_DIR, 'data')


class GpSpider(scrapy.Spider):
    name = "gp"
    allowed_domains = ["www.globoplay.com"]
    start_urls = ["https://globoplay.globo.com/categorias/top-10/"]
    path_file = os.path.join(DATA_DIR, 'globoPlay.csv')

    def parse(self, response):

        self.verifica_arquivo()

        maior_data_arquivo = self.verificar_maior_data()
        if maior_data_arquivo == DATA_COLETA:
            return None

        service = Service(
            ChromeDriverManager(
                version="114.0.5735.90").install())
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(service=service, options=options)
        driver.get('https://globoplay.globo.com/categorias/top-10/')

        listas = driver.find_elements(By.CSS_SELECTOR, '.offer-slider')

        for lista in listas:
            titulos = []
            categoria = lista.find_elements(
                By.CSS_SELECTOR,
                'h2.offer-headline')[0].get_attribute('textContent')

            pontos = 10
            stop = False
            clicked = 0
            while clicked <= 1 and not stop:
                itens = lista.find_elements(
                    By.CSS_SELECTOR,
                    '.gplay-slider__slide')

                for titulo in itens:
                    item = {}
                    item['Data'] = DATA_COLETA
                    item['Título'] = titulo.find_elements(
                        By.CSS_SELECTOR,
                        '.poster__image')[0].get_attribute('alt')
                    item['Pontos'] = pontos
                    item['Categoria'] = categoria

                    if item['Título'] not in titulos:
                        self.escrever_arquivo(item)

                        titulos.append(item['Título'])
                        pontos -= 1

                next_button = lista.find_elements(
                    By.CSS_SELECTOR,
                    '.gplay-slider__arrow--next')

                if len(next_button) > 0:
                    try:
                        cookies_button = driver.find_elements(
                            By.CSS_SELECTOR,
                            '.cookie-banner-lgpd_accept-button')

                        if len(cookies_button) > 0:
                            cookies_button[0].click()

                        next_button[0].click()
                    except Exception:
                        pass

                    clicked += 1
                else:
                    stop = True

                driver.find_element('tag name', 'body').send_keys(Keys.END)

    def verifica_arquivo(self):
        if not os.path.isfile(self.path_file):
            with open(self.path_file, mode='w', newline='',
                      encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        'Data', 'Título', 'Pontos',
                        'Categoria'
                    ]
                )

    def escrever_arquivo(self, item):
        with open(self.path_file, 'a', newline='',
                  encoding='utf-8') as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    'Data', 'Título', 'Pontos',
                    'Categoria'
                ]
            )
            writer.writerow(item)

    def verificar_maior_data(self):

        maior_data = None
        with open(self.path_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            headers = next(reader, None)

            if headers is not None:
                for row in reader:
                    data_str = row[0]
                    data = datetime.strptime(data_str, '%d/%m/%Y')

                    if maior_data is None or data > maior_data:
                        maior_data = data

        return maior_data.strftime('%d/%m/%Y') \
            if maior_data is not None else None
