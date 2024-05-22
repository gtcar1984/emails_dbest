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

SMTP_SERVER="servidor entre aspas"
SMTP_PORT="porta entre aspas"
EMAIL_USER="nome de usuário entre aspas"
EMAIL_PASSWORD="senha entre aspas"
ALIAS="alias entre aspas"

## Formato info.json

{/n
  "POS": 0,
  "MAX": 4,
  "SUBJECTS": [
    "Primeiro assunto na  ${template_empresa}? ",
    "Segundo assunto com ${template_nome}",
    "Terceiro assunto",
    "${template_nome} Quarto assunto"
  ]
}
