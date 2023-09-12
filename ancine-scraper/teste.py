import os
import re
from time import sleep

from elementos import *
from selenium import webdriver
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        ElementNotInteractableException,
                                        NoSuchElementException,
                                        StaleElementReferenceException)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class AncineScraper:

    url_pbi = 'https://app.powerbi.com/view?r=eyJrIjoiM2ViZGRmMjctYjZlNC00NjI4LWFiZDEtMDAzZjk2OTU2OGYyIiwidCI6ImIwYThiNWFkLTU5MGQtNGZiYS1hZmY4LWUzMDc0YWI0MzVhNyJ9&pageName=ReportSectiona448b45fb6e3695eb8ba'

    def __init__(self) -> None:
        self.drv = self.init_driver()
        self.wait = WebDriverWait(self.drv, 10)

    def init_driver(self):

        service = Service(ChromeDriverManager(
            version="114.0.5735.90").install())
        options = webdriver.ChromeOptions()
        drv = webdriver.Chrome(service=service, options=options)
        drv.maximize_window()

        wait = WebDriverWait(drv, 10)
        drv.get(url=self.url_pbi)

        wait.until(EC.visibility_of_all_elements_located(
            (By.CSS_SELECTOR, 'transform.bringToFront')))

        return drv

    def scrap(self, regiao='Nordeste', semana=1, modo='publico'):

        qnt_semanas = self.get_num_week()

        # Limpa todos os filtros
        self.drv.find_element('xpath', RESET_BUTTON).click()
        self.set_movie_filter()
        sleep(10000)
        self.drv.quit()

    def set_movie_filter(self):

        for filter in MOVIE_FILTERS:

            self.select_option('NACIONALIDADE', filter)
            self.set_regiao()

    def set_regiao(self):

        for regiao in REGIOES.keys():

            self.select_option('REGIAO', regiao)
            self.set_uf(regiao)

    def set_uf(self, regiao):

        ufs = REGIOES[regiao]

        for uf in ufs:
            self.select_option('UF', uf)
            self.set_week(1)
            self.select_option('UF', uf)

    def abaixar_rolagem(self, xpath, movepx):
        scroll_bar = self.drv.find_element('xpath', xpath)
        action = ActionChains(self.drv)
        action.click_and_hold(scroll_bar).perform()
        action.move_by_offset(0, movepx).perform()
        action.release().perform()

    def set_week(self, num_nextweek):
        xpath = f'//div[@class="slicerItemContainer"][@aria-level="2"][@aria-posinset="{num_nextweek}"]'

        i = 0
        while True:
            try:
                week = self.drv.find_element('xpath', xpath)
                week.click()
                break
            except ElementClickInterceptedException:
                self.abaixar_rolagem(
                    self.drv,
                    './/div[@class="scroll-wrapper scrollbar-inner"][1]/div[3]/div/div[3]', 40)
            except NoSuchElementException:
                self.abaixar_rolagem(
                    self.drv,
                    './/div[@class="scroll-wrapper scrollbar-inner"][1]/div[3]/div/div[3]', 40)
                i += 1
                if i > 5:
                    return num_nextweek, None

        return num_nextweek + 1, week

    def get_data(self):
        sleep(10)
        print('Pegando data')

    def get_num_week(self):

        texto = self.drv.find_element('tag name', 'tspan').text

        padrao = r'\b(\d+)ª Cinessemana\b'

        correspondencias = re.findall(padrao, texto)

        if correspondencias:
            numero_cinessemana = correspondencias[0]
        else:
            print("Nenhuma correspondência encontrada.")

        return int(numero_cinessemana)

    def select_option(self, filter_value, value):
        dict_filter = {
            'NACIONALIDADE': 0,
            'REGIAO': 1,
            'UF': 2
        }

        filter_number = dict_filter[filter_value]

        (self.drv
         .find_elements(
             'xpath',
             '//div[@class="slicer-dropdown-menu"]')[filter_number]
         .click())

        self.wait.until(EC.invisibility_of_element_located(
            (By.TAG_NAME, 'spinner'))
        )

        (self.drv
         .find_element(
             'xpath',
             f'//span[@class="slicerText"][@title="{value}"]')
         .click())

        (self.drv
         .find_elements(
             'xpath',
             '//div[@class="slicer-dropdown-menu"]')[filter_number]
         .click())


if __name__ == '__main__':

    ancine = AncineScraper()
    ancine.scrap()
