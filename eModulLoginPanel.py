from dataclasses import dataclass
from selenium.common import exceptions
from typing import Tuple

from eModulBase import eModulBase

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
