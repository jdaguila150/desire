# 👁️ Desire - Sistema HMI Multimodal de Control y Generación Dinámica

![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-Matemática%20Pura-green)
![Gemini](https://img.shields.io/badge/IA-Gemini%202.5%20Flash-orange)
![Arquitectura](https://img.shields.io/badge/Arquitectura-Multithreading-red)

**Desire** es un sistema avanzado de Interacción Hombre-Máquina diseñado para expositores y conferencistas. Permite controlar presentaciones de PowerPoint mediante gestos físicos y **crear/inyectar nuevas diapositivas en tiempo real** usando comandos de voz impulsados por IA (RAG), todo sin interrumpir el flujo visual ni el sistema operativo.

---

## ✨ Características Principales

* ✋ **Control Gestual Geométrico (Sin Librerías Externas de ML):** Utiliza un algoritmo K-Nearest Neighbors (K-NN) programado desde cero con álgebra lineal para clasificar la geometría de la mano (Aspect Ratio y Densidad).
* 💡 **Calibración Dinámica de Entorno:** Se adapta a cualquier condición de luz calculando la media y desviación estándar de los píxeles (ROI) en tiempo de ejecución, eliminando el problema de *Data Drift*.
* 💉 **Inyección en Memoria RAM (COM Interop):** Evita el uso de librerías estáticas de archivos. Se conecta directamente al proceso activo de `POWERPNT.EXE` mediante la API nativa de Windows para dibujar texto mientras la presentación está proyectada (F5).
* 🎙️ **Escucha Concurrente Asíncrona (Multithreading):** El procesamiento de voz ocurre en un hilo en segundo plano protegido con una compuerta de ruido (*Energy Threshold*) y un *Wake Word* ("sistema"), garantizando que el reconocimiento visual nunca baje de 30 FPS.
* 🧠 **Arquitectura RAG (Retrieval-Augmented Generation):** Lee documentos locales PDF como base de conocimiento y los cruza con comandos de voz para generar estructuras JSON mediante Google Gemini 2.5 Flash.

---

## 📂 Estructura del Proyecto

La arquitectura respeta el principio de Responsabilidad Única, separando la visión, la manipulación del sistema operativo y los conectores de IA:


Desire/

├── vision/

│   ├── config.py                 # Constantes globales y umbrales

│   ├── calibrador_vision.py      # Matemáticas para calibración HSV al vuelo

│   ├── motor_vision.py           # Morfología matemática y binarización

│   ├── motor_ml.py               # Clasificador K-NN y extracción de Bounding Box

│   ├── controlador_os.py         # Mapeo de gestos a pulsaciones de teclado nativo

│   ├── recolector_datos.py       # Script para regrabar la memoria muscular (Data Logger)

│   └── dataset_gestos.csv        # Dataset local de características geométricas



├── ppt/

│   ├── motor_ppt_envivo.py       # Conector pywin32 para inyección COM

│   ├── lector_pdf.py             # Extractor y limpiador de texto local

│   └── pinguino.pdf              # Documento de base de conocimiento (Ejemplo)



├── IA/

│   ├── motor_audio.py            # Hilo concurrente de SpeechRecognition y PyAudio

│   └── motor_ia.py               # Conector con Google GenAI (Prompt Engineering)

└── master.py                     # Director de Orquesta (Bucle principal y UI)

⚙️ Requisitos de Instalación
⚠️ IMPORTANTE: Este sistema manipula hardware a bajo nivel (Micrófono vía PortAudio) y APIs de Windows. Se requiere estrictamente Python 3.11 o 3.12 (Versiones LTS) para asegurar la compatibilidad con los binarios precompilados.

Clona este repositorio.

Crea un entorno virtual e instala las dependencias:

Bash
pip install opencv-python numpy google-genai python-pptx pywin32 SpeechRecognition pyaudio
Configura tu API Key de Google Gemini en tus variables de entorno o directamente en IA/motor_ia.py.

🚀 Guía de Uso Rápido
Fase 1: Calibración y Entrenamiento (Solo una vez por entorno)
Antes de presentar, el sistema necesita aprender la luz del salón y la silueta de tu mano.

Ejecuta python vision/recolector_datos.py.

Coloca tu mano en el recuadro verde y presiona C para calcular la matriz de luz.

Haz un puño y deja presionada la tecla 1 para grabar muestras de "Pausa".

Abre la mano y deja presionada la tecla 2 para grabar muestras de "Navegación".

Presiona Q para guardar el nuevo dataset.

Fase 2: Ejecución del Sistema Maestro
Abre tu presentación de PowerPoint y presiona F5 (Pantalla Completa).

Ejecuta python master.py.

Vuelve a colocar tu mano en el recuadro inicial y presiona C para desbloquear el sistema.

Navegación: Abre la mano y haz swipes (deslizamientos) a la izquierda o derecha para cambiar de diapositiva. Cierra el puño para pausar el rastreo.

Generación por Voz: Mientras expones, di tu comando clave:

"Sistema, genera una diapositiva sobre las características geográficas mencionadas en el documento."

El hilo en segundo plano procesará la voz, la cruzará con el PDF y, en 3 segundos, la nueva diapositiva aparecerá proyectada frente a tu audiencia.

🛠️ Aspectos Técnicos Destacados (Para Revisión Académica)
Evitación de "Cajas Negras" en Visión: No se utilizan modelos pre-entrenados como MediaPipe para la visión espacial. La detección se realiza puramente mediante la extracción del contorno más grande, cálculo de área, ancho, alto y densidad matemática usando NumPy.

Manejo del Data Drift: La función obtener_limites_dinamicos implementa un cálculo estadístico en tiempo de ejecución (np.mean y np.clip de los canales HSV) para reajustar los límites de la máscara lógica ante variaciones fotométricas.

Concurrencia Segura: La comunicación entre el hilo principal de OpenCV (30 FPS) y el hilo bloqueante de la API de Google/Gemini se gestiona a través de la clase queue.Queue(), asegurando un entorno Thread-Safe libre de colisiones de memoria (Race Conditions).
