from google import genai
import json
import re

# =================================================================
# FASE 4 (NLP): MOTOR DE INTELIGENCIA ARTIFICIAL (NUEVO SDK)
# =================================================================

# 1. Configurar la llave de acceso
API_KEY = ""
# API_KEY = "TU_API_KEY_AQUI"

# 2. Inicializar el Cliente con la arquitectura de Google
# (Asegúrate de poner tu API Key real arriba)
if API_KEY != "TU_API_KEY_AQUI":
    cliente = genai.Client(api_key=API_KEY)
else:
    cliente = None

def resumir_texto_a_json(texto_fragmento):
    """
    Envía un bloque de texto a la IA con instrucciones estrictas de 
    devolver un JSON estructurado para crear diapositivas.
    """
    if cliente is None:
        print("[ERROR] API Key no configurada.")
        return None

    # La instrucción maestra (System Prompt)
    PROMPT_SISTEMA = """
    Eres un experto estructurador de datos y diseñador de presentaciones.
    Tu tarea es leer el siguiente texto y extraer los puntos clave para crear diapositivas.
    
    REGLA ESTRICTA: Debes responder ÚNICAMENTE con un objeto JSON válido. 
    No agregues saludos, no uses bloques de código markdown (```json), solo el texto JSON crudo.
    
    El JSON debe tener EXACTAMENTE esta estructura:
    {
      "titulo_principal": "Un título general del texto",
      "subtitulo": "Un subtítulo breve",
      "diapositivas": [
        {
          "titulo": "Título del subtema 1",
          "puntos": ["Punto clave 1", "Punto clave 2", "Punto clave 3"]
        },
        {
          "titulo": "Título del subtema 2",
          "puntos": ["Punto clave 1", "Punto clave 2"]
        }
      ]
    }
    
    TEXTO A ANALIZAR:
    """
    
    prompt_final = PROMPT_SISTEMA + texto_fragmento
    
    print("Enviando texto a la IA para análisis cognitivo...")
    
    try:
        # Hacemos la llamada a la IA usando el nuevo SDK y el modelo más reciente
        respuesta = cliente.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt_final
        )
        
        texto_respuesta = respuesta.text
        
        # Limpieza de seguridad para asegurar que es un JSON puro
        texto_limpio = re.sub(r'```json\s*', '', texto_respuesta)
        texto_limpio = re.sub(r'```\s*', '', texto_limpio)
        
        # Convertimos el texto (String) a un Diccionario real de Python
        diccionario_json = json.loads(texto_limpio)
        
        return diccionario_json
        
    except json.JSONDecodeError:
        print("[ERROR CRÍTICO] La IA no devolvió un JSON válido. Respuesta cruda:")
        print(texto_respuesta)
        return None
    except Exception as e:
        print(f"[ERROR DE RED O API] {e}")
        return None

# =================================================================
# PRUEBA DEL MÓDULO (Generación de JSON)
# =================================================================
if __name__ == "__main__":
    texto_de_prueba = """
    AWS (Amazon Web Services) ofrece múltiples servicios para la infraestructura en la nube. 
    Uno de los pilares de la seguridad es IAM (Identity and Access Management), el cual permite 
    controlar de forma segura el acceso a los recursos. IAM funciona mediante la creación de 
    usuarios, grupos y roles, aplicando siempre el principio de menor privilegio, lo que significa 
    que solo se otorgan los permisos estrictamente necesarios para realizar una tarea.
    Por otro lado, para el almacenamiento de bases de datos estructuradas, AWS proporciona 
    Amazon RDS (Relational Database Service). RDS facilita la configuración, el funcionamiento 
    y la escalabilidad de bases de datos relacionales como MySQL o PostgreSQL, automatizando 
    tareas administrativas tediosas como los respaldos (backups) y la aplicación de parches.
    """
    
    if API_KEY == "TU_API_KEY_AQUI":
        print("Por favor, pon tu API Key de Google AI Studio en la variable API_KEY.")
    else:
        resultado_json = resumir_texto_a_json(texto_de_prueba)
        
        if resultado_json:
            print("\n[ÉXITO] La IA devolvió la siguiente estructura matemática:\n")
            print(json.dumps(resultado_json, indent=4, ensure_ascii=False))
