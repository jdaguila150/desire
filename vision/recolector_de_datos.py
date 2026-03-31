import cv2
import numpy as np
import os
import csv

# =================================================================
# CONFIGURACIÓN Y PURGA DE DATOS VIEJOS
# =================================================================
ARCHIVO_DATASET = "dataset_gestos.csv"

# IMPORTANTE: Al iniciar el programa, sobrescribimos (mode='w') el archivo viejo.
# No queremos mezclar datos de iluminación vieja con la iluminación nueva.
with open(ARCHIVO_DATASET, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Etiqueta", "Aspect_Ratio", "Densidad"])
    print(f"[SISTEMA] Archivo {ARCHIVO_DATASET} reseteado. Listo para datos puros.")

# =================================================================
# FUNCIÓN MATEMÁTICA DE CALIBRACIÓN
# =================================================================
def obtener_limites_dinamicos(frame, x1, y1, x2, y2, tolerancia_h=15, tolerancia_sv=40):
    roi = frame[y1:y2, x1:x2]
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    
    h_media = np.mean(hsv_roi[:,:,0])
    s_media = np.mean(hsv_roi[:,:,1])
    v_media = np.mean(hsv_roi[:,:,2])
    
    limite_inferior = np.array([
        np.clip(h_media - tolerancia_h, 0, 179),
        np.clip(s_media - tolerancia_sv, 0, 255),
        np.clip(v_media - tolerancia_sv, 0, 255)
    ], dtype=np.uint8)
    
    limite_superior = np.array([
        np.clip(h_media + tolerancia_h, 0, 179),
        np.clip(s_media + tolerancia_sv, 0, 255),
        np.clip(v_media + tolerancia_sv, 0, 255)
    ], dtype=np.uint8)
    
    return limite_inferior, limite_superior

# =================================================================
# SISTEMA PRINCIPAL DE RECOLECCIÓN
# =================================================================
def recolector_de_datos():
    cap = cv2.VideoCapture(0)
    kernel = np.ones((4, 4), np.uint8) 
    
    # Coordenadas del cuadro de calibración
    cx1, cy1, cx2, cy2 = 150, 100, 250, 200
    
    estado = "CALIBRANDO"
    lim_inf, lim_sup = None, None
    contador_grabaciones = 0

    print("\n--- RECOLECTOR DE DATOS ML (VERSIÓN DINÁMICA) ---")
    
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.flip(frame, 1)
        small_frame = cv2.resize(frame, (400, 300))
        key = cv2.waitKey(1) & 0xFF
        
        # ---------------------------------------------------------
        # FASE 0: CALIBRACIÓN DE ENTORNO
        # ---------------------------------------------------------
        if estado == "CALIBRANDO":
            cv2.rectangle(small_frame, (cx1, cy1), (cx2, cy2), (0, 255, 255), 2)
            cv2.putText(small_frame, "1. Pon tu mano aqui", (130, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            cv2.putText(small_frame, "2. Presiona 'C'", (140, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            
            if key == ord('c'):
                lim_inf, lim_sup = obtener_limites_dinamicos(small_frame, cx1, cy1, cx2, cy2)
                estado = "RECOLECTANDO"
                print("\n[CALIBRACIÓN] ¡Luz capturada! Ahora puedes empezar a grabar gestos.")
                print(" -> Mantén presionada la tecla '1' para grabar PUÑO.")
                print(" -> Mantén presionada la tecla '2' para grabar MANO ABIERTA.")
                
        # ---------------------------------------------------------
        # FASE 1: RECOLECCIÓN DE DATOS (MACHINE LEARNING)
        # ---------------------------------------------------------
        elif estado == "RECOLECTANDO":
            # 1. Aplicar los límites dinámicos
            hsv = cv2.cvtColor(small_frame, cv2.COLOR_BGR2HSV)
            binary_mask = cv2.inRange(hsv, lim_inf, lim_sup)

            # 2. Filtro Morfológico (Limpieza de Ruido)
            binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, kernel)
            binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel)

            # 3. Extracción de Características
            coords = np.argwhere(binary_mask == 255)
            
            aspect_ratio = 0
            densidad = 0
            mano_detectada = False
            
            if coords.size > 400: 
                mano_detectada = True
                y_min, x_min = coords.min(axis=0)
                y_max, x_max = coords.max(axis=0)
                
                w = (x_max - x_min)
                h_box = (y_max - y_min)
                
                if w > 0 and h_box > 0:
                    aspect_ratio = w / h_box
                    area_mancha = coords.shape[0] 
                    area_caja = w * h_box
                    densidad = area_mancha / area_caja

                    # Dibujar caja y métricas matemáticas
                    cv2.rectangle(small_frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                    cv2.putText(small_frame, f"AR: {aspect_ratio:.2f} | Den: {densidad:.2f}", 
                                (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # 4. Grabador de Datos (Data Logger)
            if mano_detectada and (key == ord('1') or key == ord('2')):
                etiqueta = 1 if key == ord('1') else 2
                
                with open(ARCHIVO_DATASET, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([etiqueta, round(aspect_ratio, 4), round(densidad, 4)])
                
                contador_grabaciones += 1
                
                color_grabacion = (0, 0, 255) if etiqueta == 1 else (255, 0, 0)
                cv2.circle(small_frame, (30, 30), 15, color_grabacion, -1)
                cv2.putText(small_frame, f"GRABANDO GESTO {etiqueta} ({contador_grabaciones})", 
                            (60, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_grabacion, 2)

            cv2.imshow("Mascara Limpia (Dinámica)", binary_mask)

        # Mostrar interfaz principal
        cv2.imshow("Etapa 2: Recolector de Datos", small_frame)
        
        if key == ord('q'):
            print(f"\n[SISTEMA] Recolección terminada. Se guardaron {contador_grabaciones} muestras en {ARCHIVO_DATASET}.")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    recolector_de_datos()