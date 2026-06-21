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
apiKey = "ca45ad00"
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
    Funcionalidad: Carga la lista de objetos Estacionamiento desde memoria secundaria.
    Entrada: ninguna
    Salida:bd (list): lista de objetos si el archivo existe, o None si no existe
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
    Funcionalidad: Carga el diccionario de configuracion del parqueo desde memoria secundaria.
    Entrada: ninguna
    Salida: config (dict): diccionario con la configuracion, o None si no existe
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
    Funcionalidad: Persiste la lista de objetos Estacionamiento en disco usando pickle.
    Entrada: baseDatos (list): lista de objetos Estacionamiento
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
    Funcionalidad: Persiste el diccionario de configuracion en disco usando pickle.
    Entrada: config (dict): diccionario de configuracion del parqueo
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
    Funcionalidad: Calcula cuantos vehiculos generales se pueden llenar masivamente segun las reglas del enunciado (5% especiales, electrico, 5% libre).
    Entrada: config (dict): diccionario con tamano, tieneElectrico, tiempoGracia, montoPorHora
    Salida: tope (int): cantidad maxima de espacios generales a llenar masivamente
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
 
def generarFechaHoraEntrada():
    """
    Funcionalidad: Genera una hora de entrada aleatoria entre las 7:00 am y la hora actual.
    Entrada: ninguna
    Salida: fechaHora (str): fecha y hora en formato DD-MM-AAAA HH:MM
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
    Funcionalidad: Genera una cadena de ubicacion basada en el indice del espacio general.
    Entrada: indice (int): numero de espacio (base 1)
    Salida: ubicacion (str): string con formato G-001, G-002, etc.
    """
    return "G-" + str(indice).zfill(3)
 
def crearQR(contenido, rutaArchivo):
    """
    Funcionalidad: Genera un codigo QR con el contenido dado y lo guarda en disco.
    Entrada: contenido (str): texto a codificar en el QR, rutaArchivo (str): ruta donde guardar la imagen PNG del QR
    Salida: ninguna
    """
    img = qrcode.make(contenido)
    img.save(rutaArchivo)
 
def crearVoucherPDF(vehiculo, rutaQR, rutaPDF):
    """
    Funcionalidad: Genera un voucher en PDF con la informacion del vehiculo y su codigo QR.
    Entrada: vehiculo (Estacionamiento): objeto con la informacion del vehiculo, rutaQR (str): ruta de la imagen QR previamente generada, rutaPDF (str): ruta donde guardar el PDF del voucher
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
    Funcionalidad: Consume la API de Mockaroo para obtener datos de vehiculos, construye un diccionario intermedio, lo imprime en el shell, crea los objetos. Estacionamiento, genera los vouchers PDF con QR y guarda la BD en disco.
    Entrada: baseDatos (list): lista actual de objetos Estacionamiento, config (dict): configuracion del parqueo (tamano, tieneElectrico, etc.)
    Salida: nuevaBD (list): lista actualizada de objetos Estacionamiento
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
 
def obtenerNombreTipo(tipoInt):
    """
    Funcionalidad: Convierte el entero de tipo de vehiculo a su nombre legible.
    Entrada: tipoInt (int): entero que representa el tipo (1-5)
    Salida: nombre (str): nombre del tipo de vehiculo
    """
    dictTipos = {1: "Sedan", 2: "SUV", 3: "Pickup", 4: "Van", 5: "Deportivo"}
    nombre = dictTipos.get(tipoInt, "Otro")
    return nombre
 
def obtenerNombrePago(pagoInt):
    """
    Funcionalidad: Convierte el entero de tipo de pago a su nombre legible.
    Entrada: pagoInt (int): 1=Efectivo, 2=SINPE, 3=Tarjeta
    Salida: nombre (str): nombre del tipo de pago
    """
    dictPagos = {pagoEfectivo: "Efectivo", pagoSinpe: "SINPE", pagoTarjeta: "Tarjeta"}
    nombre = dictPagos.get(pagoInt, "Sin pago")
    return nombre
 
def calcularMonto(fechaEntrada, tiempoGracia, montoPorHora):
    """
    Funcionalidad: Calcula el monto a cobrar segun la hora de entrada, la hora actual, el tiempo de gracia y el monto por hora configurado.
    Entrada: fechaEntrada (str): fecha y hora de entrada en formato DD-MM-AAAA HH:MM, tiempoGracia (int): minutos de gracia sin cobro, montoPorHora (int): costo en colones por hora
    Salida: monto (int): monto total a cobrar en colones
    """
    ahora = datetime.datetime.now()
    entrada = datetime.datetime.strptime(fechaEntrada, "%d-%m-%Y %H:%M")
    minutosEstadia = int((ahora - entrada).total_seconds() / 60)
    if minutosEstadia <= tiempoGracia:
        monto = 0
    else:
        minutosCobrables = minutosEstadia - tiempoGracia
        horasCobrables = minutosCobrables / 60.0
        monto = int(horasCobrables * montoPorHora)
    return monto
 
def crearFacturaPDF(vehiculo, rutaQR, rutaPDF):
    """
    Funcionalidad: Genera la factura en PDF con la informacion completa de la estadia del vehiculo y su codigo QR.
    Entrada: vehiculo (Estacionamiento): objeto con la estadia ya completada, rutaQR (str): ruta de la imagen PNG del QR, rutaPDF (str): ruta donde guardar el PDF
    Salida: ninguna
    """
    placa, marca, color, tipo     = vehiculo.info
    ubicacion, fechaEnt, fechaSal = vehiculo.estadia
    monto, tipoPago               = vehiculo.pago
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(20, 120, 60)
    pdf.cell(0, 10, "FACTURA DE ESTACIONAMIENTO", ln=True, align="C")
    pdf.set_draw_color(20, 120, 60)
    pdf.line(10, 22, 200, 22)
    pdf.ln(6)
    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, "Datos del vehiculo", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(55, 8, "Placa:",      border=0)
    pdf.cell(0,  8, placa,         border=0, ln=True)
    pdf.cell(55, 8, "Marca/Tipo:", border=0)
    pdf.cell(0,  8, str(marca) + " (" + obtenerNombreTipo(tipo) + ")", border=0, ln=True)
    pdf.cell(55, 8, "Color:",      border=0)
    pdf.cell(0,  8, str(color),    border=0, ln=True)
    pdf.cell(55, 8, "Ubicacion:",  border=0)
    pdf.cell(0,  8, ubicacion,     border=0, ln=True)
    pdf.ln(3)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "Detalle de la estadia", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(55, 8, "Hora de entrada:", border=0)
    pdf.cell(0,  8, fechaEnt,           border=0, ln=True)
    pdf.cell(55, 8, "Hora de salida:",  border=0)
    pdf.cell(0,  8, fechaSal,           border=0, ln=True)
    pdf.cell(55, 8, "Tipo de pago:",    border=0)
    pdf.cell(0,  8, obtenerNombrePago(tipoPago), border=0, ln=True)
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(20, 120, 60)
    pdf.cell(55, 10, "TOTAL A PAGAR:", border=0)
    pdf.cell(0,  10, "CRC " + str(monto), border=0, ln=True)
    pdf.ln(3)
    pdf.set_font("Arial", "I", 9)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 8, "Gracias por usar nuestro servicio de estacionamiento.", ln=True, align="C")
    pdf.image(rutaQR, x=75, y=None, w=55)
    pdf.output(rutaPDF)
 
def observarEspacio(ventanaPadre, vehiculo, baseDatos, config):
    """
    Funcionalidad: Abre una ventana Toplevel para observar la informacion de un espacio ocupado (rojo). Muestra los datos del vehiculo y permite pagar. Actualiza la BD si se realiza un pago.
    Entrada: ventanaPadre (tk.Toplevel): ventana del grid de estacionamiento ,vehiculo (Estacionamiento): objeto del espacio ocupado ,baseDatos (list): lista completa de objetos Estacionamiento, config (dict): configuracion del parqueo
    Salida: pagado (bool): True si el vehiculo pago y se libero el espacio
    """
    pagado = [False]
    ventana = tk.Toplevel(ventanaPadre)
    ventana.title("Observar Espacio")
    ventana.resizable(False, False)
    placa, marca, color, tipo  = vehiculo.info
    ubicacion, fechaEntrada, _ = vehiculo.estadia
    marco = tk.Frame(ventana, padx=25, pady=20)
    marco.pack()
    tk.Label(marco, text="Informacion del Espacio",
             font=("Arial", 13, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 12))
    tk.Label(marco, text="# Campo:", anchor="w", width=16).grid(row=1, column=0, sticky="w", pady=3)
    varCampo   = tk.StringVar(value=ubicacion)
    comboCampo = ttk.Combobox(marco, textvariable=varCampo, state="disabled",
                               disabledforeground="black", width=22)
    comboCampo.grid(row=1, column=1, pady=3)
    tk.Label(marco, text="Placa:", anchor="w", width=16).grid(row=2, column=0, sticky="w", pady=3)
    entryPlaca = tk.Entry(marco, width=25)
    entryPlaca.insert(0, placa)
    entryPlaca.config(state="disabled", disabledforeground="black")
    entryPlaca.grid(row=2, column=1, pady=3)
    tk.Label(marco, text="Marca:", anchor="w", width=16).grid(row=3, column=0, sticky="w", pady=3)
    varMarca   = tk.StringVar(value=str(marca))
    comboMarca = ttk.Combobox(marco, textvariable=varMarca, state="disabled",
                               disabledforeground="black", width=22)
    comboMarca.grid(row=3, column=1, pady=3)
    tk.Label(marco, text="Color:", anchor="w", width=16).grid(row=4, column=0, sticky="w", pady=3)
    varColor   = tk.StringVar(value=str(color))
    comboColor = ttk.Combobox(marco, textvariable=varColor, state="disabled",
                               disabledforeground="black", width=22)
    comboColor.grid(row=4, column=1, pady=3)
    tk.Label(marco, text="Hora de entrada:", anchor="w", width=16).grid(row=5, column=0, sticky="w", pady=3)
    entryEntrada = tk.Entry(marco, width=25)
    entryEntrada.insert(0, fechaEntrada)
    entryEntrada.config(state="disabled", disabledforeground="black")
    entryEntrada.grid(row=5, column=1, pady=3)
    tk.Frame(marco, height=2, bd=1, relief="sunken").grid(
        row=6, column=0, columnspan=2, sticky="ew", pady=10)
 
    def accionPagar():
        """
        Funcionalidad: Solicita el tipo de pago, calcula el monto segun la estadia, actualiza el objeto en la BD, genera la factura PDF con QR y libera el espacio en la pantalla.
        Entrada: ninguna (usa variables del closure)
        Salida: ninguna
        """
        ventPago  = tk.Toplevel(ventana)
        ventPago.title("Tipo de Pago")
        ventPago.resizable(False, False)
        marcoPago = tk.Frame(ventPago, padx=20, pady=15)
        marcoPago.pack()
        tk.Label(marcoPago, text="Seleccione el tipo de pago:",
                 font=("Arial", 11, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 8))
        varPago = tk.IntVar(value=pagoEfectivo)
        opcionesPago = [("Efectivo", pagoEfectivo),
            ("SINPE",    pagoSinpe),
            ("Tarjeta",  pagoTarjeta),]
        for i, (texto, valor) in enumerate(opcionesPago):
            tk.Radiobutton(marcoPago, text=texto, variable=varPago,
                           value=valor).grid(row=i+1, column=0, sticky="w", pady=2)
        montoEstimado = calcularMonto(fechaEntrada,
            config.get("tiempoGracia", 0),
            config.get("montoPorHora", 0))
        tk.Label(marcoPago, text="Monto a pagar: CRC " + str(montoEstimado),
                 font=("Arial", 11, "bold"), fg="darkgreen").grid(
            row=len(opcionesPago)+1, column=0, pady=(10, 4))
 
        def confirmarPago():
            """
            Funcionalidad: Confirma el pago con el tipo seleccionado, registra la fecha de salida, actualiza la BD, genera factura PDF y cierra las ventanas.
            Entrada: ninguna (usa variables del closure)
            Salida: ninguna
            """
            tipoPagoElegido = varPago.get()
            confirmacion = messagebox.askyesno(
                "Confirmar pago",
                "Tipo: " + obtenerNombrePago(tipoPagoElegido) +
                "\nMonto: CRC " + str(montoEstimado) +
                "\n\n¿Confirma el pago?")
            if not confirmacion:
                return
            fechaSalida         = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
            vehiculo.estadia[2] = fechaSalida
            vehiculo.pago       = (montoEstimado, tipoPagoElegido)
            contenidoQR  = placa + "-" + str(marca) + "-" + str(tipo) + "-" + fechaEntrada
            fechaFormato = fechaSalida.replace(":", "").replace(" ", "_").replace("-", "")
            nombreBase   = "factura_#" + placa + "_" + fechaFormato
            rutaQR       = nombreBase + ".png"
            rutaPDF      = nombreBase + ".pdf"
            try:
                crearQR(contenidoQR, rutaQR)
                crearFacturaPDF(vehiculo, rutaQR, rutaPDF)
                print("Factura generada:", rutaPDF)
            except Exception as e:
                print("Error generando factura:", e)
            guardarBD(baseDatos)
            pagado[0] = True
            messagebox.showinfo("Pago realizado",
                                "Pago registrado correctamente.\nFactura: " + rutaPDF)
            ventPago.destroy()
            ventana.destroy()
        tk.Button(marcoPago, text="Confirmar pago", width=20,
                  command=confirmarPago).grid(row=len(opcionesPago)+2, column=0, pady=(6, 2))
        tk.Button(marcoPago, text="Cancelar", width=20,
                  command=ventPago.destroy).grid(row=len(opcionesPago)+3, column=0, pady=2)
        ventPago.wait_window()
    tk.Button(marco, text="Pagar", width=22,
              command=accionPagar).grid(row=7, column=0, columnspan=2, pady=(0, 4))
    tk.Button(marco, text="Regresar", width=22,
              command=ventana.destroy).grid(row=8, column=0, columnspan=2, pady=(0, 4))
    ventana.wait_window()
    return pagado[0]
 
def obtenerUbicacionesOcupadas(baseDatos, tipoEspacio):
    """
    Funcionalidad: Retorna la lista de ubicaciones actualmente ocupadas para un tipo de espacio.
    Entrada: baseDatos (list): lista de objetos Estacionamiento, tipoEspacio (int): tipo de espacio a consultar
    Salida: ocupadas (list): lista de strings con las ubicaciones ocupadas
    """
    ocupadas = []
    for obj in baseDatos:
        if obj.tipoEspacio == tipoEspacio:
            ubicacion, _, salida = obj.estadia
            if salida == "":
                ocupadas.append(ubicacion)
    return ocupadas
 
def generarSiguienteUbicacion(baseDatos, tipoEspacio, config):
    """
    Funcionalidad: Determina la siguiente ubicacion libre disponible para el tipo de espacio solicitado, asignando un codigo secuencial (G-XXX, E-XXX, EL-001).
    Entrada: baseDatos (list): lista de objetos Estacionamiento, tipoEspacio (int): tipo de espacio requerido, config (dict): configuracion del parqueo
    Salida: ubicacion (str): codigo de ubicacion libre, o "" si no hay disponibles
    """
    ocupadas = obtenerUbicacionesOcupadas(baseDatos, tipoEspacio)
    if tipoEspacio == tipoElectrico:
        candidato = "EL-001"
        if candidato not in ocupadas:
            return candidato
        return ""
    if tipoEspacio == tipoEspecial:
        prefijo    = "E-"
        tamano     = config["tamano"]
        especiales = int(tamano * 0.05)
        if tamano * 0.05 > especiales:
            especiales = especiales + 1
        if especiales < 2:
            especiales = 2
        limite = especiales
    else:
        prefijo = "G-"
        limite  = config["tamano"]
    contador = 1
    while contador <= limite:
        candidato = prefijo + str(contador).zfill(3)
        if candidato not in ocupadas:
            return candidato
        contador = contador + 1
    return ""
 
def siguienteIdBD(baseDatos):
    """
    Funcionalidad: Calcula el siguiente id disponible para un nuevo objeto Estacionamiento.
    Entrada: baseDatos (list): lista de objetos Estacionamiento
    Salida: nuevoId (int): id siguiente al mayor existente, o 1 si la BD esta vacia
    """
    if len(baseDatos) == 0:
        return 1
    maximo = 0
    for obj in baseDatos:
        if obj.id > maximo:
            maximo = obj.id
    return maximo + 1
 
 
def estacionarVehiculo(ventanaPadre, ubicacionLibre, tipoEspacio, baseDatos, config):
    """
    Funcionalidad: Abre una ventana Toplevel para registrar un vehiculo nuevo en el parqueo. Solicita placa, marca, color y tipo. Asigna ubicacion automaticamente. Genera voucher PDF con QR y guarda la BD actualizada en disco.
    Entrada: ventanaPadre (tk.Toplevel): ventana del grid de estacionamiento, ubicacionLibre (str): ubicacion del espacio verde sobre el que se hizo clic, tipoEspacio (int): tipo del espacio (tipoGeneral, tipoEspecial, tipoElectrico), baseDatos (list): lista de objetos Estacionamiento, config (dict): configuracion del parqueo
    Salida: estacionado (bool): True si el vehiculo fue registrado exitosamente
    """
    estacionado = [False]
 
    ubicacion = generarSiguienteUbicacion(baseDatos, tipoEspacio, config)
    if ubicacion == "":
        messagebox.showwarning("Sin espacio", "No hay espacios disponibles para este tipo.")
        return False
 
    ventana = tk.Toplevel(ventanaPadre)
    ventana.title("Estacionar Vehiculo")
    ventana.resizable(False, False)
 
    marco = tk.Frame(ventana, padx=25, pady=20)
    marco.pack()
 
    tk.Label(marco, text="Registrar Vehiculo",
             font=("Arial", 13, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 4))
    tk.Label(marco, text="Monto por hora: CRC " + str(config.get("montoPorHora", 0)),
             font=("Arial", 10), fg="darkblue").grid(row=1, column=0, columnspan=2, pady=(0, 10))
 
    tk.Label(marco, text="Ubicacion:", anchor="w", width=16).grid(row=2, column=0, sticky="w", pady=4)
    entryUbicacion = tk.Entry(marco, width=25)
    entryUbicacion.insert(0, ubicacion)
    entryUbicacion.config(state="disabled", disabledforeground="black")
    entryUbicacion.grid(row=2, column=1, pady=4)
 
    tk.Label(marco, text="Placa:", anchor="w", width=16).grid(row=3, column=0, sticky="w", pady=4)
    entryPlaca = tk.Entry(marco, width=25)
    entryPlaca.grid(row=3, column=1, pady=4)
 
    tk.Label(marco, text="Marca:", anchor="w", width=16).grid(row=4, column=0, sticky="w", pady=4)
    varMarca   = tk.StringVar()
    comboMarca = ttk.Combobox(marco, textvariable=varMarca,
                               values=marcasDisponibles, state="readonly", width=22)
    comboMarca.current(0)
    comboMarca.grid(row=4, column=1, pady=4)
 
    tk.Label(marco, text="Color:", anchor="w", width=16).grid(row=5, column=0, sticky="w", pady=4)
    varColor   = tk.StringVar()
    comboColor = ttk.Combobox(marco, textvariable=varColor,
                               values=coloresDisponibles, state="readonly", width=22)
    comboColor.current(0)
    comboColor.grid(row=5, column=1, pady=4)
 
    dictTiposVehiculo = {1: "Sedan", 2: "SUV", 3: "Pickup", 4: "Van", 5: "Deportivo"}
    opcionesTipo      = []
    for k, v in dictTiposVehiculo.items():
        opcionesTipo.append(str(k) + " - " + v)
 
    tk.Label(marco, text="Tipo:", anchor="w", width=16).grid(row=6, column=0, sticky="w", pady=4)
    varTipo   = tk.StringVar()
    comboTipo = ttk.Combobox(marco, textvariable=varTipo,
                              values=opcionesTipo, state="readonly", width=22)
    comboTipo.current(0)
    comboTipo.grid(row=6, column=1, pady=4)
 
    horaActual = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    tk.Label(marco, text="Hora de entrada:", anchor="w", width=16).grid(row=7, column=0, sticky="w", pady=4)
    entryHora = tk.Entry(marco, width=25)
    entryHora.insert(0, horaActual)
    entryHora.config(state="disabled", disabledforeground="black")
    entryHora.grid(row=7, column=1, pady=4)
 
    tk.Frame(marco, height=2, bd=1, relief="sunken").grid(
        row=8, column=0, columnspan=2, sticky="ew", pady=10)
 
    def accionEstacionar():
        """
        Funcionalidad:Valida los campos, confirma la accion, crea el objeto Estacionamiento, lo agrega a la BD, genera el voucher PDF con QR y guarda en disco.
        Entrada: ninguna (usa variables del closure)
        Salida:ninguna
        """
        placa = entryPlaca.get().strip().upper()
        if placa == "":
            messagebox.showwarning("Campo vacio", "Debe ingresar la placa del vehiculo.")
            return
        tipoStr  = varTipo.get()
        tipoInt  = int(tipoStr.split(" - ")[0])
        marca    = varMarca.get()
        color    = varColor.get()
        confirmacion = messagebox.askyesno("Confirmar estacionamiento",
            "Placa: " + placa + "\n" +
            "Marca: " + marca + "\n" +
            "Color: " + color + "\n" +
            "Ubicacion: " + ubicacion + "\n\n" +
            "¿Confirma el estacionamiento?")
        if not confirmacion:
            return
        nuevoId  = siguienteIdBD(baseDatos)
        nuevoObj = Estacionamiento(id = nuevoId,
            placa = placa,
            marca = marca,
            color = color,
            tipo = tipoInt,
            tipoEspacio = tipoEspacio,
            ubicacion = ubicacion,
            fechaHoraEntrada = horaActual,
            fechaHoraSalida = "",
            monto = 0,
            tipoPago = 0)
        baseDatos.append(nuevoObj)
        contenidoQR = placa + "-" + marca + "-" + str(tipoInt) + "-" + horaActual
        fechaFormato = horaActual.replace(":", "").replace(" ", "_").replace("-", "")
        nombreBase = "voucher_#" + placa + "_" + fechaFormato
        rutaQR = nombreBase + ".png"
        rutaPDF = nombreBase + ".pdf"
        try:
            crearQR(contenidoQR, rutaQR)
            crearVoucherPDF(nuevoObj, rutaQR, rutaPDF)
            print("Voucher generado:", rutaPDF)
        except Exception as e:
            print("Error generando voucher:", e)
        guardarBD(baseDatos)
        estacionado[0] = True
        messagebox.showinfo("Registrado",
                            "Vehiculo estacionado en " + ubicacion + "\nVoucher: " + rutaPDF)
        ventana.destroy()
    tk.Button(marco, text="Estacionar", width=22,
              command=accionEstacionar).grid(row=9, column=0, columnspan=2, pady=(0, 4))
    tk.Button(marco, text="Regresar", width=22,
              command=ventana.destroy).grid(row=10, column=0, columnspan=2, pady=(0, 4))
    ventana.wait_window()
    return estacionado[0]
    
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
            pagado = observarEspacio(ventanaPadre, vehiculo, baseDatos, config)
            if pagado:
                btn.config(bg="green")
        else:
            registrado = estacionarVehiculo(ventanaPadre, ubicacion, tipoEspacio, baseDatos, config)
            if registrado:
                btn.config(bg="red")
    return comando
 
def verEstacionamiento(ventanaPadre, baseDatos, config):
    """
    Funcionalidad: Abre una ventana con el grid grafico del parqueo. Muestra cada espacio en rojo (ocupado) o verde (libre). Al hacer clic en un espacio abre observarEspacio o estacionarVehiculo segun corresponda.
    Entrada: Ventana principal, lista de objetos Estacionamiento y configuracion del parqueo
    Salida: baseDatos (list): lista actualizada tras posibles cambios
    """
    especiales, tieneElectrico, generales = calcularEspacios(config)
    ventanaParqueo = tk.Toplevel(ventanaPadre)
    ventanaParqueo.title("Ver Estacionamiento")
    ventanaParqueo.resizable(False, False)
    marco = tk.Frame(ventanaParqueo, padx=20, pady=15)
    marco.pack()
    tk.Label(marco, text="Estacionamiento", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=10, pady=(0, 2))
    tk.Label(marco, text="Verde = Libre     |     Rojo = Ocupado", font=("Arial", 9), fg="gray").grid(row=1, column=0, columnspan=10, pady=(0, 8))
    marcoCasetilla = tk.Frame(marco, bd=2, relief="ridge")
    marcoCasetilla.grid(row=2, column=0, columnspan=4, padx=4, pady=4, sticky="w")
    tk.Label(marcoCasetilla, text="CASETILLA DE COBRO", font=("Arial", 7, "bold"), bg="lightblue", width=16, height=2).pack()
    marcoBano = tk.Frame(marco, bd=2, relief="ridge")
    marcoBano.grid(row=2, column=4, columnspan=4, padx=4, pady=4, sticky="w")
    tk.Label(marcoBano, text="BANO SANITARIO", font=("Arial", 7, "bold"), bg="lightyellow", width=14, height=2).pack()
    tk.Label(marco, text="Espacios Especiales:", font=("Arial", 9, "bold")).grid(row=3, column=0, columnspan=10, sticky="w", pady=(8, 2))
    for i in range(1, especiales + 1):
        ubicacion = "E-" + str(i).zfill(3)
        color, _ = obtenerColorEspacio(ubicacion, baseDatos)
        btn = tk.Button(marco, text="ESP\n" + str(i), bg=color, fg="white", width=5, height=2, font=("Arial", 7, "bold"))
        btn.grid(row=4, column=i - 1, padx=3, pady=3)
        btn.config(command=construirComando(btn, ubicacion, ventanaParqueo, baseDatos, config, tipoEspecial))
    filaActual = 5
    if tieneElectrico:
        tk.Label(marco, text="Espacio Electrico:", font=("Arial", 9, "bold")).grid(
            row=filaActual, column=0, columnspan=10, sticky="w", pady=(8, 2))
        filaActual = filaActual + 1
        ubicacionEl = "EL-001"
        colorEl, _ = obtenerColorEspacio(ubicacionEl, baseDatos)
        btnEl = tk.Button(marco, text="EL\n001", bg=colorEl, fg="white", width=5, height=2, font=("Arial", 7, "bold"))
        btnEl.grid(row=filaActual, column=0, padx=3, pady=3)
        btnEl.config(command=construirComando(btnEl, ubicacionEl, ventanaParqueo, baseDatos, config, tipoElectrico))
        filaActual = filaActual + 1
    tk.Label(marco, text="Espacios Generales:", font=("Arial", 9, "bold")).grid(row=filaActual, column=0, columnspan=10, sticky="w", pady=(8, 2))
    filaActual = filaActual + 1
    columnas = 10
    col = 0
    fila = filaActual
    for i in range(1, generales + 1):
        ubicacion = "G-" + str(i).zfill(3)
        color, _ = obtenerColorEspacio(ubicacion, baseDatos)
        btn = tk.Button(marco, text="G\n" + str(i).zfill(3), bg=color, fg="white", width=5, height=2, font=("Arial", 7, "bold"))
        btn.grid(row=fila, column=col, padx=3, pady=3)
        btn.config(command=construirComando(btn, ubicacion, ventanaParqueo, baseDatos, config, tipoGeneral))
        col = col + 1
        if col >= columnas:
            col = 0
            fila = fila + 1
    tk.Button(marco, text="Regresar", width=20,command=ventanaParqueo.destroy).grid(row=fila + 1, column=0, columnspan=10, pady=(12, 0))
    ventanaParqueo.wait_window()
    return baseDatos
 
def cerrarVehiculosPendientes(baseDatos, config):
    """
    Funcionalidad: Recorre la BD y cierra todos los vehiculos que no tienen fecha de salida, asignandoles un tipo de pago aleatorio, calculando su monto y generando su factura PDF con QR.
    Entrada: baseDatos (list): lista de objetos Estacionamiento, config (dict): configuracion del parqueo (tiempoGracia, montoPorHora)
    Salida: ninguna (modifica los objetos directamente en la lista)
    """
    for vehiculo in baseDatos:
        _, fechaEntrada, fechaSalida = vehiculo.estadia
        if fechaSalida == "":
            tipoPagoAleatorio = random.randint(pagoEfectivo, pagoTarjeta)
            montoCalculado = calcularMonto(
                fechaEntrada,
                config.get("tiempoGracia", 0),
                config.get("montoPorHora", 0))
            fechaSalidaAhora = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
            vehiculo.estadia[2] = fechaSalidaAhora
            vehiculo.pago = (montoCalculado, tipoPagoAleatorio)
 
            placa, marca, color, tipo = vehiculo.info
            contenidoQR = placa + "-" + str(marca) + "-" + str(tipo) + "-" + fechaEntrada
            fechaFormato = fechaSalidaAhora.replace(":", "").replace(" ", "_").replace("-", "")
            nombreBase = "factura_#" + placa + "_" + fechaFormato
            rutaQR = nombreBase + ".png"
            rutaPDF = nombreBase + ".pdf"
            try:
                crearQR(contenidoQR, rutaQR)
                crearFacturaPDF(vehiculo, rutaQR, rutaPDF)
                print("Factura automatica generada:", rutaPDF)
            except Exception as e:
                print("Error generando factura automatica para", placa, ":", e)
 
def calcularTotalesPorTipo(baseDatos):
    """
    Funcionalidad: Calcula el monto total recaudado por cada tipo de pago.
    Entrada: baseDatos (list): lista de objetos Estacionamiento
    Salida: totales (dict): diccionario con claves pagoEfectivo/pagoSinpe/pagoTarjeta y sus montos acumulados como valores
    """
    totales = {pagoEfectivo: 0, pagoSinpe: 0, pagoTarjeta: 0}
    for vehiculo in baseDatos:
        monto, tipoPago = vehiculo.pago
        if tipoPago in totales:
            totales[tipoPago] = totales[tipoPago] + monto
    return totales
 
def generarCierrePDF(baseDatos):
    """
    Funcionalidad: Genera el archivo cierreDiario.pdf con titulo, fecha, tabla completa de todos los vehiculos, subtotales por tipo de pago y total acumulado. Usa obligatoriamente 3 colores y 3 tamanios de letra.
    Entrada: baseDatos (list): lista de objetos Estacionamiento con toda la info completa
    Salida: ninguna (escribe el archivo en disco)
    """
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    fechaHoy = datetime.datetime.now().strftime("%d/%m/%Y")
    pdf.set_font("Arial", "B", 18)     #Titulo principal (color azul, tamaño 18
    pdf.set_text_color(32, 58, 120)
    pdf.cell(0, 12, "CIERRE DIARIO DE ESTACIONAMIENTO", ln=True, align="C")
    pdf.set_font("Arial", "B", 11)   #Fecha (color verde, tamaño 11)
    pdf.set_text_color(20, 110, 60)
    pdf.cell(0, 7, "Fecha: " + fechaHoy, ln=True, align="C")
    pdf.ln(4)
    pdf.set_font("Arial", "B", 11)  #Encabezado de tabla (color verde, tamaño 11)
    pdf.set_fill_color(20, 110, 60)
    pdf.set_text_color(255, 255, 255)
    anchos = [30, 35, 42, 42, 35, 30]
    encabezados = ["Ubicacion", "Placa", "Hora Entrada", "Hora Salida", "Tipo Pago", "Monto (CRC)"]
    for i in range(len(encabezados)):
        pdf.cell(anchos[i], 9, encabezados[i], border=1, align="C", fill=True)
    pdf.ln()
    pdf.set_font("Arial", "", 9)    #Filas de datos (color negro, tamaño 9)
    pdf.set_text_color(0, 0, 0)
    colorFilaPar  = (240, 240, 240)
    colorFilaImpar = (255, 255, 255)
    contadorFila  = 0
    for vehiculo in baseDatos:
        placa, _, _, _           = vehiculo.info
        ubicacion, fechaEnt, fechaSal = vehiculo.estadia
        monto, tipoPago               = vehiculo.pago
        if contadorFila % 2 == 0:
            pdf.set_fill_color(colorFilaImpar[0], colorFilaImpar[1], colorFilaImpar[2])
        else:
            pdf.set_fill_color(colorFilaPar[0], colorFilaPar[1], colorFilaPar[2])
        pdf.cell(anchos[0], 8, ubicacion,                    border=1, align="C", fill=True)
        pdf.cell(anchos[1], 8, placa,                        border=1, align="C", fill=True)
        pdf.cell(anchos[2], 8, fechaEnt,                     border=1, align="C", fill=True)
        pdf.cell(anchos[3], 8, fechaSal if fechaSal != "" else "---", border=1, align="C", fill=True)
        pdf.cell(anchos[4], 8, obtenerNombrePago(tipoPago),  border=1, align="C", fill=True)
        pdf.cell(anchos[5], 8, str(monto),                   border=1, align="C", fill=True)
        pdf.ln()
        contadorFila = contadorFila + 1
    pdf.ln(5)
    totales  = calcularTotalesPorTipo(baseDatos) #Subtotales por tipo de pago (color verde, tamaño 9)
    totalDia = 0
    pdf.set_font("Arial", "B", 9)
    pdf.set_text_color(20, 110, 60)
    tiposPago = [(pagoEfectivo, "Efectivo"),
        (pagoSinpe,    "SINPE"),
        (pagoTarjeta,  "Tarjeta"),]
    for tipoClave, tipoNombre in tiposPago:
        montoTipo = totales[tipoClave]
        totalDia  = totalDia + montoTipo
        pdf.cell(0, 7,
                 "Total recaudado en " + tipoNombre + ": CRC " + str(montoTipo),
                 ln=True, align="R")
    pdf.ln(2)
    pdf.set_font("Arial", "B", 11)  #Total acumulado del dia (color rojo, tamaño 11)
    pdf.set_text_color(180, 30, 30)
    pdf.cell(0, 9,
             "Total acumulado del dia: CRC " + str(totalDia),
             ln=True, align="R")
    pdf.output("cierreDiario.pdf")
    print("cierreDiario.pdf generado exitosamente.")
 
def cierreDiario(baseDatos, config):
    """
    Funcionalidad: Cierra todos los vehiculos pendientes de pago con tipo de pago aleatorio, genera sus facturas automaticamente, produce el reporte cierreDiario.pdf con tabla completa, subtotales por tipo de pago y total acumulado del dia, usando 3 colores y 3 tamanios de letra obligatorios. Guarda la BD actualizada.
    Entrada: baseDatos (list): lista de objetos Estacionamiento, config (dict): configuracion del parqueo (tiempoGracia, montoPorHora)
    Salida: ninguna
    """
    if len(baseDatos) == 0:
        messagebox.showwarning("Sin datos", "No hay vehiculos en la base de datos.")
        return
    confirmacion = messagebox.askyesno(
        "Cierre diario",
        "Se cerraran todos los vehiculos pendientes de pago.\n"
        "Se generaran facturas automaticas y el reporte PDF.\n\n"
        "¿Desea continuar?")
    if not confirmacion:
        return
    cerrarVehiculosPendientes(baseDatos, config)
    guardarBD(baseDatos)
    try:
        generarCierrePDF(baseDatos)
        messagebox.showinfo("Cierre completado",
                            "Cierre diario realizado correctamente.\n"
                            "Reporte guardado en: cierreDiario.pdf")
    except Exception as e:
        messagebox.showerror("Error", "Error al generar el PDF del cierre:\n" + str(e))
 
def construirSeccionXML(lineas, nombreSeccion, lista):
    """
    Funcionalidad: Agrega al listado de lineas XML una seccion con todos los vehiculos de la lista recibida, de forma plana.
    Entrada: Lista de strings con el XML parcial, nombre de la seccion (Efectivo, SINPE, Tarjeta), lista de objetos del estacionamiento del tipo de pago
    Salida: Lista actualizada con la seccion agregada
    """
    lineas.append("    <" + nombreSeccion + ">")
 
    for vehiculo in lista:
        placa, marca, color, tipo = vehiculo.info
        ubicacion, fechaEntrada, fechaSalida = vehiculo.estadia
        monto, tipoPago = vehiculo.pago
     
        lineas.append("        <vehiculo>")
        lineas.append("            <id>" + str(vehiculo.id) + "</id>")
        lineas.append("            <placa>" + str(placa) + "</placa>")
        lineas.append("            <marca>" + str(marca) + "</marca>")
        lineas.append("            <color>" + str(color) + "</color>")
        lineas.append("            <tipo>" + obtenerNombreTipo(tipo) + "</tipo>")
        lineas.append("            <tipoEspacio>" + str(vehiculo.tipoEspacio) + "</tipoEspacio>")
        lineas.append("            <ubicacion>" + str(ubicacion) + "</ubicacion>")
        lineas.append("            <fechaEntrada>" + str(fechaEntrada) + "</fechaEntrada>")
        lineas.append("            <fechaSalida>" + str(fechaSalida) + "</fechaSalida>")
        lineas.append("            <monto>" + str(monto) + "</monto>")
        lineas.append("            <tipoPago>" + obtenerNombrePago(tipoPago) + "</tipoPago>")
        lineas.append("        </vehiculo>")
     
    lineas.append("    </" + nombreSeccion + ">")
 
    return lineas
def cierrePorTipoPago(baseDatos):
    """
    Funcionalidad: Genera un archivo XML con 3 secciones (Efectivo, SINPE, Tarjeta)
    Cada seccion contiene la informacion completa y plana de los vehiculos que pagaron con ese metodo. Guarda el archivo en disco.
    Entrada:lista de objetos Estacionamiento
    Salida: ninguna
    """
    efectivo = []
    sinpe = []
    tarjeta = []
 
    for vehiculo in baseDatos:
        monto, tipoPago = vehiculo.pago
        if tipoPago == pagoEfectivo:
            efectivo.append(vehiculo)
        if tipoPago == pagoSinpe:
            sinpe.append(vehiculo)
        if tipoPago == pagoTarjeta:
            tarjeta.append(vehiculo)
 
    lineas = []
    lineas.append("<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
    lineas.append("<cierrePorTipoPago>")
    lineas = construirSeccionXML(lineas, "Efectivo", efectivo)
    lineas = construirSeccionXML(lineas, "SINPE", sinpe)
    lineas = construirSeccionXML(lineas, "Tarjeta", tarjeta)
    lineas.append("</cierrePorTipoPago>")
    try:
        archivo = open("cierrePorTipoPago.xml", "w", encoding="utf-8")
        for linea in lineas:
            archivo.write(linea + "\n")
        archivo.close()
        messagebox.showinfo("Cierre por Tipo de Pago", "Archivo cierrePorTipoPago.xml generado exitosamente.")
    except Exception as e:
        messagebox.showerror("Error", "No se pudo guardar el archivo: " + str(e))
     
def exportarCSV(baseDatos):
    """
    Funcionalidad: Exporta la informacion completa de todos los vehiculos de la BD a un archivo CSV sin encabezados, para abrirlo en Excel.
    Entrada: Lista de objetos Estacionamiento
    Salida: un archivo .csv
    """
    if len(baseDatos) == 0:
        messagebox.showwarning("Sin datos", "No hay vehiculos en la base de datos.")
        return
    try:
        archivo = open("cierreDiario.csv", "w", encoding="utf-8")
        for vehiculo in baseDatos:
            placa, marca, color, tipo = vehiculo.info
            ubicacion, fechaEnt, fechaSal = vehiculo.estadia
            monto, tipoPago = vehiculo.pago
            fechaSalStr = fechaSal
            if fechaSal == "":
                fechaSalStr = "---"
            linea = (ubicacion + "," +
                     placa + "," +
                     fechaEnt + "," +
                     fechaSalStr + "," +
                     obtenerNombrePago(tipoPago) + "," +
                     str(monto))
            archivo.write(linea + "\n")
        archivo.close()
        messagebox.showinfo("Exportar CSV",
                            "Archivo cierreDiario.csv generado exitosamente.")
    except Exception as e:
        messagebox.showerror("Error", "No se pudo guardar el archivo: " + str(e))
     
def configuracion(ventanaPadre, config):
    """
    Funcionalidad: Abre una ventana Toplevel para configurar el parqueo. Solicita el tamano del estacionamiento, el tiempo de gracia en minutos, el monto por hora y si tiene espacio electrico. Si ya existe configuracion cargada, muestra los valores actuales y pide confirmacion para actualizar. Guarda en disco.
    Entrada: ventanaPadre (tk.Tk): ventana principal del sistema, config (dict): configuracion actual del parqueo (puede estar vacia)
    Salida: configNueva (dict): diccionario con la configuracion guardada, o None si el usuario cancelo sin guardar
    """
    resultado = [None]
    ventana = tk.Toplevel(ventanaPadre)
    ventana.title("Configuracion del Parqueo")
    ventana.resizable(False, False)
    marco = tk.Frame(ventana, padx=30, pady=25)
    marco.pack()
    tk.Label(marco, text="Configuracion del Parqueo",
             font=("Arial", 13, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 4))
    if len(config) > 0: # Subtitulo si hay config existente
        tk.Label(marco, text="Configuracion actual cargada. Puede modificarla.",
                 font=("Arial", 9), fg="darkblue").grid(
            row=1, column=0, columnspan=2, pady=(0, 10))
    else:
        tk.Label(marco, text="No se detecto configuracion. Complete los campos.",
                 font=("Arial", 9), fg="gray").grid(
            row=1, column=0, columnspan=2, pady=(0, 10))
    tk.Label(marco, text="Tamano del estacionamiento:", # Tamano del estacionamiento
             anchor="w", width=28).grid(row=2, column=0, sticky="w", pady=5)
    entryTamano = tk.Entry(marco, width=18)
    entryTamano.grid(row=2, column=1, pady=5)
    if len(config) > 0:
        entryTamano.insert(0, str(config.get("tamano", "")))
    tk.Label(marco, text="Tiempo de gracia (minutos):", #Tiempo de gracia
             anchor="w", width=28).grid(row=3, column=0, sticky="w", pady=5)
    entryGracia = tk.Entry(marco, width=18)
    entryGracia.grid(row=3, column=1, pady=5)
    if len(config) > 0:
        entryGracia.insert(0, str(config.get("tiempoGracia", "")))
    tk.Label(marco, text="Monto por hora (colones):",  # Monto por hora
             anchor="w", width=28).grid(row=4, column=0, sticky="w", pady=5)
    entryMonto = tk.Entry(marco, width=18)
    entryMonto.grid(row=4, column=1, pady=5)
    if len(config) > 0:
        entryMonto.insert(0, str(config.get("montoPorHora", "")))
    tk.Label(marco, text="¿Tiene espacio electrico?", # Tiene espacio electrico
             anchor="w", width=28).grid(row=5, column=0, sticky="w", pady=5)
    varElectrico = tk.BooleanVar()
    if len(config) > 0:
        varElectrico.set(config.get("tieneElectrico", False))
    else:
        varElectrico.set(False)
    marcoRadio = tk.Frame(marco)
    marcoRadio.grid(row=5, column=1, sticky="w", pady=5)
    tk.Radiobutton(marcoRadio, text="Si", variable=varElectrico,
                   value=True).pack(side="left", padx=(0, 10))
    tk.Radiobutton(marcoRadio, text="No", variable=varElectrico,
                   value=False).pack(side="left")
    tk.Frame(marco, height=2, bd=1, relief="sunken").grid(
        row=6, column=0, columnspan=2, sticky="ew", pady=12)
 
    def accionGuardar():
        """
        Funcionalidad: Valida que los campos sean enteros positivos, pide confirmacion si ya existia configuracion previa, construye el diccionario, lo guarda en disco con pickle y cierra la ventana.
        Entrada: ninguna (usa variables del closure)
        Salida: ninguna
        """
        tamanoStr = entryTamano.get().strip()
        graciaStr = entryGracia.get().strip()
        montoStr  = entryMonto.get().strip()
        if tamanoStr == "" or graciaStr == "" or montoStr == "":  # Validar que no esten vacios
            messagebox.showwarning("Campos vacios",
                                 "Todos los campos son obligatorios.")
            return
        try:
            tamano = int(tamanoStr) # Validar que sean enteros
            tiempoGracia = int(graciaStr)
            montoPorHora = int(montoStr)
        except:
            messagebox.showwarning("Valor invalido",
                                   "El tamano, tiempo de gracia y monto deben ser numeros enteros.")
            return
        if tamano <= 0 or tiempoGracia < 0 or montoPorHora <= 0: # Validar que sean positivos
            messagebox.showwarning("Valor invalido",
                                   "El tamano y monto deben ser mayores a cero.\n"
                                   "El tiempo de gracia no puede ser negativo.")
            return
        if tamano < 3: # Validar tamano minimo para tener al menos 2 especiales + generales
            messagebox.showwarning("Tamano muy pequeno",
                                   "El estacionamiento debe tener al menos 3 espacios.")
            return
        if len(config) > 0: # Pedir confirmacion si ya habia config previa
            confirmacion = messagebox.askyesno(
                "Actualizar configuracion",
                "Ya existe una configuracion guardada.\n"
                "¿Desea reemplazarla con los nuevos valores?")
            if not confirmacion:
                return
        tieneElectrico = varElectrico.get()
        configNueva = {
            "tamano":        tamano,
            "tiempoGracia":  tiempoGracia,
            "montoPorHora":  montoPorHora,
            "tieneElectrico": tieneElectrico}
        guardarConfig(configNueva)
        resultado[0] = configNueva
        messagebox.showinfo("Configuracion guardada",
                            "Configuracion guardada correctamente.\n"
                            "Tamano: "           + str(tamano)       + " espacios\n"
                            "Tiempo de gracia: " + str(tiempoGracia) + " minutos\n"
                            "Monto por hora: CRC " + str(montoPorHora) + "\n"
                            "Espacio electrico: " + ("Si" if tieneElectrico else "No"))
        ventana.destroy()
    tk.Button(marco, text="Guardar", width=24,
              command=accionGuardar).grid(row=7, column=0, columnspan=2, pady=(0, 4))
    tk.Button(marco, text="Regresar", width=24,
              command=ventana.destroy).grid(row=8, column=0, columnspan=2, pady=(0, 4))
    ventana.wait_window()
    return resultado[0]
 
def acercaDe(ventanaPadre):
    """
    Funcionalidad: Abre una ventana con informacion del sistema y del equipo desarrollador.
    Entrada: ventanaPadre (tk.Tk): ventana principal del menu
    Salida: ninguna
    """
    ventana = tk.Toplevel(ventanaPadre)
    ventana.title("Acerca de")
    ventana.resizable(False, False)
    marco = tk.Frame(ventana, padx=30, pady=25)
    marco.pack()
    tk.Label(marco, text="Sistema de Estacionamiento",
             font=("Arial", 15, "bold"), fg="#22527a").grid(row=0, column=0, pady=(0, 4))
    tk.Label(marco, text="Version 3.14.4",
             font=("Arial", 10, "italic"), fg="gray").grid(row=1, column=0, pady=(0, 14))
    tk.Frame(marco, height=2, bd=1, relief="sunken").grid(
        row=2, column=0, sticky="ew", pady=(0, 12))
    tk.Label(marco, text="Desarrollado por:",
             font=("Arial", 11, "bold")).grid(row=3, column=0, pady=(0, 6))
    tk.Label(marco, text="Pablo Vargas",
             font=("Arial", 11)).grid(row=4, column=0)
    tk.Label(marco, text="Julian Moya",
             font=("Arial", 11)).grid(row=5, column=0, pady=(0, 14))
    tk.Label(marco, text="Curso: Taller de Programacion",
             font=("Arial", 10), fg="#444444").grid(row=6, column=0)
    tk.Label(marco, text="Tecnologico de Costa Rica — 2026",
             font=("Arial", 10), fg="#444444").grid(row=7, column=0, pady=(0, 16))
    tk.Frame(marco, height=2, bd=1, relief="sunken").grid(
        row=8, column=0, sticky="ew", pady=(0, 12))
    tk.Button(marco, text="Regresar", width=22,
              command=ventana.destroy).grid(row=9, column=0)
    ventana.wait_window()
