#/usr/bin/env python
from logging import basicConfig, INFO
from eModulBaseModule import eModulBaseModule

def configure_logs():
    #TO-DO: current approach is bad, because it set logs level for selenium as
    #       well
    format = '%(asctime)s %(name)s %(levelname)s: %(message)s'
    basicConfig(format=format, level=INFO)

def main():
    configure_logs()

    em = eModulBaseModule()
    em.get_languages();
    em.set_language("Polski")
    em.login("test", "test")
    em.select_module("Pellet")
    em.get_home_values()

if __name__ == "__main__":
    main()
