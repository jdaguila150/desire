import numpy as np
import os

# =================================================================
# MÓDULO DE MACHINE LEARNING: K-VECINOS MÁS CERCANOS (KNN)
# =================================================================

def cargar_memoria(ruta_dataset):
    """
    Lee el archivo CSV con los gestos guardados y lo convierte en matrices 
    matemáticas de NumPy para un procesamiento ultra rápido.
    
    Retorna:
    - etiquetas: Array 1D con las clases (1 para Puño, 2 para Mano Abierta).
    - caracteristicas: Matriz 2D con el [Aspect Ratio, Densidad] de cada ejemplo.
    """
    if not os.path.exists(ruta_dataset):
        print(f"[ERROR ML] No se encontró la memoria (Dataset) en: {ruta_dataset}")
        return None, None
    
    # loadtxt es la forma nativa de NumPy para leer datos estructurados
    datos = np.loadtxt(ruta_dataset, delimiter=',', skiprows=1)
    
    if datos.size == 0:
        print("[ERROR ML] El dataset está vacío.")
        return None, None

    etiquetas = datos[:, 0]        # Primera columna: El ID del gesto
    caracteristicas = datos[:, 1:] # Columnas restantes: Los datos matemáticos
    
    print(f"[MOTOR ML] Memoria cargada exitosamente: {len(etiquetas)} patrones listos.")
    return etiquetas, caracteristicas

def extraer_caracteristicas(coords):
    """
    Toma las coordenadas de la máscara binaria, calcula la caja delimitadora
    y extrae las características geométricas principales de la mano.
    
    Retorna:
    - punto_actual: Un array [aspect_ratio, densidad] listo para predecir.
    - caja: Tupla (x_min, y_min, x_max, y_max) para dibujar en la interfaz.
    """
    # 1. Encontrar los extremos geométricos
    y_min, x_min = coords.min(axis=0)
    y_max, x_max = coords.max(axis=0)
    
    # 2. Calcular dimensiones de la Caja Delimitadora (Bounding Box)
    w = x_max - x_min
    h_box = y_max - y_min
    
    # Prevención de errores por divisiones entre cero
    if w <= 0 or h_box <= 0:
        return None, None
        
    # 3. Extraer Características (Feature Engineering)
    aspect_ratio = w / h_box
    area_mancha = coords.shape[0] # Cantidad de píxeles blancos reales
    area_caja = w * h_box
    densidad = area_mancha / area_caja
    
    punto_actual = np.array([aspect_ratio, densidad])
    caja = (x_min, y_min, x_max, y_max)
    
    return punto_actual, caja

def predecir_gesto(punto_actual, caracteristicas_memoria, etiquetas):
    """
    El algoritmo clasificador KNN vectorizado.
    Calcula la distancia Euclidiana simultánea hacia todos los puntos de la memoria.
    
    Retorna:
    - prediccion: La etiqueta numérica del gesto más similar (ej. 1 o 2).
    """
    # Álgebra lineal en acción: (X_i - X_0)^2 + (Y_i - Y_0)^2
    distancias = np.sqrt(np.sum((caracteristicas_memoria - punto_actual)**2, axis=1))
    
    # Encontrar el índice matemático con la distancia más corta
    indice_mas_cercano = np.argmin(distancias)
    
    # Retornar la etiqueta correspondiente a ese vecino cercano
    prediccion = etiquetas[indice_mas_cercano]
    
    return prediccion