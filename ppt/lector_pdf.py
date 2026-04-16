import pdfplumber
import os

# =================================================================
# FASE 4 (NLP): EXTRACTOR DE TEXTO CRUDO
# =================================================================

def extraer_texto_de_pdf(ruta_pdf):
    """
    Abre un archivo PDF, itera a través de sus páginas y extrae 
    el texto crudo, preservando la separación por párrafos.
    """
    if not os.path.exists(ruta_pdf):
        print(f"[ERROR] No se encontró el archivo: {ruta_pdf}")
        return None

    texto_total = ""
    print(f"Abriendo documento: {ruta_pdf} ...\n")

    try:
        # Usamos 'with' para asegurar que el archivo se cierre correctamente de la memoria
        with pdfplumber.open(ruta_pdf) as pdf:
            total_paginas = len(pdf.pages)
            print(f"El documento tiene {total_paginas} páginas.\n")

            # Iterar página por página
            for numero_pagina, pagina in enumerate(pdf.pages):
                # Extraer el texto de la página actual
                texto_pagina = pagina.extract_text()
                
                if texto_pagina:
                    # Agregamos un separador para saber dónde empieza cada página
                    texto_total += f"\n--- INICIO DE PÁGINA {numero_pagina + 1} ---\n"
                    texto_total += texto_pagina
                    texto_total += f"\n--- FIN DE PÁGINA {numero_pagina + 1} ---\n"
                else:
                    print(f"[AVISO] La página {numero_pagina + 1} parece estar vacía o es una imagen escaneada sin texto.")

        return texto_total

    except Exception as e:
        print(f"[ERROR] Ocurrió un problema al leer el PDF: {e}")
        return None


import re

# =================================================================
# FASE 4 (NLP): LIMPIEZA Y FRAGMENTACIÓN (CHUNKING)
# =================================================================

def limpiar_texto_pdf(texto_crudo):
    """
    Toma el texto sucio del PDF, elimina los saltos de línea artificiales
    y quita espacios dobles para dejar párrafos continuos y legibles.
    """
    if not texto_crudo:
        return ""
    
    # Expresión regular: Encuentra cualquier bloque de espacios, tabs o saltos de línea
    # y lo reemplaza por un solo espacio en blanco.
    texto_limpio = re.sub(r'\s+', ' ', texto_crudo)
    
    return texto_limpio.strip()

def fragmentar_texto(texto_limpio, max_palabras=500, superposicion=50):
    """
    Corta el texto en fragmentos (chunks) más pequeños que una IA pueda digerir.
    Utiliza una "ventana deslizante" (overlap) para no perder el contexto entre cortes.
    """
    # Convertimos todo el texto enorme en una lista de palabras individuales
    palabras = texto_limpio.split()
    fragmentos = []
    
    # Índice para recorrer la lista de palabras
    i = 0
    
    while i < len(palabras):
        # Tomamos un bloque de palabras (ej. de la palabra 0 a la 500)
        bloque = palabras[i : i + max_palabras]
        
        # Volvemos a unir ese bloque en un solo texto (string) y lo guardamos
        fragmentos.append(" ".join(bloque))
        
        # Avanzamos el índice, pero retrocedemos un poco (superposición)
        # para que el siguiente bloque empiece un poco antes de donde terminó este.
        i += (max_palabras - superposicion)
        
    return fragmentos

# =================================================================
# PRUEBA DEL PASO 1 Y 2 UNIDOS
# =================================================================
if __name__ == "__main__":
    archivo_prueba = "mi_documento.pdf" # El PDF que usamos en el paso 1
    
    # texto_crudo = extraer_texto_de_pdf(archivo_prueba)
    
    # usaremos un texto de relleno largo si no existe el extractor a la mano:
    texto_crudo = "Este es un texto\nde prueba.\n   Tiene muchos espacios    y saltos de linea feos que arruinan la lectura de la IA. " * 100
    
    print("--- INICIANDO PROCESAMIENTO ---")
    
    # 2. Limpiar
    texto_pulido = limpiar_texto_pdf(texto_crudo)
    print(f"\n[OK] Texto limpiado. Total de palabras: {len(texto_pulido.split())}")
    
    # 3. Fragmentar (Chunks de 50 palabras con 10 de superposición para probar)
    chunks = fragmentar_texto(texto_pulido, max_palabras=50, superposicion=10)
    
    print(f"[OK] El texto se dividió en {len(chunks)} fragmentos matemáticos.")
    print("\n--- MUESTRA DEL FRAGMENTO 1 ---")
    print(chunks[0])
    
    print("\n--- MUESTRA DEL FRAGMENTO 2 (Nota cómo se repite el final del 1) ---")
    if len(chunks) > 1:
        print(chunks[1])

