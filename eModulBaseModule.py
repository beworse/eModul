from dataclasses import dataclass

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By

import time
from typing import List

from eModulTypes import NamedElement
from eModulLoginPanel import eModulLoginPanel

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
        #TO-DO: wait for webpage load not with sleep ...
        self._log.info(f"Loading new selected module {name} home elements.")
        time.sleep(5)
        return True

    def select_module_forced(self, moduleName: str) -> None:
        self.selected_module = NamedElement(moduleName, None)
        self._log.info("Module {moduleName} set by force.")

    #TO_DO: new class?
    def get_home_values(self):
        status_elements = self._get_elements("tile__status")
        for status_element in status_elements:
            name = self._get_text_from_element("tile__subtitle", status_element, True)

            #settings_button = self._get_elemnt_from_element("tile__setting", status_element, False)
            #TO-DO: Additional check is required all status_elemnts has this class
            #settings_button = None
            #has_setting_button = True if (settings_button != None) else False

            current_value = self._get_text_from_element("tile__value-current", status_element, False)
            # is it temperature value ?
            if current_value != "":
                set_value = self._get_text_from_element("tile__value-set-temp", status_element, False)
            else:
                current_value = self._get_text_from_element("settings-tile-svg-stroke", status_element, False)
                if current_value != "":
                    set_value = "100%"
                else:
                    set_value = ""
            self._log.info(f"{name}: {current_value=}, {set_value=}")
            #self._log.info(f"{name}: {current_value=}, {set_value=}, {has_setting_button=}.")
