from flask import (
    Flask,
    render_template,
    request,
    send_from_directory,
    redirect,
    url_for,send_file,
)
import requests
import calendar, os
from datetime import datetime
from yt_dlp import YoutubeDL

app = Flask(__name__)
app.secret_key = "supersecretkey"


@app.context_processor
def inject_globals():
    return {"hoy": datetime.today()}


@app.route("/", methods=["GET", "POST"])
def calendario():
    hoy = datetime.today()
    meses = [
        {
            "nombre": calendar.month_name[m],
            "mes_numero": m,
            "semanas": calendar.Calendar().monthdayscalendar(hoy.year, m),
        }
        for m in range(hoy.month, 13)
    ]

    edad = ""
    signo = ""
    faltan = None
    descuento = None

    signos = [
        ("Capricornio", (12, 22), (1, 19)),
        ("Acuario", (1, 20), (2, 18)),
        ("Piscis", (2, 19), (3, 20)),
        ("Aries", (3, 21), (4, 19)),
        ("Tauro", (4, 20), (5, 20)),
        ("Géminis", (5, 21), (6, 20)),
        ("Cáncer", (6, 21), (7, 22)),
        ("Leo", (7, 23), (8, 22)),
        ("Virgo", (8, 23), (9, 22)),
        ("Libra", (9, 23), (10, 22)),
        ("Escorpio", (10, 23), (11, 21)),
        ("Sagitario", (11, 22), (12, 21)),
    ]

    if request.method == "POST":
        try:
            fn = datetime.strptime(request.form.get("fecha_nacimiento", ""), "%d/%m/%Y")
            edad = hoy.year - fn.year - ((hoy.month, hoy.day) < (fn.month, fn.day))
            cumple = fn.replace(year=hoy.year)
            if cumple < hoy:
                cumple = cumple.replace(year=hoy.year + 1)
            faltan = (cumple - hoy).days
            signo = next(
                s
                for s, (m1, d1), (m2, d2) in signos
                if (fn.month == m1 and fn.day >= d1)
                or (fn.month == m2 and fn.day <= d2)
            )
        except:
            edad = "Ingrese fecha correcta: dia/mes/año"

        try:
            monto = float(request.form.get("monto", 0))
            porcentaje = float(request.form.get("porcentaje", 0))
            descuento = monto - (monto * porcentaje / 100)
        except:
            descuento = "Error en los datos ingresados"

    # recoger mensajes de la descarga si existen
    msg = request.args.get("msg", "")
    msg_type = request.args.get("msg_type", "")

    return render_template(
        "app.html",
        msg=msg,
        msg_type=msg_type,
        hoy=hoy,
        meses=meses,
        edad=edad,
        signo=signo,
        faltan=faltan,
        descuento=descuento,
    )


############################################################################
# Carpeta base donde están los archivos que vas a descargar
#BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
# Crear la carpeta si no existe
#os.makedirs(BASE_DIR, exist_ok=True)

#BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#output1 = os.path.join(BASE_DIR, "downloads")
#os.makedirs(output1, exist_ok=True)

# output1 = "D:/dev/PYTHON/APPS_ANDRES/descargas_youtube/"
#output1 = "/storage/emulated/0/downloads2"
#output1 = "/sdcard/Download/okdes"
#output1 = "/sdcard/okdes"
#os.makedirs(output1, exist_ok=True)

#BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # carpeta donde está app.py
#DOWNLOADS_DIR = os.path.join(BASE_DIR, "downloads2")
#os.makedirs(DOWNLOADS_DIR, exist_ok=True)
#output1 = DOWNLOADS_DIR
#print(output1)

#output1 = "/opt/render/project/src/downloads2"
BASE_DIR = "/opt/render/project/src/downloads2"

#import tempfile, os
# Carpeta temporal para descargas # Directorio temporal del sistema (válido en la mayoría de hostings)
#BASE_DIR = os.path.join(tempfile.gettempdir(), "downloads")
#os.makedirs(BASE_DIR, exist_ok=True)

#ruta = os.path.join(BASE_DIR, "cookies.txt")
#ruta = os.path.join(DOWNLOADS_DIR, "chromewebstore.google.com_cookies.txt")

#@app.route("/descargar", methods=["GET", "POST"])
@app.route("/descargar", methods=["POST"])
def descargar():
    # download_url = None
    msg = ""
    msg_type = ""
    if request.method == "POST":
        url = request.form.get("url").split("?")[0]  # Limpiar la URL
        # url = request.form.get("url")
        download_type = request.form.get("download_type")
        # extension = 'mp3' if download_type == 'audio' else 'mp4'
        extension = "m4a" if download_type == "audio" else "webm"
        counter = 1
        while True:
            #filename = os.path.join(output1, f"{counter}.{extension}")
            #output_file = os.path.join(DOWNLOADS_DIR, f"{counter}.{extension}")
            filename = os.path.join(BASE_DIR, f"{counter}.{extension}")
            if not os.path.exists(filename):
                break
            counter += 1
        format_flag = "bestaudio" if download_type == "audio" else "best"
        ydl_opts = {
            "format": format_flag,
            "outtmpl": filename,
            "quiet": True,
            "no_warnings": True,
            #"cookiefile": ruta,
            #'noplaylist': True,
            # evitar caracteres raros en nombres
            #'restrictfilenames': True,
            #'cachedir': False,
            #'postprocessors': [
            # {
            #    'key': 'FFmpegExtractAudio',
            #    'preferredcodec': 'mp3',
            #    'preferredquality': '192',
            # }
            # ],
        }
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            # 👉 Redirige directo a la descarga del archivo
            return redirect(url_for('serve_download',
            #return redirect(url_for("calendario",
                                    msg=f"{download_type.capitalize()} descargado con éxito como {os.path.basename(filename)}.",
                                    msg_type="success",
                                    filename=os.path.basename(filename)))

        except Exception as e:
            #msg = f"Error al descargar el archivo: {str(e)}"
            msg = f"Error al descargar el archivo: Url no valido"
            return redirect(url_for("calendario", msg=msg, msg_type="error"))
            
'''from flask import send_file
from io import BytesIO
import requests
import tempfile

@app.route("/descargar", methods=["POST"])
def descargar():
    url = request.form.get("url")
    download_type = request.form.get("download_type")
    format_flag = "bestaudio" if download_type == "audio" else "best"

    ydl_opts = {"format": format_flag}

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            stream_url = info["url"]

        # Descargar el stream directamente
        r = requests.get(stream_url, stream=True)
        buffer = BytesIO(r.content)

        # Nombre del archivo
        ext = "m4a" if download_type == "audio" else "webm"
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"video.{ext}",
            mimetype="audio/m4a" if ext == "m4a" else "video/webm"
        )

    except Exception as e:
        msg = f"Error al descargar: {str(e)}"
        return redirect(url_for("calendario", msg=msg, msg_type="error"))'''


## Si quieres habilitar descarga directa de archivos:
@app.route('/downloads/<path:filename>')
#@app.route("/download/<path:output_file>")
def serve_download(filename):
    filename = os.path.basename(filename)
    #file_path = os.path.join(BASE_DIR, filename)
    #return send_from_directory(file_path, filename, as_attachment=True)
    #return send_from_directory("downloads", output_file, as_attachment=True)
    return send_from_directory(BASE_DIR, filename, as_attachment=True)

#Alternativa más simple con send_file
#Si quieres evitar confusiones con rutas, puedes usar send_file directamente:
'''from flask import send_file
import os
@app.route('/downloads/<path:filename>')
def serve_download(filename):
    filename = os.path.basename(filename)
    file_path = os.path.join(BASE_DIR, filename)
    return send_file(file_path, as_attachment=True)'''
#Esto funciona exactamente igual y es más directo.
#Ideal cuando tu archivo ya está en el servidor y no quieres preocuparte de la carpeta.

if __name__ == "__main__":
    # app.run(debug=True)
    port = int(os.environ.get("PORT", 5002))
    app.run(host="0.0.0.0", port=port, debug=True)

# {% if msg %}
#        <div class="alert {{ msg_type }}">
#            {{ msg }}
#        </div>
#        {% endif %}
