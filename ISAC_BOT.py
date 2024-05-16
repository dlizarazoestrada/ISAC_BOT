from conector import *
from telebot.types import InlineKeyboardButton
from telebot.types import InlineKeyboardMarkup
from telebot.types import ReplyKeyboardMarkup
from unicodedata import normalize
import telebot
import re


bot = telebot.TeleBot("5910750015:AAHn2eRgFQJ3Xue5QYUuD7NyXqK7P4yGQLM")

columna_codigos = bd.col_values(1)
columna_links = bd.col_values(2)
columna_nombres = bd.col_values(3)
resultados_por_pagina = 5
max_ancho_bot = 5
links_paginas = {
    'andes': "http://siebelprd.vtr.cl:2080/ecommunications_ldap_esn/start.swe?SWECmd=Login&SWECM=S&SRN=&SWEHo=siebelprd.vtr.cl",
    'andes_capa': "http://193.122.167.131:2080/ecommunicationsLDAP_esn/start.swe?SWECmd=Login&SWEBHWND=1&SWECM=S&SRN=&SWEHo=193.122.167.131&SWETS=1670369621",
    'pronto': "https://mail.vtr.net/?Skin=hPronto-",
    'superusuario': "http://superusuario.vtr.cl/loginSU/login.html",
    'mesa_ayuda' : "https://portalvtr.adexus.com/account/login?ReturnUrl=%2f",
    'xperience': "https://lla.cloudcheck.net/vtr/login-page",
    'calculadora' : "http://172.17.97.119/consultaddss/ddss/",
    'sixbell': "http://172.17.206.7:8081/",
    'simplex': "http://172.16.183.76/Simplex/index.php",
    'registro_civil': "https://www.registrocivil.cl/principal/servicios-en-linea/consulta-vigencia-documento-1",
    'endirecto': "https://endirecto.atento.com.co:9090/endirecto/web/index.php/main/login",
    'univirtual': "https://aulavirtual.uni-vtr.com/login/index.php",
    'cafego': "https://cafesite7.atento.com.co:11001/cafe_GO/?redirect=0",
    'academia': "https://academia.atento.com.co/academia/",
    'escalamiento_premium': "http://172.17.102.170/diferido/ingreso_atento.php"
}

plantillas_VTR = {
    'tipificar':"Rut:\n"+\
                "Nombre:\n"+\
                "Dirección:\n"+\
                "Fono:\n"+\
                "Correo:\n\n"+\
                "ATTCOL\n"+\
                "Consulta:\n"+\
                "Resolución:\n"+\
                "SS/Pedido:",
    '7 pasos': "P1: Comercial OK\n"+\
                "P2: Sin masivo\n"+\
                "P3: Modem online/ IP OK\n"+\
                "P4: Estado de red OK\n"+\
                "P5: Estado domicilio OK\n"+\
                "P6: Velocidad / CM COMPATIBLE / NAT7 (CONEXIÓN O VELOCIDAD) OK\n"+\
                "P7: WiFi red correcta / Parametros / RRSSI OK"
}

scripts_basicos = f'<b><i>BIENVENIDA:</i></b>\n\n'+\
                  "Muy buenas tardes / noches habla con (NOMBRE) "+\
                  "del area preferencial de VTR con quién tengo el gusto\n\n"+\
                  "Sr(a) XXXX cuál es el motivo de su consulta\n\n"+\
                  "Sr(a) Podría confirmarme el RUT del titular\n\n"+\
                  '<b><i>VERIFICAR DATOS:</i></b>\n\n'+\
                  "Para verificar en el sistema su solicitud vamos a confirmar algunos datos\n\n"+\
                  '<b><i>RESUMEN:</i></b>\n\n'+\
                  "¿La información ha sido clara?\n\n"+\
                  "¿Tiene alguna otra duda comercial o técnica en la que le pueda colaborar?\n\n"+\
                  '<b><i>ENCUESTA:</i></b>\n\n'+\
                  "Sr(a) XXXX, ¿puedo pedirle un favor?, eventualmente usted podría recibir una "+\
                  "encuesta para evaluar nuestra atención, esta encuesta es por mail con una "+\
                  "evaluación de 0 a 10 siendo 10 la puntuación máxima "+\
                  "¿puedo contar con su opinión?\n\n"+\
                  '<b><i>CIERRE:</i></b>\n\n'+\
                  "Sr(a) XXXX, ante requerimientos futuros lo invitamos a contactarse con nosotros "+\
                  "a través de whatsapp +56 9 6360 0999, también puede ver el ícono de whatsapp "+\
                  "desde la sucursal virtual y aplicación VTR\n\n"+\
                  "Recuerde que ha comunicado con Daniel del área preferencial de VTR "

# Ya sé, variables globales innecesarias, pero tenía pereza D:
pagina_actual = 0
nombres_encontrados = []
links_encontrados = []

# No agrego puntos, comas, etc porque eso se verifica
# en la función filtrar segundo if, tampoco la palabra
# DE porque ya está contenida en DEL
ralentizantes = "DEL CON LA"
# Elimina acentos y diferencias de mayúsculas para realizar la búsqueda


#Al usar el comando /start responde citando al mensaje
@bot.message_handler(commands=["start"])
def start(mensaje):
    if mensaje.text.startswith("/"):
        bot.send_chat_action(mensaje.chat.id, 'typing')
        bot.reply_to(mensaje, "Hola \n")
        obtener_bd()
        markup = sugeridas(mensaje)
        bot.send_message(mensaje.chat.id, "Para buscar una ISAC use palabras clave "+\
            "o escriba el código directamente", reply_markup=markup)
        bot.send_message(mensaje.chat.id, "Para obtener más información use /info")

@bot.message_handler(commands=["info"])
def info(mensaje):
    if mensaje.text.startswith("/"):
        texto = f'<b>ISAC_BOT</b> es un bot creado con el fin de facilitar '+\
                'la búsqueda de información en la <b>ISAC</b>, además almacena algunos ' +\
                '<i>links</i> de utilidad.\n\n' +\
                'Para buscar información envíe un mensaje con <b>palabras clave</b> de '+\
                'la ISAC que desee encontrar, también puede ingresar directamente '+\
                'el <b>código</b>\n\n'+\
                '<b><i>Comandos:</i></b>\n'+\
                '/start - Inicia el bot, carga la base de datos\n'+\
                '/refrescar - Refresca / Actualiza la base de datos\n'+\
                '/links - Muestra la lista de comandos para acceder a las páginas web \n'+ \
                '/plantillas - Muestra la lista de plantillas disponibles \n' + \
                '/scripts - Despliega una lista de scripts básicos\n\n' + \
                'Si desaparecen las palabras sugeridas use /start nuevamente'
        bot.send_message(mensaje.chat.id, texto, parse_mode="html")

@bot.message_handler(commands=["refrescar"])
def refrescar(mensaje):
    if mensaje.text.startswith("/"):
        bot.send_chat_action(mensaje.chat.id, 'typing')
        obtener_bd()
        bot.send_message(mensaje.chat.id, 'Refrescando base de datos')
        bot.send_message(mensaje.chat.id, '¡Base de datos refrescada!')

@bot.message_handler(commands=["links"])
def links(mensaje):
    if mensaje.text.startswith("/"):
        bot.send_chat_action(mensaje.chat.id, 'typing')
        texto = f'<i><b>Links</b></i> \n\n'
        num_link = 0
        for link in links_paginas:
            texto += f'[<b>{num_link + 1}</b>] <b>{link.upper()}</b>  ➡  /{link} \n'
            num_link += 1
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("❌", callback_data="cerrar"))
        bot.send_message(mensaje.chat.id, texto, reply_markup=markup,
                         parse_mode="html",
                         disable_web_page_preview=True)

@bot.message_handler(commands=["plantillas"])
def plantillas(mensaje):
    if mensaje.text.startswith("/"):
        bot.send_chat_action(mensaje.chat.id, 'typing')
        texto = f'<i><b>Plantillas</b></i> \n\n'
        num_plantilla = 0
        opciones_plantillas = []
        for plantilla in plantillas_VTR:
            texto += f'[<b>{num_plantilla + 1}</b>] <b>{plantilla.upper()}</b>\n'
            boton = InlineKeyboardButton(str(num_plantilla + 1),
                                         callback_data=f"{plantilla}")
            opciones_plantillas.append(boton)
            num_plantilla += 1
        markup = InlineKeyboardMarkup()
        markup.add(*opciones_plantillas)
        markup.add(InlineKeyboardButton("❌", callback_data="cerrar"))
        bot.send_message(mensaje.chat.id, texto, reply_markup=markup,
                         parse_mode="html",
                         disable_web_page_preview=True)

@bot.message_handler(commands=["scripts"])
def scripts(mensaje):
    if mensaje.text.startswith("/"):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("❌", callback_data="cerrar"))
        bot.send_message(mensaje.chat.id, scripts_basicos, reply_markup=markup, parse_mode="html")

@bot.message_handler(commands=["tipificaciones"])
def tipificaciones(mensaje):
    if mensaje.text.startswith("/"):
        bot.reply_to(mensaje, "https://isac.custhelp.com/euf/assets/images/adminImages/2594/Tipificaciones_19_08.xlsx")

@bot.message_handler(commands=["andes"])
def andes(mensaje):
    if mensaje.text.startswith("/"):
        bot.reply_to(mensaje, links_paginas['andes'])

@bot.message_handler(commands=["andes_capa"])
def andes_capa(mensaje):
    if mensaje.text.startswith("/"):
        bot.reply_to(mensaje, links_paginas['andes_capa'])

@bot.message_handler(commands=["pronto"])
def pronto(mensaje):
    if mensaje.text.startswith("/"):
        bot.reply_to(mensaje, links_paginas['pronto'])

@bot.message_handler(commands=["superusuario"])
def superusuario(mensaje):
    if mensaje.text.startswith("/"):
        bot.reply_to(mensaje, links_paginas['superusuario'])

@bot.message_handler(commands=["mesa_ayuda"])
def mesadeayuda(mensaje):
    if mensaje.text.startswith("/"):
        bot.reply_to(mensaje, links_paginas['mesa_ayuda'])

@bot.message_handler(commands=["xperience"])
def xperience(mensaje):
    if mensaje.text.startswith("/"):
        bot.reply_to(mensaje, links_paginas['xperience'])

@bot.message_handler(commands=["calculadora"])
def calculadora(mensaje):
    if mensaje.text.startswith("/"):
        bot.reply_to(mensaje, links_paginas['calculadora'])

@bot.message_handler(commands=["sixbell"])
def sixbell(mensaje):
    if mensaje.text.startswith("/"):
        bot.reply_to(mensaje, links_paginas['sixbell'])

@bot.message_handler(commands=["simplex"])
def simplex(mensaje):
    if mensaje.text.startswith("/"):
        bot.reply_to(mensaje, links_paginas['simplex'])

@bot.message_handler(commands=["registro_civil"])
def registro_civil(mensaje):
    if mensaje.text.startswith("/"):
        bot.reply_to(mensaje, links_paginas['registro_civil'])

@bot.message_handler(commands=["endirecto"])
def endirecto(mensaje):
    if mensaje.text.startswith("/"):
        bot.reply_to(mensaje, links_paginas['endirecto'])

@bot.message_handler(commands=["univirtual"])
def univirtual(mensaje):
    if mensaje.text.startswith("/"):
        bot.reply_to(mensaje, links_paginas['univirtual'])

@bot.message_handler(commands=["cafego"])
def cafego(mensaje):
    if mensaje.text.startswith("/"):
        bot.reply_to(mensaje, links_paginas['cafego'])

@bot.message_handler(commands=["academia"])
def academia(mensaje):
    if mensaje.text.startswith("/"):
        bot.reply_to(mensaje, links_paginas['academia'])

@bot.message_handler(commands=["escalamiento_premium"])
def escalamiento_premium(mensaje):
    if mensaje.text.startswith("/"):
        bot.reply_to(mensaje, links_paginas['escalamiento_premium'])

def obtener_bd():
    columna_codigos = bd.col_values(1)
    columna_links = bd.col_values(2)
    columna_nombres = bd.col_values(3)

def normalizar(string):
    string_normalizada = re.sub(
        r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+", r"\1",
        normalize("NFD", string), 0, re.I
    ).upper()
    return string_normalizada

# Palabras y caracteres que demoran la búsqueda
def filtrar(palabras_clave):
    for kw in palabras_clave:
        if normalizar(kw) in ralentizantes:
            palabras_clave.remove(kw)
        # Verifica que no se ingresen caracteres
        if len(kw) == 1:
            palabras_clave.remove(kw)
        if normalizar(kw) == "D-BOX":
            palabras_clave[palabras_clave.index(kw)] = "BOX"
        if normalizar(kw) == "PROCE/TO":
            palabras_clave[palabras_clave.index(kw)] = "Procedimiento"
        if normalizar(kw) == "INCON/TE":
            palabras_clave[palabras_clave.index(kw)] = "Inconveniente"
    return palabras_clave
# Comprueba si las palabras clave corresponden a una columna de la ISAC
def buscar(palabras_clave, columna_busqueda):
    # Almacenan los nombres y links que corresponden a la búsqueda
    resultados = []
    links = []
    # Almacena el peso / número de coincidencias de las ISAC
    # Sirve para posicionar en primer lugar las más relevantes
    peso = []
    # Busca el código ingresado en la bd
    # Busca el texto ingresado en la bd
    for kw in palabras_clave:
        for resultado in columna_busqueda:
            # Si corresponde a un nombre lo guarda sin repetirlo
            if (normalizar(kw) in normalizar(resultado)):
                if not (resultado in resultados):
                    # Guarda el nombre de la ISAC encontrada
                    resultados.append(columna_nombres[columna_busqueda.index(resultado)])
                    # Guarda el link correspondiente a la ISAC encontrada
                    links.append(columna_links[columna_busqueda.index(resultado)])
                    peso.append(1)
                # Agrega peso a la ISAC encontrada
                peso[resultados.index(columna_nombres[columna_busqueda.index(resultado)])] += 1

    peso_ordenado = sorted(peso, reverse=True)
    resultados_ordenados = []
    links_ordenados = []
    for coincidencia in peso_ordenado:
        resultados_ordenados.append(resultados[peso.index(coincidencia)])
        links_ordenados.append(links[peso.index(coincidencia)])
        resultados.pop(peso.index(coincidencia))
        links.pop(peso.index(coincidencia))
        peso.pop(peso.index(coincidencia))

    nombres_encontrados.extend(resultados_ordenados)
    links_encontrados.extend(links_ordenados)

# Crea los botones de los resultados de la búsqueda
def crear_botones(links):
    num_opciones = 0
    list_botones = []
    markup = InlineKeyboardMarkup(row_width=max_ancho_bot)
    while num_opciones < len(links):
        # Crea un botón para resultado encontrado
        boton = InlineKeyboardButton(str((num_opciones + 1)), url=links[num_opciones])
        list_botones.append(boton)
        num_opciones += 1

    b_atras = InlineKeyboardButton("⬅", callback_data="atras")
    b_adelante = InlineKeyboardButton("➡", callback_data="adelante")
    b_cerrar = InlineKeyboardButton("❌", callback_data="cerrar")

    markup.add(*list_botones)
    markup.add(b_atras, b_cerrar, b_adelante)

    return markup

def mostrar_pagina(nombres, links, chat_id, pag = 0, msg_id = None):
    inicio = pag * resultados_por_pagina
    fin = inicio + resultados_por_pagina
    texto = f'<i>Resultados {inicio + 1}-{fin} de {len(nombres)}</i>\n\n'
    n = 1
    markup = crear_botones(links[inicio:fin])
    for item in nombres[inicio:fin]:
        texto += f'[<b>{n}</b>] {item}\n'
        n += 1
    if msg_id:
        bot.edit_message_text(texto, chat_id, msg_id, reply_markup=markup, parse_mode="html")
    else:
        bot.send_message(chat_id, texto, reply_markup=markup, parse_mode="html")

# Responde en el chat
@bot.message_handler(content_types=["text"])
def enviar_isac(mensaje):
    nombres_encontrados.clear()
    links_encontrados.clear()
    global pagina_actual
    pagina_actual = 0
    # Muestra el "escribiendo" como si fuera una persona chateando
    bot.send_chat_action(mensaje.chat.id, 'typing')
    # Evita que se ingresen búsquedas demasiado lentas
    if len(mensaje.text) == 1 or normalizar(mensaje.text) in ralentizantes:
        bot.send_message(mensaje.chat.id, "Intente ser más específico")
        return

    # Divide el mensaje en palabras clave para realizar la búsqueda
    palabras_clave = mensaje.text.split()
    # Elimina palabras que puedan ralentizar la búsqueda
    palabras = filtrar(palabras_clave)
    # Comprueba si las palabras clave corresponden a un nombre de la ISAC
    # Retorna una lista de listas que tiene como primer elemento
    # la lista de nombres y como segundo elemento la lista de links
    if len(palabras_clave) == 1 and palabras_clave[0].isdigit():
        buscar(palabras_clave, columna_codigos)
    else:
        buscar(palabras_clave, columna_nombres)


    # Si no encuentra nada sale de la función y espera otro mensaje
    if len(nombres_encontrados) == 0:
        bot.reply_to(mensaje, "ISAC no encontrada, inténtelo nuevamente")
        return

    mostrar_pagina(nombres_encontrados, links_encontrados, mensaje.chat.id)


@bot.callback_query_handler(func=lambda x: True)
def respuesta_callback(call):
    # Se encarga de gestionar las acciones de los botones con callback
    mensaje_id = call.message.message_id
    chat_id = call.from_user.id
    if call.data == "cerrar":
        bot.delete_message(chat_id, mensaje_id)
    if call.data == "refrescar":
        refrescar()
    if call.data == "atras":
        global pagina_actual
        if pagina_actual == 0:
            bot.answer_callback_query(call.id, "Esta es la última página")
        else:
            pagina_actual -= 1
            mostrar_pagina(nombres_encontrados, links_encontrados, chat_id, pagina_actual, mensaje_id)
    if call.data == "adelante":
        if pagina_actual + 1 > int(len(nombres_encontrados) / resultados_por_pagina):
            bot.answer_callback_query(call.id, "Esta es la última página")
        else:
            pagina_actual += 1
            mostrar_pagina(nombres_encontrados, links_encontrados, chat_id, pagina_actual, mensaje_id)
    if call.data == "tipificar":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("❌", callback_data="cerrar"))
        bot.send_message(chat_id, plantillas_VTR['tipificar'], reply_markup=markup)

    if call.data == "7 pasos":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("❌", callback_data="cerrar"))
        bot.send_message(chat_id, plantillas_VTR['7 pasos'], reply_markup=markup)

def sugeridas(mensaje):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Baja de servicios", "Ajuste", "Excepciones", "Reclamo", \
               "Traslado", "Delivery", "Días sin servicio", "Inhibición", \
               "Horarios", "Incon/te con pago", "Flujo de cobranza", "7 pasos", \
               "Proce/to TV")
    return markup

if __name__ == '__main__':
    print("iniciando el bot")
    bot.infinity_polling()
