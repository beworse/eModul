from logging import getLogger

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

class eModulBase:
    def __init__(self, driver = None, implicitly_wait: int = 3):
        self.__init_logger()

        if driver != None:
            self._driver = driver
        else:
            self._driver = webdriver.Firefox()
            self._driver.implicitly_wait(implicitly_wait)

    def init_page(self, url: str):
        self._driver.get(url)

    def _click_element(self, className: str) -> WebElement:
        element = self._driver.find_element(By.CLASS_NAME , className)
        element.click()
        return element

    def _get_element(self, name: str) -> WebElement:
        return self._driver.find_element(By.CLASS_NAME, name)
    
    def _get_elemnt_from_element(self, name:str, element:WebElement, mandatory: bool):
        try:
            sub_element = element.find_element(By.CLASS_NAME, name)
            return sub_element
        except exceptions.NoSuchElementException:
            if mandatory:
                raise exceptions.NoSuchElementException()
            self._log.warning(f"No element: {name} return None")
            return None

    def _get_text_from_element(self, name:str, element:WebElement, mandatory: bool):
        try:
            sub_element = element.find_element(By.CLASS_NAME, name)
            return sub_element.text
        except exceptions.NoSuchElementException:
            if mandatory:
                raise exceptions.NoSuchElementException()
            return ""

    def _get_elements(self, name: str) -> WebElement:
        return self._driver.find_elements(By.CLASS_NAME, name)

    def _get_url(self) -> str:
        return self._driver.command_executor._url

    def __init_logger(self):
        self._log = getLogger(self.__class__.__name__)

    def _set_element_value(self, name, value: str) -> WebElement:
        element = self._driver.find_element(By.NAME, name)
        element.send_keys(value)
        return element
