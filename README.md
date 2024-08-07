# Descrição provisória.

## Envio de cadência de emails automatizada

- Este script foi desenvolvido para o envio automatizado de emails para clientes da D-Best.
 
- Ele é alimentado por um arquivo CSV com nome, empresa e email do cliente, envia um amail para cada um.

- O agendamento é feito por intermédio de um crontab.

- Os dados do servidor SMTP ficam armazenados em um arquivo .env que deverá ser criado por você, como descrito abaixo.

- O arquifo info.json armazena a posição na fila de emails, a quantidade de emails na cadência e, provisoriamente, os assuntos.
- O Programa envia duas versões do email, uma em HTML e outra TXT. A versão HTML encoda em base64 a assinatura em JPG ao final do email.
  Ele substitui automaticamente os campos ${template_nome}, ${template_empresa} e ${template_email} pelos campos contidos no arquivo CSV,
  tanto no assunto do email quanto nos corpos em HTML e plain text.

- O código pode ser usado para o envio de comunicações internas e externas, boletos, notas fiscais e afins.


## Formato CSV:

|NOME|EMPRESA|EMAIL|
|------|--------|--------|
| Fulano | fulano@empresa.com | empresa teste |

## Formato .env

Se não quiser utilizar um ALIAS, utilize o email normalmente. O Alias dá a possibilidade 
de enviar de uma caixa de emails mas com o nome e endereço de resposta de outra.

SMTP_SERVER="servidor entre aspas"<br />
SMTP_PORT="porta entre aspas"<br />
EMAIL_USER="nome de usuário entre aspas"<br />
EMAIL_PASSWORD="senha entre aspas"<br />
ALIAS="alias entre aspas"<br />

## Formato info.json

{<br /> 
  "POS": 0,<br />
  "MAX": 4,<br />
  "SUBJECTS": [<br />
  <br />
    "Primeiro assunto na  ${template_empresa}? ",<br />
    "Segundo assunto com ${template_nome}",<br />
    "Terceiro assunto",<br />
    "${template_nome} Quarto assunto"<br />
    <br />
  ]<br />
}<br />
