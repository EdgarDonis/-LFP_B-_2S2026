"""
Módulo de Análisis Léxico mediante Autómata Finito Determinista (AFD) manual.
Prohibido el uso del módulo 're'.
Estudiante: Edgar Alfredo Donis Llamas - Carnet: 202307788
"""

from modelos import Token, GestorErrores


class AnalizadorLexico:
    def __init__(self, texto: str, gestor_errores: GestorErrores = None):
        self.texto = texto.replace("\r\n", "\n").replace("\r", "\n")
        self.gestor_errores = gestor_errores if gestor_errores is not None else GestorErrores()
        self.tokens = []
        self.pos_token_actual = 0
        self.contador_tokens = 0

        texto_limpio = self.texto[:-1] if self.texto.endswith("\n") else self.texto
        self.lineas = texto_limpio.split("\n") if texto_limpio else []
        self.en_lista = False
        self.pila_indent = [0]
        self.parrafo_abierto = False

        self._tokenizar_documento()

    def _emitir_token(self, tipo: str, lexema: str, linea: int, columna: int, nivel: int = 0, info_extra: str = "") -> Token:
        self.contador_tokens += 1
        tok = Token(self.contador_tokens, tipo, lexema, linea, columna, nivel, info_extra)
        self.tokens.append(tok)
        return tok

    def _cerrar_listas_abiertas(self, linea_actual: int):
        while len(self.pila_indent) > 1:
            self.pila_indent.pop()
            self._emitir_token("DEDENT", "(virtual)", linea_actual, 1, nivel=self.pila_indent[-1])
        self.en_lista = False

    def _es_solo_espacios(self, cadena: str) -> bool:
        for c in cadena:
            if c not in (" ", "\t"):
                return False
        return True

    def _contar_espacios_inicio(self, cadena: str) -> int:
        cont = 0
        for c in cadena:
            if c == " ":
                cont += 1
            elif c == "\t":
                cont += 2
            else:
                break
        return cont

    def _es_regla_horizontal(self, cadena: str) -> bool:
        limpia = cadena.strip(" ")
        if len(limpia) < 3:
            return False
        for c in limpia:
            if c != "-":
                return False
        return True

    def _tokenizar_en_linea(self, linea_str: str, num_linea_1based: int, col_inicio_1based: int):
        """
        AFD para elementos en línea: NEGRITA (**), CURSIVA (*), CODIGO_INLINE (`) y TEXTO.
        Soporta anidamiento mutuo (**negrita con *cursiva* adentro** y viceversa) y modo literal en `codigo`.
        """
        n = len(linea_str)
        i = 0
        buffer_texto = []
        col_inicio_texto = col_inicio_1based

        def vaciar_texto():
            nonlocal buffer_texto
            if buffer_texto:
                lex = "".join(buffer_texto)
                self._emitir_token("TEXTO", lex, num_linea_1based, col_inicio_texto)
                buffer_texto = []

        negrita_abierta = False
        cursiva_abierta = False

        while i < n:
            ch = linea_str[i]
            col_actual = col_inicio_1based + i

            # 1. Código en línea (`texto`): modo literal sin interpretar * ni ** adentro
            if ch == "`":
                cierre = -1
                j = i + 1
                while j < n:
                    if linea_str[j] == "`":
                        cierre = j
                        break
                    j += 1

                if cierre != -1:
                    vaciar_texto()
                    self._emitir_token("CODIGO_INLINE", "`", num_linea_1based, col_actual)
                    contenido_cod = linea_str[i + 1:cierre]
                    if len(contenido_cod) > 0:
                        self._emitir_token("TEXTO_LITERAL", contenido_cod, num_linea_1based, col_actual + 1)
                    self._emitir_token("CODIGO_INLINE", "`", num_linea_1based, col_inicio_1based + cierre)
                    i = cierre + 1
                    col_inicio_texto = col_inicio_1based + i
                    continue
                else:
                    vaciar_texto()
                    msg = f"Código en línea sin cerrar iniciado en línea {num_linea_1based}, columna {col_actual}"
                    self.gestor_errores.agregar_error("`", "CODIGO_INLINE_SIN_CERRAR", "Léxico", msg, num_linea_1based, col_actual)
                    i += 1
                    col_inicio_texto = col_inicio_1based + i
                    continue

            # 2. Negrita (**): Maximal munch sobre *
            if ch == "*" and (i + 1 < n) and linea_str[i + 1] == "*":
                if negrita_abierta:
                    vaciar_texto()
                    self._emitir_token("NEGRITA", "**", num_linea_1based, col_actual)
                    negrita_abierta = False
                    i += 2
                    col_inicio_texto = col_inicio_1based + i
                    continue
                else:
                    cierre = -1
                    j = i + 2
                    en_bt = False
                    while j < n - 1:
                        if linea_str[j] == "`":
                            en_bt = not en_bt
                        elif not en_bt and linea_str[j] == "*" and linea_str[j + 1] == "*":
                            cierre = j
                            break
                        j += 1

                    if cierre != -1:
                        vaciar_texto()
                        self._emitir_token("NEGRITA", "**", num_linea_1based, col_actual)
                        negrita_abierta = True
                        i += 2
                        col_inicio_texto = col_inicio_1based + i
                        continue
                    else:
                        vaciar_texto()
                        msg = f"Negrita sin cerrar iniciada en línea {num_linea_1based}, columna {col_actual}"
                        self.gestor_errores.agregar_error("**", "NEGRITA_SIN_CERRAR", "Léxico", msg, num_linea_1based, col_actual)
                        i += 2
                        col_inicio_texto = col_inicio_1based + i
                        continue

            # 3. Cursiva (*)
            if ch == "*":
                if cursiva_abierta:
                    vaciar_texto()
                    self._emitir_token("CURSIVA", "*", num_linea_1based, col_actual)
                    cursiva_abierta = False
                    i += 1
                    col_inicio_texto = col_inicio_1based + i
                    continue
                else:
                    cierre = -1
                    j = i + 1
                    en_bt = False
                    while j < n:
                        if linea_str[j] == "`":
                            en_bt = not en_bt
                            j += 1
                            continue
                        if not en_bt and linea_str[j] == "*":
                            if (j + 1 < n) and linea_str[j + 1] == "*":
                                j += 2
                                continue
                            else:
                                cierre = j
                                break
                        j += 1

                    if cierre != -1:
                        vaciar_texto()
                        self._emitir_token("CURSIVA", "*", num_linea_1based, col_actual)
                        cursiva_abierta = True
                        i += 1
                        col_inicio_texto = col_inicio_1based + i
                        continue
                    else:
                        vaciar_texto()
                        msg = f"Cursiva sin cerrar iniciada en línea {num_linea_1based}, columna {col_actual}"
                        self.gestor_errores.agregar_error("*", "CURSIVA_SIN_CERRAR", "Léxico", msg, num_linea_1based, col_actual)
                        i += 1
                        col_inicio_texto = col_inicio_1based + i
                        continue

            # 4. Carácter de texto general
            if not buffer_texto:
                col_inicio_texto = col_actual
            buffer_texto.append(ch)
            i += 1

        vaciar_texto()

    def _tokenizar_documento(self):
        total_lineas = len(self.lineas)
        idx = 0

        while idx < total_lineas:
            linea = self.lineas[idx]
            num_linea = idx + 1

            # 1. Línea vacía -> SALTO_PARRAFO
            if self._es_solo_espacios(linea):
                if self.parrafo_abierto:
                    self._emitir_token("SALTO_PARRAFO", "\\n", num_linea, 1)
                    self.parrafo_abierto = False
                if self.en_lista:
                    self._cerrar_listas_abiertas(num_linea)
                idx += 1
                continue

            # 2. Bloque de código (```) en modo literal
            espacios_ini = self._contar_espacios_inicio(linea)
            resto_ini = linea[espacios_ini:]
            if resto_ini.startswith("```"):
                if self.parrafo_abierto:
                    self._emitir_token("SALTO_PARRAFO", "\\n", num_linea, 1)
                    self.parrafo_abierto = False
                if self.en_lista:
                    self._cerrar_listas_abiertas(num_linea)

                col_cerca = espacios_ini + 1
                lenguaje = resto_ini[3:].strip()
                lexema_apertura = resto_ini.strip()

                idx_cierre = -1
                k = idx + 1
                while k < total_lineas:
                    if self.lineas[k].strip() == "```":
                        idx_cierre = k
                        break
                    k += 1

                if idx_cierre != -1:
                    self._emitir_token("CERCA_CODIGO", lexema_apertura, num_linea, col_cerca, info_extra=lenguaje)
                    lineas_codigo = self.lineas[idx + 1:idx_cierre]
                    contenido_literal = "\n".join(lineas_codigo)
                    self._emitir_token("TEXTO_LITERAL", contenido_literal, num_linea + 1 if idx + 1 < idx_cierre else num_linea, 1)
                    col_cierre = self._contar_espacios_inicio(self.lineas[idx_cierre]) + 1
                    self._emitir_token("CERCA_CODIGO", "```", idx_cierre + 1, col_cierre)
                    idx = idx_cierre + 1
                    continue
                else:
                    msg = f"Bloque de código sin cerrar iniciado en línea {num_linea}"
                    self.gestor_errores.agregar_error("```", "BLOQUE_CODIGO_SIN_CERRAR", "Léxico", msg, num_linea, col_cerca)
                    idx = total_lineas
                    break

            # 3. Regla horizontal (---)
            if self._es_regla_horizontal(linea):
                if self.parrafo_abierto:
                    self._emitir_token("SALTO_PARRAFO", "\\n", num_linea, 1)
                    self.parrafo_abierto = False
                if self.en_lista:
                    self._cerrar_listas_abiertas(num_linea)
                self._emitir_token("REGLA_HORIZONTAL", linea.strip(), num_linea, 1)
                idx += 1
                continue

            # 4. Encabezados (# a ###### seguidos de espacio)
            if linea.startswith("#"):
                cant_num = 0
                for c in linea:
                    if c == "#":
                        cant_num += 1
                    else:
                        break
                if cant_num < len(linea) and linea[cant_num] == " ":
                    if self.parrafo_abierto:
                        self._emitir_token("SALTO_PARRAFO", "\\n", num_linea, 1)
                        self.parrafo_abierto = False
                    if self.en_lista:
                        self._cerrar_listas_abiertas(num_linea)

                    if cant_num > 6:
                        lex_err = linea[:cant_num]
                        msg = f"Encabezado inválido en línea {num_linea}: máximo 6 niveles"
                        self.gestor_errores.agregar_error(lex_err, "ENCABEZADO_INVALIDO", "Léxico", msg, num_linea, 1)
                        idx += 1
                        continue
                    else:
                        lex_num = linea[:cant_num]
                        self._emitir_token("NUMERAL", lex_num, num_linea, 1, nivel=cant_num)
                        contenido_enc = linea[cant_num + 1:]
                        self._tokenizar_en_linea(contenido_enc, num_linea, cant_num + 2)
                        idx += 1
                        continue

            # 5. Citas (> o >> o > > al inicio de línea)
            if linea.startswith(">"):
                if self.parrafo_abierto:
                    self._emitir_token("SALTO_PARRAFO", "\\n", num_linea, 1)
                    self.parrafo_abierto = False
                if self.en_lista:
                    self._cerrar_listas_abiertas(num_linea)

                j = 0
                n_lin = len(linea)
                nivel_cita = 0
                mal_formada = False
                while j < n_lin:
                    if linea[j] == ">":
                        nivel_cita += 1
                        j += 1
                        if j < n_lin and linea[j] not in (">", " "):
                            mal_formada = True
                            break
                        if j < n_lin and linea[j] == " ":
                            j += 1
                            if j < n_lin and linea[j] != ">":
                                break
                    else:
                        break

                lex_cita = linea[:j].rstrip(" ")
                if mal_formada:
                    self._emitir_token("CITA", linea[:j + 1], num_linea, 1, nivel=nivel_cita, info_extra="MAL_FORMADA")
                    self._tokenizar_en_linea(linea[j:], num_linea, j + 1)
                else:
                    self._emitir_token("CITA", lex_cita, num_linea, 1, nivel=nivel_cita)
                    contenido_cita = linea[j:]
                    if contenido_cita:
                        self._tokenizar_en_linea(contenido_cita, num_linea, j + 1)
                idx += 1
                continue

            # 6. Listas no ordenadas (-, *, + seguidos de espacio)
            if len(resto_ini) >= 2 and resto_ini[0] in ("-", "*", "+") and resto_ini[1] == " ":
                if self.parrafo_abierto:
                    self._emitir_token("SALTO_PARRAFO", "\\n", num_linea, 1)
                    self.parrafo_abierto = False

                col_vineta = espacios_ini + 1
                simbolo_vineta = resto_ini[0]

                if not self.en_lista:
                    self.en_lista = True
                    self.pila_indent = [0]

                indent_actual = self.pila_indent[-1]
                if espacios_ini > indent_actual:
                    diff = espacios_ini - indent_actual
                    if diff == 2:
                        self.pila_indent.append(espacios_ini)
                        self._emitir_token("INDENT", "(virtual)", num_linea, col_vineta, nivel=len(self.pila_indent) - 1)
                    else:
                        self._emitir_token("INDENT", "(virtual)", num_linea, col_vineta, nivel=-1, info_extra=f"INVALIDO:{espacios_ini}")
                elif espacios_ini < indent_actual:
                    while len(self.pila_indent) > 1 and self.pila_indent[-1] > espacios_ini:
                        self.pila_indent.pop()
                        self._emitir_token("DEDENT", "(virtual)", num_linea, col_vineta, nivel=self.pila_indent[-1])
                    if self.pila_indent[-1] != espacios_ini:
                        self._emitir_token("INDENT", "(virtual)", num_linea, col_vineta, nivel=-1, info_extra=f"INVALIDO:{espacios_ini}")

                self._emitir_token("VIÑETA", simbolo_vineta, num_linea, col_vineta)
                contenido_item = resto_ini[2:]
                self._tokenizar_en_linea(contenido_item, num_linea, col_vineta + 2)
                idx += 1
                continue

            # 7. Párrafos (soporta múltiples líneas consecutivas en el mismo párrafo)
            if self.en_lista:
                self._cerrar_listas_abiertas(num_linea)

            if self.parrafo_abierto:
                self._emitir_token("TEXTO", " ", num_linea, 1)

            self.parrafo_abierto = True
            self._tokenizar_en_linea(linea, num_linea, 1)
            idx += 1

        linea_final = total_lineas if total_lineas > 0 else 1
        if self.parrafo_abierto:
            self._emitir_token("SALTO_PARRAFO", "\\n", linea_final, 1)
            self.parrafo_abierto = False
        if self.en_lista:
            self._cerrar_listas_abiertas(linea_final)

        self._emitir_token("EOF", "EOF", linea_final, 1)

    def siguiente_token(self) -> Token:
        if self.pos_token_actual < len(self.tokens):
            tok = self.tokens[self.pos_token_actual]
            self.pos_token_actual += 1
            return tok
        return self.tokens[-1] if self.tokens else Token(0, "EOF", "EOF", 1, 1)

    def obtener_tokens_visibles(self):
        return [t for t in self.tokens if t.tipo != "EOF"]