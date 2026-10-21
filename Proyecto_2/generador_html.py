"""
Módulo Generador de Reportes HTML (Reporte 1: Documento HTML Renderizado,
Reporte 2: Estadísticas del Documento, Reporte 3: Tabla de Contenido / Mapa de Navegación).
Recorre exclusivamente el Árbol de Derivación (AST) sin usar sustitución de texto ni 're'.
Estudiante: Edgar Alfredo Donis Llamas - Carnet: 202307788
"""

import os
from modelos import NodoAST


class GeneradorHTML:
    def __init__(self, ast_raiz: NodoAST, nombre_archivo_md: str = "documento.md"):
        self.ast = ast_raiz
        self.nombre_archivo_md = nombre_archivo_md
        self.encabezados_toc = []
        self.estadisticas = {
            "palabras_totales": 0,
            "parrafos": 0,
            "encabezados_total": 0,
            "encabezados_nivel": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0},
            "listas_bloques": 0,
            "items_lista": 0,
            "max_profundidad_lista": 0,
            "citas_bloques": 0,
            "lineas_cita": 0,
            "max_profundidad_cita": 0,
            "bloques_codigo": 0,
            "negrita": 0,
            "cursiva": 0,
            "codigo_inline": 0,
            "regla_horizontal": 0
        }
        self._contador_anclas = 0

    def _escapar_html(self, texto: str) -> str:
        return (texto.replace("&", "&amp;")
                     .replace("<", "&lt;")
                     .replace(">", "&gt;")
                     .replace('"', "&quot;"))

    def _contar_palabras(self, texto: str) -> int:
        cont = 0
        for p in texto.split():
            if any(c.isalnum() for c in p):
                cont += 1
        return cont

    def _generar_id_ancla(self, texto_plano: str) -> str:
        self._contador_anclas += 1
        limpio = []
        for ch in texto_plano.lower():
            if ch.isalnum():
                limpio.append(ch)
            elif ch == " ":
                limpio.append("-")
        slug = "".join(limpio).strip("-")
        if not slug:
            slug = f"seccion-{self._contador_anclas}"
        return f"{slug}-{self._contador_anclas}"

    def _extraer_texto_plano(self, nodo: NodoAST) -> str:
        if nodo is None:
            return ""
        if nodo.es_terminal:
            if nodo.etiqueta in ("TEXTO", "TEXTO_LITERAL"):
                return nodo.valor
            return ""
        return "".join(self._extraer_texto_plano(h) for h in nodo.hijos)

    def _traducir_en_linea(self, nodo_en_linea: NodoAST) -> str:
        if nodo_en_linea is None:
            return ""
        fragmentos = []
        for hijo in nodo_en_linea.hijos:
            if hijo.etiqueta == "<elemento_linea>" and hijo.hijos:
                sub = hijo.hijos[0]
                if sub.es_terminal and sub.etiqueta == "TEXTO":
                    self.estadisticas["palabras_totales"] += self._contar_palabras(sub.valor)
                    fragmentos.append(self._escapar_html(sub.valor))
                elif sub.etiqueta == "<negrita>":
                    self.estadisticas["negrita"] += 1
                    interno = self._traducir_en_linea(sub.hijos[1]) if len(sub.hijos) > 1 else ""
                    fragmentos.append(f"<strong>{interno}</strong>")
                elif sub.etiqueta == "<cursiva>":
                    self.estadisticas["cursiva"] += 1
                    interno = self._traducir_en_linea(sub.hijos[1]) if len(sub.hijos) > 1 else ""
                    fragmentos.append(f"<em>{interno}</em>")
                elif sub.etiqueta == "<codigo_inline>":
                    self.estadisticas["codigo_inline"] += 1
                    txt_cod = ""
                    for hc in sub.hijos:
                        if hc.es_terminal and hc.etiqueta == "TEXTO_LITERAL":
                            txt_cod = hc.valor
                            self.estadisticas["palabras_totales"] += self._contar_palabras(txt_cod)
                    fragmentos.append(f"<code>{self._escapar_html(txt_cod)}</code>")
        return "".join(fragmentos)

    def _traducir_lista(self, nodo_lista: NodoAST, profundidad_actual: int) -> str:
        if profundidad_actual > self.estadisticas["max_profundidad_lista"]:
            self.estadisticas["max_profundidad_lista"] = profundidad_actual

        items_html = []
        for hijo in nodo_lista.hijos:
            if hijo.etiqueta == "<item_lista>":
                self.estadisticas["items_lista"] += 1
                html_linea = ""
                html_sublistas = []
                for sub in hijo.hijos:
                    if sub.etiqueta == "<en_linea>":
                        html_linea = self._traducir_en_linea(sub)
                    elif sub.etiqueta == "<sublista>":
                        for s_hijo in sub.hijos:
                            if s_hijo.etiqueta == "<lista>":
                                html_sublistas.append(self._traducir_lista(s_hijo, profundidad_actual + 1))
                sub_str = "".join(html_sublistas)
                items_html.append(f"<li>{html_linea}{sub_str}</li>")
        return "<ul>\n" + "\n".join(items_html) + "\n</ul>"

    def _traducir_cita(self, nodo_cita: NodoAST) -> str:
        self.estadisticas["citas_bloques"] += 1
        pares = []
        i = 0
        hijos = nodo_cita.hijos
        while i < len(hijos):
            if hijos[i].es_terminal and hijos[i].etiqueta == "CITA":
                nivel = hijos[i].nivel if hijos[i].nivel > 0 else 1
                nodo_lin = hijos[i + 1] if (i + 1 < len(hijos) and hijos[i + 1].etiqueta == "<en_linea>") else None
                pares.append((nivel, nodo_lin))
                i += 2
            else:
                i += 1

        html_partes = []
        nivel_abierto = 0
        for nivel, nodo_lin in pares:
            self.estadisticas["lineas_cita"] += 1
            if nivel > self.estadisticas["max_profundidad_cita"]:
                self.estadisticas["max_profundidad_cita"] = nivel

            while nivel_abierto < nivel:
                html_partes.append("<blockquote>")
                nivel_abierto += 1
            while nivel_abierto > nivel:
                html_partes.append("</blockquote>")
                nivel_abierto -= 1

            contenido_html = self._traducir_en_linea(nodo_lin) if nodo_lin else ""
            html_partes.append(f"<p>{contenido_html}</p>")

        while nivel_abierto > 0:
            html_partes.append("</blockquote>")
            nivel_abierto -= 1

        return "\n".join(html_partes)

    def construir_cuerpo_html(self) -> str:
        self.encabezados_toc.clear()
        self._contador_anclas = 0
        for k in self.estadisticas:
            if isinstance(self.estadisticas[k], dict):
                for nk in self.estadisticas[k]:
                    self.estadisticas[k][nk] = 0
            else:
                self.estadisticas[k] = 0

        if self.ast is None:
            return ""

        bloques_html = []
        for nodo_bloque in self.ast.hijos:
            if nodo_bloque.etiqueta != "<bloque>" or not nodo_bloque.hijos:
                continue
            especifico = nodo_bloque.hijos[0]
            etq = especifico.etiqueta

            if etq == "<encabezado>":
                nivel = especifico.nivel if 1 <= especifico.nivel <= 6 else 1
                self.estadisticas["encabezados_total"] += 1
                self.estadisticas["encabezados_nivel"][nivel] += 1
                nodo_lin = next((h for h in especifico.hijos if h.etiqueta == "<en_linea>"), None)
                texto_plano = self._extraer_texto_plano(nodo_lin).strip()
                ancla_id = self._generar_id_ancla(texto_plano)
                html_interno = self._traducir_en_linea(nodo_lin)
                self.encabezados_toc.append({
                    "nivel": nivel,
                    "texto": texto_plano,
                    "html": html_interno,
                    "id": ancla_id
                })
                bloques_html.append(f'<h{nivel} id="{ancla_id}">{html_interno}</h{nivel}>')

            elif etq == "<parrafo>":
                self.estadisticas["parrafos"] += 1
                nodo_lin = especifico.hijos[0] if especifico.hijos else None
                html_interno = self._traducir_en_linea(nodo_lin)
                bloques_html.append(f"<p>{html_interno}</p>")

            elif etq == "<lista>":
                self.estadisticas["listas_bloques"] += 1
                bloques_html.append(self._traducir_lista(especifico, profundidad_actual=1))

            elif etq == "<cita>":
                bloques_html.append(self._traducir_cita(especifico))

            elif etq == "<bloque_codigo>":
                self.estadisticas["bloques_codigo"] += 1
                lenguaje = especifico.valor.strip() if especifico.valor else ""
                contenido_lit = ""
                for h in especifico.hijos:
                    if h.es_terminal and h.etiqueta == "TEXTO_LITERAL":
                        contenido_lit = h.valor
                attr_class = f' class="language-{self._escapar_html(lenguaje)}"' if lenguaje else ""
                bloques_html.append(f"<pre><code{attr_class}>{self._escapar_html(contenido_lit)}</code></pre>")

            elif etq == "<regla_horizontal>":
                self.estadisticas["regla_horizontal"] += 1
                bloques_html.append("<hr>")

        return "\n\n".join(bloques_html)

    def generar_tres_reportes(self, directorio_salida: str) -> dict:
        os.makedirs(directorio_salida, exist_ok=True)
        cuerpo_rep1 = self.construir_cuerpo_html()

        ruta_rep1 = os.path.join(directorio_salida, "reporte1_documento.html")
        ruta_rep2 = os.path.join(directorio_salida, "reporte2_estadisticas.html")
        ruta_rep3 = os.path.join(directorio_salida, "reporte3_indice.html")

        # Reporte 1: Documento HTML Renderizado
        html_rep1 = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Reporte 1 - {self._escapar_html(self.nombre_archivo_md)}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; color: #1f2937; background: #f9fafb; margin: 0; padding: 40px 20px; line-height: 1.65; }}
        .container {{ max-width: 820px; margin: 0 auto; background: #fff; padding: 40px 50px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); border: 1px solid #e5e7eb; }}
        .badge-ok {{ display: inline-block; background: #dcfce7; color: #15803d; font-size: 0.85rem; font-weight: 600; padding: 5px 14px; border-radius: 9999px; margin-bottom: 18px; }}
        h1, h2, h3, h4, h5, h6 {{ color: #111827; margin-top: 1.4em; margin-bottom: 0.5em; font-weight: 700; }}
        h1 {{ font-size: 2rem; border-bottom: 1px solid #e5e7eb; padding-bottom: 0.35em; margin-top: 0.4em; }}
        h2 {{ font-size: 1.5rem; border-bottom: 1px solid #f3f4f6; padding-bottom: 0.25em; }}
        code {{ font-family: Consolas, Monaco, monospace; background: #f3f4f6; color: #1f2937; padding: 2px 6px; border-radius: 5px; font-size: 0.9em; }}
        pre {{ background: #18181b; color: #f4f4f5; padding: 18px 22px; border-radius: 10px; overflow-x: auto; margin: 1.2em 0; }}
        pre code {{ background: none; color: inherit; padding: 0; }}
        blockquote {{ margin: 0.8em 0; padding: 4px 0 4px 16px; border-left: 4px solid #cbd5e1; color: #4b5563; background: #f8fafc; border-radius: 0 6px 6px 0; }}
        blockquote blockquote {{ margin: 6px 0; border-left-color: #94a3b8; }}
        ul {{ padding-left: 24px; margin: 0.6em 0; }}
        li {{ margin: 0.3em 0; }}
        hr {{ border: 0; border-top: 2px solid #e5e7eb; margin: 2em 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="badge-ok">&#10003; Análisis completado sin errores</div>
        {cuerpo_rep1}
    </div>
</body>
</html>"""
        with open(ruta_rep1, "w", encoding="utf-8") as f:
            f.write(html_rep1)

        # Reporte 2: Estadísticas del Documento
        st = self.estadisticas
        max_h = max(st["encabezados_nivel"].values()) if st["encabezados_nivel"] else 1
        if max_h == 0:
            max_h = 1

        barras_html = []
        for niv in range(1, 7):
            cant = st["encabezados_nivel"][niv]
            porcentaje = int((cant / max_h) * 100) if cant > 0 else 0
            barras_html.append(f"""
            <div class="bar-row">
                <div class="bar-label">H{niv}</div>
                <div class="bar-track"><div class="bar-fill" style="width: {porcentaje}%;"></div></div>
                <div class="bar-val">{cant}</div>
            </div>""")

        html_rep2 = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Reporte 2 - Estadísticas ({self._escapar_html(self.nombre_archivo_md)})</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; background: #f9fafb; color: #1f2937; margin: 0; padding: 40px 20px; }}
        .container {{ max-width: 820px; margin: 0 auto; background: #fff; padding: 40px 48px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); border: 1px solid #e5e7eb; }}
        h1 {{ margin: 0 0 4px 0; font-size: 1.8rem; color: #111827; }}
        .subtitle {{ color: #6b7280; font-size: 0.95rem; margin-bottom: 28px; }}
        .grid-3 {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 28px; }}
        .card {{ border: 1px solid #e5e7eb; background: #fafafa; border-radius: 10px; padding: 18px 22px; }}
        .card-num {{ font-size: 2rem; font-weight: 700; color: #1d63b8; margin-bottom: 6px; }}
        .card-label {{ color: #6b7280; font-size: 0.9rem; }}
        h2 {{ font-size: 1.15rem; color: #111827; border-bottom: 1px solid #e5e7eb; padding-bottom: 8px; margin-top: 30px; margin-bottom: 16px; }}
        .bar-row {{ display: flex; align-items: center; margin-bottom: 10px; font-size: 0.9rem; }}
        .bar-label {{ width: 36px; font-weight: 600; color: #4b5563; }}
        .bar-track {{ flex: 1; height: 16px; background: #f3f4f6; border-radius: 4px; overflow: hidden; margin: 0 14px; }}
        .bar-fill {{ height: 100%; background: #2563eb; border-radius: 4px; }}
        .bar-val {{ width: 28px; text-align: right; color: #4b5563; font-weight: 600; }}
        .grid-2 {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }}
        .stat-row-box {{ display: flex; justify-content: space-between; align-items: center; border: 1px solid #e5e7eb; background: #fafafa; border-radius: 10px; padding: 14px 20px; }}
        .stat-title {{ color: #4b5563; font-size: 0.95rem; }}
        .stat-badge-purple {{ font-size: 1.25rem; font-weight: 700; color: #5b21b6; }}
        .stat-badge-amber {{ font-size: 1.25rem; font-weight: 700; color: #b45309; }}
        .stat-badge-dark {{ font-size: 1.25rem; font-weight: 700; color: #111827; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Estadísticas del Documento</h1>
        <div class="subtitle">{self._escapar_html(self.nombre_archivo_md)}</div>
        <div class="grid-3">
            <div class="card"><div class="card-num">{st["palabras_totales"]}</div><div class="card-label">Palabras totales</div></div>
            <div class="card"><div class="card-num">{st["parrafos"]}</div><div class="card-label">Párrafos</div></div>
            <div class="card"><div class="card-num">{st["encabezados_total"]}</div><div class="card-label">Encabezados</div></div>
            <div class="card"><div class="card-num">{st["items_lista"]}</div><div class="card-label">Ítems de lista</div></div>
            <div class="card"><div class="card-num">{st["lineas_cita"]}</div><div class="card-label">Líneas de cita</div></div>
            <div class="card"><div class="card-num">{st["bloques_codigo"]}</div><div class="card-label">Bloques de código</div></div>
        </div>
        <h2>Encabezados por nivel</h2>
        {"".join(barras_html)}
        <h2>Profundidad máxima de anidamiento</h2>
        <div class="grid-2">
            <div class="stat-row-box"><span class="stat-title">Listas</span><span class="stat-badge-purple">{st["max_profundidad_lista"]} niveles</span></div>
            <div class="stat-row-box"><span class="stat-title">Citas</span><span class="stat-badge-amber">{st["max_profundidad_cita"]} niveles</span></div>
        </div>
        <h2>Elementos en línea</h2>
        <div class="grid-2">
            <div class="stat-row-box"><span class="stat-title">Negrita (**texto**)</span><span class="stat-badge-dark">{st["negrita"]}</span></div>
            <div class="stat-row-box"><span class="stat-title">Cursiva (*texto*)</span><span class="stat-badge-dark">{st["cursiva"]}</span></div>
            <div class="stat-row-box"><span class="stat-title">Código en línea (`texto`)</span><span class="stat-badge-dark">{st["codigo_inline"]}</span></div>
            <div class="stat-row-box"><span class="stat-title">Regla horizontal (---)</span><span class="stat-badge-dark">{st["regla_horizontal"]}</span></div>
        </div>
    </div>
</body>
</html>"""
        with open(ruta_rep2, "w", encoding="utf-8") as f:
            f.write(html_rep2)

        # Reporte 3: Tabla de Contenido / Mapa de Navegación
        if not self.encabezados_toc:
            contenido_toc = '<div class="empty-msg">El documento analizado no contiene encabezados (# a ######) para generar la tabla de contenido.</div>'
        else:
            filas_toc = []
            for item in self.encabezados_toc:
                niv = item["nivel"]
                indent_px = (niv - 1) * 28
                enlace = f'reporte1_documento.html#{item["id"]}'
                filas_toc.append(f"""
                <div class="toc-item" style="padding-left: {indent_px}px;">
                    <span class="badge-h badge-h{niv}">H{niv}</span>
                    <a href="{enlace}" class="toc-link">{self._escapar_html(item["texto"])}</a>
                </div>""")
            contenido_toc = "\n".join(filas_toc)

        html_rep3 = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Reporte 3 - Tabla de Contenido ({self._escapar_html(self.nombre_archivo_md)})</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; background: #f9fafb; color: #1f2937; margin: 0; padding: 40px 20px; }}
        .container {{ max-width: 820px; margin: 0 auto; background: #fff; padding: 40px 48px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); border: 1px solid #e5e7eb; }}
        h1 {{ margin: 0 0 4px 0; font-size: 1.8rem; color: #111827; }}
        .subtitle {{ color: #6b7280; font-size: 0.95rem; margin-bottom: 24px; }}
        .toc-box {{ border: 1px solid #e5e7eb; background: #fafafa; border-radius: 10px; padding: 20px 26px; }}
        .toc-item {{ display: flex; align-items: center; padding: 10px 0; border-bottom: 1px dashed #e5e7eb; }}
        .toc-item:last-child {{ border-bottom: none; }}
        .badge-h {{ display: inline-block; font-size: 0.75rem; font-weight: 700; padding: 3px 8px; border-radius: 5px; margin-right: 12px; color: #fff; background: #2563eb; }}
        .badge-h2 {{ background: #3b82f6; }}
        .badge-h3 {{ background: #60a5fa; }}
        .badge-h4, .badge-h5, .badge-h6 {{ background: #93c5fd; color: #1e3a8a; }}
        .toc-link {{ color: #1e40af; text-decoration: none; font-weight: 600; font-size: 1.02rem; }}
        .toc-link:hover {{ text-decoration: underline; }}
        .empty-msg {{ color: #6b7280; font-style: italic; padding: 12px 0; }}
        .footer-note {{ margin-top: 18px; color: #6b7280; font-size: 0.88rem; font-style: italic; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Tabla de Contenido</h1>
        <div class="subtitle">{self._escapar_html(self.nombre_archivo_md)} — generado a partir de los encabezados reconocidos</div>
        <div class="toc-box">{contenido_toc}</div>
        <div class="footer-note">Cada entrada enlaza a su sección correspondiente dentro del Reporte 1.</div>
    </div>
</body>
</html>"""
        with open(ruta_rep3, "w", encoding="utf-8") as f:
            f.write(html_rep3)

        return {"reporte1": ruta_rep1, "reporte2": ruta_rep2, "reporte3": ruta_rep3}