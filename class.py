from yt_dlp import YoutubeDL
import subprocess
import shutil
from faster_whisper import WhisperModel
from tools import to_srt_time, a_lineas


class ShortParams:
    def __init__(self, number, titulo_short, inicio_short, final_short, potencia_whisper):
        self.number = number
        self.titulo_short = titulo_short
        self.inicio_short = inicio_short
        self.final_short = final_short
        self.potencia_whisper = potencia_whisper


    def crear_fragmento(self): # Corta el video de entrada.mp4 desde el tiempo de inicio hasta el tiempo final y lo guarda en salida.mp4
        ffmpeg = shutil.which("ffmpeg")

        subprocess.run([
            ffmpeg,"-y", "-ss", self.inicio_short, "-to", self.final_short, "-i", "multimedia/entrada.mp4", "-c", "copy", f"multimedia/salida.mp4"
        ], check = True)


    def extraer_substitulos_whisper(self): # Extrae los substitulos del short usando whisper y los guarda en un archivo .srt
        model = WhisperModel(self.potencia_whisper, device="cpu", compute_type="int8")
        segments, _ = model.transcribe(f"multimedia/salida.mp4", language="es", word_timestamps=True)
        n=1
        with open("salida_corta.srt", "w", encoding="utf-8") as f:
            for seg in segments:
                if not seg.words:
                    continue
                for texto, ini, fin in a_lineas(seg.words, 20):
                    f.write(f"{n}\n{to_srt_time(ini)} --> {to_srt_time(fin)}\n{texto}\n\n")
                    n += 1


    def crear_short(self):
        self.crear_fragmento()
        self.extraer_substitulos_whisper()
        ffmpeg = shutil.which("ffmpeg")

        base = "crop=trunc(ih*9/16/2)*2:ih"
        subs = (
            "subtitles=salida_corta.srt:"
            "force_style='FontSize=22,PrimaryColour=&H00FFFF,BackColour=&H80000000,BorderStyle=4,MarginV=60'"
        )
        if self.titulo_short and self.titulo_short.strip():
            titulo = self.titulo_short.replace("'", r"\'").replace(":", r"\:")
            draw = (
                f"drawtext=fontfile=/usr/share/fonts/TTF/DejaVuSans-Bold.ttf:text='{titulo}':"
                "fontsize=26:fontcolor=white:x=(w-text_w)/2:y=100:"
                "box=1:boxcolor=black@0.6:boxborderw=10"
            )
            vf = f"{base},{draw},{subs}"
        else:
            vf = f"{base},{subs}"
        subprocess.run([
            ffmpeg, "-y", "-i", "multimedia/salida.mp4",
            "-vf", vf,
            "-c:a", "copy", f"multimedia/short_{self.number}.mp4"
        ], check=True)