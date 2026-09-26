# MANUAL TÉCNICO: HorarioScript

**UNIVERSIDAD DE SAN CARLOS DE GUATEMALA**  
**Facultad de Ingeniería**  
**Escuela de Ingeniería en Ciencias y Sistemas**  
**Lenguajes Formales y de Programación - Segundo Semestre 2026**  
**Proyecto 1**  
**Edgar Alfredo Donis Llamas - 202307788**
---

## 1. Arquitectura del Sistema y Diagrama de Clases
El sistema está construido bajo el paradigma de Programación Orientada a Objetos (POO) en Python 3.10+, dividiendo las responsabilidades lógicas y gráficas en módulos independientes. Las clases principales son:

* **Token / ErrorLexico:** Estructuras de datos puras que almacenan el lexema, tipo, línea y columna de cada elemento analizado.
* **AnalizadorLexico:** El motor central. Contiene el texto de entrada y gestiona el estado actual (fila, columna, posición). Implementa la lógica del Autómata Finito Determinista (AFD).
* **GeneradorReportes:** Recibe las listas de tokens, agrupa la información semántica básica y genera archivos HTML independientes para horarios, catedráticos y estadísticas.
* **AplicacionHorario:** Clase principal en `main.py` que instancia la interfaz gráfica utilizando `tkinter`, gestiona los eventos de los botones y enlaza el texto de entrada con el analizador y los reportes.

## 2. Autómata Finito Determinista (AFD)
El reconocimiento de tokens se realiza mediante un AFD diseñado para evaluar la entrada carácter por carácter.

![máquina de estados.png](Documentaci%C3%B3n/m%C3%A1quina%20de%20estados.png)

### Tabla de Transiciones
| Estado Actual | Condición (Lectura) | Estado Siguiente | Acción / Reconocimiento |
| :--- | :--- | :--- | :--- |
| **S0** | Letra | S1 | Inicia palabra/código |
| **S0** | Dígito | S3 | Inicia número/hora |
| **S0** | `"` (Comilla) | S6 | Inicia cadena |
| **S0** | `#` | S7 | Inicia comentario |
| **S0** | `{ } [ ] : , ;` | S_Simbolo | Token SÍMBOLO |
| **S1** | Letra | S1 | Continúa palabra |
| **S1** | `-` (Guión) | S2 | Transición a código |
| **S1** | Otro | S_Palabra | Token PR / DIA / CAT |
| **S2** | Dígito | S_Codigo | Token CÓDIGO |
| **S3** | Dígito | S3 | Continúa entero |
| **S3** | `:` (Dos puntos) | S4 | Transición a hora |
| **S3** | Otro | S_Entero | Token ENTERO |
| **S4** | Dígito | S5 | Minutos (1) |
| **S5** | Dígito | S_Hora | Token HORA (si 06:00 a 21:00) |
| **S6** | Cualquier char | S6 | Continúa cadena |
| **S6** | `"` (Comilla) | S_Cadena | Token CADENA |

## 3. Algoritmo de Tokenización y Recuperación de Errores
El método `siguiente_token()` (integrado en el ciclo `analizar()`) se implementó de manera manual. En cumplimiento estricto con los requerimientos, no se utilizaron expresiones regulares (módulo `re`) ni funciones de alto nivel de división de cadenas como `split()`. El algoritmo lee la entrada utilizando indexación de listas (`self.entrada[self.posicion]`), acumulando caracteres en una variable temporal `lexema` según las transiciones del estado actual.

**Modo Pánico:** Para evitar que la ejecución se detenga al encontrar un error léxico (ej. un carácter fuera del alfabeto o una hora fuera de rango), el sistema registra el error instanciando un objeto `ErrorLexico` en su respectiva lista y avanza el puntero de lectura (`self.avanzar()`), permitiendo procesar el documento en una sola pasada de principio a fin.

## 4. Lógica de Detección de Choques de Horario
Para el reporte de conflictos, el `GeneradorReportes` extrae la información secuencial de cada `PR_CLASE` en diccionarios. Posteriormente, itera sobre la lista de clases comparando cada elemento contra los demás mediante dos condicionales:
1. **Conflicto de Entidad:** `(aula A == aula B) OR (catedratico A == catedratico B)`.
2. **Conflicto de Tiempo:** `(dia A == dia B) AND (inicio A == inicio B)`.

Si ambas condiciones se cumplen simultáneamente, el par de clases se agrega a una lista de choques para ser renderizadas con fondo rojo y alerta en el Reporte 1.

## 5. Justificación de Decisiones de Diseño
* **Iteración Indexada vs Métodos de String:** Se optó por recorrer la cadena con un puntero numérico (`self.posicion`) en lugar de consumir la cadena. Esto garantiza precisión total en el rastreo de líneas y columnas para el reporte de errores.
* **Uso de diccionarios para palabras reservadas:** En lugar de crear múltiples estados en el AFD para cada letra de palabras extensas como "CATEDRATICOS", el AFD extrae el bloque alfabético completo y lo busca en una tabla hash (`self.reservadas`). Si existe, asigna el tipo correspondiente; si no, lo reporta como error, optimizando la complejidad ciclomática del código.