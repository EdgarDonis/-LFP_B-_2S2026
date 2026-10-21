"""
Módulo de modelos base: Token, ErrorAnalisis, GestorErrores y NodoAST.
Estudiante: Edgar Alfredo Donis Llamas - Carnet: 202307788
Curso: Lenguajes Formales y de Programación - Sección B+
"""

class Token:
    def __init__(self, numero: int, tipo: str, lexema: str, linea: int, columna: int, nivel: int = 0, info_extra: str = ""):
        self.numero = numero
        self.tipo = tipo
        self.lexema = lexema
        self.linea = linea
        self.columna = columna
        self.nivel = nivel          # Nivel para NUMERAL (1..6), CITA (1..N) o INDENT
        self.info_extra = info_extra # Lenguaje en CERCA_CODIGO o banderas de validación

    def __repr__(self):
        return f"Token(#{self.numero}, {self.tipo}, {repr(self.lexema)}, L:{self.linea}, C:{self.columna})"


class ErrorAnalisis:
    def __init__(self, numero: int, lexema: str, tipo_error: str, fase: str, descripcion: str, linea: int, columna: int):
        self.numero = numero
        self.lexema = lexema
        self.tipo_error = tipo_error
        self.fase = fase  # 'Léxico' o 'Sintáctico'
        self.descripcion = descripcion
        self.linea = linea
        self.columna = columna

    def __repr__(self):
        return f"Error(#{self.numero}, {self.tipo_error} [{self.fase}], L:{self.linea}, C:{self.columna}: {self.descripcion})"


class GestorErrores:
    def __init__(self):
        self.errores = []

    def agregar_error(self, lexema: str, tipo_error: str, fase: str, descripcion: str, linea: int, columna: int):
        num = len(self.errores) + 1
        err = ErrorAnalisis(num, lexema, tipo_error, fase, descripcion, linea, columna)
        self.errores.append(err)
        return err

    def tiene_errores(self) -> bool:
        return len(self.errores) > 0

    def limpiar(self):
        self.errores.clear()


class NodoAST:
    def __init__(self, etiqueta: str, es_terminal: bool = False, token: Token = None, valor: str = "", nivel: int = 0):
        self.etiqueta = etiqueta
        self.es_terminal = es_terminal
        self.token = token
        self.valor = valor
        self.nivel = nivel
        self.hijos = []

    def agregar_hijo(self, hijo):
        if hijo is not None:
            self.hijos.append(hijo)
        return self

    def __repr__(self):
        return f"NodoAST({self.etiqueta}, terminal={self.es_terminal}, hijos={len(self.hijos)})"