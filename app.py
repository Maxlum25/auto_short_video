from flask import *
from dotenv import load_dotenv
import os
import requests

load_dotenv()

APP_SECRET_KEY=os.getenv("APP_SECRET_KEY")

app = Flask(__name__)
app.secret_key = APP_SECRET_KEY

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    if not session.get("flag_session"):
        return redirect(url_for("login"))

    if request.method == "POST":
        youtube_url = request.form.get("youtube_url")
        titulo_short_1, titulo_short_2, titulo_short_3, titulo_short_4, titulo_short_5 = request.form.get("titulo_short_1"), request.form.get("titulo_short_2"), request.form.get("titulo_short_3"), request.form.get("titulo_short_4"), request.form.get("titulo_short_5")
        inicio_short_1, inicio_short_2, inicio_short_3, inicio_short_4, inicio_short_5 = request.form.get("inicio_short_1"), request.form.get("inicio_short_2"), request.form.get("inicio_short_3"), request.form.get("inicio_short_4"), request.form.get("inicio_short_5")
        final_short_1, final_short_2, final_short_3, final_short_4, final_short_5 = request.form.get("final_short_1"), request.form.get("final_short_2"), request.form.get("final_short_3"), request.form.get("final_short_4"), request.form.get("final_short_5")
        
        # continua con la potencia del whisper, se deberia elegir para cada short??..



    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    login_error = None
    if request.method == "POST":
        username = request.form("username")
        password = request.form("password")
        validate_user = credential.test_credential(username, password)
        if validate_user:
            session.update("flag_session": True)
            return redirect(url_for("index"))
        else:
            login_error = "Error al iniciar sesion"
            return render_template("login.html", login_error=login_error)
    return render_template("login.html")

    
    
