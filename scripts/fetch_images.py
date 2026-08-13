"""Rellena las portadas del banco desde Wikipedia / Wikimedia Commons.

Sin clave de API, sin límite de peticiones y sin coste. Para una app de
cultura general da además imágenes más pertinentes que un banco de fotos de
stock: en la lección sobre la crisis de los misiles sale la foto real de
reconocimiento, y en las de arte, el cuadro.

Estrategia por lección, en orden:
  1. `cover_image.wikipedia` → imagen principal de ese artículo.
  2. `cover_image.query`     → búsqueda en Wikipedia y luego en Commons.
  3. Portada local de la categoría en assets/covers/.

Es idempotente: solo toca las lecciones sin `url`. Uso:

    python scripts/fetch_images.py                 # rellena lo que falte
    python scripts/fetch_images.py --only historia # una categoría
    python scripts/fetch_images.py --force         # rehace todas
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from html import unescape
from pathlib import Path
from urllib.parse import unquote

import requests

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from config.categories import CATEGORIES  # noqa: E402

RUTA_BANCO = RAIZ / "data" / "lessons_bank.json"
UA = "SophiaLF/1.0 (https://github.com/lucasfdezortiz; proyecto personal de aprendizaje)"
CABECERAS = {"User-Agent": UA}
TIMEOUT = 15
PAUSA = 1.0  # Wikimedia limita peticiones: por debajo de ~1 s/llamada devuelve 429
REINTENTOS = 4
ANCHO_MIN = 600

# Una sola conexión reutilizada: Wikimedia lo agradece y va más rápido.
SESION = requests.Session()
SESION.headers.update(CABECERAS)


class LimiteAlcanzado(RuntimeError):
    """El servidor sigue devolviendo 429 tras agotar los reintentos."""


def _get(url: str, params: dict) -> dict | None:
    """GET con reintentos ante 429/5xx.

    Devuelve None solo cuando la consulta es válida pero no hay resultado. Un
    límite de peticiones lanza excepción en vez de confundirse con un 'no hay
    imagen': ese silencio era lo que hacía parecer que faltaban portadas.
    """
    espera = PAUSA
    for intento in range(REINTENTOS):
        try:
            r = SESION.get(url, params=params, timeout=TIMEOUT)
        except requests.RequestException:
            time.sleep(espera)
            espera *= 2
            continue

        if r.status_code == 429:
            cabecera = r.headers.get("Retry-After")
            pausa = float(cabecera) if (cabecera or "").isdigit() else espera
            print(f"    · límite alcanzado, esperando {pausa:.0f}s…", flush=True)
            time.sleep(min(pausa, 60))
            espera = min(espera * 2, 60)
            continue

        if r.status_code >= 500:
            time.sleep(espera)
            espera *= 2
            continue

        if not r.ok:
            return None

        try:
            return r.json()
        except json.JSONDecodeError:
            return None

    raise LimiteAlcanzado(
        "Wikimedia sigue limitando las peticiones tras varios reintentos. "
        "Espera unos minutos y vuelve a lanzar el script: es idempotente."
    )


def _limpiar_html(texto: str) -> str:
    return unescape(re.sub(r"<[^>]+>", "", texto or "")).strip()


def buscar_articulo(consulta: str, lang: str = "es") -> str | None:
    datos = _get(
        f"https://{lang}.wikipedia.org/w/api.php",
        {
            "action": "query",
            "list": "search",
            "srsearch": consulta,
            "srlimit": 1,
            "format": "json",
        },
    )
    resultados = (datos or {}).get("query", {}).get("search", [])
    return resultados[0]["title"] if resultados else None


def imagen_de_articulo(titulo: str, lang: str = "es") -> tuple[str, str] | None:
    """(url_imagen, nombre_archivo_commons) de la imagen principal del artículo."""
    datos = _get(
        f"https://{lang}.wikipedia.org/w/api.php",
        {
            "action": "query",
            "titles": titulo,
            "prop": "pageimages",
            "piprop": "original|name",
            "redirects": 1,
            "format": "json",
        },
    )
    paginas = (datos or {}).get("query", {}).get("pages", {})
    for pagina in paginas.values():
        original = pagina.get("original")
        if not original or original.get("width", 0) < ANCHO_MIN:
            continue
        archivo = pagina.get("pageimage") or unquote(original["source"].rsplit("/", 1)[-1])
        return original["source"], archivo
    return None


def buscar_en_commons(consulta: str) -> tuple[str, str] | None:
    datos = _get(
        "https://commons.wikimedia.org/w/api.php",
        {
            "action": "query",
            "generator": "search",
            "gsrsearch": f"{consulta} filetype:bitmap",
            "gsrnamespace": 6,
            "gsrlimit": 5,
            "prop": "imageinfo",
            "iiprop": "url|size",
            "iiurlwidth": 1600,
            "format": "json",
        },
    )
    paginas = (datos or {}).get("query", {}).get("pages", {})
    for pagina in paginas.values():
        info = (pagina.get("imageinfo") or [{}])[0]
        url = info.get("thumburl") or info.get("url")
        if url and info.get("width", 0) >= ANCHO_MIN:
            return url, pagina["title"].removeprefix("File:")
    return None


def metadatos_commons(archivo: str) -> dict[str, str]:
    """Autoría, licencia y enlace a la ficha del archivo (requisito de atribución)."""
    datos = _get(
        "https://commons.wikimedia.org/w/api.php",
        {
            "action": "query",
            "titles": f"File:{archivo}",
            "prop": "imageinfo",
            "iiprop": "extmetadata|url",
            "format": "json",
        },
    )
    paginas = (datos or {}).get("query", {}).get("pages", {})
    for pagina in paginas.values():
        info = (pagina.get("imageinfo") or [{}])[0]
        meta = info.get("extmetadata", {}) or {}
        autor = _limpiar_html(meta.get("Artist", {}).get("value", ""))
        licencia = _limpiar_html(meta.get("LicenseShortName", {}).get("value", ""))
        return {
            "credit": autor or "Wikimedia Commons",
            "license": licencia or "Ver ficha del archivo",
            "source_url": info.get("descriptionurl")
            or f"https://commons.wikimedia.org/wiki/File:{archivo}",
        }
    return {
        "credit": "Wikimedia Commons",
        "license": "Ver ficha del archivo",
        "source_url": f"https://commons.wikimedia.org/wiki/File:{archivo}",
    }


def resolver_portada(cover: dict) -> dict | None:
    """Intenta las tres vías y devuelve los campos a fusionar, o None."""
    candidatos: list[tuple[str, str]] = []

    if cover.get("wikipedia"):
        for lang in ("es", "en"):
            if hit := imagen_de_articulo(cover["wikipedia"], lang):
                candidatos.append(hit)
                break
            time.sleep(PAUSA)

    consulta = cover.get("query", "")
    if not candidatos and consulta:
        for lang in ("es", "en"):
            if titulo := buscar_articulo(consulta, lang):
                time.sleep(PAUSA)
                if hit := imagen_de_articulo(titulo, lang):
                    candidatos.append(hit)
                    break
            time.sleep(PAUSA)

    if not candidatos and consulta:
        if hit := buscar_en_commons(consulta):
            candidatos.append(hit)

    if not candidatos:
        return None

    url, archivo = candidatos[0]
    time.sleep(PAUSA)
    return {"url": url, **metadatos_commons(archivo)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only", help="limitar a una categoría")
    ap.add_argument("--force", action="store_true", help="rehacer también las que ya tienen url")
    ap.add_argument("--dry-run", action="store_true", help="no escribir el banco")
    args = ap.parse_args()

    banco = json.loads(RUTA_BANCO.read_text(encoding="utf-8"))
    lecciones = banco["lecciones"]

    pendientes = [
        l
        for l in lecciones
        if (args.only is None or l["category"] == args.only)
        and (args.force or not l.get("cover_image", {}).get("url"))
    ]

    if not pendientes:
        print("Nada que hacer: todas las portadas están resueltas.")
        return 0

    print(f"Resolviendo {len(pendientes)} portadas…\n")
    resueltas = fallidas = 0
    interrumpido = False

    def escribir() -> None:
        if not args.dry_run:
            RUTA_BANCO.write_text(
                json.dumps(banco, ensure_ascii=False, indent=2), encoding="utf-8"
            )

    for i, lec in enumerate(pendientes, 1):
        cover = lec.setdefault("cover_image", {})
        etiqueta = (
            f"[{i}/{len(pendientes)}] "
            f"{CATEGORIES[lec['category']]['nombre'][:14]:<14} {lec['title'][:44]}"
        )
        try:
            datos = resolver_portada(cover)
        except LimiteAlcanzado as e:
            print(f"\n{e}")
            interrumpido = True
            break

        if datos:
            cover.update(datos)
            resueltas += 1
            print(f"  ok   {etiqueta}", flush=True)
        else:
            cover.setdefault("url", None)
            fallidas += 1
            print(f"  --   {etiqueta}  (sin imagen: portada de categoría)", flush=True)

        # Guardado incremental: si se corta, no se pierde lo ya resuelto.
        if i % 10 == 0:
            escribir()
        time.sleep(PAUSA)

    print(f"\n{resueltas} resueltas · {fallidas} sin imagen en Wikipedia ni Commons")

    if args.dry_run:
        print("--dry-run: no se ha escrito el banco.")
        return 0

    escribir()
    print(f"Banco actualizado: {RUTA_BANCO}")
    return 1 if interrumpido else 0


if __name__ == "__main__":
    raise SystemExit(main())
