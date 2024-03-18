from flask import Flask, request, jsonify
from telegram import Bot
from web_driver import WebDriver
import time
import requests
import os, re
from PIL import Image, ImageEnhance
import pytesseract
import cv2
import numpy as np

app = Flask(__name__)


@app.route('/ocr', methods=['POST'])
async def ocr():

    data = request.json

    #   Obtem os dados da URL e erro do JSON recebido
    url = data.get('url', 'URL não especificada')
    tipo = data.get('tipo', 'Erro não especificado')
    print(url, tipo)

    # Salvar Por request a url
    tesseract_folder = "tesseract"
    if not os.path.exists(tesseract_folder):
        os.makedirs(tesseract_folder)

    caminho_png = os.path.join(tesseract_folder, "imagem.png")
    response = requests.get(url)

    with open(caminho_png, "wb") as f:
        f.write(response.content)

    ## editar imagem para melhorar extração de textos
    # Carregue a imagem da CNH (substitua 'sua_imagem.png' pelo caminho correto)
    img = Image.open(caminho_png)



    def redimencionar_imagem(img):
             # Redimensione a imagem para uma resolução maior (opcional)
            largura, altura = img.size
            print(f'\x1b[32mNOVA IMAGEM RECEBIDA PELA API\n\nResolucação da imagem: {largura} x {altura}\x1b[0m')


            # Redimensione a imagem para a resolução desejada (1280x860)
            nova_largura = 1000
            nova_altura = 640
            img = img.resize((nova_largura, nova_altura), Image.ANTIALIAS)
            print(f'\x1b[36mREDIMENSIONANDO PARA PADRÃO\n\nResolucação da imagem: 1000 x 640\x1b[0m')
            return img
    
    def editar_imagem(img,option):
        caminho_png_editado = os.path.join(tesseract_folder, "imagem_edited.png")
        realce_maximo = ImageEnhance.Sharpness(img)
        contraste_maximo = ImageEnhance.Contrast(img)
        exposicao_maxima = ImageEnhance.Brightness(img)


        if option == 1 : 
            # Converta a imagem em escala de cinza
            img = img.convert('L')
            img = realce_maximo.enhance(3.0)

        if option == 2 : 
            # Converta a imagem em escala de cinza
            img = img.convert('L')
            img = realce_maximo.enhance(3.0)

        if option == 3:
            img = img.convert('L')
            img = realce_maximo.enhance(3.0)
            img = contraste_maximo.enhance(2.0)  # Ajuste o valor para o efeito desejado

        if option == 4:
            img = img.convert('L')
            img = realce_maximo.enhance(3.0)
            img = contraste_maximo.enhance(2.0)  # Ajuste o valor para o efeito desejado
            img = exposicao_maxima.enhance(1.0)  # ajustar conforme necessário
   
        img.save(caminho_png_editado)
        return img

    def extrair_texto(img):    

        def trocar_simbolos(texto_extraido):
            texto_extraido = texto_extraido.replace('(','')
            texto_extraido = texto_extraido.replace(')','')
            texto_extraido = texto_extraido.replace('[1','4')
            texto_extraido = texto_extraido.replace('[','')
            texto_extraido = texto_extraido.replace(']','')
            texto_extraido = texto_extraido.replace('. ','.')
            texto_extraido = texto_extraido.replace(' .','.')
            return texto_extraido
    
        texto_extraido = pytesseract.image_to_string(img,lang='por')

        texto_extraido = trocar_simbolos(texto_extraido)
        print(f'\x1b[35mTEXTO EXTRAÍDO DA IMAGEM INTEIRA\n\n{texto_extraido}\x1b[0m')
        return texto_extraido
    
    def encontrar_dados(texto_extraido, resposta):
        nome = resposta['nome']
        cpf = resposta['cpf']
        data_nasc = resposta['nasc']
        numero_rg = resposta['doc']
        print(f'\x1b[34mTENTATIVA -INIT>  {resposta}\x1b[0m')
        caminho_png_editado = os.path.join(tesseract_folder, "imagem_edited.png")
         # localizar CPF pelo padrão xxx.xxx.xxx-xx
        correspondencias_cpf = re.search(r'\d{3}.\d{3}.\d{3}-\d{2}', texto_extraido)
                          
        if correspondencias_cpf and cpf==None:
            cpf = correspondencias_cpf.group(0)
            print("\x1b[33m campo contém o padrão \x1b[34m' 'CPF'")

            print("CPF:", cpf)
       
        # se nome não foi encontrado, tentar extrair do texto completo
        if "NOME" in texto_extraido and nome==None:
                        print("\x1b[33m campo contém a palavra \x1b[34m'NOME'\x1b[0m")
                        linhas = texto_extraido.split('\n')
                        nome = None
                        
                        for i, linha in enumerate(linhas):
                            if "NOME" in linha or "Sobrenome" in linha:
                                if i < len(linhas) - 1:
                                    nome = linhas[i+1]  # Pega o texto da próxima linha
                                    print(f'nome = %{nome}%')
                                    if nome == "" or nome == "\n":
                                        nome = linhas[i+2]
                                    # Use uma expressão regular para remover números e símbolos
                                    nome = re.sub(r'[^A-Za-zÀ-ÖØ-öø-ÿ\s]', '', nome)
                                    nome = nome.replace('SOSE ', 'JOSE ')
                                    nome = nome.replace('FOSE ', 'JOSE ')

                                    print(f"Nome: %{nome}%")
                                    break  # Parar a busca após encontrar o nome
        

        elif "NASCIMENTO" in texto_extraido and data_nasc==None:
            if data_nasc == None:
                print(f"\x1b[36m campo contém a palavra \x1b[34m'DATA DE NASCIMENTO {data_nasc}'")

                linhas = texto_extraido.split('\n')

                # Procurar uma data no texto (assumindo que a data está no formato DD/MM/AAAA)
                for linha in linhas:
                    correspondencias_data = re.search(r'(\d{2}/\d{2}/\d{4})', linha)
                    correspondencias_data2 = re.search(r'(\d{2}/\d{2}/\d{3} d{1})', linha)
                    if correspondencias_data:
                        data_nasc = correspondencias_data.group(1)
                        print("Data de Nascimento:\x1b[0m", data_nasc)
                        break  
                    elif correspondencias_data2:
                        data_nasc = correspondencias_data.group(1)
                        data_nasc = data_nasc.replace(' ', '')
                        break
                
                print(f'\n\n DATA DE NASCIMENTO ENCONTRADA: {data_nasc}\n\n')

 
        elif " UF" in texto_extraido or 'DOC' in texto_extraido:
                        print("\x1b[33m campo contém a palavra \x1b[34m'DOC IDENTIDADE'\x1b[0m")

                        # Procurar por um padrão de dígitos seguido por um espaço e, em seguida, uma sequência de letras maiúsculas
                        linhas = texto_extraido.split('\n')

                        for i, linha in enumerate(linhas):
                            if 'DOC' in linha:
                                print(linha)
                                if i<len(linhas)-1:
                                    linha = linhas[i+1]
                                    print(f'LINHA +1 -> {linha}')

                                    numero_rg = linha
                        
                        
                        print("Número do RG:", numero_rg)

        # Verificar se o texto contém a palavra "DATA DE NASCIMENTO"

        resposta = {
             'nome': nome,
             'cpf': cpf, 
             "nasc": data_nasc, 
             "doc": numero_rg
        }

        return resposta

    def encontrar_por_contorno(caminho_png_editado, resposta):
            def trocar_simbolos(texto_extraido):
                texto_extraido = texto_extraido.replace('(','')
                texto_extraido = texto_extraido.replace(')','')
                texto_extraido = texto_extraido.replace('[1','4')
                texto_extraido = texto_extraido.replace('[','')
                texto_extraido = texto_extraido.replace(']','')
                texto_extraido = texto_extraido.replace('. ','.')
                texto_extraido = texto_extraido.replace(' .','.')
                return texto_extraido
            
            nome = resposta['nome']
            cpf = resposta['cpf']
            data_nasc = resposta['nasc']
            numero_rg = resposta['doc']
            # Usar expressão padrão para encontrar o campo "x"
            try:
                # Carregar a imagem da CNH
                imagem = cv2.imread(caminho_png_editado)

                # Pré-processar a imagem (converter para tons de cinza e aplicar filtro de borda)
                imagem_cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
                bordas = cv2.Canny(imagem, threshold1=25, threshold2=100)

                # Encontrar contornos na imagem
                contornos, _ = cv2.findContours(bordas, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # Critérios para identificar campos de interesse
                area_minima = 500  # Ajuste conforme necessário
                campos_interesse = []
                # Margem para ajustar a posição de corte (pode ser ajustada conforme necessário)
                margem_acima = 10

                for contorno in contornos:
                    area = cv2.contourArea(contorno)
                    x, y, w, h = cv2.boundingRect(contorno)
                    if area > area_minima:
                        campos_interesse.append((x-2, y - margem_acima, w, h+3))


                # Recortar os campos identificados e salvar dentro da pasta "tesseract"
                for i, (x, y, w, h) in enumerate(campos_interesse):
                    campo_recortado = imagem[max(0, y):y+h, x:x+w]  # Certifique-se de não ter valores negativos

                    # Verificar se o campo recortado não está vazio
                    if not campo_recortado.any():
                        continue

                    nome_arquivo_ocr = f'tesseract/campo_{i}.png'  # Salvar dentro da pasta "tesseract"
                    cv2.imwrite(nome_arquivo_ocr, campo_recortado)

                    try:
                        # campo_recortado = imagem[y:y+h, x:x+w]
                        nome_arquivo = f'campo_{i}.png'
                        
                        # verificar texto
                        caminho_png_campo = os.path.join(tesseract_folder, nome_arquivo)

                        img = Image.open(caminho_png_campo)

                        textO_campo = pytesseract.image_to_string(img,lang='por')
                        textO_campo = trocar_simbolos(textO_campo)

                        # print(f'\x1b[34mTEXTO EXTRAÍDO DO CAMPO {i}\n\n{textO_campo}\n_______________________________________________\n\x1b[0m')

                            
                        # print(f'\x1b[36m_____________
                        # ____________________________\x1b[32m\nCAMPO {i}    -   {textO_campo}\x1b[0m')

                        # verificar se o tem a palavra NOME no textO_campo
                        # Verificar se o texto contém a palavra "NOME"
                        if "EMISSOR" in textO_campo and uf_emissor == None:
                            print("\x1b[36m campo contém a palavra \x1b[34m'DOC IDENTIDADE'\x1b[0m")

                            # Procurar por um padrão de dígitos seguido por um espaço e, em seguida, uma sequência de letras maiúsculas
                            linhas = textO_campo.split('\n')

                            for i, linha in enumerate(linhas):
                                if 'DOC' in linha or 'EMISSOR' in  linha:
                                    if i<len(linhas)-1:
                                        linha = linhas[i+1]
                                        numero_rg = str(linha)
                            
                            
                            print("Número do RG:", linha)

                        if "NOME" in textO_campo and nome==None:
                            print("\x1b[36m campo contém a palavra \x1b[34m'NOME'\x1b[0m")
                            linhas = textO_campo.split('\n')
                            nome = None
                            
                            for i, linha in enumerate(linhas):
                                if "NOME" in linha or "Sobrenome" in linha:
                                    if i < len(linhas) - 1:
                                        nome = linhas[i+1]  # Pega o texto da próxima linha
                                        print(f'nome = %{nome}%')
                                        if nome == "" or nome == "\n":
                                            nome = linhas[i+2]
                                        # Use uma expressão regular para remover números e símbolos
                                        nome = re.sub(r'[^A-Za-zÀ-ÖØ-öø-ÿ\s]', '', nome)
                                        nome = nome.replace('SOSE ', 'JOSE ')
                                        nome = nome.replace('FOSE ', 'JOSE ')

                                        print("Nome:", nome)
                                        break  # Parar a busca após encontrar o nome
                        
                        # Verificar se o texto contém a palavra "DATA DE NASCIMENTO"
                        if "NASCIMENTO" in textO_campo and data_nasc==None :
                            print("\x1b[36m campo contém a palavra \x1b[34m'DATA DE NASCIMENTO'")
                            textO_campo.replace('[','')
                            textO_campo.replace(']','')
                            textO_campo.replace(')','')
                            textO_campo.replace('(','')
                            textO_campo.replace('|','')
                            linhas = textO_campo.split('\n')

                            # Procurar uma data no texto (assumindo que a data está no formato DD/MM/AAAA)
                            data_nasc = None
                            for linha in linhas:
                                correspondencias_data = re.search(r'(\d{2}/\d{2}/\d{4})', linha)
                                if correspondencias_data:
                                    data_nasc = correspondencias_data.group(1)
                                    print("Data de Nascimento:\x1b[0m", data_nasc)
                                    break  

                                # Verificar se o texto contém a palavra-chave "CPF" no texto do campo
                        
                        if "CPF" in textO_campo and cpf == None:
                            print("\x1b[36m campo contém a palavra \x1b[34m' 'CPF'")
                            linhas = textO_campo.split('\n')
                            
                            # Procurar um CPF no texto (assumindo que o CPF está no formato XXX.XXX.XXX-XX)
                            cpf = None
                            for linha in linhas:
                                correspondencias_cpf = re.search(r'(\d{3}.\d{3}.\d{3}-\d{2})', linha)
                                if correspondencias_cpf:
                                    cpf = correspondencias_cpf.group(1)
                                    print("CPF:\x1b[0m", cpf)
                                    break  # Parar a busca após encontrar o CPF


                    finally:

                        pass
                resposta = {
                    'nome': nome,
                    'cpf': cpf, 
                    "nasc": data_nasc, 
                    "doc": numero_rg
                }
                return resposta
                        
            except Exception as e: return jsonify({"message":e})


    nome = None
    cpf = None
    data_nasc = None
    numero_rg = None
    uf_emissor = None
    resposta = [nome, cpf, data_nasc, numero_rg, uf_emissor]

    img = redimencionar_imagem(img)

    img = editar_imagem(img, 1)

    texto_extraido = extrair_texto(img)

    print(f'\x1b[32m $$$$\n {texto_extraido}\n$$$$\n\x1b[0m')
    
    resposta = {
         'nome': nome, 
         'cpf': cpf, 
         'nasc': data_nasc, 
         'doc': numero_rg
    }
    data = encontrar_dados(texto_extraido, resposta)
    caminho_png_editado = os.path.join(tesseract_folder, "imagem_edited.png")
    data2 = encontrar_por_contorno(caminho_png_editado, data)
    

    if data2['nome'] == None or data2['cpf']==None or data2['nasc']==None or data2['doc']==None:
        print( 'TENTATIVA 2')

        print('procurar item faltante', data2)
        # tentativa 2
        img = editar_imagem(img, 2)
        texto_extraido = extrair_texto(img)
        resposta = data2
        data = encontrar_dados(texto_extraido, resposta)
        data2 = encontrar_por_contorno(caminho_png_editado, data)
        print(data2)

    if data2['nome'] == None or data2['cpf']==None or data2['nasc']==None or data2['doc']==None:
        print( 'TENTATIVA 3')

        print('procurar item faltante', data2)
        # tentativa 2
        img = editar_imagem(img, 3)
        texto_extraido = extrair_texto(img)
        resposta = data2
        data = encontrar_dados(texto_extraido, resposta)
        data2 = encontrar_por_contorno(caminho_png_editado, data)
        print(data2)

    if data2['nome'] == None or data2['cpf']==None or data2['nasc']==None or data2['doc']==None:
        print( 'TENTATIVA 4')

        print('procurar item faltante', data2)
        # tentativa 2
        img = editar_imagem(img, 4)
        texto_extraido = extrair_texto(img)
        resposta = data2
        data = encontrar_dados(texto_extraido, resposta)
        data2 = encontrar_por_contorno(caminho_png_editado, data)
        print(data2)


    else:
        print(f'TODOS OS ITENS FORAM ENCONTRADOS. RETORNANDO DATA')
            
    return jsonify(data2)

if __name__ == '__main__':
    app.run(port=5000, host='localhost', debug=True)
