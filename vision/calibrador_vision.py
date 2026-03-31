import cv2
import numpy as np

# =================================================================
# MÓDULO DE VISIÓN: CALIBRADOR DINÁMICO DE COLOR (SIN LIBRERÍAS EXTERNAS ML)
# =================================================================

def obtener_limites_dinamicos(frame, x1, y1, x2, y2, tolerancia_h=15, tolerancia_sv=40):
    """
    Toma un recorte de la imagen (ROI), analiza los píxeles matemáticamente
    y devuelve los límites Inferior y Superior para la máscara HSV.
    """
    # 1. Recortar solo el pedacito de la imagen donde está tu mano
    roi = frame[y1:y2, x1:x2]
    
    # 2. Convertir ese pedacito a HSV
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    
    # 3. Extraer los canales separados
    h_canal = hsv_roi[:,:,0]
    s_canal = hsv_roi[:,:,1]
    v_canal = hsv_roi[:,:,2]
    
    # 4. Matemáticas: Calcular la Media (Promedio) de cada canal
    h_media = np.mean(h_canal)
    s_media = np.mean(s_canal)
    v_media = np.mean(v_canal)
    
    # 5. Calcular los límites sumando y restando una "tolerancia"
    # Usamos np.clip para que los números no se salgan del rango (0-255)
    lower_bound = np.array([
        np.clip(h_media - tolerancia_h, 0, 179),
        np.clip(s_media - tolerancia_sv, 0, 255),
        np.clip(v_media - tolerancia_sv, 0, 255)
    ], dtype=np.uint8)
    
    upper_bound = np.array([
        np.clip(h_media + tolerancia_h, 0, 179),
        np.clip(s_media + tolerancia_sv, 0, 255),
        np.clip(v_media + tolerancia_sv, 0, 255)
    ], dtype=np.uint8)
    
    return lower_bound, upper_bound

# =================================================================
# PRUEBA DE LABORATORIO (Presiona 'C' para calibrar)
# =================================================================
if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    
    # Coordenadas del cuadrado de calibración (Centro de la pantalla)
    x1, y1, x2, y2 = 250, 180, 350, 280
    
    # Variables para guardar nuestros rangos dinámicos
    limite_inferior = None
    limite_superior = None
    calibrado = False
    
    print("==================================================")
    print(" MODO CALIBRACIÓN ACTIVO")
    print("==================================================")
    print("1. Pon tu mano/guante en el cuadrado verde.")
    print("2. Presiona 'C' para capturar la luz actual.")
    print("3. Presiona 'Q' para salir.")
    
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.flip(frame, 1) # Efecto espejo
        frame_mostrar = frame.copy()
        
        # Dibujar el cuadro de calibración
        cv2.rectangle(frame_mostrar, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame_mostrar, "Pon tu mano aqui", (x1 - 20, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Si ya calibramos, mostramos la máscara trabajando en tiempo real
        if calibrado:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            mascara = cv2.inRange(hsv, limite_inferior, limite_superior)
            
            # Limpieza morfológica básica para quitar ruido
            kernel = np.ones((5,5), np.uint8)
            mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, kernel)
            
            cv2.imshow("Mascara Binarizada", mascara)
            cv2.putText(frame_mostrar, "[ CALIBRADO ]", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            
        cv2.imshow("Camara Principal", frame_mostrar)
        
        tecla = cv2.waitKey(1) & 0xFF
        
        # Lógica de Captura (Cuando presionas 'C')
        if tecla == ord('c'):
            limite_inferior, limite_superior = obtener_limites_dinamicos(frame, x1, y1, x2, y2)
            calibrado = True
            print("\n[ÉXITO] Matriz de píxeles analizada.")
            print(f"Límite Inferior: {limite_inferior}")
            print(f"Límite Superior: {limite_superior}")
            
        elif tecla == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()