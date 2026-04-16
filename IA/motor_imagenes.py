import os
import requests
from dotenv import load_dotenv

load_dotenv()

# =================================================================
# MOTOR DE DESCARGA VISUAL (UNSPLASH API)
# =================================================================

# Tu llave pública (Client ID) de Unsplash
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
if not UNSPLASH_ACCESS_KEY:
    raise ValueError("[ALERTA] No se encontró la llave de Unsplash en el archivo .env")

def descargar_imagen_unsplash(query, carpeta_destino="assets"):
    
    """
    Busca una imagen en Unsplash usando la palabra clave de la IA,
    la descarga en formato horizontal y devuelve la ruta local.
    """
    if not query:
        return None

    # Creamos la carpeta 'assets' si no existe
    if not os.path.exists(carpeta_destino):
        os.makedirs(carpeta_destino)

    # Limpiamos el nombre para guardarlo en Windows/Mac de forma segura
    nombre_archivo = query.replace(" ", "_").lower() + ".jpg"
    ruta_completa = os.path.join(carpeta_destino, nombre_archivo)

    # SISTEMA DE CACHÉ: Si la imagen ya existe, no gastamos peticiones a la API
    if os.path.exists(ruta_completa):
        return ruta_completa

    print(f"\n[🖼️ BUSCADOR VISUAL] Buscando fotografía de: '{query}'...")
    
    url_busqueda = "https://api.unsplash.com/search/photos"
    parametros = {
        "query": query,
        "client_id": UNSPLASH_ACCESS_KEY,
        "per_page": 1,              # Solo queremos el primer y mejor resultado
        "orientation": "landscape"  # Perfecto para presentaciones 16:9
    }

    try:
        respuesta = requests.get(url_busqueda, params=parametros)
        
        if respuesta.status_code == 200:
            datos = respuesta.json()
            if datos["results"]:
                # Sacamos la URL de la imagen en resolución 'regular'
                url_imagen = datos["results"][0]["urls"]["regular"]
                
                # Descargamos los bytes de la imagen
                print(f"[🖼️ DESCARGANDO] Guardando en disco...")
                img_data = requests.get(url_imagen).content
                
                with open(ruta_completa, 'wb') as archivo:
                    archivo.write(img_data)
                
                return ruta_completa
            else:
                print(f"[⚠️ ALERTA VISUAL] No se encontraron imágenes para '{query}'.")
                return None
        else:
            print(f"[❌ ERROR UNSPLASH] Código: {respuesta.status_code}")
            return None
            
    except Exception as e:
        print(f"[❌ ERROR DE RED] Fallo al conectar con Unsplash: {e}")
        return None