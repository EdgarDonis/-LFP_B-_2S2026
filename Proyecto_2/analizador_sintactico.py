"""
Módulo de Análisis Sintáctico mediante Parser Descendente Recursivo LL(1).
Construye el Árbol de Derivación (AST) y exporta el código Graphviz (arbol.dot).
Estudiante: Edgar Alfredo Donis Llamas - Carnet: 202307788
"""

from modelos import Token, GestorErrores, NodoAST
from analizador_lexico import AnalizadorLexico


class AnalizadorSintactico:
    def __init__(self, lexico: AnalizadorLexico, gestor_errores: GestorErrores = None):
        self.lexico = lexico
        self.gestor_errores = gestor_errores if gestor_errores is not None else lexico.gestor_errores
        self.token_actual: Token = self.lexico.siguiente_token()
        self.arbol_ast: NodoAST = None

    def _avanzar(self) -> Token:
        tok_previo = self.token_actual
        self.token_actual = self.lexico.siguiente_token()
        return tok_previo

    def _coincidir(self, tipo_esperado: str) -> Token:
        if self.token_actual.tipo == tipo_esperado:
            return self._avanzar()
        return None

    def analizar(self) -> NodoAST:
        self.arbol_ast = self._parse_documento()
        return self.arbol_ast

    # <documento> ::= <bloque> <documento> | ε
    def _parse_documento(self) -> NodoAST:
        nodo_doc = NodoAST("<documento>", es_terminal=False)
        while self.token_actual.tipo != "EOF":
            if self.token_actual.tipo in ("SALTO_PARRAFO", "DEDENT"):
                self._avanzar()
                continue
            nodo_bloque = self._parse_bloque()
            if nodo_bloque is not None:
                nodo_doc.agregar_hijo(nodo_bloque)
        return nodo_doc

    # <bloque> ::= <encabezado> | <parrafo> | <lista> | <cita> | <bloque_codigo> | <regla_horizontal>
    def _parse_bloque(self) -> NodoAST:
        nodo_bloque = NodoAST("<bloque>", es_terminal=False)
        tipo = self.token_actual.tipo

        if tipo == "NUMERAL":
            nodo_bloque.agregar_hijo(self._parse_encabezado())
        elif tipo in ("VIÑETA", "INDENT"):
            nodo_bloque.agregar_hijo(self._parse_lista())
        elif tipo == "CITA":
            nodo_bloque.agregar_hijo(self._parse_cita())
        elif tipo == "CERCA_CODIGO":
            nodo_bloque.agregar_hijo(self._parse_bloque_codigo())
        elif tipo == "REGLA_HORIZONTAL":
            nodo_bloque.agregar_hijo(self._parse_regla_horizontal())
        elif tipo in ("TEXTO", "NEGRITA", "CURSIVA", "CODIGO_INLINE"):
            nodo_bloque.agregar_hijo(self._parse_parrafo())
        else:
            self._avanzar()
            return None

        return nodo_bloque

    # <encabezado> ::= NUMERAL <en_linea>
    def _parse_encabezado(self) -> NodoAST:
        tok_num = self._coincidir("NUMERAL")
        nodo = NodoAST("<encabezado>", es_terminal=False, nivel=tok_num.nivel)
        nodo.agregar_hijo(NodoAST("NUMERAL", es_terminal=True, token=tok_num, valor=tok_num.lexema, nivel=tok_num.nivel))
        nodo_linea = self._parse_en_linea(delimitadores_cierre=set(), parar_en_bloques=True, linea_fija=tok_num.linea)
        nodo.agregar_hijo(nodo_linea)
        return nodo

    # <parrafo> ::= <en_linea> SALTO_PARRAFO
    def _parse_parrafo(self) -> NodoAST:
        nodo = NodoAST("<parrafo>", es_terminal=False)
        nodo_linea = self._parse_en_linea(delimitadores_cierre=set(), parar_en_bloques=True, linea_fija=None)
        nodo.agregar_hijo(nodo_linea)
        if self.token_actual.tipo == "SALTO_PARRAFO":
            tok_salto = self._coincidir("SALTO_PARRAFO")
            nodo.agregar_hijo(NodoAST("SALTO_PARRAFO", es_terminal=True, token=tok_salto, valor="\\n"))
        return nodo

    # <lista> ::= <item_lista> <lista_prima>
    def _parse_lista(self) -> NodoAST:
        nodo_lista = NodoAST("<lista>", es_terminal=False)
        while self.token_actual.tipo in ("VIÑETA", "INDENT"):
            if self.token_actual.tipo == "INDENT" and self.token_actual.info_extra.startswith("INVALIDO"):
                tok_err = self._avanzar()
                msg = f"Indentación inválida en línea {tok_err.linea}, columna {tok_err.columna}"
                self.gestor_errores.agregar_error("    ", "INDENTACION_INVALIDA", "Sintáctico", msg, tok_err.linea, tok_err.columna)
                if self.token_actual.tipo == "VIÑETA":
                    tok_v = self._avanzar()
                    self._parse_en_linea(delimitadores_cierre=set(), parar_en_bloques=True, linea_fija=tok_v.linea)
                continue

            if self.token_actual.tipo == "VIÑETA":
                nodo_item = self._parse_item_lista()
                nodo_lista.agregar_hijo(nodo_item)
            else:
                break
        return nodo_lista

    # <item_lista> ::= VIÑETA <en_linea> <sublista_opc>
    def _parse_item_lista(self) -> NodoAST:
        nodo_item = NodoAST("<item_lista>", es_terminal=False)
        tok_vin = self._coincidir("VIÑETA")
        nodo_item.agregar_hijo(NodoAST("VIÑETA", es_terminal=True, token=tok_vin, valor=tok_vin.lexema))

        nodo_linea = self._parse_en_linea(delimitadores_cierre=set(), parar_en_bloques=True, linea_fija=tok_vin.linea)
        nodo_item.agregar_hijo(nodo_linea)

        while self.token_actual.tipo == "INDENT":
            if self.token_actual.info_extra.startswith("INVALIDO"):
                tok_err = self._avanzar()
                msg = f"Indentación inválida en línea {tok_err.linea}, columna {tok_err.columna}"
                self.gestor_errores.agregar_error("    ", "INDENTACION_INVALIDA", "Sintáctico", msg, tok_err.linea, tok_err.columna)
                if self.token_actual.tipo == "VIÑETA":
                    tok_v = self._avanzar()
                    self._parse_en_linea(delimitadores_cierre=set(), parar_en_bloques=True, linea_fija=tok_v.linea)
            else:
                nodo_sub = self._parse_sublista()
                nodo_item.agregar_hijo(nodo_sub)

        return nodo_item

    # <sublista> ::= INDENT <lista> DEDENT
    def _parse_sublista(self) -> NodoAST:
        nodo_sub = NodoAST("<sublista>", es_terminal=False)
        tok_ind = self._coincidir("INDENT")
        nodo_sub.agregar_hijo(NodoAST("INDENT", es_terminal=True, token=tok_ind, valor="(virtual)"))
        nodo_lista = self._parse_lista()
        nodo_sub.agregar_hijo(nodo_lista)
        if self.token_actual.tipo == "DEDENT":
            tok_ded = self._coincidir("DEDENT")
            nodo_sub.agregar_hijo(NodoAST("DEDENT", es_terminal=True, token=tok_ded, valor="(virtual)"))
        return nodo_sub

    # <cita> ::= CITA <bloque> <cita_prima>
    def _parse_cita(self) -> NodoAST:
        nodo_cita = NodoAST("<cita>", es_terminal=False)
        while self.token_actual.tipo == "CITA":
            tok_cita = self._coincidir("CITA")
            if tok_cita.info_extra == "MAL_FORMADA":
                msg = f"Cita mal formada en línea {tok_cita.linea}, columna {tok_cita.columna}"
                self.gestor_errores.agregar_error(tok_cita.lexema, "CITA_MAL_FORMADA", "Sintáctico", msg, tok_cita.linea, tok_cita.columna)
                self._parse_en_linea(delimitadores_cierre=set(), parar_en_bloques=True, linea_fija=tok_cita.linea)
                continue

            nodo_linea_cita = NodoAST("CITA", es_terminal=True, token=tok_cita, valor=tok_cita.lexema, nivel=tok_cita.nivel)
            nodo_cita.agregar_hijo(nodo_linea_cita)
            nodo_texto_cita = self._parse_en_linea(delimitadores_cierre=set(), parar_en_bloques=True, linea_fija=tok_cita.linea)
            nodo_cita.agregar_hijo(nodo_texto_cita)

        return nodo_cita

    # <bloque_codigo> ::= CERCA_CODIGO TEXTO_LITERAL CERCA_CODIGO
    def _parse_bloque_codigo(self) -> NodoAST:
        nodo_bc = NodoAST("<bloque_codigo>", es_terminal=False)
        tok_ap = self._coincidir("CERCA_CODIGO")
        nodo_bc.valor = tok_ap.info_extra
        nodo_bc.agregar_hijo(NodoAST("CERCA_CODIGO", es_terminal=True, token=tok_ap, valor=tok_ap.lexema))

        if self.token_actual.tipo == "TEXTO_LITERAL":
            tok_lit = self._coincidir("TEXTO_LITERAL")
            nodo_bc.agregar_hijo(NodoAST("TEXTO_LITERAL", es_terminal=True, token=tok_lit, valor=tok_lit.lexema))

        if self.token_actual.tipo == "CERCA_CODIGO":
            tok_ci = self._coincidir("CERCA_CODIGO")
            nodo_bc.agregar_hijo(NodoAST("CERCA_CODIGO", es_terminal=True, token=tok_ci, valor=tok_ci.lexema))

        return nodo_bc

    # <regla_horizontal> ::= REGLA_HORIZONTAL
    def _parse_regla_horizontal(self) -> NodoAST:
        nodo_rh = NodoAST("<regla_horizontal>", es_terminal=False)
        tok_rh = self._coincidir("REGLA_HORIZONTAL")
        nodo_rh.agregar_hijo(NodoAST("REGLA_HORIZONTAL", es_terminal=True, token=tok_rh, valor=tok_rh.lexema))
        return nodo_rh

    # <en_linea> ::= <elemento_linea> <en_linea> | ε
    def _parse_en_linea(self, delimitadores_cierre: set, parar_en_bloques: bool = True, linea_fija: int = None) -> NodoAST:
        nodo_en_linea = NodoAST("<en_linea>", es_terminal=False)
        tokens_fin_bloque = {"EOF", "SALTO_PARRAFO", "NUMERAL", "VIÑETA", "INDENT", "DEDENT", "CITA", "CERCA_CODIGO", "REGLA_HORIZONTAL"}

        while self.token_actual.tipo != "EOF":
            if linea_fija is not None and self.token_actual.linea != linea_fija:
                break
            if self.token_actual.tipo in delimitadores_cierre:
                break
            if parar_en_bloques and self.token_actual.tipo in tokens_fin_bloque:
                break

            tipo = self.token_actual.tipo
            if tipo == "NEGRITA":
                nodo_en_linea.agregar_hijo(self._parse_negrita(delimitadores_cierre, linea_fija))
            elif tipo == "CURSIVA":
                nodo_en_linea.agregar_hijo(self._parse_cursiva(delimitadores_cierre, linea_fija))
            elif tipo == "CODIGO_INLINE":
                nodo_en_linea.agregar_hijo(self._parse_codigo_inline())
            elif tipo == "TEXTO":
                tok_txt = self._coincidir("TEXTO")
                nodo_elem = NodoAST("<elemento_linea>", es_terminal=False)
                nodo_elem.agregar_hijo(NodoAST("TEXTO", es_terminal=True, token=tok_txt, valor=tok_txt.lexema))
                nodo_en_linea.agregar_hijo(nodo_elem)
            else:
                break

        return nodo_en_linea

    # <negrita> ::= "**" <en_linea> "**"
    def _parse_negrita(self, delimitadores_superiores: set, linea_fija: int = None) -> NodoAST:
        nodo_elem = NodoAST("<elemento_linea>", es_terminal=False)
        nodo_neg = NodoAST("<negrita>", es_terminal=False)
        tok_ap = self._coincidir("NEGRITA")
        nodo_neg.agregar_hijo(NodoAST("NEGRITA", es_terminal=True, token=tok_ap, valor=tok_ap.lexema))

        nuevos_delim = set(delimitadores_superiores)
        nuevos_delim.add("NEGRITA")
        nodo_interno = self._parse_en_linea(delimitadores_cierre=nuevos_delim, parar_en_bloques=True, linea_fija=linea_fija)
        nodo_neg.agregar_hijo(nodo_interno)

        if self.token_actual.tipo == "NEGRITA":
            tok_ci = self._coincidir("NEGRITA")
            nodo_neg.agregar_hijo(NodoAST("NEGRITA", es_terminal=True, token=tok_ci, valor=tok_ci.lexema))

        nodo_elem.agregar_hijo(nodo_neg)
        return nodo_elem

    # <cursiva> ::= "*" <en_linea> "*"
    def _parse_cursiva(self, delimitadores_superiores: set, linea_fija: int = None) -> NodoAST:
        nodo_elem = NodoAST("<elemento_linea>", es_terminal=False)
        nodo_cur = NodoAST("<cursiva>", es_terminal=False)
        tok_ap = self._coincidir("CURSIVA")
        nodo_cur.agregar_hijo(NodoAST("CURSIVA", es_terminal=True, token=tok_ap, valor=tok_ap.lexema))

        nuevos_delim = set(delimitadores_superiores)
        nuevos_delim.add("CURSIVA")
        nodo_interno = self._parse_en_linea(delimitadores_cierre=nuevos_delim, parar_en_bloques=True, linea_fija=linea_fija)
        nodo_cur.agregar_hijo(nodo_interno)

        if self.token_actual.tipo == "CURSIVA":
            tok_ci = self._coincidir("CURSIVA")
            nodo_cur.agregar_hijo(NodoAST("CURSIVA", es_terminal=True, token=tok_ci, valor=tok_ci.lexema))

        nodo_elem.agregar_hijo(nodo_cur)
        return nodo_elem

    # <codigo_inline> ::= "`" TEXTO_LITERAL "`"
    def _parse_codigo_inline(self) -> NodoAST:
        nodo_elem = NodoAST("<elemento_linea>", es_terminal=False)
        nodo_cod = NodoAST("<codigo_inline>", es_terminal=False)
        tok_ap = self._coincidir("CODIGO_INLINE")
        nodo_cod.agregar_hijo(NodoAST("CODIGO_INLINE", es_terminal=True, token=tok_ap, valor=tok_ap.lexema))

        if self.token_actual.tipo == "TEXTO_LITERAL":
            tok_lit = self._coincidir("TEXTO_LITERAL")
            nodo_cod.agregar_hijo(NodoAST("TEXTO_LITERAL", es_terminal=True, token=tok_lit, valor=tok_lit.lexema))

        if self.token_actual.tipo == "CODIGO_INLINE":
            tok_ci = self._coincidir("CODIGO_INLINE")
            nodo_cod.agregar_hijo(NodoAST("CODIGO_INLINE", es_terminal=True, token=tok_ci, valor=tok_ci.lexema))

        nodo_elem.agregar_hijo(nodo_cod)
        return nodo_elem

    def generar_dot(self, ruta_archivo: str = None) -> str:
        if self.arbol_ast is None:
            return ""

        lineas_dot = [
            "digraph ArbolDerivacion {",
            "    rankdir=TB;",
            '    node [shape=box, style=filled, fontname="Arial"];'
        ]

        contador = [0]

        def escapar_dot(texto: str) -> str:
            res = texto.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
            if len(res) > 28:
                res = res[:25] + "..."
            return res

        def recorrer(nodo: NodoAST, es_raiz: bool = False) -> str:
            id_actual = f"n{contador[0]}"
            contador[0] += 1

            if es_raiz:
                lineas_dot.append(f'    {id_actual} [label="{escapar_dot(nodo.etiqueta)}", fillcolor="#2E75B6", fontcolor=white];')
            elif nodo.es_terminal:
                etiqueta_term = nodo.etiqueta
                if nodo.valor and nodo.etiqueta not in ("INDENT", "DEDENT", "SALTO_PARRAFO"):
                    etiqueta_term = f"{nodo.etiqueta}\\n({escapar_dot(nodo.valor)})"
                lineas_dot.append(f'    {id_actual} [label="{etiqueta_term}", fillcolor="#F9E79F"];')
            else:
                lineas_dot.append(f'    {id_actual} [label="{escapar_dot(nodo.etiqueta)}", fillcolor="#D6EAF8"];')

            for hijo in nodo.hijos:
                id_hijo = recorrer(hijo, es_raiz=False)
                lineas_dot.append(f"    {id_actual} -> {id_hijo};")

            return id_actual

        recorrer(self.arbol_ast, es_raiz=True)
        lineas_dot.append("}")
        codigo_dot = "\n".join(lineas_dot)

        if ruta_archivo:
            with open(ruta_archivo, "w", encoding="utf-8") as f:
                f.write(codigo_dot)

        return codigo_dot