#!/usr/bin/env python3
"""Convierte un tramo de un video (link o archivo) en un Short 9:16 con subtítulos palabra por palabra.

Ejemplos:
  python clipear.py "https://www.youtube.com/watch?v=XXXX" --inicio 1:02:10 --fin 1:02:45 \
      --gancho "NADIE ESPERABA ESTO" --credito "Clip: @streamer" --modo blur

  python clipear.py vod.mp4 --inicio 00:12:00 --fin 00:12:30 --modo split --facecam 1500,800,400,250

Usa solo contenido que tengas permiso de usar (campañas de clipping o autorización del creador).
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ANCHO, ALTO = 1080, 1920


def run(cmd, **kw):
    print("  $", " ".join(str(c) for c in cmd)[:200])
    subprocess.run(cmd, check=True, **kw)


def a_segundos(t):
    partes = [float(p) for p in str(t).split(":")]
    s = 0.0
    for p in partes:
        s = s * 60 + p
    return s


def obtener_tramo(fuente, inicio, fin, destino):
    """Descarga (yt-dlp) o recorta (ffmpeg) solo el tramo pedido."""
    if Path(fuente).exists():
        run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(inicio), "-to", str(fin), "-i", fuente,
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "aac", "-b:a", "192k", str(destino)])
        return
    if not shutil.which("yt-dlp") and not _modulo("yt_dlp"):
        sys.exit("Falta yt-dlp: pip install yt-dlp")
    run([sys.executable, "-m", "yt_dlp", "-f", "bv*[height<=1080]+ba/b[height<=1080]/b",
         "--download-sections", f"*{inicio}-{fin}", "--force-keyframes-at-cuts",
         "--merge-output-format", "mp4", "-o", str(destino), fuente])


def _modulo(nombre):
    try:
        __import__(nombre)
        return True
    except ImportError:
        return False


def transcribir(video, idioma, modelo):
    from faster_whisper import WhisperModel  # se importa aquí para que el resto funcione sin él

    m = WhisperModel(modelo, device="auto", compute_type="auto")
    segs, info = m.transcribe(str(video), language=idioma, word_timestamps=True, vad_filter=True)
    palabras = [{"w": w.word.strip(), "s": w.start, "e": w.end} for s in segs for w in (s.words or []) if w.word.strip()]
    print(f"  idioma detectado: {info.language}, {len(palabras)} palabras")
    return palabras


def t_ass(s):
    s = max(0.0, s)
    h, r = divmod(s, 3600)
    m, r = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{r:05.2f}"


def esc(txt):
    return txt.replace("\\", "").replace("{", "(").replace("}", ")").replace("\n", " ")


def generar_ass(palabras, gancho, credito, duracion, por_linea, salida, y_subs):
    cab = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {ANCHO}
PlayResY: {ALTO}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Subs,Arial,86,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,7,2,2,60,60,{y_subs},1
Style: Gancho,Arial,78,&H00FFFFFF,&H00FFFFFF,&H00000000,&HC0000000,-1,0,0,0,100,100,0,0,3,18,0,8,70,70,170,1
Style: Credito,Arial,38,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,3,0,8,40,40,60,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    if gancho:
        ev.append(f"Dialogue: 2,{t_ass(0)},{t_ass(min(3.0, duracion))},Gancho,,0,0,0,,{{\\fad(0,250)}}{esc(gancho.upper())}")
    if credito:
        ev.append(f"Dialogue: 1,{t_ass(0)},{t_ass(duracion)},Credito,,0,0,0,,{esc(credito)}")
    grupos = [palabras[i:i + por_linea] for i in range(0, len(palabras), por_linea)]
    for g in grupos:
        for j, w in enumerate(g):
            ini = w["s"]
            fin = g[j + 1]["s"] if j + 1 < len(g) else w["e"] + 0.15
            if fin <= ini:
                continue
            partes = []
            for k, x in enumerate(g):
                txt = esc(x["w"].upper())
                if k == j:  # palabra actual: amarilla y con "pop"
                    partes.append("{\\c&H00F2FF&\\fscx112\\fscy112}" + txt + "{\\c&HFFFFFF&\\fscx100\\fscy100}")
                else:
                    partes.append(txt)
            ev.append(f"Dialogue: 0,{t_ass(ini)},{t_ass(fin)},Subs,,0,0,0,,{' '.join(partes)}")
    Path(salida).write_text(cab + "\n".join(ev) + "\n", encoding="utf-8")


def filtro_video(modo, facecam, desplazamiento):
    if modo == "blur":  # video completo al centro y fondo desenfocado
        return (f"[0:v]split[a][b];[a]scale={ANCHO}:{ALTO}:force_original_aspect_ratio=increase,"
                f"crop={ANCHO}:{ALTO},boxblur=25:4,eq=brightness=-0.08[bg];"
                f"[b]scale={ANCHO}:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2[v0]")
    if modo == "fill":  # recorte vertical, desplazamiento 0=izq 0.5=centro 1=der
        return (f"[0:v]scale=-2:{ALTO},crop={ANCHO}:{ALTO}:(iw-{ANCHO})*{desplazamiento}:0[v0]")
    if modo == "split":  # facecam arriba, gameplay abajo
        x, y, w, h = facecam
        arriba = 640
        abajo = ALTO - arriba
        return (f"[0:v]split[f][g];[f]crop={w}:{h}:{x}:{y},scale={ANCHO}:{arriba}:force_original_aspect_ratio=increase,"
                f"crop={ANCHO}:{arriba}[fc];[g]scale=-2:{abajo},crop={ANCHO}:{abajo}:(iw-{ANCHO})*{desplazamiento}:0[gp];"
                f"[fc][gp]vstack[v0]")
    sys.exit(f"Modo desconocido: {modo}")


def duracion_de(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("fuente", help="Link (YouTube/Twitch/Kick...) o archivo local")
    ap.add_argument("--inicio", required=True, help="ej. 1:02:10")
    ap.add_argument("--fin", required=True, help="ej. 1:02:45")
    ap.add_argument("--salida", default=None, help="archivo .mp4 de salida")
    ap.add_argument("--modo", choices=["blur", "fill", "split"], default="blur")
    ap.add_argument("--facecam", default=None, help="x,y,ancho,alto de la facecam en el video original (modo split)")
    ap.add_argument("--desplazamiento", type=float, default=0.5, help="0=izquierda, 0.5=centro, 1=derecha (fill/split)")
    ap.add_argument("--gancho", default="", help="texto grande arriba durante los primeros 3 s")
    ap.add_argument("--credito", default="", help="crédito visible del creador original, ej. 'Clip: @streamer'")
    ap.add_argument("--idioma", default=None, help="es, en... (vacío = detectar)")
    ap.add_argument("--modelo", default="small", help="tiny/base/small/medium/large-v3 (más grande = más preciso y lento)")
    ap.add_argument("--palabras-por-linea", type=int, default=3)
    ap.add_argument("--altura-subs", type=int, default=520, help="distancia de los subtítulos al borde inferior (px)")
    ap.add_argument("--sin-subtitulos", action="store_true")
    ap.add_argument("--palabras-json", default=None, help="usar una transcripción ya hecha (lista de {w,s,e})")
    a = ap.parse_args()

    if a.modo == "split" and not a.facecam:
        sys.exit("El modo split necesita --facecam x,y,ancho,alto")
    if a_segundos(a.fin) <= a_segundos(a.inicio):
        sys.exit("--fin debe ser mayor que --inicio")
    facecam = [int(v) for v in a.facecam.split(",")] if a.facecam else None
    salida = Path(a.salida or f"short_{a.inicio.replace(':', '-')}.mp4").resolve()

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        tramo = tmp / "tramo.mp4"
        print("1/4 Obteniendo el tramo…")
        obtener_tramo(a.fuente, a.inicio, a.fin, tramo)
        dur = duracion_de(tramo)

        palabras = []
        if a.palabras_json:
            palabras = json.loads(Path(a.palabras_json).read_text(encoding="utf-8"))
        elif not a.sin_subtitulos:
            print("2/4 Transcribiendo (faster-whisper)…")
            palabras = transcribir(tramo, a.idioma, a.modelo)
            (salida.with_suffix(".palabras.json")).write_text(json.dumps(palabras, ensure_ascii=False, indent=1), encoding="utf-8")

        print("3/4 Generando subtítulos…")
        generar_ass(palabras, a.gancho, a.credito, dur, a.palabras_por_linea, tmp / "subs.ass", a.altura_subs)

        print("4/4 Renderizando 1080x1920…")
        fc = filtro_video(a.modo, facecam, a.desplazamiento) + ";[v0]ass=subs.ass,format=yuv420p[v]"
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tramo), "-filter_complex", fc,
             "-map", "[v]", "-map", "0:a?", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
             "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-r", "30",
             "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(salida)], cwd=tmp)
    print(f"Listo: {salida}")


if __name__ == "__main__":
    main()
