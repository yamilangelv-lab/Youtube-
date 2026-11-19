#!/usr/bin/env python3
"""Arma un Short 9:16 a partir de imágenes (p. ej. Higgsfield) y narración por escena (p. ej. ElevenLabs).

Por escena: movimiento de cámara (Ken Burns / zoom a un punto), desenfoque u oscurecido opcional,
textos animados (fechas, años, tachados), subtítulos grandes palabra por palabra sincronizados
con la narración. Entre escenas: transiciones (xfade) con "whoosh". Fondo musical sintetizado
(o tu propio archivo) con ducking bajo la voz, "boom" en el clímax, botón de suscripción animado
y audio final a -14 LUFS.

Uso:  python short_imagenes.py proyecto.json
Ver ejemplo: ../videos/13-anios/proyecto.json
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

W, H, FPS, T = 1080, 1920, 30, 0.35  # T = duración de cada transición
FUENTE = "Inter Display Black"


def run(cmd, **kw):
    subprocess.run(cmd, check=True, **kw)


def dur_de(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def t_ass(s):
    s = max(0.0, s)
    h, r = divmod(s, 3600)
    m, r = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{r:05.2f}"


def esc(t):
    return t.replace("{", "(").replace("}", ")").replace("\n", " ")


# ---------- video por escena ----------
def clip_escena(esc_, base, largo, salida):
    img = str((base / esc_["imagen"]).resolve())
    n = int(round(largo * FPS))
    mov = esc_.get("movimiento", "in")
    zs, ze, fx0, fy0, fx1, fy1 = {
        "in": (1.0, 1.12, .5, .5, .5, .5),
        "out": (1.14, 1.0, .5, .5, .5, .5),
        "up": (1.12, 1.12, .5, .65, .5, .35),
        "down": (1.12, 1.12, .5, .35, .5, .65),
    }.get(mov, (1.0, 1.12, .5, .5, .5, .5))
    if "foco" in esc_:  # [fx, fy, zoom_inicial, zoom_final]: acercarse a un punto de la imagen
        fx0 = fx1 = esc_["foco"][0]
        fy0 = fy1 = esc_["foco"][1]
        zs, ze = esc_["foco"][2], esc_["foco"][3]
    p = f"(on/{max(n - 1, 1)})"
    z = f"({zs}+({ze}-{zs})*{p})"
    fx = f"({fx0}+({fx1}-{fx0})*{p})"
    fy = f"({fy0}+({fy1}-{fy0})*{p})"
    efecto = {"blur": ",boxblur=10:2,eq=brightness=-0.12:saturation=0.9",
              "oscuro": ",eq=brightness=-0.28:saturation=0.85"}.get(esc_.get("efecto"), "")
    vf = (f"scale={W * 2}:{H * 2}:force_original_aspect_ratio=increase,crop={W * 2}:{H * 2},"
          f"zoompan=z='{z}':x='max(0,min(iw-iw/zoom,iw*{fx}-iw/zoom/2))':"
          f"y='max(0,min(ih-ih/zoom,ih*{fy}-ih/zoom/2))':d={n}:s={W}x{H}:fps={FPS}"
          f"{efecto},vignette=PI/5,noise=alls=5:allf=t,format=yuv420p")
    run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", img, "-vf", vf, "-frames:v", str(n),
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-r", str(FPS), str(salida)])


# ---------- subtítulos y textos ----------
def palabras_escena(texto, ini, dur):
    ws = texto.split()
    if not ws:
        return []
    pesos = [len(w) + 2 for w in ws]
    tot = sum(pesos)
    out, t = [], ini
    for w, p in zip(ws, pesos):
        d = dur * p / tot
        out.append({"w": w, "s": t, "e": t + d})
        t += d
    return out


def ass(proyecto, tiempos, total, salida):
    cab = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Subs,{FUENTE},94,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,8,3,2,70,70,{proyecto.get('altura_subs', 640)},1
Style: Gancho,{FUENTE},82,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,3,20,0,8,70,70,200,1
Style: Fecha,{FUENTE},120,&H00FFFFFF,&H00FFFFFF,&H00000000,&H009A2BFF,0,0,0,0,100,100,2,0,3,26,0,5,60,60,0,1
Style: Anio,{FUENTE},260,&H0000F2FF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,12,6,5,40,40,0,1
Style: Tachado,{FUENTE},130,&H004040FF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,10,4,5,40,40,0,1
Style: CTA,{FUENTE},86,&H00FFFFFF,&H00FFFFFF,&H00000000,&HA0000000,0,0,0,0,100,100,0,0,1,8,4,5,70,70,0,1
Style: Boton,{FUENTE},64,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,0,0,5,0,0,0,1
Style: Forma,{FUENTE},20,&H000000FF,&H000000FF,&H000000FF,&H00000000,0,0,0,0,100,100,0,0,1,0,6,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    g = proyecto.get("gancho")
    if g:
        ev.append(f"Dialogue: 5,{t_ass(0)},{t_ass(g.get('hasta', 3))},Gancho,,0,0,0,,{{\\fad(0,200)}}{esc(g['texto'].upper())}")
    for e, (ini, dur_voz, fin) in zip(proyecto["escenas"], tiempos):
        # subtítulos palabra por palabra
        if e.get("texto") and dur_voz:
            ws = palabras_escena(e["texto"], ini + 0.12, dur_voz - 0.1)
            grupos = [ws[i:i + 3] for i in range(0, len(ws), 3)]
            for gi, gr in enumerate(grupos):
                sig = grupos[gi + 1][0]["s"] if gi + 1 < len(grupos) else fin - 0.05
                for j, w in enumerate(gr):
                    a = w["s"]
                    b = gr[j + 1]["s"] if j + 1 < len(gr) else min(w["e"] + 0.25, sig)
                    txt = " ".join(("{\\c&H00F2FF&\\fscx110\\fscy110}" + esc(x["w"].upper()) + "{\\c&HFFFFFF&\\fscx100\\fscy100}")
                                   if k == j else esc(x["w"].upper()) for k, x in enumerate(gr))
                    ev.append(f"Dialogue: 1,{t_ass(a)},{t_ass(b)},Subs,,0,0,0,,{txt}")
        # textos extra de la escena
        for o in e.get("overlays", []):
            a = ini + o.get("desde", 0.1)
            b = ini + o.get("hasta", fin - ini)
            estilo = o.get("estilo", "Fecha")
            pos = o.get("pos")
            tag = f"\\pos({pos[0]},{pos[1]})" if pos else ""
            pop = "\\fscx40\\fscy40\\t(0,180,\\fscx105\\fscy105)\\t(180,260,\\fscx100\\fscy100)"
            pre = "\\s1" if o.get("tachado") else ""
            ev.append(f"Dialogue: 3,{t_ass(a)},{t_ass(b)},{estilo},,0,0,0,,{{{tag}{pop}{pre}\\fad(0,150)}}{esc(o['texto'])}")
        # botón de suscripción animado
        if e.get("boton_suscribirse"):
            a = ini + 0.6
            cambio = a + 1.7
            bw, bh, cx, cy = 600, 140, W // 2, 1180
            caja = f"m 0 0 l {bw} 0 {bw} {bh} 0 {bh}"
            base = f"\\an7\\pos({cx - bw // 2},{cy - bh // 2})\\p1"
            ev.append(f"Dialogue: 2,{t_ass(a)},{t_ass(cambio)},Forma,,0,0,0,,{{{base}\\1c&H0000FF&\\3c&H0000FF&"
                      f"\\fscx30\\fscy30\\t(0,200,\\fscx106\\fscy106)\\t(200,280,\\fscx100\\fscy100)}}{caja}")
            ev.append(f"Dialogue: 3,{t_ass(a)},{t_ass(cambio)},Boton,,0,0,0,,{{\\pos({cx},{cy})\\fscx30\\fscy30"
                      f"\\t(0,200,\\fscx106\\fscy106)\\t(200,280,\\fscx100\\fscy100)}}SUSCRIBIRSE")
            ev.append(f"Dialogue: 2,{t_ass(cambio)},{t_ass(fin)},Forma,,0,0,0,,{{{base}\\1c&H505050&\\3c&H505050&"
                      f"\\t(0,120,\\fscx94\\fscy94)\\t(120,240,\\fscx100\\fscy100)}}{caja}")
            ev.append(f"Dialogue: 3,{t_ass(cambio)},{t_ass(fin)},Boton,,0,0,0,,{{\\pos({cx},{cy})"
                      f"\\t(0,120,\\fscx94\\fscy94)\\t(120,240,\\fscx100\\fscy100)}}SUSCRITO ✓")
    Path(salida).write_text(cab + "\n".join(ev) + "\n", encoding="utf-8")


# ---------- audio ----------
def musica_synth(total, salida):
    """Pad synthwave suave (Am - F - C - G), sin derechos de autor: lo genera ffmpeg."""
    acordes = [(110.0, 220.0, 261.63, 329.63), (87.31, 174.61, 220.0, 261.63),
               (65.41, 130.81, 196.0, 261.63), (98.0, 196.0, 246.94, 293.66)]
    partes = []
    with tempfile.TemporaryDirectory() as tmp:
        for i, ac in enumerate(acordes):
            expr = "+".join(f"{0.22 if k == 0 else 0.12}*sin(2*PI*{f}*t)*(1+0.15*sin(2*PI*0.5*t))"
                            f"+0.06*sin(2*PI*{f * 1.003}*t)" for k, f in enumerate(ac))
            p = Path(tmp) / f"c{i}.wav"
            run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"aevalsrc='{expr}':s=48000:d=4",
                 "-af", "afade=t=in:d=0.6,afade=t=out:st=3.4:d=0.6,lowpass=f=1400", "-ac", "2", str(p)])
            partes.append(p)
        lista = Path(tmp) / "l.txt"
        lista.write_text("".join(f"file '{p}'\n" for p in partes))
        loop = Path(tmp) / "loop.wav"
        run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lista), str(loop)])
        run(["ffmpeg", "-y", "-loglevel", "error", "-stream_loop", "-1", "-i", str(loop), "-t", f"{total:.2f}",
             "-af", "aecho=0.8:0.7:120|260:0.35|0.2,afade=t=out:st=" + f"{max(0, total - 1.5):.2f}" + ":d=1.5",
             str(salida)])


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    pj = Path(sys.argv[1]).resolve()
    base = pj.parent
    proyecto = json.loads(pj.read_text(encoding="utf-8"))
    escenas = proyecto["escenas"]
    salida = (base / proyecto.get("salida", "short.mp4")).resolve()

    # duración de cada escena según su narración
    tiempos, t = [], 0.0
    for e in escenas:
        dv = dur_de(base / e["audio"]) if e.get("audio") else 0.0
        d = max(e.get("min", 1.8), dv + e.get("respiro", 0.45))
        tiempos.append((t, dv, t + d))
        t += d
    total = t
    transiciones = proyecto.get("transiciones", ["fadewhite", "slideup", "smoothleft", "circleopen", "zoomin",
                                                  "fadeblack", "radial", "slidedown"])

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        clips = []
        for i, (e, (ini, dv, fin)) in enumerate(zip(escenas, tiempos)):
            largo = (fin - ini) + (T if i < len(escenas) - 1 else 0)
            c = tmp / f"c{i:02d}.mp4"
            print(f"Escena {i + 1}/{len(escenas)} ({largo:.1f}s)")
            clip_escena(e, base, largo, c)
            clips.append(c)

        # unir con transiciones
        entradas = sum((["-i", str(c)] for c in clips), [])
        fc, prev = [], "[0:v]"
        for i in range(1, len(clips)):
            off = tiempos[i][0]
            tr = escenas[i].get("transicion", transiciones[(i - 1) % len(transiciones)])
            out = f"[x{i}]"
            fc.append(f"{prev}[{i}:v]xfade=transition={tr}:duration={T}:offset={off:.3f}{out}")
            prev = out
        video = tmp / "video.mp4"
        run(["ffmpeg", "-y", "-loglevel", "error", *entradas, "-filter_complex", ";".join(fc) or "[0:v]null[x0]",
             "-map", prev if fc else "[x0]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", str(video)])

        # subtítulos y textos
        ass(proyecto, tiempos, total, tmp / "subs.ass")

        # audio: narración + música + sfx
        a_in, a_fc, mezcla = [], [], []
        k = 0
        for e, (ini, dv, fin) in zip(escenas, tiempos):
            if e.get("audio"):
                a_in += ["-i", str((base / e["audio"]).resolve())]
                ms = int((ini + 0.12) * 1000)
                a_fc.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms}[n{k}]")
                mezcla.append(f"[n{k}]")
                k += 1
        a_fc.append(f"{''.join(mezcla)}amix=inputs={len(mezcla)}:normalize=0:duration=longest,apad=whole_dur={total:.2f}[voz]")
        musica = proyecto.get("musica", "synth")
        mus_path = tmp / "musica.wav"
        if musica == "synth":
            musica_synth(total, mus_path)
        elif musica:
            run(["ffmpeg", "-y", "-loglevel", "error", "-stream_loop", "-1", "-i", str((base / musica).resolve()),
                 "-t", f"{total:.2f}", str(mus_path)])
        if musica:
            clim = next((ini for e, (ini, _, _) in zip(escenas, tiempos) if e.get("boom")), total)
            a_in += ["-i", str(mus_path)]
            a_fc.append(f"[{k}:a]aresample=48000,volume='if(gte(t,{clim:.2f}),0.55,0.32)':eval=frame[mus]")
            a_fc.append("[voz]asplit=2[v1][v2]")
            a_fc.append("[mus][v1]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[mduck]")
            k += 1
            voz_final, fondo = "[v2]", "[mduck]"
        else:
            voz_final, fondo = "[voz]", None
        # whoosh en cada transición
        sfx = []
        for i in range(1, len(escenas)):
            ms = int(max(0, tiempos[i][0] - 0.12) * 1000)
            a_fc.append(f"anoisesrc=d=0.45:c=pink:a=0.5,highpass=f=900,lowpass=f=6000,"
                        f"afade=t=in:d=0.2,afade=t=out:st=0.2:d=0.25,volume=0.35,aformat=channel_layouts=stereo,"
                        f"adelay={ms}|{ms}[w{i}]")
            sfx.append(f"[w{i}]")
        for i, (e, (ini, _, _)) in enumerate(zip(escenas, tiempos)):
            if e.get("boom"):
                ms = int(ini * 1000)
                a_fc.append(f"aevalsrc='0.9*sin(2*PI*(60-35*t)*t)*exp(-3.5*t)':s=48000:d=1.6,"
                            f"aformat=channel_layouts=stereo,adelay={ms}|{ms}[b{i}]")
                sfx.append(f"[b{i}]")
        partes = [voz_final] + ([fondo] if fondo else []) + sfx
        a_fc.append(f"{''.join(partes)}amix=inputs={len(partes)}:normalize=0:duration=first,"
                    f"loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
        print("Render final…")
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), *a_in,
             "-filter_complex", ";".join(_reindex(a_fc, 1)) + ";[0:v]ass=subs.ass,format=yuv420p[vout]",
             "-map", "[vout]", "-map", "[aout]", "-t", f"{total:.2f}",
             "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", str(FPS),
             "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(salida)], cwd=tmp)
    print(f"Listo: {salida} ({total:.1f}s)")


def _reindex(filtros, desplazamiento):
    """Las entradas de audio empiezan en 1 porque la 0 es el video."""
    import re
    return [re.sub(r"\[(\d+):a\]", lambda m: f"[{int(m.group(1)) + desplazamiento}:a]", f) for f in filtros]


if __name__ == "__main__":
    main()
