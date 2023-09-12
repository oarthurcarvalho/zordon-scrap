import csv
import sys

import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class ImdbKeySpider(scrapy.Spider):
    name = "imdb_key"
    start_urls = ["https://www.imdb.com/"]

    def start_requests(self):
        imdb_codes = self.get_imdb_codes()

        my_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'

        options = webdriver.ChromeOptions()
        options.add_argument(f"user-agent={my_agent}")

        service = Service(ChromeDriverManager().install())

        driver = webdriver.Chrome(options=options, service=service)

        for code in imdb_codes:

            url = f"https://www.imdb.com/title/{code}/keywords/"
            yield scrapy.Request(
                url,
                callback=self.parse, meta={'imdb_code': code, 'driver': driver})

    def parse(self, response):
        code = response.meta['imdb_code']

        driver = response.meta['driver']

        driver.get(response.url)

        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, '//li[@data-testid="list-summary-item"]')
            )
        )

        item_lista = driver.find_elements(
            By.XPATH, '//li[@data-testid="list-summary-item"]')

        dados_lista = []

        for item in item_lista:

            dados = {
                'IMDB_code': code,
                'Keywords': item.find_element(
                    By.XPATH,
                    './/a[contains(@class, "ipc-metadata-list-summary-item__t"\
                        )]').get_attribute("textContent"),
                'Upvotes': item.find_element(
                    By.XPATH,
                    './/span[contains(@class, "ipc-voting__label__count--up"\
                        )]').get_attribute("textContent"),
                'Downvotes': item.find_element(
                    By.XPATH,
                    './/span[contains(@class, "ipc-voting__label__count--down"\
                        )]').get_attribute("textContent")
            }
            dados_lista.append(dados)

        self.escrever_arquivo(dados_lista)

    def escrever_arquivo(self, dados_lista):
        with open(
            'data/imdb_keywords.csv', 'a',
                newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    'IMDB_code', 'Keywords', 'Upvotes', 'Downvotes'
                ]
            )
            if file.tell() == 0:
                writer.writeheader()
            writer.writerows(dados_lista)

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
