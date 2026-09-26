import os
from datetime import datetime


class GeneradorReportes:
    def __init__(self, tokens, errores):
        self.tokens = tokens
        self.errores = errores

    def extraer_clases_simuladas(self):
        clases = []
        clase_actual = {}

        for i, token in enumerate(self.tokens):
            if token.tipo == 'PR_CLASE':
                if clase_actual:
                    clases.append(clase_actual)
                clase_actual = {}
            elif token.tipo == 'CODIGO':
                if 'curso' not in clase_actual:
                    clase_actual['curso'] = token.lexema
                elif 'catedratico' not in clase_actual:
                    clase_actual['catedratico'] = token.lexema
                elif 'aula' not in clase_actual:
                    clase_actual['aula'] = token.lexema
            elif token.tipo == 'DIA':
                clase_actual['dia'] = token.lexema
            elif token.tipo == 'HORA':
                if 'inicio' not in clase_actual:
                    clase_actual['inicio'] = token.lexema
                else:
                    clase_actual['fin'] = token.lexema

        if clase_actual:
            clases.append(clase_actual)

        return clases

    def detectar_choques(self, clases):
        choques = []
        for i, c1 in enumerate(clases):
            for c2 in clases[i + 1:]:
                if all(k in c1 and k in c2 for k in ('aula', 'catedratico', 'dia', 'inicio')):
                    conflicto_lugar = c1['aula'] == c2['aula']
                    conflicto_docente = c1['catedratico'] == c2['catedratico']
                    conflicto_tiempo = (c1['dia'] == c2['dia']) and (c1['inicio'] == c2['inicio'])

                    if conflicto_tiempo and (conflicto_lugar or conflicto_docente):
                        choques.append((c1, c2))
        return choques

    def generar_reporte_1_horario(self, clases, choques, timestamp):
        html = """
        <html>
        <head>
            <meta charset="utf-8">
            <title>Reporte 1 - Horario</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                table { border-collapse: collapse; width: 100%; margin-top: 20px; }
                th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
                th { background-color: #f2f2f2; }
                .choque { background-color: #ffcccc; color: #cc0000; font-weight: bold; }
                .ok { background-color: #e6ffe6; }
            </style>
        </head>
        <body>
            <h2>Reporte 1: Horario Semanal y Detección de Choques</h2>
            <table>
                <tr><th>Día</th><th>Inicio - Fin</th><th>Curso</th><th>Catedrático</th><th>Aula</th><th>Estado</th></tr>
        """

        clases_en_choque = []
        for c1, c2 in choques:
            clases_en_choque.extend([c1, c2])

        for c in clases:
            es_choque = c in clases_en_choque
            clase_css = "choque" if es_choque else "ok"
            estado_txt = "CHOQUE DETECTADO" if es_choque else "Confirmado"

            dia = c.get('dia', 'N/A')
            horario = f"{c.get('inicio', 'N/A')} - {c.get('fin', 'N/A')}"
            curso = c.get('curso', 'N/A')
            cat = c.get('catedratico', 'N/A')
            aula = c.get('aula', 'N/A')

            html += f"""
                <tr class="{clase_css}">
                    <td>{dia}</td><td>{horario}</td><td>{curso}</td>
                    <td>{cat}</td><td>{aula}</td><td>{estado_txt}</td>
                </tr>
            """

        html += "</table></body></html>"

        nombre_archivo = f"Reporte_1_Horario_{timestamp}.html"
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write(html)

    def generar_reporte_2_catedraticos(self, clases, timestamp):
        carga_docente = {}
        for c in clases:
            cat = c.get('catedratico', 'Desconocido')
            if cat not in carga_docente:
                carga_docente[cat] = {'cursos': set(), 'bloques': 0}
            carga_docente[cat]['cursos'].add(c.get('curso', ''))
            carga_docente[cat]['bloques'] += 1

        html = """
        <html>
        <head>
            <meta charset="utf-8">
            <title>Reporte 2 - Catedráticos</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                table { border-collapse: collapse; width: 100%; margin-top: 20px; }
                th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
                th { background-color: #f2f2f2; }
                .baja { color: white; background-color: #2196F3; }
                .normal { color: white; background-color: #4CAF50; }
                .alta { color: white; background-color: #FF9800; }
                .saturada { color: white; background-color: #f44336; }
            </style>
        </head>
        <body>
            <h2>Reporte 2: Carga de Catedráticos</h2>
            <table>
                <tr><th>Catedrático</th><th>Cursos Distintos</th><th>Bloques Asignados</th><th>Nivel de Carga</th></tr>
        """

        for cat, datos in carga_docente.items():
            bloques = datos['bloques']
            cursos_distintos = len(datos['cursos'])

            if bloques <= 4:
                nivel, clase_css = "BAJA", "baja"
            elif bloques <= 10:
                nivel, clase_css = "NORMAL", "normal"
            elif bloques <= 15:
                nivel, clase_css = "ALTA", "alta"
            else:
                nivel, clase_css = "SATURADA", "saturada"

            html += f"""
                <tr>
                    <td>{cat}</td><td>{cursos_distintos}</td><td>{bloques}</td>
                    <td class="{clase_css}"><b>{nivel}</b></td>
                </tr>
            """

        html += "</table></body></html>"

        nombre_archivo = f"Reporte_2_Catedraticos_{timestamp}.html"
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write(html)

    def generar_reporte_3_estadistico(self, clases, choques, timestamp):
        total_clases = len(clases)
        total_choques = len(choques)

        aulas_ocupacion = {}
        for c in clases:
            aula = c.get('aula', 'Desconocida')
            aulas_ocupacion[aula] = aulas_ocupacion.get(aula, 0) + 1

        html = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <title>Reporte 3 - Estadístico</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .kpi-container {{ display: flex; gap: 20px; margin-bottom: 30px; }}
                .kpi-card {{ border: 1px solid #ddd; padding: 20px; border-radius: 8px; background-color: #f9f9f9; text-align: center; flex: 1; }}
                .kpi-card h3 {{ margin: 0 0 10px 0; color: #555; }}
                .kpi-card p {{ margin: 0; font-size: 24px; font-weight: bold; color: #333; }}
                .alerta {{ color: #cc0000; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h2>Reporte 3: Estadístico General del Ciclo</h2>

            <div class="kpi-container">
                <div class="kpi-card">
                    <h3>Total Clases</h3>
                    <p>{total_clases}</p>
                </div>
                <div class="kpi-card">
                    <h3>Choques de Horario</h3>
                    <p class="{'alerta' if total_choques > 0 else ''}">{total_choques}</p>
                </div>
                <div class="kpi-card">
                    <h3>Aulas en Uso</h3>
                    <p>{len(aulas_ocupacion)}</p>
                </div>
            </div>

            <h3>Ocupación por Aula</h3>
            <table>
                <tr><th>Aula</th><th>Clases Asignadas</th></tr>
        """

        aulas_ordenadas = sorted(aulas_ocupacion.items(), key=lambda x: x[1], reverse=True)
        for aula, uso in aulas_ordenadas:
            html += f"<tr><td>{aula}</td><td>{uso}</td></tr>"

        html += "</table></body></html>"

        nombre_archivo = f"Reporte_3_Estadistico_{timestamp}.html"
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write(html)

    def generar_todos(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        clases = self.extraer_clases_simuladas()
        choques = self.detectar_choques(clases)

        self.generar_reporte_1_horario(clases, choques, timestamp)
        self.generar_reporte_2_catedraticos(clases, timestamp)
        self.generar_reporte_3_estadistico(clases, choques, timestamp)