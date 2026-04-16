from google import genai
from google.genai import types
import json
from dotenv import load_dotenv
import os

# =================================================================
# FASE 4 (NLP): MOTOR DE INTELIGENCIA ARTIFICIAL (DISEÑADOR)
# =================================================================

# 1. Configurar la llave de acceso
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("[ALERTA] No se encontró la llave de Gemini en el archivo .env")

if API_KEY != "TU_API_KEY_AQUI":
    cliente = genai.Client(api_key=API_KEY)
else:
    cliente = None

def resumir_texto_a_json(texto_fragmento):
    """
    Actúa como un Diseñador Instruccional, estructurando el texto
    y decidiendo el mejor layout visual para cada diapositiva.
    """
    if cliente is None:
        print("[ERROR] API Key no configurada.")
        return None

    # LA INSTRUCCIÓN MAESTRA (Diseño Arquitectónico de Diapositivas)
    PROMPT_SISTEMA = """
    Eres un experto en Diseño Instruccional y Narrativa Visual. 
    Tu objetivo es transformar texto técnico en diapositivas amigables y profesionales.
    
    REGLAS DE DISEÑO:
    - Puntos: Máximo 12 palabras por viñeta.
    - Dato Extra: Máximo 20 palabras.
    
    Además, debes analizar el "sentimiento" del texto y elegir UN tema visual global:
    - "corporativo": Para temas serios, seguridad o finanzas (Tonos azules).
    - "creativo": Para innovación, marketing o ideas nuevas (Tonos naranjas/cálidos).
    - "oscuro": Para tecnología profunda, código o hacking (Fondo oscuro, acentos neón).

    Responde ESTRICTAMENTE con este formato JSON:
    {
      "titulo_principal": "Título de la Presentación",
      "subtitulo": "Frase de enganche",
      "tema": "corporativo", 
      "diapositivas": [
        {
          "layout": "clasico" | "destacado" | "insight",
          "titulo": "Título de la slide",
          "puntos": ["Punto 1", "Punto 2"],
          "dato_extra": "Texto para el layout de insight o destacado",
          "query_imagen": "servidores nube moderno"
        }
      ]
    }

    TEXTO A ANALIZAR:
    """
    
    prompt_final = PROMPT_SISTEMA + texto_fragmento
    
    print("Enviando texto a la IA para análisis de diseño instruccional...")
    
    # try:
    #     # Hacemos la llamada obligando a Gemini a responder en formato JSON Nativo
    #     respuesta = cliente.models.generate_content(
    #         # model='gemini-2.5-flash',
    #         model='gemini-3.1-pro-preview',
    #         contents=prompt_final,
    #         config=types.GenerateContentConfig(
    #             response_mime_type="application/json",
    #         )
    #     )
        
    #     # Como usamos application/json, la respuesta ya es un string JSON puro y perfecto
    #     diccionario_json = json.loads(respuesta.text)
        
    #     return diccionario_json
        
    # except json.JSONDecodeError:
    #     print("[ERROR CRÍTICO] Fallo en la decodificación JSON nativa.")
    #     return None
    # except Exception as e:
    #     print(f"[ERROR DE RED O API] {e}")
    #     return None

    try:
        # Hacemos la llamada obligando a Gemini a responder en formato JSON Nativo
        respuesta = cliente.models.generate_content(
            # model='gemini-2.5-flash', # <--- Flash es ideal para latencia en vivo
            model='gemini-2.5-flash-lite', 
            contents=prompt_final,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        
        # Como usamos application/json, la respuesta ya es un string JSON puro y perfecto
        diccionario_json = json.loads(respuesta.text)
        print("DICCIONARIO JSON", diccionario_json)
        
        print("[INTELIGENCIA ARTIFICIAL] JSON estructurado correctamente.")
        return diccionario_json
        
    except json.JSONDecodeError as e:
        print(f"[ERROR CRÍTICO] Fallo en la decodificación JSON nativa: {e}")
        # Si falla, imprimimos lo que sea que haya devuelto para saber por qué se rompió
        if 'respuesta' in locals():
            print(f"-> Respuesta cruda de la API:\n{respuesta.text}")
        return None
        
    except Exception as e:
        print(f"[ERROR DE RED O API] Fallo en la comunicación con Google: {e}")
        return None
# =================================================================
# PRUEBA DEL MÓDULO (Generación de JSON)
# =================================================================
if __name__ == "__main__":
    texto_de_prueba = """
    La Evolución de la Interacción Humano-Máquina (HMI): De los Periféricos a la Computación Espacial
1. Introducción a los Sistemas HMI
La Interacción Humano-Máquina (HMI, por sus siglas en inglés) es la disciplina que estudia el diseño y uso de la tecnología informática, centrándose en las interfaces entre las personas y las computadoras. Durante décadas, esta interacción estuvo limitada por periféricos físicos y rígidos. El teclado, inventado en el siglo XIX para las máquinas de escribir, y el ratón, popularizado en la década de 1980, dictaron la forma en que los humanos debían adaptarse al lenguaje de las máquinas.

Sin embargo, el paradigma moderno exige que las máquinas se adapten al comportamiento natural humano. La verdadera revolución de la HMI no radica en crear botones más rápidos, sino en eliminar los botones por completo. La computación espacial y las interfaces naturales (NUI) buscan que la voz, los gestos y la mirada sean los únicos controladores necesarios, democratizando el acceso a la tecnología y reduciendo la carga cognitiva del usuario.

2. Visión por Computadora y Procesamiento Digital de Imágenes
El procesamiento digital de imágenes es el núcleo tecnológico que permite a las computadoras "ver". No se trata simplemente de capturar luz a través de un lente, sino de traducir matrices multidimensionales de píxeles en datos matemáticos procesables en tiempo real.

Tradicionalmente, la segmentación de objetos se lograba mediante umbralización de color (como el espacio HSV - Hue, Saturation, Value), aislando rangos específicos de luz. Sin embargo, este enfoque es altamente vulnerable a la desviación de datos (Data Drift) provocada por cambios en la iluminación ambiental. La luz no es estática; rebota, se refracta y altera la percepción del color constantemente.

Para superar esto, la ingeniería moderna de visión por computadora abandona el color y se enfoca en la topología. El uso de algoritmos de extracción de contornos y cálculo de momentos espaciales permite a las computadoras entender la geometría y el centro de gravedad de un objeto. Al calcular variables adimensionales como la densidad de píxeles y la relación de aspecto (Aspect Ratio), un sistema puede volverse matemáticamente inmune a las variaciones de luz del entorno.

3. Machine Learning Aplicado: El Algoritmo K-NN
Reconocer una mano es solo el primer paso; comprender su intención es el verdadero desafío. Aquí es donde el Machine Learning clásico, específicamente el algoritmo de K-Vecinos Más Cercanos (K-Nearest Neighbors o K-NN), demuestra su elegancia algorítmica.

A diferencia de las redes neuronales profundas que requieren hardware especializado (GPUs) y millones de parámetros, K-NN es un modelo de aprendizaje perezoso (Lazy Learning). Funciona calculando la distancia euclidiana entre un nuevo dato (por ejemplo, la forma geométrica actual de una mano) y una base de datos de entrenamiento en un plano multidimensional. Si la forma actual está matemáticamente cerca de los datos etiquetados como "Mano Abierta", el sistema clasifica el gesto con precisión milimétrica. La eficiencia de K-NN permite inferencias en microsegundos, garantizando un flujo constante de 30 a 60 cuadros por segundo, vital para evitar el retraso (lag) en las interfaces en vivo.

4. Arquitecturas RAG y Generación Aumentada por Recuperación
La voz humana es el método de transferencia de información de mayor ancho de banda que poseemos. Con la llegada de los Modelos de Lenguaje Grande (LLMs) modernos, el reconocimiento de voz ha evolucionado del simple dictado a la comprensión semántica profunda.

No obstante, los LLMs sufren de un problema crítico: las alucinaciones. Para mitigar esto en entornos profesionales, se implementa la arquitectura RAG (Retrieval-Augmented Generation). En lugar de confiar en la memoria general del modelo, un sistema RAG inyecta contexto de documentos locales y verificados directamente en el "prompt" antes de generar una respuesta. Esto ancla el conocimiento de la Inteligencia Artificial a una base de la verdad (Ground Truth), permitiendo generar estructuras de datos, resúmenes o incluso diapositivas completas con un margen de error cercano a cero.

El dato clave del éxito en RAG es la calidad de la inyección: una IA solo será tan precisa como el texto que se le otorgue como contexto.

5. El Futuro de la Interacción: Sistemas Multimodales
La convergencia de la visión por computadora algorítmica y el procesamiento de lenguaje natural en tiempo real da origen a los Sistemas Multimodales. Un sistema multimodal no obliga al usuario a elegir entre hablar o moverse; le permite hacer ambas cosas simultáneamente.

Imaginemos un expositor que camina por un escenario. Con un movimiento de su mano, navega por su presentación con una fluidez anatómica. Simultáneamente, al formular un comando de voz, la arquitectura de software en segundo plano invoca microservicios en la nube, procesa bases de datos documentales, maquetiza resultados visuales y los inyecta dinámicamente en la pantalla sin interrumpir la experiencia visual de la audiencia.

La seguridad, la eficiencia en multithreading (concurrencia) y el manejo de excepciones son los pilares fundamentales para mantener estas infraestructuras robustas operando sin bloqueos del sistema operativo. Estamos presenciando el fin de las presentaciones estáticas y el nacimiento de las narrativas generativas en tiempo real.
    """
    # texto_de_prueba = """
    # AWS (Amazon Web Services) ofrece múltiples servicios para la infraestructura en la nube. 
    # Uno de los pilares de la seguridad es IAM (Identity and Access Management), el cual permite 
    # controlar de forma segura el acceso a los recursos. IAM funciona mediante la creación de 
    # usuarios, grupos y roles, aplicando siempre el principio de menor privilegio, lo que significa 
    # que solo se otorgan los permisos estrictamente necesarios para realizar una tarea.
    # Por otro lado, para el almacenamiento de bases de datos estructuradas, AWS proporciona 
    # Amazon RDS (Relational Database Service). RDS facilita la configuración, el funcionamiento 
    # y la escalabilidad de bases de datos relacionales como MySQL o PostgreSQL, automatizando 
    # tareas administrativas tediosas como los respaldos (backups) y la aplicación de parches.
    # """
    
    if API_KEY == "TU_API_KEY_AQUI":
        print("Por favor, pon tu API Key de Google AI Studio en la variable API_KEY.")
    else:
        resultado_json = resumir_texto_a_json(texto_de_prueba)
        
        if resultado_json:
            print("\n[ÉXITO] La IA devolvió la siguiente estructura matemática:\n")
            print(json.dumps(resultado_json, indent=4, ensure_ascii=False))
