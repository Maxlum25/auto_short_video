from flask import *
from dotenv import load_dotenv
import os
import glob
import time
import re
import shutil
import secrets
from tools import es_publico, a_seg, descargar_video
import credential
from clases import ShortParams


load_dotenv()

APP_SECRET_KEY=os.getenv("APP_SECRET_KEY")
if not APP_SECRET_KEY:
    raise RuntimeError("Falta APP_SECRET_KEY en el entorno (.env)")

SHORT_TTL = 30 * 60  # los shorts viven 30 min: reintentable sin refrescar, luego se liberan

def limpiar_viejos():
    ahora = time.time()
    for p in glob.glob("multimedia/*/short_*.mp4"):
        try:
            if ahora - os.path.getmtime(p) > SHORT_TTL:
                os.remove(p)
        except OSError:
            pass

def user_dir():
    username = re.sub(r"[^A-Za-z0-9_-]", "_", session.get("username") or "anon")
    return f"multimedia/{username}"

app = Flask(__name__)
app.secret_key = APP_SECRET_KEY
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")

@app.before_request
def csrf_protect():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)
    if request.method == "POST":
        if request.form.get("csrf_token") != session.get("csrf_token"):
            return "CSRF inválido", 400

@app.route('/', methods=['GET', 'POST'])
def index():
    error_link_youtube = None
    error_time_range = None
    error_titulo = None
    if not session.get("flag_session") or not session.get("username"):
        return redirect(url_for("login"))
    workdir = user_dir()
    limpiar_viejos()

    if request.method == "POST":
        titulos = []
        inicio_shorts = []
        final_shorts = []
        potencia_whispers = []
        youtube_url = request.form.get("youtube_url")

        for i in range(1, 6):
            if not request.form.get(f"inicio_short_{i}"): # Si no hay un inicio para el short, se rompe el bucle
                break
            titulos.append(request.form.get(f"titulo_short_{i}"))            
            inicio_shorts.append(request.form.get(f"inicio_short_{i}"))
            final_shorts.append(request.form.get(f"final_short_{i}"))
            potencia_whispers.append(request.form.get(f"potencia_whisper_{i}"))

        if not youtube_url or ("www.youtube.com" not in youtube_url and "youtu.be" not in youtube_url): # Solo se permite links de youtube
            error_link_youtube = "Ingresa un link de youtube valido"
            return render_template("index.html", error_link_youtube=error_link_youtube)

        if not es_publico(youtube_url): # Verifica si el video es publico
            error_link_youtube = "El video no es público o no se puede acceder a él"
            return render_template("index.html", error_link_youtube=error_link_youtube)

        patron_hora = re.compile(r"^\d+:[0-5]\d:[0-5]\d$")
        for i, j in zip(inicio_shorts, final_shorts):
            if not patron_hora.fullmatch(i or "") or not patron_hora.fullmatch(j or ""):
                error_time_range = "Formato de tiempo inválido, usa HH:MM:SS"
                return render_template("index.html", error_time_range=error_time_range)
            if a_seg(i) > a_seg(j): # Verifica que el inicio no sea mayor que el final
                error_time_range = "El inicio no puede ser mayor que el termino del short"
                return render_template("index.html", error_time_range=error_time_range)
            if a_seg(j) - a_seg(i) < 5: # Verifica que el short dure al menos 5 segundos
                error_time_range = "el Short debe durar al menos 5 segundos"
                return render_template("index.html", error_time_range=error_time_range)
            if a_seg(j) - a_seg(i) > 175: # Verifica que el short dure como maximo 2:55
                error_time_range = "el Short debe durar como maximo 2:55"
                return render_template("index.html", error_time_range=error_time_range)

        for i in titulos:
            if len(i or "") > 34: # Verifica que el titulo no sea mayor a 30 caracteres
                error_titulo = f"Titulo demasido largo: {i}, maximo 30 caracteres"
                return render_template("index.html", error_titulo=error_titulo)

        for p in potencia_whispers:
            if p not in ("tiny", "small", "medium"):
                error_titulo = "Potencia de subtítulos inválida"
                return render_template("index.html", error_titulo=error_titulo)

        if os.path.isdir(workdir): # borrón fresco: evita huérfanos de corridas anteriores
            shutil.rmtree(workdir)
        os.makedirs(workdir, exist_ok=True)

        if not descargar_video(youtube_url, workdir): # Descarga el video de youtube y lo guarda como entrada.mp4
            error_link_youtube = "No se pudo descargar el video, intenta con otro link"
            return render_template("index.html", error_link_youtube=error_link_youtube)

        for i in range(len(inicio_shorts)):
            titulo, inicio, final, potencia = titulos[i], inicio_shorts[i], final_shorts[i], potencia_whispers[i]
            short_params = ShortParams(i+1, titulo, inicio, final, potencia, workdir)
            short_params.crear_short()

        generados = [f"short_{i+1}.mp4" for i in range(len(inicio_shorts))]
        base = [f"{workdir}/entrada.mp4", f"{workdir}/salida.mp4",
                f"{workdir}/salida_corta.srt"] + glob.glob(f"{workdir}/titulo_*.ass")
        for f in base:
            if os.path.exists(f):
                os.remove(f)
        if generados:
            return render_template("index.html", generados=generados)
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    login_error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        validate_user = credential.test_credential(username, password)
        if validate_user:
            session.update({"flag_session": True})
            session["username"] = username
            return redirect(url_for("index"))
        else:
            login_error = "Error al iniciar sesion"
            return render_template("login.html", login_error=login_error)
    return render_template("login.html")

@app.route("/descargar/<filename>")
def descargar(filename):
    if not session.get("flag_session") or not session.get("username"):
        return redirect(url_for("login"))
    if not re.fullmatch(r"short_[1-5]\.mp4", filename or ""):
        return render_template("index.html",
            error_descarga="Nombre de archivo inválido"), 400
    path = f"{user_dir()}/{filename}"
    if not os.path.exists(path):
        return render_template("index.html",
            error_descarga="Ese short ya expiró o fue borrado, genera los shorts de nuevo"), 410
    return send_file(path, as_attachment=True)


if __name__ == "__main__":
    app.run(host=os.getenv("HOST", "127.0.0.1"),
            port=int(os.getenv("PORT", "8000")),
            debug=os.getenv("FLASK_DEBUG", "0") == "1")
    
