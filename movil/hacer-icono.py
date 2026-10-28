#!/usr/bin/env python3
"""Convierte una foto cualquiera en el icono de la app.

    python3 movil/hacer-icono.py ~/Desktop/mi-foto.jpg

Recorta al centro para dejarla cuadrada, la lleva a 1024x1024 y la guarda
como `movil/icono.png`, que es el archivo que lee `index.html`. iOS redondea
las esquinas por su cuenta, así que la imagen se entrega a sangre.

Si no se pasa ninguna foto, regenera el icono de marca: las iniciales en
dorado sobre el azul de la app.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

LADO = 1024
DESTINO = Path(__file__).resolve().parent / "icono.png"
SERIF = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"

ORO = (231, 188, 99)
ORO_CLARO = (244, 213, 146)
ORO_APAGADO = (170, 128, 56)
PANEL = (22, 32, 46)
FONDO = (9, 13, 19)


def desde_foto(ruta: Path) -> Image.Image:
    img = Image.open(ruta).convert("RGB")
    # Recorte centrado al cuadrado: así no se deforma nada.
    lado = min(img.size)
    izq = (img.width - lado) // 2
    arr = (img.height - lado) // 2
    return img.crop((izq, arr, izq + lado, arr + lado)).resize(
        (LADO, LADO), Image.LANCZOS
    )


def de_marca() -> Image.Image:
    img = Image.new("RGB", (LADO, LADO), FONDO)
    d = ImageDraw.Draw(img)
    for y in range(LADO):
        t = y / (LADO - 1)
        k = t * t * (3 - 2 * t)          # suaviza el degradado
        d.line([(0, y), (LADO, y)],
               fill=tuple(int(a + (b - a) * k) for a, b in zip(PANEL, FONDO)))

    rejilla = Image.new("RGBA", (LADO, LADO), (0, 0, 0, 0))
    dr = ImageDraw.Draw(rejilla)
    paso = LADO // 8
    for i in range(1, 8):
        dr.line([(i * paso, 0), (i * paso, LADO)], fill=(*ORO, 16), width=2)
        dr.line([(0, i * paso), (LADO, i * paso)], fill=(*ORO, 16), width=2)
    img = Image.alpha_composite(img.convert("RGBA"), rejilla).convert("RGB")
    d = ImageDraw.Draw(img)

    for x in range(LADO):                 # filo superior en degradado
        a = max(0.0, 1 - (x / LADO) / 0.92)
        d.line([(x, 0), (x, 11)],
               fill=tuple(int(c * a + f * (1 - a)) for c, f in zip(ORO_CLARO, PANEL)))

    f = ImageFont.truetype(SERIF, 430)
    caja = d.textbbox((0, 0), "LF", font=f)
    w, h = caja[2] - caja[0], caja[3] - caja[1]
    x, y = (LADO - w) / 2 - caja[0], (LADO - h) / 2 - caja[1] - 48
    d.text((x, y), "LF", font=f, fill=ORO)

    rw = int(w * 0.80)
    ry = y + caja[3] + 78
    d.rounded_rectangle([(LADO - rw) // 2, ry, (LADO + rw) // 2, ry + 9],
                        radius=5, fill=ORO_APAGADO)
    return img


def main() -> None:
    if len(sys.argv) > 1:
        ruta = Path(sys.argv[1]).expanduser()
        if not ruta.exists():
            sys.exit(f"No encuentro la imagen: {ruta}")
        img = desde_foto(ruta)
        origen = ruta.name
    else:
        img = de_marca()
        origen = "icono de marca"

    img.save(DESTINO, "PNG")
    print(f"{DESTINO}  ←  {origen}  ({img.width}x{img.height})")
    print("Vuelve a subir la carpeta `movil` para que el cambio llegue al móvil.")


if __name__ == "__main__":
    main()
