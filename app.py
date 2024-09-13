from flask import Flask, render_template, request, jsonify
from aforo import CalculadoraTanque
from api import ApiCorreccion
from datos import DataLoader
import os

app = Flask(__name__)

# Ruta principal del proyecto
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.json
        numerotk = int(data['numero'])
        altura_inicial = float(data['altura_inicial'])
        volumen_recibido = float(data['volumen_recibido'])
        api_observado = float(data['api_observado'])
        temperatura = float(data.get('temperatura', 0))  # Usa .get() para manejar posibles valores ausentes
        
        tks = DataLoader(".")
        if numerotk==8:
           datos_path = "aforo_tk_08.json"
        if numerotk==9:
           datos_path="aforo_tk_09.json"
        aforo_tks = tks.load_file(datos_path)   
        
        obAforo = CalculadoraTanque(altura_inicial, volumen_recibido,aforo_tks)

        vol_1 = obAforo.mostrar_volumen(aforo_tks,altura_inicial)
        if vol_1 is None:
            return jsonify({'error': 'La altura inicial está fuera de rango.'})

        vol = vol_1 + volumen_recibido
        altura_final = obAforo.mostrar_altura(vol,aforo_tks)
        if altura_final is None:
            return jsonify({'error': 'No se pudo calcular la altura final.'})

        vol_final = obAforo.mostrar_volumen(aforo_tks, altura_final)
        if vol_final is None:
            return jsonify({'error': 'No se pudo calcular el volumen final.'})

        vol_br_rec = vol_final - vol_1
        api = ApiCorreccion(api_observado, temperatura)
        api_corregido, fac_cor = api.corregir_correccion()
        vol_neto_rec = vol_br_rec * fac_cor

        return jsonify({
            'altura_inicial': altura_inicial,
            'volumen_inicial': vol_1,
            'altura_final': altura_final,
            'volumen_final': vol_final,
            'volumen_br_rec': vol_br_rec,
            'temperatura': temperatura,
            'api_observado': api_observado,
            'api_corregido': api_corregido,
            'fac_cor': fac_cor,
            'vol_neto_rec': vol_neto_rec
        })
    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

