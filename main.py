#/usr/bin/env python
from dataclasses import fields
from logging import basicConfig, INFO
from eModulBaseModule import eModulBaseModule
from eModulTranslations import eModulTranslations, PelletTranslations


def configure_logs():
    #TO-DO: current approach is bad, because it set logs level for selenium as
    #       well
    format = '%(asctime)s %(name)s %(levelname)s: %(message)s'
    basicConfig(format=format, level=INFO)

def main():
    configure_logs()
    lang = "Polski"
    module = "Pellet"
    translation = eModulTranslations("./data/").get_translation_module(lang, module)
    pellet_translation = PelletTranslations(**translation)
    print(pellet_translation)

    em = eModulBaseModule()
    em.get_languages();
    em.set_language(lang)
    em.login("test", "test")
    em.select_module(module)
    em.get_home_values()

if __name__ == "__main__":
    main()
