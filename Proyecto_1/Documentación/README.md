# HorarioScript: Analizador Léxico para Horarios Académicos

Proyecto 1 del curso Lenguajes Formales y de Programación (Segundo Semestre 2026)[cite: 1]. 
Universidad de San Carlos de Guatemala (USAC) - Ingeniería en Ciencias y Sistemas[cite: 1].

## Descripción del Proyecto
HorarioScript es un analizador léxico desarrollado íntegramente en Python con una interfaz gráfica en Tkinter[cite: 1]. Su función principal es leer, tokenizar y validar archivos de texto con extensión `.hor` que contienen programaciones académicas[cite: 1]. 

El motor de análisis se basa en un Autómata Finito Determinista (AFD) programado de forma completamente manual (carácter por carácter), cumpliendo con la restricción estricta de no utilizar el módulo `re` (expresiones regulares) ni generadores automáticos de analizadores[cite: 1].

## Características Principales
*   **Tokenización Manual:** Reconocimiento de palabras reservadas, literales de hora (HH:MM), códigos alfanuméricos con guión (ej. LFP-0796), cadenas de texto, enteros y delimitadores sintácticos[cite: 1].
*   **Modo Pánico (Recuperación de Errores):** El analizador no se detiene al encontrar caracteres inválidos o errores léxicos; los recolecta y permite visualizar la posición exacta (línea y columna) al finalizar[cite: 1].
*   **Detección de Choques de Horario:** Algoritmo que evalúa los tokens para advertir si un mismo catedrático o aula tienen dos clases asignadas el mismo día y en el mismo bloque horario[cite: 1].
*   **Generación de Reportes HTML:** Creación automática de tres reportes estructurados con CSS embebido (Horario Semanal, Carga de Catedráticos y Estadístico General)[cite: 1].

## Requisitos del Sistema
*   Python 3.10 o superior (asegurarse de haber marcado la casilla "Add Python to PATH" durante la instalación)[cite: 1].
*   Librería `tkinter` (Incluida por defecto en la instalación estándar de Python para Windows)[cite: 1].

## Instrucciones de Ejecución
1.  Clonar este repositorio en su máquina local.
2.  Abrir la terminal (CMD o PowerShell) y navegar hasta el directorio raíz del proyecto (`Proyecto1`)[cite: 1].
3.  Ejecutar el archivo principal del programa con el siguiente comando:
    ```cmd
    python main.py
    ```

## Guía Rápida de Uso
1.  **Cargar Archivo:** Al abrir la aplicación, haga clic en el botón "Cargar Archivo" y seleccione un documento `.hor`[cite: 1].
2.  **Analizar Léxico:** Presione el botón verde "Analizar Léxico"[cite: 1]. El sistema procesará el texto y llenará las tablas inferiores.
3.  **Visualizar Resultados:** 
    *   La pestaña **Tabla de Tokens** mostrará todos los elementos reconocidos exitosamente con su tipo, fila y columna[cite: 1].
    *   La pestaña **Tabla de Errores** enlistará cualquier problema léxico encontrado (ej. cadenas sin cerrar, horas fuera del rango 06:00-21:00, caracteres no reconocidos)[cite: 1].
4.  **Generar Reportes:** Haga clic en el botón azul "Generar Reportes". Se crearán tres archivos HTML en la misma carpeta del proyecto para revisar la programación y los conflictos detectados[cite: 1].

## Ejemplo de Estructura Válida HorarioScript
```horarioscript
HORARIO {
    CURSOS {
        curso: "Lenguajes Formales y de Programacion" [codigo: "LFP-0796", creditos: 4],
    };
    CATEDRATICOS {
        catedratico: "Otto Rodriguez" [codigo: "DOC-001", categoria: TITULAR],
    };
    AULAS {
        aula: "A-101" [capacidad: 40, edificio: "T-3"],
    };
    CLASES {
        clase: "LFP-0796" con "DOC-001" en "A-101" [dia: LUNES, inicio: 07:00, fin: 08:40, seccion: "N"],
    };
};