import cv2
import numpy as np
import time

# --- IMPORTACIÓN DE TUS MÓDULOS ---
import config as cfg
from motor_vision import obtener_mascara_hsv
from motor_ml import cargar_memoria, extraer_caracteristicas, predecir_gesto
from controlador_os import abrir_presentacion, presionar_tecla, VK_RIGHT, VK_LEFT, VK_ESCAPE

def iniciar_gestura():
    print("==================================================")
    print(" GESTURA - SISTEMA DE CONTROL HMI ACTIVO ")
    print("==================================================")

    # 1. Cargar el Cerebro (Machine Learning)
    etiquetas, memoria = cargar_memoria(cfg.ARCHIVO_DATASET)
    if etiquetas is None: return

    # 2. Preparar el Entorno (PowerPoint)
    abrir_presentacion(cfg.RUTA_PPT)

    # 3. Inicializar Cámara y Variables de Estado
    cap = cv2.VideoCapture(0)
    prev_x, prev_y = None, None
    ultimo_tiempo_gesto = 0

    print("\n[SISTEMA] Listo. Presiona 'q' en la cámara para salir.")

    # =================================================================
    # BUCLE PRINCIPAL (El corazón del programa)
    # =================================================================
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        # Preparar imagen
        frame = cv2.flip(frame, 1)
        small_frame = cv2.resize(frame, (400, 300))
        
        # --- A. MOTOR DE VISIÓN ---
        # Una sola línea obtiene la máscara limpia usando álgebra de matrices
        mascara = obtener_mascara_hsv(
            small_frame, 
            cfg.H_MIN, cfg.H_MAX, cfg.S_MIN, cfg.V_MIN
        )
        coords = np.argwhere(mascara == 255)
        
        # --- B. MOTOR DE MACHINE LEARNING Y ESTADOS ---
        if coords.size > 400: 
            punto_actual, caja = extraer_caracteristicas(coords)
            
            if punto_actual is not None:
                # La IA decide qué gesto estás haciendo
                gesto = predecir_gesto(punto_actual, memoria, etiquetas)
                x_min, y_min, x_max, y_max = caja
                cy, cx = coords.mean(axis=0).astype(int)

                # ESTADO 1: PUÑO (SISTEMA EN PAUSA)
                if gesto == 1:
                    cv2.rectangle(small_frame, (x_min, y_min), (x_max, y_max), (0, 0, 255), 2)
                    cv2.putText(small_frame, "ESTADO: PAUSADO (Puno)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    prev_x, prev_y = None, None # Romper inercia

                # ESTADO 2: MANO ABIERTA (SISTEMA ACTIVO / NAVEGACIÓN)
                elif gesto == 2:
                    cv2.rectangle(small_frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                    cv2.circle(small_frame, (cx, cy), 8, (255, 0, 0), -1)
                    cv2.putText(small_frame, "ESTADO: ACTIVO (Navegacion)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                    # --- C. CONTROLADOR DE NAVEGACIÓN (SWIPES) ---
                    tiempo_actual = time.time()
                    if prev_x is None or prev_y is None:
                        prev_x, prev_y = cx, cy

                    if (tiempo_actual - ultimo_tiempo_gesto) > cfg.COOLDOWN_GESTO:
                        delta_x = cx - prev_x
                        delta_y = cy - prev_y
                        
                        # Evaluar movimiento dominante
                        if abs(delta_x) > abs(delta_y):
                            if delta_x > cfg.UMBRAL_SWIPE:
                                print("--> SIGUIENTE")
                                presionar_tecla(VK_RIGHT)
                                ultimo_tiempo_gesto = tiempo_actual
                            elif delta_x < -cfg.UMBRAL_SWIPE:
                                print("<-- ANTERIOR")
                                presionar_tecla(VK_LEFT)
                                ultimo_tiempo_gesto = tiempo_actual
                        else:
                            if delta_y > cfg.UMBRAL_SWIPE:
                                print("vvv SALIR (ESC)")
                                presionar_tecla(VK_ESCAPE)
                                ultimo_tiempo_gesto = tiempo_actual

                    # Suavizado de trayectoria (Inercia)
                    prev_x = int(prev_x * 0.7 + cx * 0.3)
                    prev_y = int(prev_y * 0.7 + cy * 0.3)
        else:
            prev_x, prev_y = None, None

        # --- D. VISUALIZACIÓN ---
        cv2.imshow("Gestura - Interfaz Principal", small_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Liberar hardware
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    iniciar_gestura()