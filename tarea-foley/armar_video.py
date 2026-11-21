#!/usr/bin/env python3
"""
Arma el video final de la tarea de foley:

  Portada -> "SONIDO ORIGINAL" -> escena con su audio
          -> "SONIDO RECREADO" -> misma escena con los sonidos grabados por el grupo
          -> (opcional) detrás de cámaras -> créditos

Uso:
    python3 armar_video.py proyecto.json

Necesita ffmpeg instalado. Todo se configura en proyecto.json (ver proyecto_ejemplo.json).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

W, H, FPS = 1920, 1080, 30
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
VENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(FPS)]
AENC = ["-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]


def seg(t):
    """'1:05.5' -> 65.5 ; 12 -> 12.0"""
    if isinstance(t, (int, float)):
        return float(t)
    partes = [float(p) for p in str(t).strip().split(":")]
    s = 0.0
    for p in partes:
        s = s * 60 + p
    return s


def run(cmd):
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if r.returncode != 0:
        print("\n".join(r.stderr.splitlines()[-25:]))
        sys.exit("ffmpeg falló con el comando de arriba.")


def duracion(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nw=1:nk=1", path], capture_output=True, text=True)
    return float(r.stdout.strip())


def escribir_txt(tmp, nombre, texto):
    p = os.path.join(tmp, nombre)
    with open(p, "w", encoding="utf-8") as f:
        f.write(texto)
    return p


def escala():
    return (f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
            f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fps={FPS}")


def tarjeta(tmp, nombre, titulo, subtitulo, dur):
    """Pantalla negra con texto y audio en silencio."""
    t1 = escribir_txt(tmp, nombre + "_t1.txt", titulo)
    filtros = [f"drawtext=fontfile={FONT}:textfile={t1}:fontcolor=white:fontsize=84:"
               f"x=(w-text_w)/2:y=(h-text_h)/2-60"]
    if subtitulo:
        # cada línea centrada por separado
        for i, linea in enumerate(subtitulo.split("\n")):
            if not linea.strip():
                continue
            t2 = escribir_txt(tmp, f"{nombre}_l{i}.txt", linea)
            filtros.append(f"drawtext=fontfile={FONT_REG}:textfile={t2}:fontcolor=0xCCCCCC:fontsize=40:"
                           f"x=(w-text_w)/2:y=(h/2)+40+{i * 58}")
    filtros.append(f"fade=t=in:st=0:d=0.4,fade=t=out:st={dur - 0.4}:d=0.4")
    out = os.path.join(tmp, nombre + ".mp4")
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=black:s={W}x{H}:r={FPS}:d={dur}",
         "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", str(dur),
         "-vf", ",".join(filtros), *VENC, *AENC, "-shortest", out])
    return out


def rotulo(tmp, nombre, texto):
    """Cartelito fijo arriba a la izquierda (ORIGINAL / RECREADO)."""
    p = escribir_txt(tmp, nombre, texto)
    return (f"drawtext=fontfile={FONT}:textfile={p}:fontcolor=white:fontsize=38:"
            f"box=1:boxcolor=black@0.55:boxborderw=18:x=40:y=40")


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    cfg_path = os.path.abspath(sys.argv[1])
    base = os.path.dirname(cfg_path)
    with open(cfg_path, encoding="utf-8") as f:
        cfg = json.load(f)

    def ruta(p):
        return p if os.path.isabs(p) else os.path.join(base, p)

    clip = ruta(cfg["clip"])
    ini = seg(cfg.get("inicio", 0))
    fin = seg(cfg["fin"]) if "fin" in cfg else duracion(clip)
    dur = fin - ini
    if not 1 <= dur <= 120:
        sys.exit(f"El tramo dura {dur:.1f} s; revisa 'inicio' y 'fin'.")
    if not 30 <= dur <= 60:
        print(f"Aviso: el tramo dura {dur:.1f} s y la tarea pide entre 30 y 60 s.")

    salida = ruta(cfg.get("salida", "video_final.mp4"))
    pelicula = cfg.get("pelicula", "")
    tmp = tempfile.mkdtemp(prefix="foley_")
    partes = []

    # 1. Portada
    integrantes = "\n".join(cfg.get("integrantes", []))
    partes.append(tarjeta(tmp, "00_portada", cfg.get("titulo", "Recreación de Foley"),
                          (pelicula + ("\n\n" + integrantes if integrantes else "")).strip(), 5))

    # 2. Original
    partes.append(tarjeta(tmp, "01_card_orig", "SONIDO ORIGINAL", pelicula, 2.5))
    orig = os.path.join(tmp, "02_original.mp4")
    run(["ffmpeg", "-y", "-ss", str(ini), "-t", str(dur), "-i", clip,
         "-vf", escala() + "," + rotulo(tmp, "rot_o.txt", "SONIDO ORIGINAL"),
         *VENC, *AENC, orig])
    partes.append(orig)

    # 3. Recreado
    partes.append(tarjeta(tmp, "03_card_rec", "SONIDO RECREADO",
                          "Todos los sonidos fueron grabados por el grupo\ncon objetos cotidianos", 3))

    sonidos = cfg.get("sonidos", [])
    amb = cfg.get("ambiente")
    entradas = ["-ss", str(ini), "-t", str(dur), "-i", clip]
    fc = []
    mezclas = []
    n = 1
    if amb:
        entradas += ["-stream_loop", "-1", "-i", ruta(amb["archivo"])]
        v = float(amb.get("volumen", 0.3))
        fc.append(f"[{n}:a]aformat=sample_rates=48000:channel_layouts=stereo,"
                  f"atrim=0:{dur},afade=t=in:d=0.8,afade=t=out:st={dur - 1}:d=1,volume={v}[a{n}]")
        mezclas.append(f"[a{n}]")
        n += 1
    etiquetas_vf = []
    for i, s in enumerate(sonidos):
        entradas += ["-i", ruta(s["archivo"])]
        t = seg(s["tiempo"])
        v = float(s.get("volumen", 1.0))
        cadena = f"[{n}:a]aformat=sample_rates=48000:channel_layouts=stereo"
        if s.get("auto_recorte", True):
            # quita el silencio del principio de la grabación
            cadena += ",silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.02"
        if "recorte_inicio" in s:
            cadena += f",atrim=start={seg(s['recorte_inicio'])},asetpts=PTS-STARTPTS"
        if "duracion" in s:
            cadena += f",atrim=0:{seg(s['duracion'])},afade=t=out:st={max(seg(s['duracion']) - 0.05, 0)}:d=0.05"
        ms = int(round(t * 1000))
        cadena += f",volume={v},adelay={ms}|{ms}[a{n}]"
        fc.append(cadena)
        mezclas.append(f"[a{n}]")
        n += 1
        if s.get("etiqueta"):
            p = escribir_txt(tmp, f"et_{i}.txt", s["etiqueta"])
            dur_et = float(s.get("mostrar_etiqueta", 2.5))
            etiquetas_vf.append(
                f"drawtext=fontfile={FONT}:textfile={p}:fontcolor=white:fontsize=44:"
                f"box=1:boxcolor=0x1E1E1E@0.75:boxborderw=20:x=(w-text_w)/2:y=h-170:"
                f"enable='between(t,{t:.3f},{t + dur_et:.3f})'")
    if not mezclas:
        sys.exit("No hay sonidos en 'sonidos' ni 'ambiente'.")
    fc.append("".join(mezclas) + f"amix=inputs={len(mezclas)}:normalize=0:duration=longest,"
              f"apad,atrim=0:{dur},alimiter=limit=0.9[aout]")
    vf = escala() + "," + rotulo(tmp, "rot_r.txt", "SONIDO RECREADO")
    if etiquetas_vf and cfg.get("mostrar_etiquetas", True):
        vf += "," + ",".join(etiquetas_vf)
    fc.append(f"[0:v]{vf}[vout]")
    rec = os.path.join(tmp, "04_recreado.mp4")
    run(["ffmpeg", "-y", *entradas, "-filter_complex", ";".join(fc),
         "-map", "[vout]", "-map", "[aout]", "-t", str(dur), *VENC, *AENC, rec])
    partes.append(rec)

    # 4. Detrás de cámaras (opcional)
    if cfg.get("detras_de_camaras"):
        partes.append(tarjeta(tmp, "06_card_bts", "DETRÁS DE CÁMARAS", "Así hicimos los sonidos", 2.5))
        bts_in = ruta(cfg["detras_de_camaras"])
        bts = os.path.join(tmp, "07_bts.mp4")
        tiene_audio = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
             "-of", "csv=p=0", bts_in], capture_output=True, text=True).stdout.strip() != ""
        if tiene_audio:
            run(["ffmpeg", "-y", "-i", bts_in, "-vf", escala(), *VENC, *AENC, bts])
        else:
            run(["ffmpeg", "-y", "-i", bts_in, "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                 "-vf", escala(), "-map", "0:v", "-map", "1:a", "-shortest", *VENC, *AENC, bts])
        partes.append(bts)

    # 6. Créditos
    creditos = cfg.get("creditos",
                       f"Escena: {pelicula}\nTodos los derechos a sus respectivos dueños.\n"
                       f"Uso exclusivamente educativo.")
    partes.append(tarjeta(tmp, "08_creditos", "Gracias", creditos, 5))

    lista = escribir_txt(tmp, "lista.txt", "".join(f"file '{p}'\n" for p in partes))
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lista, "-c", "copy",
         "-movflags", "+faststart", salida])
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"Listo: {salida}  ({duracion(salida):.1f} s)")


if __name__ == "__main__":
    main()
