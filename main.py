from web_driver import WebDriver
import logging
import asyncio
from time import sleep
from datetime import datetime
import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters, CallbackContext

from web_driver import WebDriver


# logging.basicConfig(filename='logfile.txt', level=logging.ERROR,
#                     format='%(asctime)s %(levelname)s: %(message)s',
#                     datefmt="%Y-%m-%d %H:%M:%S")
from warnings import filterwarnings
from telegram.warnings import PTBUserWarning
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

class kintBot:
    # TOKEN = '6542439813:AAEal1i78lytSOWeozuuQcNdPQ52gFBZC3w' #  @kinlogbot
    TOKEN = '5948987229:AAGp_D70hJsDYR3_3zSHlZmLMxR20eLTh88'
    STEP = range(1)
    driver = None
    running = False
    task = None
    AMBIENTE = range(1)
    FINALIZAR_PROPOSTA = 1
    RECEIVE_IMAGE = 3
    IMAGEM = 1
    async def start(self, update: Update, context) -> None:
        user = update.message.from_user
        await update.message.reply_text(f'Olá {user.first_name} {user.last_name} 👋, bom te ver!')
        await update.message.reply_text('Informe o ambiente (LAB ou DEV)\nutilize /cancel para abortar a operação.')
        return self.STEP

    async def validate(self, update: Update) -> None:
        environment = update.message.text.lower()
        
        if not environment in ('lab', 'dev'):
            await update.message.reply_text('Ambiente desconhecido!\nTente novamente, por favor.')
            return
        
        await update.message.reply_text('Ok! Vamos lá...')
        
        # Iniciar drive
        self.driver = WebDriver(environment)
        
        # Login
        if self.driver.login_site():
            await update.message.reply_text('✔️Login realizado com sucesso')
        else:
            pass
        sleep(2)
        
        """
        Criar proposta para um cliente fictício
        """
        await update.message.reply_text('Criando um novo cliente e uma proposta')
        data = self.driver.create_cliente()
        await update.message.reply_text('Novo cliente e nova proposta criada!')
        ### verificado###
        print(f'\033[36m  data = {data} \033[0m')

        await update.message.reply_text('Processo finalizado!')
        self.driver.driver.close()
        self.driver.driver.quit()
        
        return ConversationHandler.END

    async def validate_command(self, update: Update, context) -> None:
        """Inicia o teste em uma nova tarefa assíncrona"""
        if self.running:
            await update.message.reply_text('O teste já está em andamento.')
            return

        self.running = True
        self.task = asyncio.create_task(self.validate(update))
        
        return

    async def stop_command(self, update, context) -> None:
        """Interrompe o teste"""
        if not self.running:
            await update.message.reply_text('O teste não está em andamento.')
            return
        
        # Cancela a tarefa do teste
        try: 
            self.driver.driver.close()
            self.driver.driver.quit()
        except:
            ...
        self.running = False
        self.task.cancel()
        print('>>> [INFO]: teste finalizado.')
        await update.message.reply_text('teste interrompido.')

    async def cancel_validate(self, update: Update, context) -> int:
        await update.message.reply_text('Validação cancelada.')
        return ConversationHandler.END
    
    async def cancel_get_option(self, update: Update, context: CallbackContext):
        await update.message.reply_text('✖️ Operação cancelada! ✖️')
        return ConversationHandler.END #encerra chat
    
    ############# criar botões ##### EXIBIÇÃO NOVA
    async def get_option_ambiente(self, update: Update, context: CallbackContext):
        keyboard = [
            [InlineKeyboardButton("👨‍💻 localhost", callback_data='lab')],
            # [InlineKeyboardButton("👨‍💻 DEV", callback_data='dev')],
            [InlineKeyboardButton("✖️ CANCELAR", callback_data='cancelar')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("⚙️ Iniciar Execução do Bot QA..\n\nSelecione o Ambiente em que deseja executar...", reply_markup=reply_markup)

        return self.AMBIENTE
    
    # Executar o cadastro de cliente e nova proposta OKKK
    async def button_callback_ambiente(self, update: Update, context: CallbackContext):
        query = update.callback_query ## pega a função de leitura dos botões
        user_choice = query.data  ## pega qual botão foi apertado
        update = query ## chama o update para enviar mensagem (gambiarra)
        
        if user_choice == 'cancelar':                 
                await query.message.reply_text('✖️ Operação Cancelada! ✖️')
                return ConversationHandler.END #encerra chat
        
        elif user_choice == 'lab' or user_choice == 'dev':
            print(f'Iniciar execução em {user_choice}')
           
            environment = user_choice
                    
                    
            
            
            await update.message.reply_text('Ok! Vamos lá...')
            
            # Iniciar drive
            self.driver = WebDriver(environment)
            logar_site = self.driver.login_site()
            print(logar_site)
            """
            Criar proposta para um cliente fictício
            """
            await update.message.reply_text('📝')
            await update.message.reply_text('📝 Criando um novo cliente e uma proposta')
            data = self.driver.create_cliente()
            await update.message.reply_text('✔️ Novo cliente cadastrado e nova proposta elaborada com sucesso!')
            ### verificado###
            print(f'\033[36m  data = {data} \033[0m')
            if not data['status']:
                await update.message.reply_text('Erro ao criar uma nova proposta')
            else:
                try:
                    response = self.driver.handle_verify_proposonal()
                    # print(f'response: {response}')
                except Exception as e: print(e)
                await update.message.reply_text(f"👤 Nome do novo cliente: {data['nome']}\n🪪  CPF: {data['cpf']}\n🎟️ Código da proposta: {response['proposonal-code']}\n🔗 Link da proposta: {response['proposonal-url']}")

            self.codigo_da_proposta = response['proposonal-code']
            await update.message.reply_text('Processo finalizado!  ✔️')
            await update.message.reply_text('✅')

            dados_weg = response['proposta_weg']
            dados_deye = response['proposta_deye']
            
            weg_valor_da_proposta = dados_weg['valor_da_proposta']
            weg_conta_atual = dados_weg['conta_atual']
            weg_conta_com_sistema = dados_weg['conta_com_sistema']
            weg_1_ano = dados_weg['economia_1_ano']
            weg_25_anos = dados_weg['economia_25_anos']
            # comissao_franqueado = dados_weg['comissao_franqueado']

            proposta_weg = (
                        f'📄     PROPOSTA WEG\n\n'
                        f'💰   Valor da Proposta: {weg_valor_da_proposta}\n'
                        f'🧾   Conta Atual: {weg_conta_atual}\n'
                        f'🌞   Conta com Sistema: {weg_conta_com_sistema} \n'
                        f'⌛   Economia em 1 ano: {weg_1_ano}\n'
                        f'⌛   Economia em 25 anos: {weg_25_anos}\n'
                        # f'🤑   Comissão do Franqueado: {comissao_franqueado}\n'

            )

            print(proposta_weg)
            await update.message.reply_text(proposta_weg)
            deye_valor_da_proposta = dados_deye['valor_da_proposta']
            deye_conta_atual = dados_deye['conta_atual']
            deye_conta_com_sistema = dados_deye['conta_com_sistema']
            deye_1_ano = dados_deye['economia_1_ano']
            deye_25_anos = dados_deye['economia_25_anos']
            # comissao_franqueado = dados_deye['comissao_franqueado']

            proposta_deye = (
                        f'📄     PROPOSTA DEYE\n\n'
                        f'💰   Valor da Proposta: {deye_valor_da_proposta}\n'
                        f'🧾   Conta Atual: {deye_conta_atual}\n'
                        f'🌞   Conta com Sistema: {deye_conta_com_sistema} \n'
                        f'⌛   Economia em 1 ano: {deye_1_ano}\n'
                        f'⌛   Economia em 25 anos: {deye_25_anos}\n'
                        # f'🤑   Comissão do Franqueado: {comissao_franqueado}\n'

            )            
            print(proposta_deye)
            await update.message.reply_text(proposta_deye)

    
        


            await self.get_option_finalizar_proposta(update, context)

        elif user_choice == 'aprovar_proposta_weg':
            await update.message.reply_text('✅  BOTÃO APROVAR PROPOSTA WEG SELECIONADO')
            self.aprovado_weg = 'Ok'
            self.aprovado_deye= 'Not'
            self.driver.aprove('weg')
            await self.get_option_finalizar_proposta(update, context)

        elif user_choice == 'aprovar_proposta_deye':
            await update.message.reply_text('✅  BOTÃO APROVAR PROPOSTA DEYE SELECIONADO')
            self.aprovado_deye = 'Ok'
            self.aprovado_weg = 'Not'
            self.driver.aprove('deye')


            await self.get_option_finalizar_proposta(update, context)
               
        elif user_choice == 'imprimir_pdf':
            await query.message.reply_text('🖨️ Botão Imprimir PDF selecionado')
            await self.get_option_finalizar_proposta(update, context)
       
        elif user_choice == 'contrato_express':
            if self.aprovado_weg != 'Ok' and self.aprovado_deye != 'Ok':
                await query.message.reply_text('⚠️  Proposta ainda não está aprovada. \nAprove a proposta e tente gerar o contrato novamente... ')
                await self.get_option_finalizar_proposta(update, context)
            else:
                await query.message.reply_text('📃 Gerar Contrato Express')

                if self.aprovado_deye == 'Ok':
                    aprove = 'deye'
                elif self.aprovado_weg == 'Ok':
                    aprove = 'weg'

                self.driver.gerar_contrato(aprove)
                await self.get_option_finalizar_proposta(update, context)

        elif user_choice == 'fim_contrato':
            await query.message.reply_text('🔚')
            self.driver.driver.close()
            self.driver.driver.quit()
            return ConversationHandler.END    


    """ criar nova conversação para parte de finalização """
    # Aprovar proposta, Gerar Contrato (Finalizar), Gerar Contrato Expresss
      ############# criar botões ##### EXIBIÇÃO NOVA
    async def get_option_finalizar_proposta(self,update: Update, context: CallbackContext):
        # return ConversationHandler.END
        
        keyboard = [
            [InlineKeyboardButton("✅    APROVAR WEG", callback_data='aprovar_proposta_weg')],
            [InlineKeyboardButton("✅    APROVAR DEYE", callback_data='aprovar_proposta_deye')],
            # [InlineKeyboardButton("🖨️ IMPRIMIR PDF", callback_data='imprimir_pdf')],
            [InlineKeyboardButton("📃   CONTRATO", callback_data='contrato_express')],
            [InlineKeyboardButton("🌐  FINALIZAR", callback_data='fim_contrato')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            codigo = self.codigo_da_proposta
            await update.message.reply_text(f'🎟️ Código da proposta: {codigo}', reply_markup=reply_markup)
        except:pass


        
    async def button_finalizar_proposta(self, update: Update, context: CallbackContext):
        print('Chegou aqui')
        query = update.callback_query ## pega a função de leitura dos botões
        user_choice = query.data  ## pega qual botão foi apertado
        update = query ## chama o update para enviar mensagem (gambiarra)

        await update.message.reply_text(f'FINALIZAR PROPOSTA {user_choice}')
    

    # _______________________________________________________________________
    """         TESSERACT        """


    async def get_image(self, update: Update, context: CallbackContext):
        user = update.message.from_user
        await update.message.reply_text("🪪📸   Envie uma BOA foto da frente da CNH:\n\n💡 A foto deve conter todo o documento e não cortar as bordas.\n💡 Se o documento tiver um plástico de proteção, o melhor é retirá-lo para evitar possíveis reflexos. ")
        return self.RECEIVE_IMAGE
    
    def chamar_api (self,url):
        import requests
        import json

        # URL da API Flask 
        api_url = 'http://127.0.0.1:5000/ocr' # PEGAR DA API CRIADA
        url_verificada = url
        data = {
            "url": url_verificada,
            "tipo": 'cnh'
        }

        # Enviar os dados para a API
        response = requests.post(api_url, json=data)

        #verifica se a solicitação foi bem-sucedida
        if response.status_code == 200:
            response_data = response.json()
            print(f'\x1b[32m COMUNICAÇÃO VIA API REALIZADA COM SUCESSO\x1b[0m')
            nome = response_data['nome']
            cpf = response_data['cpf']
            nasc = response_data['nasc']
            print(f'\x1b[32m Nome: \x1b[36m {nome}')
            print(f'\x1b[32m CPF: \x1b[36m {cpf}')
            print(f'\x1b[32m Data de Nascimento: \x1b[36m {nasc}\x1b[0m')
            return response_data

        else:
            print(f'Erro ao chamar a API: {response.status_code} - {response.text}')
            return 
    
    async def receive_image(self, update: Update, context: CallbackContext):
        try:
            user = update.message.from_user
            photo = update.message.photo[-1]  # Obtain the last photo sent (there might be several)

            # Get the file ID
            file_id = photo.file_id

            
            # Use context.bot to download the file
            bot = context.bot

            file = await bot.get_file(file_id)

            print(file)  ## verificar se é aqui que tem os dados da imagem recebida


            ## extrair o caminho e tentar fazer download por request da imagem
            caminho = file.file_path

            await update.message.reply_text(f"Imagem recebida com sucesso. Chamando API Tesseract\n{caminho}")

            try:
                response = self.chamar_api(caminho)

                nome = response['nome']
                cpf = response['cpf']
                nasc = response['nasc']
                doc = response['doc']
                # if nome != None and cpf != None and nasc != None and doc != None:
                    # texto_retorno_bot = (f"EXTRAÇÃO REALIZADA COM SUCESSO ✅\n\nNome: {nome}\nRG: {doc} \nCPF: {cpf}\nData de Nascimento: {nasc}"  )
                dados_faltando = []

                if nome is None:
                    dados_faltando.append('Nome')
                if cpf is None:
                    dados_faltando.append('CPF')
                if nasc is None:
                    dados_faltando.append('Data de Nascimento')
                if doc is None:
                    dados_faltando.append('RG')

                if dados_faltando:
                    texto_retorno_bot = (f"⚠️       EXTRAÇÃO FALHOU -- FALTANDO DADOS:\n{', '.join(dados_faltando)}         ⚠️\n\nNome: {nome}\nRG: {doc}\nCPF: {cpf}\nData de Nascimento: {nasc}")
                    await update.message.reply_text(texto_retorno_bot)
                    await update.message.reply_text('📸 Vamos tentar novamente.. Envie uma nova foto do documento para tentarmos extrair os dados... ')
                    await update.message.reply_text("🪪📸   Envie uma BOA foto da frente da CNH:\n\n💡 A foto deve conter todo o documento e não cortar as bordas.\n💡 Se o documento tiver um plástico de proteção, o melhor é retirá-lo para evitar possíveis reflexos. ")

                    return self.RECEIVE_IMAGE
                    
                else:
                    texto_retorno_bot = (f"EXTRAÇÃO REALIZADA COM SUCESSO ✅\n\nNome: {nome}\nRG: {doc}\nCPF: {cpf}\nData de Nascimento: {nasc}")
                    await update.message.reply_text(texto_retorno_bot)
                    print('\x1b[34mFIM DA EXTRAÇÃO\x1b[0m')

                    return ConversationHandler.END
            except: 
                
                    await update.message.reply_text('⚠️     Erro ao se comunicar com a API, tente novamente /cnh')
                    return ConversationHandler.END
            

        except Exception as e:
            print(e)
    
    def start_kin(self):
        print('>>> Seja bem vindo.')
        print('>>> \033[92mBOT QA inicido.\033[0m')
        
        self.application = Application.builder().token(self.TOKEN).build()

        self.application.add_handler(CommandHandler('stop', self.stop_command))

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start_old', self.start)],
            states={
                self.STEP: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.validate_command)]
            },
            fallbacks=[CommandHandler('cancel', self.cancel_validate)]
        )

        conv_handler_start = ConversationHandler(
            entry_points=[CommandHandler('start', self.get_option_ambiente)],
            states={
                self.AMBIENTE: [CallbackQueryHandler(self.button_callback_ambiente)],  
                # self.FINALIZAR_PROPOSTA: [CallbackQueryHandler(self.button_finalizar_proposta)],
            },
            fallbacks=[CommandHandler('cancel', self.cancel_get_option)]
        )
        conv_handler_img = ConversationHandler(
            entry_points=[CommandHandler('cnh', self.get_image)],
            states={
               self.RECEIVE_IMAGE: [MessageHandler(filters.PHOTO, self.receive_image)], 
            },
            fallbacks=[CommandHandler('cancel', self.cancel_get_option)]
        )
        self.application.add_handler(conv_handler)
        self.application.add_handler(conv_handler_start)
        self.application.add_handler(conv_handler_img)

        self.application.run_polling()

if __name__ == '__main__':
    kinbot = kintBot()
    kinbot.start_kin()