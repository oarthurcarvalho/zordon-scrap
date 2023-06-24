import csv
import os
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        NoSuchElementException)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

service = Service(ChromeDriverManager().install())

chrome_options = Options()
chrome_options = webdriver.ChromeOptions()

driver = webdriver.Chrome(options=chrome_options, service=service)
driver.maximize_window()

while True:
    try:
        semana_select = int(input(
            'Digite o número da semana que você deseja obter os dados: '))
        break
    except ValueError:
        print('Digite apenas o número da semana')

url = 'https://www.gov.br/ancine/pt-br/oca/\
    resultados-cinema-brasileiro/painel-de-ranking-de-filmes'


def abaixar_rolagem(xpath, movepx):
    scroll_bar = driver.find_element(
        'xpath', xpath)
    action = ActionChains(driver)
    action.click_and_hold(scroll_bar).perform()
    action.move_by_offset(0, movepx).perform()
    action.release().perform()


def verificar_rolagem(valor_atual, ultimo_valor):
    return True if (valor_atual > ultimo_valor and valor_atual != 0) else False


def check_exists_by_xpath(xpath, driver=driver):
    try:
        driver.find_element('xpath', xpath)
    except NoSuchElementException:
        return False
    return True


def getNextWeek(driver, num_nextweek):
    xpath = f'//div[@class="slicerItemContainer"][@aria-level="2"]\
        [@aria-posinset="{num_nextweek}"]'

    i = 0
    while True:
        try:
            week = driver.find_element('xpath', xpath)
            week.click()
            break
        except ElementClickInterceptedException:
            abaixar_rolagem(
                './/div[@class="scroll-wrapper scrollbar-inner"]\
                    [1]/div[3]/div/div[3]', 40)
        except NoSuchElementException:
            abaixar_rolagem(
                './/div[@class="scroll-wrapper scrollbar-inner"]\
                    [1]/div[3]/div/div[3]', 40)
            i += 1
            if i > 5:
                return num_nextweek, None

    return num_nextweek + 1, week


driver.get(url=url)
# driver.maximize_window()
sleep(1)
driver.refresh()
sleep(2)
driver.find_element(
    'xpath', '//button[@class="br-button secondary small btn-accept"]').click()


url_pbi = driver.find_element(
    'xpath',
    '//iframe[@title="Painel de Ranking Filmes"]').get_attribute('src')
driver.get(url=url_pbi)
sleep(10)

# Limpar os filtros do dashboard
driver.find_element('xpath',
                    '//*[@id="pvExplorationHost"]/div/div/exploration/div/\
                        explore-canvas/div/div[2]/div/div[2]/div[2]/\
                            visual-container-repeat/visual-container-group[2]/\
                                transform/div/div[2]/visual-container-group/\
                                    transform/div/div[2]/visual-container[2]/\
                                        transform/div/div[2]/div').click()
movie_filters = ['ESTRANGEIRA', 'BRASILEIRA']

list_films = {}

for filter in movie_filters:
    sleep(3)

    if driver.find_elements(
        'xpath',
            '//div[@class="slicer-restatement"]')[0].text != "All":
        valor = driver.find_elements(
            'xpath', '//div[@class="slicer-restatement"]')[0].text
        driver.find_elements(
            'xpath', '//div[@class="slicer-dropdown-menu"]')[0].click()

        driver.find_element(
            'xpath',
            f'//div[@class="slicerItemContainer"]/span[@title="{valor}"]'
        ).click()

        driver.find_elements(
            'xpath', '//div[@class="slicer-dropdown-menu"]')[0].click()

    driver.find_elements(
        'xpath', '//div[@class="slicer-dropdown-menu"]')[0].click()
    sleep(1)
    driver.find_element(
        'xpath', f'//span[@class="slicerText"][@title="{filter}"]').click()

    driver.find_elements(
        'xpath', '//div[@class="slicer-dropdown-menu"]')[0].click()
    sleep(3)

    num_week, semana = getNextWeek(driver, semana_select)

    while semana is not None:

        name_semana = semana.find_element(
            'xpath', './/span[@class="slicerText"]').text.split('- ')[-1]

        num_semana = semana.find_element(
            'xpath', './/span[@class="slicerText"]').text.split("\u2003")[0]

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
                    'xpath',
                    './/div[@class="caption"]'
                )[0].text.rstrip('.0').replace(',', '')
                sessoes = card.find_elements(
                    'xpath',
                    './/div[@class="caption"]')[1].text.replace(',', '')

                cod_film = name_semana + titulo

                list_films[cod_film] = [num_semana, name_semana, rank_position,
                                        titulo, publico, sessoes, filter,
                                        "Nacional"]
                print(num_semana, name_semana, rank_position,
                      titulo, publico, sessoes, filter, "Nacional")

            num_last_movie = int(info[-1].split()[0])
            num_movies = int(info[-1].split()[2].replace('.', ''))

            if num_movies == num_last_movie:
                break

            while (int(driver.find_elements('xpath', '//div[@class="card"]')[0].get_attribute('aria-label').split()[-3]) < num_last_movie + 1) and \
                    (int(driver.find_elements('xpath', '//div[@class="card"]')[5].get_attribute('aria-label').split()[-3]) < num_movies):
                abaixar_rolagem('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-group[5]/transform/div/div[2]/visual-container-group/transform/div/div[2]/visual-container[2]/transform/div/div[2]/div/visual-modern/div/div/div/div[3]/div/div[3]', 5)

        semana.click()
        num_week, semana = getNextWeek(driver, num_week)
    abaixar_rolagem(
        './/div[@class="scroll-wrapper scrollbar-inner"][1]/div[3]/div/div[3]', -100)
    sleep(1)


driver.find_element(
    'xpath', '//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-group[7]/transform/div/div[2]/visual-container[2]/transform/div/div[2]/div').click()
sleep(5)

# Limpar os filtros do dashboard
driver.find_element('xpath',
                    '//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-group[2]/transform/div/div[2]/visual-container-group/transform/div/div[2]/visual-container[2]/transform/div/div[2]/div').click()

for filter in movie_filters:
    sleep(3)

    if driver.find_elements('xpath', '//div[@class="slicer-restatement"]')[0].text != "All":
        valor = driver.find_elements(
            'xpath', '//div[@class="slicer-restatement"]')[0].text
        driver.find_elements(
            'xpath', '//div[@class="slicer-dropdown-menu"]')[0].click()

        driver.find_element(
            'xpath', f'//div[@class="slicerItemContainer"]/span[@title="{valor}"]').click()

        driver.find_elements(
            'xpath', '//div[@class="slicer-dropdown-menu"]')[0].click()

    driver.find_elements(
        'xpath', '//div[@class="slicer-dropdown-menu"]')[0].click()
    sleep(1)
    driver.find_element(
        'xpath', f'//span[@class="slicerText"][@title="{filter}"]').click()

    driver.find_elements(
        'xpath', '//div[@class="slicer-dropdown-menu"]')[0].click()

    num_week, semana = getNextWeek(driver, semana_select)

    while semana is not None:

        name_semana = semana.find_element(
            'xpath', './/span[@class="slicerText"]').text.split('- ')[-1]

        num_semana = semana.find_element(
            'xpath', './/span[@class="slicerText"]').text.split("\u2003")[0]

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
                renda = card.find_elements(
                    'xpath', './/div[@class="caption"]')[0].text.rstrip('.0').replace(',', '')
                preco_medio = card.find_elements(
                    'xpath', './/div[@class="caption"]')[1].text.replace(',', '')

                cod_film = name_semana + titulo

                try:
                    list_films[cod_film].append(renda)
                    list_films[cod_film].append(preco_medio)
                except:
                    continue

                print(num_semana, name_semana, rank_position,
                      titulo, renda, preco_medio, filter, 'Nacional')

            num_last_movie = int(info[-1].split()[0])
            num_movies = int(info[-1].split()[2].replace('.', ''))

            if num_movies == num_last_movie:
                break

            while (int(driver.find_elements('xpath', '//div[@class="card"]')[0].get_attribute('aria-label').split()[-3]) < num_last_movie + 1) and \
                    (int(driver.find_elements('xpath', '//div[@class="card"]')[5].get_attribute('aria-label').split()[-3]) < num_movies):
                abaixar_rolagem('//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container-group[5]/transform/div/div[2]/visual-container-group/transform/div/div[2]/visual-container[2]/transform/div/div[2]/div/visual-modern/div/div/div/div[3]/div/div[3]', 5)

        semana.click()
        num_week, semana = getNextWeek(driver, num_week)
    abaixar_rolagem(
        './/div[@class="scroll-wrapper scrollbar-inner"][1]/div[3]/div/div[3]', -100)
    sleep(1)

filename = f'output_nacional.csv'
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
