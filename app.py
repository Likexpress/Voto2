from flask import Flask, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
import os
import requests
from itsdangerous import SignatureExpired
from itsdangerous import URLSafeTimedSerializer
from paises import PAISES_CODIGOS

# ---------------------------
# Cargar configuración
# ---------------------------
load_dotenv()

app = Flask(__name__)
SECRET_KEY = os.environ.get("SECRET_KEY", "clave-super-secreta")
serializer = URLSafeTimedSerializer(SECRET_KEY)

# ---------------------------
# Base de datos
# ---------------------------
db_url = os.environ.get("DATABASE_URL", "sqlite:///votos.db")
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
from flask_migrate import Migrate
migrate = Migrate(app, db)



@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    import requests

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
            serializer = URLSafeTimedSerializer(os.environ.get("SECRET_KEY", "clave-super-secreta"))

            token = serializer.dumps("+" + numero)
            link = f"https://primariasbunker.org/votar?token={token}"

            # Guardar en la base de datos si no existe
            if not Solicitud.query.filter_by(numero="+" + numero).first():
                nueva_solicitud = Solicitud(numero="+" + numero)
                db.session.add(nueva_solicitud)
                db.session.commit()

            # Enviar mensaje por 360dialog
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
                print("✅ Enlace enviado correctamente.")
            else:
                print("❌ Error al enviar:", r.text)

    except Exception as e:
        print("❌ Error procesando mensaje:", str(e))

    return "ok", 200

# ---------------------------
# Modelo de votos
# ---------------------------
class Voto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50), unique=True, nullable=False, index=True)  # ✅ Índice agregado
    ci = db.Column(db.BigInteger, unique=True, nullable=False, index=True)      # ✅ Índice agregado
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

class Solicitud(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50), unique=True, nullable=False, index=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)


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
        numero = serializer.loads(token, max_age=600)  # 10 minutos
    except SignatureExpired:
        return "Este enlace ha expirado. Solicita uno nuevo por WhatsApp."
    except BadSignature:
        return "Enlace inválido o alterado."

    # Verificación en tabla Solicitud
    if not Solicitud.query.filter_by(numero=numero).first():
        return render_template("acceso_no_autorizado.html")

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
    lat = request.form.get('latitud')
    lon = request.form.get('longitud')

    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()

    # Verificar que el número esté en la tabla de solicitudes
    if not Solicitud.query.filter_by(numero=numero).first():
        return render_template("acceso_no_autorizado.html")

    # Validación de campos obligatorios
    if not all([numero, ci, candidato, pais, ciudad, dia, mes, anio]):
        return render_template("error.html", mensaje="Faltan campos obligatorios.")


    try:
        ci = int(ci)
    except ValueError:
        return "CI inválido."

    # Verificar si ya votó con ese número o CI
    if Voto.query.filter((Voto.numero == numero) | (Voto.ci == ci)).first():
        return render_template("voto_ya_registrado.html")

    # Guardar el voto
    nuevo_voto = Voto(
        numero=numero,
        ci=ci,
        candidato=candidato,
        pais=pais,
        ciudad=ciudad,
        dia_nacimiento=int(dia),
        mes_nacimiento=int(mes),
        anio_nacimiento=int(anio),
        ip=ip,
        latitud=float(lat) if lat else None,
        longitud=float(lon) if lon else None
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


# ---------------------------
# Ejecutar app
# ---------------------------
if __name__ == '__main__':
    app.run()
