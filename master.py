import cv2
import numpy as np
import time
import threading

# =================================================================
# IMPORTACIÓN DE TUS MÓDULOS DE INGENIERÍA
# =================================================================
import config as cfg 
from motor_vision import obtener_mascara_hsv
from motor_ml import cargar_memoria, extraer_caracteristicas, predecir_gesto
from controlador_os import abrir_presentacion, presionar_tecla, VK_RIGHT, VK_LEFT, VK_ESCAPE
from motor_ppt_envivo import inyectar_diapositiva_en_vivo
from motor_audio import iniciar_oido_en_segundo_plano, buzon_de_voz
from motor_ia import resumir_texto_a_json
from lector_pdf import extraer_texto_de_pdf, limpiar_texto_pdf

def procesar_comando_voz_en_hilo(comando_voz, contexto_pdf):
    """
    Esta función se ejecuta en un Hilo 3 temporal para que la llamada 
    a Gemini no congele la cámara ni un solo segundo.
    """
    print(f"\n[IA TRABAJANDO] Procesando tu petición: '{comando_voz}'...")
    
    # Juntamos lo que pediste con la información del PDF (RAG - Retrieval-Augmented Generation)
    # Solo tomamos los primeros 3000 caracteres del PDF para que la IA responda ultra rápido
    prompt_combinado = f"""
    INSTRUCCIÓN DEL USUARIO: {comando_voz}
    
    BASE DE CONOCIMIENTO (Usa esto como referencia):
    {contexto_pdf[:3000]}
    """
    
    # Llamamos a Gemini
    json_generado = resumir_texto_a_json(prompt_combinado)
    
    if json_generado and "diapositivas" in json_generado and len(json_generado["diapositivas"]) > 0:
        # Tomamos la primera diapositiva generada
        diapo = json_generado["diapositivas"][0]
        titulo = diapo.get("titulo", "Nuevo Tema")
        puntos = diapo.get("puntos", [])
        
        print("\n[INYECTOR] ¡JSON recibido! Disparando a PowerPoint...")
        inyectar_diapositiva_en_vivo(titulo, puntos)
    else:
        print("\n[ALERTA] La IA no pudo generar el formato correcto o no entendió el comando.")

def iniciar_sistema_maestro():
    print("==========================================================")
    print(" Desire - SUITE COMPLETA (VISIÓN + NLP + IA) ")
    print("==========================================================")

    # 1. Cargar Memoria Muscular (KNN)
    etiquetas, memoria_knn = cargar_memoria(cfg.ARCHIVO_DATASET)
    if etiquetas is None: return

    # 2. Cargar Conocimiento Base (PDF)
    print("\n[SISTEMA] Leyendo base de datos local (PDF)...")
    texto_crudo = extraer_texto_de_pdf("mujer.pdf") # Cambia al nombre de tu PDF
    texto_base = limpiar_texto_pdf(texto_crudo) if texto_crudo else "Sin contexto local."

    # 3. Encender el Oído Asíncrono
    detener_microfono = iniciar_oido_en_segundo_plano()

    # 4. Inicializar Hardware (Cámara)
    cap = cv2.VideoCapture(0)
    prev_x, prev_y = None, None
    ultimo_tiempo_gesto = 0
    estado_actual = "ACTIVO"

    print("\n[SISTEMA EN LÍNEA] Todo listo. Presiona 'q' en la cámara para salir.")

    # =================================================================
    # BUCLE PRINCIPAL (Hilo 1 - Visión)
    # =================================================================
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.flip(frame, 1)
        small_frame = cv2.resize(frame, (400, 300))
        
        # --- A. REVISAR SI HAY ÓRDENES DE VOZ PENDIENTES ---
        if not buzon_de_voz.empty():
            comando = buzon_de_voz.get()
            # Lanzamos la petición a la IA en un hilo separado (Hilo 3 temporal)
            # Así la cámara sigue fluida mientras Gemini "piensa"
            hilo_ia = threading.Thread(target=procesar_comando_voz_en_hilo, args=(comando, texto_base))
            hilo_ia.start()
            
            # Feedback visual
            cv2.putText(small_frame, "Generando IA...", (150, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)

        # --- B. MOTOR DE VISIÓN Y MACHINE LEARNING ---
        mascara = obtener_mascara_hsv(small_frame, cfg.H_MIN, cfg.H_MAX, cfg.S_MIN, cfg.V_MIN)
        coords = np.argwhere(mascara == 255)
        
        if coords.size > 400: 
            punto_actual, caja = extraer_caracteristicas(coords)
            
            if punto_actual is not None:
                gesto = predecir_gesto(punto_actual, memoria_knn, etiquetas)
                x_min, y_min, x_max, y_max = caja
                cy, cx = coords.mean(axis=0).astype(int)

                # ESTADO: PUÑO (PAUSA)
                if gesto == 1:
                    estado_actual = "PAUSA"
                    cv2.rectangle(small_frame, (x_min, y_min), (x_max, y_max), (0, 0, 255), 2)
                    cv2.putText(small_frame, "[ PAUSADO ]", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    prev_x, prev_y = None, None

                # ESTADO: MANO ABIERTA (NAVEGACIÓN)
                elif gesto == 2:
                    estado_actual = "ACTIVO"
                    cv2.rectangle(small_frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                    cv2.circle(small_frame, (cx, cy), 8, (255, 0, 0), -1)
                    cv2.putText(small_frame, "[ NAVEGACION ]", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                    # Controlador de Navegación Gestual
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

        cv2.imshow("Desire - Master Control", small_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Apagar todos los sistemas al salir
    print("\n[SISTEMA] Apagando hardware y liberando memoria...")
    detener_microfono(wait_for_stop=False)
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    iniciar_sistema_maestro()