import constraints
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class HandleDash:

    def __init__(self, url) -> None:

        self.driver = self.__set_config()
        self.driver.get(url=url)

    def handle_dash(self, type='click'):

        if type == 'click':
            self.__click()
        else:
            self.__scroll()

    def select_filter(self, value, filter):

        xpath_filter = f'//div[@class="slicer-dropdown-menu"]\
            [@aria-label={filter}]'

        xpath_value = f'//span[@class="slicerText"][@title="{value}"]'

        self.__click('xpath', xpath_filter)
        self.__wait_load()
        self.__click('xpath', xpath_value)
        self.__wait_load()
        self.__click('xpath', xpath_filter)
        self.__wait_load()

    def get_driver(self):
        return self.driver

    def clear_filters(self):
        self.__click('xpath', constraints.RESET_BUTTON)

    def __set_config(self):
        service = Service(ChromeDriverManager().install())

        chrome_options = Options()
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--headless')

        driver = webdriver.Chrome(options=chrome_options, service=service)
        driver.maximize_window()

        return driver

    def __wait_load(self):

        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.visibility_of_all_elements_located(
            (By.CSS_SELECTOR, 'transform.bringToFront')))

    def __click(self, by, element):
        week = self.driver.find_element(by, element)
        week.click()
        self.__wait_load()

    def __scroll(self, by, element, movepx):
        scroll_bar = self.driver.find_element(by, element)
        action = ActionChains(self.driver)
        action.click_and_hold(scroll_bar).perform()
        action.move_by_offset(0, movepx).perform()
        action.release().perform()
        self.__wait_load()
