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
# PATHS
PATH_PARENT = pathlib.Path(__file__).parent
PATH_LOG = PATH_PARENT / 'log.txt'
PATH_CSV = PATH_PARENT / 'data.csv'
PATH_SEQUENCE = PATH_PARENT / 'cadencia'
PATH_INFO = PATH_PARENT / 'info.json'

with open(PATH_INFO, 'r') as info_file:
    info = json.load(info_file)
    
POS = info.get('POS') # Pega a POSIÇÃO ATUAL NA SEQUÊNCIA
MAX = info.get('MAX') # Pega o Limite para saber até onde ir

# Aborta o programa se já tiver completado a cadência
if POS >= MAX:
    with open(PATH_LOG, 'a', encoding='utf-8') as log:
        log.write((f'{datetime.strftime(datetime.now(), "%d/%m/%Y - %H:%M:%S")} - Sequência chegou ao fim!\n'))
    os.abort()
    
PATH_HTML = PATH_SEQUENCE / info.get('PATHS')[POS]

    
# Pega as configs para mandar o email
smtp_server = os.getenv('SMTP_SERVER','')
smtp_port = os.getenv('SMTP_PORT','')
smtp_username = os.getenv('EMAIL_USER', '')
smtp_password = os.getenv('EMAIL_PASSWORD', '')

# Função geradora para passar as linhas do CSV uma a uma.
def read_csv(filename):
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            yield row
            
DATA_LIST = read_csv(PATH_CSV)
    
# Carrega o texto e transforma em template
with open(PATH_HTML, 'r') as file:
    text_file = file.read()
    template_text = Template(text_file)
# Carrega o assunto e transforma em Tamplate
subject = info.get('SUBJECTS')[POS] # Carrega o assunto na posição atual
template_subject = Template(subject)

for dest in DATA_LIST:
    try:
        text_email = template_text.substitute(
            template_nome = dest['NOME'],
            template_empresa = dest['EMPRESA'],
            template_email = dest['EMAIL']
        )
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

        # Conecta e envia o email
        with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(mime_multipart)

            # Escreve no log
            with open(PATH_LOG, 'a+', encoding='utf-8') as log:
                log.write((f'{datetime.strftime(datetime.now(), "%d/%m/%Y - %H:%M:%S")} - Email para {dest["NOME"]} da empresa {dest["EMPRESA"]} enviado com sucesso!\n'))

        
    except smtplib.SMTPRecipientsRefused:
        with open(PATH_LOG, 'a', encoding='utf-8') as log:
            log.write((f'{datetime.strftime(datetime.now(), "%d/%m/%Y - %H:%M:%S")} - Email para {dest["NOME"]} FALHOU!\n'))
            
    except Exception as e:
        with open(PATH_LOG, 'a', encoding='utf-8') as log:
            log.write((f'{datetime.strftime(datetime.now(), "%d/%m/%Y - %H:%M:%S")} - "Ocorreu um Erro!: {e}"\n'))

info['POS'] += 1 # Atualiza a posição na cadência de emails

# Aualiza o arquivo de configuração com a nova posição na cadência
with open(PATH_INFO, 'w') as info_file:
    json.dump(info, info_file, ensure_ascii= False, indent= 2)
    
# Apenas para checar o tempo total de execução
with open(PATH_LOG, 'a', encoding='utf-8') as log:
    log.write(f'O tempo total de execução do main_2 foi {time.time() - start_time}\n')