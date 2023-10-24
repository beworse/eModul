#/usr/bin/env python

from collections import namedtuple
from dataclasses import dataclass
import logging

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement

from typing import Tuple, List

NamedElement = namedtuple("WebElement", "name element")

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
    _logged: bool = False

    def __init__(self, webdriver = None):
        super().__init__(webdriver)
        self.init_page("https://emodul.pl/login")

    def login(self, user: str, password: str):
        self._set_element_value("username", user)
        self._set_element_value("password", password)
        self._click_element(eModulLoginPanelClassNames.loginButton)
        if not self.verify_login():
            raise Exception("Couldn't loging. For more details check logs.")

    def is_logged(self) -> bool:
        return self._logged

    def verify_login(self) -> bool:
        #TO-DO: BUG same class is used to inform user that something is wrong
        #       with device on with module.
        try:
            btn = self._get_element(eModulLoginPanelClassNames.alertButton)\
                         .get_attribute("value")
            error = self._get_element(eModulLoginPanelClassNames.alertMessage)\
                        .text
            self._log.error(f"\"{error}\". Available button: {btn}")
            return False
        except exceptions.NoSuchElementException:
            self._log.info("Succefully logged.")
            self._logged = True
            return True

    def get_languages(self) -> Tuple[str]:
        current_language = self._click_element(
                eModulLoginPanelClassNames.languageHeader)
        elements = self._get_elements(eModulLoginPanelClassNames.languageElemnt)
        languages =[language.text for language in elements]
        current_language.click()
        self._log.info(f"Available languages: {languages}")
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
    moduleSelectionIcon : str = "module-selection-list__icon"

class eModulBaseModule(eModulLoginPanel):
    available_modules : List[NamedElement] = []
    selected_module : NamedElement = None

    def __init__(self, webdriver: webdriver = None):
        super().__init__(webdriver)

    def get_module_names(self) -> str:
        if len(self.available_modules) == 0:
            if self.selected_module != None:
                return str([self.select_module.name])
            self._log.warning("Method get_module_names called before"
                " read_available_modules.")
            return str(None)
        return str([module.name for module in self.available_modules])

    def read_available_modules(self) -> bool:
        if len(self.available_modules) > 0:
            self._log.info(f"No need to read modules again. Available modules:"
                " {self.get_module_names()}")
            return True
        try:
            self._click_element(eModulBaseModuleClassNames\
                .moduleSelectionButton)
            self._log.info("There is more than one module available.")
            elements = self._get_elements(eModulBaseModuleClassNames\
                .moduleSelectionElement)
            self.available_modules = [\
                NamedElement(module.text, module)\
                for module in elements\
                if len(module.text) > 0]
            self._log.info(f"Available modules: {self.get_module_names()}.")
            for element in elements:
                if len(element.text) == 0:
                    continue
                selected = element.find_element(By.CLASS_NAME,
                    eModulBaseModuleClassNames.moduleSelectionIcon) \
                    .get_attribute("src")
                if "selected.svg" in selected:
                    self.selected_module = NamedElement(element.text, element)
                    self._log.info(f"Currently smodule module:"
                        f" {self.selected_module.name}")
                    element.click()
                    return True
            self._log.error("Couldn't find selected module")
            return False
        except exceptions.NoSuchElementException:
            self._log.error("Couldn't get available modules. Probably you"
                " have only one module available. Use method:"
                " select_module_forced.")
            return False

    def select_module(self, name: str) -> bool:
        self.read_available_modules()
        toSelect = [module for module in self.available_modules \
            if name.lower() in module.name.lower()]
        if len(toSelect) == 0:
            self._log.error(f"Module: {name} not found!")
            return False
        elif len(toSelect) > 1:
            self._log.error(f"Module: {name} find multiple times try to be more specific.")
            return False
        toSelect = toSelect[0]
        self._log.info(f"Chnage selected module to: {toSelect.name}.")
        self._click_element(eModulBaseModuleClassNames.moduleSelectionButton)
        toSelect.element.click()
        return True

    def select_module_forced(self, moduleName: str) -> None:
        self.selected_module = NamedElement(moduleName, None)
        self._log.info("Module {moduleName} set by force.")

def configure_logs():
    #TO-DO: current approach is bad, because it set logs level for selenium as
    #       well
    format = '%(asctime)s %(name)s %(levelname)s: %(message)s'
    logging.basicConfig(
        format=format,
        level=logging.INFO
    )

def main():
    configure_logs()

    em = eModulBaseModule()
    em.get_languages();
    em.set_language("Polski")
    em.login("test", "test")
    em.select_module("Pellet")

if __name__ == "__main__":
    main()
