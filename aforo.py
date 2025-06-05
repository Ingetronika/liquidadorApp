import math
import requests
from datos import DataLoader

class CalculadoraTanque:
    def __init__(self,altura_inicial,volumen_bruto_recibido,tanque):
        self.altura_inicial=altura_inicial
        self.volumen_bruto_recibido=volumen_bruto_recibido
        self.tanque=tanque

    @staticmethod
    def obtener_valor_desde_url(archivo_json, clave_busqueda):
        url = f"https://bucketunir2025.s3.amazonaws.com/{archivo_json}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # Convertir clave a string para evitar problemas con claves numéricas
            clave_str = str(clave_busqueda)

            if clave_str in data:
                return data[clave_str]
            else:
                return f"La clave '{clave_str}' no existe en el JSON."

        except Exception as e:
            return f"Error al obtener o procesar el archivo: {str(e)}"    
    def mostrar_volumen_prueba(self,diccionario,medida):
        return diccionario.get(str(medida))
    
    def mostrar_altura_1(self, volumen, diccionario):
        if volumen == 0:
            return 0.0

        # Inicializar variables para el mínimo y la clave correspondiente
        clave_cercana = None
        diferencia_minima = float('inf')

        for key, value in diccionario.items():
            diferencia = abs(value - volumen)
            if diferencia < diferencia_minima:
                diferencia_minima = diferencia
                clave_cercana = key

        if clave_cercana is None:
            raise ValueError(f"No se encontró una altura correspondiente al volumen {volumen}.")

        return (clave_cercana)

            


   


