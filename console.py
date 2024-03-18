from web_driver import WebDriver
import logging
from time import sleep
from datetime import datetime

from web_driver import WebDriver

logging.basicConfig(filename='logfile.txt', level=logging.ERROR,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt="%Y-%m-%d %H:%M:%S")

def validate(environment) -> None:
        # Iniciar drive
        driver = WebDriver(environment)
        
        # Login
        if driver.login_site():
            print('Login realizado com sucesso')
        else:
            print('Erro ao realizar login')
            return
        sleep(2)

        """
        Criar proposta de para um cliente existente
        """
        print('Criando nova proposta de um cliente já existente')
        data = driver.get_customer()
        
        if not data['status']:
            print('Erro ao criar uma proposta com cliente existente')
        else:
            response = driver.handle_verify_proposonal()
            print(f'👤Cliente selecionado: {data["nome"]}')
            print(f'🎟️Código da proposta: {response["proposonal-code"]}')
            print(f'🔗Link da proposta: {response["proposonal-url"]}')
            message = 'Campos não válidos: \n'
            message += '\n'.join(response['message-list'])
            print(message)
        
        """
        Criar proposta para um cliente fictício
        """
        print('Criando um novo cliente e uma proposta')
        data = driver.create_cliente()
        
        if not data['status']:
            print('Erro ao criar uma nova proposta')
        else:
            response = driver.handle_verify_proposonal()
            print(f'👤 Nome do novo cliente: {data["nome"]}, CPF: {data["cpf"]}')
            print(f'🎟️ Código da proposta: {response["proposonal-code"]}')
            print(f'🔗 Link da proposta: {response["proposonal-url"]}')
            message = 'Campos não válidos: \n'
            message += '\n'.join(response['message-list'])
            print(message)
        
        print('Processo finalizado!')
        
        driver.driver.close()
        driver.driver.quit()
        
        return

def menu():
    while True:
        print("Escolha um ambiente de desenvolvimento:")
        print("1 - LAB")
        print("2 - DEV")
        print("0 - Sair")
        
        try:
            match input("Escolha uma opção: "):
                case "1":
                    # Executar a opção 1
                    validate('lab')
                case "2":
                    # Executar a opção 2
                    validate('dev')
                case "0":
                    # Sair do menu
                    print("Saindo do menu...")
                    break
                case _:
                    # Opção inválida
                    print("Opção inválida, tente novamente.")
        except KeyboardInterrupt:
            # Usuário pressionou ctrl + c
            print("Operação interrompida pelo usuário. Voltando ao menu.")
            
    # Menu encerrado
    print("Menu encerrado.")
    
if __name__=='__main__':
    menu()