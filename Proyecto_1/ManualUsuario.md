# MANUAL DE USUARIO: HorarioScript

**UNIVERSIDAD DE SAN CARLOS DE GUATEMALA**  
**Facultad de Ingeniería**  
**Escuela de Ingeniería en Ciencias y Sistemas**  
**Lenguajes Formales y de Programación - Segundo Semestre 2026**  
**Proyecto 1**  
**Edgar Alfredo Donis Llamas - 202307788**
---

## 1. Introducción
HorarioScript es una herramienta de escritorio diseñada para analizar la programación académica a través de archivos de texto con extensión `.hor`[cite: 1]. Este programa valida la estructura léxica del documento, identifica errores de escritura y genera reportes visuales para detectar choques de horario de forma automática[cite: 1].

## 2. Ejecución de la Aplicación
Para iniciar el sistema, asegúrese de tener Python 3.10 o superior instalado.
1. Abra la consola de comandos (CMD o PowerShell).
2. Navegue hasta la carpeta raíz del proyecto.
3. Ejecute el comando: `python main.py`

## 3. Interfaz Principal
Al iniciar, visualizará la ventana principal de la aplicación, compuesta por tres áreas clave:
1. **Barra de Controles:** Botones para cargar archivos, ejecutar el análisis y generar los reportes[cite: 1].
2. **Editor de Código:** Área central donde se muestra el texto del archivo cargado. Permite la edición manual en tiempo real[cite: 1].
3. **Panel de Resultados:** Pestañas inferiores que desglosan las tablas de validación léxica[cite: 1].

![pantallaPrincipal.png](Documentaci%C3%B3n/pantallaPrincipal.png)

## 4. Carga y Análisis de Archivos
Haga clic en el botón **"Cargar Archivo"** y seleccione un documento con la extensión `.hor`[cite: 1]. El lenguaje HorarioScript reconoce bloques de configuración estructurados mediante llaves `{}` y corchetes `[]`[cite: 1].

Una vez cargado el texto, presione **"Analizar Léxico"**. El sistema evaluará el documento completo de principio a fin.

![cargadearchivos.png](Documentaci%C3%B3n/cargadearchivos.png)  

## 5. Interpretación de Resultados
La aplicación no se detiene si encuentra un error, sino que recopila toda la información (modo de recuperación) para presentarla detalladamente[cite: 1].
* **Tabla de Tokens:** Muestra todos los elementos válidos reconocidos (Palabras reservadas, códigos, cadenas, horas, días), indicando la fila y columna exacta de su aparición[cite: 1].
* **Tabla de Errores (Recuperación):** Si el archivo contiene caracteres inválidos o estructuras mal formadas (como códigos sin el formato correcto o cadenas sin cerrar), se listarán en esta pestaña con una descripción detallada y su posición exacta para facilitar su corrección[cite: 1].

![archivoanalizado.png](Documentaci%C3%B3n/archivoanalizado.png)

## 6. Generación de Reportes
Al hacer clic en **"Generar Reportes"**, el sistema exportará tres documentos en formato HTML en la misma carpeta del proyecto. Puede abrirlos en su navegador web predeterminado[cite: 1]:
![ReporteGenerado.png](Documentaci%C3%B3n/ReporteGenerado.png)
### Reporte 1: Horario Semanal
Presenta la agenda de clases programadas. Si el sistema detecta que un mismo catedrático o aula tienen dos clases al mismo tiempo, la fila se resaltará en color rojo marcando un "CHOQUE DETECTADO"[cite: 1].

![reporte1.png](Documentaci%C3%B3n/reporte1.png) 

### Reporte 2: Carga de Catedráticos
Clasifica a los docentes registrados según la cantidad de bloques que imparten, aplicando alertas de color según su nivel de carga (BAJA, NORMAL, ALTA, SATURADA)[cite: 1].

![reporte2.png](Documentaci%C3%B3n/reporte2.png)

### Reporte 3: Estadístico General
Ofrece un resumen ejecutivo con los indicadores clave del ciclo, incluyendo el conteo total de clases, choques identificados y una tabla ordenada con la ocupación porcentual de las aulas[cite: 1].

![reporte3.png](Documentaci%C3%B3n/reporte3.png)