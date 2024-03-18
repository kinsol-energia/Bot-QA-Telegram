import re
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
def value_is_valid(value) -> dict:
    """
    Verifica se o valor é válido
    """
    print(value)
    try:
        if re.sub(r'[^0-9,]', '', value).isnumeric():
            return True
        
        elif float(re.sub(r'[^0-9,]', '', value).replace(',','.')) < 0:
            return False
        
        return True
    except:
        return False
    
def vermelho(texto):
        print(f'\033[31m {texto} \033[0m')

def verde(texto):
        print(f'\033[36m {texto} \033[0m')

def verify_proposonal(driver) -> dict:
    """Verifica se algum campo de ambas as propostas deram NAN ou negatívo"""
    proposonal_code = ''
    message_list = []
    time.sleep(5)
    try:
        print(f'\x1b[33m AGUARDANDO CARREGAR PROPOSTA \x1b[0m')
        try:
            driver.find_element(By.ID, 'fraseLoading')
            print('Frase Encontrada')
            time.sleep(5)
        except: print("Frase não encontrada")

        # Aguarde até que o preloader desapareça
        WebDriverWait(driver, 90).until(
            EC.invisibility_of_element_located((By.ID, 'fraseLoading'))
        )


        print("Preloader desapareceu, iniciar verificação!")
    except Exception as e:
        print(f"O preloader não desapareceu ou ocorreu um erro.\nERROR-> {e}")
    
    try:
        # http://localhost:8000/admin/propostas-v2/proposta/SP23103323.1
        proposonal_url = driver.current_url
        proposonal_code = proposonal_url.split("/")[-1]
    except: return
    vermelho(f'>>>  TODOS OS ITENS ABAIXO ESTÃO COM CLASS NAME (ID INDISPONIVEL)')

    verde('proposonal_code: ')
    print(proposonal_code)
    # Conta atual
    current_counts_weg = driver.find_elements(By.CSS_SELECTOR, '#app > div.d-flex.justify-content-around.row > div:nth-child(1) > div:nth-child(3) > table > tbody > tr:nth-child(1) > td:nth-child(2)')[0].text
    current_counts_deye = driver.find_elements(By.CSS_SELECTOR, '#app > div.d-flex.justify-content-around.row > div:nth-child(2) > div:nth-child(3) > table > tbody > tr:nth-child(1) > td:nth-child(2)')[0].text
    verde('\nConta Atual: ')

    if not value_is_valid(current_counts_weg):
        message_list.append('Conta atual WEG')
    if not value_is_valid(current_counts_deye):
        message_list.append('Conta atual DEYE')
    

    # Conta com sistema
    counts_with_system_weg = driver.find_elements(By.CSS_SELECTOR, '#app > div.d-flex.justify-content-around.row > div:nth-child(1) > div:nth-child(3) > table > tbody > tr:nth-child(2) > td:nth-child(2)')
    counts_with_system_deye = driver.find_elements(By.CSS_SELECTOR, '#app > div.d-flex.justify-content-around.row > div:nth-child(2) > div:nth-child(3) > table > tbody > tr:nth-child(2) > td:nth-child(2)')
    verde('\nConta com Sistema: ')
    if not value_is_valid(counts_with_system_weg[0].text):
        message_list.append('Conta com sistema WEG')
    if not value_is_valid(counts_with_system_deye[0].text):
        message_list.append('Conta com sistemal DEYE')

    # economia 1 ano
    one_year_savings_weg = driver.find_elements(By.CSS_SELECTOR, '#app > div.d-flex.justify-content-around.row > div:nth-child(1) > div:nth-child(3) > table > tbody > tr:nth-child(3) > td:nth-child(2)')
    one_year_savings_deye = driver.find_elements(By.CSS_SELECTOR, '#app > div.d-flex.justify-content-around.row > div:nth-child(2) > div:nth-child(3) > table > tbody > tr:nth-child(3) > td:nth-child(2)')
    verde('\nEconomia (1 ano): ')
    if not value_is_valid(one_year_savings_weg[0].text):
        message_list.append('economia 1 ano WEG')
    if not value_is_valid(one_year_savings_deye[0].text):
        message_list.append('economia 1 ano DEYE')

    # economia 25 anos
    twenty_five_year_savings_weg = driver.find_elements(By.CSS_SELECTOR, '#app > div.d-flex.justify-content-around.row > div:nth-child(1) > div:nth-child(3) > table > tbody > tr:nth-child(4) > td:nth-child(2)')
    twenty_five_year_savings_deye = driver.find_elements(By.CSS_SELECTOR, '#app > div.d-flex.justify-content-around.row > div:nth-child(2) > div:nth-child(3) > table > tbody > tr:nth-child(4) > td:nth-child(2)')
    verde('\nEconomia (25 anos): ')
    if not value_is_valid(twenty_five_year_savings_weg[0].text):
        message_list.append('economia 25 anos WEG')
    if not value_is_valid(twenty_five_year_savings_deye[0].text):
        message_list.append('economia 25 anos DEYE')

    # Retorno no mês
    return_month_weg = driver.find_elements(By.CSS_SELECTOR, '#app > div.d-flex.justify-content-around.row > div:nth-child(1) > div:nth-child(3) > table > tbody > tr:nth-child(5) > td:nth-child(2)')
    return_month_deye = driver.find_elements(By.CSS_SELECTOR, '#app > div.d-flex.justify-content-around.row > div:nth-child(2) > div:nth-child(3) > table > tbody > tr:nth-child(5) > td:nth-child(2)')
    return_month = driver.find_elements(By.CLASS_NAME, 'form-retornomes')
    verde('\nRetorno (anos - mês) ')
    if not value_is_valid(return_month_weg[0].text):
        message_list.append('Retorno no mês WEG')
    if not value_is_valid(return_month_deye[0].text):
        message_list.append('Retorno no mês DEYE')

    # Disjuntor requerido
    input_disjuntor_weg = driver.find_elements(By.CSS_SELECTOR, '#app > div.d-flex.justify-content-around.row > div:nth-child(1) > div:nth-child(4) > div:nth-child(1) > input')
    input_disjuntor_deye = driver.find_elements(By.CSS_SELECTOR, '#app > div.d-flex.justify-content-around.row > div:nth-child(2) > div:nth-child(4) > div:nth-child(1) > input')
    verde('\n Disjuntor Requerido: ')
    if not value_is_valid(input_disjuntor_weg[0].get_attribute('value')):
        message_list.append('Disjuntor requerido WEG')
    if not value_is_valid(input_disjuntor_deye[0].get_attribute('value')):
        message_list.append('Disjuntor requerido DEYE')

    # Valor base
    input_valor_tabela_weg = driver.find_elements(By.CSS_SELECTOR, '#app > div.d-flex.justify-content-around.row > div:nth-child(1) > div:nth-child(4) > div:nth-child(2) > input')
    input_valor_tabela_deye = driver.find_elements(By.CSS_SELECTOR, '#app > div.d-flex.justify-content-around.row > div:nth-child(2) > div:nth-child(4) > div:nth-child(2) > input')
    verde('\nValor de Tabela: ')
    if not value_is_valid(input_valor_tabela_weg[0].get_attribute('value')):
        message_list.append('Valor tabela WEG')
    if not value_is_valid(input_valor_tabela_deye[0].get_attribute('value')):
        message_list.append('Valor tabela DEYE')

    # # Fator proposta
    # input_fator_proposta = driver.find_elements(By.CLASS_NAME, 'form-valorTabela')
    # verde('\nFator de Proposta: ')
    # if not value_is_valid(input_fator_proposta[0].get_attribute('value')):
    #     message_list.append('Fator proposta WEG')
    # if not value_is_valid(input_fator_proposta[1].get_attribute('value')):
    #     message_list.append('Fator proposta DEYE')

    # Desconto (%)
    input_desconto_weg = driver.find_elements(By.CSS_SELECTOR, '#app > div.d-flex.justify-content-around.row > div:nth-child(1) > div:nth-child(4) > div:nth-child(5) > input')
    input_desconto_deye = driver.find_elements(By.CSS_SELECTOR, '#app > div.d-flex.justify-content-around.row > div:nth-child(2) > div:nth-child(4) > div:nth-child(5) > input')
    verde('\n Desconto (%):')
    if not value_is_valid(input_desconto_weg[0].get_attribute('value')):
        message_list.append('Desconto (%) WEG')
    if not value_is_valid(input_desconto_deye[0].get_attribute('value')):
        message_list.append('Desconto (%) DEYE')

    # # Desconto real
    # input_desconto_real = driver.find_elements(By.CLASS_NAME, 'form-descontoReal')
    # verde('\n Desconto (R$): ')
    # if not value_is_valid(input_desconto_real[0].get_attribute('value')):
    #     message_list.append('Desconto real WEG')
    # if not value_is_valid(input_desconto_real[1].get_attribute('value')):
    #     message_list.append('Desconto real DEYE')

    # # Ajuste
    # input_ajuste = driver.find_elements(By.CLASS_NAME, 'form-ajuste')
    # verde('\n input_ajuste: ')
    # if not value_is_valid(input_ajuste[0].get_attribute('value')):
    #     message_list.append('Ajuste WEG')
    # if not value_is_valid(input_ajuste[1].get_attribute('value')):
    #     message_list.append('Ajuste DEYE')

    # # Comissão
    # input_comissao = driver.find_elements(By.CLASS_NAME, 'form-comissao')
    # verde('\n Comissão Franqueado: ')
    # if not value_is_valid(input_comissao[0].get_attribute('value')):
    #     message_list.append('Comissão WEG')
    # if not value_is_valid(input_comissao[1].get_attribute('value')):
    #     message_list.append('Comissão DEYE')

    # Valor proposta
    input_valor_proposta_weg = driver.find_elements(By.CSS_SELECTOR, '#app > div.d-flex.justify-content-around.row > div:nth-child(1) > div:nth-child(4) > div:nth-child(12) > input')
    input_valor_proposta_deye = driver.find_elements(By.CSS_SELECTOR, '#app > div.d-flex.justify-content-around.row > div:nth-child(2) > div:nth-child(4) > div:nth-child(12) > input')
    verde('\n Valor da Proposta: ')
    if not value_is_valid(input_valor_proposta_weg[0].get_attribute('value')):
        message_list.append('Valor proposta WEG')
    if not value_is_valid(input_valor_proposta_deye[0].get_attribute('value')):
        message_list.append('Valor proposta DEYE')

    # """
    # Equipamentos
    # """

    # # Potência dos modulos
    # potencia_modulos = driver.find_elements(By.CLASS_NAME, 'recebePotnciaModulos')
    # verde('\nPotencia dos Módulos: ')
    # if not value_is_valid(potencia_modulos[0].text):
    #     message_list.append('Potência dos modulos WEG')
    # if not value_is_valid(potencia_modulos[1].text):
    #     message_list.append('Potência dos modulos DEYE')
        
    # # form-PercentPotenciaModulos
    # percent_potencia_modulos = driver.find_elements(By.CLASS_NAME, 'form-PercentPotenciaModulos')
    # verde('\n percent_potencia_modulos: ')
    # if not value_is_valid(percent_potencia_modulos[0].text):
    #     message_list.append('(%) Potência dos modulos WEG')
    # if not value_is_valid(percent_potencia_modulos[1].text):
    #     message_list.append('(%) Potência dos modulos DEYE')

    # # Percentual potência dos inversores
    # potencia_inversores = driver.find_elements(By.CLASS_NAME, 'form-PotenciaInversor')
    # verde('\n Potência do Inversor: ')
    # if not value_is_valid(potencia_inversores[0].text):
    #     message_list.append('Potência dos inversoresWEG')
    # if not value_is_valid(potencia_inversores[2].text):
    #     message_list.append('Potência dos inversores DEYE')
        
    # # Percentual potência dos inversores
    # percent_potencia_inversores = driver.find_elements(By.CLASS_NAME, 'form-PotenciaInversor')
    # verde('\n potencia_inversores: ')
    # if not value_is_valid(percent_potencia_inversores[0].text):
    #     message_list.append('(%) Potência dos inversoresWEG')
    # if not value_is_valid(percent_potencia_inversores[2].text):
    #     message_list.append('(%) Potência dos inversores DEYE')

    # # Aplicação possível
    # aplicacao_possivel = driver.find_elements(By.CLASS_NAME, 'form-AmpliacaoPossivel')
    # verde('\n aplicacao_possivel: ')
    # if not value_is_valid(aplicacao_possivel[0].text):
    #     message_list.append('Aplicação possível WEG')
    # if not value_is_valid(aplicacao_possivel[1].text):
    #     message_list.append('Aplicação possível DEYE')

    # # Geração
    # geracao = driver.find_elements(By.CLASS_NAME, 'form-Geracao')
    # verde('\n Geracão: ')
    # if not value_is_valid(geracao[0].text):
    #     message_list.append('Geração WEG')
    # if not value_is_valid(geracao[1].text):
    #     message_list.append('Geração DEYE')

    # # Área necessária
    # area_necessaria = driver.find_elements(By.CLASS_NAME, 'form-AreaNecessaria')
    # verde('\n Área Necessária: ')
    # if not value_is_valid(area_necessaria[0].text):
    #     message_list.append('Área necessária WEG')
    # if not value_is_valid(area_necessaria[1].text):
    #     message_list.append('Área necessária DEYE')
        
    # """
    # Sistema Recomendado
    # QTDE | POT. | VALOR
    # """

    # # Módulo Fotovoltaico QTDE
    # quantity_equipment = driver.find_elements(By.CLASS_NAME, 'recebeqtdModulo')
    # verde('\n Quantidade de Módulos: ')
    # if not value_is_valid(quantity_equipment[0].text):
    #     message_list.append('Área necessária WEG')
    # if not value_is_valid(quantity_equipment[2].text):
    #     message_list.append('Área necessária DEYE')
    
    # # Módulo Fotovoltaico POT
    # pot_equipment = driver.find_elements(By.CLASS_NAME, 'form-potenciaModulo')
    # verde('\nPotência do Inversor ')
    # if not value_is_valid(pot_equipment[0].text):
    #     message_list.append('Área necessária WEG')
    # if not value_is_valid(pot_equipment[2].text):
    #     message_list.append('Área necessária DEYE')
    
    # # Módulo Fotovoltaico VALOR
    # equipment = driver.find_elements(By.CLASS_NAME, 'form-ValorModulo')
    # verde('\nValor dos Módulos: ')
    # if not value_is_valid(equipment[0].text):
    #     message_list.append('Área necessária WEG')
    # if not value_is_valid(equipment[2].text):
    #     message_list.append('Área necessária DEYE')
        
    # # Inversor
    # quantity_inverters = driver.find_elements(By.CLASS_NAME, 'form-QtdInversor')
    # verde('\nQuantidade de Inversores:')
    # if not value_is_valid(quantity_inverters[0].text):
    #     message_list.append('QTDE Inversor WEG')
    # if not value_is_valid(quantity_inverters[1].text):
    #     message_list.append('QTDE Inversor DEYE')
        
    # # Inversor
    # pot_inverters = driver.find_elements(By.CLASS_NAME, 'form-PotenciaInversor')
    # verde('\n POT inverters: ')
    # if not value_is_valid(pot_inverters[0].text):
    #     message_list.append('POT Inversor WEG')
    # if not value_is_valid(pot_inverters[1].text):
    #     message_list.append('POT Inversor DEYE')
        
    # # Inversor
    # inverters = driver.find_elements(By.CLASS_NAME, 'form-ValorInversor')
    # print('\nValor do inversor: ')
    # if not value_is_valid(inverters[0].text):
    #     message_list.append('Inversor WEG')
    # if not value_is_valid(inverters[1].text):
    #     message_list.append('Inversor DEYE')
        
    # # QTDE Protetor surto CA
    # quantity_ca_surge_protector = driver.find_elements(By.CLASS_NAME, 'form-RecebeQtdeProtetorAntiSurto')
    # print('\nQuantidade Protetor de Surto: ')
    # if not value_is_valid(quantity_ca_surge_protector[0].text):
    #     message_list.append('QTDE Protetor surto CA WEG')
    # if not value_is_valid(quantity_ca_surge_protector[1].text):
    #     message_list.append('QTDE Protetor surto CA DEYE')
        
    # # Protetor surto CA
    # ca_surge_protector = driver.find_elements(By.CLASS_NAME, 'form-ValorTotalProtetorAntiSurto')
    # verde('Valor Protetor de Surto: ')
    # if not value_is_valid(ca_surge_protector[0].text):
    #     message_list.append('Protetor surto CA WEG')
    # if not value_is_valid(ca_surge_protector[1].text):
    #     message_list.append('Protetor surto CA DEYE')
        
    # # QTDE Conector
    # quantity_connectors = driver.find_elements(By.CLASS_NAME, 'form-QtdeConector')
    # verde('\nQuantidade de Conectores: ')
    # if not value_is_valid(quantity_connectors[0].text):
    #     message_list.append('QTDE Conector WEG')
    # if not value_is_valid(quantity_connectors[1].text):
    #     message_list.append('QTDE Conector DEYE')
        
    # # Conector
    # connectors = driver.find_elements(By.CLASS_NAME, 'form-AreaNecessaria')
    # verde('\n Area Necessaria: ')
    # if not value_is_valid(connectors[0].text):
    #     message_list.append('Conector WEG')
    # if not value_is_valid(connectors[1].text):
    #     message_list.append('Conector DEYE')
        
    # # QTDE Cabos CC [preto]
    # quantity_black_cc_cables = driver.find_elements(By.CLASS_NAME, 'form-QtdeCaboCCPreto')
    # verde('Valor de Cabos CC Preto: ')
    # if not value_is_valid(quantity_black_cc_cables[0].text):
    #     message_list.append('QTDE Cabos CC [preto] WEG')
    # if not value_is_valid(quantity_black_cc_cables[1].text):
    #     message_list.append('QTDE Cabos CC [preto] DEYE')
        
    # # Cabos CC [preto]
    # black_cc_cables = driver.find_elements(By.CLASS_NAME, 'form-ValorTotalCaboCCPreto')
    # verde('\nQuantidade de CC Preto (m): ')
    # if not value_is_valid(black_cc_cables[0].text):
    #     message_list.append('Cabos CC [preto] WEG')
    # if not value_is_valid(black_cc_cables[1].text):
    #     message_list.append('Cabos CC [preto] DEYE')
        
    # # QTDE Cabos CC [vermelho]
    # quantity_red_cc_cables = driver.find_elements(By.CLASS_NAME, 'form-QtdeCaboCC')
    # verde('\nValor dos cabos CC Vermelho: ')
    # if not value_is_valid(quantity_red_cc_cables[0].text):
    #     message_list.append('QTDE Cabos CC [vermelho] WEG')
    # if not value_is_valid(quantity_red_cc_cables[1].text):
    #     message_list.append('QTDE Cabos CC [vermelho] DEYE')
        
    # # Cabos CC [vermelho]
    # red_cc_cables = driver.find_elements(By.CLASS_NAME, 'form-ValorTotalCaboCCVermelho')
    # verde('\nQuantidade dos cabos CC Vermelho: ')
    # if not value_is_valid(red_cc_cables[0].text):
    #     message_list.append('Cabos CC [vermelho] WEG')
    # if not value_is_valid(red_cc_cables[1].text):
    #     message_list.append('Cabos CC [vermelho] DEYE')
        
    # # Frete
    # quantity_freight = driver.find_elements(By.CLASS_NAME, 'form-FretePercent')
    # verde('\n Frete (%): ')
    # if not value_is_valid(quantity_freight[0].text):
    #     message_list.append('(%) Frete WEG')
    # if not value_is_valid(quantity_freight[1].text):
    #     message_list.append('(%) Frete DEYE')
        
    # # Frete
    # freight = driver.find_elements(By.CLASS_NAME, 'form-FreteValor')
    # verde('\n Valor do Frete (R$): ')
    # if not value_is_valid(freight[0].text):
    #     message_list.append('Frete WEG')
    # if not value_is_valid(freight[1].text):
    #     message_list.append('Frete DEYE')
        
    # # QTDE Descarga
    # quantity_discharges = driver.find_elements(By.CLASS_NAME, 'form-qtdMo')
    # verde('\n Quantidade de Descargas: ')
    # if not value_is_valid(quantity_discharges[0].text):
    #     message_list.append('QTDE Descarga WEG')
    # if not value_is_valid(quantity_discharges[1].text):
    #     message_list.append('QTDE Descarga DEYE')
        
    # # Descarga
    # discharges = driver.find_elements(By.CLASS_NAME, 'form-ValorDescarga')
    # verde('\nValor Descarga de Placas: ')
    # if not value_is_valid(discharges[0].text):
    #     message_list.append('Descarga WEG')
    # if not value_is_valid(discharges[1].text):
    #     message_list.append('Descarga DEYE')
        
    # # QTDE Instalação
    # quantity_installations = driver.find_elements(By.CLASS_NAME, 'form-QtdeInstalacao')
    # verde('\n Instalação do Sistema (%): ')
    # if not value_is_valid(quantity_installations[0].text):
    #     message_list.append('QTDE Instalação WEG')
    # if not value_is_valid(quantity_installations[1].text):
    #     message_list.append('QTDE Instalação DEYE')
        
    # # Instalação
    # installations = driver.find_elements(By.CLASS_NAME, 'form-ValorFinalInstalacao')
    # verde('\nValor da Instalação: ')
    # if not value_is_valid(installations[0].text):
    #     message_list.append('Instalação WEG')
    # if not value_is_valid(installations[1].text):
    #     message_list.append('Instalação DEYE')
        
    # # CA
    # ca = driver.find_elements(By.CLASS_NAME, 'form-ValorFinalCA')
    # verde('\n Acessórios de instalação CA: ')
    # if not value_is_valid(ca[0].text):
    #     message_list.append('CA WEG')
    # if not value_is_valid(ca[1].text):
    #     message_list.append('CA DEYE')
        
    # # CA
    # quantity_ca = driver.find_elements(By.CLASS_NAME, 'form-QtdeCA')
    # verde('\n Acessórios de Instalação CA (%) ')
    # if not value_is_valid(quantity_ca[0].text):
    #     message_list.append('QTDE CA WEG')
    # if not value_is_valid(quantity_ca[1].text):
    #     message_list.append('QTDE CA DEYE')
    
    # vermelho('message_list: ')
    # print( message_list)
    try:
        proposta_weg = {
            'valor_da_proposta' : input_valor_proposta_weg[0].get_attribute('value'),
            'conta_atual': current_counts_weg,
            'conta_com_sistema': counts_with_system_weg[0].text,
            'economia_1_ano': one_year_savings_weg[0].text,
            'economia_25_anos': twenty_five_year_savings_weg[0].text,
            # 'comissao_franqueado': input_comissao[0].get_attribute('value')
        }
        proposta_deye = {
            'valor_da_proposta' : input_valor_proposta_deye[0].get_attribute('value'),
            'conta_atual': current_counts_deye,
            'conta_com_sistema': counts_with_system_deye[0].text,
            'economia_1_ano': one_year_savings_deye[0].text,
            'economia_25_anos': twenty_five_year_savings_deye[0].text,
            # 'comissao_franqueado': input_comissao[1].get_attribute('value')
        }    
    except Exception as e: vermelho(f'Erro ao declarar propostas: {e}')
    vermelho('Fim da execução do verify_proposonal')
    return {
        'message-list': message_list,
        'proposonal-code': proposonal_code,
        'proposonal-url': proposonal_url,
        'proposta_weg': proposta_weg, 
        'proposta_deye': proposta_deye
    }
