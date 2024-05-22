import time
import os
import csv
import json
import pathlib
import smtplib
import base64
import traceback
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template
from dotenv import load_dotenv

# Constants / Constantes
PATH_PARENT = pathlib.Path(__file__).parent
PATH_LOG = PATH_PARENT / 'log.txt'
PATH_CSV = PATH_PARENT / 'data.csv'
PATH_SEQUENCE = PATH_PARENT / 'cadencia'
PATH_INFO = PATH_PARENT / 'info.json'
PATH_ATTACHMENTS = PATH_PARENT / 'anexos'
PATH_SIGNATURE = PATH_ATTACHMENTS / 'assinatura_andreza.jpeg'

# Load environment variables
# Carrega variaveis de ambiente
load_dotenv()


def load_info():
    '''
    Loads information from info.json
    Carrega informações de info.json
    '''
    with open(PATH_INFO, 'r', encoding='utf-8') as info_file:
        return json.load(info_file)


def save_info(info):
    '''
    Saves information to info.json
    Salva informações em info.json
    '''
    with open(PATH_INFO, 'w', encoding='utf-8') as info_file:
        json.dump(info, info_file, ensure_ascii=False, indent=2)


def read_csv(filename):
    '''
    Reads the list of recipients from csv file
    Lê a lista de destinatários do data.csv
    '''
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        yield from reader


def load_email_template(template_path):
    '''
    Loads email template
    Carrega template dos emails
    '''
    with open(template_path, 'r', encoding='utf-8') as file:
        return Template(file.read())


def load_subject_template(info_path, pos):
    '''
    Loads subject template
    Carrega o template dos assuntos
    '''
    with open(info_path, 'r', encoding='utf-8') as info_file:
        info = json.load(info_file)
        subject_template = info.get('SUBJECTS')[pos]
        return Template(subject_template)


def send_email(smtp_server, smtp_port,
               smtp_username, smtp_password,
               alias, subject,
               body_html, body_text,
               recipient, signature_path
               ):
    """
    Send email using SMTP server.
    Envia o email usando SMTP.
    """
    msg = MIMEMultipart('alternative')
    msg['From'] = alias
    msg['To'] = recipient
    msg['Subject'] = subject

    # Read signature image and encode it in base64
    # Lê a imagem da assinatura e codifica em base64
    with open(signature_path, 'rb') as f:
        signature_data = f.read()
        signature_base64 = base64.b64encode(signature_data).decode('utf-8')

    # Insert the base64 encoded image data into the HTML body
    # Insere a imagem codificada em base64 no corpo do HTML
    body_html_with_signature = body_html.replace(
        '<!--SIGNATURE_BASE64-->', signature_base64
        )

    # Attach both plain text and HTML versions of the email
    # Adiciona ambas as versões de texto simples e HTML do email
    part1 = MIMEText(body_text, 'plain')
    part2 = MIMEText(body_html_with_signature, 'html')

    msg.attach(part1)
    msg.attach(part2)

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)


def log_message(message):
    '''
    Writes to log file
    Escreve arquivo de LOG
    '''
    with open(PATH_LOG, 'a', encoding='utf-8') as log_file:
        log_file.write(message + '\n')


def main():
    '''
    Execute code
    Executa o código
    '''
    try:
        start_time = time.time()
        info = load_info()

        POS = info.get('POS')
        MAX = info.get('MAX')

        if POS >= MAX:
            log_message(f'{datetime.now().strftime("%d/%m/%Y - %H:%M:%S")} \
                - Sequência chegou ao fim!')
            return
        
        
        PATH_HTML = PATH_SEQUENCE / f'{POS}.html'
        PATH_TEXT = PATH_SEQUENCE / f'{POS}.txt'

        smtp_server = os.getenv('SMTP_SERVER', '')
        smtp_port = os.getenv('SMTP_PORT', '')
        smtp_username = os.getenv('EMAIL_USER', '')
        smtp_password = os.getenv('EMAIL_PASSWORD', '')
        alias = os.getenv('ALIAS', '')

        email_template_html = load_email_template(PATH_HTML)
        email_template_text = load_email_template(PATH_TEXT)

        for dest in read_csv(PATH_CSV):
            try:
                body_html = email_template_html.substitute(
                    template_nome=dest['NOME'],
                    template_empresa=dest['EMPRESA'],
                    template_email=dest['EMAIL']
                )

                body_text = email_template_text.substitute(
                    template_nome=dest['NOME'],
                    template_empresa=dest['EMPRESA'],
                    template_email=dest['EMAIL']
                )

                subject_template = load_subject_template(PATH_INFO, POS)
                subject = subject_template.substitute(
                    template_nome=dest['NOME'],
                    template_empresa=dest['EMPRESA'],
                    template_email=dest['EMAIL']
                )

                send_email(
                    smtp_server,
                    int(smtp_port),
                    smtp_username,
                    smtp_password,
                    alias,
                    subject,
                    body_html,
                    body_text,
                    dest['EMAIL'],
                    PATH_SIGNATURE,
                )

                log_message(f'{datetime.now().strftime("%d/%m/%Y - %H:%M:%S")} - Email para {dest["NOME"]} da empresa {dest["EMPRESA"]} enviado com sucesso!')

            except Exception as e:
                log_message(f'{datetime.now().strftime("%d/%m/%Y - %H:%M:%S")} - Email para {dest["NOME"]} FALHOU!: {e}')
                log_message(traceback.format_exc())

        info['POS'] += 1
        save_info(info)
        log_message(f'O tempo total de execução foi {time.time() - start_time}')

    except Exception as e:
        log_message(f'Erro inesperado: {e}')
        log_message(traceback.format_exc())


if __name__ == "__main__":
    
    main()

