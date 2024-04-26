import time
start_time = time.time() # Pega a hora atual para medir o tempo de execução
import os
import csv
import json
import pathlib
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template
from dotenv import load_dotenv  # type: ignore

# Carrega as informações de usuário e senha para login no SMTP do arquivo
load_dotenv()

# Caminho para a pasta raiz
PATH_PARENT = pathlib.Path(__file__).parent
# Caminho para a criação e edição do arquivo de log de envio
PATH_LOG = PATH_PARENT / 'log.txt'
# Caminho do arquivo CSV
PATH_CSV = PATH_PARENT / 'data.csv'
# Caminho para a pasta da cadência
PATH_SEQUENCE = PATH_PARENT / 'cadencia'
# Caminho para o arquivo de informações
PATH_INFO = PATH_PARENT / 'info.json'

# Carrega o arquivo de informações
with open(PATH_INFO, 'r') as info_file:
    info = json.load(info_file)

POS = info.get('POS') # Pega a POSIÇÃO ATUAL NA SEQUÊNCIA
MAX = info.get('MAX') # Pega o Limite para saber até onde ir


# Verificação para saber se já chegou ao fim da sequência
if POS < MAX:

    # Caminho arquivo HTML
    PATH_HTML = PATH_SEQUENCE / info.get('PATHS')[POS] # Carrega o caminho na posição atual

    # Configurações SMTP
    # Preciso dessas configs do HOSTINGER. GMAIL apenas para testes
    smtp_server = os.getenv('SMTP_SERVER','') # 'smtp.gmail.com'
    smtp_port = os.getenv('SMTP_PORT','')
    smtp_username = os.getenv('EMAIL_USER', '')
    smtp_password = os.getenv('EMAIL_PASSWORD', '')

    # Abre o arquivo CSV e joga todos os dados na lista de dicionários para envio.
    # Não é um problema agora e é mais rápido, mas aloca mais memória. 
    # DEVOPS - Verificar performance do servidor.
    with open(PATH_CSV, 'r') as file:
        DATA_LIST = [row for row in csv.DictReader(file)]

    # Lê a lista e manda para a função de um em um.
    # Escreve arquivo de log
    for dest in DATA_LIST:
        try:
            # Tentar abrir o arquivo e montar o template uma vez só.
            with open(PATH_HTML, 'r') as file:
                text_file = file.read()
                template = Template(text_file)
                text_email = template.substitute(
                    template_nome = dest['NOME'],
                    template_empresa = dest['EMPRESA'],
                    template_email = dest['EMAIL']
                    )
            # Assunto do email
            subject = info.get('SUBJECTS')[POS] # Carrega o assunto na posição atual
            template_subject = Template(subject) # Transforma em template
            # Substitui o que quer que se queira do template para o campo no CSV
            subject_email = template_subject.substitute(
                    template_nome = dest['NOME'],
                    template_empresa = dest['EMPRESA'],
                    template_email = dest['EMAIL']
            )
            # Monta o email
            mime_multipart = MIMEMultipart()
            mime_multipart['from'] = os.getenv('ALIAS')
            mime_multipart['to'] = dest['EMAIL']
            mime_multipart['subject'] = subject_email

            email_body = MIMEText(text_email, 'html', 'utf-8')
            mime_multipart.attach(email_body)

            with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
                server.ehlo()
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(mime_multipart)
    
                with open(PATH_LOG, 'a+', encoding='utf-8') as log:
                    log.write((f'{datetime.strftime(datetime.now(), "%d/%m/%Y - %H:%M:%S")} - Email para {dest["NOME"]} da empresa {dest["EMPRESA"]} enviado com sucesso!\n'))

        except smtplib.SMTPRecipientsRefused:
            with open(PATH_LOG, 'a', encoding='utf-8') as log:
                log.write((f'{datetime.strftime(datetime.now(), "%d/%m/%Y - %H:%M:%S")} - Email para {dest["NOME"]} FALHOU!\n'))

        
    info['POS'] += 1 # Atualiza a posição na cadência de emails

    # Aualiza o arquivo de configuração com a nova posição na cadência
    with open(PATH_INFO, 'w') as info_file:
        json.dump(info, info_file, ensure_ascii= False, indent= 2)

else:
    with open(PATH_LOG, 'a', encoding='utf-8') as log:
        log.write((f'{datetime.strftime(datetime.now(), "%d/%m/%Y - %H:%M:%S")} - Sequência chegou ao fim!\n'))

# Apenas para checar o tempo total de execução
with open(PATH_LOG, 'a', encoding='utf-8') as log:
    log.write(f'O tempo total de execução do main foi {time.time() - start_time}\n')