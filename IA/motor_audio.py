import speech_recognition as sr
import queue
import time

# =================================================================
# FASE 4 (AVANZADA): MOTOR DE AUDIO ASÍNCRONO (MULTITHREADING)
# =================================================================

# Creamos un "buzón de mensajes" (Queue). El hilo de audio meterá los 
# textos aquí, y el hilo de la cámara (main.py) los sacará cuando tenga tiempo.
buzon_de_voz = queue.Queue()

def callback_reconocimiento(recognizer, audio):
    try:
        texto_crudo = recognizer.recognize_google(audio, language="es-MX")
        texto = texto_crudo.lower() 
        
        # 1. Definimos una tupla o lista con todas las formas naturales de pedirlo
        # Puedes agregar todas las variaciones que suelas usar al exponer
        frases_gatillo = [
            "en la siguiente diapositiva",
            "seguido veremos",
            "vamos a pasar con el tema de",
            "hablemos ahora sobre",
            "el siguiente punto es",
            "pasemos a ver",
            "me gustaría explicarles"
        ]
        
        # 2. La Regla de Negocio: Evaluamos si ALGUNA de las frases está en el texto
        # any() devolverá True en el instante en que encuentre una coincidencia
        if any(gatillo in texto for gatillo in frases_gatillo):
            print(f"\n[HILO DE AUDIO 🎤] Intención detectada: '{texto_crudo}'")
            
            # Metemos TODO el texto al buzón. 
            # (Ej: "bueno compañeros, vamos a pasar con el tema de redes neuronales")
            buzon_de_voz.put(texto_crudo)
        else:
            # Escuchó algo, pero era charla normal de tu exposición. Lo ignoramos.
            pass
            
    except sr.UnknownValueError:
        # Ruido de fondo o palabras incomprensibles
        pass
    except sr.RequestError as e:
        print(f"\n[HILO DE AUDIO ❌] Error de conexión a internet: {e}")

        

def iniciar_oido_en_segundo_plano():
    """
    Configura el micrófono y lanza el hilo de fondo.
    Devuelve una función que puedes llamar si alguna vez quieres "apagar" el micrófono.
    """
    r = sr.Recognizer()
    mic = sr.Microphone()
    
    with mic as fuente:
        print("\n[SISTEMA] Configurando filtros de reducción de ruido...")
        
        # 1. Ajuste inicial rápido
        r.adjust_for_ambient_noise(fuente, duration=2)
        
        # 2. EL TRUCO: Forzar el umbral de energía. 
        # Valores normales van de 150 a 300. Si ponemos 3000 o 4000, 
        # el micrófono SOLO te escuchará si hablas fuerte y claro y de cerca.
        r.energy_threshold = 500
        
        # 3. Apagar el ajuste automático para que no se vuelva a bajar solo
        r.dynamic_energy_threshold = False 
        
        # 4. Tiempo de pausa: Cuánto silencio determina que ya terminaste tu oración
        r.pause_threshold = 0.8 
        
        print("[SISTEMA] ¡Filtros activos! Debes hablar claro para activar el sistema.")
    
    # Esto lanza el Hilo 2. Le pasamos el micrófono y la función que debe
    # ejecutar cuando detecte una frase completa.
    funcion_para_detener = r.listen_in_background(mic, callback_reconocimiento)
    
    return funcion_para_detener

# =================================================================
# PRUEBA DE LABORATORIO (Multithreading)
# =================================================================
if __name__ == "__main__":
    print("==========================================================")
    print(" PRUEBA DE CONCURRENCIA: AUDIO EN SEGUNDO PLANO")
    print("==========================================================")
    
    # Encendemos el Hilo 2
    detener_microfono = iniciar_oido_en_segundo_plano()
    
    print("\n[HILO PRINCIPAL] Iniciando un bucle infinito simulando tu cámara...")
    print("[HILO PRINCIPAL] Habla por tu micrófono. El bucle NO se va a detener.")
    
    try:
        contador = 0
        while True:
            # Simulamos el trabajo de tu cámara y tus gestos
            print(f"Frame {contador} procesado...", end="\r")
            contador += 1
            time.sleep(0.1) # Simulando 10 FPS
            
            # Revisamos si el Hilo 2 nos dejó algún mensaje en el buzón
            if not buzon_de_voz.empty():
                mensaje_recibido = buzon_de_voz.get()
                print(f"\n\n[HILO PRINCIPAL] Acabo de sacar este texto del buzón: {mensaje_recibido}")
                print("[HILO PRINCIPAL] Aquí es donde le mandaríamos este texto a la IA (Gemini)...\n")
                
    except KeyboardInterrupt:
        print("\n\nApagando sistemas...")
        detener_microfono(wait_for_stop=False)