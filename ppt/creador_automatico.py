import os
import time

from ppt.lector_pdf import extraer_texto_de_pdf, limpiar_texto_pdf, fragmentar_texto
from IA.motor_ia import resumir_texto_a_json
from IA.motor_nlp import crear_presentacion_desde_json
from IA.motor_imagenes import descargar_imagen_unsplash

# =================================================================
# FASE 4 (NLP): EL PIPELINE COMPLETO (PDF -> IA -> PPTX)
# =================================================================

def procesar_documento_a_pptx(ruta_pdf, nombre_salida="Presentacion_Generada.pptx"):
    print("==================================================")
    print(" INICIANDO GENERADOR AUTOMÁTICO DE DIAPOSITIVAS ")
    print("==================================================")

    texto_crudo = extraer_texto_de_pdf(ruta_pdf)
    if not texto_crudo: return
    texto_limpio = limpiar_texto_pdf(texto_crudo)
    
    chunks = fragmentar_texto(texto_limpio, max_palabras=1000, superposicion=100)
    print(f"\n[INFO] Documento dividido en {len(chunks)} bloque(s) cognitivo(s).")

    json_maestro = {
        "titulo_principal": "Resumen Automático",
        "subtitulo": f"Generado desde: {os.path.basename(ruta_pdf)}",
        "diapositivas": []
    }

    # Contador global para que las imágenes no se sobrescriban entre sí
    contador_imagenes = 1 

    for i, chunk in enumerate(chunks):
        print(f"\nProcesando bloque {i+1} de {len(chunks)} con Inteligencia Artificial...")
        time.sleep(2) 
        
        resultado_json = resumir_texto_a_json(chunk)

        if resultado_json:
            if i == 0 and "titulo_principal" in resultado_json:
                json_maestro["titulo_principal"] = resultado_json.get("titulo_principal", "")
                json_maestro["subtitulo"] = resultado_json.get("subtitulo", "")

            if "diapositivas" in resultado_json:
                # --- LA INTERCEPCIÓN DE IMÁGENES ---
                for diapo in resultado_json["diapositivas"]:
                    query = diapo.get("query_imagen", "")
                    
                    if query: # Si la IA sugirió una imagen
                        nombre_img = f"img_temp_{contador_imagenes}.jpg"
                        ruta_descargada = descargar_imagen_unsplash(query, nombre_img)
                        
                        if ruta_descargada:
                            # Inyectamos la ruta física en el diccionario para que python-pptx la encuentre
                            diapo["ruta_imagen_local"] = ruta_descargada
                            contador_imagenes += 1
                # -----------------------------------

                json_maestro["diapositivas"].extend(resultado_json["diapositivas"])
                print(f" -> Se extrajeron {len(resultado_json['diapositivas'])} diapositivas de este bloque.")
        else:
            print(f"[ERROR] El bloque {i+1} falló y fue omitido.")

    total_diapositivas = len(json_maestro["diapositivas"])
    if total_diapositivas > 0:
        print(f"\n[ENSAMBLADOR] Construyendo PPTX con {total_diapositivas} diapositivas en total...")
        # Adentro de esta función, python-pptx debe buscar 'diapo.get("ruta_imagen_local")'
        crear_presentacion_desde_json(json_maestro, nombre_salida) 
        print("\n==================================================")
        print(" PROCESO FINALIZADO CON ÉXITO ")
        print("==================================================")
    else:
        print("\n[ERROR CRÍTICO] No se generó ninguna diapositiva válida.")



        
# =================================================================
# EJECUCIÓN DEL PIPELINE
# =================================================================
if __name__ == "__main__":
    # Cambia esto por el nombre de tu PDF real
    archivo_entrada = "../pinguino.pdf"
    archivo_salida = "Presentacion_Final.pptx"
    
    procesar_documento_a_pptx(archivo_entrada, archivo_salida)