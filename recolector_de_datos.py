import cv2
import numpy as np
import os
import csv

# =================================================================
# CONFIGURACIÓN
# =================================================================
H_MIN, H_MAX = 331, 360
S_MIN = 0.44
V_MIN = 0.48

ARCHIVO_DATASET = "dataset_gestos.csv"

# Crear el archivo y los encabezados si no existe
if not os.path.exists(ARCHIVO_DATASET):
    with open(ARCHIVO_DATASET, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Etiqueta", "Aspect_Ratio", "Densidad"])
        print(f"Archivo {ARCHIVO_DATASET} creado con éxito.")

def recolector_de_datos():
    cap = cv2.VideoCapture(0)
    kernel = np.ones((4, 4), np.uint8) # Brocha para limpiar ruido
    
    print("\n--- RECOLECTOR DE DATOS ML ---")
    print("Instrucciones:")
    print("Mantén presionada la tecla '1' para grabar PUÑO.")
    print("Mantén presionada la tecla '2' para grabar MANO ABIERTA.")
    print("Presiona 'q' para salir.")
    
    contador_grabaciones = 0

    while True:
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.flip(frame, 1)
        small_frame = cv2.resize(frame, (400, 300))
        
        # --- 1. PROCESAMIENTO HSV Y MÁSCARA ---
        b, g, r = small_frame[:,:,0]/255.0, small_frame[:,:,1]/255.0, small_frame[:,:,2]/255.0
        cmax = np.maximum(np.maximum(r, g), b)
        cmin = np.minimum(np.minimum(r, g), b)
        diff = cmax - cmin
        
        h = np.zeros_like(cmax)
        idx = diff != 0
        h[(cmax==r) & idx] = (60 * ((g[(cmax==r) & idx] - b[(cmax==r) & idx]) / diff[(cmax==r) & idx]) + 360) % 360
        h[(cmax==g) & idx] = (60 * ((b[(cmax==g) & idx] - r[(cmax==g) & idx]) / diff[(cmax==g) & idx]) + 120) % 360
        h[(cmax==b) & idx] = (60 * ((r[(cmax==b) & idx] - g[(cmax==b) & idx]) / diff[(cmax==b) & idx]) + 240) % 360
        
        s = np.zeros_like(cmax)
        s[cmax != 0] = diff[cmax != 0] / cmax[cmax != 0]
        v = cmax

        mascara_logica = (h >= H_MIN) & (h <= H_MAX) & (s >= S_MIN) & (v >= V_MIN)
        binary_mask = np.zeros_like(h, dtype=np.uint8)
        binary_mask[mascara_logica] = 255

        # --- 2. FILTRO DE RUIDO (SAL Y PIMIENTA) ---
        binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, kernel)
        binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel)

        # --- 3. EXTRACCIÓN DE CARACTERÍSTICAS ---
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

                # Dibujar caja
                cv2.rectangle(small_frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                cv2.putText(small_frame, f"AR: {aspect_ratio:.2f} | Den: {densidad:.2f}", 
                            (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # --- 4. SISTEMA DE GRABACIÓN (DATA LOGGER) ---
        key = cv2.waitKey(1) & 0xFF
        
        # Si hay una mano visible y presionamos 1 o 2, guardamos el dato
        if mano_detectada and (key == ord('1') or key == ord('2')):
            etiqueta = 1 if key == ord('1') else 2
            
            # Guardar en el CSV
            with open(ARCHIVO_DATASET, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([etiqueta, round(aspect_ratio, 4), round(densidad, 4)])
            
            contador_grabaciones += 1
            
            # Feedback visual de que estamos grabando
            color_grabacion = (0, 0, 255) if etiqueta == 1 else (255, 0, 0)
            cv2.circle(small_frame, (30, 30), 15, color_grabacion, -1)
            cv2.putText(small_frame, f"GRABANDO GESTO {etiqueta} ({contador_grabaciones})", 
                        (60, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_grabacion, 2)

        cv2.imshow("Etapa 2: Recolector de Datos", small_frame)
        cv2.imshow("Mascara Limpia", binary_mask)
        
        if key == ord('q'):
            print(f"\nRecolección terminada. Se guardaron {contador_grabaciones} muestras en {ARCHIVO_DATASET}.")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    recolector_de_datos()