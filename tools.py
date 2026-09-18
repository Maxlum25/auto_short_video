import yt_dlp

def es_publico(url: str) -> bool: # Verifica si el video de youtube es publico o privado, devuelve True si es publico y False si es privado
    opts = {"quiet": True, "no_warnings": True, "skip_download": True}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return True
    except Exception:
        return False

def a_seg(t: str): # Convierte un tiempo en formato hh:mm:ss a segundos
    h,m,s = map(int, t.split(':'))
    return h*3600 + m*60 + s

def to_srt_time(s): # Convierte un tiempo en segundos a formato hh:mm:ss,ms
    h, r = divmod(int(s*1000), 3600000)
    m, r = divmod(r, 60000)
    sec, ms = divmod(r, 1000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"

def a_lineas(words, max_width=20): # Divide una lista de palabras en líneas de un ancho máximo
    lineas, cur, cur_w = [], "", []
    for w in words:
        txt = w.word.strip()
        t = (cur + " " + txt).strip()
        if len(t) <= max_width:
            cur, cur_w = t, cur_w + [w]
        else:
            lineas.append((cur, cur_w[0].start, cur_w[-1].end))
            cur, cur_w = txt, [w]
    if cur:
        lineas.append((cur, cur_w[0].start, cur_w[-1].end))
    return lineas

def descargar_video(url): # Descarga el video de youtube en formato mp4 y lo guarda en la carpeta multimedia con el nombre entrada.mp4
    ydl_opts = {
            "format": "bestvideo[vcodec*=avc1][height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[vcodec*=avc1][height<=1080]+bestaudio/best[vcodec*=avc1][height<=1080][ext=mp4]/best[height<=1080][ext=mp4]",
            "outtmpl": "multimedia/entrada.%(ext)s",
            "merge_output_format": "mp4",
            "noplaylist": True,
            "overwrites": True,
        }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            return True
    except Exception as e:
        print(f"Error al descargar el video: {e}")
        return False


if __name__ == "__main__":
    url = ""
    if es_publico(url):
        print("El video es público.")
    else:
        print("El video no es público o no se puede acceder a él.")