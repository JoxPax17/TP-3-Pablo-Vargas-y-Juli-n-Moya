# Elaborado por: Pablo Vargas y Julian Moya
# Fecha de creacion: 16-06-26 9:30 PM
# Ultima modificacion: 17-06-26 12:00 AM
# Version: 3.14.4
 
import pickle, random, datetime, urllib.request, json, qrcode
from fpdf import FPDF
import tkinter as tk
from tkinter import ttk, messagebox
 
archivoBd = "baseDatos.pkl"
archivoConfig = "config.pkl"
tipoGeneral = 1
tipoEspecial = 2
tipoElectrico = 3
pagoEfectivo = 1
pagoSinpe = 2
pagoTarjeta = 3
apiKey = "Poner api key" #Hay que reemplazar esto por la api key real cuando la tengamos 
marcasDisponibles = ["Toyota", "Hyundai", "Kia", "Honda", "Nissan",
                     "Mazda", "Suzuki", "Ford", "Chevrolet", "Volkswagen"]
coloresDisponibles = ["Blanco", "Negro", "Gris", "Rojo", "Azul",
                      "Verde", "Plateado", "Amarillo", "Naranja", "Cafe"]
 
class Estacionamiento:
    def __init__(self, id, placa, marca, color, tipo, tipoEspacio,
                 ubicacion, fechaHoraEntrada, fechaHoraSalida, monto, tipoPago):
        self.id          = id
        self.info        = (placa, marca, color, tipo)
        self.estadia     = [ubicacion, fechaHoraEntrada, fechaHoraSalida]
        self.pago        = (monto, tipoPago)
        self.tipoEspacio = tipoEspacio
 
def cargarBD():
    """
    Funcionalidad:
        Carga la lista de objetos Estacionamiento desde memoria secundaria.
    Entrada: ninguna
    Salida:
        -bd (list): lista de objetos si el archivo existe, o None si no existe
    """
    try:
        archivo = open(archivoBd, "rb")
        bd = pickle.load(archivo)
        archivo.close()
        return bd
    except:
        return None
 
def cargarConfig():
    """
    Funcionalidad:
        Carga el diccionario de configuracion del parqueo desde memoria secundaria.
    Entrada:
        - ninguna
    Salida:
        - config (dict): diccionario con la configuracion, o None si no existe
    """
    try:
        archivo = open(archivoConfig, "rb")
        config = pickle.load(archivo)
        archivo.close()
        return config
    except:
        return None
 
def guardarBD(baseDatos):
    """
    Funcionalidad:
        Persiste la lista de objetos Estacionamiento en disco usando pickle.
    Entrada:
        - baseDatos (list): lista de objetos Estacionamiento
    Salida: ninguna
    """
    try:
        archivo = open(archivoBd, "wb")
        pickle.dump(baseDatos, archivo)
        archivo.close()
    except Exception as e:
        print("Error al guardar BD:", e)
 
def guardarConfig(config):
    """
    Funcionalidad:
        Persiste el diccionario de configuracion en disco usando pickle.
    Entrada:
        - config (dict): diccionario de configuracion del parqueo
    Salida: ninguna
    """
    try:
        archivo = open(archivoConfig, "wb")
        pickle.dump(config, archivo)
        archivo.close()
    except Exception as e:
        print("Error al guardar config:", e)
 
def calcularTopeMasivo(config):
    """
    Funcionalidad:
        Calcula cuantos vehiculos generales se pueden llenar masivamente
        segun las reglas del enunciado (5% especiales, electrico, 5% libre).
    Entrada:
        - config (dict): diccionario con tamano, tieneElectrico, tiempoGracia, montoPorHora
    Salida:
        - tope (int): cantidad maxima de espacios generales a llenar masivamente
    """
    tamano = config["tamano"]
    especiales = int(tamano * 0.05)
    if tamano * 0.05 > especiales:
        especiales = especiales + 1
    if especiales < 2:
        especiales = 2
    disponibles = tamano - especiales
    if config["tieneElectrico"]:
        disponibles = disponibles - 1
    reserva = int(disponibles * 0.05)
    if disponibles * 0.05 > reserva:
        reserva = reserva + 1
    tope = disponibles - reserva
    return tope
 
def calcularEspacios(config):
    """
    Funcionalidad:
        Calcula la cantidad de espacios generales, especiales y electrico
        segun la configuracion del parqueo.
    Entrada:
        - config (dict): configuracion con tamano y tieneElectrico
    Salida:
        - especiales (int): cantidad de espacios especiales
        - tieneElectrico (bool): si el parqueo tiene espacio electrico
        - generales (int): cantidad de espacios generales disponibles
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
 
def generarFechaHoraEntrada():
    """
    Funcionalidad:
        Genera una hora de entrada aleatoria entre las 7:00 am y la hora actual.
    Entrada:
        - ninguna
    Salida:
        - fechaHora (str): fecha y hora en formato DD-MM-AAAA HH:MM
    """
    ahora  = datetime.datetime.now()
    hoy    = ahora.date()
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
    Salida: ninguna
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
    Salida: ninguna
    """
    placa, marca, color, tipo  = vehiculo.info
    ubicacion, fechaEntrada, _ = vehiculo.estadia
    dictTipos = {1: "Sedan", 2: "SUV", 3: "Pickup", 4: "Van", 5: "Deportivo"}
    tipoStr   = dictTipos.get(tipo, "Otro")
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
    pdf.cell(50, 8, "Tipo:",         border=0)
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
    tope = calcularTopeMasivo(config)
    url  = ("https://api.mockaroo.com/api/generate.json""?key=" + apiKey + "&count=" + str(tope))
    try:
        respuesta = urllib.request.urlopen(url)
        datos     = json.loads(respuesta.read().decode("utf-8"))
        respuesta.close()
    except Exception as e:
        print("Error al consumir la API:", e)
        return baseDatos
    diccionario = {}
    indice = 1
    for registro in datos:
        placa = str(registro.get("reg_number", "SIN-" + str(indice))).upper()
        marca = str(registro.get("make",  "Desconocida"))
        color = str(registro.get("color", "Blanco"))
        tipoRaw = registro.get("vehicle_year", 2000)
        tipo = (int(tipoRaw) % 5) + 1
        ubicacion = generarUbicacion(indice)
        fechaHoraEntrada = generarFechaHoraEntrada()
        diccionario[placa] = {
            "marca":marca,
            "color":color,
            "tipo":tipo,
            "ubicacion":ubicacion,
            "fechaHoraEntrada": fechaHoraEntrada,
            "fechaHoraSalida": "",
            "monto":0,
            "tipoPago":0}
        indice = indice + 1
    print("\n===== DICCIONARIO DE VEHICULOS CARGADOS =====")
    for placa, datosVehiculo in diccionario.items():
        print("Placa:", placa, "->", datosVehiculo)
    print("=============================================\n")
    nuevaBD    = []
    idContador = 1
    for placa, datosVehiculo in diccionario.items():
        obj = Estacionamiento(
            id               = idContador,
            placa            = placa,
            marca            = datosVehiculo["marca"],
            color            = datosVehiculo["color"],
            tipo             = datosVehiculo["tipo"],
            tipoEspacio      = tipoGeneral,
            ubicacion        = datosVehiculo["ubicacion"],
            fechaHoraEntrada = datosVehiculo["fechaHoraEntrada"],
            fechaHoraSalida  = datosVehiculo["fechaHoraSalida"],
            monto            = datosVehiculo["monto"],
            tipoPago         = datosVehiculo["tipoPago"])
        nuevaBD.append(obj)
        idContador = idContador + 1
    for obj in nuevaBD:
        placa, marca, color, tipo = obj.info
        _, fechaEntrada, _ = obj.estadia
        contenidoQR = placa + "-" + str(marca) + "-" + str(tipo) + "-" + fechaEntrada
        fechaFormato = fechaEntrada.replace(":", "").replace(" ", "_").replace("-", "")
        nombreBase = "voucher_#" + placa + "_" + fechaFormato
        rutaQR = nombreBase + ".png"
        rutaPDF = nombreBase + ".pdf"
        try:
            crearQR(contenidoQR, rutaQR)
            crearVoucherPDF(obj, rutaQR, rutaPDF)
            print("Voucher creado:", rutaPDF)
        except Exception as e:
            print("Error creando voucher para", placa, ":", e)
    try:
        archivo = open(archivoBd, "wb")
        pickle.dump(nuevaBD, archivo)
        archivo.close()
        print("BD guardada exitosamente con", len(nuevaBD), "vehiculos.")
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

def obtenerColorEspacio(ubicacion, baseDatos):
    """
    Funcionalidad:
        Determina si un espacio esta ocupado o libre buscando en la BD.
        Un espacio esta ocupado si tiene fecha de salida vacia.
    Entrada:
        - ubicacion (str): codigo del espacio (ej: G-001, E-001, EL-001)
        - baseDatos (list): lista de objetos Estacionamiento
    Salida:
        - color (str): "red" si ocupado, "green" si libre
        - vehiculo (Estacionamiento|None): objeto si esta ocupado, None si libre
    """
    for vehiculo in baseDatos:
        if vehiculo.estadia[0] == ubicacion and vehiculo.estadia[2] == "":
            return "red", vehiculo
    return "green", None
 
def construirComando(btn, ubicacion, ventanaPadre, baseDatos, config, tipoEspacio):
    """
    Funcionalidad:
        Construye la funcion que ejecuta el clic en un espacio del grid.
    Entrada:
        - btn (tk.Button): boton del espacio en el grid
        - ubicacion (str): codigo del espacio
        - ventanaPadre (tk.Toplevel): ventana del parqueo
        - baseDatos (list): lista de objetos Estacionamiento
        - config (dict): configuracion del parqueo
        - tipoEspacio (int): tipo del espacio (tipoGeneral, tipoEspecial, tipoElectrico)
    Salida:
        - comando (function): funcion lista para asignar al boton
    """
    def comando():
        color, vehiculo = obtenerColorEspacio(ubicacion, baseDatos)
        if color == "red":
            pagado = observarEspacio(ventanaPadre, vehiculo, baseDatos, config)
            if pagado:
                btn.config(bg="green")
        else:
            registrado = estacionarVehiculo(ventanaPadre, ubicacion, tipoEspacio, baseDatos, config)
            if registrado:
                btn.config(bg="red")
    return comando
 
