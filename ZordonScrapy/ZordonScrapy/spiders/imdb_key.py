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

        for code in imdb_codes:

            url = f"https://www.imdb.com/title/{code}/keywords/"
            yield scrapy.Request(
                url, callback=self.parse, meta={'imdb_code': code})

    def parse(self, response):
        code = response.meta['imdb_code']

        options = webdriver.ChromeOptions()

        service = Service(ChromeDriverManager(
            version="114.0.5735.90").install())
        driver = webdriver.Chrome(service=service, options=options)

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

        driver.quit()

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
        csv_path = 'data/flixPatrol.csv'
        try:
            with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    imdb_code = row.get('IMDB_cod')

                    if imdb_code:
                        imdb_codes.append(imdb_code)

            return imdb_codes
        except FileNotFoundError as e:
            print(e)
            sys.exit()
