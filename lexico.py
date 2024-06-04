from flask import Flask, request, render_template_string
import os

aplicacion = Flask(__name__)
DIRECTORIO_ARCHIVOS = 'archivos/'
if not os.path.exists(DIRECTORIO_ARCHIVOS):
    os.makedirs(DIRECTORIO_ARCHIVOS)
aplicacion.config['DIRECTORIO_ARCHIVOS'] = DIRECTORIO_ARCHIVOS

def analisis_lexico(codigo):
    resultado = []
    palabras_clave = {'int', 'for', 'if', 'else', 'while', 'return', 'system.out.println'}
    lineas = codigo.split('\n')
    for numero_linea, linea in enumerate(lineas, start=1):
        indice = 0
        while indice < len(linea):
            token_detectado = False
            for palabra in palabras_clave:
                if linea[indice:].startswith(palabra) and (indice + len(palabra) == len(linea) or not linea[indice + len(palabra)].isalnum()):
                    resultado.append((numero_linea, indice, 'Palabra clave', palabra))
                    indice += len(palabra)
                    token_detectado = True
                    break
            if token_detectado:
                continue

            caracter = linea[indice]
            if caracter in [';', '{', '}', '(', ')']:
                tipo_caracter = 'Punto y coma' if caracter == ';' else 'Llave' if caracter in ['{', '}'] else 'Paréntesis'
                resultado.append((numero_linea, indice, tipo_caracter, caracter))
                indice += 1
            elif caracter.isdigit():
                resultado.append((numero_linea, indice, 'Número', caracter))
                indice += 1
            else:
                indice += 1
    return resultado

def analisis_sintactico(codigo):
    resultado = []
    palabras_clave_con_punto_y_coma = {'return'}
    lineas = codigo.split('\n')
    for numero_linea, linea in enumerate(lineas, start=1):
        linea_limpiada = linea.strip()
        necesita_punto_y_coma = any(palabra in linea_limpiada for palabra in palabras_clave_con_punto_y_coma) or linea_limpiada.endswith(')')
        es_correcto = necesita_punto_y_coma and linea_limpiada.endswith(';')
        if necesita_punto_y_coma and not es_correcto:
            resultado.append((numero_linea, "Se esperaba ';'", False))
        else:
            resultado.append((numero_linea, "Correcto", True))
    return resultado

@aplicacion.route('/', methods=['GET', 'POST'])
def index():
    codigo = ""
    resultado_lexico = []
    resultado_sintactico = []
    if request.method == 'POST':
        if 'archivo' in request.files and request.files['archivo'].filename != '':
            archivo = request.files['archivo']
            ruta_archivo = os.path.join(aplicacion.config['DIRECTORIO_ARCHIVOS'], archivo.filename)
            archivo.save(ruta_archivo)
            with open(ruta_archivo, 'r') as f:
                codigo = f.read()
        elif 'codigo' in request.form and request.form['codigo'].strip() != '':
            codigo = request.form['codigo']
        else:
            return "No se seleccionó archivo ni se proporcionó código"
        
        resultado_lexico = analisis_lexico(codigo)
        resultado_sintactico = analisis_sintactico(codigo)
        
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: 'Arial', sans-serif;
                background-color: #f0f0f5;
                color: #333;
                display: flex;
                flex-direction: row;
                align-items: flex-start;
                justify-content: center;
                min-height: 100vh;
                margin: 0;
                padding: 20px;
            }
            header {
                width: 100%;
                background-color: #4CAF50;
                color: white;
                padding: 15px;
                text-align: center;
                box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
            }
            .container {
                display: flex;
                flex-direction: row;
                width: 100%;
                margin-top: 70px;
            }
            .input-area {
                flex: 1;
                padding-right: 20px;
            }
            .results {
                flex: 1;
                padding-left: 20px;
            }
            form {
                background-color: #ffffff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
            }
            .input-group {
                margin-bottom: 15px;
            }
            .input-group label {
                display: block;
                margin-bottom: 5px;
            }
            .input-group input[type="file"],
            .input-group textarea,
            .input-group input[type="submit"] {
                width: 100%;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                box-sizing: border-box;
            }
            .input-group input[type="submit"] {
                background-color: #4CAF50;
                color: white;
                cursor: pointer;
                transition: background_color 0.3s;
            }
            .input-group input[type="submit"]:hover {
                background-color: #45a049;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }
            table, th, td {
                border: 1px solid #ddd;
            }
            th, td {
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
            }
            td {
                background-color: #fff;
            }
        </style>
        <title>Análisis Léxico y Sintáctico</title>
    </head>
    <body>
        <header>
            <h1>Análisis Léxico y Sintáctico</h1>
        </header>
        <div class="container">
            <div class="input-area">
                <form method="POST" enctype="multipart/form-data">
                    <div class="input-group">
                        <label for="file">Cargar archivo:</label>
                        <input type="file" name="archivo">
                    </div>
                    <div class="input-group">
                        <label for="codigo">O ingresa el código aquí:</label>
                        <textarea name="codigo" rows="10" placeholder="Ingresa tu código aquí...">{{ codigo }}</textarea>
                    </div>
                    <div class="input-group">
                        <input type="submit" value="Analizar">
                    </div>
                </form>
            </div>
            <div class="results">
                {% if resultado_lexico %}
                <h2>Análisis Léxico</h2>
                <table>
                    <tr>
                        <th>Línea</th>
                        <th>Posición</th>
                        <th>Tipo de Token</th>
                        <th>Carácter</th>
                        <th>Palabra Clave</th>
                    </tr>
                    {% for linea in resultado_lexico %}
                    <tr>
                        <td>{{ linea[0] }}</td>
                        <td>{{ linea[1] }}</td>
                        <td>{{ linea[2] }}</td>
                        <td>{% if linea[2] != 'Palabra clave' %}{{ linea[3] }}{% endif %}</td>
                        <td>{% if linea[2] == 'Palabra clave' %}{{ linea[3] }}{% endif %}</td>
                    </tr>
                    {% endfor %}
                </table>
                {% endif %}
                {% if resultado_sintactico %}
                <h2>Análisis Sintáctico</h2>
                <table>
                    <tr>
                        <th>Línea</th>
                        <th>Resultado</th>
                        <th>Correcto/Incorrecto</th>
                    </tr>
                    {% for linea in resultado_sintactico %}
                    <tr>
                        <td>{{ linea[0] }}</td>
                        <td>{{ linea[1] }}</td>
                        <td>{{ '✔' if linea[2] else '✘' }}</td>
                    </tr>
                    {% endfor %}
                </table>
                {% endif %}
            </div>
        </div>
    </body>
    </html>
    """, codigo=codigo, resultado_lexico=resultado_lexico, resultado_sintactico=resultado_sintactico)

if __name__ == '__main__':
    aplicacion.run(debug=True)
