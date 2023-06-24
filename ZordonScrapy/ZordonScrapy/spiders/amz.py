import csv
import os
from datetime import datetime
from time import sleep

import scrapy
from bs4 import BeautifulSoup
from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

SPIDER_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SPIDER_DIR)
ROOT_DIR = os.path.dirname(PROJECT_DIR)
DATA_DIR = os.path.join(ROOT_DIR, 'data')


class AmzEbSpider(scrapy.Spider):
    name = "amz"
    SPIDER_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_DIR = os.path.dirname(SPIDER_DIR)
    ROOT_DIR = os.path.dirname(PROJECT_DIR)
    DATA_DIR = os.path.join(ROOT_DIR, 'data')
    DATA_COLETA = datetime.now().strftime('%d-%m-%Y')
    start_urls = [
        "https://www.amazon.com.br/gp/bestsellers/digital-text/5475882011/"]

    path_file = os.path.join(DATA_DIR, 'amazon_kindle.csv')

    def __init__(self):
        self.data = datetime.now().strftime('%d-%m-%Y')
        self.paginas = [(
            'https://www.amazon.com.br/gp/bestsellers/digital-text/5475882011/',
            'Kindle'),
            ('https://www.amazon.com.br/gp/bestsellers/books/', 'Books')]

        for pagina in self.paginas:
            url, tipo = pagina
            self.path_file = os.path.join(DATA_DIR, f'amazon_{tipo}.csv')
            self.verifica_arquivo()
            maior_data_arquivo = self.verificar_maior_data()
            if maior_data_arquivo == self.DATA_COLETA:
                return None

            self.driver = self.init_page(url)

            self.scrap_page(tipo)

    def scroll_to_bottom(self, driver):

        prev_height = driver.execute_script(
            "return document.body.scrollHeight"
        )

        while True:
            driver.find_element('tag name', 'body').send_keys(Keys.END)

            sleep(1)

            curr_height = driver.execute_script(
                "return document.body.scrollHeight")
            if curr_height == prev_height:
                break
            prev_height = curr_height

    def write_row(self, item):

        with open(self.path_file, 'a',
                  newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                item.get('Data', ''),
                item.get('Tipo', ''),
                item.get('Genero', ''),
                item.get('Posicao', ''),
                item.get('Livro', ''),
                item.get('Autor', ''),
                item.get('Pontos', ''),
                item.get('num_avaliacoes', ''),
                item.get('avaliacao', '')
            ])

    def init_page(self, url):
        service = Service(ChromeDriverManager().install())
        chrome_options = Options()
        chrome_options = webdriver.ChromeOptions()
        my_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        chrome_options.add_argument(f"user-agent={my_agent}")
        driver = webdriver.Chrome(options=chrome_options, service=service)
        driver.maximize_window()
        driver.get(url=url)
        sleep(1)
        driver.refresh()
        sleep(1)

        return driver

    def scrap_page(self, tipo):

        categorias = self.get_genre_links()

        for categoria in categorias:
            genero, url = categoria

            self.driver.get(url)
            self.scroll_to_bottom(self.driver)

            bs = BeautifulSoup(self.driver.page_source, 'html.parser')
            lxml_soup = etree.HTML(str(bs))

            cards = lxml_soup.xpath('.//div[@id="gridItemRoot"]')
            pontos = len(cards)

            for card in cards:

                item = {}
                item["Data"] = self.DATA_COLETA
                item['Tipo'] = tipo
                item['Genero'] = genero
                item["Posicao"] = card.xpath(
                    './/span[@class="zg-bdg-text"]//text()')[0]
                item["Livro"] = card.xpath(
                    './/a[@class="a-link-normal"]/span/div//text()')[0]

                try:
                    item["Autor"] = card.xpath(
                        './/div[@class="a-row a-size-small"]/a/div//text()')[0]
                except IndexError:
                    item["Autor"] = card.xpath(
                        './/div[@class="a-row a-size-small"]\
                            /span/div//text()')[0]

                item["Pontos"] = pontos

                num_avaliacoes = card.xpath(
                    './/div[@class="a-row"]/div/a/span//text()')
                item["num_avaliacoes"] = num_avaliacoes[0].replace('.', '') \
                    if num_avaliacoes else None

                avaliacao = card.xpath(
                    './/div[@class="a-row"]/div/a/i/span//text()')
                item["avaliacao"] = float(
                    avaliacao[0].split()[0].replace(',', '.')) if avaliacao else None

                pontos -= 1
                self.write_row(item)

        self.driver.quit()

    def verificar_maior_data(self):
        maior_data = None

        with open(self.path_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)

            # Verificar se há mais de uma linha no leitor
            if sum(1 for i in reader) <= 1:
                return None

            # Voltar para o início do arquivo
            file.seek(0)

            # Pular a primeira linha, se houver
            next(reader, None)

            for row in reader:
                data_str = row[0]
                data = datetime.strptime(data_str, '%d-%m-%Y')

                if maior_data is None or data > maior_data:
                    maior_data = data

        return maior_data.strftime('%d-%m-%Y') \
            if maior_data is not None else None

    def verifica_arquivo(self):
        if not os.path.isfile(self.path_file):
            with open(self.path_file, mode='w', newline='',
                      encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        'Data', 'Tipo', 'Genero', 'Posicao', 'Livro',
                        'Autor', 'Pontos', 'num_avaliacoes',
                        'avaliacao'
                    ]
                )

    def get_genre_links(self):

        lista = []

        xpath_categorias = self.driver.find_elements(
            'xpath', './/div[@role="group"]/div')

        for xpath_categoria in xpath_categorias:

            url = xpath_categoria.find_element(
                'tag name', 'a').get_attribute('href')
            categoria = xpath_categoria.text

            lista.append((categoria, url))

        return lista

    def parse(self, response):
        pass
