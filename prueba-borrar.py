import cv2
import numpy as np
import time
import threading

# =================================================================
# IMPORTACIÓN DE TUS MÓDULOS DE INGENIERÍA
# =================================================================
import vision.config as cfg 
from vision.motor_vision import obtener_mascara_hsv
from vision.motor_ml import cargar_memoria, extraer_caracteristicas, predecir_gesto
from vision.controlador_os import abrir_presentacion, presionar_tecla, VK_RIGHT, VK_LEFT, VK_ESCAPE
from ppt.motor_ppt_envivo import inyectar_diapositiva_en_vivo
from IA.motor_audio import iniciar_oido_en_segundo_plano, buzon_de_voz
from IA.motor_ia import resumir_texto_a_json
from ppt.lector_pdf import extraer_texto_de_pdf, limpiar_texto_pdf
from vision.calibrador_vision import obtener_limites_dinamicos # <--- NUESTRA NUEVA HERRAMIENTA

def iniciar_sistema_maestro():
 
    etiquetas, memoria_knn = cargar_memoria(cfg.ARCHIVO_DATASET)
    if etiquetas is None: return



    cap = cv2.VideoCapture(0)
    prev_x, prev_y = None, None
    ultimo_tiempo_gesto = 0
    estado_actual = "CALIBRANDO" # <--- NUEVO ESTADO INICIAL
    
    # Variables de Calibración Dinámica
    limite_inferior = None
    limite_superior = None
    # Coordenadas del cuadro central para una cámara reducida a 400x300
    cx1, cy1, cx2, cy2 = 150, 100, 250, 200 

    print("\n[✅ SISTEMA EN LÍNEA] Pon tu mano en el recuadro y presiona 'C' para calibrar.")

    while True:
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.flip(frame, 1)
        small_frame = cv2.resize(frame, (400, 300))
        tecla = cv2.waitKey(1) & 0xFF
        
        # ===============================================================
        # FASE 0: CALIBRACIÓN DINÁMICA DE ENTORNO
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
        # FASE 1: EJECUCIÓN DEL SISTEMA MAESTRO
        # ===============================================================
        elif estado_actual in ["ACTIVO", "PAUSA"]:
            
           
            # 2. Extracción de Máscara (Usando los límites dinámicos calculados)
            hsv = cv2.cvtColor(small_frame, cv2.COLOR_BGR2HSV)
            mascara = cv2.inRange(hsv, limite_inferior, limite_superior)
            
            # Limpieza de ruido
            kernel = np.ones((5,5), np.uint8)
            mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, kernel)
            
            coords = np.argwhere(mascara == 255)
            
            # 3. Machine Learning y Control Gestual
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

                        # Controlador OS
                        tiempo_actual = time.time()
                        if prev_x is None or prev_y is None: prev_x, prev_y = cx, cy

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

        # Mostrar la ventana final
        cv2.imshow("Gestura & Verbum - Master Control", small_frame)
        
        # Salida segura
        if tecla == ord('q'):
            break

    print("\n[SISTEMA] Apagando hardware y liberando memoria...")
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    iniciar_sistema_maestro()