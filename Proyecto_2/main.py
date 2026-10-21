"""
Interfaz Gráfica Principal en Tkinter para MarkdownCheck (Proyecto 2 - LFP).
Estudiante: Edgar Alfredo Donis Llamas - Carnet: 202307788
"""

import os
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from modelos import GestorErrores
from analizador_lexico import AnalizadorLexico
from analizador_sintactico import AnalizadorSintactico
from generador_html import GeneradorHTML


class AplicacionMarkdownCheck(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MarkdownCheck - Analizador Léxico-Sintáctico de Markdown a HTML | 202307788")
        self.geometry("1220x740")
        self.configure(bg="#f3f4f6")

        self.ruta_archivo_actual = None
        self.nombre_archivo_md = "documento_sin_titulo.md"
        self.directorio_reportes = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reportes"))
        os.makedirs(self.directorio_reportes, exist_ok=True)
        self.rutas_reportes = {}

        self._construir_interfaz()

    def _construir_interfaz(self):
        # Barra de herramientas superior
        barra = tk.Frame(self, bg="#1e293b", height=54, padx=14, pady=8)
        barra.pack(fill=tk.X)

        lbl_titulo = tk.Label(barra, text="MarkdownCheck", fg="#ffffff", bg="#1e293b", font=("Segoe UI", 13, "bold"))
        lbl_titulo.pack(side=tk.LEFT, padx=(0, 20))

        estilo_btn = {"font": ("Segoe UI", 9, "bold"), "bd": 0, "padx": 12, "pady": 6, "cursor": "hand2"}

        tk.Button(barra, text="Cargar .md", bg="#3b82f6", fg="white", command=self.cargar_archivo, **estilo_btn).pack(side=tk.LEFT, padx=4)
        tk.Button(barra, text="Guardar .md", bg="#475569", fg="white", command=self.guardar_archivo, **estilo_btn).pack(side=tk.LEFT, padx=4)
        tk.Button(barra, text="Analizar y Traducir", bg="#16a34a", fg="white", command=self.ejecutar_analisis, **estilo_btn).pack(side=tk.LEFT, padx=12)

        # Botones de acceso directo a los 3 reportes HTML y Graphviz
        tk.Button(barra, text="Abrir Reporte 3 (Índice)", bg="#6366f1", fg="white", command=lambda: self.abrir_reporte("reporte3"), **estilo_btn).pack(side=tk.RIGHT, padx=4)
        tk.Button(barra, text="Abrir Reporte 2 (Estadísticas)", bg="#0284c7", fg="white", command=lambda: self.abrir_reporte("reporte2"), **estilo_btn).pack(side=tk.RIGHT, padx=4)
        tk.Button(barra, text="Abrir Reporte 1 (HTML)", bg="#2563eb", fg="white", command=lambda: self.abrir_reporte("reporte1"), **estilo_btn).pack(side=tk.RIGHT, padx=4)

        # Panel dividido central
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        # Panel izquierdo: Editor Markdown
        frame_izq = ttk.LabelFrame(paned, text=" Editor de Entrada Markdown (.md) ")
        paned.add(frame_izq, weight=2)

        self.txt_editor = tk.Text(frame_izq, wrap=tk.NONE, font=("Consolas", 11), undo=True, bg="#ffffff", fg="#111827", padx=8, pady=8)
        scroll_y_ed = ttk.Scrollbar(frame_izq, orient=tk.VERTICAL, command=self.txt_editor.yview)
        scroll_x_ed = ttk.Scrollbar(frame_izq, orient=tk.HORIZONTAL, command=self.txt_editor.xview)
        self.txt_editor.configure(yscrollcommand=scroll_y_ed.set, xscrollcommand=scroll_x_ed.set)

        scroll_y_ed.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x_ed.pack(side=tk.BOTTOM, fill=tk.X)
        self.txt_editor.pack(fill=tk.BOTH, expand=True)

        # Panel derecho: Pestañas de resultados
        frame_der = ttk.Frame(paned)
        paned.add(frame_der, weight=3)

        self.notebook = ttk.Notebook(frame_der)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Pestaña 1: Tabla de Tokens
        tab_tokens = ttk.Frame(self.notebook)
        self.notebook.add(tab_tokens, text=" Tabla de Tokens (AFD) ")

        cols_tok = ("numero", "lexema", "tipo", "linea", "columna")
        self.tabla_tokens = ttk.Treeview(tab_tokens, columns=cols_tok, show="headings")
        self.tabla_tokens.heading("numero", text="#")
        self.tabla_tokens.heading("lexema", text="Lexema")
        self.tabla_tokens.heading("tipo", text="Tipo de Token")
        self.tabla_tokens.heading("linea", text="Línea")
        self.tabla_tokens.heading("columna", text="Columna")

        self.tabla_tokens.column("numero", width=55, anchor=tk.CENTER)
        self.tabla_tokens.column("lexema", width=260, anchor=tk.W)
        self.tabla_tokens.column("tipo", width=160, anchor=tk.CENTER)
        self.tabla_tokens.column("linea", width=70, anchor=tk.CENTER)
        self.tabla_tokens.column("columna", width=70, anchor=tk.CENTER)

        scroll_tok = ttk.Scrollbar(tab_tokens, orient=tk.VERTICAL, command=self.tabla_tokens.yview)
        self.tabla_tokens.configure(yscrollcommand=scroll_tok.set)
        scroll_tok.pack(side=tk.RIGHT, fill=tk.Y)
        self.tabla_tokens.pack(fill=tk.BOTH, expand=True)

        # Pestaña 2: Tabla de Errores Léxicos y Sintácticos
        tab_errores = ttk.Frame(self.notebook)
        self.notebook.add(tab_errores, text=" Tabla de Errores ")

        cols_err = ("numero", "lexema", "tipo", "fase", "descripcion", "linea", "columna")
        self.tabla_errores = ttk.Treeview(tab_errores, columns=cols_err, show="headings")
        self.tabla_errores.heading("numero", text="#")
        self.tabla_errores.heading("lexema", text="Lexema")
        self.tabla_errores.heading("tipo", text="Tipo de Error")
        self.tabla_errores.heading("fase", text="Fase")
        self.tabla_errores.heading("descripcion", text="Descripción")
        self.tabla_errores.heading("linea", text="Línea")
        self.tabla_errores.heading("columna", text="Columna")

        self.tabla_errores.column("numero", width=45, anchor=tk.CENTER)
        self.tabla_errores.column("lexema", width=90, anchor=tk.CENTER)
        self.tabla_errores.column("tipo", width=175, anchor=tk.W)
        self.tabla_errores.column("fase", width=85, anchor=tk.CENTER)
        self.tabla_errores.column("descripcion", width=280, anchor=tk.W)
        self.tabla_errores.column("linea", width=60, anchor=tk.CENTER)
        self.tabla_errores.column("columna", width=65, anchor=tk.CENTER)

        scroll_err = ttk.Scrollbar(tab_errores, orient=tk.VERTICAL, command=self.tabla_errores.yview)
        self.tabla_errores.configure(yscrollcommand=scroll_err.set)
        scroll_err.pack(side=tk.RIGHT, fill=tk.Y)
        self.tabla_errores.pack(fill=tk.BOTH, expand=True)

        # Pestaña 3: Árbol de Derivación (Graphviz DOT)
        tab_dot = ttk.Frame(self.notebook)
        self.notebook.add(tab_dot, text=" Árbol Graphviz (arbol.dot) ")
        self.txt_dot = tk.Text(tab_dot, wrap=tk.NONE, font=("Consolas", 10), bg="#1e1e1e", fg="#d4d4d4")
        self.txt_dot.pack(fill=tk.BOTH, expand=True)

        # Barra de estado inferior
        self.lbl_estado = tk.Label(self, text="Listo. Cargue un archivo .md o escriba en el editor.", anchor=tk.W, bg="#e2e8f0", fg="#1e293b", padx=12, pady=5)
        self.lbl_estado.pack(fill=tk.X, side=tk.BOTTOM)

    def cargar_archivo(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo Markdown",
            filetypes=[("Archivos Markdown", "*.md"), ("Todos los archivos", "*.*")]
        )
        if not ruta:
            return
        if not os.path.exists(ruta):
            messagebox.showerror("Error", "El archivo seleccionado no existe.")
            return
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                contenido = f.read()
            self.ruta_archivo_actual = ruta
            self.nombre_archivo_md = os.path.basename(ruta)
            self.txt_editor.delete("1.0", tk.END)
            self.txt_editor.insert("1.0", contenido)
            self.lbl_estado.config(text=f"Archivo cargado: {self.nombre_archivo_md}")
        except Exception as e:
            messagebox.showerror("Error de lectura", f"No se pudo leer el archivo:\n{e}")

    def guardar_archivo(self):
        ruta = self.ruta_archivo_actual
        if not ruta:
            ruta = filedialog.asksaveasfilename(
                title="Guardar archivo Markdown",
                defaultextension=".md",
                filetypes=[("Archivos Markdown", "*.md")]
            )
        if ruta:
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(self.txt_editor.get("1.0", "end-1c"))
            self.ruta_archivo_actual = ruta
            self.nombre_archivo_md = os.path.basename(ruta)
            self.lbl_estado.config(text=f"Archivo guardado en: {ruta}")

    def ejecutar_analisis(self):
        texto_md = self.txt_editor.get("1.0", "end-1c")

        # Limpiar tablas previas
        for item in self.tabla_tokens.get_children():
            self.tabla_tokens.delete(item)
        for item in self.tabla_errores.get_children():
            self.tabla_errores.delete(item)
        self.txt_dot.delete("1.0", tk.END)

        gestor_err = GestorErrores()
        lexico = AnalizadorLexico(texto_md, gestor_err)
        sintactico = AnalizadorSintactico(lexico, gestor_err)
        ast = sintactico.analizar()

        # Llenar tabla de tokens
        tokens_visibles = lexico.obtener_tokens_visibles()
        for t in tokens_visibles:
            lex_mostrar = t.lexema.replace("\n", "\\n")
            self.tabla_tokens.insert("", tk.END, values=(t.numero, lex_mostrar, t.tipo, t.linea, t.columna))

        # Llenar tabla de errores
        for err in gestor_err.errores:
            self.tabla_errores.insert("", tk.END, values=(
                err.numero, err.lexema, err.tipo_error, err.fase, err.descripcion, err.linea, err.columna
            ))

        # Generar arbol.dot
        ruta_dot = os.path.join(self.directorio_reportes, "arbol.dot")
        codigo_dot = sintactico.generar_dot(ruta_dot)
        self.txt_dot.insert("1.0", codigo_dot)

        # Generar los 3 reportes HTML si no hay errores (o aun en modo pánico para inspección)
        generador = GeneradorHTML(ast, self.nombre_archivo_md)
        self.rutas_reportes = generador.generar_tres_reportes(self.directorio_reportes)

        if gestor_err.tiene_errores():
            self.notebook.select(1)  # Mostrar pestaña de errores
            self.lbl_estado.config(
                text=f"Análisis finalizado con {len(gestor_err.errores)} errores y {len(tokens_visibles)} tokens reconocidos."
            )
            messagebox.showwarning(
                "Errores detectados",
                f"Se detectaron {len(gestor_err.errores)} errores durante el análisis (modo pánico).\nRevise la pestaña 'Tabla de Errores'."
            )
        else:
            self.notebook.select(0)
            self.lbl_estado.config(
                text=f"Análisis exitoso sin errores: {len(tokens_visibles)} tokens reconocidos. Reportes HTML y arbol.dot generados en /reportes."
            )
            messagebox.showinfo(
                "Análisis Completado",
                "Análisis léxico y sintáctico completado sin errores.\nLos 3 reportes HTML y arbol.dot fueron generados exitosamente."
            )

    def abrir_reporte(self, clave_reporte: str):
        if clave_reporte not in self.rutas_reportes or not os.path.exists(self.rutas_reportes[clave_reporte]):
            messagebox.showinfo("Aviso", "Primero ejecute 'Analizar y Traducir' para generar los reportes.")
            return
        webbrowser.open(f"file://{os.path.abspath(self.rutas_reportes[clave_reporte])}")


if __name__ == "__main__":
    app = AplicacionMarkdownCheck()
    app.mainloop()