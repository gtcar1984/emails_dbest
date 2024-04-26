import time
import os
import csv
import json
import pathlib
import smtplib
import base64
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
PATH_SIGNATURE = PATH_ATTACHMENTS / 'assinatura_andreza.JPG'

# Load environment variables / Carrega variaveis de ambiente
load_dotenv()


def load_info():
    """
    Load information from info.json.
    Carrega as informações do info.json
    """
    with open(PATH_INFO, 'r') as info_file:
        return json.load(info_file)


def save_info(info):
    """
    Save information to info.json.
    Atualiza info.json.
    """
    with open(PATH_INFO, 'w') as info_file:
        json.dump(info, info_file, ensure_ascii=False, indent=2)


def read_csv(filename):
    """
    Read CSV file and return a generator of rows.
    Lê o arquivo CSV e retorna um gerador das linhas.
    """
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        yield from reader


def load_email_template(template_path):
    """
    Load email template from HTML file.
    Carrega o template do arquivo HTML
    """
    with open(template_path, 'r') as file:
        return Template(file.read())


def load_subject_template(info_path, pos):
    """
    Load subject template from info.json.
    Carrega o template do assunto do arquivo info.json.
    """
    with open(info_path, 'r') as info_file:
        info = json.load(info_file)
        subject_template = info.get('SUBJECTS')[pos]
        return Template(subject_template)


def send_email(
    smtp_server, smtp_port,
    smtp_username, smtp_password,
    alias, subject,
    body, recipient,
    signature_path,
):
    """
    Send email using SMTP server.
    Envia o email usando SMTP.
    """
    msg = MIMEMultipart()
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
    body_with_signature = body.replace(
        '<!--SIGNATURE_BASE64-->', signature_base64)

    msg.attach(MIMEText(body_with_signature, 'html'))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)


def log_message(message):
    """
    Write message to log file.
    Escreve a mensagem no arquivo de log.
    """
    with open(PATH_LOG, 'a', encoding='utf-8') as log_file:
        log_file.write(message + '\n')


def main():
    """
    Execute all functions in the correct order.
    Executa todas as funções na ordem correta.
    """
    start_time = time.time()
    info = load_info()

    # Get current position and maximum limit from info.json
    # Pega a posição atual e o limite máximo do arquivo info.json
    POS = info.get('POS')
    MAX = info.get('MAX')

    # Abort the program if the cadence is completed
    # Interrompe o programa se a cadência já foi completa
    if POS >= MAX:
        log_message(f'{datetime.now().strftime(
            "%d/%m/%Y - %H:%M:%S")} - Sequência chegou ao fim!')
        os.abort()

    # Construct HTML template path
    # Contrói o caminho correto para o template HTML
    PATH_HTML = PATH_SEQUENCE / info.get('PATHS')[POS]

    # Get SMTP server settings from environment variables
    # Pega as configurações do srvidor SMTP das variáveis de ambiente
    smtp_server = os.getenv('SMTP_SERVER', '')
    smtp_port = os.getenv('SMTP_PORT', '')
    smtp_username = os.getenv('EMAIL_USER', '')
    smtp_password = os.getenv('EMAIL_PASSWORD', '')
    alias = os.getenv('ALIAS', '')

    # Load email template
    # Carrega o template do email
    email_template = load_email_template(PATH_HTML)

    # Iterate through CSV data and send emails
    # Corre o arquivo CSV e manda os emails
    for dest in read_csv(PATH_CSV):
        try:
            # Substitute placeholders in email template
            # Substitui os placeholders no template do email
            body = email_template.substitute(
                template_nome=dest['NOME'],
                template_empresa=dest['EMPRESA'],
                template_email=dest['EMAIL']
            )

            # Substitute placeholders in subject template
            # Substitui os placeholders no templade do assunto
            subject_template = load_subject_template(PATH_INFO, POS)
            subject = subject_template.substitute(
                template_nome=dest['NOME'],
                template_empresa=dest['EMPRESA'],
                template_email=dest['EMAIL']
            )

            # Send email
            # Envia o email
            send_email(
                smtp_server,
                int(smtp_port),
                smtp_username,
                smtp_password,
                alias,
                subject,
                body,
                dest['EMAIL'],
                PATH_SIGNATURE,
            )

            # Log success
            # Escreve o sucesso no log
            log_message(
                f'{
                    datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
                } - Email para {
                    dest["NOME"]
                } da empresa {
                    dest["EMPRESA"]
                } enviado com sucesso!'
            )

        except Exception as e:
            # Log errors
            # Escreve erros no log
            log_message(f'{datetime.now().strftime(
                "%d/%m/%Y - %H:%M:%S")} - Email para {dest["NOME"]} FALHOU!: {e}')

    # Update position in cadence
    # Atualiza a posição na cadência
    info['POS'] += 1

    # Update info.json
    # Atualiza o arquivo info.json
    save_info(info)

    # Log total execution time
    # Escreve o tempo total de execução no log
    log_message(
        f'O tempo total de execução foi {time.time() - start_time}'
    )


# Check if its the main file and execute the main function
# Verifica se é o arquivo principal e executa a função main
if __name__ == "__main__":
    main()
