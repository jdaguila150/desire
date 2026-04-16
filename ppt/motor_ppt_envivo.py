import win32com.client
import time
import os

# =================================================================
# FASE 4 (AVANZADA): MOTOR DE INYECCIÓN EN TIEMPO REAL (pywin32)
# =================================================================

def inyectar_diapositiva_en_vivo(titulo_texto, puntos_lista, ruta_imagen=None):
    """
    Se conecta al proceso activo de PowerPoint y dibuja una nueva 
    diapositiva. Si recibe una ruta de imagen, auto-maqueta el layout.
    """
    try:
        ppt_app = win32com.client.Dispatch("PowerPoint.Application")
        ppt_app.Visible = True 
        
        try:
            presentacion = ppt_app.ActivePresentation
        except Exception:
            print("[ERROR] No tienes ninguna presentación abierta. Abre una primero.")
            return False

        total_diapositivas = presentacion.Slides.Count
        indice_nueva = total_diapositivas + 1

        nueva_slide = presentacion.Slides.Add(indice_nueva, 2)

        # 5. Inyectar el Título
        nueva_slide.Shapes(1).TextFrame.TextRange.Text = titulo_texto

        # 6. Inyectar los puntos (Viñetas / Bullets)
        cuerpo_texto = nueva_slide.Shapes(2).TextFrame.TextRange
        texto_completo = ""
        for i, punto in enumerate(puntos_lista):
            texto_completo += punto
            if i < len(puntos_lista) - 1:
                texto_completo += "\n" 
                
        cuerpo_texto.Text = texto_completo

        # =========================================================
        # 7. INYECCIÓN DE IMAGEN Y MAQUETACIÓN DINÁMICA (NUEVO)
        # =========================================================
        if ruta_imagen and os.path.exists(ruta_imagen):
            print(f"[COM INTEROP] Maquetando imagen en coordenadas cartesianas...")
            
            # En la API COM, 72 puntos = 1 pulgada. Una slide 16:9 mide aprox 960x540.
            # Reducimos el ancho del cuadro de texto a la mitad para hacer espacio
            nueva_slide.Shapes(2).Width = 450 
            
            # Posicionamos la imagen a la derecha (Left=500, Top=130, Width=400)
            # El -1 en el Height obliga a PowerPoint a mantener la proporción original (Aspect Ratio)
            # AddPicture(FileName, LinkToFile (0=False), SaveWithDocument (-1=True), Left, Top, Width, Height)
            nueva_slide.Shapes.AddPicture(ruta_imagen, 0, -1, 500, 130, 400, -1)
        # =========================================================

        print(f"[COM INTEROP] ¡Inyección exitosa! Se agregó: '{titulo_texto}'")
        
        try:
            if ppt_app.SlideShowWindows.Count > 0:
                ppt_app.SlideShowWindows(1).View.GotoSlide(indice_nueva)
        except Exception as e:
            pass 

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