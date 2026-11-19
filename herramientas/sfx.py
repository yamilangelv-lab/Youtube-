#!/usr/bin/env python3
"""Efectos de sonido sintetizados con ffmpeg: 100 % propios y sin derechos de autor.

Tipos: whoosh, boom, boing, bonk, ding, risa_grave (un "uuuh" descendente cómico).
Uso como módulo: generar("boing", "boing.wav")
Uso por consola: python sfx.py boing salida.wav
"""
import subprocess
import sys

RECETAS = {
    # ruido rosa filtrado con subida y bajada: transición
    "whoosh": ("anoisesrc=d=0.5:c=pink:a=0.6",
               "highpass=f=700,lowpass=f=5500,afade=t=in:d=0.22,afade=t=out:st=0.22:d=0.28,volume=0.9"),
    # golpe grave tipo "vine boom"
    "boom": ("aevalsrc='0.95*sin(2*PI*(62-38*t)*t)*exp(-2.8*t)+0.25*sin(2*PI*31*t)*exp(-2*t)':s=48000:d=1.6",
             "lowpass=f=400,volume=1.4"),
    # resorte de dibujos animados
    "boing": ("aevalsrc='0.7*sin(2*PI*(260+140*sin(2*PI*14*t)*exp(-3.5*t))*t)*exp(-3.2*t)':s=48000:d=0.8",
              "volume=1.0"),
    # golpe en la cabeza
    "bonk": ("aevalsrc='0.9*sin(2*PI*190*t)*exp(-28*t)+0.5*sin(2*PI*410*t)*exp(-40*t)':s=48000:d=0.25",
             "volume=1.5"),
    # campanita de "correcto"/remate
    "ding": ("aevalsrc='0.5*sin(2*PI*1318*t)*exp(-4*t)+0.25*sin(2*PI*2636*t)*exp(-6*t)':s=48000:d=1.0",
             "volume=0.9"),
    # trombón triste / "uuuh" cómico descendente
    "risa_grave": ("aevalsrc='0.45*sin(2*PI*(233-90*t)*t+3*sin(2*PI*6*t))*(1-exp(-12*t))*exp(-1.2*t)':s=48000:d=1.4",
                   "lowpass=f=1800,volume=1.1"),
}


def generar(tipo, salida):
    if tipo not in RECETAS:
        raise ValueError(f"SFX desconocido: {tipo}. Opciones: {', '.join(RECETAS)}")
    fuente, filtro = RECETAS[tipo]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", fuente,
                    "-af", f"{filtro},aformat=sample_rates=48000:channel_layouts=stereo", str(salida)], check=True)
    return salida


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    generar(sys.argv[1], sys.argv[2])
