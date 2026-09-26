class Token:
    def __init__(self, lexema, tipo, linea, columna):
        self.lexema = lexema
        self.tipo = tipo
        self.linea = linea
        self.columna = columna

class ErrorLexico:
    def __init__(self, caracter, tipo_error, descripcion, linea, columna):
        self.caracter = caracter
        self.tipo_error = tipo_error
        self.descripcion = descripcion
        self.linea = linea
        self.columna = columna