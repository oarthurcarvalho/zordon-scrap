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

    def parse(self, response):

        my_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'

        options = webdriver.ChromeOptions()
        options.add_argument(f"user-agent={my_agent}")

        service = Service(ChromeDriverManager().install())

        driver = webdriver.Chrome(options=options, service=service)
        driver.get(
            'https://www1.folha.uol.com.br/maispopulares/#educacao/mais-lidas')

        sleep(10)

        page_content = driver.page_source

        soup = BeautifulSoup(page_content, 'html.parser')

        noticias = soup.find_all('li', attrs={'class': 'c-most-popular__item'})

        for index, noticia in enumerate(noticias):

            tag = noticia.find(
                'a',
                attrs={'class': 'c-kicker c-most-popular__kicker'})

            if tag is None:
                tag = noticia.find(
                    'span',
                    attrs={'class': 'c-kicker c-most-popular__kicker'})

            div = noticia.find('div', 'c-most-popular__content')
            manchete = div.find('a')

            print(f'{index} - {tag.text.strip()} - {manchete.text}')
        #     test = noticia.find_elements(
        #         'xpath',
        #         '//a[@class="c-kicker c-most-popular__kicker"]')

        #     print()
        #     print(test.text)
        #     print()
