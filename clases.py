import os
import subprocess
import shutil
from faster_whisper import WhisperModel
from tools import to_srt_time, a_lineas, a_seg

def _ffmpeg():
    return os.getenv("FFMPEG") or shutil.which("ffmpeg")


_MODELOS = {}

def _modelo(potencia):
    if potencia not in _MODELOS:
        _MODELOS[potencia] = WhisperModel(potencia, device="cpu", compute_type="int8")
    return _MODELOS[potencia]


def _ass_time(total_s: float) -> str:
    total_s = max(0.0, float(total_s))
    h = int(total_s // 3600)
    m = int((total_s % 3600) // 60)
    s = int(total_s % 60)
    cs = int(round((total_s - int(total_s)) * 100))
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def _ass_escape(t: str) -> str:
    return t.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}").replace("\n", " ")


class ShortParams:
    def __init__(self, number, titulo_short, inicio_short, final_short, potencia_whisper, workdir="multimedia"):
        self.number = number
        self.titulo_short = titulo_short
        self.inicio_short = inicio_short
        self.final_short = final_short
        self.potencia_whisper = potencia_whisper
        self.workdir = workdir


    def crear_fragmento(self): # Corta el video de entrada.mp4 desde el tiempo de inicio hasta el tiempo final y lo guarda en salida.mp4
        ffmpeg = _ffmpeg()

        subprocess.run([
            ffmpeg,"-y", "-ss", self.inicio_short, "-to", self.final_short, "-i", f"{self.workdir}/entrada.mp4", "-c", "copy", f"{self.workdir}/salida.mp4"
        ], check = True)


    def extraer_substitulos_whisper(self): # Extrae los substitulos del short usando whisper y los guarda en un archivo .srt
        model = _modelo(self.potencia_whisper)
        segments, _ = model.transcribe(f"{self.workdir}/salida.mp4", language="es", word_timestamps=True)
        n=1
        with open(f"{self.workdir}/salida_corta.srt", "w", encoding="utf-8") as f:
            for seg in segments:
                if not seg.words:
                    continue
                for texto, ini, fin in a_lineas(seg.words, 20):
                    f.write(f"{n}\n{to_srt_time(ini)} --> {to_srt_time(fin)}\n{texto}\n\n")
                    n += 1


    def crear_short(self):
        self.crear_fragmento()
        self.extraer_substitulos_whisper()
        ffmpeg = _ffmpeg()

        base = "crop=trunc(ih*9/16/2)*2:ih"
        style = "FontSize=18,PrimaryColour=&H00FFFF,BackColour=&H80000000,BorderStyle=4,MarginV=80,MarginL=40,MarginR=40"
        srt = f"{self.workdir}/salida_corta.srt"
        subs = f"subtitles={srt}:force_style='{style}'"
        if self.titulo_short and self.titulo_short.strip():
            dur = a_seg(self.final_short) - a_seg(self.inicio_short)
            ass_path = f"{self.workdir}/titulo_{self.number}.ass"
            with open(ass_path, "w", encoding="utf-8") as f:
                f.write("[Script Info]\nScriptType: v4.00+\nPlayResX: 720\nPlayResY: 1280\n"
                        "ScaledBorderAndShadow: yes\n\n[V4+ Styles]\n"
                        "Format: Name, Fontname, Fontsize, PrimaryColour, BackColour, Bold, "
                        "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
                        "Style: Title,DejaVu Sans,60,&H00FFFFFF,&H99000000,1,4,1,0,8,10,10,100,1\n\n"
                        "[Events]\nFormat: Layer, Start, End, Style, Text\n"
                        f"Dialogue: 0,0:00:00.00,{_ass_time(dur)},Title,{_ass_escape(self.titulo_short.strip())}\n")
            graph = f"{base},{subs},subtitles={ass_path}"
        else:
            graph = f"{base},{subs}"

        subprocess.run([
            ffmpeg, "-y", "-i", f"{self.workdir}/salida.mp4",
            "-vf", graph,
            "-c:a", "copy", f"{self.workdir}/short_{self.number}.mp4"
        ], check=True)