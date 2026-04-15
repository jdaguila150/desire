import cv2
import numpy as np
import time
import threading

# =================================================================
# IMPORTACIÓN DE MÓDULOS
# =================================================================
import vision.config as cfg 
from vision.calibrador_vision import obtener_limites_dinamicos # <--- VITAL PARA EL DÍA DE LA PRESENTACIÓN
from vision.motor_ml import cargar_memoria, predecir_gesto
from vision.controlador_os import presionar_tecla, VK_RIGHT, VK_LEFT
from ppt.motor_ppt_envivo import inyectar_diapositiva_en_vivo
from IA.motor_audio import iniciar_oido_en_segundo_plano, buzon_de_voz
from IA.motor_ia import resumir_texto_a_json
from ppt.lector_pdf import extraer_texto_de_pdf, limpiar_texto_pdf

def procesar_comando_voz_en_hilo(comando_voz, contexto_pdf):
    print(f"\n[IA TRABAJANDO] Procesando tu petición: '{comando_voz}'...")
    prompt_combinado = f"INSTRUCCIÓN: {comando_voz}\nCONTEXTO:\n{contexto_pdf[:3000]}"
    json_generado = resumir_texto_a_json(prompt_combinado)
    
    if json_generado and "diapositivas" in json_generado and len(json_generado["diapositivas"]) > 0:
        diapo = json_generado["diapositivas"][0]
        print("\n[INYECTOR] ¡JSON recibido! Disparando a PowerPoint...")
        inyectar_diapositiva_en_vivo(diapo.get("titulo", "Nuevo Tema"), diapo.get("puntos", []))
    else:
        print("\n[ALERTA] La IA no pudo generar el formato correcto.")

def iniciar_sistema_maestro():
    print("==========================================================")
    print(" Desire - VERSIÓN DE PRODUCCIÓN (OPENCV PROFESIONAL) ")
    print("==========================================================")

    etiquetas, memoria_knn = cargar_memoria(cfg.ARCHIVO_DATASET)
    if etiquetas is None: return

    print("\n[SISTEMA] Leyendo base de datos local (PDF)...")
    texto_crudo = extraer_texto_de_pdf("pinguino.pdf") 
    texto_base = limpiar_texto_pdf(texto_crudo) if texto_crudo else ""

    detener_microfono = iniciar_oido_en_segundo_plano()
    cap = cv2.VideoCapture(0)
    
    prev_x, prev_y = None, None
    ultimo_tiempo_gesto = 0
    
    # Variables de Calibración
    estado_actual = "CALIBRANDO" 
    limite_inferior = None
    limite_superior = None
    cx1, cy1, cx2, cy2 = 150, 100, 250, 200

    print("\n[SISTEMA EN LÍNEA] Todo listo. Presiona 'q' para salir.")

    while True:
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.flip(frame, 1)
        small_frame = cv2.resize(frame, (400, 300))
        tecla = cv2.waitKey(1) & 0xFF
        
        # ===============================================================
        # FASE 0: CALIBRACIÓN (ANTIFALLOS DE LUZ)
        # ===============================================================
        if estado_actual == "CALIBRANDO":
            cv2.rectangle(small_frame, (cx1, cy1), (cx2, cy2), (0, 255, 255), 2)
            cv2.putText(small_frame, "Coloca tu mano", (140, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            cv2.putText(small_frame, "y presiona 'C'", (145, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            
            if tecla == ord('c'):
                limite_inferior, limite_superior = obtener_limites_dinamicos(small_frame, cx1, cy1, cx2, cy2)
                estado_actual = "ACTIVO"
                print("\n[CALIBRACIÓN] ¡Entorno analizado! Sistema Gestual Desbloqueado.")
                
        # ===============================================================
        # FASE 1: EJECUCIÓN (CON CONTORNOS PROFESIONALES)
        # ===============================================================
        elif estado_actual in ["ACTIVO", "PAUSA"]:
            
            if not buzon_de_voz.empty():
                comando = buzon_de_voz.get()
                threading.Thread(target=procesar_comando_voz_en_hilo, args=(comando, texto_base)).start()
                cv2.putText(small_frame, "Generando IA...", (150, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)

            # Binarización con los límites de la Fase 0
            hsv = cv2.cvtColor(small_frame, cv2.COLOR_BGR2HSV)
            mascara = cv2.inRange(hsv, limite_inferior, limite_superior)
            
            # Limpieza morfológica estricta
            kernel = np.ones((5,5), np.uint8)
            mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, kernel)
            
            # --- LA VÍA PROFESIONAL DE OPENCV ---
            # cv2.findContours encuentra los perímetros de las figuras blancas
            contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contornos:
                # Tomamos solo la figura geométrica más grande (ignoramos el ruido de fondo)
                contorno_maximo = max(contornos, key=cv2.contourArea)
                area_real = cv2.contourArea(contorno_maximo)
                
                # Umbral de seguridad (solo procesar si el área es significativa)
                if area_real > 400:
                    # Bounding Box perfecto
                    x, y, w, h = cv2.boundingRect(contorno_maximo)
                    
                    # Extracción matemática en tiempo real
                    aspect_ratio = w / float(h) if h > 0 else 0
                    densidad = area_real / float(w * h) if w * h > 0 else 0
                    punto_actual = [aspect_ratio, densidad]
                    
                    # Cálculo del Centro de Masa usando Momentos (Física)
                    M = cv2.moments(contorno_maximo)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                    else:
                        cx, cy = x + w//2, y + h//2

                    # --- PREDICCIÓN K-NN ---
                    gesto = predecir_gesto(punto_actual, memoria_knn, etiquetas)

                    # ESTADO: PUÑO (PAUSA)
                    if gesto == 1:
                        estado_actual = "PAUSA"
                        cv2.rectangle(small_frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                        cv2.putText(small_frame, "[ PAUSADO ]", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        prev_x, prev_y = None, None

                    # ESTADO: MANO ABIERTA (NAVEGACIÓN)
                    elif gesto == 2:
                        estado_actual = "ACTIVO"
                        cv2.rectangle(small_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        cv2.circle(small_frame, (cx, cy), 8, (255, 0, 0), -1) # Dibuja el centro de masa
                        cv2.putText(small_frame, "[ NAVEGACION ]", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                        # Controlador de Navegación Suave
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
                                
                        # Filtro de paso bajo para estabilizar el movimiento
                        prev_x = int(prev_x * 0.7 + cx * 0.3)
                        prev_y = int(prev_y * 0.7 + cy * 0.3)
            else:
                prev_x, prev_y = None, None

        cv2.imshow("Desire - Master Control", small_frame)
        if tecla == ord('q'):
            break

    print("\n[SISTEMA] Apagando hardware y liberando memoria...")
    detener_microfono(wait_for_stop=False)
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    iniciar_sistema_maestro()