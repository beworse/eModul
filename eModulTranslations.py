from logging import getLogger
from pathlib import Path
import os
import yaml

# TO-DO: Currently module and language are case sensitive 
class eModulTranslations:
    def __init__(self, dir):
        self.__init_logger()
        self.__path = os.path.abspath(dir)
        self._log.info(f"{self.__path =}")
        self.__translations = {}

    def __init_logger(self):
        self._log = getLogger(self.__class__.__name__)

    def get_translation(self, language: str):
        self.get_translations()
        if not language in self.__translations.keys():
            self._log.error(f"Language {language} not available.")
            raise Exception("Language {language} not available.")
        return self.__translations[language]

    def get_translation_module(self, language: str, module: str):
        l = self.get_translation(language)
        if not module in l.keys():
            self._log.error(f"Module {module} is missing.")
            raise Exception(f"Module {module} is missing.")
        return l[module]

    def get_translations(self):
        if self.__translations == {}:
            self.__translations = self.load_languages()
            if self.__translations == {}:
                self._log.error("Translations undetected! Please verify path")
                raise Exception("Translations undetected!")
        return self.__translations
        
    def load_language(self, fname):
        self._log.info(f"Trying to find language in file \"{fname}\".")
        language = ""
        m = {}
        with open(fname, 'r') as file:
            docs = yaml.load_all(file, yaml.FullLoader)
            for doc in docs:
                if "language" in doc.keys():
                    language = doc["language"]
                elif "module" in doc.keys():
                    modul = doc["module"]
                    if "translations" in doc.keys():
                        m[modul] = doc["translations"]
                    else:
                        self._log.warning(f"Missing translations for module:"
                            f"{module}.")
                else:
                    self._log.warning(f"Unknown section: {doc}")
        data = {}
        if language == "":
            self._log.warning("Unknown language.")
        elif m == {}:
            self._log.warning("Translations undetected.")
        else:
            data[language] = m
        return data

    def load_languages(self):
        languages = {}
        for entry in os.listdir(self.__path):
            self._log.info(f"{entry =}")
            file = os.path.join(self.__path, entry)
            if (not os.path.isfile(file)) \
                and ("yaml" != Path(file).suffix):
                continue
            l = self.load_language(file)
            languages.update(l)
        self._log.info(f"Loaded languages: {languages.keys()}")
        self._log.debug(f"Full dictionary:\n{yaml.dump(languages)}")
        return languages
