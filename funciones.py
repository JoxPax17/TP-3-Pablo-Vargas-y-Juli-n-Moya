# Elaborado por: Pablo Vargas y Julian Moya
# Fecha de creacion: 16-06-26 5:30 PM
# Ultima modificacion: 16-06-26 9:00 PM
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