# Elaborado por: Pablo Vargas y Julian Moya
# Fecha de creacion: 16-06-26 9:30 PM
# Ultima modificacion: 16-06-26 11:30 PM
# Version: 3.14.3

import pickle, random, datetime, urllib.request, json, qrcode
from fpdf import FPDF

ARCHIVO_BD = "baseDatos.pkl"
ARCHIVO_CONFIG = "config.pkl"

def cargarBD():
    """https://github.com/JoxPax17/TP-3-Pablo-Vargas-y-Juli-n-Moya
    Funcionalidad: Carga la lista de objetos Estacionamiento desde memoria secundaria.
    Entrada: ninguna
    Salida: lista de objetos si el archivo existe o None si el archivo no existe
    """
    try:
        archivo = open(ARCHIVO_BD, "rb")
        bd = pickle.load(archivo)
        archivo.close()
        return bd
    except:
        return None

def cargarConfig():
    """
    Funcionalidad: Carga el diccionario de configuracion del parqueo desde memoria secundaria.
    Entrada: ninguna
    Salida: diccionario con la configuracion si el archivo existe o None si el archivo no existe
    """
    try:
        archivo = open(ARCHIVO_CONFIG, "rb")
        config = pickle.load(archivo)
        archivo.close()
        return config
    except:
        return None

ARCHIVO_BD     = "baseDatos.pkl"
ARCHIVO_CONFIG = "config.pkl"
TIPO_GENERAL   = 1
TIPO_ESPECIAL  = 2
TIPO_ELECTRICO = 3
PAGO_EFECTIVO = 1
PAGO_SINPE    = 2
PAGO_TARJETA  = 3
API_KEY = "TU_API_KEY_AQUI"   #reemplazar mas adelante con la key real de Mockaroo
 
class Estacionamiento:
    def __init__(self, id, placa, marca, color, tipo, tipoEspacio,
                 ubicacion, fechaHoraEntrada, fechaHoraSalida, monto, tipoPago):
        self.id          = id
        self.info        = (placa, marca, color, tipo)
        self.estadia     = [ubicacion, fechaHoraEntrada, fechaHoraSalida]
        self.pago        = (monto, tipoPago)
        self.tipoEspacio = tipoEspacio

def calcularTopeMasivo(config):
    """
    Funcionalidad:
        Calcula cuantos vehiculos generales se pueden llenar masivamente
        segun las reglas del enunciado (5% especiales, eléctrico, 5% libre).
    Entrada:
        - config (dict): diccionario con tamano, tieneElectrico, tiempoGracia, montoPorHora
    Salida:
        - tope (int): cantidad maxima de espacios generales a llenar masivamente
    """
    tamano = config["tamano"]
    especiales = int(tamano * 0.05) # Calcular especiales: maximo entre 2 y techo del 5%
    if tamano * 0.05 > especiales:
        especiales = especiales + 1
    if especiales < 2:
        especiales = 2
    disponibles = tamano - especiales # Calcular disponibles para generales
    if config["tieneElectrico"]:
        disponibles = disponibles - 1
    reserva = int(disponibles * 0.05) # Dejar techo del 5% libre para clientes nuevos
    if disponibles * 0.05 > reserva:
        reserva = reserva + 1
    tope = disponibles - reserva
    return tope
 
def generarFechaHoraEntrada():
    """
    Funcionalidad:
        Genera una hora de entrada aleatoria entre las 7:00 am y la hora actual del sistema.
    Entrada:
        - ninguna
    Salida:
        - fechaHora (str): fecha y hora en formato DD-MM-AAAA HH:MM
    """
    ahora = datetime.datetime.now()
    hoy   = ahora.date()
    inicio = datetime.datetime(hoy.year, hoy.month, hoy.day, 7, 0)
    fin    = ahora
    diferencia = int((fin - inicio).total_seconds() / 60)
    if diferencia <= 0:
        diferencia = 1
    minutosAleatorios = random.randint(0, diferencia)
    entrada = inicio + datetime.timedelta(minutes=minutosAleatorios)
    return entrada.strftime("%d-%m-%Y %H:%M")
 
def generarUbicacion(indice):
    """
    Funcionalidad:
        Genera una cadena de ubicacion basada en el indice del espacio general.
    Entrada:
        - indice (int): numero de espacio (base 1)
    Salida:
        - ubicacion (str): string con formato G-001, G-002, etc.
    """
    return "G-" + str(indice).zfill(3)
 
def crearQR(contenido, rutaArchivo):
    """
    Funcionalidad:
        Genera un codigo QR con el contenido dado y lo guarda en disco.
    Entrada:
        - contenido (str): texto a codificar en el QR
        - rutaArchivo (str): ruta donde guardar la imagen PNG del QR
    Salida:
        - ninguna
    """
    img = qrcode.make(contenido)
    img.save(rutaArchivo)
 
def crearVoucherPDF(vehiculo, rutaQR, rutaPDF):
    """
    Funcionalidad:
        Genera un voucher en PDF con la informacion del vehiculo y su codigo QR.
    Entrada:
        - vehiculo (Estacionamiento): objeto con la informacion del vehiculo
        - rutaQR (str): ruta de la imagen QR previamente generada
        - rutaPDF (str): ruta donde guardar el PDF del voucher
    Salida:
        - ninguna
    """
    placa, marca, color, tipo = vehiculo.info
    ubicacion, fechaEntrada, _ = vehiculo.estadia
    MARCAS = {1: "Sedan", 2: "SUV", 3: "Pickup", 4: "Van", 5: "Deportivo"}
    tipoStr = MARCAS.get(tipo, "Otro")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(34, 85, 153)
    pdf.cell(0, 10, "VOUCHER DE ESTACIONAMIENTO", ln=True, align="C")
    pdf.set_draw_color(34, 85, 153)
    pdf.line(10, 22, 200, 22)
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(50, 8, "Placa:",        border=0)
    pdf.cell(0,  8, placa,           border=0, ln=True)
    pdf.cell(50, 8, "Marca:",        border=0)
    pdf.cell(0,  8, tipoStr,         border=0, ln=True)
    pdf.cell(50, 8, "Color:",        border=0)
    pdf.cell(0,  8, str(color),      border=0, ln=True)
    pdf.cell(50, 8, "Ubicacion:",    border=0)
    pdf.cell(0,  8, ubicacion,       border=0, ln=True)
    pdf.cell(50, 8, "Hora entrada:", border=0)
    pdf.cell(0,  8, fechaEntrada,    border=0, ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "I", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 8, "Conserve este voucher para el retiro de su vehiculo.", ln=True, align="C")
    pdf.image(rutaQR, x=75, y=None, w=60)
    pdf.output(rutaPDF)

def obtenerVehiculos(baseDatos, config):
    """
    Funcionalidad:
        Consume la API de Mockaroo para obtener datos de vehiculos, construye
        un diccionario intermedio, lo imprime en el shell, crea los objetos
        Estacionamiento, genera los vouchers PDF con QR y guarda la BD en disco.
    Entrada:
        - baseDatos (list): lista actual de objetos Estacionamiento
        - config (dict): configuracion del parqueo (tamano, tieneElectrico, etc.)
    Salida:
        - nuevaBD (list): lista actualizada de objetos Estacionamiento
    """
    tope = calcularTopeMasivo(config) # 1. Calcular cuántos vehículos pedir
    url = ("https://api.mockaroo.com/api/generate.json"
           "?key=" + API_KEY + "&count=" + str(tope))
    try: # 2. Consumir la API
        respuesta   = urllib.request.urlopen(url)
        datos       = json.loads(respuesta.read().decode("utf-8"))
        respuesta.close()
    except Exception as e:
        print("Error al consumir la API:", e)
        return baseDatos
    diccionario = {} # 3. Construir diccionario intermedio (placa como llave)
    indice      = 1
    for registro in datos:
        # Mockaroo devuelve campos variados; adaptar según el schema configurado
        placa  = str(registro.get("reg_number", "SIN-" + str(indice))).upper()
        marca  = str(registro.get("make",   "Desconocida"))
        color  = str(registro.get("color",  "Blanco"))
        tipoRaw = registro.get("vehicle_year", 2000) # tipo: usamos vehicle_year para derivar un int 1-5 de forma sencilla
        tipo    = (int(tipoRaw) % 5) + 1   # mapea a 1..5
        ubicacion      = generarUbicacion(indice)
        fechaHoraEntrada = generarFechaHoraEntrada()
        diccionario[placa] = {
            "marca":            marca,
            "color":            color,
            "tipo":             tipo,
            "ubicacion":        ubicacion,
            "fechaHoraEntrada": fechaHoraEntrada,
            "fechaHoraSalida":  "",
            "monto":            0,
            "tipoPago":         0}
        indice = indice + 1
    # 4. Imprimir diccionario en shell para verificación
    print("\n===== DICCIONARIO DE VEHICULOS CARGADOS =====")
    for placa, datos in diccionario.items():
        print("Placa:", placa, "->", datos)
    print("=============================================\n")
    nuevaBD = [] # 5. Convertir a objetos Estacionamiento
    idContador = 1
    for placa, datos in diccionario.items():
        obj = Estacionamiento(
            id             = idContador,
            placa          = placa,
            marca          = datos["marca"],
            color          = datos["color"],
            tipo           = datos["tipo"],
            tipoEspacio    = TIPO_GENERAL,
            ubicacion      = datos["ubicacion"],
            fechaHoraEntrada = datos["fechaHoraEntrada"],
            fechaHoraSalida  = datos["fechaHoraSalida"],
            monto          = datos["monto"],
            tipoPago       = datos["tipoPago"])
        nuevaBD.append(obj)
        idContador = idContador + 1
    for obj in nuevaBD: # 6. Generar voucher PDF + QR por cada vehículo
        placa, marca, color, tipo = obj.info
        _, fechaEntrada, _        = obj.estadia
        contenidoQR = (placa + "-" + str(marca) + "-" +
                       str(tipo) + "-" + fechaEntrada)
        fechaFormato = fechaEntrada.replace(":", "").replace(" ", "_").replace("-", "")
        nombreBase   = "voucher_#" + placa + "_" + fechaFormato
        rutaQR  = nombreBase + ".png"
        rutaPDF = nombreBase + ".pdf"
        try:
            crearQR(contenidoQR, rutaQR)
            crearVoucherPDF(obj, rutaQR, rutaPDF)
            print("Voucher creado:", rutaPDF)
        except Exception as e:
            print("Error creando voucher para", placa, ":", e)
    try: # 7. Guardar BD en disco
        archivo = open(ARCHIVO_BD, "wb")
        pickle.dump(nuevaBD, archivo)
        archivo.close()
        print("BD guardada exitosamente con", len(nuevaBD), "vehículos.")
    except Exception as e:
        print("Error al guardar la BD:", e)
    return nuevaBD
    
def calcularEspacios(config):
    """
    Funcionalidad: Calcula la cantidad de espacios generales, especiales y electrico segun la configuracion del parqueo.
    Entrada: configuracion con tamano y tieneElectrico
    Salida:cantidad de espacios especiales, si el parqueo tiene espacio electrico, cantidad de espacios generales disponibles
    """
    tamano = config["tamano"]
    especiales = int(tamano * 0.05)
    if tamano * 0.05 > especiales:
        especiales = especiales + 1
    if especiales < 2:
        especiales = 2
    tieneElectrico = config["tieneElectrico"]
    generales = tamano - especiales
    if tieneElectrico:
        generales = generales - 1
    return especiales, tieneElectrico, generales


def obtenerColorEspacio(ubicacion, baseDatos):
    """
    Funcionalidad: Determina si un espacio esta ocupado o libre buscando en la BD. Un espacio esta ocupado si tiene fecha de salida vacia.
    Entrada: codigo del espacio (ej: G-001, ESP-1, EL-001), lista de objetos Estacionamiento
    Salida: red si ocupado, green si libre y objeto si esta ocupado, None si libre
    """
    for vehiculo in baseDatos:
        if vehiculo.estadia[0] == ubicacion and vehiculo.estadia[2] == "":
            return "red", vehiculo
    return "green", None


def construirComando(btn, ubicacion, ventanaPadre, baseDatos, config, tipoEspacio):
    """
    Funcionalidad:Construye la funcion que ejecuta el clic en un espacio del grid
    Entrada:boton del espacio en el grid, codigo del espacio, ventana del parqueo, lista de objetos Estacion
    configuracion del parqueo y tipo de espacio
    Salida: funcion lista para asignar a comando de un botón
    """
    def comando():
        color, vehiculo = obtenerColorEspacio(ubicacion, baseDatos)
        if color == "red":
            observarEspacio(btn, ubicacion, ventanaPadre, baseDatos, config, vehiculo)
        else:
            estacionarVehiculo(btn, ubicacion, ventanaPadre, baseDatos, config, tipoEspacio)
    return comando
