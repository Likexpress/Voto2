from flask import Flask, request, render_template, redirect
<<<<<<< HEAD
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeSerializer, BadSignature
from datetime import datetime
from dotenv import load_dotenv
import os
import requests

# ---------------------------
# Cargar variables del archivo .env
# ---------------------------
load_dotenv()

# ---------------------------
# Inicializar la app
# ---------------------------
app = Flask(__name__)
SECRET_KEY = os.environ.get("SECRET_KEY", "clave-super-secreta")
serializer = URLSafeSerializer(SECRET_KEY)

# ---------------------------
# Configuración de la base de datos
# ---------------------------
db_url = os.environ.get("DATABASE_URL", "sqlite:///votos.db")
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
=======
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeSerializer, BadSignature
import os
import requests
import phonenumbers
from phonenumbers import geocoder, carrier, PhoneNumberFormat, region_code_for_country_code, COUNTRY_CODE_TO_REGION_CODE
from phonenumbers import geocoder, carrier

# COdigo Funcional
# ---------------------------
# Inicialización de la aplicación Flask
# ---------------------------
app = Flask(__name__)
SECRET_KEY = os.environ.get("SECRET_KEY", "clave-secreta-segura")
serializer = URLSafeSerializer(SECRET_KEY)
IPQUALITY_API_KEY = os.environ.get("IPQUALITY_API_KEY")

# ---------------------------
# Configuración de la base de datos PostgreSQL
# ---------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
8cf28b4428885cc5cb91ed4d67c1438aac69f77c
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ---------------------------
<<<<<<< HEAD
# Modelo de datos
=======
# Modelo de tabla: Voto
>>>>>>> 8cf28b4428885cc5cb91ed4d67c1438aac69f77c
# ---------------------------
class Voto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50), unique=True, nullable=False)
<<<<<<< HEAD
    ci = db.Column(db.BigInteger, unique=True, nullable=False)
=======
    ci = db.Column(db.BigInteger, nullable=False)
>>>>>>> 8cf28b4428885cc5cb91ed4d67c1438aac69f77c
    candidato = db.Column(db.String(100), nullable=False)
    pais = db.Column(db.String(100), nullable=False)
    ciudad = db.Column(db.String(100), nullable=False)
    dia_nacimiento = db.Column(db.Integer, nullable=False)
    mes_nacimiento = db.Column(db.Integer, nullable=False)
    anio_nacimiento = db.Column(db.Integer, nullable=False)
    latitud = db.Column(db.Float, nullable=True)
    longitud = db.Column(db.Float, nullable=True)
    ip = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

<<<<<<< HEAD
=======
# ---------------------------
# Crear tabla si no existe
# ---------------------------
>>>>>>> 8cf28b4428885cc5cb91ed4d67c1438aac69f77c
with app.app_context():
    db.create_all()

# ---------------------------
<<<<<<< HEAD
=======
# Función para verificar IP con IPQualityScore
# ---------------------------
def ip_es_vpn(ip):
    if not IPQUALITY_API_KEY or not ip:
        return False
    try:
        url = f"https://ipqualityscore.com/api/json/ip/{IPQUALITY_API_KEY}/{ip}"
        res = requests.get(url)
        data = res.json()
        return data.get("proxy") or data.get("vpn") or data.get("tor")
    except:
        return False

# ---------------------------
>>>>>>> 8cf28b4428885cc5cb91ed4d67c1438aac69f77c
# Página de inicio
# ---------------------------
@app.route('/')
def index():
<<<<<<< HEAD
    return redirect('/generar_link')

# ---------------------------
# Webhook para recibir mensajes en WhatsApp
# ---------------------------
@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    data = request.json
    print("📥 JSON recibido:", data)

    try:
        entry = data['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        messages = value.get('messages')

        if not messages:
            return "ok", 200  # No hay mensaje nuevo

        message = messages[0]
        numero = message['from']  # Número en formato internacional sin "+"
        texto = message['text']['body'].strip().lower()

        if "votar" in texto:
            token = serializer.dumps("+" + numero)
            link = f"https://primariasbunker.org/votar?token={token}"

            # Preparar datos para 360dialog
            url = "https://waba-v2.360dialog.io/messages"

            headers = {
                "Content-Type": "application/json",
                "D360-API-KEY": os.environ.get("WABA_TOKEN")
            }
            body = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": f"Hola, gracias por participar en las Primarias Bolivia 2025.\n\nAquí tienes tu enlace único para votar:\n{link}"
                }
            }

            r = requests.post(url, headers=headers, json=body)

            if r.status_code == 200:
                print("✅ Enlace enviado correctamente por WhatsApp.")
            else:
                print("❌ Error al enviar respuesta:", r.text)

    except Exception as e:
        print("❌ Error al procesar mensaje:", str(e))

    return "ok", 200




# ---------------------------
# Formulario para generar link (opcional)
# ---------------------------
@app.route('/generar_link', methods=['GET', 'POST'])
def generar_link():
    if request.method == 'POST':
        pais = request.form.get('pais')
        numero = request.form.get('numero')

        if not pais or not numero:
            return "Por favor, selecciona un país e ingresa tu número."

        numero = numero.replace(" ", "").replace("-", "")
        if not pais.startswith("+"):
            return "El formato del código de país es incorrecto."

        numero_completo = pais + numero
        return redirect(f"https://wa.me/{numero_completo}?text=Quiero%20votar")

    return render_template("generar_link.html", paises=PAISES_CODIGOS)

# ---------------------------
# Página de votación
=======
    return "Bienvenido al sistema de votación. Este enlace debe ser accedido desde WhatsApp."

# ---------------------------
# Página de votación protegida con token cifrado
>>>>>>> 8cf28b4428885cc5cb91ed4d67c1438aac69f77c
# ---------------------------
@app.route('/votar')
def votar():
    token = request.args.get('token')
    if not token:
        return "Acceso no válido."

    try:
        numero = serializer.loads(token)
    except BadSignature:
        return "Enlace inválido o alterado."

<<<<<<< HEAD
    if Voto.query.filter_by(numero=numero).first():
        return render_template("voto_ya_registrado.html")

    recaptcha_site_key = os.environ.get("RECAPTCHA_SITE_KEY", "")
    return render_template("votar.html", numero=numero, recaptcha_site_key=recaptcha_site_key)
=======
    voto_existente = Voto.query.filter_by(numero=numero).first()
    if voto_existente:
        return f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
          <meta charset="UTF-8">
          <title>Voto ya registrado</title>
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
          <style>
            body {{
              background-color: #f8f9fa;
            }}
            .mensaje-wrapper {{
              max-width: 700px;
              margin: 60px auto;
              padding: 30px;
              background: #fff;
              border-radius: 8px;
              box-shadow: 0 0 10px rgba(0,0,0,0.05);
              text-align: center;
            }}
            .mensaje-wrapper h3 {{
              color: #dc3545;
            }}
          </style>
        </head>
        <body>
          <div class="mensaje-wrapper">
            <h3>Voto ya registrado</h3>
            <p class="mt-3 fs-5">
              Nuestro sistema ha detectado que este número ya ha emitido su voto.
            </p>
            <p class="text-muted">
              Agradecemos tu participación en este proceso democrático.
            </p>
            <hr>
            <p class="text-secondary">Si crees que esto es un error, por favor contacta con el equipo organizador.</p>
          </div>
        </body>
        </html>
        """


    x_forwarded_for = request.headers.get('X-Forwarded-For')
    ip = x_forwarded_for.split(',')[0].strip() if x_forwarded_for else request.remote_addr


    if ip_es_vpn(ip):
        return "No se permite votar desde conexiones de VPN o proxy. Por favor, desactiva tu VPN."

    votos_misma_ip = Voto.query.filter_by(ip=ip).count()

    if votos_misma_ip >= 10:
        return f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
          <meta charset="UTF-8">
          <title>Voto ya registrado</title>
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
          <style>
            body {{
              background-color: #f8f9fa;
            }}
            .mensaje-wrapper {{
              max-width: 700px;
              margin: 60px auto;
              padding: 30px;
              background: #fff;
              border-radius: 8px;
              box-shadow: 0 0 10px rgba(0,0,0,0.05);
              text-align: center;
            }}
            .mensaje-wrapper h3 {{
              color: #dc3545;
            }}
          </style>
        </head>
        <body>
          <div class="mensaje-wrapper">
            <h3>Voto ya registrado</h3>
            <p class="mt-3 fs-5">
              Nuestro sistema ha detectado que este número ya ha emitido su voto.
            </p>
            <p class="text-muted">
              Agradecemos tu participación en este proceso democrático.
            </p>
            <hr>
            <p class="text-secondary">Si crees que esto es un error, por favor contacta con el equipo organizador.</p>
          </div>
        </body>
        </html>
        """


    return render_template("votar.html", numero=numero)
>>>>>>> 8cf28b4428885cc5cb91ed4d67c1438aac69f77c

# ---------------------------
# Procesar el voto
# ---------------------------
@app.route('/enviar_voto', methods=['POST'])
def enviar_voto():
    numero = request.form.get('numero')
    ci = request.form.get('ci')
    candidato = request.form.get('candidato')
    pais = request.form.get('pais')
    ciudad = request.form.get('ciudad')
    dia = request.form.get('dia_nacimiento')
    mes = request.form.get('mes_nacimiento')
    anio = request.form.get('anio_nacimiento')
    lat = request.form.get('latitud')
    lon = request.form.get('longitud')
<<<<<<< HEAD
    recaptcha_token = request.form.get('recaptcha_token')

    x_forwarded_for = request.headers.get('X-Forwarded-For')
    ip = x_forwarded_for.split(',')[0].strip() if x_forwarded_for else request.remote_addr

    # Validar reCAPTCHA
    recaptcha_secret = os.environ.get("RECAPTCHA_SECRET_KEY", "")
    resultado = requests.post("https://www.google.com/recaptcha/api/siteverify", data={
        "secret": recaptcha_secret,
        "response": recaptcha_token
    }).json()
    if not resultado.get("success") or resultado.get("score", 0) < 0.5:
        return render_template("recaptcha_invalido.html")

    # Validar navegador
    ua = request.headers.get('User-Agent', '').lower()
    if not any(n in ua for n in ['chrome', 'firefox', 'safari', 'edge', 'opera', 'mobile']):
        return render_template("navegador_no_valido.html")

    if not all([numero, ci, pais, ciudad, dia, mes, anio, candidato]):
        return "Faltan campos obligatorios."

    ci = int(ci)

    if Voto.query.filter((Voto.numero == numero) | (Voto.ci == ci)).first():
        return render_template("voto_ya_registrado.html")

    if Voto.query.filter_by(ip=ip).count() >= 10:
        return render_template("limite_ip.html")

    if Voto.query.filter_by(ip=ip, ciudad=ciudad, candidato=candidato,
                            dia_nacimiento=int(dia), mes_nacimiento=int(mes), anio_nacimiento=int(anio)).count() >= 3:
        return render_template("voto_sospechoso.html")

    try:
        if lat and lon:
            res = requests.get("https://nominatim.openstreetmap.org/reverse", params={
                "format": "json", "lat": lat, "lon": lon, "zoom": 10, "addressdetails": 1
            }, headers={"User-Agent": "VotacionCiudadana/1.0"})
            data = res.json()
            if ciudad.lower() not in data.get("address", {}).get("city", "").lower() and \
               ciudad.lower() != data.get("address", {}).get("town", "").lower():
                return "La ciudad seleccionada no coincide con tu ubicación GPS."
            if pais.lower() not in data.get("address", {}).get("country", "").lower():
                return "El país seleccionado no coincide con tu ubicación GPS."
    except Exception as e:
        print("Error validando ubicación GPS:", e)

    nuevo_voto = Voto(
        numero=numero,
        ci=ci,
=======
    x_forwarded_for = request.headers.get('X-Forwarded-For')
    ip = x_forwarded_for.split(',')[0].strip() if x_forwarded_for else request.remote_addr


    if not numero:
        return "Error: el número de WhatsApp es obligatorio."
    if not ci:
        return "Error: el número de carnet de identidad es obligatorio."
    if not pais:
        return "Error: el país es obligatorio."
    if not ciudad:
        return "Error: la ciudad es obligatoria."
    if not dia:
        return "Error: el día de nacimiento es obligatorio."
    if not mes:
        return "Error: el mes de nacimiento es obligatorio."
    if not anio:
        return "Error: el año de nacimiento es obligatorio."
    if not candidato:
        return "Error: debes seleccionar un candidato."

    if Voto.query.filter_by(numero=numero).first():
        return "Ya registramos tu voto."
    if ip_es_vpn(ip):
        return "Voto denegado. No se permite votar desde una VPN o proxy."
    votos_misma_ip = Voto.query.filter_by(ip=ip).count()
    if votos_misma_ip >= 10:
        return "Se ha alcanzado el límite de votos permitidos desde esta conexión."

    nuevo_voto = Voto(
        numero=numero,
        ci=int(ci),
>>>>>>> 8cf28b4428885cc5cb91ed4d67c1438aac69f77c
        candidato=candidato,
        pais=pais,
        ciudad=ciudad,
        dia_nacimiento=int(dia),
        mes_nacimiento=int(mes),
        anio_nacimiento=int(anio),
        latitud=float(lat) if lat else None,
        longitud=float(lon) if lon else None,
        ip=ip
    )
    db.session.add(nuevo_voto)
    db.session.commit()

<<<<<<< HEAD
    return render_template("voto_exitoso.html",
                           candidato=candidato,
                           numero=numero,
                           ci=ci,
                           dia=dia,
                           mes=mes,
                           anio=anio,
                           ciudad=ciudad,
                           pais=pais)

# ---------------------------
# Países (puedes ampliarlo)
# ---------------------------
PAISES_CODIGOS = {
    "Bolivia": "+591"
}

# ---------------------------
# Ejecutar localmente
# ---------------------------
if __name__ == '__main__':
    app.run()
=======
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Voto registrado</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{
                background-color: #f8f9fa;
                padding-top: 50px;
            }}
            .card-confirmacion {{
                max-width: 600px;
                margin: auto;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 12px rgba(0,0,0,0.08);
                background-color: #fff;
            }}
            .titulo {{
                color: #198754;
                font-weight: bold;
            }}
            .detalle {{
                font-size: 1.1rem;
            }}
        </style>
    </head>
    <body>
        <div class="card card-confirmacion text-center">
            <h3 class="titulo mb-4">¡Tu voto ha sido registrado exitosamente!</h3>
            <div class="detalle text-start">
                <p><strong>Candidato elegido:</strong> {candidato}</p>
                <p><strong>Número de WhatsApp:</strong> {numero}</p>
                <p><strong>Carnet de Identidad:</strong> {ci}</p>
                <p><strong>Fecha de Nacimiento:</strong> {dia}/{mes}/{anio}</p>
                <p><strong>Ubicación:</strong> {ciudad}, {pais}</p>
            </div>
            <hr class="my-4">
            <p class="text-muted">Gracias por participar en las <strong>Elecciones Ciudadanas 2025</strong>.</p>
            <p class="text-muted">Tu voz ha sido registrada y cuenta para el futuro democrático de Bolivia.</p>
        </div>
    </body>
    </html>
    """



# ---------------------------
# Enviar mensaje con link cifrado vía WhatsApp
# ---------------------------
@app.route('/whatsapp', methods=['POST'])
def whatsapp_reply():
    sender = request.values.get('From', '')
    numero = sender.replace("whatsapp:", "").strip()

    token = serializer.dumps(numero)
    link_votacion = f"https://primariasbunker.org/votar?token={token}"

    response = MessagingResponse()
    msg = response.message()
    msg.body(f"Hola, gracias por ser parte de este proceso democrático.\n\n"
             f"Haz clic en el siguiente enlace para emitir tu voto en las Votaciones Primarias Bolivia 2025:\n"
             f"{link_votacion}")
    return str(response)



# ---------------------------
# Rutas para desarrollo
# ---------------------------
@app.route('/eliminar_tabla_voto')
def eliminar_tabla_voto():
    try:
        Voto.__table__.drop(db.engine)
        return "La tabla 'voto' ha sido eliminada correctamente."
    except Exception as e:
        return f"Error al eliminar la tabla: {str(e)}"

@app.route('/crear_tabla_voto')
def crear_tabla_voto():
    try:
        with app.app_context():
            db.create_all()
        return "La tabla 'voto' ha sido creada exitosamente."
    except Exception as e:
        return f"Error al crear la tabla: {str(e)}"




@app.route('/generar_link', methods=['GET', 'POST'])
def generar_link():
    if request.method == 'POST':
        pais = request.form.get('pais')
        numero = request.form.get('numero')

        if not pais or not numero:
            return "Por favor, selecciona un país e ingresa tu número."

        numero = numero.replace(" ", "").replace("-", "")

        if not pais.startswith("+"):
            return "El formato del código de país es incorrecto."

        numero_completo = pais + numero
        token = serializer.dumps(numero_completo)
        return redirect(f"/votar?token={token}")

    return render_template("generar_link.html", paises=PAISES_CODIGOS)


    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Inicio de Votación</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                background-color: #f8f9fa;
                padding-top: 60px;
                font-family: Arial, sans-serif;
            }
            .card {
                max-width: 500px;
                margin: auto;
                padding: 30px;
                border-radius: 10px;
                background: #fff;
                box-shadow: 0 0 15px rgba(0,0,0,0.06);
            }
            .logo {
                width: 150px;
                margin-bottom: 20px;
            }
            footer {
                text-align: center;
                font-size: 0.9rem;
                color: #777;
                margin-top: 40px;
            }
        </style>
    </head>
    <body>
        <div class="card text-center">
            <div class="text-center mb-4">
              <img src="/static/img/logo.png" alt="Logo Bunker" class="logo">
            </div>

            <h3><strong>¡Bienvenido a las Votaciones Primarias 2025!</strong></h3>
            <p class="text-muted">Para comenzar, selecciona tu país e ingresa tu número de WhatsApp. Recuerda que solo puedes votar una vez por número.</p>
            <form method="POST">
                <div class="mb-3 text-start">
                    <label for="pais" class="form-label">País</label>
                    <select name="pais" id="pais" class="form-select" required>
                        <option value="">Selecciona un país</option>
                        {% for nombre, codigo in paises.items() %}
                            <option value="{{ codigo }}">{{ nombre }} ({{ codigo }})</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="mb-3 text-start">
                    <label for="numero" class="form-label">Número de WhatsApp</label>
                    <input type="text" name="numero" id="numero" class="form-control" placeholder="Ej: 70000000" required>
                </div>
                <button type="submit" class="btn btn-success w-100">Obtener enlace de votación</button>
            </form>
        </div>
        <footer class="mt-4">
            &copy; 2025 Primarias Bunker<br>
            <small>Participación ciudadana por un futuro democrático</small>
        </footer>
    </body>
    </html>

    """








PAISES_CODIGOS = {
    "Afganistán": "+93",
    "Albania": "+355",
    "Alemania": "+49",
    "Andorra": "+376",
    "Angola": "+244",
    "Antigua y Barbuda": "+1-268",
    "Arabia Saudita": "+966",
    "Argelia": "+213",
    "Argentina": "+54",
    "Armenia": "+374",
    "Australia": "+61",
    "Austria": "+43",
    "Azerbaiyán": "+994",
    "Bahamas": "+1-242",
    "Bangladés": "+880",
    "Barbados": "+1-246",
    "Baréin": "+973",
    "Bélgica": "+32",
    "Belice": "+501",
    "Benín": "+229",
    "Bielorrusia": "+375",
    "Birmania (Myanmar)": "+95",
    "Bolivia": "+591",
    "Bosnia y Herzegovina": "+387",
    "Botsuana": "+267",
    "Brasil": "+55",
    "Brunéi": "+673",
    "Bulgaria": "+359",
    "Burkina Faso": "+226",
    "Burundi": "+257",
    "Bután": "+975",
    "Cabo Verde": "+238",
    "Camboya": "+855",
    "Camerún": "+237",
    "Canadá": "+1",
    "Catar": "+974",
    "Chad": "+235",
    "Chile": "+56",
    "China": "+86",
    "Chipre": "+357",
    "Colombia": "+57",
    "Comoras": "+269",
    "Corea del Norte": "+850",
    "Corea del Sur": "+82",
    "Costa de Marfil": "+225",
    "Costa Rica": "+506",
    "Croacia": "+385",
    "Cuba": "+53",
    "Dinamarca": "+45",
    "Dominica": "+1-767",
    "Ecuador": "+593",
    "Egipto": "+20",
    "El Salvador": "+503",
    "Emiratos Árabes Unidos": "+971",
    "Eritrea": "+291",
    "Eslovaquia": "+421",
    "Eslovenia": "+386",
    "España": "+34",
    "Estados Unidos": "+1",
    "Estonia": "+372",
    "Esuatini": "+268",
    "Etiopía": "+251",
    "Filipinas": "+63",
    "Finlandia": "+358",
    "Fiyi": "+679",
    "Francia": "+33",
    "Gabón": "+241",
    "Gambia": "+220",
    "Georgia": "+995",
    "Ghana": "+233",
    "Granada": "+1-473",
    "Grecia": "+30",
    "Guatemala": "+502",
    "Guinea": "+224",
    "Guinea-Bisáu": "+245",
    "Guinea Ecuatorial": "+240",
    "Guyana": "+592",
    "Haití": "+509",
    "Honduras": "+504",
    "Hungría": "+36",
    "India": "+91",
    "Indonesia": "+62",
    "Irak": "+964",
    "Irán": "+98",
    "Irlanda": "+353",
    "Islandia": "+354",
    "Israel": "+972",
    "Italia": "+39",
    "Jamaica": "+1-876",
    "Japón": "+81",
    "Jordania": "+962",
    "Kazajistán": "+7",
    "Kenia": "+254",
    "Kirguistán": "+996",
    "Kiribati": "+686",
    "Kuwait": "+965",
    "Laos": "+856",
    "Lesoto": "+266",
    "Letonia": "+371",
    "Líbano": "+961",
    "Liberia": "+231",
    "Libia": "+218",
    "Liechtenstein": "+423",
    "Lituania": "+370",
    "Luxemburgo": "+352",
    "Madagascar": "+261",
    "Malasia": "+60",
    "Malaui": "+265",
    "Maldivas": "+960",
    "Malí": "+223",
    "Malta": "+356",
    "Marruecos": "+212",
    "Islas Marshall": "+692",
    "Mauricio": "+230",
    "Mauritania": "+222",
    "México": "+52",
    "Micronesia": "+691",
    "Moldavia": "+373",
    "Mónaco": "+377",
    "Mongolia": "+976",
    "Montenegro": "+382",
    "Mozambique": "+258",
    "Namibia": "+264",
    "Nauru": "+674",
    "Nepal": "+977",
    "Nicaragua": "+505",
    "Níger": "+227",
    "Nigeria": "+234",
    "Noruega": "+47",
    "Nueva Zelanda": "+64",
    "Omán": "+968",
    "Países Bajos": "+31",
    "Pakistán": "+92",
    "Palaos": "+680",
    "Palestina": "+970",
    "Panamá": "+507",
    "Papúa Nueva Guinea": "+675",
    "Paraguay": "+595",
    "Perú": "+51",
    "Polonia": "+48",
    "Portugal": "+351",
    "Reino Unido": "+44",
    "República Centroafricana": "+236",
    "República Checa": "+420",
    "República del Congo": "+242",
    "República Democrática del Congo": "+243",
    "República Dominicana": "+1-809",
    "Ruanda": "+250",
    "Rumanía": "+40",
    "Rusia": "+7",
    "Samoa": "+685",
    "San Cristóbal y Nieves": "+1-869",
    "San Marino": "+378",
    "San Vicente y las Granadinas": "+1-784",
    "Santa Lucía": "+1-758",
    "Santo Tomé y Príncipe": "+239",
    "Senegal": "+221",
    "Serbia": "+381",
    "Seychelles": "+248",
    "Sierra Leona": "+232",
    "Singapur": "+65",
    "Siria": "+963",
    "Somalia": "+252",
    "Sri Lanka": "+94",
    "Sudáfrica": "+27",
    "Sudán": "+249",
    "Sudán del Sur": "+211",
    "Suecia": "+46",
    "Suiza": "+41",
    "Surinam": "+597",
    "Tailandia": "+66",
    "Tanzania": "+255",
    "Tayikistán": "+992",
    "Timor Oriental": "+670",
    "Togo": "+228",
    "Tonga": "+676",
    "Trinidad y Tobago": "+1-868",
    "Túnez": "+216",
    "Turkmenistán": "+993",
    "Turquía": "+90",
    "Tuvalu": "+688",
    "Ucrania": "+380",
    "Uganda": "+256",
    "Uruguay": "+598",
    "Uzbekistán": "+998",
    "Vanuatu": "+678",
    "Vaticano": "+379",
    "Venezuela": "+58",
    "Vietnam": "+84",
    "Yemen": "+967",
    "Yibuti": "+253",
    "Zambia": "+260",
    "Zimbabue": "+263"
}


# ---------------------------
# Ejecutar la app localmente
# ---------------------------
if __name__ == '__main__':
    app.run(debug=True)
>>>>>>> 8cf28b4428885cc5cb91ed4d67c1438aac69f77c
