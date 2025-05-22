# app.py
from flask import Flask, request, jsonify
import json # Importar json para pretty print en depuracion y manejo de errores

app = Flask(__name__)

# Sub-Paso 1.2: Estructura de datos de ejemplo en memoria
# ESTOS SON TUS DATOS DE EJEMPLO DE CITAS. PUEDES A\u00D1ADIR M\u00C1S AQU\u00CD.
citas_ejemplo = {
    "XYZ123": {
        "numero_confirmacion": "XYZ123",
        "servicio": "Corte de Cabello",
        "fecha": "2025-05-20",
        "hora": "14:00",
        "cliente_nombre": "Juan Perez"
    },
    "ABC789": {
        "numero_confirmacion": "ABC789",
        "servicio": "Masaje",
        "fecha": "2025-05-22",
        "hora": "10:30",
        "cliente_nombre": "Maria Rodriguez"
    },
    "DEF456": {
        "numero_confirmacion": "DEF456",
        "servicio": "Manicura",
        "fecha": "2025-05-21",
        "hora": "16:00",
        "cliente_nombre": "Ana Gomez"
    }
}

# Sub-Paso 1.3: Crear el Endpoint /consultar-cita
@app.route('/consultar-cita', methods=['POST'])
def consultar_cita():
    # Sub-Paso 1.4: Implementar la L\u00F3gica de Consulta y Respuesta

    # --- Inicio de Depuraci\u00F3n: Imprimir solicitud recibida ---
    print("\n--- Solicitud Webhook recibida ---")
    print("M\u00E9todo:", request.method)
    print("URL:", request.url)
    print("Encabezados:", request.headers)
    # Usa request.get_data() para obtener el cuerpo crudo ANTES de intentar parsearlo como JSON
    raw_body = request.get_data()
    print("Cuerpo crudo:", raw_body)
    print("------------------------------------")
    # --- Fin de Depuraci\u00F3n ---


    # 1. Recibir y parsear el JSON de la solicitud de Webhook de Dialogflow CX
    request_data = None
    try:
        # Intenta parsear el cuerpo como JSON. Si el Content-Type es application/json, esto funcionar\u00E1 autom\u00E1ticamente.
        request_data = request.get_json() # No usamos force=True ahora que sabemos enviar Content-Type correctamente

        # --- Opcional: Imprimir el JSON parseado si fue exitoso ---
        # print("JSON parseado:")
        # print(json.dumps(request_data, indent=2))
        # -------------------------------------------------------

        if request_data is None:
             # Esto puede ocurrir si el Content-Type no era application/json o si el cuerpo estaba vac\u00EDo/inv\u00E1lido
             print("Error: request.get_json() devolvi\u00F3 None.")
             return jsonify({
                 "fulfillmentResponse": {
                     "messages": [
                         {
                             "text": {
                                 "text": ["Error interno del API: No se pudo parsear el cuerpo de la solicitud como JSON."]
                             }
                         }
                     ]
                 }
             }), 400 # HTTP 400 Bad Request

    except Exception as e:
         # Captura cualquier otro error durante el parseo del JSON
         print(f"Error inesperado al parsear JSON: {e}")
         return jsonify({
             "fulfillmentResponse": {
                 "messages": [
                     {
                         "text": {
                             "text": [f"Error interno del API: Falla al procesar JSON. Detalle: {e}"]
                         }
                     }
                 ]
             }
         }), 400 # HTTP 400 Bad Request


    numero_confirmacion = None
    # Extraer el confirmation_number del JSON recibido.
    # La estructura t\u00EDpica de DFCX es request_data['queryParams']['parameters']['nombre_parametro_en_dfcx']
    try:
        # Usamos .get() con diccionarios vac\u00EDos {} por defecto para evitar KeyError si queryParams o parameters no existen
        # Aseg\u00FArate que 'confirmation_number' coincide EXACTAMENTE con el nombre del par\u00E1metro en tu formulario/Intent de DFCX
        numero_confirmacion = request_data.get('queryParams', {}).get('parameters', {}).get('confirmation_number')

        if numero_confirmacion is None:
             # Si el par\u00E1metro no se encontr\u00F3 o es None en la estructura JSON recibida
             print("Par\u00E1metro 'confirmation_number' no encontrado o es None en el JSON.")
             return jsonify({
                 "fulfillmentResponse": {
                     "messages": [
                         {
                             "text": {
                                 "text": ["Error interno del API: No se recibi\u00F3 el par\u00E1metro de n\u00FAmero de confirmaci\u00F3n."]
                             }
                         }
                     ]
                 }
             }), 400 # HTTP 400 Bad Request


        print(f"N\u00FAmero de confirmaci\u00F3n extra\u00EDdo: {numero_confirmacion}") # Para depuraci\u00F3n

    except Exception as e:
         # Captura cualquier otro error durante la extracci\u00F3n del par\u00E1metro
         print(f"Error inesperado al extraer par\u00E1metro: {e}")
         return jsonify({
             "fulfillmentResponse": {
                 "messages": [
                     {
                         "text": {
                             "text": [f"Error interno inesperado del API al procesar par\u00E1metro. Detalle: {e}"]
                         }
                     }
                 ]
             }
         }), 500 # HTTP 500 Internal Server Error


    # 2. Buscar la cita usando el n\u00FAmero de confirmaci\u00F3n
    # Usamos .get() en el diccionario citas_ejemplo para buscar.
    # Convertimos el n\u00FAmero a may\u00FAsculas .upper() si tus claves en citas_ejemplo est\u00E1n en may\u00FAsculas,
    # para hacer la b\u00FAsqueda insensible a may\u00FAsculas/min\u00FAsculas si el usuario lo dicta diferente.
    cita_encontrada = citas_ejemplo.get(numero_confirmacion.upper()) # Considerar .upper() si es el caso

    # 3. Construir la respuesta JSON en el formato esperado por Dialogflow CX
    response_dfcx = {}

    if cita_encontrada:
        # Cita encontrada: Construir respuesta de \u00E9xito
        response_text = (
            f"Su cita con n\u00FAmero {cita_encontrada['numero_confirmacion']} "
            f"para {cita_encontrada['servicio']} est\u00E1 agendada para el "
            f"{cita_encontrada['fecha']} a las {cita_encontrada['hora']}."
        )

        response_dfcx = {
            "fulfillmentResponse": {
                "messages": [
                    {
                        "text": {
                            "text": [response_text]
                        }
                    }
                ]
            },
            # Opcional: Puedes devolver los detalles de la cita como par\u00E1metros de sesi\u00F3n a DFCX
            "sessionInfo": {
                 "parameters": {
                     "appointment_found": True,
                     "appointment_number_returned": cita_encontrada['numero_confirmacion'], # Devuelve el n\u00FAmero encontrado
                     "appointment_date": cita_encontrada['fecha'],
                     "appointment_time": cita_encontrada['hora'],
                     "appointment_service": cita_encontrada['servicio'],
                     "client_name": cita_encontrada['cliente_nombre']
                 }
              }
        }
        print("Cita encontrada. Respondiendo a DFCX con detalles.") # Para depuraci\u00F3n
        return jsonify(response_dfcx), 200 # HTTP 200 OK

    else:
        # Cita no encontrada: Construir respuesta de "no encontrada"
        response_dfcx = {
            "fulfillmentResponse": {
                "messages": [
                    {
                        "text": {
                            "text": [f"Lo siento, no encontr\u00E9 una cita con el n\u00FAmero de confirmaci\u00F3n {numero_confirmacion}."]
                        }
                    }
                ]
            },
             "sessionInfo": {
                 "parameters": {
                     "appointment_found": False,
                     "appointment_number_returned": numero_confirmacion # Devuelve el n\u00FAmero buscado
                 }
              }
        }
        print("Cita no encontrada. Respondiendo a DFCX con mensaje de no encontrada.") # Para depuraci\u00F3n
        # Devolvemos 200 OK porque la solicitud al webhook fue procesada exitosamente,
        # aunque la cita no se encontrara en los datos.
        return jsonify(response_dfcx), 200

# Para ejecutar localmente usando `python app.py`
if __name__ == '__main__':
    # Ejecuta la aplicaci\u00F3n en modo debug (se reinicia con cambios y muestra errores)
    # En despliegue real (Cloud Functions/Run) no usas app.run() directamente as\u00ED.
    app.run(debug=True, port=5000) # El puerto 5000 es com\u00FAn para desarrollo local