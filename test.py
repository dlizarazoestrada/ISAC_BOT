"""info - Muestra toda la información del bot
start - Inicia el bot
refrescar - Refresca / Actualiza la base de datos
links - Muestra una lista de links útiles
plantillas - Muestra la lista de plantillas disponibles
scripts - Despliega una lista de scripts básicos
tipificaciones - Envía el pdf para realizar tipificaciones
andes - Link de Andes
andes_capa - Link del Andes de capacitación
pronto - Link de Pronto
superusuario - Link de Superusuario
mesa_ayuda - Link de Mesa de ayuda
xperience - Link de Xperience
calculadora - Link de la calculadora ISAC
sixbell - Link de Sixbell
simplex - Link de Simplex
registro_civil - Link de la página del registro civil chileno
endirecto - Link de Endirecto sin dominio Atento
univirtual - Link de la Univirtual
cafego - Link de Cafe_GO
academia - Link de Academia Atento
escalamiento_premium - Link para realizar escalamientos de canales premium

ISAC_BOT es un bot creado con el fin de facilitar la búsqueda de información en la ISAC. /info para obtener más información."""

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

print(plantillas_VTR['7 pasos'])