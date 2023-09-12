import csv
import os
from datetime import datetime, timedelta
from time import sleep

import pandas as pd
import scrapy
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

DATA_COLETA = (datetime.now() - timedelta(days=1)).strftime('%d-%m-%Y')
print(DATA_COLETA)

SPIDER_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SPIDER_DIR)
ROOT_DIR = os.path.dirname(PROJECT_DIR)
DATA_DIR = os.path.join(ROOT_DIR, 'data')


class TtSpider(scrapy.Spider):
    name = "tt"
    allowed_domains = ["archive.twitter-trending.com"]
    start_urls = [
        f"https://archive.twitter-trending.com/brazil/{DATA_COLETA}"
    ]
    path_file_tempo = os.path.join(DATA_DIR, 'twitterTrendings_tempo.csv')
    path_file_volume = os.path.join(DATA_DIR, 'twitterTrendings_volume.csv')

    def parse(self, response):

        self.verifica_arquivo(
            self.path_file_tempo,
            ['index', 'tag', 'tempo', 'data']
        )

        self.verifica_arquivo(
            self.path_file_volume,
            ['index', 'tag', 'volume', 'data']
        )

        flag_volume = False
        flag_tempo = False

        data_tempo_tempo = self.verificar_maior_data(self.path_file_tempo)
        data_tempo_volume = self.verificar_maior_data(self.path_file_volume)

        if data_tempo_tempo == DATA_COLETA:
            flag_tempo = True
        if data_tempo_volume == DATA_COLETA:
            flag_volume = True

        if flag_tempo and flag_volume:
            return None

        my_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'

        options = webdriver.ChromeOptions()
        options.add_argument(f"user-agent={my_agent}")

        service = Service(ChromeDriverManager().install())

        driver = webdriver.Chrome(options=options, service=service)
        driver.get('https://archive.twitter-trending.com/brazil/%s' %
                   (DATA_COLETA.replace('/', '-')))

        df = pd.DataFrame(columns=['data', 'horario', 'tag', 'volume'])

        sleep(10)

        cards = driver.find_elements(
            'class name', 'tek_tablo')

        for card in cards:

            horario = card.find_element('class name', 'trend_baslik611').text

            tags_name = card.find_elements('class name', 'tr_table')
            tags_number = card.find_elements('class name', 'tr_table1')

            for i in range(len(tags_name)):

                tag_name = tags_name[i]
                tag_number = tags_number[i]

                hashtag = tag_name.find_element('class name', 'word_ars').text
                print(tag_number.get_attribute('class'))
                try:
                    hashtag_vol = tag_number.find_element(
                        'class name', 'volume61').text
                    hashtag_vol = hashtag_vol.split()[0].replace('.', '')
                except NoSuchElementException:
                    hashtag_vol = 0

                new_row = {
                    'data': DATA_COLETA, 'horario': horario,
                    'tag': hashtag, 'volume': hashtag_vol
                }

                df = pd.concat(
                    [df, pd.DataFrame([new_row])],
                    ignore_index=True
                )

        self.ranking_time(df)
        self.ranking_volume(df)

    def ranking_time(self, dataframe):
        tempo = timedelta(minutes=30)

        ranking = dataframe.groupby('tag').size().sort_values(ascending=False)
        df_ranking = ranking * tempo

        df_ranking = df_ranking.reset_index()
        df_ranking.columns = ['tag', 'tempo']
        df_ranking['tempo'] = df_ranking['tempo']\
            .astype(str).str.extract(r'(\d+:\d+)')
        df_ranking.index += 1
        df_ranking['data'] = DATA_COLETA

        df_ranking.to_csv(
            self.path_file_tempo,
            header=False,
            mode='a'
        )

    def ranking_volume(self, dataframe):

        dataframe['volume'] = pd.to_numeric(
            dataframe['volume'],
            errors='coerce'
        )

        dataframe = dataframe.dropna(subset=['volume'])

        df_ranking = dataframe.groupby('tag')['volume']\
            .max().astype('int64').sort_values(ascending=False).reset_index()
        df_ranking.index += 1
        df_ranking['data'] = DATA_COLETA

        df_ranking.to_csv(self.path_file_volume, header=False, mode='a')

    def verifica_arquivo(self, path, header):
        if not os.path.isfile(path):
            with open(path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(header)

    def verificar_maior_data(self, path):
        maior_data = None

        with open(path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)

            # Verificar se há mais de uma linha no leitor
            if sum(1 for _ in reader) <= 1:
                return None

            # Voltar para o início do arquivo
            file.seek(0)

            # Pular a primeira linha, se houver
            next(reader, None)

            for row in reader:
                data_str = row[3]
                data = datetime.strptime(data_str, '%d-%m-%Y')

                if maior_data is None or data > maior_data:
                    maior_data = data

        return maior_data.strftime('%d-%m-%Y') \
            if maior_data is not None else None
