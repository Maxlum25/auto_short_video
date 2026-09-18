from flask import *
from dotenv import load_dotenv
import os
import requests
from tools import es_publico, a_seg
import credential


load_dotenv()

APP_SECRET_KEY=os.getenv("APP_SECRET_KEY")

app = Flask(__name__)
app.secret_key = APP_SECRET_KEY

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    error_link_youtube = None
    error_time_range = None
    error_titulo = None
    if not session.get("flag_session"):
        return redirect(url_for("login"))

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

        if not "www.youtube.com" in youtube_url: # Solo se permite links de youtube
            error_link_youtube = "Ingresa un link de youtube valido"
            return render_template("index.html", error_link_youtube=error_link_youtube)

        if not es_publico(youtube_url): # Verifica si el video es publico
            error_link_youtube = "El video no es público o no se puede acceder a él"
            return render_template("index.html", error_link_youtube=error_link_youtube)

        for i, j in zip(inicio_shorts, final_shorts):
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
            if len(i) > 34: # Verifica que el titulo no sea mayor a 30 caracteres
                error_titulo = f"Titulo demasido largo: {i}, maximo 30 caracteres"
                return render_template("index.html", error_titulo=error_titulo)

        for i in range(len(inicio_shorts)):
            pass


            

        


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
            return redirect(url_for("index"))
        else:
            login_error = "Error al iniciar sesion"
            return render_template("login.html", login_error=login_error)
    return render_template("login.html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
    
