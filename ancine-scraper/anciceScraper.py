import re
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        NoSuchElementException)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager


class AncineScraper:

    def __init__(self, driver) -> None:
        self.driver = driver
        self.scroll_periodos = './/div[@class="scroll-wrapper scrollbar-inner"][1]/div[3]/div/div[3]'
        self.clear_button = '//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-group[2]/transform/div/div[2]/visual-container-group/transform/div/div[2]/visual-container[2]/transform/div/div[2]/div'
        self.nacionalidade = ['ESTRANGEIRA', 'BRASILEIRA']
        self.list_films = {}
        self.filtro_nacionalidade = '//div[@class="slicer-restatement"]'
        self.texto_periodo = './/span[@class="slicerText"]'

    def scrap(self):

        for filter in self.nacionalidade:
            self.resetar_dropdown()
            self.selecionar_dropdown(filter)
            num_week, semana = self.getNextWeek(driver, 1)

            while semana is not None:

                name_semana = semana.find_element(
            'xpath', self.texto_periodo).text.split('- ')[-1]

                num_semana = semana.find_element(
                    'xpath', self.texto_periodo).text.split("\u2003")[0]

                sleep(2)
                card_filmes_exibidos = driver.find_elements('tag name', 'tspan')

                num_movies = int(card_filmes_exibidos[1].text)
                num_last_movie = 0

                while True:
                    cards_filmes = driver.find_elements(
                        'xpath', '//div[@class="card"]')

                    if (num_movies - num_last_movie) < len(cards_filmes):
                        num_new_cards = num_movies - num_last_movie
                    else:
                        num_new_cards = 0

                    for card in cards_filmes[num_new_cards * -1:]:
                        info = card.get_attribute('aria-label').split('. ')
                        rank_position = info[-1].split()[0]
                        titulo = card.find_element(
                            'xpath', './/div[@class="title"]').text
                        publico = card.find_elements(
                            'xpath', './/div[@class="caption"]')[0].text.rstrip('.0').replace(',', '')
                        sessoes = card.find_elements(
                            'xpath', './/div[@class="caption"]')[1].text.replace(',', '')

                        cod_film = name_semana + titulo

                        self.list_films[cod_film] = [num_semana, name_semana, rank_position, titulo, publico, sessoes, filter, "Nacional"]
                        print(num_semana, name_semana, rank_position,
                      titulo, publico, sessoes, filter, "Nacional")

                    num_last_movie = int(info[-1].split()[0])
                    num_movies = int(info[-1].split()[2].replace('.', ''))


    def abaixar_rolagem(self, xpath, movepx):
        scroll_bar = self.driver.find_element(
            'xpath', xpath)
        action = ActionChains(self.driver)
        action.click_and_hold(scroll_bar).perform()
        action.move_by_offset(0, movepx).perform()
        action.release().perform()

    def getNextWeek(self, num_nextweek):
        xpath = f'//div[@class="slicerItemContainer"][@aria-level="2"][@aria-posinset="{num_nextweek}"]'

        i = 0
        while True:
            try:
                week = self.driver.find_element('xpath', xpath)
                week.click()
                break
            except ElementClickInterceptedException:
                self.abaixar_rolagem(
                    self.scroll_periodos, 40)
            except NoSuchElementException:
                self.abaixar_rolagem(
                    self.scroll_periodos, 40)
                i += 1
                if i > 5:
                    return num_nextweek, None

        return num_nextweek + 1, week

    def resetar_dropdown(self):
        if driver.find_elements('xpath', self.filtro_nacionalidade)[0].text != "All":
            valor = driver.find_elements(
                'xpath', '//div[@class="slicer-restatement"]')[0].text
            driver.find_elements(
                'xpath', '//div[@class="slicer-dropdown-menu"]')[0].click()

            driver.find_element(
                'xpath', f'//div[@class="slicerItemContainer"]/span[@title="{valor}"]').click()

            driver.find_elements(
                'xpath', '//div[@class="slicer-dropdown-menu"]')[0].click()

    def selecionar_dropdown(self, filter):
        driver.find_elements(
            'xpath', '//div[@class="slicer-dropdown-menu"]')[0].click()
        sleep(1)
        driver.find_element(
            'xpath', f'//span[@class="slicerText"][@title="{filter}"]').click()

        driver.find_elements(
            'xpath', '//div[@class="slicer-dropdown-menu"]')[0].click()
        sleep(1)

    def get_data(self):




if __name__ == '__main__':
    service = Service(ChromeDriverManager().install())

    chrome_options = Options()
    chrome_options = webdriver.ChromeOptions()

    driver = webdriver.Chrome(options=chrome_options, service=service)
    driver.maximize_window()

    url = 'https://www.gov.br/ancine/pt-br/oca/resultados-cinema-brasileiro/painel-de-ranking-de-filmes'

    driver.get(url=url)
    # driver.maximize_window()
    sleep(1)
    driver.refresh()
    sleep(2)

    driver.find_element(
        'xpath', '//button[@class="br-button secondary small btn-accept"]').click()

    url_pbi = driver.find_element(
        'xpath', '//iframe[@title="Painel de Ranking Filmes"]').get_attribute('src')
    driver.get(url=url_pbi)
    sleep(10)

    scrap = AncineScraper(driver)
    scrap.scrap()
