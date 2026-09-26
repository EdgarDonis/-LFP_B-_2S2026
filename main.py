#Proyecto #1: HorarioScript, Analizador Léxico para horarios Académicos

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from analizador_lexico import AnalizadorLexico
from generador_reportes import GeneradorReportes


class AplicacionHorario:
    def __init__(self, root):
        self.root = root
        self.root.title("HorarioScript - Analizador Léxico")
        self.root.geometry("1100x700")
        self.lexer = None

        # Barra de botones
        frame_botones = tk.Frame(root, pady=10)
        frame_botones.pack(fill="x")

        tk.Button(frame_botones, text="Cargar Archivo", width=15, command=self.cargar_archivo).pack(side="left",
                                                                                                    padx=10)
        tk.Button(frame_botones, text="Analizar Léxico", width=15, bg="#4CAF50", fg="white",
                  command=self.analizar_texto).pack(side="left", padx=10)
        tk.Button(frame_botones, text="Generar Reportes", width=15, bg="#2196F3", fg="white",
                  command=self.generar_reportes).pack(side="left", padx=10)

        # Área de texto central para editar el código
        frame_texto = tk.LabelFrame(root, text="Código Fuente HorarioScript", padx=5, pady=5)
        frame_texto.pack(fill="both", expand=True, padx=10, pady=5)

        self.area_texto = tk.Text(frame_texto, height=15, font=("Consolas", 11))
        self.area_texto.pack(fill="both", expand=True)

        # Pestañas inferiores para resultados
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Configuración Tabla Tokens
        self.frame_tokens = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_tokens, text='Tabla de Tokens (100%)')
        self.tree_tokens = ttk.Treeview(self.frame_tokens, columns=("No", "Lexema", "Tipo", "Fila", "Col"),
                                        show='headings')
        for col in ("No", "Lexema", "Tipo", "Fila", "Col"):
            self.tree_tokens.heading(col, text=col)
            self.tree_tokens.column(col, anchor="center")
        self.tree_tokens.pack(fill="both", expand=True)

        # Configuración Tabla Errores
        self.frame_errores = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_errores, text='Tabla de Errores (Recuperación)')
        self.tree_errores = ttk.Treeview(self.frame_errores,
                                         columns=("No", "Carácter/Lexema", "Tipo", "Descripción", "Fila", "Col"),
                                         show='headings')
        for col in ("No", "Carácter/Lexema", "Tipo", "Descripción", "Fila", "Col"):
            self.tree_errores.heading(col, text=col)
            self.tree_errores.column(col, anchor="center")
        self.tree_errores.pack(fill="both", expand=True)

    def cargar_archivo(self):
        ruta = filedialog.askopenfilename(filetypes=[("Archivos Horario", "*.hor")])
        if ruta:
            try:
                with open(ruta, 'r', encoding='utf-8') as archivo:
                    self.area_texto.delete("1.0", "end")
                    self.area_texto.insert("end", archivo.read())
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo leer el archivo: {e}")

    def analizar_texto(self):
        entrada = self.area_texto.get("1.0", "end")
        self.lexer = AnalizadorLexico(entrada)
        self.lexer.analizar()

        # Limpiar tablas
        self.tree_tokens.delete(*self.tree_tokens.get_children())
        self.tree_errores.delete(*self.tree_errores.get_children())

        # Llenar tokens
        for i, token in enumerate(self.lexer.tokens, 1):
            self.tree_tokens.insert("", "end", values=(i, token.lexema, token.tipo, token.linea, token.columna))

        # Llenar errores
        for i, error in enumerate(self.lexer.errores, 1):
            self.tree_errores.insert("", "end",
                                     values=(i, error.caracter, error.tipo_error, error.descripcion, error.linea,
                                             error.columna))

        if self.lexer.errores:
            messagebox.showwarning("Análisis Finalizado",
                                   f"Se encontraron {len(self.lexer.errores)} errores léxicos. Revisa la pestaña de Errores.")
        else:
            messagebox.showinfo("Análisis Finalizado", "Análisis léxico exitoso. 0 errores encontrados.")

    def generar_reportes(self):
        if not self.lexer or not self.lexer.tokens:
            messagebox.showerror("Error", "Primero debes ejecutar el Análisis Léxico.")
            return

        reportes = GeneradorReportes(self.lexer.tokens, self.lexer.errores)
        reportes.generar_todos()
        messagebox.showinfo("Éxito", "Reportes HTML generados en la carpeta del proyecto.")


if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionHorario(root)
    root.mainloop()