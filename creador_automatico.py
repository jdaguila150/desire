import os
import time

from lector_pdf import extraer_texto_de_pdf, limpiar_texto_pdf, fragmentar_texto
from motor_ia import resumir_texto_a_json
from motor_nlp import crear_presentacion_desde_json

# =================================================================
# FASE 4 (NLP): EL PIPELINE COMPLETO (PDF -> IA -> PPTX)
# =================================================================

def procesar_documento_a_pptx(ruta_pdf, nombre_salida="Presentacion_Generada.pptx"):
    print("==================================================")
    print(" INICIANDO GENERADOR AUTOMÁTICO DE DIAPOSITIVAS ")
    print("==================================================")

    # 1. Extracción y Preprocesamiento
    texto_crudo = extraer_texto_de_pdf(ruta_pdf)
    if not texto_crudo:
        return

    texto_limpio = limpiar_texto_pdf(texto_crudo)
    
    # Como Gemini 2.5 Flash es muy potente, podemos enviarle bloques grandes
    # (1000 palabras con 100 de superposición)
    chunks = fragmentar_texto(texto_limpio, max_palabras=1000, superposicion=100)
    print(f"\n[INFO] Documento dividido en {len(chunks)} bloque(s) cognitivo(s).")

    # 2. El JSON Maestro (Aquí guardaremos todo)
    json_maestro = {
        "titulo_principal": "Resumen Automático",
        "subtitulo": f"Generado desde: {os.path.basename(ruta_pdf)}",
        "diapositivas": []
    }

    # 3. Procesamiento Cognitivo (Bucle LLM)
    for i, chunk in enumerate(chunks):
        print(f"\nProcesando bloque {i+1} de {len(chunks)} con Inteligencia Artificial...")
        
        # Opcional: Pausa de 2 segundos para no saturar la API gratuita de Google
        time.sleep(2) 
        
        resultado_json = resumir_texto_a_json(chunk)

        if resultado_json:
            # Si es el primer bloque, dejamos que la IA decida el Título Principal
            if i == 0 and "titulo_principal" in resultado_json:
                json_maestro["titulo_principal"] = resultado_json["titulo_principal"]
                if "subtitulo" in resultado_json:
                    json_maestro["subtitulo"] = resultado_json["subtitulo"]

            # Extraemos las diapositivas de este bloque y las sumamos a la lista maestra
            if "diapositivas" in resultado_json:
                json_maestro["diapositivas"].extend(resultado_json["diapositivas"])
                print(f" -> Se extrajeron {len(resultado_json['diapositivas'])} diapositivas de este bloque.")
        else:
            print(f"[ERROR] El bloque {i+1} falló y fue omitido.")

    # 4. Ensamblaje del PowerPoint
    total_diapositivas = len(json_maestro["diapositivas"])
    if total_diapositivas > 0:
        print(f"\n[ENSAMBLADOR] Construyendo PPTX con {total_diapositivas} diapositivas en total...")
        crear_presentacion_desde_json(json_maestro, nombre_salida)
        print("\n==================================================")
        print(" PROCESO FINALIZADO CON ÉXITO ")
        print("==================================================")
    else:
        print("\n[ERROR CRÍTICO] No se generó ninguna diapositiva válida. Revisa tu API o el documento.")

# =================================================================
# EJECUCIÓN DEL PIPELINE
# =================================================================
if __name__ == "__main__":
    # Cambia esto por el nombre de tu PDF real
    archivo_entrada = "../pinguino.pdf"
    archivo_salida = "Presentacion_Final.pptx"
    
    procesar_documento_a_pptx(archivo_entrada, archivo_salida)