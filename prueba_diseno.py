# Importamos tu nuevo diseñador gráfico
from IA.motor_nlp import crear_presentacion_desde_json

# Pegamos exactamente el JSON que te generó la IA
json_aws = {
    "titulo_principal": "La HMI del Mañana",
    "subtitulo": "Transformando la Interacción Humana-Máquina",
    "tema": "oscuro",
    "diapositivas": [
        {
            "layout": "destacado",
            "titulo": "HMI: De Botones a la Intuición",
            "puntos": [
                "Interfaces persona-máquina evolucionan.",
                "Antes, nos adaptábamos a periféricos rígidos.",
                "Hoy, la máquina se adapta al humano.",
                "El control es voz, gestos y mirada.",
                "Acceso democrático y menos esfuerzo cognitivo."
            ],
            "dato_extra": "La verdadera revolución HMI no es crear botones más rápidos, sino eliminarlos por completo.",
            "query_imagen": "futuro interaccion humano maquina computacion espacial hologramas, oscuro neon"
        },
        {
            "layout": "insight",
            "titulo": "Visión Computarizada: Más Allá del Color",
            "puntos": [
                "Computadoras 'ven': píxeles a datos procesables.",
                "Segmentación clásica por color, vulnerable a la luz.",
                "Moderno: Enfocarse en topología, no en color.",
                "Algoritmos entienden geometría y contornos.",
                "Inmune a variaciones de iluminación ambiental."
            ],
            "dato_extra": "La luz no es estática; rebota, refracta y altera la percepción constantemente, afectando el color.",
            "query_imagen": "ojo robotico procesando datos visuales, algoritmo de contornos, ciberpunk, oscuro neon"
        },
        {
            "layout": "destacado",
            "titulo": "K-NN: Entendiendo la Intención Humana",
            "puntos": [
                "Reconocer mano es un inicio; comprender la intención.",
                "K-NN: Algoritmo 'Lazy Learning' de ML clásico.",
                "Calcula distancia euclidiana a datos conocidos.",
                "Clasifica gestos con precisión milimétrica.",
                "Inferencia en microsegundos, esencial para fluidez."
            ],
            "dato_extra": "A diferencia de redes neuronales, K-NN es eficiente y no requiere hardware especializado de alto costo.",
            "query_imagen": "visualizacion algoritmo k-nn puntos cercanos en espacio multidimensional, ciberseguridad, neon azul"
        },
        {
            "layout": "insight",
            "titulo": "RAG: LLMs Confiables y Sin Alucinaciones",
            "puntos": [
                "Voz humana: alto ancho de banda de información.",
                "LLMs: reconocimiento de voz a comprensión profunda.",
                "Problema crítico: los LLMs pueden alucinar.",
                "RAG inyecta contexto verificado al 'prompt'.",
                "Ancla la IA a una base de verdad documentada.",
                "Genera datos precisos, con error cercano a cero."
            ],
            "dato_extra": "La precisión de un sistema RAG es directamente proporcional a la calidad de la información contextual inyectada.",
            "query_imagen": "arquitectura rag flujo de datos documentos base de datos llm, neuronas, futurista, neon violeta"
        },
        {
            "layout": "destacado",
            "titulo": "Multimodales: La Interacción del Futuro",
            "puntos": [
                "Sistemas Multimodales: visión y lenguaje unificados.",
                "Permite interacción simultánea con voz y gestos.",
                "Ej: Expositor navega presentación con fluidez anatómica.",
                "Invoca microservicios, procesa datos, actualiza pantalla.",
                "Seguridad, eficiencia y manejo de excepciones son clave.",
                "Adiós presentaciones estáticas; hola narrativas generativas."
            ],
            "dato_extra": "Estamos presenciando el fin de las presentaciones estáticas y el nacimiento de las narrativas generativas en tiempo real.",
            "query_imagen": "interaccion multimodal persona controlando hologramas con gestos y voz, fondo oscuro futurista neon"
        }
    ]
}

print("=========================================")
print(" INICIANDO PRUEBA DE DISEÑO INSTRUCCIONAL")
print("=========================================")

# Ejecutamos la función de tu archivo motor_nlp.py
nombre_archivo = "Prueba_AWS_Diseños.pptx"
crear_presentacion_desde_json(json_aws, nombre_archivo)

print("=========================================")
print(" PRUEBA FINALIZADA")
print("=========================================")