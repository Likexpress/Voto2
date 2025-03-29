from flask import Flask, request, render_template, redirect
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
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ---------------------------
# Modelo de datos
# ---------------------------
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

# ---------------------------
# Página de inicio
# ---------------------------
@app.route('/')
def index():
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

    recaptcha_site_key = os.environ.get("RECAPTCHA_SITE_KEY", "")
    return render_template("votar.html", numero=numero, recaptcha_site_key=recaptcha_site_key)

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
