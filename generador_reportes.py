import os

class GeneradorReportes:
    def __init__(self, tokens, errores):
        self.tokens = tokens
        self.errores = errores

    def extraer_clases_simuladas(self):
        # Lógica simplificada para extraer datos secuenciales basándose en los tokens
        # En un compilador real esto lo hace el Análisis Sintáctico (Proyecto 2),
        # pero aquí improvisamos una extracción heurística requerida para el Proyecto 1.
        clases = []
        clase_actual = {}

        for i, token in enumerate(self.tokens):
            if token.tipo == 'PR_CLASE':
                if clase_actual:
                    clases.append(clase_actual)
                clase_actual = {}
            elif token.tipo == 'CODIGO':
                # El primer código después de 'clase' suele ser el curso
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
        # Detecta si el mismo catedrático o aula están en el mismo día y hora inicial
        choques = []
        for i, c1 in enumerate(clases):
            for c2 in clases[i + 1:]:
                # Verifica que ambas clases tengan las llaves necesarias para evitar KeyError
                if all(k in c1 and k in c2 for k in ('aula', 'catedratico', 'dia', 'inicio')):
                    conflicto_lugar = c1['aula'] == c2['aula']
                    conflicto_docente = c1['catedratico'] == c2['catedratico']
                    conflicto_tiempo = (c1['dia'] == c2['dia']) and (c1['inicio'] == c2['inicio'])

                    if conflicto_tiempo and (conflicto_lugar or conflicto_docente):
                        choques.append((c1, c2))
        return choques

    def generar_reporte_1_horario(self, clases, choques):
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

        # Aplanar la lista de choques para búsqueda rápida
        clases_en_choque = []
        for c1, c2 in choques:
            clases_en_choque.extend([c1, c2])

        for c in clases:
            # Validar si esta clase específica está en la lista de choques
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

        with open("Reporte_1_Horario.html", "w", encoding="utf-8") as f:
            f.write(html)

    def generar_todos(self):
        clases = self.extraer_clases_simuladas()
        choques = self.detectar_choques(clases)
        self.generar_reporte_1_horario(clases, choques)

        # Aquí puedes replicar la misma lógica simple de HTML para crear:
        # Reporte_2_Catedraticos.html
        # Reporte_3_Estadistico.html
        # Reporte_Errores.html (Iterando sobre self.errores)