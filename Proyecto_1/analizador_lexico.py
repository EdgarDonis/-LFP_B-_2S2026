from token_horario import Token, ErrorLexico

class AnalizadorLexico:
    def __init__(self, entrada):
        self.entrada = entrada
        self.posicion = 0
        self.linea = 1
        self.columna = 1
        self.tokens = []
        self.errores = []

        # Diccionario de palabras reservadas requeridas
        # Diccionario de palabras reservadas requeridas y atributos
        self.reservadas = {
            "HORARIO": "PR_HORARIO", "CURSOS": "PR_CURSOS",
            "CATEDRATICOS": "PR_CATEDRATICOS", "AULAS": "PR_AULAS",
            "CLASES": "PR_CLASES", "curso": "PR_CURSO",
            "catedratico": "PR_CATEDRATICO", "aula": "PR_AULA",
            "clase": "PR_CLASE", "con": "PR_CON", "en": "PR_EN",
            "TITULAR": "CAT_TITULAR", "INTERINO": "CAT_INTERINO", "AUXILIAR": "CAT_AUXILIAR",
            "LUNES": "DIA", "MARTES": "DIA", "MIERCOLES": "DIA",
            "JUEVES": "DIA", "VIERNES": "DIA", "SABADO": "DIA",
            # Atributos internos
            "codigo": "ATRIBUTO", "creditos": "ATRIBUTO",
            "categoria": "ATRIBUTO", "capacidad": "ATRIBUTO",
            "edificio": "ATRIBUTO", "dia": "ATRIBUTO",
            "inicio": "ATRIBUTO", "fin": "ATRIBUTO", "seccion": "ATRIBUTO"
        }

    def avanzar(self):
        """Avanza un carácter y actualiza contadores."""
        if self.posicion < len(self.entrada):
            if self.entrada[self.posicion] == '\n':
                self.linea += 1
                self.columna = 1
            else:
                self.columna += 1
            self.posicion += 1

    def analizar(self):
        """Ciclo principal del AFD sin usar funciones de alto nivel de cadenas."""
        while self.posicion < len(self.entrada):
            char = self.entrada[self.posicion]

            # 1. Ignorar espacios en blanco, tabulaciones y retornos de carro
            if char.isspace():
                self.avanzar()
                continue

            # 2. Comentarios de línea (##)
            if char == '#' and self.posicion + 1 < len(self.entrada) and self.entrada[self.posicion + 1] == '#':
                self.avanzar()  # Consume primer #
                self.avanzar()  # Consume segundo #
                while self.posicion < len(self.entrada) and self.entrada[self.posicion] != '\n':
                    self.avanzar()
                continue

            # 3. Cadenas de texto ("...") y Códigos entre comillas
            if char == '"':
                col_inicial = self.columna
                self.avanzar()
                lexema = ""
                while self.posicion < len(self.entrada) and self.entrada[self.posicion] != '"':
                    if self.entrada[self.posicion] == '\n':
                        break  # Prevención de cadenas multilínea
                    lexema += self.entrada[self.posicion]
                    self.avanzar()

                if self.posicion < len(self.entrada) and self.entrada[self.posicion] == '"':
                    self.avanzar()  # Consume la comilla de cierre

                    # --- LÓGICA DE VERIFICACIÓN PARA CÓDIGOS ---
                    letras_o_digitos = 0
                    guiones = 0
                    espacios_u_otros = 0

                    for c in lexema:
                        if c.isalnum():
                          letras_o_digitos += 1
                        elif c == '-':
                            guiones += 1
                        else:
                            espacios_u_otros += 1

                    has_letters = False
                    has_digits = False
                    for c in lexema:
                        if c.isalpha(): has_letters = True
                        if c.isdigit(): has_digits = True

                    # Es un código académico si no tiene espacios y combina letras/números o tiene un guion
                    if espacios_u_otros == 0 and letras_o_digitos > 0 and (
                            (has_letters and has_digits) or guiones > 0):
                        valido = True
                        if guiones != 1:
                             valido = False  # Un código válido debe tener exactamente un guion
                        else:
                            guion_encontrado = False
                            for c in lexema:
                                if c == '-':
                                    guion_encontrado = True
                                elif guion_encontrado:
                                    if not c.isdigit():  # Después del guion solo pueden ir dígitos
                                        valido = False
                                else:
                                    if not c.isalnum():  # Antes del guion van letras/dígitos
                                        valido = False

                        if valido:
                            self.tokens.append(Token(f'"{lexema}"', "CODIGO", self.linea, col_inicial))
                        else:
                            self.errores.append(
                                ErrorLexico(f'"{lexema}"', "CODIGO_MAL_FORMADO", f"Código mal formado: '{lexema}'",
                                            self.linea, col_inicial))
                    else:
                        # Si tiene espacios o no cumple la estructura mínima, es texto normal
                        self.tokens.append(Token(f'"{lexema}"', "CADENA", self.linea, col_inicial))
                else:
                    self.errores.append(ErrorLexico(lexema, "CADENA_SIN_CERRAR",
                        f"Cadena sin cerrar iniciada en línea {self.linea}, columna {col_inicial}",
                                                self.linea, col_inicial))
                continue


            # 4. Alfanuméricos: Palabras Reservadas y Códigos (Letras + guión + dígitos)
            if char.isalpha():
                lexema = ""
                col_inicial = self.columna
                estado_codigo = 0  # 0: leyendo letras, 1: encontró guion, 2: leyendo dígitos
                mal_formado = False

                while self.posicion < len(self.entrada):
                    actual = self.entrada[self.posicion]
                    if actual.isalpha():
                        if estado_codigo == 1 or estado_codigo == 2:
                            mal_formado = True  # Letras después del guion invalida el patrón
                        lexema += actual
                        self.avanzar()
                    elif actual == '-':
                        if estado_codigo == 0:
                            estado_codigo = 1
                        else:
                            mal_formado = True  # Más de un guion es inválido
                        lexema += actual
                        self.avanzar()
                    elif actual.isdigit():
                        if estado_codigo == 1 or estado_codigo == 2:
                            estado_codigo = 2
                        else:
                            mal_formado = True  # Números antes del guion invalida el patrón
                        lexema += actual
                        self.avanzar()
                    else:
                        break  # Fin de la secuencia

                # Evaluación de lo recolectado
                if estado_codigo >= 1:
                    if estado_codigo == 2 and not mal_formado:
                        self.tokens.append(Token(lexema, "CODIGO", self.linea, col_inicial))
                    else:
                        self.errores.append(ErrorLexico(lexema, "CODIGO_MAL_FORMADO",
                                                        f"Código mal formado: '{lexema}' en línea {self.linea}, columna {col_inicial}",
                                                        self.linea, col_inicial))
                elif lexema in self.reservadas:
                    self.tokens.append(Token(lexema, self.reservadas[lexema], self.linea, col_inicial))
                else:
                    # En caso de escribir mal un día como "LNES"
                    self.errores.append(ErrorLexico(lexema, "DIA_NO_RECONOCIDO",
                                                    f"Día o palabra no reconocida: '{lexema}' en línea {self.linea}, columna {col_inicial}",
                                                    self.linea, col_inicial))
                continue

            # 5. Dígitos: Enteros u Horas (HH:MM)
            if char.isdigit():
                lexema = ""
                col_inicial = self.columna

                # Extrae los primeros dígitos
                while self.posicion < len(self.entrada) and self.entrada[self.posicion].isdigit():
                    lexema += self.entrada[self.posicion]
                    self.avanzar()

                # Evalúa si los dígitos son seguidos por un delimitador de hora ':'
                if self.posicion < len(self.entrada) and self.entrada[self.posicion] == ':':
                    lexema += self.entrada[self.posicion]
                    self.avanzar()

                    # Extrae los dígitos de los minutos
                    while self.posicion < len(self.entrada) and self.entrada[self.posicion].isdigit():
                        lexema += self.entrada[self.posicion]
                        self.avanzar()

                    # Validación manual sin usar len() de alto nivel
                    if len(lexema) == 5:
                        # Cálculo aritmético en lugar de int() sobre un sub-string para mayor rigor
                        horas = (int(lexema[0]) * 10) + int(lexema[1])
                        minutos = (int(lexema[3]) * 10) + int(lexema[4])

                        # Rango institucional: 06:00 a 21:00
                        if 6 <= horas <= 21 and 0 <= minutos <= 59:
                            if horas == 21 and minutos > 0:
                                self.errores.append(ErrorLexico(lexema, "HORA_FUERA_DE_RANGO",
                                                                f"Hora fuera de rango en línea {self.linea}, columna {col_inicial}",
                                                                self.linea, col_inicial))
                            else:
                                self.tokens.append(Token(lexema, "HORA", self.linea, col_inicial))
                        else:
                            self.errores.append(ErrorLexico(lexema, "HORA_FUERA_DE_RANGO",
                                                            f"Hora fuera de rango en línea {self.linea}, columna {col_inicial}",
                                                            self.linea, col_inicial))
                    else:
                        self.errores.append(ErrorLexico(lexema, "HORA_FUERA_DE_RANGO",
                                                        f"Hora mal estructurada en línea {self.linea}, columna {col_inicial}",
                                                        self.linea, col_inicial))
                else:
                    # Si no encontró ':', era simplemente un número entero (ej. capacidad del aula)
                    self.tokens.append(Token(lexema, "ENTERO", self.linea, col_inicial))
                continue

            # 6. Símbolos de agrupación y sintaxis ({, }, [, ], :, ,, ;)
            if char in "{}[]:,;":
                self.tokens.append(Token(char, "SIMBOLO", self.linea, self.columna))
                self.avanzar()
                continue

            # 7. Modo Pánico: Carácter fuera del alfabeto
            self.errores.append(ErrorLexico(char, "CARACTER_NO_RECONOCIDO",
                                            f"Carácter no reconocido: '{char}' en línea {self.linea}, columna {self.columna}",
                                            self.linea, self.columna))
            self.avanzar()