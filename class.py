from yt_dlp import YoutubeDL
import subprocess
import shutil

class ShortParams:
    def __init__(self, youtube_url, titulo_short, inicio_short, final_short, potencia_whisper):
        self.youtube_url = youtube_url
        self.titulo_short = titulo_short
        self.inicio_short = inicio_short
        self.final_short = final_short
        self.potencia_whisper = potencia_whisper

    def descargar_video(self):
        ydl_opts = {
                "format": "bestvideo[vcodec*=avc1][height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[vcodec*=avc1][height<=1080]+bestaudio/best[vcodec*=avc1][height<=1080][ext=mp4]/best[height<=1080][ext=mp4]",
                "outtmpl": "multimedia/entrada.%(ext)s",
                "merge_output_format": "mp4",
                "noplaylist": True,
                "overwrites": True,
            }
        url = self.youtube_url

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    def crear_fragmento(self):
        ffmpeg = shutil.which("ffmpeg")

        subprocess.run([
            ffmpeg, "-ss", self.inicio_short, "-to", self.final_short, "-i", "multimedia/entrada.mp4", "-c", "copy", "multimedia/salida.mp4"
        ], check = True)


    def extraer_substitulos_whisper(self):
        pass

    def crear_short(self):
        pass