import os
import sys
import subprocess
import shutil
import platform
import re
import datetime
import platform

# CONSTANTES
VERSION = '22.05.12'  # versión del script (año.mes.día)
DEBUG = False  # True: sin cursor_arriba() y muestra los comandos
SO = platform.system()  # sistema operativo
URL_INST_GIT = "https://git-scm.com/downloads"
URL_INST_HEROKU_CLI = "https://devcenter.heroku.com/articles/heroku-cli#install-the-heroku-cli"
MIN_HEROKU_PYTHON_VERSION = "3.7.13"  # versión mínima de Python soportada por Heroku
MAX_HEROKU_PYTHON_VERSION = "3.10.3"  # versión máxima de Python soportada por Heroku
#   colores de texto en la terminal
verde = "\33[1;32m" # texto verde claro
verde2 = "\33[0;32m" # texto verde claro
magenta = "\33[1;35m" # texto magenta claro
azul = "\33[1;36m" # texto azul claro
rojo = "\33[1;31m" # texto rojo claro
amarillo = "\33[1;33m" # texto amarillo claro
blanco = "\33[1;37m" # texto blanco
gris = "\33[0;37m" # texto gris
#    modo de uso
modo_uso = f'Modo de uso:\n'
modo_uso+= f'   {os.path.splitext(os.path.basename(sys.executable))[0]} {sys.argv[0]} nombre_app_heroku [commit]\n'
modo_uso+= f'Parámetros opcionales:\n'
modo_uso+= f'   commit: breve descripción de la versión a desplegar.\n'
modo_uso+= f'\n'
modo_uso+= f'Ejemplo:\n'
modo_uso+= f'   {os.path.splitext(os.path.basename(sys.executable))[0]} {sys.argv[0]} mi-app-en-heroku Corrección de errores\n'


def cuadro(texto):
    """Imprime en la terminal un cuadro con un texto dentro."""
    linea = "─"
    caracteres = len(texto) + 2
    print(f'{amarillo}\33[K┌{linea*caracteres}┐{gris}')
    print(f'{amarillo}\33[K│ {blanco}{texto}{amarillo} │{gris}')
    print(f'{amarillo}\33[K└{linea*caracteres}┘{gris}')
    print()


def cmd_comando(comando, metodo="popen", salida=False):
    """Devuelve el string de salida en la terminal de un comando del sistema."""
    mostrar_comando(comando)
    if metodo == "run":
        if salida:  # imprime la salida de la ejecución en la terminal
            res = subprocess.run(comando, shell=True)
        else:  # sin salida en la terminal
            res = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    elif metodo == "popen":
        out = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = out.communicate()
        if stdout:
            res = stdout.decode("utf-8").strip()
        elif stderr:
            res = stderr.decode("utf-8").strip()
        else:
            res = None
    return res


def cursor_arriba(n=1):
    """Posiciona el cursor n filas hacia arriba."""
    if DEBUG:
        return
    print(f'\33[{n}A', end="")


def mostrar_comando(comando):
    """Muestra el comando en la terminal si procede."""
    if DEBUG:
        print(f'{magenta}{comando}{gris}')

def comprobar_datos_git():
    """Comprueba si los datos personales están configurados en GIT."""
    FALTAN = []  # datos que faltan por añadir a la configuración
    if SO == "Windows":
        VAR_ENV = "UserProfile"
    elif SO == "Linux":
        VAR_ENV = "HOME"
    else:
        return
    RUTA_HOME = os.getenv(VAR_ENV)
    # comprobamos si existe el archivo de configuración
    if not os.path.isfile(RUTA_HOME + "/.gitconfig"):
        FALTAN = ["email", "nombre"]
    # si existe el archivo de configuración
    else:
        # leemos el archivo de configuración
        with open(RUTA_HOME + "/.gitconfig", "r", encoding="utf-8") as f:
            conf_git = f.read()
        # comprobamos si falta el email en el archivo de configuración
        if not re.findall(r'email = \w+@\w+[.]\w+', conf_git):
            FALTAN.append("email")
        # comprobamos si falta el nombre en el archivo de configuración
        if not re.findall(r'name = (.+)', conf_git):
            FALTAN.append("nombre")
    # si procede, solicitamos los datos que faltan
    if FALTAN:
        print(f'{amarillo}\33[KAVISO: Es necesario configurar GIT:{gris}')
    else:
        return  # si todo está correcto, finalizamos la función aquí
    if "email" in FALTAN:
        # solicitamos el email del usuario
        while True:
            EMAIL = input(f'{azul}\33[KIntroduce tu email:{gris} ')
            # comprobamos si el email tiene un formato correcto
            if not re.match(r'\w+@\w+[.]\w+', EMAIL):
                print(f'{rojo}   ERROR: Introduce un email válido{gris}')
                continue
            else:
                break
        # añadimos el email en la configuración de GIT
        comando = f'git config --global user.email "{EMAIL}"'
        res = cmd_comando(comando)
    if "nombre" in FALTAN:
        # solicitamos el nombre del usuario
        NOMBRE = input(f'{azul}\33[KIntroduce tu nombre:{gris} ')
        # añadimos el nombre en la configuración de GIT
        comando = f'git config --global user.name "{NOMBRE}"'
        res = cmd_comando(comando)
    print(f'{verde}GIT configurado correctamente{gris}')


def comprobar_version(programa):
    """Devuelve la versión si el programa es accesible en el PATH y False en caso contrario."""
    comando = f'{programa} --version'
    res = cmd_comando(comando, metodo="run")
    if res.stdout:
        return res.stdout.decode("utf-8").strip()
    else:
        return False

def comprobar_raspbian():
    """Comprueba si se está ejecutando en Raspbian, en cuyo caso devuelve la versión."""
    if os.path.isfile("/etc/os-release"):
        with open("/etc/os-release", "r", encoding="utf-8") as f:
            contenido = f.read()
        # buscamos la versión en el archivo
        try:
            version = re.search(f'PRETTY_NAME="(.+)"', contenido).group(1)
            if "raspbian" in version.lower():
                return version
        except:
            return False
    else:
        return False


def instalar_heroku_raspbian():
    """Instala Heroku CLI en Raspbian."""
    # preguntamos si se desea instalar Heroku
    while True:
        respuesta = input(f'{amarillo}¿Quieres instalar Heroku ahora? (S/N):{gris} ').upper()
        if respuesta != "S" and respuesta != "N":
            print(f'{rojo}   ERROR: Escribe S (sí) o N (no){gris}')
            continue
        elif respuesta == "N":
            return "NO_INSTALAR"
        elif respuesta == "S":
            break
    # archivos temporales
    temporales = (
        'heroku-linux-arm.tar.gz*',
        '$HOME/.config/heroku',
        '$HOME/.cache/heroku',
        '$HOME/.local/share/heroku',
        '/usr/local/lib/heroku',
        '/usr/local/bin/heroku',
        )
    # elimina archivos que pueda haber de instalaciones erróneas anteriores
    print(f'{azul}Eliminando temporales de sesiones anteriores{gris}')
    for temporal in temporales:
        comando = f'sudo rm -rf {temporal} > /dev/null 2>&1'
        res = cmd_comando(comando)
    # comandos para instalar Heroku CLI en Raspbian ((comando, mensaje_terminal))    
    comandos = (
        ('wget https://cli-assets.heroku.com/branches/stable/heroku-linux-arm.tar.gz', 'Descargando Heroku CLI'),  # descarga Heroku CLI para ARM
        ('mkdir -p /usr/local/lib /usr/local/bin', 'Creando directorios'),  # crea las carpetas necesarias
        ('sudo tar -xvzf heroku-linux-arm.tar.gz -C /usr/local/lib', 'Descomprimiendo Heroku CLI'),  # descomprime el contenido
        ('sudo ln -s /usr/local/lib/heroku/bin/heroku /usr/local/bin/heroku', 'Creando enlaces'),  # crea un enlace simbólico
        ('rm -rf heroku-linux-arm.tar.gz* > /dev/null 2>&1', 'Eliminando archivos temporales'),  # elimina el archivo descargado
        ('heroku update', 'Actualizando Heroku CLI #1'),  # actualiza Heroku
        ('heroku update', 'Actualizando Heroku CLI #2'),  # actualiza Heroku (a veces hay que ejecutarlo 2 veces)
        )
    print(f'{azul}Instalando {blanco}Heroku CLI {azul}en Raspbian{gris}')
    for comando, mensaje in comandos:
        print(f'{azul}{mensaje}{gris}')
        res = cmd_comando(comando, metodo="run", salida=True)
        if res.returncode != 0:
            return "ERROR"
    print(f'{verde}Instalado {blanco}Heroku CLI {verde}en Raspbian{gris}')
    return "OK"


def str_version(version, digitos=6, prof=6):
    """Convierte en un string la versión dada para poder compararla con otra versión."""
    lista = version.split(".")
    lista_subversiones = []
    for indice in range(prof):
        try:
            lista_subversiones.append(lista[indice].zfill(digitos))
        except IndexError:
            lista_subversiones.append("0".zfill(digitos))
    return "".join(lista_subversiones)
        

def comprobar_version_python(version_instalada):
    """Comprueba si la versión instalada de Python está dentro del rango de versiones soportadas por Heroku.
    Si se sale del rango, devuelve la versión soportada más próxima a la instalada."""
    if str_version(version_instalada) < str_version(MIN_HEROKU_PYTHON_VERSION):
        return "MIN", MIN_HEROKU_PYTHON_VERSION
    elif str_version(version_instalada) > str_version(MAX_HEROKU_PYTHON_VERSION):
        return "MAX", MAX_HEROKU_PYTHON_VERSION
    else:
        return "OK", version_instalada


# MAIN ##########################################################
if __name__ == '__main__':
    # cuadro con el nombre y versión del programa (que no falte XD)
    cuadro(f'{os.path.splitext(sys.argv[0])[0]} {VERSION} by FRIKIdelTO.com')
    # control de parámetros
    salir = False
    if len(sys.argv) == 1 or "help" in str(sys.argv[1:]):  # sin parámetros necesarios
        print(modo_uso)
        salir = True
    elif len(sys.argv) == 2:  # si se indica solo el nombre de la app
        APP = sys.argv[1].lower()
        COMMIT = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
    else:  # si se indica también el commit
        APP = sys.argv[1].lower()
        COMMIT = " ".join(sys.argv[2:])
    # comprobamos si GIT está instalado
    res = comprobar_version("git")
    if not res:
        print(f'{rojo}ERROR: {blanco}GIT{rojo} no está instalado o no se encuentra en el PATH.{gris}')
        print(f'{amarillo}       Visita el siguiente enlace para instalar GIT:{gris}')
        print(f'{blanco}       {URL_INST_GIT}{gris}')
        salir = True
    # comprobamos si Heroku CLI está instalado
    res = comprobar_version("heroku")
    if not res:
        print(f'{rojo}ERROR: {blanco}Heroku CLI{rojo} no está instalado o no se encuentra en el PATH.{gris}')
        # si el sistema operativo es Raspbian
        if comprobar_raspbian():
            # instalamos Heroku en Raspbian
            res = instalar_heroku_raspbian()
            if res == "ERROR":
                print(f'{rojo}ERROR: No se pudo instalar Heroku.{gris}')
                salir = True
            elif res == "NO_INSTALAR":
                salir = True
            elif len(sys.argv) > 1:
                salir = False
        else:
            print(f'{amarillo}       Visita el siguiente enlace para instalar HEROKU CLI:{gris}')
            print(f'{blanco}       {URL_INST_HEROKU_CLI}{gris}')
            salir = True
    if salir:
        print()
        sys.exit(1)
    # comprobamos si hay que configurar GIT (imprescindible email y nombre del usuario para poder hacer commit)
    comprobar_datos_git()
    # comprobamos si estamos logueados en heroku
    while True:
        print(f'{gris}\33[KComprobando login{gris}')
        comando = 'heroku auth:whoami'
        res = cmd_comando(comando)
        if "not logged in" in res:
            cursor_arriba()
            print(f'{amarillo}\33[KAVISO: Debes loguearte en Heroku para poder continuar{gris}')
            comando = 'heroku login -i'
            mostrar_comando(comando)
            os.system(comando)
        else:
            cursor_arriba()
            print(f'{verde}\33[KLogin OK: {blanco}{res}{gris}')
            break
    # comprobamos si la app indicada ya está creada
    print(f'{gris}\33[KComprobando si la app {blanco}{APP}{gris} existe{gris}')
    comando = f'heroku apps:info {APP}'
    res = cmd_comando(comando)
    cursor_arriba()
    NUEVA_APP = False  # inicializamos la variable
    # si la app existe pero no es nuestra
    if "not have access to the app" in res:
        print(f'{rojo}\33[KERROR: La app {blanco}{APP} {rojo}pertenece a otro usuario.{gris}')
        print(f'{rojo}\33[K       Debes indicar un nombre de app que no exista o que ya hayas creado.{gris}')
        sys.exit(1)
    # si la app indicada no existe
    elif not APP in res:
        NUEVA_APP = True
        while True:
            respuesta = input(f'{amarillo}\33[KLa app {blanco}{APP}{amarillo} no está creada. ¿Quieres crearla? (S/N):{gris} ').upper()
            if respuesta != "S" and respuesta != "N":
                print(f'{rojo}   ERROR: Escribe S (sí) o N (no){gris}')
            else:
                break
        if respuesta == "N":
            sys.exit(0)
        else:
            REGION = None
            while True:
                REGION = input(f'{amarillo}\33[KSelecciona la región (EU/US):{gris} ').upper()
                if REGION != "EU" and REGION != "US":
                    print(f'{rojo}   ERROR: Escribe EU (Europa) o US (Estados Unidos){gris}')
                else:
                    break
            # creamos la app en la región indicada
            comando = f'heroku create {APP} --region {REGION.lower()}'
            res = cmd_comando(comando)
            cursor_arriba()
            # si se produjo algún error al crear la app
            if not "https://" in res:
                print(f'{rojo}\33[KERROR: No se ha podido crear la app {blanco}{APP}{gris}')
                print(res)
                sys.exit(1)
            else:
                print(f'{verde}\33[KCreada app {blanco}{APP}{gris}')
    # si la app indicada existe
    elif APP in res:
        print(f'{verde2}\33[KLa app {blanco}{APP} {verde2}ya fue creada anteriormente{gris}')
    # si no existe el archivo Procfile o es la primera vez que desplegamos el programa en Heroku
    if not os.path.isfile("Procfile") or NUEVA_APP:
        # lista de programas de Python en el directorio actual
        archivos = [_ for _ in os.listdir(".") if _.lower().endswith(".py") and _.lower() != "config.py" and _ != sys.argv[0]]
        # si no se encuentra ningún programa de Python
        if len(archivos) == 0:
            print(f'{rojo}\33[KERROR: No se ha encontrado ningún programa de Python{gris}')
            sys.exit(1)
        # si se encuentra solo un programa de Python (seleccionamos ese como el programa principal)
        elif len(archivos) == 1:
            PROGRAMA = archivos[0]
        # si se encuentra más de un programa de Python
        else:
            # mostramos un menú para seleccionar cuál es el programa principal
            n = 1
            for item in archivos:
                print(f'{azul}[{blanco}{n}{azul}] {item}{gris}')
                n+= 1
            while True:
                respuesta = input(f'{amarillo}\33[KSelecciona el programa principal:{gris} ')
                # controlamos que el valor introducido es un número
                try:
                    respuesta = int(respuesta)
                except ValueError:
                    print(f'{rojo}\33[K   ERROR: Escribe el número que corresponde al programa principal{gris}')
                    continue
                # controlamos que el número introducido esté dentro del rango de opciones
                if respuesta <= 0 or respuesta > len(archivos):
                    print(f'{rojo}\33[K   ERROR: Escribe un número entre 1 y {len(archivos)}{gris}')
                    continue
                # guardamos en la variable el programa seleccionado
                PROGRAMA = archivos[respuesta-1]
                break
    # si ya existía el archivo Procfile
    else:
        # detenemos el programa en Heroku
        print(f'{gris}\33[KDeteniendo {blanco}{APP}{gris}')
        comando = f'heroku ps:kill web.1 -a {APP}'
        res = cmd_comando(comando)
        cursor_arriba()
        if "... done" in res:
            print(f'{verde}\33[KDetenido {blanco}{APP}{gris}')
        else:
            print(f'{rojo}\33[KERROR: No se pudo detener la ejecución de {blanco}{APP}{gris}')
            print(res)
            sys.exit(1)
        with open("Procfile", "r", encoding="utf-8") as f:
            # leemos el archivo y obtenemos el nombre del archivo del programa principal
            contenido_procfile = f.read()
            PROGRAMA = re.search(f'python (.*.py)', contenido_procfile).group(1).strip()
        print(f'{verde2}\33[KCreado {blanco}Procfile {verde2}anteriormente {gris}({contenido_procfile})')
    if NUEVA_APP:
        # creamos el archivo Procfile
        print(f'{gris}Creando {blanco}Procfile{gris}')
        contenido_procfile = f'web: python {PROGRAMA}'
        with open("Procfile", "w", encoding="utf-8") as f:
            f.write(contenido_procfile)
        cursor_arriba()
        print(f'{verde}\33[KCreado {blanco}Procfile{gris} ({contenido_procfile})')
    # creamos el archivo runtime.txt
    print(f'{gris}Creando {blanco}runtime.txt{gris}')
    # nos aseguramos de que la versión de Python que configuremos esté dentro del rango soportado por Heroku
    version_instalada = platform.python_version()
    res, version_python = comprobar_version_python(version_instalada)
    contenido_runtime = f'python-{version_python}'
    with open("runtime.txt", "w", encoding="utf-8") as f:
        f.write(contenido_runtime)
    cursor_arriba()
    if res == "MIN":    
        print(f'{amarillo}La versión de Python instalada ({version_instalada}) es inferior a la soportada por Heroku ({MIN_HEROKU_PYTHON_VERSION}). Se usará esta última.{gris}')
    elif res == "MAX":
        print(f'{amarillo}La versión de Python instalada ({version_instalada}) es superior a la soportada por Heroku ({MAX_HEROKU_PYTHON_VERSION}). Se usará esta última.{gris}')
    print(f'{verde}\33[KCreado {blanco}runtime.txt{gris} ({contenido_runtime})')
    # eliminamos el archivo requirements.txt
    try:
        os.remove("requirements.txt")
    except:
        pass
    # creamos el archivo requirements.txt
    try:
        import pipreqs.pipreqs
    # si el módulo no está instalado
    except ModuleNotFoundError:
        # instalamos el módulo
        print(f'{gris}\33[KInstalando {blanco}pipreqs{gris}')
        comando = f'{sys.executable} -m pip install pipreqs'
        res = cmd_comando(comando)
        cursor_arriba()
        print(f'{verde}\33[KInstalado {blanco}pipreqs{gris}')
    print(f'{gris}\33[KCreando {blanco}requirements.txt{gris}')
    # si la versión de Python instalada no está dentro del rango soportado por Heroku
    if version_instalada != version_python:
        # configuramos pipreqs para que no guarde en el archivo la versión de cada módulo
        # porque si la versión de Python no es la misma, es más probable que haya problemas de dependencias
        # en este caso, Heroku instalará la última versión disponible de cada módulo
        sin_versiones = "--mode no-pin"
    else:
        sin_versiones = ""
    # guardamos en la variable res los módulos detectados por pipreqs
    comando = f'pipreqs --encoding=utf-8 --print {sin_versiones}'
    res = cmd_comando(comando)
    modulos = []  # lista en la que guardaremos los nombres de los módulos
    with open("requirements.txt", "w", encoding="utf-8") as f:
        total_modulos = 0
        for req in res.split("\n"):
            nombre = req.split("==")[0]  # nombre del módulo
            modulos.append(nombre)
            if nombre != "pipreqs":
                f.write(req.strip() + "\n")
                total_modulos+= 1
    cursor_arriba()
    if not os.path.isfile("requirements.txt"):
        print(f'{rojo}\33[KERROR: No se pudo crear el archivo {blanco}requirements.txt{gris}')
        print(res)
        sys.exit(1)
    else:
        print(f'{verde}\33[KCreado {blanco}requirements.txt{gris} ({total_modulos} módulos)')
    # comprobamos los buildpacks
    print(f'{gris}Comprobando buildpacks{gris}')
    comando = f'heroku buildpacks -a {APP}'
    res = cmd_comando(comando)
    buildpacks = re.findall(r'\d+. (.*)', res)
    cursor_arriba()
    # añadimos Python si procede
    if not "heroku/python" in res:
        comando = f'heroku buildpacks:add -a {APP} heroku/python'
        res = cmd_comando(comando)
        # si ya se había añadido (pero aún no se ha desplegado un commit)
        if "already set" in res:
            print(f'{amarillo}Buildpack {blanco}python {amarillo}añadido en esta sesión{gris}')
        elif not "Buildpack added" in res:
            print(f'{rojo}\33[KERROR: No se pudo añadir buildpack {blanco}python{gris}')
            print(res)
            sys.exit(1)
        else:
            print(f'{verde}Buildpack {blanco}python {verde}añadido{gris}')
    else:
        print(f'{verde2}Buildpack {blanco}python {verde2}añadido anteriormente{gris}')
    # comprobamos si es necesario añadir los buildpacks de chrome y chromedriver
    if "selenium" in modulos:
        # si no figura chrome
        if not "https://github.com/heroku/heroku-buildpack-google-chrome" in buildpacks:
            comando = f'heroku buildpacks:add -a {APP} https://github.com/heroku/heroku-buildpack-google-chrome'
            res = cmd_comando(comando)
            # si ya se había añadido (pero aún no se ha desplegado un commit)
            if "already set" in res:
                print(f'{amarillo}Buildpack {blanco}chrome {amarillo}añadido en esta sesión{gris}')
            elif not "Buildpack added" in res:
                print(f'{rojo}\33[KERROR: No se pudo añadir buildpack {blanco}chrome{gris}')
                print(res)
                sys.exit(1)
            else:
                print(f'{verde}Buildpack {blanco}chrome {verde}añadido{gris}')
        else:
            print(f'{verde2}Buildpack {blanco}chrome {verde2}añadido anteriormente{gris}')
        # si no figura chromedriver
        if not "https://github.com/heroku/heroku-buildpack-chromedriver" in buildpacks:
            comando = f'heroku buildpacks:add -a {APP} https://github.com/heroku/heroku-buildpack-chromedriver'
            res = cmd_comando(comando)
            # si ya se había añadido (pero aún no se ha desplegado un commit)
            if "already set" in res:
                print(f'{amarillo}Buildpack {blanco}chromedriver {amarillo}añadido en esta sesión{gris}')
            elif not "Buildpack added" in res:
                print(f'{rojo}\33[KERROR: No se pudo añadir buildpack {blanco}chromedriver{gris}')
                print(res)
                sys.exit(1)
            else:
                print(f'{verde}Buildpack {blanco}chromedriver {verde}añadido{gris}')
        else:
            print(f'{verde2}Buildpack {blanco}chromedriver {verde2}añadido anteriormente{gris}')
    # si es la primera vez que se va a desplegar el programa
    if NUEVA_APP:
        comando = 'git init'
        res = cmd_comando(comando)
        print(f'{verde}\33[KRepositorio GIT inicializado{gris}')
    # vinculamos el repositorio a nuestra app de Heroku
    comando = f'heroku git:remote {APP}'
    res = cmd_comando(comando)
    if not "set git remote" in res:
        print(f'{rojo}\33[KERROR: No se ha podido vincular el repositorio a la app{gris}')
        print(res)
        sys.exit(1)
    else:
        print(f'{verde}\33[KRepositorio GIT vinculado a la app{gris}')
    # añadimos el origen
    if NUEVA_APP:
        comando = f'git remote add origin https://git.heroku.com/{APP}.git'
        res = cmd_comando(comando)
        print(f'{verde}Añadido origen al repositorio{gris}')
    # añadimos todos los archivos al repositorio
    comando = 'git add .'
    res = cmd_comando(comando)
    print(f'{verde}Añadidos todos los archivos al repositorio{gris}')
    # definimos un commit
    comando = f'git commit -am "{COMMIT}"'
    res = cmd_comando(comando)
    print(f'{verde}Creado commit {blanco}{COMMIT}{gris}')
    # desplegamos el programa en Heroku
    print(f'{azul}Desplegando en Heroku{gris}')
    comando = 'git push heroku master'
    res = cmd_comando(comando, metodo="run", salida=True)
    if res.returncode == 0:
        print(f'{verde}\33[KPrograma desplegado correctamente{gris}')
    else:
        print(f'{rojo}\33[KERROR: No se pudo desplegar el programa en Heroku.{gris}')
        sys.exit(1)
    # preguntamos si se desea ejecutar el programa en Heroku
    while True:
        respuesta = input(f'{amarillo}\33[K¿Quieres ejecutar el programa aquí desde Heroku? (S/N):{gris} ').upper()
        if respuesta != "S" and respuesta != "N":
            print(f'{rojo}   ERROR: Escribe S (sí) o N (no){gris}')
        else:
            break
    if respuesta == "N":
        sys.exit(0)
    else:
        # ejecutamos el programa
        with open("Procfile", "r", encoding="utf-8") as f:
            contenido_procfile = f.read()
        PROGRAMA = re.search(r'python (.+)', contenido_procfile).group(1)
        print(f'{azul}\33[KEjecutando {blanco}{PROGRAMA}{gris}')
        comando = f'heroku run -a {APP} python {PROGRAMA}'
        res = cmd_comando(comando, metodo="run", salida=True)
        sys.exit(res.returncode)
