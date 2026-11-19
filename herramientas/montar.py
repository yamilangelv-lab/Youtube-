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

    # clips que ya son verticales (p. ej. Shorts de streamers): ocupan toda la pantalla
    dims = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                           "stream=width,height", "-of", "csv=p=0", src], capture_output=True, text=True).stdout
    w_src, h_src = (int(x) for x in dims.strip().split(",")[:2])
    alto_fg = ALTO if h_src > w_src else ALTO_FG
    zy = float(seg.get("zoom_y", 0.5))  # centro vertical del zoom (0 = arriba, 0.5 = centro)
    if zoom_en is not None:
        z = f"if(gte(in_time,{zoom_en}),{zoom},1)"
        fg = (f"scale={ANCHO}:{alto_fg}:force_original_aspect_ratio=increase,crop={ANCHO}:{alto_fg},"
              f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='max(0,min(ih-ih/zoom,ih*{zy}-ih/zoom/2))':"
              f"d=1:s={ANCHO}x{alto_fg}:fps={FPS}")
    else:
        fg = (f"scale={ANCHO}:{alto_fg}:force_original_aspect_ratio=increase,crop={ANCHO}:{alto_fg}"
              if h_src > w_src else f"scale={ANCHO}:-2")
    if seg.get("efecto") == "oscuro":
        fg += ",eq=brightness=-0.3:saturation=0.7"
    fc = (f"{pre_v},split[a][b];[a]scale={ANCHO}:{ALTO}:force_original_aspect_ratio=increase,crop={ANCHO}:{ALTO},"
          f"boxblur=25:4,eq=brightness=-0.08[bg];[b]{fg}[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p,"
          f"setsar=1[v];{audio}")
    run(["ffmpeg", "-y", "-loglevel", "error", *entrada, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-r", str(FPS),
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", str(salida)])
    return duracion_de(salida)


COLORES_PUESTO = {1: "&H00F2FF&", 2: "&HD8D8D8&", 3: "&H1A7AFF&", 4: "&HFFFFFF&", 5: "&HFFFFFF&"}


def estilos_ranking(plan):
    f = plan.get("fuente", "Arial")
    rk = plan["ranking"]
    return (f"Style: RTitulo,{f},{rk.get('tam_titulo', 108)},&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,"
            f"0,0,0,0,100,100,0,0,1,9,5,8,40,40,{rk.get('y_titulo', 470)},1\n"
            f"Style: RLista,{f},{rk.get('tam_lista', 70)},&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,"
            f"0,0,0,0,100,100,0,0,1,7,4,4,0,0,0,1")


def eventos_ranking(rk, puestos, fin):
    """Título en dos colores y lista 1-5 a la izquierda; cada puesto muestra su título al llegar."""
    ev = []
    t1, t1b, t2 = rk.get("linea1", "TOP 5"), rk.get("linea1_color", "MOMENTOS"), rk.get("linea2", "")
    ev.append(f"Dialogue: 4,{t_ass(0)},{t_ass(fin)},RTitulo,,0,0,0,,{esc(t1)} {{\\c&H00F2FF&}}{esc(t1b)}"
              f"\\N{{\\c&HFFA829&}}{esc(t2)}")
    x, y0, paso = rk.get("x_lista", 70), rk.get("y_lista", 900), rk.get("paso_lista", 125)
    revel = {p: (ini, tit) for ini, p, tit in puestos}
    for p in range(1, 6):
        y = y0 + (p - 1) * paso
        col = COLORES_PUESTO[p]
        base = f"\\an4\\pos({x},{y})\\c{col}"
        if p in revel:
            ini, tit = revel[p]
            ev.append(f"Dialogue: 4,{t_ass(0)},{t_ass(ini)},RLista,,0,0,0,,{{{base}}}{p}.")
            ev.append(f"Dialogue: 4,{t_ass(ini)},{t_ass(fin)},RLista,,0,0,0,,{{{base}\\fscx60\\fscy60"
                      f"\\t(0,180,\\fscx112\\fscy112)\\t(180,300,\\fscx100\\fscy100)}}{p}. {esc(tit.upper())}")
        else:
            ev.append(f"Dialogue: 4,{t_ass(0)},{t_ass(fin)},RLista,,0,0,0,,{{{base}}}{p}.")
    return "\n".join(ev) + "\n"


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
        partes, etiquetas, sfx_eventos, puestos, t = [], [], [], [], 0.0
        inicio_cta = None
        for i, seg in enumerate(plan["segmentos"], 1):
            print(f"Segmento {i}/{len(plan['segmentos'])}: {seg.get('nota', seg['archivo'])}")
            p = tmp / f"seg{i:02d}.mp4"
            d = render_segmento(seg, base, p)
            if plan.get("whoosh_entre_segmentos") and i > 1:
                sfx_eventos.append((max(0.0, t - 0.15), "whoosh"))
            for s in seg.get("sfx", []):  # efectos en segundos relativos al segmento
                sfx_eventos.append((t + float(s.get("en", 0)), s["tipo"]))
            if seg.get("puesto"):
                puestos.append((t, int(seg["puesto"]), seg.get("titulo_puesto", "")))
            if seg.get("cta"):
                inicio_cta = t
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
        txt = ass.read_text(encoding="utf-8")
        if plan.get("altura_gancho"):  # mover títulos (gancho y #N) para no tapar la cámara del streamer
            txt = txt.replace(",8,70,70,170,1", f",8,70,70,{plan['altura_gancho']},1")
        if plan.get("fuente"):  # p. ej. "Inter Display Black"
            txt = txt.replace("Style: Subs,Arial,", f"Style: Subs,{plan['fuente']},").replace(
                "Style: Gancho,Arial,", f"Style: Gancho,{plan['fuente']},")
        rk = plan.get("ranking")
        if rk:  # formato "TOP 5": título fijo + lista 1-5 que se va revelando
            txt = txt.replace("\n[Events]", "\n" + estilos_ranking(plan) + "\n[Events]", 1)
            txt += eventos_ranking(rk, puestos, inicio_cta if inicio_cta is not None else dur)
        ass.write_text(txt, encoding="utf-8")
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
        if sfx_eventos:  # efectos sintetizados (sin derechos de autor)
            from sfx import generar
            hechos, etiq_sfx = {}, []
            for k, (en, tipo) in enumerate(sfx_eventos):
                if tipo not in hechos:
                    hechos[tipo] = generar(tipo, tmp / f"sfx_{tipo}.wav")
                entradas += ["-i", str(hechos[tipo])]
                ms = int(en * 1000)
                filtros.append(f"[{n}:a]volume={plan.get('volumen_sfx', 0.8)},adelay={ms}|{ms}[s{k}]")
                etiq_sfx.append(f"[s{k}]")
                n += 1
            filtros.append(f"[{actual}]{''.join(etiq_sfx)}amix=inputs={len(etiq_sfx) + 1}:duration=first:normalize=0[mixs]")
            actual = "mixs"
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
