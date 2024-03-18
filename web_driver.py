from time import sleep
import random

import pandas as pd
from faker import Faker

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from time import sleep
import os
from selenium import webdriver
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from verificacao.verify_proposonal import verify_proposonal
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver import *
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Cores ANSI
colors = [(30, "Black"), (31, "Red"), (32, "Green"), (33, "Yellow"), (34, "Blue"),(35, "Magenta"), (36, "Cyan"), (37, "White")]

class WebDriver():
    username = 'kinsol.servidor@gmail.com'
    password = 'kinsolbot10'
    URLS = {}

    def check():
            print('\033[92m----- STATUS CHECK -----\033[0m❓❔❓❔❓❔❓❔❓❔')

    def __init__(self, environment):
        self.URLS = {
            'login': f'http://localhost:8000/',
            
            'propostasv2': {
                'lista_de_clientes': f'http://localhost:8000/admin/propostas-v2/listar-clientes',
                'criar_novo': f'http://localhost:8000/admin/propostas-v2/adicionar-cliente',
                'log_url_adicionar_cliente': f'http://localhost:8000/admin/propostas-v2/adicionar_cliente'
            }
        }

        try:

            self.driver = abrir_navegador()
            self.driver.maximize_window()
        
        except Exception as erro: print(f'🚨 : {erro}')
        
    def login_site(self) -> bool:
        try:
            # Acessa o site
            self.driver.get(self.URLS['login'])
            # Informar usuário
            print('\033[36m----- Realizando Login... -----\033[0m🔐')

            self.driver.find_element(By.NAME, 'email').send_keys(self.username)
            # Informar senha
            self.driver.find_element(By.NAME, 'password').send_keys(self.password)
            # Clicar no botão de login
            self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
            return True

        except:
            try:
                url_atual = self.driver.current_url()
                print(url_atual)
                if url_atual == 'https://app-lab.kinsol.com.br/admin/calendar?user=me' or url_atual == 'https://app-dev.kinsol.com.br/admin/calendar?user=me':
                    print('\033[32m----- Login Realizado com sucesso !... -----\033[0m🔐')
                    return True
            except: return False
        
    def element_select_option_by_text(self, element:object, value:str='') -> None:
        """"""
        select = Select(element)
        try:
            try:
                    select.select_by_value(value)
                    # print(f'Selecionando value : {value}')
            except:
                try:
                    select.select_by_visible_text(value)
                    # print(f'Selecionando texto : {value}')

                except:        
                    # print(f'Selecionando index 1')
                    select.select_by_index(1)
                    select.select_by_value
        except Exception as e: print(f'Erro ao selecionar {value}: {e}')
            
    def element_select_option_by_index(self, element:object='', value:int=0) -> None:
        """"""
        select = Select(element)
        try:
            select.select_by_index(value)
        except:
            select.select_by_index(1)
    
    def insert_monthly_consumption(self) -> None:
            try:
                input_monthly = self.driver.find_element(By.CSS_SELECTOR, '#app > div.card.bg-white.px-5.py-3 > div > div:nth-child(5) > div.col > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > input')
                input_monthly.clear()
                input_monthly.send_keys('500')

                replicar_button = self.driver.find_element(By.CSS_SELECTOR, '#labelConsumoMedio > button')
                replicar_button.click()
            except Exception as e: print(f'Erro ao inserir consumação mensal: {e}')

    def handle_verify_proposonal(self) -> dict:
        """
        Verifica se algum campo de ambas as propostas deram NAN ou negatívo
        """
        try:
            df = pd.read_excel('./RPA-PropostaV2.xlsx', sheet_name='Planilha2')
            proposal = df.set_index('Nome Campo - Proposta')['Valores esperados'].to_dict()
        except Exception as e: print(f'Erro handle_verify_proposonal: ',e)
        try:
            retorno_da_verificacao =  verify_proposonal(self.driver)
        except Exception as erro:
            retorno_da_verificacao = f'ERRO NA VERIFICAÇÃO: {erro}'

        return retorno_da_verificacao

    def create_proposal(self) -> None:

        excel_file = pd.ExcelFile('./RPA-PropostaV2.xlsx')
        sheet_name = random.choice(excel_file.sheet_names)
        print('\n📑 >>> Planilha selecionada: ', sheet_name)
        df = pd.read_excel('./RPA-PropostaV2.xlsx',
            sheet_name=sheet_name)
        proposal = df.set_index('Nome Campo - Inserção')['Valores a inserir'].to_dict()
        
        # print('>>> ', proposal)

        # Clicar em gerar proposta
        try:
            try:
                self.driver.find_element(By.XPATH,
                    '/html/body/div[2]/div/main/div[2]/div/div/div/div[2]/div/form/div/div[2]/a').click()
            except:
                self.driver.find_element(By.CSS_SELECTOR, 'body > div.d-flex.flex-column.flex-root > div > main > div.content.pt-3.px-3.px-lg-6.d-flex.flex-column-fluid > div > div > div > div.card.bg-white.p-2.mb-5 > div > form > div > div.col-md-3 > a').click()

                print('\n🖱️ >>> Clicou em Gerar Proposta')
        except NoSuchElementException as er:
            print('>>> [error]', er)
            return False
        sleep(5)

        try:
            self.driver.execute_script(
                "arguments[0].click();",
                self.driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/div/div[1]/input')
            )
            sleep(1)
            print('\n🖱️ >>> Clicou em flexSwitchCheckDefault (Usar endereço de cobrança)')
        except NoSuchElementException as er:
            print('>>> [error]', er)
        
        while True:
            if self.driver.find_element(
                By.ID, 'inputRegiao').get_attribute('value').strip() != '':
                
                break
            sleep(2)
        
        try:
            self.insert_monthly_consumption()
        except Exception as e: print(f'>>> Erro ao inserir monthly consumption: \n {e}')
        
        def verificar_selects():
                valor_campo = self.driver.find_element(By.ID, 'inputSistema').get_attribute('value')
                print(f'Tipo de Sistema = {valor_campo}')

                valor_campo = self.driver.find_element(By.ID, 'inputTipoEstrutura').get_attribute('value')
                print(f'Tipo de Estrutura = {valor_campo}')       
                
                valor_campo = self.driver.find_element(By.ID, 'inputEstrutura').get_attribute('value')
                print(f'Estrutura = {valor_campo}')

                valor_campo = self.driver.find_element(By.ID, 'inputFace').get_attribute('value')
                print(f'Face = {valor_campo}')     

                valor_campo = self.driver.find_element(By.ID, 'inputSombreamento').get_attribute('value')
                print(f'Sombreamento = {valor_campo}')

                valor_campo = self.driver.find_element(By.ID, 'inputQuantidadeFase').get_attribute('value')
                print(f'Quantidade de Fases = {valor_campo}')       
                
                valor_campo = self.driver.find_element(By.ID, 'inputTensaoFase').get_attribute('value')
                print(f'Tensão das Fases = {valor_campo}')

                valor_campo = self.driver.find_element(By.ID, 'inputDisjuntorEntrada').get_attribute('value')
                print(f'Disjuntor de Entrada = {valor_campo}') 
                
                valor_campo = self.driver.find_element(By.ID, 'inputAreaDisponivel').get_attribute('value')
                print(f'Área disponível para instalação = {valor_campo}')     

                valor_campo = self.driver.find_element(By.ID, 'inputDistanciaInversor').get_attribute('value')
                print(f'Distância do inversor até os módulos = {valor_campo}')

                # valor_campo = self.driver.find_element(By.ID, 'inputDistanciaCA').get_attribute('value')
                # print(f'Distância CA = {valor_campo}')       
                
                valor_campo = self.driver.find_element(By.ID, 'inputConcessionaria').get_attribute('value')
                print(f'Concessionária = {valor_campo}')

                valor_campo = self.driver.find_element(By.ID, 'inputTipoInstalacao').get_attribute('value')
                print(f'Tipo Instalação = {valor_campo}') 
                
                valor_campo = self.driver.find_element(By.ID, 'inputCanalCampanha').get_attribute('value')
                print(f'Canal de Campanha = {valor_campo}')
 


        try:

            # clicar em botão invisivel
            self.driver.execute_script(
                "arguments[0].click();",
                self.driver.find_element(By.ID, 'btn-automacao')
        )
            sleep(2)

        except Exception as e: print(f'Erro no botão automação: {e}')

        try:
            # Tipo do sistema
            try:
                self.driver.find_element(By.ID, 'auto-inputSistema').send_keys('ON-GRID') # ON-GRID
            except Exception as e: print(f'Erro ao selecionar tipo de sistema: {e}')

            # Tipo da estrutura
            self.driver.find_element(By.ID, 'auto-inputTipoEstrutura').send_keys('1') # TELHADO


            # Estrutura
            values_estrutura = ['FIBROCIMENTO (Fixação Madeira)','FIBROCIMENTO (Fixação Metálica)','CERÂMICO','METÁLICO']
            self.driver.find_element(By.ID, 'auto-inputEstrutura').send_keys(random.choice(values_estrutura))
            
            # Face 
            values_face = ['1','2','3','4','5','6','7','8','9']
            self.driver.find_element(By.ID, 'auto-inputFace').send_keys(random.choice(values_face))
            
            # Sombreamento
            values_sombreamento = ['1','2','3','4']
            self.driver.find_element(By.ID, 'auto-inputSombreamento').send_keys(random.choice(values_sombreamento))
            
            # Quantidade de fases
            values_qtdefases = ['1','2','3']
            self.driver.find_element(By.ID, 'auto-inputQuantidadeFase').send_keys(random.choice(values_qtdefases))
            
            # Tensão das fases
            values_tensao_fase = ['127','220']
            self.driver.find_element(By.ID, 'auto-inputTensaoFase').send_keys(random.choice(values_tensao_fase)) 

            # Dijuntor entrada(A)
            values_disjuntor_entrada = ['6','10','16','20','25','32','40','50','63','70','90','100','110','120','150','180','200','250','300']
            self.driver.find_element(By.ID, 'auto-inputDisjuntorEntrada').send_keys(random.choice(values_disjuntor_entrada))
            
            area_disponivel  = self.driver.find_element(By.ID, 'inputAreaDisponivel')
            area_disponivel.send_keys(proposal['ÁREA DISOPONÍVEL (m²)'])
            area_disponivel.send_keys(Keys.TAB)  # Simulate pressing the Tab key
            sleep(2)     
            
            # distancia inversor até os módulos (Distância CC)
            values_distancia_inversor = ['< 10m','< 20m',' < 30m','> 30m']
            self.driver.find_element(By.ID, 'auto-inputDistanciaInversor').send_keys(random.choice(values_distancia_inversor))
            
            # valores_disponiveis_ca = [15,35,45,60,61]
            # # distancia inversor até o padrão (Distância CA)
            # self.element_select_option_by_text(
            #     self.driver.find_element(By.ID, 'inputDistanciaCA'),
            #     random.choice(valores_disponiveis_ca))


            # Concessionária
            values_concessionaria = ['ALIANÇA - Cooperativa Aliança','CELPA - Centrais Elétricas do Pará S/A','CELPE - Companhia Energética de Pernambuco','CEMAR - Companhia Energética do Maranhão','CHESP - Companhia Hidroelétrica São Patrício','COCEL - Companhia Campolarguense de Energia','COELBA - Companhia de Eletricidade do Estado da Bahia','COSERN - Companhia Energética do Rio Grande do Norte','CPFL PAULISTA - Companhia Paulista de Força e Luz','CPFL PIRATININGA - Companhia Piratininga de Força e Luz','CPFL SANTA CRUZ - Companhia Luz e Força Santa Cruz','EDP ES - EDP ESPÍRITO SANTO – DISTRIBUIÇÃO DE ENERGIA ELÉTRICA S.A.','EDP SP - EDP SÃO PAULO – DISTRIBUIÇÃO DE ENERGIA ELÉTRICA S.A.','ELEKTRO - Elektro Eletricidade e Serviços S/A','ENEL - Metropolitana Eletricidade de São Paulo S.A.','ENEL CE - Enel Distribuição Ceará','ENEL-GO - Enel Distribuicão Goiás','ENEL RJ - Enel Distribuição Rio','ENERGISA BO - Energisa Borborema – Distribuidora de Energia S/A','ENERGISA MG - Energisa Minas Gerais – Distribuidora de Energia S/A','ENERGISA MS - Energisa Mato Grosso do Sul – Distribuidora de Energia S/A','ENERGISA MT - Energisa Mato Grosso – Distribuidora de Energia S/A','FORCEL - Força e Luz Coronel Vivida Ltda.','IGUAÇU ENERGIA - Iguaçu Distribuidora de Energia Elétrica Ltda.','JARI - Jari Energética S/A. – JESA','LIGHT - Light Serviços de Eletricidade S/A','MUXFELDT - Muxfeldt, Marin & Cia Ltda.','NOVA PALMA - Usina Hidroelétrica Nova Palma (UENPAL)','PANAMBI - Hidroelétrica Panambi S.A (HIDROPAN)']
            self.driver.find_elements(By.ID, 'auto-inputConcessionaria')[0].send_keys(random.choice(values_concessionaria))
            sleep(2)

            # Tipo de instalação
            values_tipo_instalacao = ['0','1','2','3','4','5','6','7']
            self.driver.find_element(By.ID, 'auto-inputTipoInstalacao').send_keys(random.choice(values_tipo_instalacao))
            
            # Canal de campanha
            values_campanha = ['INDICAÇÃO','MÍDIAS SOCIAIS','SITE','PESQUISA','CAMPANHA NACIONAL']
            self.driver.find_element(By.ID, 'auto-inputCanalCampanha').send_keys(random.choice(values_campanha))
            

            # Inserir Custo (R$ / kWh)
            try:
                input_kwh = self.driver.find_element(By.ID, 'campo-custo-0')
                input_kwh.clear()
                print(proposal['CUSTO (R$ / kWh)'])
                custo = proposal['CUSTO (R$ / kWh)']
                input_kwh.send_keys(custo)
            except Exception as e: 
                input_kwh = self.driver.find_element(By.ID, 'campo-custo-0')
                input_kwh.clear()
                input_kwh.send_keys('1.11')

            # Inserir CIP
            input_cip = self.driver.find_element(By.ID, 'campo-cosip-0')
            input_cip.clear()
            input_cip.send_keys(proposal['CIP (ou COSIP)'])
            sleep(5)
            
        except Exception as e: print(f'[ERRO dentro do Inserir]: {e}')

        print('\n\n\x1b[33mIMPRIMIR VALORES DOS CAMPOS ANTES DE CLICAR NO BOTÃO GERAR SISTEMA RECOMENDADO\x1b[0m')
        verificar_selects()
        # botão gerar proposta
        self.driver.execute_script(
            "arguments[0].click();",
            self.driver.find_element(By.CSS_SELECTOR, '#app > div.card.bg-white.px-5.py-3 > button')
        )
        sleep(2)

        
        return True
        # return False
    
    def get_customer(self) -> str:
        data = {'nome': '', 'status': True}
        self.driver.get(self.URLS['propostasv2']['lista_de_clientes'])
        sleep(5)
        
        buttons_edit = self.driver.find_elements(By.CSS_SELECTOR, 'a[title="Editar usuário"]')
        
        # Pegar aleatoriamente um cliente dos 10 primeiros exibidos na tela
        buttons_edit[random.randint(0, 9)].click()
        sleep(5)
        data['nome'] = self.driver.find_element(By.NAME, 'nome').get_attribute('value').strip()
        
        if not self.create_proposal():
            data = {'status': False}
        
        return data
        
    def create_cliente(self) -> dict:
        zip_codes = ['14026-080', '05182-480', '59123-540', '91750-072',
            '23030-625', '68903-389', '69059-845', '68903-369',
            '11310-030', '84172-090', '76908-323', '66055-901']
        select_cep = zip_codes[random.randint(0, (len(zip_codes) - 1))]
    
        self.driver.get(self.URLS['propostasv2']['criar_novo'])
        fake = Faker('pt_BR')
        sleep(2)
        
        # Pessoais
        fake_cpf = fake.cpf()
        fake_email = fake.email()
        fake_nome_completo = fake.name()
        fake_estado_civil = random.choice(['solteiro', 'casado'])
        fake_rg = fake.rg()
        fake_emprego = 'tester'
        fake_telefone = fake.phone_number()
        fake_celular = fake.cellphone_number()
        
        self.driver.find_element(By.NAME, 'cnpj').send_keys(fake_cpf)
        self.driver.find_element(By.NAME, 'email').send_keys(fake_email)
        self.driver.find_element(By.ID, 'nome').send_keys(fake_nome_completo)
        self.driver.find_element(By.ID, 'estado-civil').send_keys(fake_estado_civil)
        self.driver.find_element(By.ID, 'rg').send_keys(fake_rg)
        self.driver.find_element(By.ID, 'emprego').send_keys(fake_emprego)
        self.driver.find_element(By.ID, 'telefone').send_keys(fake_telefone)
        self.driver.find_element(By.ID, 'celular').send_keys(fake_celular)
        # Endereço
        fake_numero = str(random.randint(100, 700))
        self.driver.find_element(By.ID, 'form-cep').send_keys(select_cep)
        sleep(2)
        self.driver.find_element(By.ID, 'form-numero').click()
        sleep(3)
        self.driver.find_element(By.ID, 'form-numero').send_keys(fake_numero)
        
        sleep(2)
        ## imprimir dados gerados para o cliente
        try:
            cliente = (
                f"\n\n👤    NOVO CLIENTE CADASTRADO    ✔️\n"
                f"CPF/CNPJ: {fake_cpf}    |  email: {fake_email}\n"
                f"Nome Completo: {fake_nome_completo}\n"
                f"Estado Civil: {fake_estado_civil}  | RG: {fake_rg}\n"
                f"Emprego: {fake_emprego}   | CEP {select_cep}\n"
                f"Telefone {fake_telefone}   | Celular {fake_celular}\n\n"
            )
            print(f'\033[36m {cliente}\033[0m')
        except Exception as e: print(f'>>> ERROR: {e}')
        self.driver.execute_script(
            "arguments[0].click();",
            self.driver.find_element(By.CSS_SELECTOR, 'input[value="CADASTRAR CLIENTE"]')
        )
        
        sleep(5)
        
        try:
            data = {'nome': '', 'cpf': '', 'status': True}
            # print('VERIFICAR E ANOTAR EM DATA')
            data['nome'] = fake_nome_completo
            data['cpf'] =  fake_cpf
            print(data['nome'])
        except Exception as e: print('>>> data: ', e)
        try:
            if not self.create_proposal():
                data = {'status': False}
        except Exception as e: print(f'>>> erro no create_proposal: {e}')
        
        print('\n\n\033[36m>>> Tela de Cadastro de Cliente finalizada!\033[0m\n\n')

        return data
    
    def aprove(self,aprove) -> None:
        if aprove == 'weg':
            botao = '#app > div.d-flex.justify-content-around.row > div:nth-child(1) > div.row.align-items-center > div.col-md-4.text-center.d-md-inline > div > button.btn.btn-outline-success.text-start > i'
        else:
            botao = '#app > div.d-flex.justify-content-around.row > div:nth-child(2) > div.row.align-items-center > div.col-md-4.text-center.d-md-inline > div > button.btn.btn-outline-success.text-start'
        self.driver.find_element(By.CSS_SELECTOR, botao).click()

    def gerar_contrato(self, aprove) -> None:
        botao_locator = (
            'body > div.d-flex.flex-column.flex-root > div.page.d-flex.flex-row.flex-column-fluid > main > div.content.pt-3.px-3.px-lg-6.d-flex.flex-column-fluid > div > div > div > div.card.mb-5.bg-white > div > div.row > '
            f'div.row{"Weg" if aprove == "weg" else "Deye"}.col.mb-4 > div.row.align-items-center > div.col-md-4.text-center.d-none.d-md-inline > div > button.btn.btn-outline-gray.text-start.btnGerarContratoModal.btnGerarContrato{aprove.capitalize()}'
        )
        if aprove == "weg":
            botao_locator = '#app > div.d-flex.justify-content-around.row > div:nth-child(1) > div.row.align-items-center > div.col-md-4.text-center.d-md-inline > div > button:nth-child(3)'
        else:
            botao_locator = '#app > div.d-flex.justify-content-around.row > div:nth-child(2) > div.row.align-items-center > div.col-md-4.text-center.d-md-inline > div > button:nth-child(3)'

        try:
            # Aguarda até que o botão esteja visível e clicável
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, botao_locator))
            )
            
            self.driver.find_element(By.CSS_SELECTOR, botao_locator).click()
            print(f'Clicou no botão Gerar Contrato')
            

            #TRY EXCEPT DE LISTAR TODOS OS BOTÕES DA PÁGINA COM O TEXTO ATRIBUIDO A ELE 
            # Agora, para listar todos os botões com texto atribuído a eles na página
            # buttons_with_text = self.driver.find_elements(By.TAG_NAME, "button")
            # ok = True
            # while ok == True:# Itera sobre os botões e imprime o texto e outros atributos, se necessário
            #     for button in buttons_with_text:
            #         if button.text.strip():  # Verifica se o texto não está em branco
            #             # se conter o texto Ok, Entendi! no botão, imprimir o texto do botão
            #             if "Ok, Entendi!" in button.text:
            #                 print("Texto do botão:", button.text)
            #             if button.text == 'Ok, Entendi! (0)':
            #                 button.click()
            #                 print(f'\x1b[34m🖱️ Clicou em Ok, Entendi! \x1b[0m')
            #                 ok = False
                

            try:
                while True:
                    # Encontre todos os botões com texto
                    buttons_with_text = self.driver.find_elements(By.TAG_NAME, "button")
                    texto_alvo = 'Ok, Entendi! (0)'
                    for button in buttons_with_text:
                        if texto_alvo in button.text:
                            try:
                                button.click()
                                print(f'\x1b[34m🖱️ Clicou em {texto_alvo}\x1b[0m')
                            except StaleElementReferenceException:
                                # Trate exceção de elemento obsoleto e continue
                                pass

                    sleep(2)
            except Exception as e:
                print(f'Ocorreu um erro: {e}')

            # Franqueado Responsável
            franqueado = 'Gabriel Graton'
            cpf = '123456789'
            try:
                self.driver.find_element(By.ID, 'franqueadoResponsavel').send_keys(franqueado)
                self.driver.find_element(By.ID, 'franqueadoIdentificacaoCPF').send_keys(cpf)
            except Exception as e: print(f'Erro ao inserir dados do franqueado')
            try:
                # Encontre todos os botões com texto
                buttons_with_text = self.driver.find_elements(By.TAG_NAME, "button")
                texto_alvo = 'AVANÇAR arrow_forward'
                for button in buttons_with_text:
                    if texto_alvo == button.text:
                        print(button.text)
                        try:
                            self.driver.execute_script("arguments[0].click();", button)
                            print(f'\x1b[34m🖱️ Clicou em {texto_alvo}\x1b[0m')
                        except Exception as e:
                            print(f'Erro ao clicar em {texto_alvo}: {e}')

                sleep(2)
            except Exception as e:
                print(f'Ocorreu um erro: {e}')
            try:
               ## Selecionar forma de pagamento À Vista

               print(f'\x1b[34m✏️ Atualizando Forma de Pagamento 💳')
               self.element_select_option_by_text(self.driver.find_element(By.ID, 'formaPagamento'),'À Vista')
               self.element_select_option_by_text(self.driver.find_element(By.ID, 'formaPagamentoOpcaoAVista'), 'Pix')
               self.element_select_option_by_text(self.driver.find_element(By.ID, 'monitoramento'), random.choice(['Auto Monitoramento','Essencial', 'Completo', 'Premium']))
               self.element_select_option_by_text(self.driver.find_element(By.ID,  'monitoramentoPrazo'), random.choice(['1 Ano', '2 Anos', '3 Anos', '4 Anos', '5 Anos', '6 Anos', '7 Anos', '8 Anos', '9 Anos', '10 Anos']))
               self.element_select_option_by_text(self.driver.find_element(By.ID, 'monitoramentoFormaPagamento'), 'À Vista')
               self.element_select_option_by_text(self.driver.find_element(By.ID, 'monitoramentoOpcaoPagamentoAVista'), 'Pix')
            except Exception as e:
                print(f'Erro ao clicar no botão: {e}')

            try:
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '#stepper-step-2 > div.d-flex.justify-content-between > button.btn.btn-primary'))
                )
                # Execute o script JavaScript para clicar no elemento
                css_selector = '#stepper-step-2 > div.d-flex.justify-content-between > button.btn.btn-primary'
                script = f"document.querySelector('{css_selector}').click();"
                self.driver.execute_script(script)
                sleep(2)
            except Exception as e: 
                print(f'Erro ao clicar no botão avançar: {e}')
            
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '#stepper-step-3 > div.d-flex.justify-content-between > button.btn.btn-primary'))
                )
                print(f'Botão Encontrado:  AVANÇAR ->   ')
                # Execute o script JavaScript para clicar no elemento
                css_selector = '#stepper-step-3 > div.d-flex.justify-content-between > button.btn.btn-primary'
                script = f"document.querySelector('{css_selector}').click();"
                self.driver.execute_script(script)
                sleep(2)
            except Exception as e: 
                print(f'Erro ao clicar no botão avançar: {e}')

            try:
                self.driver.find_element(By.ID, 'signatarioContrato1').clear()
                self.driver.find_element(By.ID, 'signatarioContrato1').send_keys('automacoeskinsol@gmail.com')
                self.driver.find_element(By.ID, 'generate-pdf').click()
            except Exception as e: print(e)

        except TimeoutException:
            print("Tempo limite excedido ao aguardar elementos.")
        except Exception as e:
            print(f"Ocorreu um erro: {str(e)}")