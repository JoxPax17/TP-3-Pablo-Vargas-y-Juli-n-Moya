# Elaborado por: Pablo Vargas y Julian Moya
# Fecha de creacion: 16-06-26 5:30 PM
# Ultima modificacion: 16-06-26 9:14 PM
# Version: 3.14.3

import tkinter as tk
from tkinter import messagebox
import funciones

baseDatos = []
config = {}

def cargarDatos():
    """
    Funcionalidad:Intenta cargar la BD y la configuracion desde disco al iniciar.
    Si existe BD activa los botones 1, 2 y 3 si no, solo 4 y 5.
    Entrada: ninguna
    Salida: ninguna
    """
    bdCargada = funciones.cargarBD()
    if bdCargada != None:
        baseDatos[:] = bdCargada
    configCargada = funciones.cargarConfig()
    if configCargada != None:
        config.update(configCargada)

def actualizarBotones():
    """
    Funcionalidad: Habilita o deshabilita botones segun si hay BD cargada.
    Entrada: ninguna
    Salida: ninguna
    """
    if len(baseDatos) > 0:
        estadoBD = "normal"
    else:
        estadoBD = "disabled"
    btnObtenerVehiculos.config(state=estadoBD)
    btnVerEstacionamiento.config(state=estadoBD)
    btnReportes.config(state=estadoBD)

def accionObtenerVehiculos():
    """
    Funcionalidad: Llama a la funcion que consume la API y llena el parqueo masivamente.
    Entrada: ninguna
    Salida: ninguna
    """
    baseDatos[:] = funciones.obtenerVehiculos(baseDatos, config)
    actualizarBotones()

def accionVerEstacionamiento():
    """
    Funcionalidad: Abre la ventana del grid grafico del parqueo (luces rojo/verde).
    Entrada: ninguna
    Salida: ninguna
    """
    baseDatos[:] = funciones.verEstacionamiento(ventana, baseDatos, config)
    actualizarBotones()

def accionCierreDiario():
    """
    Funcionalidad: Llama al cierre diario del parqueo.
    Entrada: ninguna
    Salida: ninguna
    """
    funciones.cierreDiario(baseDatos, config)

def accionCierrePorTipoPago():
    """
    Funcionalidad: Llama al reporte de cierre por tipo de pago en XML.
    Entrada: ninguna
    Salida: ninguna
    """
    funciones.cierrePorTipoPago(baseDatos)

def accionExportarCSV():
    """
    Funcionalidad: Exporta el cierre diario a un archivo CSV.
    Entrada: ninguna
    Salida: ninguna
    """
    funciones.exportarCSV(baseDatos)

def accionReportes():
    """
    Funcionalidad: Abre una ventana secundaria con los 3 botones de reportes disponibles.
    Entrada: ninguna
    Salida: ninguna
    """
    ventanaRep = tk.Toplevel(ventana)
    ventanaRep.title("Reportes")
    ventanaRep.resizable(False, False)
    marcoRep = tk.Frame(ventanaRep, padx=25, pady=20)
    marcoRep.pack()
    tk.Label(marcoRep, text="Reportes", font=("Arial", 14, "bold")).grid(row=0, column=0, pady=(0, 12))
    opcionesRep = [
        ("a. Cierre diario",           accionCierreDiario),
        ("b. Cierre por tipo de pago", accionCierrePorTipoPago),
        ("c. Exportar cierre a CSV",   accionExportarCSV),
    ]
    for i, (texto, comando) in enumerate(opcionesRep):
        tk.Button(marcoRep, text=texto, width=28, anchor="w", padx=6, command=comando).grid(row=i+1, column=0, pady=3)
    tk.Button(marcoRep, text="Regresar", width=28, command=ventanaRep.destroy).grid(row=len(opcionesRep)+1, column=0, pady=(10, 0))

def accionConfiguracion():
    """
    Funcionalidad: Abre la ventana de configuracion del parqueo (tamano, gracia, monto/hora).
    Entrada: ninguna
    Salida: ninguna
    """
    configNueva = funciones.configuracion(ventana, config)
    if configNueva:
        config.update(configNueva)
        actualizarBotones()

def accionAcercaDe():
    """
    Funcionalidad: Abre la ventana con informacion del equipo desarrollador.
    Entrada: ninguna
    Salida: ninguna
    """
    funciones.acercaDe(ventana)

def accionSalir():
    """
    Funcionalidad: Muestra despedida y cierra la aplicacion.
    Entrada: ninguna
    Salida: ninguna
    """
    messagebox.showinfo("Hasta pronto", "Gracias por usar el Sistema de Parqueo.")
    ventana.destroy()
ventana = tk.Tk()
ventana.title("Sistema de Estacionamiento")
ventana.resizable(False, False)
marco = tk.Frame(ventana, padx=30, pady=25)
marco.pack()
tk.Label(marco, text="Sistema de Estacionamiento", font=("Arial", 16, "bold")).grid(row=0, column=0, pady=(0, 4))
tk.Label(marco, text="Administracion de Parqueo", font=("Arial", 10)).grid(row=1, column=0, pady=(0, 14))
tk.Frame(marco, height=2, bd=1, relief="sunken").grid(row=2, column=0, sticky="ew", pady=(0, 10))
opcionesMenu = [
    ("1. Obtener vehiculos", accionObtenerVehiculos),
    ("2. Ver estacionamiento", accionVerEstacionamiento),
    ("3. Reportes", accionReportes),
    ("4. Configuracion", accionConfiguracion),
    ("5. Acerca de", accionAcercaDe),
    ("6. Salir", accionSalir),]
botonesMenu = []
for i, (texto, comando) in enumerate(opcionesMenu):
    btn = tk.Button(marco, text=texto, width=32, anchor="w", padx=8, command=comando)
    btn.grid(row=i+3, column=0, pady=3)
    botonesMenu.append(btn)
btnObtenerVehiculos = botonesMenu[0]
btnVerEstacionamiento = botonesMenu[1]
btnReportes = botonesMenu[2]
cargarDatos()
actualizarBotones()
ventana.mainloop()
