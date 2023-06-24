from time import sleep

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains


def abaixar_rolagem(driver, xpath, movepx):
    scroll_bar = driver.find_element(
        'xpath', xpath)
    action = ActionChains(driver)
    action.click_and_hold(scroll_bar).perform()
    action.move_by_offset(0, movepx).perform()
    action.release().perform()


def check_exists_by_xpath(xpath, driver):
    try:
        driver.find_element('xpath', xpath)
    except NoSuchElementException:
        return False
    return True


def set_dash_filters(driver):

    expanded_items = driver.find_elements(
        'xpath', '//div[@class="slicerItemContainer"]')

    for items in expanded_items:
        if items.get_attribute('aria-expanded') == 'false':
            items.find_element(
                'xpath', './/div[@class="expandButton"]').click()

    sleep(5)
    semanas_selecionadas = driver.find_elements(
        'xpath', '//div[@class="slicerItemContainer"][@aria-level="3"]/div[@class="slicerCheckbox selected"]')

    for semana_selecionada in semanas_selecionadas:
        semana_selecionada.click()

    sleep(2)


def select_filter(driver, value, filter_value):

    dict_filter = {
        'NACIONALIDADE': 0,
        'REGIAO': 1,
        'UF': 2
    }

    filter_number = dict_filter[filter_value]

    driver.find_elements(
        'xpath', '//div[@class="slicer-dropdown-menu"]')[filter_number].click()
    sleep(2)

    driver.find_element(
        'xpath', f'//span[@class="slicerText"][@title="{value}"]').click()

    driver.find_elements(
        'xpath', '//div[@class="slicer-dropdown-menu"]')[filter_number].click()
