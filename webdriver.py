from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import subprocess, os, asyncio, websockets, time, logging, math
## manipulação de excel
import pandas as pd
import openpyxl
from openpyxl import Workbook, load_workbook
from openpyxl.styles import PatternFill
from openpyxl.styles import Font, Alignment
from openpyxl.formatting.rule import IconSet, FormatObject, Rule
from datetime import datetime, timedelta
import os
import psutil


def fechar_processos_chrome():
    # Percorre todos os processos em execução
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            # Verifica se o nome do processo contém 'chrome'
            if 'chrome' in proc.info['name'].lower():
                # Obtém o PID (identificador do processo) e o fecha
                pid = proc.info['pid']
                processo = psutil.Process(pid)
                processo.terminate()
                print(f"Processo Chrome com PID {pid} foi encerrado.")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

async def aguardar_elemento(driver, tempo, tipo, code):
    try:
        if tipo == 'CSS':   
            element = WebDriverWait(driver, tempo).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, code))
            )
        elif tipo == 'ID':
            element = WebDriverWait(driver, tempo).until(
                EC.element_to_be_clickable((By.ID, code))
            )  
        return element
    except Exception as e:  
        # print(f'\x1b[36m erro ao aguardar elemento {e}\x1b[0m')
        return 'Elemento não encontrado'

async def listar_pagina(driver):
    try:
        print(f'\x1b[32m>>> Listando elementos da página \x1b[33m {driver.current_url} <<<\x1b[0m')

        # Identificar e imprimir informações sobre os elementos
        elementos = driver.find_elements(By.XPATH, "//*")  # XPath para todos os elementos
        for indice, elemento in enumerate(elementos):
            # Imprimir informações sobre o elemento
            print(f"Elemento {indice + 1}:")
            print(f"  - ID: {elemento.get_attribute('id')}")
            xpath_elemento = driver.execute_script("""
                    function absoluteXPath(element) {
                        var comp, comps = [];
                        var parent = null;
                        var xpath = '';
                        var getPos = function(element) {
                            var position = 1, curNode;
                            if (element.nodeType == Node.ATTRIBUTE_NODE) {
                                return null;
                            }
                            for (curNode = element; curNode; curNode = curNode.nextSibling) {
                                if (curNode.nodeType == Node.ELEMENT_NODE) {
                                    if (curNode.nodeName == element.nodeName) {
                                        ++position;
                                    }
                                }
                            }
                            return position;
                        };

                        if (element instanceof Document) {
                            return '/';
                        }

                        for (; element && !(element instanceof Document); element = element.nodeType == Node.ATTRIBUTE_NODE ? element.ownerElement : element.parentNode) {
                            comp = comps[comps.length] = {};
                            switch (element.nodeType) {
                                case Node.TEXT_NODE:
                                    comp.name = 'text()';
                                    break;
                                case Node.ATTRIBUTE_NODE:
                                    comp.name = '@' + element.nodeName;
                                    break;
                                case Node.PROCESSING_INSTRUCTION_NODE:
                                    comp.name = 'processing-instruction()';
                                    break;
                                case Node.COMMENT_NODE:
                                    comp.name = 'comment()';
                                    break;
                                case Node.ELEMENT_NODE:
                                    comp.name = element.nodeName;
                                    break;
                            }
                            comp.position = getPos(element);
                        }

                        for (var i = comps.length - 1; i >= 0; i--) {
                            comp = comps[i];
                            xpath += '/' + comp.name.toLowerCase();
                            if (comp.position !== null) {
                                xpath += '[' + comp.position + ']';
                            }
                        }

                        return xpath;
                    }

                    return absoluteXPath(arguments[0]);
                """, elemento)

           
           
            print(f"  - XPATH: {xpath_elemento}")
            print(f"  - Texto: {elemento.text}")
            print("\x1b[34m\n" + "-"*50 + "\n\x1b[0m")  # Separador para melhor legibilidade
    except Exception as e: print(f'\x1b[36m >>> Erro ao listar elementos da página <<<\n {e}\x1b[0m')
    
def abrir_navegador(browser='chrome'):
    fechar_processos_chrome()

    try:
        if browser.lower() == 'chrome':
            chrome_options = Options()
            
            # Set Chrome options for headless mode and no-sandbox
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')  # Disable GPU acceleration
            chrome_options.add_argument('--no-sandbox')   # Disable sandboxing for non-graphical environment
            chrome_options.add_argument('--disable-dev-shm-usage')  # Disable /dev/shm usage
            chrome_options.add_argument('--disable-software-rasterizer')  # Desativar rasterização de software
            chrome_options.add_argument('--disable-extensions')  # Desativar extensões
            chrome_options.add_experimental_option('prefs', {'download.default_directory': os.path.join(os.getcwd(), 'geracao')})
            # verificar ultima versão disponível do chromedriver
            try:
                import requests

                url = 'https://chromedriver.storage.googleapis.com/LATEST_RELEASE'
                response = requests.get(url)

                if response.status_code == 200:
                    latest_version = response.text.strip()
                    print(f"Última versão do Chromedriver disponível: {latest_version}")
                else:
                    print("Não foi possível obter a versão mais recente do Chromedriver.")        
            except Exception as e:  # dessa forma pode ser acessado via localhost (otimização de tempo de teste)
                    print(f'> ERRO NO TESTE \n >>> {e}')
                    return e
                        # Add logging preferences to capture browser logs
            chrome_options.add_argument('--enable-logging')
            chrome_options.add_argument('--log-level=2')  # Set log level (0 = INFO, 1 = WARNING, 2 = ERROR)

            try: # dessa forma executa em conteiner (railway)
                driver = webdriver.Chrome(options=chrome_options)
                print('\x1b[42m>>> 🌐   WEBDRIVER INICIADO COM SUCESSO! [via opt] <<<\x1b[0m')

            except Exception as e:  # dessa forma pode ser acessado via localhost (otimização de tempo de teste)
                try:
                    driver_manager = ChromeDriverManager()
                    # version latest release 114.0.5735.90
                    driver = webdriver.Chrome(executable_path=driver_manager.install(), options=chrome_options)
                    print('\x1b[42m>>> 🌐   WEBDRIVER INICIADO COM SUCESSO! [via executable_path install] <<<\x1b[0m')

                except Exception as e: 
                      # Tentativa de iniciar o webdriver com chromedriver no mesmo diretório
                    try:
                        chromedriver_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chromedriver')
                        driver = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)
                        print(f'\x1b[42m>>> 🌐   WEBDRIVER INICIADO COM SUCESSO! [via webdriver local] <<<\npath = {chromedriver_path}\x1b[0m')

                    except Exception as e:
                        # Tratamento de erro ao iniciar o webdriver
                        driver = None
                        print(f'\x1b[41m>>> Erro ao iniciar o webdriver {e}\x1b[0m')

                    # try -> RAILWAY (só options)
                    # except -> MÁQUINA LOCAL (executable_path.install() + option)
                    #       try -> EXECUTABLE PATH COM WEBDRIVER LOCAL APP
                    #       except: -> ERRO AO INICIAR WEBDRIVER
                    #               try -> executar no firefox (instalar no dockerfile)
                    #               except -> desisto
                    driver = None
                    print(f'\x1b[41m>>> Erro ao iniciar o webdriver {e}\x1b[0m')
            
            return driver

        if browser.lower() == 'whatsapp':
            chrome_options = Options()
            
            # Set Chrome options for headless mode and no-sandbox
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')  # Disable GPU acceleration
            chrome_options.add_argument('--no-sandbox')   # Disable sandboxing for non-graphical environment
            chrome_options.add_argument('--disable-dev-shm-usage')  # Disable /dev/shm usage
            chrome_options.add_argument('--disable-software-rasterizer')  # Desativar rasterização de software
            chrome_options.add_argument('--disable-extensions')  # Desativar extensões
            chrome_options.add_experimental_option('prefs', {'download.default_directory': os.path.join(os.getcwd(), 'geracao')})
            dir_path = os.getcwd()
            profile = os.path.join(dir_path, "Relatórios de Geração - Whatsapp", "wpp")
            options.add_argument(r"user-data-dir={}".format(profile))
            # verificar ultima versão disponível do chromedriver
            try:
                import requests

                url = 'https://chromedriver.storage.googleapis.com/LATEST_RELEASE'
                response = requests.get(url)

                if response.status_code == 200:
                    latest_version = response.text.strip()
                    print(f"Última versão do Chromedriver disponível: {latest_version}")
                else:
                    print("Não foi possível obter a versão mais recente do Chromedriver.")        
            except Exception as e:  # dessa forma pode ser acessado via localhost (otimização de tempo de teste)
                    print(f'> ERRO NO TESTE \n >>> {e}')
                    return e
                        # Add logging preferences to capture browser logs
            chrome_options.add_argument('--enable-logging')
            chrome_options.add_argument('--log-level=2')  # Set log level (0 = INFO, 1 = WARNING, 2 = ERROR)

            try: # dessa forma executa em conteiner (railway)
                driver = webdriver.Chrome(options=chrome_options)
                print('\x1b[42m>>> 🌐   WEBDRIVER WHATSAPP INICIADO COM SUCESSO! [via opt] <<<\x1b[0m')

            except Exception as e:  # dessa forma pode ser acessado via localhost (otimização de tempo de teste)
                try:
                    driver_manager = ChromeDriverManager()
                    # version latest release 114.0.5735.90
                    driver = webdriver.Chrome(executable_path=driver_manager.install(), options=chrome_options)
                    print('\x1b[42m>>> 🌐   WEBDRIVER WHATSAPP INICIADO COM SUCESSO! [via executable_path install] <<<\x1b[0m')

                except Exception as e: 
                      # Tentativa de iniciar o webdriver com chromedriver no mesmo diretório
                    try:
                        chromedriver_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chromedriver')
                        driver = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)
                        print(f'\x1b[42m>>> 🌐   WEBDRIVER WHATSAPP INICIADO COM SUCESSO! [via webdriver local] <<<\npath = {chromedriver_path}\x1b[0m')

                    except Exception as e:
                        # Tratamento de erro ao iniciar o webdriver
                        driver = None
                        print(f'\x1b[41m>>> Erro ao iniciar o webdriver WHATSAPP {e}\x1b[0m')

                    # try -> RAILWAY (só options)
                    # except -> MÁQUINA LOCAL (executable_path.install() + option)
                    #       try -> EXECUTABLE PATH COM WEBDRIVER LOCAL APP
                    #       except: -> ERRO AO INICIAR WEBDRIVER
                    #               try -> executar no firefox (instalar no dockerfile)
                    #               except -> desisto
                    driver = None
                    print(f'\x1b[41m>>> Erro ao iniciar o webdriver WHATSAPP {e}\x1b[0m')
            
            return driver   
        else:
            print(f'Unsupported browser: {browser}')

    except Exception as e:
        print(f'ERRO AO ABRIR NAVEGADOR -> {e}')
