#/usr/bin/env python

from dataclasses import dataclass

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement

from typing import Tuple
import logging

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
       
    def _get_elements(self, name: str) -> WebElement:
        return self._driver.find_elements(By.CLASS_NAME, name)

    def _get_url(self) -> str:
        return self._driver.command_executor._url
   
    def __init_logger(self):
        self._log = logging.getLogger(self.__class__.__name__)
   
    def _set_element_value(self, name, value: str) -> WebElement:
        element = self._driver.find_element(By.NAME, name)
        element.send_keys(value)
        return element

@dataclass
class eModulLoginPanelClassNames:
    alertButton : str = "app-alert__button"
    alertMessage: str = "app-alert__message"
    languageHeader : str = "login-header__language-box"
    languageElemnt: str = "languages-list__element"
    loginButton : str = "login-box__button"

class eModulLoginPanel(eModulBase):
    def __init__(self, webdriver = None):
        super().__init__(webdriver)
        self.init_page("https://emodul.pl/login")

    def login(self, user: str, password: str):
        self._set_element_value("username", user)
        self._set_element_value("password", password)
        self._click_element(eModulLoginPanelClassNames.loginButton)
        self.verify_login()
       
    def verify_login(self) -> bool:
        # TODO: check url
        try:
            btn = self._get_element(eModulLoginPanelClassNames.alertButton)\
                         .get_attribute("value")
            error = self._get_element(eModulLoginPanelClassNames.alertMessage)\
                        .text
            self._log.error(f"error")
            self._log.info(f"Available button: {btn}")
            return False
        except exceptions.NoSuchElementException:
            self._log.info(f"login success")
            return True

    def get_languages(self) -> Tuple[str]:
        current_language = self._click_element(
                eModulLoginPanelClassNames.languageHeader)
        elements = self._get_elements(eModulLoginPanelClassNames.languageElemnt)
        languages =[language.text for language in elements]
        current_language.click()
        self._log.info(f"Available Languages: {languages}")
        return tuple(languages)

    def set_language(self, language: str) -> bool:
        self._click_element(eModulLoginPanelClassNames.languageHeader)
        elements = self._get_elements(eModulLoginPanelClassNames.languageElemnt)
        for element in elements:
            if element.text.lower() == language.lower():
                element.click()
                self._log.info(f"Language changed to {language}")
                return True
        self._log.warning(f"Language {language} not found.")
        return False


@dataclass
class eModulBaseModuleClassNames:
    moduleSelectionButton : str = "module-selection__name"
    moduleSelectionElement : str = "module-selection-list__element"


from collections import namedtuple
#TODO: selected look incorrect
#TODO: printing this it looks terrible in logs
Selected = namedtuple("Selected", "name element")

class eModulBaseModule(eModulBase):
    available_modules : [Selected] = []
    selected_module : Selected = None

    def __init__(self, webdriver = None):
        super().__init__(webdriver)

    def read_available_modules(self) -> bool:
        if len(self.available_modules) > 0:
            self._log.info(f"No need to read modules again. Available modules:"\
                " {self.available_modules}")
            return True
        try:
            self._click_element(eModulBaseModuleClassNames\
                .moduleSelectionButton)
            self._log.info("There is more than one module available.")
            elements = self._get_elements(eModulBaseModuleClassNames\
                .moduleSelectionElement)
            self.available_modules = [\
                Selected(module.text, module)\
                for module in elements\
                if len(module.text) > 0]
            self._log.info(f"Available modules: {self.available_modules}.")
            for element in elements:
                if len(element.text) == 0:
                    continue
                self._log.info(f"type: {element}")
                #TODO: move module-slection ...
                selected = element.find_element(By.CLASS_NAME, "module-selection-list__icon") \
                    .get_attribute("src")
                if "selected.svg" in selected:
                    self.selected_module = Selected(element.text, element)
                    self._log.info(f"Selected element: {self.selected_module}")
                    element.click()
                    return True
            self._log.error("Couldn't find selected module")
            return False
        except exceptions.NoSuchElementException:
            self._log.error("Couldn't get available modules. Probably you" \
                " have only one module available. Use method:" \
                " select_module_forced.")
            return False

    def select_module(self, name: str) -> bool:
        self.read_available_modules()
        toSelect = [module for module in self.available_modules \
            if name.lower() in module.name.lower()]
        if len(toSelect) == 0:
            self._log.error(f"Module: {name} not found")
            return False
        elif len(toSelect) > 1:
            self._log.error(f"Module: {name} find multiple times try to be more specific.")
            return False
        toSelect = toSelect[0]
        self._log.info(f"Selecting module {toSelect.name}")
        self._click_element(eModulBaseModuleClassNames.moduleSelectionButton)
        toSelect.element.click()
        return True

    def select_module_forced(self, module) -> None:
        self._log.info(f"Module set!")
        pass

##########
# docs
#################
# - https://www.selenium.dev/selenium/docs/api/py/webdriver_remote/selenium.webdriver.remote.webelement.html
# - https://www.selenium.dev/selenium/docs/api/py/webdriver/selenium.webdriver.common.by.html
# - https://stackoverflow.com/questions/8344776/can-selenium-interact-with-an-existing-browser-session
# - https://stackoverflow.com/questions/71601442/perform-mouse-actions-in-selenium-python
# - https://stackoverflow.com/questions/47861813/how-can-i-reconnect-to-the-browser-opened-by-webdriver-with-selenium

def configure_logs():
    format = '%(asctime)s %(name)s %(levelname)s: %(message)s'
    logging.basicConfig(
        format=format,
        level=logging.INFO
    )

def main(user: str = "test", password: str = "test" , language: str = "Polski", module: str = "pellet"):
    configure_logs()

    em = eModulLoginPanel()
    #languages = em.get_languages();
    em.set_language(language)
    em.login(user, password)

    em = eModulBaseModule(em._driver)
    em.select_module(module)

if __name__ == "__main__":
    main()
