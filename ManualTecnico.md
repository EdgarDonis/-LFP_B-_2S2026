# Manual Técnico
**USAC - Ingeniería en Ciencias y Sistemas**  
**Proyecto:** Torneo de Sudoku: Validación y Análisis de Partidas 
**Autor:** Edgar Alfredo Donis Llamas  
**Carnet:** 202307788  
**Laboratorio Lenguajes Formales y de Programación B+**

---

## 1. Descripción General
El presente sistema es un motor de validación desarrollado bajo el paradigma de Programación Orientada a Objetos (POO) diseñado para el torneo "Numerix Academy". Su función principal es leer archivos de texto plano con extensión `.lfp`, transformar cadenas de 81 caracteres en matrices bidimensionales de $9\times9$ y aplicar reglas de validación lógica para determinar el éxito de los intentos de Sudoku.

## 2. Requerimientos Técnicos
*   **Lenguaje:** Python 3.x nativo.
*   **Paradigma:** Programación Orientada a Objetos.
*   **Manejo de Archivos:** Funciones nativas `open()`, `readlines()` y manipulación de cadenas con `split(',')`.
*   **Sistema Operativo:** Windows / Linux / macOS.

---

## 3. Arquitectura del Sistema (Clases y Objetos)

El programa se divide en cuatro clases principales para modularizar la información:

### 3.1. Clase `Tablero`
Se encarga de modelar los sudokus disponibles en el torneo.
*   **Atributos:** `id_sudoku` (int), `dificultad` (str), `matriz` (list).
*   **Lógica:** Al instanciarse, recibe una cadena plana de 81 caracteres y utiliza una comprensión de listas anidada para transformarla en una matriz de $9\times9$.

### 3.2. Clase `Jugador`
Modela a los participantes inscritos.
*   **Atributos:** `carnet` (int), `nombre` (str), `apellido` (str), `nivel` (str).

### 3.3. Clase `Intento`
Almacena las propuestas de solución de los jugadores y sus resultados de validación.
*   **Atributos:** `carnet`, `id_sudoku`, `tiempo_segundos`, `fecha`, `matriz` ($9\times9$), `es_valido` (bool), `porcentaje_validez` (float).

### 3.4. Clase `SistemaSudoku`
Es el motor lógico y el controlador principal del programa.
*   **Estructuras de Datos:** Utiliza diccionarios (`{}`) para almacenar tableros y jugadores (permitiendo búsquedas rápidas por ID/Carnet) y listas (`[]`) para almacenar los intentos.
*   **Métodos Principales:**
    *   `cargar_sudokus()`, `cargar_jugadores()`, `cargar_intentos()`: Manejan la apertura de archivos `.lfp` y la limpieza de datos (`strip()`).
    *   `validar_y_calificar()`: Ejecuta el análisis matricial.
    *   `generar_reporte_1()`, `generar_reporte_2()`, `generar_reporte_3()`: Procesan las métricas y construyen el código HTML de salida.

---

## 4. Lógica de Validación Matricial

Para que un intento sea evaluado, el sistema primero verifica que las pistas originales del tablero (celdas distintas de `0`) no hayan sido modificadas por el jugador. Si se respeta el tablero original, se procede a contar las áreas válidas (un total máximo de 27).

A continuación, se presenta el pseudocódigo que explica el algoritmo utilizado para extraer y validar las subcuadrículas de $3\times3$, el cual representa el mayor desafío de indexación de la práctica:

### Pseudocódigo: Validación de Cajas de $3\times3$

```text
INICIO ValidarCajas
    areas_validas = 0
    
    // Recorrer las 3 "super-filas" de cajas
    PARA caja_fila DESDE 0 HASTA 2 HACER:
        
        // Recorrer las 3 "super-columnas" de cajas
        PARA caja_col DESDE 0 HASTA 2 HACER:
            
            caja_actual = ListaVacia()
            
            // Recorrer las 3 filas internas de la caja específica
            PARA i DESDE 0 HASTA 2 HACER:
                
                // Recorrer las 3 columnas internas de la caja específica
                PARA j DESDE 0 HASTA 2 HACER:
                    
                    // Calcular las coordenadas exactas en la matriz de 9x9
                    fila_absoluta = (caja_fila * 3) + i
                    col_absoluta = (caja_col * 3) + j
                    
                    // Extraer el valor e insertarlo en la lista plana
                    valor = matriz_intento[fila_absoluta][col_absoluta]
                    Agregar valor a caja_actual
                    
                FIN PARA
            FIN PARA
            
            // Validar si la caja extraída tiene los números del 1 al 9 sin ceros ni repetidos
            SI (Longitud(ValoresUnicos(caja_actual)) == 9) Y (0 NO ESTÁ EN caja_actual) ENTONCES:
                areas_validas = areas_validas + 1
            FIN SI
            
        FIN PARA
    FIN PARA
FIN ValidarCajas