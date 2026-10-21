# Manual Técnico - MarkdownCheck: Analizador Léxico-Sintáctico de Markdown a HTML

**Universidad de San Carlos de Guatemala**  
**Facultad de Ingeniería - Escuela de Ingeniería en Ciencias y Sistemas**  
**Curso:** Lenguajes Formales y de Programación (0796) - Sección B+  
**Auxiliar:** Carlos Samuel Aguilar Acosta  
**Estudiante:** Edgar Alfredo Donis Llamas  
**Carnet:** 202307788  
**Fecha:** Octubre de 2026  

---

## 1. Introducción y Objetivos Técnicos

**MarkdownCheck** es un analizador léxico-sintáctico y traductor de documentos escritos en un subconjunto de Markdown (`.md`) hacia código HTML semántico, desarrollado desde cero en **Python 3.10+** con interfaz gráfica en **Tkinter**.

El sistema implementa:
1. **Analizador Léxico manual (`AnalizadorLexico`)**: Basado en un Autómata Finito Determinista (AFD) programado carácter por carácter sin utilizar expresiones regulares (`re`), con soporte de tokens virtuales de anidamiento (`INDENT` y `DEDENT`) y modo literal para código.
2. **Analizador Sintáctico Descendente Recursivo (`AnalizadorSintactico`)**: Basado en una Gramática Libre de Contexto (GLC) factorizada y libre de recursión por la izquierda (`LL(1)`), que construye un Árbol de Derivación / Sintaxis Abstracta (`NodoAST`).
3. **Recuperación de Errores en Modo Pánico (`GestorErrores`)**: Capaz de detectar, registrar y recuperarse de errores léxicos y sintácticos en una sola pasada sin abortar la ejecución.
4. **Generador de Reportes HTML (`GeneradorHTML`) y Visualizador Graphviz**: Recorre el AST para producir 3 reportes HTML independientes con CSS embebido y el archivo `arbol.dot` del árbol de derivación.

---

## 2. Arquitectura del Sistema y Diagrama de Clases

El proyecto sigue el paradigma de Programación Orientada a Objetos (POO) y separa las responsabilidades en cinco módulos desacoplados dentro del directorio `/src`:

```text
+-----------------------------------------------------------------------+
|                       main.py (Capa de Presentación)                  |
|  - AplicacionMarkdownCheck(tk.Tk): Interfaz gráfica, editor, tablas   |
+-----------------------------------+-----------------------------------+
                                    |
         +--------------------------+--------------------------+
         |                                                     |
         v                                                     v
+----------------------------------+     +----------------------------------+
|    analizador_lexico.py          |     |    analizador_sintactico.py      |
|  - AnalizadorLexico              |---->|  - AnalizadorSintactico          |
|    + siguiente_token(): Token    |     |    + analizar(): NodoAST         |
|    + obtener_tokens_visibles()   |     |    + generar_dot(): str          |
+----------------+-----------------+     +----------------+-----------------+
                 |                                        |
                 +-------------------+--------------------+
                                     |
                                     v
                 +----------------------------------------+
                 |              modelos.py                |
                 |  - Token                               |
                 |  - ErrorAnalisis                       |
                 |  - GestorErrores                       |
                 |  - NodoAST                             |
                 +-------------------+--------------------+
                                     |
                                     v
                 +----------------------------------------+
                 |           generador_html.py            |
                 |  - GeneradorHTML                       |
                 |    + construir_cuerpo_html(): str      |
                 |    + generar_tres_reportes(): dict     |
                 +----------------------------------------+
```

### Descripción de Clases Principales
* **`Token` (`modelos.py`)**: Encapsula el número correlativo, tipo de token, lexema reconocido, línea, columna, nivel jerárquico (`1..6` en encabezados, `1..N` en citas o nivel de indentación) e información adicional (lenguaje en bloques de código).
* **`ErrorAnalisis` y `GestorErrores` (`modelos.py`)**: Almacenan la lista de errores léxicos y sintácticos detectados con su fase, lexema, posición exacta (`línea`, `columna`) y descripción detallada.
* **`NodoAST` (`modelos.py`)**: Representa cada nodo del árbol de derivación. Distingue entre nodos no terminales (`es_terminal=False`, ej. `<documento>`, `<bloque>`, `<lista>`) y nodos hoja terminales (`es_terminal=True`, ej. `NUMERAL`, `TEXTO`, `VIÑETA`).
* **`AnalizadorLexico` (`analizador_lexico.py`)**: Recorre el flujo de caracteres del archivo `.md`, administra la pila de indentación (`pila_indent = [0]`), resuelve ambigüedades contextuales y expone el método `siguiente_token()`.
* **`AnalizadorSintactico` (`analizador_sintactico.py`)**: Implementa un método recursivo por cada símbolo no terminal de la GLC, consume tokens mediante `siguiente_token()`, sincroniza errores en modo pánico y exporta el árbol a formato Graphviz (`arbol.dot`).
* **`GeneradorHTML` (`generador_html.py`)**: Recorre recursivamente el `NodoAST` raíz para emitir el Reporte 1 (HTML renderizado), el Reporte 2 (Estadísticas cuantitativas) y el Reporte 3 (Tabla de contenido interactiva con anclas).

---

## 3. Especificación Léxica y Autómata Finito Determinista (AFD)

### 3.1 Tabla de Terminales (Tokens)

| Token | Descripción / Regla Léxica | Ejemplo de Lexema | Justificación / Observación |
| :--- | :--- | :--- | :--- |
| `NUMERAL` | De 1 a 6 símbolos `#` consecutivos al inicio de línea, seguidos obligatoriamente de un espacio. | `##` | Definido en el enunciado (determina H1 a H6). |
| `VIÑETA` | Símbolo `-`, `*` o `+` al inicio de línea (tras la indentación), seguido de un espacio. | `-`, `*`, `+` | Definido en el enunciado. Solo se evalúa al inicio de línea. |
| `INDENT` | Token virtual emitido al aumentar la indentación en exactamente 2 espacios respecto al nivel previo en listas. | `(virtual)` | Definido en el enunciado para abrir sublistas anidadas. |
| `DEDENT` | Token virtual emitido al disminuir la indentación hacia un nivel previo válido en la pila de listas. | `(virtual)` | Definido en el enunciado para cerrar niveles de sublistas. |
| `CITA` | Uno o más símbolos `>` al inicio de línea (admite notación continua `>>` o separada por espacio `> >`). | `>`, `>>`, `> >` | Definido en el enunciado. Su atributo `nivel` guarda la profundidad. |
| `CERCA_CODIGO` | Tres acentos graves (` ``` `) al inicio de línea. Abre y cierra el modo literal de bloque. | ` ```python ` | Definido en el enunciado. Guarda el lenguaje en `info_extra`. |
| `REGLA_HORIZONTAL` | Tres o más guiones (`---`) solos en una línea sin otro contenido. | `---` | Definido en el enunciado. |
| `NEGRITA` | Doble asterisco (`**`). Aplica *maximal munch* para tener prioridad sobre `CURSIVA`. | `**` | Definido en el enunciado. |
| `CURSIVA` | Asterisco simple (`*`) fuera de posición de viñeta de lista. | `*` | Definido en el enunciado. |
| `CODIGO_INLINE` | Acento grave simple (`` ` ``). Delimita un tramo de código literal en línea. | `` ` `` | Definido en el enunciado. |
| `TEXTO` | Secuencia de caracteres planos que no coinciden con delimitadores especiales. | `Compiladores` | Definido en el enunciado. |
| `TEXTO_LITERAL` | Contenido interno sin tokenizar dentro de un bloque de código o código en línea. | `int x = 2 * 3;` | **[Agregado]** Permite encapsular contenido literal sin interpretar `*`, `#` o `>` internos. |
| `SALTO_PARRAFO` | Línea en blanco (vacía o solo espacios) que separa bloques o finaliza un párrafo. | `\n` | Definido en el enunciado. |
| `EOF` | Marca el fin del flujo de tokens del archivo de entrada. | `EOF` | **[Agregado]** Necesario para que el parser LL(1) detecte el fin del documento y valide cierres. |

### 3.2 Diagrama de Estados y Transiciones del AFD Léxico

```text
                     +------------------------+
                     |   ESTADO S0 (INICIO)   |
                     +-----------+------------+
                                 |
      +--------------------------+--------------------------+
      | (Inicio de línea)                                   | (En línea / Párrafo)
      v                                                     v
+-----+------------------------------------+    +-----------+-------------------------+
| Evaluar prefijo e indentación (espacios) |    | Carácter actual ch                  |
+-----+------------------------------------+    +-----------+-------------------------+
      |                                                     |
      +--> Línea vacía ---------> [SALTO_PARRAFO]           +--> '`' -> Buscar cierre '`'
      |                                                     |           |-- Cerrado -> [CODIGO_INLINE] + [TEXTO_LITERAL] + [CODIGO_INLINE]
      +--> "```" ---------------> [CERCA_CODIGO]            |           +-- Sin cerrar -> Error: CODIGO_INLINE_SIN_CERRAR
      |                           Modo Literal hasta "```"  |
      |                           |-- Cerrado -> [TEXTO_LITERAL] + [CERCA_CODIGO]
      |                           +-- EOF -----> Error: BLOQUE_CODIGO_SIN_CERRAR
      |                                                     +--> '*' -> ¿Siguiente es '*'? (Maximal Munch)
      +--> "---" (3+ guiones) --> [REGLA_HORIZONTAL]        |           |-- Sí ("**") -> ¿Tiene cierre "**"?
      |                                                     |           |                |-- Sí -> [NEGRITA]
      +--> '#' (1..N veces)                                 |           |                +-- No -> Error: NEGRITA_SIN_CERRAR
      |    |-- Seguido de ' ' y N<=6 -> [NUMERAL]           |           +-- No ('*')  -> ¿Tiene cierre '*'?
      |    |-- Seguido de ' ' y N>6  -> Error: ENCABEZADO_INVALIDO      |                |-- Sí -> [CURSIVA]
      |    +-- Sin espacio (#texto)  -> Pasa a [TEXTO]      |                +-- No -> Error: CURSIVA_SIN_CERRAR
      |                                                     |
      +--> '>' (1..N veces, con o sin espacio intermedio)   +--> Otro carácter -> Acumular en [TEXTO]
      |    |-- Seguido de ' ' o '>' -> [CITA (nivel=N)]
      |    +-- Pegado a texto (>Cita) -> [CITA (MAL_FORMADA)] -> Error Sintáctico: CITA_MAL_FORMADA
      |
      +--> ('-', '*', '+') + ' '
           |-- Comparar espacios_ini con pila_indent[-1]:
           |   * diff == +2 -> apilar y emitir [INDENT]
           |   * diff > 2   -> emitir [INDENT (INVALIDO)] -> Error Sintáctico: INDENTACION_INVALIDA
           |   * menor      -> desapilar y emitir [DEDENT]
           +-- Emitir [VIÑETA] y pasar resto de línea a AFD En Línea
```

---

## 4. Especificación Sintáctica y Gramática Libre de Contexto (GLC)

### 4.1 Gramática en Notación BNF Factorizada (LL(1))
Símbolo inicial: `<documento>`

```bnf
<documento>        ::= <bloque> <documento_prima>
                     | EOF

<documento_prima>  ::= <bloque> <documento_prima>
                     | EOF

<bloque>           ::= <encabezado>
                     | <parrafo>
                     | <lista>
                     | <cita>
                     | <bloque_codigo>
                     | <regla_horizontal>

<encabezado>       ::= NUMERAL <en_linea>

<parrafo>          ::= <en_linea> SALTO_PARRAFO

<lista>            ::= <item_lista> <lista_prima>

<lista_prima>      ::= <item_lista> <lista_prima>
                     | ε

<item_lista>       ::= VIÑETA <en_linea> <sublista_opc>

<sublista_opc>     ::= <sublista>
                     | ε

<sublista>         ::= INDENT <lista> DEDENT

<cita>             ::= CITA <en_linea> <cita_prima>

<cita_prima>       ::= CITA <en_linea> <cita_prima>
                     | ε

<bloque_codigo>    ::= CERCA_CODIGO TEXTO_LITERAL CERCA_CODIGO

<regla_horizontal> ::= REGLA_HORIZONTAL

<en_linea>         ::= <elemento_linea> <en_linea>
                     | ε

<elemento_linea>   ::= <negrita>
                     | <cursiva>
                     | <codigo_inline>
                     | TEXTO

<negrita>          ::= NEGRITA <en_linea> NEGRITA

<cursiva>          ::= CURSIVA <en_linea> CURSIVA

<codigo_inline>    ::= CODIGO_INLINE TEXTO_LITERAL CODIGO_INLINE
```

### 4.2 Justificación de Ajustes respecto a la Gramática de Referencia 4.6
1. **Factorización por la izquierda en `<lista>`, `<item_lista>` y `<cita>`**: En la gramática de referencia 4.6, producciones como `<lista> ::= <item_lista> <lista> | <item_lista>` e `<item_lista> ::= VIÑETA <en_linea> <sublista> | VIÑETA <en_linea>` comparten el mismo prefijo inicial, lo que impide elegir la regla viendo un solo token de anticipación (`LL(1)`). Se introdujeron los no terminales `<lista_prima>`, `<sublista_opc>` y `<cita_prima>` que pueden derivar en `ε`.
2. **Incorporación de `TEXTO_LITERAL` y `EOF`**: Separa formalmente el texto libre de formato (`TEXTO`) del texto protegido dentro de bloques de código y código en línea (`TEXTO_LITERAL`), y garantiza una condición de parada determinista al llegar a `EOF`.

### 4.3 Conjuntos PRIMERO (FIRST) y SIGUIENTE (FOLLOW)

| No Terminal | PRIMERO (FIRST) | SIGUIENTE (FOLLOW) |
| :--- | :--- | :--- |
| `<documento>` | `{ NUMERAL, VIÑETA, CITA, CERCA_CODIGO, REGLA_HORIZONTAL, NEGRITA, CURSIVA, CODIGO_INLINE, TEXTO, EOF }` | `{ $ }` |
| `<documento_prima>` | `{ NUMERAL, VIÑETA, CITA, CERCA_CODIGO, REGLA_HORIZONTAL, NEGRITA, CURSIVA, CODIGO_INLINE, TEXTO, EOF }` | `{ $ }` |
| `<bloque>` | `{ NUMERAL, VIÑETA, CITA, CERCA_CODIGO, REGLA_HORIZONTAL, NEGRITA, CURSIVA, CODIGO_INLINE, TEXTO }` | `{ NUMERAL, VIÑETA, CITA, CERCA_CODIGO, REGLA_HORIZONTAL, NEGRITA, CURSIVA, CODIGO_INLINE, TEXTO, EOF }` |
| `<encabezado>` | `{ NUMERAL }` | `FOLLOW(<bloque>)` |
| `<parrafo>` | `{ NEGRITA, CURSIVA, CODIGO_INLINE, TEXTO }` | `FOLLOW(<bloque>)` |
| `<lista>` | `{ VIÑETA }` | `FOLLOW(<bloque>) ∪ { DEDENT }` |
| `<lista_prima>` | `{ VIÑETA, ε }` | `FOLLOW(<lista>)` |
| `<item_lista>` | `{ VIÑETA }` | `{ VIÑETA } ∪ FOLLOW(<lista>)` |
| `<sublista_opc>` | `{ INDENT, ε }` | `{ VIÑETA } ∪ FOLLOW(<lista>)` |
| `<sublista>` | `{ INDENT }` | `{ VIÑETA } ∪ FOLLOW(<lista>)` |
| `<cita>` | `{ CITA }` | `FOLLOW(<bloque>)` |
| `<cita_prima>` | `{ CITA, ε }` | `FOLLOW(<cita>)` |
| `<bloque_codigo>` | `{ CERCA_CODIGO }` | `FOLLOW(<bloque>)` |
| `<regla_horizontal>` | `{ REGLA_HORIZONTAL }` | `FOLLOW(<bloque>)` |
| `<en_linea>` | `{ NEGRITA, CURSIVA, CODIGO_INLINE, TEXTO, ε }` | `{ SALTO_PARRAFO, INDENT, DEDENT, VIÑETA, CITA, NUMERAL, CERCA_CODIGO, REGLA_HORIZONTAL, NEGRITA, CURSIVA, EOF }` |
| `<elemento_linea>` | `{ NEGRITA, CURSIVA, CODIGO_INLINE, TEXTO }` | `FIRST(<en_linea>) ∪ FOLLOW(<en_linea>)` |
| `<negrita>` | `{ NEGRITA }` | `FIRST(<en_linea>) ∪ FOLLOW(<en_linea>)` |
| `<cursiva>` | `{ CURSIVA }` | `FIRST(<en_linea>) ∪ FOLLOW(<en_linea>)` |
| `<codigo_inline>` | `{ CODIGO_INLINE }` | `FIRST(<en_linea>) ∪ FOLLOW(<en_linea>)` |

---

## 5. Algoritmo del Parser Descendente Recursivo y Recuperación de Errores

### 5.1 Funcionamiento del Parser Descendente Recursivo
En `AnalizadorSintactico`, cada símbolo no terminal se implementa como un método privado (`_parse_documento`, `_parse_bloque`, `_parse_lista`, etc.). El parser mantiene un puntero de anticipación en `self.token_actual`.
* Cuando se procesa `<en_linea>` dentro de `<negrita>` o `<cursiva>`, el método recibe un conjunto `delimitadores_cierre` (por ejemplo, `{"NEGRITA"}` o `{"NEGRITA", "CURSIVA"}`). Si el token actual coincide con el delimitador de cierre esperado, la recursión de `<en_linea>` finaliza limpiamente (`ε`) y devuelve el control al nodo padre `<negrita>` o `<cursiva>` para que consuma su token de cierre. Esto permite anidar cursivas dentro de negritas y negritas dentro de cursivas sin conflicto.

### 5.2 Estrategia de Recuperación de Errores (Modo Pánico)
El sistema nunca se detiene ante el primer error:
1. **Delimitadores en línea sin cerrar (`NEGRITA_SIN_CERRAR`, `CURSIVA_SIN_CERRAR`, `CODIGO_INLINE_SIN_CERRAR`)**: Si el AFD detecta que un delimitador abierto (`**`, `*` o `` ` ``) no tiene su pareja de cierre antes del fin de línea/bloque, registra el error en `GestorErrores` con la línea y columna exactas de apertura, descarta el delimitador huérfano y continúa tokenizando el resto de la línea como texto normal.
2. **Encabezado inválido (`ENCABEZADO_INVALIDO`)**: Si una línea comienza con 7 o más símbolos `#` seguidos de espacio, se registra el error léxico en la línea actual, se sincroniza saltando al final de la línea y continúa con el siguiente bloque.
3. **Bloque de código sin cerrar (`BLOQUE_CODIGO_SIN_CERRAR`)**: Si se abre ```` ``` ```` y se alcanza `EOF` sin cierre, se reporta la línea de apertura y se cierra el flujo con `EOF`.
4. **Indentación inválida (`INDENTACION_INVALIDA`)**: Si un ítem de lista salta más de 2 espacios de una vez (por ejemplo, de 0 a 4 espacios), el parser registra el error sintáctico en la línea y columna del ítem mal indentado, consume dicho ítem como sincronización y continúa analizando el resto de la lista.
5. **Cita mal formada (`CITA_MAL_FORMADA`)**: Si un símbolo `>` no va seguido de un espacio ni de otro `>` (ej. `>Cita`), el parser reporta el error sintáctico, descarta esa línea de cita defectuosa y continúa con la siguiente línea.