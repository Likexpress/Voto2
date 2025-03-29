from flask import Flask, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeSerializer, BadSignature
from datetime import datetime
from dotenv import load_dotenv
import os

# ---------------------------
# Cargar configuración
# ---------------------------
load_dotenv()

app = Flask(__name__)
SECRET_KEY = os.environ.get("SECRET_KEY", "clave-super-secreta")
serializer = URLSafeSerializer(SECRET_KEY)

# ---------------------------
# Base de datos
# ---------------------------
db_url = os.environ.get("DATABASE_URL", "sqlite:///votos.db")
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
from flask_migrate import Migrate
migrate = Migrate(app, db)


# ---------------------------
# Modelo de votos
# ---------------------------
class Voto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
<<<<<<< HEAD
    numero = db.Column(db.String(50), unique=True, nullable=False, index=True)  # ✅ Índice agregado
    ci = db.Column(db.BigInteger, unique=True, nullable=False, index=True)      # ✅ Índice agregado
=======
    numero = db.Column(db.String(50), unique=True, nullable=False)
    ci = db.Column(db.BigInteger, unique=True, nullable=False)
>>>>>>> 6b136e3a2f5e04e28d32e0a652c8991dababba96
    candidato = db.Column(db.String(100), nullable=False)
    pais = db.Column(db.String(100), nullable=False)
    ciudad = db.Column(db.String(100), nullable=False)
    dia_nacimiento = db.Column(db.Integer, nullable=False)
    mes_nacimiento = db.Column(db.Integer, nullable=False)
    anio_nacimiento = db.Column(db.Integer, nullable=False)
    ip = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

<<<<<<< HEAD


=======
>>>>>>> 6b136e3a2f5e04e28d32e0a652c8991dababba96
with app.app_context():
    db.create_all()

# ---------------------------
# Página inicial
# ---------------------------
@app.route('/')
def index():
    return redirect('/generar_link')

# ---------------------------
# Generar link de votación
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
            return "Código de país inválido."

        numero_completo = pais + numero

        # Verificar si ya votó
        if Voto.query.filter_by(numero=numero_completo).first():
            return render_template("voto_ya_registrado.html")

        return redirect("https://wa.me/59172902813?text=Quiero%20votar")

    return render_template("generar_link.html", paises=PAISES_CODIGOS)

# ---------------------------
# Página para emitir voto
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

    if Voto.query.filter_by(numero=numero).first():
        return render_template("voto_ya_registrado.html")

    return render_template("votar.html", numero=numero)

# ---------------------------
# Enviar voto
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

    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()

    if not all([numero, ci, candidato, pais, ciudad, dia, mes, anio]):
        return "Faltan campos obligatorios."

    ci = int(ci)

    # Validar que no haya votado con ese número o CI
    if Voto.query.filter((Voto.numero == numero) | (Voto.ci == ci)).first():
        return render_template("voto_ya_registrado.html")

    nuevo_voto = Voto(
        numero=numero,
        ci=ci,
        candidato=candidato,
        pais=pais,
        ciudad=ciudad,
        dia_nacimiento=int(dia),
        mes_nacimiento=int(mes),
        anio_nacimiento=int(anio),
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

# ---------------------------
# Preguntas frecuentes
# ---------------------------
@app.route('/preguntas')
def preguntas_frecuentes():
    return render_template("preguntas.html")

# ---------------------------
# Lista de países
# ---------------------------
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
# Ejecutar app
# ---------------------------
if __name__ == '__main__':
    app.run()
