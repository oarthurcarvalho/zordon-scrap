import requests
import scrapy
from bs4 import BeautifulSoup
from lxml import etree


class FolhaSpSpider(scrapy.Spider):
    name = "folha_sp"
    allowed_domains = ["www1.folha.uol.com.br"]
    start_urls = [
        "https://www1.folha.uol.com.br/maispopulares/#educacao/mais-lidas"]

    def parse(self, response):

        # user_agent = '--user-agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"'

        url = "https://www1.folha.uol.com.br/maispopulares/#educacao/mais-lidas"

        response = requests.get(url)

        html = response.text

        # Crie um objeto BeautifulSoup
        soup = BeautifulSoup(html, 'lxml')

        # Converta o objeto BeautifulSoup para um objeto ElementTree do lxml
        element_tree = etree.HTML(str(soup))

        xpath_expression = '//li[@class="c-most-popular__item"]'
        li_elements = element_tree.xpath(xpath_expression)

        print()
        print()
        print()
        print(len(li_elements))
        print()
        print()
        print()

        # Itere sobre os elementos encontrados
        for li_element in li_elements:

            print(li_element.text)
