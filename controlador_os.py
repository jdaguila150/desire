# # =================================================================
# # CONTROLADOR NATIVO DE WINDOWS
# # =================================================================
# # Códigos Hexadecimales de las teclas en Windows (VK_CODES)
# VK_RIGHT  = 0x27  # Flecha Derecha
# VK_LEFT   = 0x25  # Flecha Izquierda
# VK_ESCAPE = 0x1B  # Tecla ESC
# VK_F5     = 0x74  # Tecla F5

# # Constante de Windows para soltar una tecla
# KEYEVENTF_KEYUP = 0x0002


import ctypes
import time
import os

# Códigos Hexadecimales de Windows (Virtual Key Codes)
VK_RIGHT  = 0x27
VK_LEFT   = 0x25
VK_ESCAPE = 0x1B
VK_F5     = 0x74

def presionar_tecla(hexKeyCode):
    "pulsación de tecla a nivel de sistema operativo."
    ctypes.windll.user32.keybd_event(hexKeyCode, 0, 0, 0)
    time.sleep(0.05) 
    ctypes.windll.user32.keybd_event(hexKeyCode, 0, 0x0002, 0)

def abrir_presentacion(ruta):
    "Abre el archivo y lanza la pantalla completa."
    if os.path.exists(ruta):
        print(f"[OS] Abriendo: {ruta}")
        os.startfile(ruta)
        time.sleep(6) # Tiempo para que PowerPoint cargue
        presionar_tecla(VK_F5)
    else:
        print(f"[OS] ADVERTENCIA: No se encontró {ruta}. Modo cámara únicamente.")

        