# Torneo de Sudoku: Validación y Análisis de Partidas
# Edgar Alfredo Donis Llamas - 202307788

import os

class Tablero:
    def __init__(self, id_sudoku, dificultad, tablero_str):
        self.id_sudoku = int(id_sudoku)
        self.dificultad = dificultad.strip()
        tablero_str = tablero_str.strip()
        # Transforma los 81 caracteres del string en una matriz 9x9
        self.matriz = [[int(tablero_str[i * 9 + j]) for j in range(9)] for i in range(9)]

class Jugador:
    def __init__(self, carnet, nombre, apellido, nivel):
        self.carnet = int(carnet)
        self.nombre = nombre.strip()
        self.apellido = apellido.strip()
        self.nivel = nivel.strip()

class Intento:
    def __init__(self, carnet, id_sudoku, solucion_str, tiempo_segundos, fecha):
        self.carnet = int(carnet)
        self.id_sudoku = int(id_sudoku)
        solucion_str = solucion_str.strip()
        # Matriz 9x9
        self.matriz = [[int(solucion_str[i * 9 + j]) for j in range(9)] for i in range(9)]
        self.tiempo_segundos = int(tiempo_segundos)
        self.fecha = fecha.strip()
        self.es_valido = False
        self.porcentaje_validez = 0.0

# "Motor" del sistema
class SistemaSudoku:
    def __init__(self):
        self.tableros = {}
        self.jugadores = {}
        self.intentos = []

    def cargar_sudokus(self, ruta):
        try:
            with open(ruta, 'r', encoding="utf-8") as file:
                lineas = file.readlines()
                for linea in lineas:
                    if linea.strip():
                        datos = linea.strip().split(',')
                        if len(datos) == 3:
                            tablero = Tablero(datos[0], datos[1], datos[2])
                            self.tableros[tablero.id_sudoku] = tablero
                        else:
                            print(f"Línea ignorada por mal formato: {linea}")
            print("Archivo de sudoku cargado correctamente")
        except Exception as e:
            print(f"Error al cargar sudoku: {e}")

    def cargar_jugadores(self, ruta):
        try:
            with open(ruta, 'r', encoding="utf-8") as file:
                lineas = file.readlines()
                for linea in lineas:
                    if linea.strip():
                        datos = linea.strip().split(',')
                        if len(datos) == 4:
                            jugador = Jugador(datos[0], datos[1], datos[2], datos[3])
                            self.jugadores[jugador.carnet] = jugador
                        else:
                            print(f"Línea ignorada por mal formato: {linea}")
            print("Archivo de jugador cargado correctamente")
        except Exception as e:
            print(f"Error al cargar jugador: {e}")

    def cargar_intentos(self, ruta):
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                lineas = f.readlines()
                for linea in lineas:
                    if linea.strip():
                        datos = linea.strip().split(',')
                        if len(datos) == 5:
                            intento = Intento(datos[0], datos[1], datos[2], datos[3], datos[4])
                            self.intentos.append(intento)
                        else:
                            print(f"Línea ignorada por mal formato: {linea}")
            print("Archivo de intentos cargado exitosamente.")
        except Exception as e:
            print(f"Error al cargar intentos: {e}")

    def validar_y_calificar(self):
        if not self.tableros or not self.intentos:
            print("Debe cargar los archivos primero.")
            return

        for intento in self.intentos:
            tablero_original = self.tableros.get(intento.id_sudoku)
            if not tablero_original:
                continue

            pistas_modificadas = False
            # Validar que no se alteraran las pistas originales
            for i in range(9):
                for j in range(9):
                    val_original = tablero_original.matriz[i][j]
                    if val_original != 0 and val_original != intento.matriz[i][j]:
                        pistas_modificadas = True
                        break
                if pistas_modificadas:
                    break

            if pistas_modificadas:
                intento.es_valido = False
                intento.porcentaje_validez = 0.0
                continue

            # Contar filas, columnas y cajas correctas
            areas_validas = 0

            # Filas
            for fila in intento.matriz:
                if len(set(fila)) == 9 and 0 not in fila:
                    areas_validas += 1

            # Columnas
            for col in range(9):
                columna = [intento.matriz[fila][col] for fila in range(9)]
                if len(set(columna)) == 9 and 0 not in columna:
                    areas_validas += 1

            # Cajas de 3x3
            for caja_fila in range(3):
                for caja_col in range(3):
                    caja = []
                    for i in range(3):
                        for j in range(3):
                            caja.append(intento.matriz[caja_fila * 3 + i][caja_col * 3 + j])
                    if len(set(caja)) == 9 and 0 not in caja:
                        areas_validas += 1

            # Calcular métricas
            intento.porcentaje_validez = (areas_validas / 27) * 100
            if intento.porcentaje_validez == 100.0:
                intento.es_valido = True
            else:
                intento.es_valido = False

        print("Intentos validados y calificados.")

    # Reportes HTML
    def generar_reporte_1(self):
        html = "<html><head><meta charset='UTF-8'><title>Resumen por Sudoku</title></head><body>"
        html += "<h1>Reporte 1: Resumen por Sudoku</h1>"
        html += "<table border='1'><tr><th>ID Tablero</th><th>Dificultad</th><th>Intentos</th><th>Tiempo Promedio (s)</th><th>Tasa de Éxito (%)</th></tr>"

        for id_sud, tablero in self.tableros.items():
            intentos_tablero = [i for i in self.intentos if i.id_sudoku == id_sud]
            total_intentos = len(intentos_tablero)

            if total_intentos > 0:
                tiempo_prom = sum(i.tiempo_segundos for i in intentos_tablero) / total_intentos
                exitos = sum(1 for i in intentos_tablero if i.es_valido)
                tasa_exito = (exitos / total_intentos) * 100
            else:
                tiempo_prom = 0
                tasa_exito = 0

            html += f"<tr><td>{id_sud}</td><td>{tablero.dificultad}</td><td>{total_intentos}</td><td>{tiempo_prom:.2f}</td><td>{tasa_exito:.2f}%</td></tr>"

        html += "</table></body></html>"
        with open("reporte1_sudokus.html", "w", encoding='utf-8') as f:
            f.write(html)
        print("Reporte 1 generado: reporte1_sudokus.html")

    def generar_reporte_2(self):
        html = "<html><head><meta charset='UTF-8'><title>Rendimiento por Jugador</title></head><body>"
        html += "<h1>Reporte 2: Rendimiento por Jugador</h1>"
        html += "<table border='1'><tr><th>Nombre Completo</th><th>Carnet</th><th>Nivel</th><th>Tableros Intentados</th><th>Validez Promedio (%)</th><th>Tiempo Promedio (s)</th><th>Resueltos Perfectamente</th></tr>"

        for carnet, jugador in self.jugadores.items():
            intentos_jugador = [i for i in self.intentos if i.carnet == carnet]
            total_intentos = len(intentos_jugador)

            if total_intentos > 0:
                validez_prom = sum(i.porcentaje_validez for i in intentos_jugador) / total_intentos
                tiempo_prom = sum(i.tiempo_segundos for i in intentos_jugador) / total_intentos
                perfectos = sum(1 for i in intentos_jugador if i.es_valido)
            else:
                validez_prom = 0
                tiempo_prom = 0
                perfectos = 0

            html += f"<tr><td>{jugador.nombre} {jugador.apellido}</td><td>{carnet}</td><td>{jugador.nivel}</td><td>{total_intentos}</td><td>{validez_prom:.2f}%</td><td>{tiempo_prom:.2f}</td><td>{perfectos}</td></tr>"

        html += "</table></body></html>"
        with open("reporte2_jugadores.html", "w", encoding='utf-8') as f:
            f.write(html)
        print("Reporte 2 generado: reporte2_jugadores.html")

    def generar_reporte_3(self):
        intentos_validos = [i for i in self.intentos if i.es_valido]
        # Ordenar por tiempo de menor a mayor
        intentos_validos.sort(key=lambda x: x.tiempo_segundos)
        top_10 = intentos_validos[:10]

        html = "<html><head><meta charset='UTF-8'><title>Top 10 Mejores Tiempos</title></head><body>"
        html += "<h1>Reporte 3: Top 10 Mejores Tiempos</h1>"
        html += "<table border='1'><tr><th>Posición</th><th>Carnet</th><th>Nombre Completo</th><th>ID Tablero</th><th>Dificultad</th><th>Tiempo (s)</th></tr>"

        for idx, intento in enumerate(top_10):
            jugador = self.jugadores.get(intento.carnet)
            tablero = self.tableros.get(intento.id_sudoku)
            if jugador and tablero:
                html += f"<tr><td>{idx + 1}</td><td>{jugador.carnet}</td><td>{jugador.nombre} {jugador.apellido}</td><td>{tablero.id_sudoku}</td><td>{tablero.dificultad}</td><td>{intento.tiempo_segundos}</td></tr>"

        html += "</table></body></html>"
        with open("reporte3_top10.html", "w", encoding='utf-8') as f:
            f.write(html)
        print("Reporte 3 generado: reporte3_top10.html")


# Menú Principal
def menu():
    sistema = SistemaSudoku()
    while True:
        print("\n***** TORNEO DE SUDOKU NUMERIX *****")
        print("1. Cargar archivo de sudokus")
        print("2. Cargar archivo de jugadores")
        print("3. Cargar archivo de intentos")
        print("4. Validar y calificar intentos")
        print("5. Generar Reporte: Resumen por Sudoku")
        print("6. Generar Reporte: Rendimiento por Jugador")
        print("7. Generar Reporte: Top 10 Mejores Tiempos")
        print("8. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            ruta = input("Ingrese ruta del archivo sudokus.lfp: ")
            sistema.cargar_sudokus(ruta)
        elif opcion == '2':
            ruta = input("Ingrese ruta del archivo jugadores.lfp: ")
            sistema.cargar_jugadores(ruta)
        elif opcion == '3':
            ruta = input("Ingrese ruta del archivo intentos.lfp: ")
            sistema.cargar_intentos(ruta)
        elif opcion == '4':
            sistema.validar_y_calificar()
        elif opcion == '5':
            sistema.generar_reporte_1()
        elif opcion == '6':
            sistema.generar_reporte_2()
        elif opcion == '7':
            sistema.generar_reporte_3()
        elif opcion == '8':
            print("Saliendo")
            break
        else:
            print("Opción inválida. Intente de nuevo.")

if __name__ == "__main__":
    menu()