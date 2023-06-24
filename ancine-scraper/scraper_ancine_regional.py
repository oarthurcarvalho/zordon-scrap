import csv
import os
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        ElementNotInteractableException,
                                        NoSuchElementException)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from utils import abaixar_rolagem, select_filter


def getNextWeek(driver, num_nextweek):
    xpath = f'//div[@class="slicerItemContainer"][@aria-level="2"][@aria-posinset="{num_nextweek}"]'

    i = 0
    while True:
        try:
            week = driver.find_element('xpath', xpath)
            week.click()
            break
        except ElementClickInterceptedException:
            abaixar_rolagem(driver,
                            './/div[@class="scroll-wrapper scrollbar-inner"][1]/div[3]/div/div[3]', 40)
        except NoSuchElementException:
            abaixar_rolagem(driver,
                            './/div[@class="scroll-wrapper scrollbar-inner"][1]/div[3]/div/div[3]', 40)
            i += 1
            if i > 5:
                return num_nextweek, None

    return num_nextweek + 1, week


def verificar_mais_filmes(driver, num_movies, num_last_movie):
    cond1 = int(
        driver.find_elements(
            'xpath', '//div[@class="card"]')[0]
        .get_attribute('aria-label').split()[-3])
    cond2 = int(
        driver.find_elements(
            'xpath', '//div[@class="card"]')[-1]
        .get_attribute('aria-label').split()[-3])

    return True if (cond1 < num_last_movie + 1) and \
        (cond2 < num_movies) else False


def scraper_regiao(region_filter, semana_select):

    service = Service(ChromeDriverManager().install())

    chrome_options = Options()
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('--headless')

    driver = webdriver.Chrome(options=chrome_options, service=service)
    driver.maximize_window()

    url_pbi = 'https://app.powerbi.com/view?r=eyJrIjoiM2ViZGRmMjctYjZlNC00NjI4LWFiZDEtMDAzZjk2OTU2OGYyIiwidCI6ImIwYThiNWFkLTU5MGQtNGZiYS1hZmY4LWUzMDc0YWI0MzVhNyJ9&pageName=ReportSectiona448b45fb6e3695eb8ba'
    wait = WebDriverWait(driver, 10)
    driver.get(url=url_pbi)

    wait.until(EC.visibility_of_all_elements_located(
        (By.CSS_SELECTOR, 'transform.bringToFront')))

    sleep(10)

    # Limpar os filtros do dashboard
    driver.find_element('xpath',
                        '//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-group[2]/transform/div/div[2]/visual-container-group/transform/div/div[2]/visual-container[2]/transform/div/div[2]/div').click()

    movie_filters = ['BRASILEIRA', 'ESTRANGEIRA']

    list_films = {}

    for filter in movie_filters:

        select_filter(driver, filter, 'NACIONALIDADE')
        wait.until(EC.visibility_of_all_elements_located(
            (By.CSS_SELECTOR, 'transform.bringToFront')))

        regiao_filtro = region_filter.keys()

        for region in regiao_filtro:

            select_filter(driver, region, 'REGIAO')
            wait.until(EC.visibility_of_all_elements_located(
                (By.CSS_SELECTOR, 'transform.bringToFront')))

            uf_filter = region_filter[region]

            for uf in uf_filter:

                select_filter(driver, uf, 'UF')
                wait.until(EC.visibility_of_all_elements_located(
                    (By.CSS_SELECTOR, 'transform.bringToFront')))

                num_week, semana = getNextWeek(driver, semana_select)
                wait.until(EC.visibility_of_all_elements_located(
                    (By.CSS_SELECTOR, 'transform.bringToFront')))

                while semana is not None:

                    sleep(2)
                    name_semana = semana.find_element(
                        'xpath', './/span[@class="slicerText"]').text.split('- ')[-1]

                    num_semana = semana.find_element(
                        'xpath', './/span[@class="slicerText"]').text.split("\u2003")[0]

                    card_filmes_exibidos = driver.find_elements(
                        'tag name', 'tspan')

                    num_movies = int(
                        card_filmes_exibidos[1].text) if card_filmes_exibidos[1].text != '(Blank)' else 0
                    num_last_movie = 0
                    index = 0
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
                            titulo = info[0]
                            publico = info[1].split(
                            )[-1].rstrip('.0').replace(',', '')
                            sessoes = info[2].split()[-1].replace(',', '')

                            cod_film = name_semana + titulo + uf

                            list_films[cod_film] = [
                                num_semana, name_semana, rank_position, titulo, publico, sessoes, filter, region, uf]
                            print(num_semana, name_semana, rank_position,
                                  titulo, publico, sessoes, filter, region, uf)

                        num_last_movie = int(
                            info[-1].split()[0]) if num_movies != 0 else 0

                        if num_movies == num_last_movie:
                            break
                        try:

                            while verificar_mais_filmes(driver, num_movies, num_last_movie):
                                try:
                                    abaixar_rolagem(
                                        driver, '//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-group[5]/transform/div/div[2]/visual-container-group/transform/div/div[2]/visual-container[2]/transform/div/div[2]/div/visual-modern/div/div/div/div[3]/div/div[3]', 30)
                                    sleep(1)
                                except ElementNotInteractableException:
                                    pass
                        except IndexError:
                            pass

                    semana.click()
                    sleep(1)
                    num_week, semana = getNextWeek(driver, num_week)
                    wait.until(EC.visibility_of_all_elements_located(
                        (By.CSS_SELECTOR, 'transform.bringToFront')))
                abaixar_rolagem(driver,
                                './/div[@class="scroll-wrapper scrollbar-inner"][1]/div[3]/div/div[3]', -100)
            select_filter(driver, uf, 'UF')
        select_filter(driver, region, 'REGIAO')
        sleep(1)

    driver.find_element(
        'xpath', '//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-group[7]/transform/div/div[2]/visual-container[2]/transform/div/div[2]/div').click()
    sleep(5)

    # Limpar os filtros do dashboard
    driver.find_element('xpath',
                        '//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-group[2]/transform/div/div[2]/visual-container-group/transform/div/div[2]/visual-container[2]/transform/div/div[2]/div').click()

    for filter in movie_filters:

        select_filter(driver, filter, 'NACIONALIDADE')

        regiao_filtro = region_filter.keys()

        for region in regiao_filtro:

            select_filter(driver, region, 'REGIAO')

            uf_filter = region_filter[region]

            for uf in uf_filter:

                select_filter(driver, uf, 'UF')

                num_week, semana = getNextWeek(driver, semana_select)

                while semana is not None:

                    name_semana = semana.find_element(
                        'xpath', './/span[@class="slicerText"]').text.split('- ')[-1]

                    num_semana = semana.find_element(
                        'xpath', './/span[@class="slicerText"]').text.split("\u2003")[0]

                    sleep(2)
                    card_filmes_exibidos = driver.find_elements(
                        'tag name', 'tspan')

                    num_movies = int(
                        card_filmes_exibidos[1].text) if card_filmes_exibidos[1].text != '(Blank)' else 0
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
                            preco_medio = card.find_elements(
                                'xpath', './/div[@class="caption"]')[1].text.rstrip('.0').replace(',', '')
                            renda = card.find_elements(
                                'xpath', './/div[@class="caption"]')[0].text.replace(',', '')

                            cod_film = name_semana + titulo + uf

                            try:
                                list_films[cod_film].append(renda)
                                list_films[cod_film].append(preco_medio)
                            except:
                                continue

                            print(num_semana, name_semana, rank_position,
                                  titulo, renda, preco_medio, filter, region, uf)

                        num_last_movie = int(
                            info[-1].split()[0]) if num_movies != 0 else 0
                        num_movies = int(
                            info[-1].split()[2].replace('.', '')) if card_filmes_exibidos[1].text != '(Blank)' else 0

                        if num_movies == num_last_movie:
                            break

                        index = 0
                        while (int(driver.find_elements('xpath', '//div[@class="card"]')[0].get_attribute('aria-label').split()[-3]) < num_last_movie + 1) and \
                                (int(driver.find_elements('xpath', '//div[@class="card"]')[-1].get_attribute('aria-label').split()[-3]) < num_movies):
                            if index == 20:
                                break
                            abaixar_rolagem(driver, '//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-group[5]/transform/div/div[2]/visual-container-group/transform/div/div[2]/visual-container[2]/transform/div/div[2]/div/visual-modern/div/div/div/div[3]/div/div[3]', 30)

                    semana.click()
                    num_week, semana = getNextWeek(driver, num_week)
                abaixar_rolagem(driver,
                                './/div[@class="scroll-wrapper scrollbar-inner"][1]/div[3]/div/div[3]', -100)
            select_filter(driver, uf, 'UF')
        select_filter(driver, region, 'REGIAO')

    filename = f'output_{region}.csv'
    arquivo_existe = os.path.isfile(filename)
    header = ['num_semana', 'name_semana', 'rank', 'titulo', 'publico',
              'sessoes', 'nacionalidade', 'regiao', 'uf', 'renda',
              'preco_medio']

    with open(filename, 'a', newline='', encoding='utf-8') as file:

        writer = csv.writer(file)

        if not arquivo_existe or os.stat(filename).st_size == 0:
            writer.writerow(header)

        for line in list_films.values():
            linha = [str(value) for value in line]
            writer.writerow(linha)
