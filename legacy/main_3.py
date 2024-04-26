import time
import os
import csv
import json
import pathlib
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from string import Template
from dotenv import load_dotenv

# Constants
PATH_PARENT = pathlib.Path(__file__).parent
PATH_LOG = PATH_PARENT / 'log.txt'
PATH_CSV = PATH_PARENT / 'data.csv'
PATH_SEQUENCE = PATH_PARENT / 'cadencia'
PATH_INFO = PATH_PARENT / 'info.json'
PATH_ATTACHMENTS = PATH_PARENT / 'anexos'
PATH_SIGNATURE = PATH_ATTACHMENTS / 'assinatura_andreza.JPG'

# Load environment variables
load_dotenv()


def load_info():
    """Load information from info.json."""
    with open(PATH_INFO, 'r') as info_file:
        return json.load(info_file)


def save_info(info):
    """Save information to info.json."""
    with open(PATH_INFO, 'w') as info_file:
        json.dump(info, info_file, ensure_ascii=False, indent=2)


def read_csv(filename):
    """Read CSV file and return a generator of rows."""
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        yield from reader


def load_email_template(template_path):
    """Load email template from HTML file."""
    with open(template_path, 'r') as file:
        return Template(file.read())


def load_subject_template(info_path, pos):
    """Load subject template from info.json."""
    with open(info_path, 'r') as info_file:
        info = json.load(info_file)
        subject_template = info.get('SUBJECTS')[pos]
        return Template(subject_template)


def send_email(smtp_server, smtp_port, smtp_username, smtp_password, alias, subject, body, recipient, signature):
    """Send email using SMTP server."""
    msg = MIMEMultipart()
    msg['From'] = alias
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    # Attach signature image
    with open(signature, 'rb') as f:
        img = MIMEImage(f.read())
        img.add_header('Content-ID', '<signature>')
        msg.attach(img)

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)


def log_message(message):
    """Write message to log file."""
    with open(PATH_LOG, 'a', encoding='utf-8') as log_file:
        log_file.write(message + '\n')


def main():
    start_time = time.time()
    info = load_info()

    # Get current position and maximum limit from info.json
    POS = info.get('POS')
    MAX = info.get('MAX')

    # Abort the program if the cadence is completed
    if POS >= MAX:
        log_message(f'{datetime.now().strftime(
            "%d/%m/%Y - %H:%M:%S")} - Sequência chegou ao fim!')
        os.abort()

    # Construct HTML template path
    PATH_HTML = PATH_SEQUENCE / info.get('PATHS')[POS]

    # Get SMTP server settings from environment variables
    smtp_server = os.getenv('SMTP_SERVER', '')
    smtp_port = os.getenv('SMTP_PORT', '')
    smtp_username = os.getenv('EMAIL_USER', '')
    smtp_password = os.getenv('EMAIL_PASSWORD', '')
    alias = os.getenv('ALIAS', '')

    # Load email template
    email_template = load_email_template(PATH_HTML)

    # Iterate through CSV data and send emails
    for dest in read_csv(PATH_CSV):
        try:
            # Substitute placeholders in email template
            body = email_template.substitute(
                template_nome=dest['NOME'],
                template_empresa=dest['EMPRESA'],
                template_email=dest['EMAIL']
            )

            # Substitute placeholders in subject template
            subject_template = load_subject_template(PATH_INFO, POS)
            subject = subject_template.substitute(
                template_nome=dest['NOME'],
                template_empresa=dest['EMPRESA'],
                template_email=dest['EMAIL']
            )

            # Send email
            send_email(
                smtp_server,
                int(smtp_port),
                smtp_username,
                smtp_password,
                alias,
                subject,
                body,
                dest['EMAIL'],
                PATH_SIGNATURE)

            # Log success
            log_message(
                f'{
                    datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
                } - Email para {
                    dest["NOME"]
                } da empresa {
                    dest["EMPRESA"]
                } enviado com sucesso!'
            )

        except smtplib.SMTPRecipientsRefused:
            # Log failure
            log_message(f'{datetime.now().strftime(
                "%d/%m/%Y - %H:%M:%S")} - Email para {dest["NOME"]} FALHOU!')

        except Exception as e:
            # Log other errors
            log_message(f'{datetime.now().strftime(
                "%d/%m/%Y - %H:%M:%S")} - Ocorreu um Erro!: {e}')

    # Update position in cadence
    info['POS'] += 1

    # Update info.json
    save_info(info)

    # Log total execution time
    log_message(
        f'O tempo total de execução do main 3 foi {time.time() - start_time}'
    )


if __name__ == "__main__":
    main()
