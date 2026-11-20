#!/usr/bin/env python3
"""Arma un video largo horizontal (1920x1080) de "mejores momentos" a partir de clips cortos.

Diseño pensado para NO tapar nunca al streamer ni el clip:
  ┌──────────────┬──────────────┬──────────────┐
  │ MOMENTO 5    │              │ Clips: @...  │
  │ TÍTULO DEL   │   CLIP       │              │
  │ MOMENTO      │  (centro)    │ (suscríbete) │
  ├──────────────┴──────────────┴──────────────┤
  │            subtítulos (franja propia)       │
  └─────────────────────────────────────────────┘
Fondo: el mismo clip desenfocado y oscurecido.

Incluye: gancho inicial (montaje de remates), tarjeta de título, capítulos con título y número,
subtítulos palabra por palabra (faster-whisper), efectos de sonido sintetizados (sfx.py),
recordatorio de suscripción a mitad de video, cierre con llamada a la acción, audio a -14 LUFS,
capítulos para la descripción de YouTube y miniatura 1280x720.

Uso:  python largo.py plan.json
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from clipear import a_segundos, duracion_de, esc, t_ass, transcribir  # noqa: E402
from sfx import generar as generar_sfx  # noqa: E402

W, H, FPS = 1920, 1080, 30
ALTO_CLIP = 960          # alto del clip central; debajo queda la franja de subtítulos
ANCHO_MAX_CLIP = 1300


COMPLETA = False  # True: clip a pantalla completa 16:9 (pantalla_completa.py), sin fondo desenfocado


def run(cmd, **kw):
    subprocess.run(cmd, check=True, **kw)


def render_clip(src, ini, fin, salida, solo_fondo=False):
    """Clip centrado arriba + fondo desenfocado. solo_fondo=True deja solo el fondo (tarjetas)."""
    fg = (f"[b]scale={ANCHO_MAX_CLIP}:{ALTO_CLIP}:force_original_aspect_ratio=decrease,setsar=1,"
          f"pad=iw+8:ih+8:4:4:color=white@0.85[fg];[bg][fg]overlay=(W-w)/2:0[v0]") if not solo_fondo else "[bg]null[v0]"
    if COMPLETA and not solo_fondo:
        from pantalla_completa import filtro
        fc = (f"[0:v]setpts=PTS-STARTPTS,fps={FPS}[pre];{filtro(src, '[pre]', '[v0]')};"
              f"[v0]format=yuv420p,setsar=1[v];"
              f"[0:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS[a]")
    else:
        fc = (f"[0:v]setpts=PTS-STARTPTS,fps={FPS},split[a][b];"
              f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:5,"
              f"eq=brightness=-0.3:saturation=0.8[bg];{fg};[v0]format=yuv420p,setsar=1[v];"
              f"[0:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS[a]")
    run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(ini), "-to", str(fin), "-i", str(src),
         "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast",
         "-crf", "18", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", str(salida)])
    return duracion_de(salida)


def render_congelado(src, t, dur, salida, con_clip=True):
    """Imagen congelada (para tarjeta de título o cierre), con audio en silencio."""
    fg = (f"[b]scale={ANCHO_MAX_CLIP}:{ALTO_CLIP}:force_original_aspect_ratio=decrease,setsar=1,"
          f"pad=iw+8:ih+8:4:4:color=white@0.85,eq=brightness=-0.15[fg];[bg][fg]overlay=(W-w)/2:0[v0]"
          if con_clip else "[bg]null[v0]")
    division = "split[a][b]" if con_clip else "null[a]"
    congelar = f"[0:v]trim=end_frame=1,loop=loop=-1:size=1,trim=duration={dur},setpts=N/{FPS}/TB,fps={FPS}"
    if COMPLETA and con_clip:
        from pantalla_completa import filtro
        fc = (f"{congelar}[pre];{filtro(src, '[pre]', '[v1]')};"
              f"[v1]eq=brightness=-0.12,format=yuv420p,setsar=1[v]")
    else:
        fc = (f"{congelar},{division};"
              f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:5,"
              f"eq=brightness=-0.35:saturation=0.8[bg];{fg};[v0]format=yuv420p,setsar=1[v]")
    run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(t), "-i", str(src), "-f", "lavfi", "-t", str(dur),
         "-i", "anullsrc=r=48000:cl=stereo", "-filter_complex", fc, "-map", "[v]", "-map", "1:a",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k",
         "-ar", "48000", "-ac", "2", "-t", str(dur), str(salida)])
    return duracion_de(salida)


def transcribir_tramo(base, archivo, ini, fin, idioma="es", modelo="medium", vad=False):
    """Transcribe un tramo de un clip con caché en base/.transcripciones.json (tiempos relativos al tramo)."""
    cache_f = base / ".transcripciones.json"
    cache = json.loads(cache_f.read_text(encoding="utf-8")) if cache_f.exists() else {}
    clave = f"{archivo}|{ini}|{fin}|{modelo}|vad={vad}"
    if clave not in cache:
        with tempfile.TemporaryDirectory() as t2:
            wav = Path(t2) / "a.wav"
            run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(ini), "-to", str(fin), "-i", str(base / archivo),
                 "-vn", "-ac", "1", "-ar", "16000", str(wav)])
            cache[clave] = transcribir(wav, idioma, modelo, vad)
        cache_f.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    return cache[clave]


def estilos(f):
    margen_panel = W - 640  # el texto del panel izquierdo se ajusta a ~580 px de ancho
    if COMPLETA:  # pantalla completa: textos pequeños en la esquina superior izquierda y franja inferior
        lineas = f"""Style: Num,{f},34,&H0000F2FF,&H00FFFFFF,&H90000000,&H00000000,0,0,0,0,100,100,3,0,3,10,0,7,40,{W - 900},34,1
Style: Capitulo,{f},50,&H00FFFFFF,&H00FFFFFF,&H90000000,&H00000000,0,0,0,0,100,100,0,0,3,12,0,7,40,{W - 900},92,1
Style: Credito,{f},24,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,3,1,1,40,40,20,1
Style: Subs,{f},58,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,6,2,2,160,160,64,1"""
    else:
        lineas = f"""Style: Num,{f},42,&H0000F2FF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,3,0,1,4,2,7,60,{margen_panel},330,1
Style: Capitulo,{f},70,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,6,3,7,60,{margen_panel},390,1
Style: Credito,{f},30,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,3,1,9,40,60,60,1
Style: Subs,{f},54,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,5,2,2,80,80,22,1"""
    return f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
{lineas}
Style: Grande,{f},118,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,9,5,5,120,120,0,1
Style: PanelD,{f},50,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,5,2,4,{W - 640},60,0,1
Style: Boton,{f},50,&H00FFFFFF,&H00FFFFFF,&H000000FF,&H00000000,0,0,0,0,100,100,1,0,3,18,0,5,0,0,0,1
Style: BotonGris,{f},50,&H00FFFFFF,&H00FFFFFF,&H00505050,&H00000000,0,0,0,0,100,100,1,0,3,18,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


POP = "\\fscx50\\fscy50\\t(0,160,\\fscx108\\fscy108)\\t(160,260,\\fscx100\\fscy100)"


def subs_eventos(palabras, por_linea=4):
    ev = []
    grupos = [palabras[i:i + por_linea] for i in range(0, len(palabras), por_linea)]
    for gi, g in enumerate(grupos):
        sig = grupos[gi + 1][0]["s"] if gi + 1 < len(grupos) else None
        for j, w in enumerate(g):
            a = w["s"]
            b = g[j + 1]["s"] if j + 1 < len(g) else w["e"] + 0.2
            if sig is not None:
                b = min(b, sig)
            if b <= a:
                continue
            txt = " ".join(("{\\c&H00F2FF&}" + esc(x["w"].upper()) + "{\\c&HFFFFFF&}") if k == j else esc(x["w"].upper())
                           for k, x in enumerate(g))
            ev.append(f"Dialogue: 1,{t_ass(a)},{t_ass(b)},Subs,,0,0,0,,{txt}")
    return ev


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    pj = Path(sys.argv[1]).resolve()
    base = pj.parent
    plan = json.loads(pj.read_text(encoding="utf-8"))
    salida = (base / plan.get("salida", "largo.mp4")).resolve()
    global COMPLETA
    COMPLETA = bool(plan.get("pantalla_completa"))
    fuente = plan.get("fuente", "Inter Display Black")
    credito = plan.get("credito", "")

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        piezas, ev, sfx, capitulos, t = [], [], [], [], 0.0

        def agregar(p, d):
            nonlocal t
            piezas.append(p)
            t += d

        # 1) gancho: remates rápidos
        for i, g in enumerate(plan.get("gancho", [])):
            p = tmp / f"g{i:02d}.mp4"
            d = render_clip(base / g["archivo"], a_segundos(g["inicio"]), a_segundos(g["fin"]), p)
            if i:
                sfx.append((t - 0.1, "whoosh"))
            for s in g.get("sfx", []):
                sfx.append((t + s["en"], s["tipo"]))
            agregar(p, d)
        # 2) tarjeta de título
        tt = plan.get("tarjeta_titulo")
        if tt:
            p = tmp / "titulo.mp4"
            d = render_congelado(base / tt["archivo"], a_segundos(tt["momento"]), tt.get("duracion", 3.0), p, con_clip=False)
            l1, l2 = plan["titulo"]
            ev.append(f"Dialogue: 5,{t_ass(t)},{t_ass(t + d)},Grande,,0,0,0,,{{{POP}}}{esc(l1)}\\N{{\\c&H00F2FF&}}{esc(l2)}")
            sfx.append((t, "boom"))
            agregar(p, d)
        inicio_momentos = t
        capitulos.append((0.0, "Intro"))

        # 3) momentos
        n = len(plan["momentos"])
        palabras_tot = []
        for i, m in enumerate(plan["momentos"], 1):
            p = tmp / f"m{i:02d}.mp4"
            print(f"Momento {i}/{n}: {m['titulo']}")
            d = render_clip(base / m["archivo"], a_segundos(m["inicio"]), a_segundos(m["fin"]), p)
            sfx.append((max(0, t - 0.12), "whoosh"))
            for s in m.get("sfx", []):
                sfx.append((t + s["en"], s["tipo"]))
            ev.append(f"Dialogue: 3,{t_ass(t)},{t_ass(t + d)},Num,,0,0,0,,{{{POP}}}MOMENTO {i}")
            ev.append(f"Dialogue: 3,{t_ass(t + 0.15)},{t_ass(t + d)},Capitulo,,0,0,0,,{{{POP}}}{esc(m['titulo'].upper())}")
            if credito:
                ev.append(f"Dialogue: 2,{t_ass(t)},{t_ass(t + d)},Credito,,0,0,0,,{esc(credito)}")
            if plan.get("subtitulos", True):
                try:
                    pal = transcribir_tramo(base, m["archivo"], a_segundos(m["inicio"]), a_segundos(m["fin"]),
                                            plan.get("idioma", "es"), plan.get("modelo", "medium"))
                    for w in pal:  # correcciones manuales: {"palabra mal": "palabra bien"}
                        w["w"] = m.get("correcciones", {}).get(w["w"], w["w"])
                    pal = [w for w in pal if w["w"]]
                except Exception as e:  # sin modelo: seguir sin subtítulos
                    print("   (sin subtítulos:", e, ")")
                    pal = []
                for w in pal:
                    if w["s"] < d - 0.05:
                        palabras_tot.append({"w": w["w"], "s": t + w["s"], "e": t + min(w["e"], d)})
            if d >= 10:  # YouTube exige capítulos de 10 s o más
                capitulos.append((t, m["titulo"]))
            agregar(p, d)
        ev += subs_eventos(palabras_tot, plan.get("palabras_por_linea", 4))

        # 4) recordatorio de suscripción a mitad de video (panel derecho)
        mitad = inicio_momentos + (t - inicio_momentos) * plan.get("recordatorio_en", 0.45)
        yr = 800 if COMPLETA else 430  # pantalla completa: abajo a la derecha, lejos del recuadro de cámara
        ev.append(f"Dialogue: 4,{t_ass(mitad)},{t_ass(mitad + 5)},PanelD,,0,0,0,,{{\\an4\\pos({W - 600},{yr}){POP}}}¿TE ESTÁS RIENDO?")
        ev.append(f"Dialogue: 4,{t_ass(mitad + 0.4)},{t_ass(mitad + 3.2)},Boton,,0,0,0,,{{\\pos({W - 330},{yr + 110}){POP}}}SUSCRÍBETE")
        ev.append(f"Dialogue: 4,{t_ass(mitad + 3.2)},{t_ass(mitad + 5)},BotonGris,,0,0,0,,{{\\pos({W - 330},{yr + 110})}}SUSCRITO ✓")
        sfx.append((mitad + 0.4, "ding"))

        # 5) cierre
        c = plan.get("cierre")
        if c:
            p = tmp / "cierre.mp4"
            d = render_congelado(base / c["archivo"], a_segundos(c["momento"]), c.get("duracion", 6.0), p)
            sfx.append((t - 0.1, "whoosh"))
            ev.append(f"Dialogue: 5,{t_ass(t)},{t_ass(t + d)},Capitulo,,0,0,0,,{{{POP}}}{esc(c['texto'].upper())}")
            ev.append(f"Dialogue: 5,{t_ass(t + 0.6)},{t_ass(t + 2.6)},Boton,,0,0,0,,{{\\pos({W - 330},500){POP}}}SUSCRÍBETE")
            ev.append(f"Dialogue: 5,{t_ass(t + 2.6)},{t_ass(t + d)},BotonGris,,0,0,0,,{{\\pos({W - 330},500)}}SUSCRITO ✓")
            ev.append(f"Dialogue: 5,{t_ass(t + 1.2)},{t_ass(t + d)},PanelD,,0,0,0,,{{\\an4\\pos({W - 600},640){POP}}}{esc(c.get('despedida', 'Nos vemos en el próximo video'))}")
            sfx += [(t + 0.6, "ding"), (t + 2.6, "bonk")]
            agregar(p, d)
        total = t

        # unir
        (tmp / "lista.txt").write_text("".join(f"file '{p}'\n" for p in piezas))
        unido = tmp / "unido.mp4"
        run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(tmp / "lista.txt"),
             "-c", "copy", str(unido)])
        (tmp / "subs.ass").write_text(estilos(fuente) + "\n".join(ev) + "\n", encoding="utf-8")

        # audio: original + efectos
        entradas, filtros, etq = ["-i", str(unido)], [], []
        hechos = {}
        for k, (en, tipo) in enumerate(sfx):
            if tipo not in hechos:
                hechos[tipo] = generar_sfx(tipo, tmp / f"sfx_{tipo}.wav")
            entradas += ["-i", str(hechos[tipo])]
            ms = int(max(0, en) * 1000)
            filtros.append(f"[{k + 1}:a]volume={plan.get('volumen_sfx', 0.6)},adelay={ms}|{ms}[s{k}]")
            etq.append(f"[s{k}]")
        filtros.append(f"[0:a]{''.join(etq)}amix=inputs={len(etq) + 1}:duration=first:normalize=0,"
                       f"loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
        filtros.append("[0:v]ass=subs.ass,format=yuv420p[vout]")
        print("Render final…")
        run(["ffmpeg", "-y", "-loglevel", "error", *entradas, "-filter_complex", ";".join(filtros),
             "-map", "[vout]", "-map", "[aout]", "-t", f"{total:.2f}", "-c:v", "libx264", "-preset", "medium",
             "-crf", "20", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
             "-movflags", "+faststart", str(salida)], cwd=tmp)

    # capítulos para la descripción de YouTube
    def mmss(s):
        s = int(s)
        return f"{s // 60}:{s % 60:02d}"
    cap_txt = "\n".join(f"{mmss(a)} {tit}" for a, tit in capitulos)
    salida.with_suffix(".capitulos.txt").write_text(cap_txt + "\n", encoding="utf-8")
    print(f"Listo: {salida} ({total / 60:.1f} min)\nCapítulos:\n{cap_txt}")


if __name__ == "__main__":
    main()
