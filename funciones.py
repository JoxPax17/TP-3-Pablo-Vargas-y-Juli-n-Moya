# Elaborado por: Pablo Vargas y Julian Moya
# Fecha de creacion: 16-06-26 9:30 PM
# Ultima modificacion: 16-06-26 11:30 PM
# Version: 3.14.3

import pickle

ARCHIVO_BD = "baseDatos.pkl"
ARCHIVO_CONFIG = "config.pkl"

def cargarBD():
    """
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

# Elaborado por: Pablo Vargas y Julian Moya
# Fecha de creacion: 16-06-26 5:30 PM
# Ultima modificacion: 16-06-26 9:14 PM
# Version: 3.14.3

import pickle, random, datetime, urllib.request, json, qrcode
from fpdf import FPDF

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
 
    except Exception as e:
        print("Error al guardar la BD:", e)
    return nuevaBD
