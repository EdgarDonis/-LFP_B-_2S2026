# Documento de Casos de Prueba - MarkdownCheck

**Universidad de San Carlos de Guatemala**  
**Facultad de Ingeniería - Escuela de Ingeniería en Ciencias y Sistemas**  
**Curso:** Lenguajes Formales y de Programación (0796) - Sección B+  
**Estudiante:** Edgar Alfredo Donis Llamas - **Carnet:** 202307788  

---

## Caso de Prueba 01: Documento Completo del Auxiliar (`prueba_valida.md`)
* **Objetivo:** Validar el reconocimiento integral de todos los elementos obligatorios, párrafos multilínea, listas de 4 niveles con viñetas mixtas (`*`, `+`, `-`), citas de 3 niveles (`>`, `> >`, `>>>`), anidamiento mutuo negrita/cursiva y falso encabezado `#sinespacio`.
* **Resultado Esperado:** Análisis sin errores (`0` errores). Reporte 1 con jerarquía exacta. Reporte 2 con 4 encabezados (H1..H4), 9 ítems de lista (4 niveles), 4 líneas de cita (3 niveles), 5 negritas, 5 cursivas, 2 códigos inline, 1 bloque de código y 1 regla horizontal.
* **Resultado Obtenido:** Exactamente igual al esperado (`0` errores, 3 reportes HTML y `arbol.dot` generados con éxito). **ESTADO: APROBADO**.

## Caso de Prueba 02: Archivo de Errores Múltiples del Auxiliar (`prueba_errores.md`)
* **Objetivo:** Comprobar la recuperación de errores en **modo pánico** ante los 7 tipos de errores léxicos y sintácticos en una sola pasada.
* **Resultado Esperado:** Detectar los 7 errores sin detener el programa en el primero.
* **Resultado Obtenido:** Se reportaron los 7 errores con precisión del 100% en la Tabla de Errores:
  1. `NEGRITA_SIN_CERRAR` (Léxico) - Línea 3, Columna 20.
  2. `CURSIVA_SIN_CERRAR` (Léxico) - Línea 5, Columna 17.
  3. `CODIGO_INLINE_SIN_CERRAR` (Léxico) - Línea 7, Columna 19.
  4. `ENCABEZADO_INVALIDO` (Léxico) - Línea 9, Columna 1.
  5. `INDENTACION_INVALIDA` (Sintáctico) - Línea 12, Columna 5.
  6. `CITA_MAL_FORMADA` (Sintáctico) - Línea 15, Columna 1.
  7. `BLOQUE_CODIGO_SIN_CERRAR` (Léxico) - Línea 19, Columna 1.
  **ESTADO: APROBADO**.

## Caso de Prueba 03: Ejemplo Oficial del Enunciado (`ejemplo_valido.md`)
* **Objetivo:** Verificar que las métricas del Reporte 2 coincidan con la figura de la sección 4.8 del enunciado.
* **Resultado Esperado:** `0` errores, 2 párrafos, 2 encabezados (1 H1, 1 H2), 8 ítems de lista (3 niveles), 2 líneas de cita (2 niveles), 1 bloque de código, 1 negrita, 1 cursiva, 1 código en línea y 1 regla horizontal.
* **Resultado Obtenido:** Todas las métricas coinciden exactamente con el enunciado. **ESTADO: APROBADO**.

## Caso de Prueba 04: Listas No Ordenadas con 4 Niveles de Anidamiento y Retorno Directo
* **Entrada:** `- Nivel 1` -> `  - Nivel 2` -> `    - Nivel 3` -> `      - Nivel 4` -> `- Regreso a Nivel 1`.
* **Resultado Esperado:** Emisión de 3 tokens `INDENT` progresivos y 3 tokens `DEDENT` juntos antes del último ítem de Nivel 1. Profundidad máxima = 4 niveles.
* **Resultado Obtenido:** Secuencia de tokens `INDENT`/`DEDENT` y HTML `<ul><li>...</li></ul>` generados correctamente. **ESTADO: APROBADO**.

## Caso de Prueba 05: Citas Anidadas en 3 Niveles con Notación Mixta (`>`, `> >` y `>>>`)
* **Entrada:** `> Cita nivel 1` / `> > Cita nivel 2 con espacio` / `>>> Cita nivel 3 continua`.
* **Resultado Esperado:** Traducción a tres `<blockquote>` anidados y profundidad máxima de citas = 3 niveles.
* **Resultado Obtenido:** `<blockquote>` anidados en 3 niveles exactos. **ESTADO: APROBADO**.

## Caso de Prueba 06: Error Léxico Individual - `NEGRITA_SIN_CERRAR`
* **Entrada:** `Texto con **énfasis fuerte abierto sin cerrar.`
* **Resultado Esperado:** Error léxico `NEGRITA_SIN_CERRAR` en línea 1, columna 11.
* **Resultado Obtenido:** Reportado en línea 1, columna 11 con mensaje `"Negrita sin cerrar iniciada en línea 1, columna 11"`. **ESTADO: APROBADO**.

## Caso de Prueba 07: Error Léxico Individual - `CURSIVA_SIN_CERRAR` vs Viñeta `*`
* **Entrada:** `* Ítem válido con *cursiva rota`
* **Resultado Esperado:** Token `VIÑETA` en columna 1 y error `CURSIVA_SIN_CERRAR` en línea 1, columna 19.
* **Resultado Obtenido:** Token `#1 VIÑETA '*'` en L:1, C:1 y Error `CURSIVA_SIN_CERRAR` en L:1, C:19. **ESTADO: APROBADO**.

## Caso de Prueba 08: Error Léxico Individual - `ENCABEZADO_INVALIDO` (7 niveles)
* **Entrada:** `####### Nivel 7 no existe en HTML` seguido de `###### Nivel 6 sí es válido`.
* **Resultado Esperado:** Error `ENCABEZADO_INVALIDO` en línea 1 y reconocimiento normal de `<h6>` en línea 2.
* **Resultado Obtenido:** Error registrado en línea 1 y `<h6>Nivel 6 sí es válido</h6>` generado en el Reporte 1. **ESTADO: APROBADO**.

## Caso de Prueba 09: Error Sintáctico - `INDENTACION_INVALIDA` (Salto Impar)
* **Entrada:** `- Ítem base` seguido de `   - Tres espacios de indentación`.
* **Resultado Esperado:** Error sintáctico `INDENTACION_INVALIDA` en línea 2, columna 4.
* **Resultado Obtenido:** Error `INDENTACION_INVALIDA` reportado en L:2, C:4. **ESTADO: APROBADO**.

## Caso de Prueba 10: Error Sintáctico - `CITA_MAL_FORMADA`
* **Entrada:** `>Texto pegado al símbolo` y `>>Segundo nivel pegado`.
* **Resultado Esperado:** Dos errores sintácticos `CITA_MAL_FORMADA` en líneas 1 y 2.
* **Resultado Obtenido:** Ambos errores reportados en L:1, C:1 y L:2, C:1. **ESTADO: APROBADO**.

## Caso de Prueba 11: Caso Borde - Símbolos Markdown dentro de Bloques de Código y Código Inline
* **Entrada:** ``En consola ejecute `grep "**hola**" #archivo` `` y un bloque ```` ```bash ```` con `#`, `>` y `*`.
* **Resultado Esperado:** `0` errores, `0` encabezados, `0` citas, `0` negritas, `0` cursivas. Todo preservado en `TEXTO_LITERAL`.
* **Resultado Obtenido:** `0` errores; estadísticas muestran `0` encabezados, `0` citas, `1` código en línea y `1` bloque de código. **ESTADO: APROBADO**.

## Caso de Prueba 12: Caso Borde - Documento Sin Encabezados (Reporte 3 Vacío Explicado)
* **Entrada:** `Documento compuesto únicamente por un párrafo con **negrita** y una regla horizontal.`
* **Resultado Esperado:** El Reporte 3 debe mostrar un mensaje explícito indicando que el documento no contiene encabezados.
* **Resultado Obtenido:** El Reporte 3 muestra el mensaje: *"El documento analizado no contiene encabezados (# a ######) para generar la tabla de contenido."* **ESTADO: APROBADO**.