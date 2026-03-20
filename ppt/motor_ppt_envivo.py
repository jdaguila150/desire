import win32com.client
import time

# =================================================================
# FASE 4 (AVANZADA): MOTOR DE INYECCIÓN EN TIEMPO REAL (pywin32)
# =================================================================

def inyectar_diapositiva_en_vivo(titulo_texto, puntos_lista):
    """
    Se conecta al proceso activo de PowerPoint y dibuja una nueva 
    diapositiva al final de la presentación sin cerrar el archivo.
    """
    try:
        # 1. Engancharse al PowerPoint que ya se está ejecutando
        # Si no hay ninguno abierto, esto abrirá PowerPoint en segundo plano
        ppt_app = win32com.client.Dispatch("PowerPoint.Application")
        
        # Asegurarnos de que la ventana sea visible
        ppt_app.Visible = True 
        
        # 2. Obtener la presentación activa (la que estamos viendo)
        try:
            presentacion = ppt_app.ActivePresentation
        except Exception:
            print("[ERROR] No tienes ninguna presentación abierta. Abre una primero.")
            return False

        # 3. Calcular en qué número de diapositiva vamos a insertar la nueva
        total_diapositivas = presentacion.Slides.Count
        indice_nueva = total_diapositivas + 1

        # 4. Crear la nueva diapositiva (El 2 significa Diseño de Título y Objetos/Viñetas)
        nueva_slide = presentacion.Slides.Add(indice_nueva, 2)

        # 5. Inyectar el Título
        # Shapes(1) suele ser el cuadro del título
        nueva_slide.Shapes(1).TextFrame.TextRange.Text = titulo_texto

        # 6. Inyectar los puntos (Viñetas / Bullets)
        # Shapes(2) suele ser el cuadro del cuerpo del texto
        cuerpo_texto = nueva_slide.Shapes(2).TextFrame.TextRange
        
        texto_completo = ""
        for i, punto in enumerate(puntos_lista):
            texto_completo += punto
            if i < len(puntos_lista) - 1:
                texto_completo += "\n" # Salto de línea para la siguiente viñeta
                
        cuerpo_texto.Text = texto_completo

        print(f"[COM INTEROP] ¡Inyección exitosa! Se agregó: '{titulo_texto}'")
        
        # 7. (Opcional) Si estás en modo presentación (F5), saltar a la nueva diapositiva
        try:
            if ppt_app.SlideShowWindows.Count > 0:
                ppt_app.SlideShowWindows(1).View.GotoSlide(indice_nueva)
        except Exception as e:
            pass # Si no está en F5, no pasa nada

        return True

    except Exception as e:
        print(f"[ERROR CRÍTICO DEL SISTEMA OS] No se pudo comunicar con PowerPoint: {e}")
        return False

# =================================================================
# PRUEBA DE CAMPO
# =================================================================
if __name__ == "__main__":
    print("==========================================================")
    print(" INICIANDO PRUEBA DE INYECCIÓN COM INTEROP ")
    print("==========================================================")
    print("INSTRUCCIONES:")
    print("1. Abre CUALQUIER archivo de PowerPoint.")
    print("2. Ponlo en Modo Presentación (F5) si quieres ver la magia real.")
    print("3. Tienes 5 segundos para regresar a PPT antes de la inyección...")
    
    time.sleep(5)
    
    # Datos simulados que después vendrán de tu voz + Gemini
    titulo_prueba = "Generación Dinámica: Contenedores Inteligentes"
    viñetas_prueba = [
        "El sistema escuchó tu voz y buscó en el PDF local.",
        "Gemini estructuró este texto en microsegundos.",
        "pywin32 inyectó esto directo a la memoria RAM."
    ]
    
    inyectar_diapositiva_en_vivo(titulo_prueba, viñetas_prueba)