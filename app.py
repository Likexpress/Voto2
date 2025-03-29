from flask import Flask, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeSerializer, BadSignature
from datetime import datetime
from dotenv import load_dotenv
import os
import requests

load_dotenv()

app = Flask(__name__)
SECRET_KEY = os.environ.get("SECRET_KEY", "clave-super-secreta")
serializer = URLSafeSerializer(SECRET_KEY)

db_url = os.environ.get("DATABASE_URL", "sqlite:///votos.db")
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Voto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50), unique=True, nullable=False)
    ci = db.Column(db.BigInteger, unique=True, nullable=False)
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

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return redirect('/generar_link')

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
            return "ok", 200

        message = messages[0]
        numero = message['from']
        texto = message['text']['body'].strip().lower()

        if "votar" in texto:
            token = serializer.dumps("+" + numero)
            link = f"https://primariasbunker.org/votar?token={token}"
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
        return redirect("https://wa.me/59172902813?text=Quiero%20votar")
    return render_template("generar_link.html", paises=PAISES_CODIGOS)

@app.route('/votar')
def votar():
    token = request.args.get('token')
    if not token:
        return "Acceso no válido."
    try:
        numero = serializer.loads(token)
    except BadSignature:
        return "Enlace inválido o alterado."
    if Voto.query.filter_by(numero=numero).first():
        return render_template("voto_ya_registrado.html")
    return render_template("votar.html", numero=numero, recaptcha_site_key="")

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
    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()

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

    return render_template("voto_exitoso.html",
                           candidato=candidato,
                           numero=numero,
                           ci=ci,
                           dia=dia,
                           mes=mes,
                           anio=anio,
                           ciudad=ciudad,
                           pais=pais)

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

if __name__ == '__main__':
    app.run()
