from flask import Flask, render_template, request, jsonify
from aforo import CalculadoraTanque
from api import ApiCorreccion
from datos import DataLoader
from datetime import datetime, timedelta
import os
import pytz

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('easy.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.json
        numerotk = int(data['numero'])
        altura_inicial = int(data['altura_inicial'])
        volumen_recibido = float(data['volumen_recibido'])

        def redondear_al_mas_cercano_05(valor):
            return round(valor * 2) / 2

        api_observado = redondear_al_mas_cercano_05(float(data['api_observado']))
        temperatura = float(data.get('temperatura', 0))

        # Manejar hora de finalización, si se proporciona
        hora_finalizacion = data.get('hora_finalizacion')
        zona_horaria = pytz.timezone('America/Bogota')  # Zona horaria de Colombia
        
        if hora_finalizacion:
            # Convertir la hora de finalización ingresada a un objeto time
            hora_finalizacion = datetime.strptime(hora_finalizacion, '%H:%M').time()
            fecha_actual = datetime.now(zona_horaria).date()
            tiempo_actual = datetime.combine(fecha_actual, hora_finalizacion)
            tiempo_actual = zona_horaria.localize(tiempo_actual)  # Localizar en la zona horaria
        else:
            tiempo_actual = datetime.now(zona_horaria)

        tks = DataLoader(".")
        if numerotk == 8:
            datos_path = "aforo_tk_08.json"
        elif numerotk == 9:
            datos_path = "aforo_tk_09.json"
        elif numerotk == 10:
            datos_path = "aforo_tk_10.json"
        aforo_tks = tks.load_file(datos_path)

        obAforo = CalculadoraTanque(altura_inicial, volumen_recibido, aforo_tks)

        vol_1 = obAforo.mostrar_volumen_prueba(aforo_tks, altura_inicial)
        if vol_1 is None:
            return jsonify({'error': 'La altura inicial está fuera de rango ombe.'})

        vol = vol_1 + volumen_recibido
        if vol > list(aforo_tks.values())[-1]:
            return jsonify({'error': 'Volumen final Fuera de rango.'})

        altura_final = obAforo.mostrar_altura_1(vol, aforo_tks)
        if altura_final is None:
            return jsonify({'error': 'No se pudo calcular la altura final.'})

        vol_final = obAforo.mostrar_volumen_prueba(aforo_tks, altura_final)
        if vol_final is None:
            return jsonify({'error': 'No se pudo calcular el volumen final.'})

        vol_br_rec = vol_final - vol_1
        api = ApiCorreccion(api_observado, temperatura)
        api_corregido, fac_cor = api.corregir_correccion()
        vol_neto_rec = vol_br_rec * fac_cor

        horas_para_liberar = (int(altura_final) / 1000) * 3
        if horas_para_liberar >= 24:
            horas_para_liberar = 24

        hora_liberacion = tiempo_actual + timedelta(hours=horas_para_liberar)
        hora_liberacion = zona_horaria.normalize(hora_liberacion)

        fecha_liberacion = hora_liberacion.date()
        hora_liberacion_formateada = hora_liberacion.strftime('%H:%M')

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
            'vol_neto_rec': vol_neto_rec,
            'fecha_finalizacion_recibo': tiempo_actual.date().strftime('%d-%m-%Y'),
            'hora_finalizacion_recibo': tiempo_actual.strftime('%H:%M'),
            'fecha_liberacion': fecha_liberacion.strftime('%d-%m-%Y'),
            'hora_liberacion': hora_liberacion_formateada
        })
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
