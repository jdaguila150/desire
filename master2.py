import cv2
import numpy as np
import time
import threading
import mediapipe as mp
import os
import urllib.request
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import traceback

# =================================================================
# IMPORTACIÓN DE MÓDULOS DE PROYECTO
# =================================================================
import vision.config as cfg 
from vision.controlador_os import presionar_tecla, VK_RIGHT, VK_LEFT
from ppt.motor_ppt_envivo import inyectar_diapositiva_en_vivo
from IA.motor_audio import iniciar_oido_en_segundo_plano, buzon_de_voz
from IA.motor_ia import resumir_texto_a_json
from ppt.lector_pdf import extraer_texto_de_pdf, limpiar_texto_pdf
from IA.motor_imagenes import descargar_imagen_unsplash

def descargar_modelo_si_no_existe():
    ruta_modelo = 'hand_landmarker.task'
    if not os.path.exists(ruta_modelo):
        print("\n[SISTEMA] Descargando modelo neuronal de Google (solo ocurrirá esta vez)...")
        url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
        urllib.request.urlretrieve(url, ruta_modelo)
        print("[SISTEMA] Modelo descargado con éxito.\n")
    return ruta_modelo

def procesar_comando_voz_en_hilo(comando_voz, contexto_pdf):
    print(f"\n[HILO IA] Procesando tu petición: '{comando_voz}'...")
    
    # try:
    #     prompt_combinado = f"INSTRUCCIÓN: {comando_voz}\nCONTEXTO:\n{contexto_pdf}"
    #     json_generado = resumir_texto_a_json(prompt_combinado)
        
    #     if json_generado and "diapositivas" in json_generado and len(json_generado["diapositivas"]) > 0:
    #         diapo = json_generado["diapositivas"][0]
    #         titulo = diapo.get("titulo", "Nuevo Tema")
    #         puntos = diapo.get("puntos", [])
    #         query_visual = diapo.get("query_imagen", "")

            
    #         ruta_foto = None
    #         if query_visual:
    #             print(f"[HILO IA] El modelo solicitó una imagen sobre: '{query_visual}'")
    #             # Descargamos la imagen antes de inyectar
    #             ruta_relativa = descargar_imagen_unsplash(query_visual)
    #             if ruta_relativa:
    #                 # 2. VITAL PARA POWERPOINT: Convertimos la ruta 'assets/foto.jpg' 
    #                 # a una ruta completa 'C:\Users\...\assets\foto.jpg'
    #                 ruta_foto = os.path.abspath(ruta_relativa)
    #             print("\n[INYECTOR] Disparando a PowerPoint...")
    #         print("\n[INYECTOR] ¡Datos listos! Disparando a PowerPoint...")
            
    #         # Pasamos la ruta de la foto (puede ser None si no hubo query o si falló la descarga)
    #         inyectar_diapositiva_en_vivo(titulo, puntos, ruta_foto)
            
    #     else:
    #         print("\n[ALERTA] La IA no pudo generar el formato correcto.")
            
    # except Exception as e:
    #     import traceback
    #     print("\n❌ FATAL ERROR EN EL HILO DE IA ❌")
    #     print(traceback.format_exc())


    try:
        # 1. INGENIERÍA DE PROMPTS: Le damos las reglas del juego a Gemini
        reglas_negocio = """
        REGLA DE CANTIDAD:
        - Si el usuario dice "diapositiva", "siguiente", o pide un tema muy específico, genera EXACTAMENTE UNA (1) diapositiva.
        - Si el usuario dice "generar presentación", "crear el bloque", "todo el tema", genera MÚLTIPLES diapositivas que cubran la información.
        """
        
        prompt_combinado = f"{reglas_negocio}\nINSTRUCCIÓN: {comando_voz}\nCONTEXTO:\n{contexto_pdf}"
        json_generado = resumir_texto_a_json(prompt_combinado)
        
        # 2. EL BUCLE ITERATIVO (Soporta 1 o N diapositivas)
        if json_generado and "diapositivas" in json_generado and len(json_generado["diapositivas"]) > 0:
            
            total_diapos = len(json_generado["diapositivas"])
            print(f"\n[HILO IA] La IA interpretó tu intención y generará {total_diapos} diapositiva(s).")
            
            # Recorremos cada elemento que nos haya devuelto Gemini
            for index, diapo in enumerate(json_generado["diapositivas"]):
                print(f"\n--- Procesando Diapositiva {index + 1} de {total_diapos} ---")
                
                titulo = diapo.get("titulo", "Nuevo Tema")
                puntos = diapo.get("puntos", [])
                query_visual = diapo.get("query_imagen", "")
                
                ruta_foto = None
                if query_visual:
                    print(f"[API VISUAL] Solicitando imagen de: '{query_visual}'")
                    ruta_relativa = descargar_imagen_unsplash(query_visual)
                    
                    if ruta_relativa:
                        ruta_foto = os.path.abspath(ruta_relativa)
                
                print(f"[INYECTOR] Escribiendo en PowerPoint: {titulo}...")
                inyectar_diapositiva_en_vivo(titulo, puntos, ruta_foto)
                
                # VITAL: Pausa de seguridad para el sistema operativo
                # PowerPoint (API COM) puede colapsar si le inyectamos 5 fotos en el mismo milisegundo.
                if total_diapos > 1:
                    time.sleep(1.5)
            
            print("\n[SISTEMA] ¡Ciclo de generación finalizado con éxito!")
            
        else:
            print("\n[ALERTA] La IA no pudo generar el formato correcto.")
            
    except Exception as e:
        import traceback
        print("\n❌ FATAL ERROR EN EL HILO DE IA ❌")
        print(traceback.format_exc())


def iniciar_sistema_maestro():
    print("==========================================================")
    print(" Desire - VERSIÓN ENTERPRISE (VISIÓN + IA MULTIMODAL) ")
    print("==========================================================")

    # 1. Preparar el archivo neuronal
    ruta_modelo = descargar_modelo_si_no_existe()

    # 2. Cargar conocimiento base
    print("\n[SISTEMA] Leyendo base de datos local (PDF)...")
    texto_crudo = extraer_texto_de_pdf("Documento_ Sistema_Desire.pdf") 
    texto_base = limpiar_texto_pdf(texto_crudo) if texto_crudo else ""

    # 3. Iniciar hilos secundarios (Audio)
    print("[SISTEMA] Encendiendo el módulo de escucha en segundo plano...")
    detener_microfono = iniciar_oido_en_segundo_plano()
    
    # 4. Iniciar hardware visual
    cap = cv2.VideoCapture(0)
    
    # ---------------------------------------------------------
    # INICIALIZACIÓN DE MEDIAPIPE (TASKS API)
    # ---------------------------------------------------------
    base_options = python.BaseOptions(model_asset_path=ruta_modelo)
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=1,
        min_hand_detection_confidence=0.7,
        min_hand_presence_confidence=0.7,
        min_tracking_confidence=0.7
    )
    detector = vision.HandLandmarker.create_from_options(options)
    
    prev_x, prev_y = None, None
    ultimo_tiempo_gesto = 0
    estado_actual = "ACTIVO" 
    estado_ia = "" # Variable para mostrar un texto en pantalla si la IA está pensando

    print("[SISTEMA EN LÍNEA] Todo listo. Presiona 'q' para salir.")

    while True:
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        
        tecla = cv2.waitKey(1) & 0xFF
        
        # =========================================================
        # 1. ESCUCHA DE COMANDOS DE VOZ (EL ESLABÓN PERDIDO)
        # =========================================================
        if not buzon_de_voz.empty():
            comando = buzon_de_voz.get()
            estado_ia = "IA Pensando..." # Mostramos feedback visual
            threading.Thread(target=procesar_comando_voz_en_hilo, args=(comando, texto_base)).start()
            
        # Limpiar el mensaje de la IA de la pantalla después de un rato (opcional)
        if estado_ia != "":
            cv2.putText(frame, estado_ia, (120, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)

        # =========================================================
        # 2. PROCESAMIENTO VISUAL
        # =========================================================
        resultados = detector.detect(mp_image)
        
        if resultados.hand_landmarks:
            hand_landmarks = resultados.hand_landmarks[0] 
            h, w, c = frame.shape
            
            # --- DIBUJADO DE LA MALLA MANUALMENTE ---
            conexiones = [(0,1),(1,2),(2,3),(3,4), (0,5),(5,6),(6,7),(7,8), (5,9),(9,10),(10,11),(11,12), (9,13),(13,14),(14,15),(15,16), (13,17),(17,18),(18,19),(19,20), (0,17)]
            
            for inicio, fin in conexiones:
                x1, y1 = int(hand_landmarks[inicio].x * w), int(hand_landmarks[inicio].y * h)
                x2, y2 = int(hand_landmarks[fin].x * w), int(hand_landmarks[fin].y * h)
                cv2.line(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
            
            for punto in hand_landmarks:
                x, y = int(punto.x * w), int(punto.y * h)
                cv2.circle(frame, (x, y), 5, (0, 255, 255), -1)

            # --- LÓGICA DE GESTOS (Anatomía) ---
            puntas = [8, 12, 16, 20]
            nudillos = [6, 10, 14, 18]
            dedos_levantados = 0
            
            for punta, nudillo in zip(puntas, nudillos):
                if hand_landmarks[punta].y < hand_landmarks[nudillo].y:
                    dedos_levantados += 1

            # Puntero inercial en el nudillo central (Landmark 9)
            cx = int(hand_landmarks[9].x * w)
            cy = int(hand_landmarks[9].y * h)

            # --- MÁQUINA DE ESTADOS ---
            if dedos_levantados <= 1:
                estado_actual = "PAUSA"
                cv2.putText(frame, "[ PAUSADO ]", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.circle(frame, (cx, cy), 15, (0, 0, 255), -1) 
                prev_x, prev_y = None, None

            elif dedos_levantados >= 3:
                estado_actual = "ACTIVO"
                cv2.putText(frame, "[ NAVEGACION ]", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 15, (0, 255, 0), -1) 

                tiempo_actual = time.time()
                if prev_x is None or prev_y is None:
                    prev_x, prev_y = cx, cy

                if (tiempo_actual - ultimo_tiempo_gesto) > cfg.COOLDOWN_GESTO:
                    delta_x = cx - prev_x
                    if delta_x > cfg.UMBRAL_SWIPE:
                        print("--> SIGUIENTE")
                        presionar_tecla(VK_RIGHT)
                        ultimo_tiempo_gesto = tiempo_actual
                    elif delta_x < -cfg.UMBRAL_SWIPE:
                        print("<-- ANTERIOR")
                        presionar_tecla(VK_LEFT)
                        ultimo_tiempo_gesto = tiempo_actual
                        
                prev_x = int(prev_x * 0.7 + cx * 0.3)
                prev_y = int(prev_y * 0.7 + cy * 0.3)
        else:
            prev_x, prev_y = None, None

        cv2.imshow("Desire - Master Control", frame)
        if tecla == ord('q'):
            break

    print("\n[SISTEMA] Apagando hardware y liberando memoria...")
    detener_microfono(wait_for_stop=False) # <--- AHORA SÍ APAGAMOS EL MICRÓFONO
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    iniciar_sistema_maestro()