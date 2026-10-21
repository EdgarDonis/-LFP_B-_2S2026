# Manual de Usuario - MarkdownCheck

**Universidad de San Carlos de Guatemala**  
**Facultad de Ingeniería - Escuela de Ingeniería en Ciencias y Sistemas**  
**Curso:** Lenguajes Formales y de Programación (0796) - Sección B+  
**Estudiante:** Edgar Alfredo Donis Llamas - **Carnet:** 202307788  

---

## 1. Requisitos e Instrucciones de Ejecución

### Requisitos del Sistema
* **Sistema Operativo:** Windows 10/11, Linux (Fedora, Ubuntu, Kali, etc.) o macOS.
* **Intérprete:** Python 3.10 o superior (con `tkinter` incluido en la biblioteca estándar).
* **Navegador Web:** Cualquier navegador moderno (Chrome, Firefox, Edge, Brave) para visualizar los 3 reportes HTML.
* **Graphviz (Opcional):** Para compilar el archivo `arbol.dot` a imagen `.png` o `.svg`.

### Cómo Iniciar la Aplicación
1. Abra una terminal en la carpeta raíz del proyecto.
2. Ejecute el siguiente comando:
   ```bash
   python src/main.py
   ```
3. Se abrirá la ventana principal de **MarkdownCheck**.

---

## 2. Descripción de la Interfaz Gráfica

```text
+--------------------------------------------------------------------------------------------------+
|  MarkdownCheck   [Cargar .md] [Guardar .md] [Analizar y Traducir]   [Rep 1] [Rep 2] [Rep 3]      |
+-----------------------------------------+--------------------------------------------------------+
| Editor de Entrada Markdown (.md)        | [Tabla de Tokens] [Tabla de Errores] [Árbol Graphviz]  |
|                                         |                                                        |
| 1  # Guía de Estudio: Compiladores      |  #  | Lexema                 | Tipo          | L | C   |
| 2                                       | ----+------------------------+---------------+---+---  |
| 3  Un **compilador** traduce...         |  1  | #                      | NUMERAL       | 1 | 1   |
| 4                                       |  2  | Guía de Estudio...     | TEXTO         | 1 | 3   |
| 5  ## Fases del compilador              |  3  | Un                     | TEXTO         | 3 | 1   |
| 6  * Análisis léxico                    |  4  | **                     | NEGRITA       | 3 | 4   |
| 7    * Reconoce tokens con un **AFD**   |  5  | compilador             | TEXTO         | 3 | 6   |
+-----------------------------------------+--------------------------------------------------------+
| Estado: Análisis exitoso sin errores: 98 tokens reconocidos. Reportes generados en /reportes.    |
+--------------------------------------------------------------------------------------------------+
```

1. **Barra de Herramientas Superior**:
   * **Cargar .md**: Abre un selector de archivos para cargar cualquier documento `.md` en el editor.
   * **Guardar .md**: Guarda los cambios realizados directamente en el editor de texto.
   * **Analizar y Traducir**: Ejecuta el análisis léxico (AFD), el análisis sintáctico descendente recursivo, llena las tablas, genera el archivo `arbol.dot` y exporta los 3 reportes HTML.
   * **Abrir Reporte 1 (HTML) / Reporte 2 (Estadísticas) / Reporte 3 (Índice)**: Abren cada reporte generado directamente en su navegador web predeterminado.
2. **Panel Izquierdo (Editor de Entrada Markdown)**: Permite escribir, pegar o modificar el documento `.md` con desplazamiento horizontal y vertical.
3. **Panel Derecho (Pestañas de Resultados)**:
   * **Pestaña 1 - Tabla de Tokens (AFD)**: Muestra el número de token, el lexema exacto (incluyendo tokens virtuales `INDENT` y `DEDENT`), el tipo de token, la línea y la columna.
   * **Pestaña 2 - Tabla de Errores**: Si el archivo tiene errores léxicos o sintácticos, muestra el número, lexema, tipo de error, fase (`Léxico` o `Sintáctico`), descripción detallada, línea y columna.
   * **Pestaña 3 - Árbol Graphviz (`arbol.dot`)**: Muestra en vivo el código DOT generado a partir del Árbol de Derivación.

---

## 3. Sintaxis Markdown Soportada

| Elemento Markdown | Sintaxis de Entrada | Traducción HTML | Reglas importantes |
| :--- | :--- | :--- | :--- |
| **Encabezados (H1-H6)** | `# Título` hasta `###### Título` | `<h1>` a `<h6>` | Debe ir al inicio de línea seguido de un espacio. Más de 6 `#` es error léxico. |
| **Párrafos** | Texto separado por línea en blanco | `<p>...</p>` | Líneas consecutivas sin línea en blanco pertenecen al mismo párrafo. |
| **Negrita** | `**texto en negrita**` | `<strong>...</strong>` | Puede contener cursiva adentro (`**negrita *cursiva***`). |
| **Cursiva** | `*texto en cursiva*` | `<em>...</em>` | Puede contener negrita adentro (`*cursiva **negrita***`). |
| **Código en línea** | `` `int x = 1;` `` | `<code>...</code>` | Modo literal: no interpreta `*` ni `**` en su interior. |
| **Listas no ordenadas** | `- ítem`, `* ítem` o `+ ítem` | `<ul><li>...</li></ul>` | Cada nivel de sublista requiere **exactamente 2 espacios** adicionales de indentación. |
| **Citas anidadas** | `> Cita`, `>> Nivel 2` o `> > Nivel 2` | `<blockquote>...</blockquote>` | Debe haber un espacio o un `>` después de cada símbolo `>`. |
| **Bloque de código** | ```` ```lenguaje ... ``` ```` | `<pre><code>...</code></pre>` | Todo el interior se toma como texto literal sin tokenizar. |
| **Regla horizontal** | `---` (3 o más guiones) | `<hr>` | Debe estar sola en su propia línea. |