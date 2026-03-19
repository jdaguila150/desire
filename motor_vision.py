import numpy as np

# =================================================================
# FILTROS MORFOLÓGICOS DESDE CERO (Procesamiento Digital de Imágenes)
# =================================================================

def erosionar_numpy(img, k=5):
    """ Filtro Mínimo: Reduce las manchas blancas """
    pad = k // 2
    # Acolchamos los bordes con blanco para no erosionar los límites de la pantalla
    padded = np.pad(img, pad_width=pad, mode='constant', constant_values=255)
    out = np.full_like(img, 255)
    
    # Desplazamos la imagen en las 25 direcciones del kernel
    for dy in range(k):
        for dx in range(k):
            out = np.minimum(out, padded[dy:dy+img.shape[0], dx:dx+img.shape[1]])
    return out

def dilatar_numpy(img, k=5):
    """ Filtro Máximo: Expande las manchas blancas """
    pad = k // 2
    # Acolchamos los bordes con negro
    padded = np.pad(img, pad_width=pad, mode='constant', constant_values=0)
    out = np.zeros_like(img)
    
    for dy in range(k):
        for dx in range(k):
            out = np.maximum(out, padded[dy:dy+img.shape[0], dx:dx+img.shape[1]])
    return out

def apertura_numpy(img, k=5):
    """ Apertura: Quita la 'Sal' del fondo """
    # Primero erosiona (borra la sal), luego dilata (recupera el tamaño de la mano)
    return dilatar_numpy(erosionar_numpy(img, k), k)

def cierre_numpy(img, k=5):
    """ Cierre: Quita la 'Pimienta' de la mano """
    # Primero dilata (rellena agujeros), luego erosiona (recupera el tamaño de la mano)
    return erosionar_numpy(dilatar_numpy(img, k), k)
# =================================================================

# =================================================================
# MÓDULO DE VISIÓN: PROCESAMIENTO DE COLOR
# =================================================================

def obtener_mascara_hsv(frame, h_min, h_max, s_min, v_min, k_morfologia=5):
    """
    Convierte un frame BGR a HSV mediante álgebra de matrices, aplica los 
    umbrales deseados y devuelve una máscara binaria limpia de ruido.
    """
    # 1. Normalizar BGR al rango [0, 1.0]
    b = frame[:,:,0] / 255.0
    g = frame[:,:,1] / 255.0
    r = frame[:,:,2] / 255.0

    cmax = np.maximum(np.maximum(r, g), b)
    cmin = np.minimum(np.minimum(r, g), b)
    diff = cmax - cmin

    # 2. Cálculo Vectorizado de Hue (Tono) en grados [0, 360]
    h = np.zeros_like(cmax)
    idx = diff != 0
    
    r_max = (cmax == r) & idx
    h[r_max] = (60 * ((g[r_max] - b[r_max]) / diff[r_max]) + 360) % 360
    
    g_max = (cmax == g) & idx
    h[g_max] = (60 * ((b[g_max] - r[g_max]) / diff[g_max]) + 120) % 360
    
    b_max = (cmax == b) & idx
    h[b_max] = (60 * ((r[b_max] - g[b_max]) / diff[b_max]) + 240) % 360

    # 3. Cálculo de Saturation y Value
    s = np.zeros_like(cmax)
    s[cmax != 0] = diff[cmax != 0] / cmax[cmax != 0]
    v = cmax

    # 4. Aplicación de la Máscara Lógica
    mascara_logica = (h >= h_min) & (h <= h_max) & (s >= s_min) & (v >= v_min)
    binary_mask = np.zeros_like(h, dtype=np.uint8)
    binary_mask[mascara_logica] = 255

    # 5. Limpieza de Ruido (Filtros Morfológicos)
    binary_mask = apertura_numpy(binary_mask, k=k_morfologia)
    binary_mask = cierre_numpy(binary_mask, k=k_morfologia)

    return binary_mask