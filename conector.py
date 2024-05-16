import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive']

credenciales = ServiceAccountCredentials.from_json_keyfile_name("key.json")
cliente = gspread.authorize(credenciales)

# Crea la base de datos
# sheet = cliente.create('Codigos_ISAC_BOT')
# La comparte con el correo seleccionado
# sheet.share('danielizarazstrad20@gmail.com', perm_type='user', role='writer')
bd = cliente.open("Codigos_ISAC_BOT").sheet1