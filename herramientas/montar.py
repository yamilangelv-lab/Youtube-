#!/usr/bin/env python3
"""Monta un Short completo (1080x1920) a partir de un plan JSON con varios clips.

Para cada segmento: recorte, reframe 9:16 con fondo desenfocado, zoom "punch" opcional,
cámara lenta opcional, imagen congelada opcional y etiqueta con el crédito del creador.
Después une todo y añade tu narración (bajando el audio original cuando hablas), música de fondo,
subtítulos palabra por palabra, el gancho de los primeros segundos y audio a -14 LUFS.

Uso:
  python montar.py plan.json
  python montar.py plan.json --palabras-json correcciones.json   # re-render sin transcribir

Formato del plan: ver ../primer-video/plan.json
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from clipear import ANCHO, ALTO, a_segundos, duracion_de, esc, generar_ass, run, t_ass, transcribir  # noqa: E402

FPS = 30
ALTO_FG = 608  # alto del video 16:9 escalado a 1080 de ancho


def render_segmento(seg, base, salida):
    src = str((base / seg["archivo"]).resolve())
    if not Path(src).exists():
        sys.exit(f"No existe el clip: {src}")
    lento = float(seg.get("lento", 1.0))  # 0.5 = mitad de velocidad
    zoom_en = seg.get("zoom_en")  # segundos desde el inicio del segmento (ya en cámara lenta)
    zoom = float(seg.get("zoom", 1.25))

    if "congelar" in seg:  # imagen congelada de N segundos
        t, dur = a_segundos(seg["congelar"]), float(seg.get("duracion", 2.0))
        entrada = ["-ss", str(t), "-i", src, "-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=48000:cl=stereo"]
        pre_v = f"[0:v]trim=end_frame=1,loop=loop=-1:size=1,trim=duration={dur},setpts=N/{FPS}/TB,fps={FPS}"
        audio = "[1:a]anull[a]"
    else:
        ini, fin = a_segundos(seg["inicio"]), a_segundos(seg["fin"])
        entrada = ["-ss", str(ini), "-to", str(fin), "-i", src]
        pre_v = f"[0:v]setpts={1 / lento}*PTS,fps={FPS}"
        audio = f"[0:a]atempo={max(0.5, lento)},aresample=48000[a]" if lento != 1.0 else "[0:a]aresample=48000[a]"

    if zoom_en is not None:
        z = f"if(gte(in_time,{zoom_en}),{zoom},1)"
        fg = (f"scale={ANCHO}:{ALTO_FG}:force_original_aspect_ratio=increase,crop={ANCHO}:{ALTO_FG},"
              f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={ANCHO}x{ALTO_FG}:fps={FPS}")
    else:
        fg = f"scale={ANCHO}:-2"
    fc = (f"{pre_v},split[a][b];[a]scale={ANCHO}:{ALTO}:force_original_aspect_ratio=increase,crop={ANCHO}:{ALTO},"
          f"boxblur=25:4,eq=brightness=-0.08[bg];[b]{fg}[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p,"
          f"setsar=1[v];{audio}")
    run(["ffmpeg", "-y", "-loglevel", "error", *entrada, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-r", str(FPS),
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", str(salida)])
    return duracion_de(salida)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plan")
    ap.add_argument("--palabras-json", default=None, help="transcripción ya corregida (lista de {w,s,e})")
    a = ap.parse_args()

    plan_path = Path(a.plan).resolve()
    base = plan_path.parent
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    salida = (base / plan.get("salida", "final.mp4")).resolve()

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        partes, etiquetas, t = [], [], 0.0
        for i, seg in enumerate(plan["segmentos"], 1):
            print(f"Segmento {i}/{len(plan['segmentos'])}: {seg.get('nota', seg['archivo'])}")
            p = tmp / f"seg{i:02d}.mp4"
            d = render_segmento(seg, base, p)
            if seg.get("etiqueta"):
                etiquetas.append((t, t + d, seg["etiqueta"]))
            if seg.get("texto"):
                etiquetas.append((t, t + d, "§" + seg["texto"]))
            partes.append(p)
            t += d
        (tmp / "lista.txt").write_text("".join(f"file '{p}'\n" for p in partes))
        unido = tmp / "unido.mp4"
        run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(tmp / "lista.txt"),
             "-c", "copy", str(unido)])
        dur = duracion_de(unido)

        narr = plan.get("narracion")
        narr = (base / narr).resolve() if narr else None
        if narr and not narr.exists():
            print(f"Aviso: no encontré la narración {narr}; sigo sin ella.")
            narr = None
        musica = plan.get("musica")
        musica = (base / musica).resolve() if musica else None
        if musica and not musica.exists():
            print(f"Aviso: no encontré la música {musica}; sigo sin ella.")
            musica = None

        # subtítulos: de la narración si existe (audio limpio), si no del audio de los clips
        if a.palabras_json:
            palabras = json.loads(Path(a.palabras_json).read_text(encoding="utf-8"))
        elif plan.get("subtitulos", True):
            print("Transcribiendo para subtítulos…")
            palabras = transcribir(narr or unido, plan.get("idioma", "es"), plan.get("modelo", "small"))
            salida.with_suffix(".palabras.json").write_text(json.dumps(palabras, ensure_ascii=False, indent=1),
                                                            encoding="utf-8")
        else:
            palabras = []
        ass = tmp / "subs.ass"
        generar_ass(palabras, plan.get("gancho", ""), "", dur, plan.get("palabras_por_linea", 3), ass,
                    plan.get("altura_subs", 520))
        extra = []
        for ini, fin, txt in etiquetas:
            if txt.startswith("§"):  # texto grande arriba (ej. "#3")
                extra.append(f"Dialogue: 2,{t_ass(max(ini, 3.0) if ini < 3 else ini)},{t_ass(fin)},Gancho,,0,0,0,,{esc(txt[1:].upper())}")
            else:  # crédito del creador
                extra.append(f"Dialogue: 1,{t_ass(ini)},{t_ass(fin)},Credito,,0,0,0,,{esc(txt)}")
        with open(ass, "a", encoding="utf-8") as fh:
            fh.write("\n".join(extra) + "\n")

        # mezcla de audio: clips + narración (con ducking) + música
        entradas = ["-i", str(unido)]
        filtros = ["[0:a]volume=1.0[orig]"]
        actual = "orig"
        n = 1
        if narr:
            entradas += ["-i", str(narr)]
            filtros += [f"[{n}:a]aresample=48000,volume=1.6,asplit=2[n1][n2]",
                        f"[{actual}][n1]sidechaincompress=threshold=0.02:ratio=10:attack=15:release=350[duck]",
                        "[duck][n2]amix=inputs=2:duration=first:normalize=0[mix1]"]
            actual, n = "mix1", n + 1
        if musica:
            entradas += ["-stream_loop", "-1", "-i", str(musica)]
            filtros += [f"[{n}:a]aresample=48000,volume={plan.get('volumen_musica', 0.10)}[mus]",
                        f"[{actual}][mus]amix=inputs=2:duration=first:normalize=0[mix2]"]
            actual, n = "mix2", n + 1
        filtros.append(f"[{actual}]loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
        filtros.append("[0:v]ass=subs.ass,format=yuv420p[vout]")
        print("Render final…")
        run(["ffmpeg", "-y", "-loglevel", "error", *entradas, "-filter_complex", ";".join(filtros),
             "-map", "[vout]", "-map", "[aout]", "-t", str(dur),
             "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-r", str(FPS),
             "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(salida)], cwd=tmp)
    print(f"Listo: {salida}  ({dur:.1f} s)")


if __name__ == "__main__":
    main()
