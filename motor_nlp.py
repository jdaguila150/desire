from pptx import Presentation
import os

# =================================================================
# FASE 4 (NLP): ENSAMBLADOR DE DIAPOSITIVAS (POWERPOINT)
# =================================================================

def crear_presentacion_desde_json(datos_json, nombre_archivo="Presentacion_Generada.pptx"):
    """
    Toma un diccionario estructurado (la salida de Gemini)
    y construye un archivo de PowerPoint (.pptx) real.
    """
    print(f"\n[ENSAMBLADOR] Iniciando la creación del archivo: {nombre_archivo}")
    
    # 1. Crear el objeto base de la presentación
    prs = Presentation()

    # 2. Crear la Diapositiva de Título (Diseño 0)
    slide_layout_titulo = prs.slide_layouts[0]
    slide_titulo = prs.slides.add_slide(slide_layout_titulo)
    
    # Asignar textos al título y subtítulo
    titulo = slide_titulo.shapes.title
    subtitulo = slide_titulo.placeholders[1]
    
    # Usamos .get() por seguridad, por si la IA olvidó generar la llave "titulo_principal"
    titulo.text = datos_json.get("titulo_principal", "Presentación Generada por IA")
    subtitulo.text = datos_json.get("subtitulo", "Resumen Automático")

    # 3. Iterar sobre las diapositivas de contenido (Diseño 1: Título y Objetos)
    slide_layout_contenido = prs.slide_layouts[1]

    # Extraer la lista de diapositivas del JSON
    lista_diapositivas = datos_json.get("diapositivas", [])
    
    for i, diapo_data in enumerate(lista_diapositivas):
        slide = prs.slides.add_slide(slide_layout_contenido)
        
        # Asignar el título de la diapositiva
        titulo_shape = slide.shapes.title
        titulo_shape.text = diapo_data.get("titulo", f"Diapositiva {i+1}")
        
        # Asignar los puntos (bullet points) al cuerpo del texto
        body_shape = slide.placeholders[1]
        tf = body_shape.text_frame
        
        lista_puntos = diapo_data.get("puntos", [])
        
        for j, punto in enumerate(lista_puntos):
            if j == 0:
                # El primer punto se asigna directamente al primer párrafo (que ya existe por defecto)
                tf.text = punto
            else:
                # Los siguientes se añaden como nuevos párrafos (viñetas)
                p = tf.add_paragraph()
                p.text = punto
                p.level = 0 # Nivel de indentación base

    # 4. Guardar el archivo en el disco duro
    ruta_guardado = os.path.join(os.getcwd(), nombre_archivo)
    
    try:
        prs.save(ruta_guardado)
        print(f"[ENSAMBLADOR] ¡Éxito! Presentación guardada correctamente en:\n -> {ruta_guardado}")
        return ruta_guardado
    except PermissionError:
        print(f"[ERROR CRÍTICO] No se pudo guardar. Asegúrate de que el archivo '{nombre_archivo}' no esté abierto actualmente en PowerPoint.")
        return None

# =================================================================
# PRUEBA UNITARIA RÁPIDA (Opcional)
# =================================================================
if __name__ == "__main__":
    # Datos de prueba para verificar que python-pptx está funcionando bien
    datos_prueba = {
        "titulo_principal": "Prueba del Motor NLP",
        "subtitulo": "Sistema de Ensamblaje Funcional",
        "diapositivas": [
            {
                "titulo": "¿Funciona el código?",
                "puntos": ["Sí, los paquetes se instalaron correctamente.", "El archivo .pptx se generó sin errores."]
            }
        ]
    }
    crear_presentacion_desde_json(datos_prueba, "Prueba_Ensamblador.pptx")