"""Validador del banco de lecciones.

Como las lecciones se escriben a mano (desde Claude Code, sin llamadas de pago
a la API), esta es la red de seguridad: comprueba mecánicamente el esquema, los
duplicados y las reglas de calidad antes de que nada llegue a la app.

    python scripts/validate_bank.py
    python scripts/validate_bank.py --fix-shuffle   # baraja las opciones del quiz
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
import unicodedata
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from config.categories import CATEGORIES, PREFIJOS  # noqa: E402

RUTA_BANCO = RAIZ / "data" / "lessons_bank.json"

MIN_TARJETAS, MAX_TARJETAS = 3, 5
MIN_PALABRAS_TARJETA, MAX_PALABRAS_TARJETA = 35, 90
MAX_PALABRAS_HEADING = 5
N_PREGUNTAS, N_OPCIONES = 4, 4
MAX_TITULO, MAX_SUBTITULO, MAX_KEY_FACT = 80, 130, 220

PROHIBIDAS = ["¿sabías que", "increíble", "todas las anteriores", "ninguna de las anteriores"]


def normalizar(texto: str) -> str:
    sin_tildes = "".join(
        c for c in unicodedata.normalize("NFD", texto.lower()) if unicodedata.category(c) != "Mn"
    )
    return " ".join(sin_tildes.split())


def validar_leccion(lec: dict, idx: int) -> list[str]:
    errores: list[str] = []
    lid = lec.get("id", f"#{idx}")

    def err(msg: str) -> None:
        errores.append(f"{lid}: {msg}")

    cat = lec.get("category")
    if cat not in CATEGORIES:
        err(f"categoría desconocida: {cat!r}")
    elif not str(lec.get("id", "")).startswith(PREFIJOS[cat] + "-"):
        err(f"el id debería empezar por '{PREFIJOS[cat]}-'")

    titulo = lec.get("title", "")
    if not titulo:
        err("sin título")
    elif len(titulo) > MAX_TITULO:
        err(f"título de {len(titulo)} caracteres (máx {MAX_TITULO})")

    subtitulo = lec.get("subtitle", "")
    if not subtitulo:
        err("sin subtítulo")
    elif len(subtitulo) > MAX_SUBTITULO:
        err(f"subtítulo de {len(subtitulo)} caracteres (máx {MAX_SUBTITULO})")

    key_fact = lec.get("key_fact", "")
    if not key_fact:
        err("sin key_fact")
    elif len(key_fact) > MAX_KEY_FACT:
        err(f"key_fact de {len(key_fact)} caracteres (máx {MAX_KEY_FACT})")

    cover = lec.get("cover_image") or {}
    if not cover.get("query"):
        err("cover_image sin 'query'")

    tarjetas = lec.get("cards") or []
    if not MIN_TARJETAS <= len(tarjetas) <= MAX_TARJETAS:
        err(f"{len(tarjetas)} tarjetas (se esperan {MIN_TARJETAS}-{MAX_TARJETAS})")
    for j, t in enumerate(tarjetas, 1):
        heading, texto = t.get("heading", ""), t.get("text", "")
        if not heading:
            err(f"tarjeta {j} sin heading")
        elif len(heading.split()) > MAX_PALABRAS_HEADING:
            err(f"tarjeta {j}: heading de {len(heading.split())} palabras (máx {MAX_PALABRAS_HEADING})")
        n = len(texto.split())
        if not MIN_PALABRAS_TARJETA <= n <= MAX_PALABRAS_TARJETA:
            err(f"tarjeta {j}: {n} palabras (se esperan {MIN_PALABRAS_TARJETA}-{MAX_PALABRAS_TARJETA})")

    preguntas = lec.get("questions") or []
    if len(preguntas) != N_PREGUNTAS:
        err(f"{len(preguntas)} preguntas (se esperan {N_PREGUNTAS})")
    for j, p in enumerate(preguntas, 1):
        opciones = p.get("options") or []
        if len(opciones) != N_OPCIONES:
            err(f"pregunta {j}: {len(opciones)} opciones (se esperan {N_OPCIONES})")
        if len({normalizar(o) for o in opciones}) != len(opciones):
            err(f"pregunta {j}: opciones duplicadas")
        correct = p.get("correct")
        if not isinstance(correct, int) or not 0 <= correct < len(opciones):
            err(f"pregunta {j}: 'correct' fuera de rango ({correct})")
        if not p.get("note"):
            err(f"pregunta {j}: sin 'note'")
        for o in opciones:
            if any(pr in normalizar(o) for pr in PROHIBIDAS[2:]):
                err(f"pregunta {j}: opción comodín prohibida")

    texto_total = normalizar(
        " ".join([titulo, subtitulo, key_fact] + [t.get("text", "") for t in tarjetas])
    )
    for frase in PROHIBIDAS[:2]:
        if frase in texto_total:
            err(f"contiene fórmula prohibida: {frase!r}")
    if "!" in " ".join([titulo, subtitulo, key_fact] + [t.get("text", "") for t in tarjetas]):
        err("contiene signos de exclamación")

    return errores


def barajar_opciones(banco: dict) -> int:
    """Reordena las opciones de cada pregunta de forma determinista e idempotente.

    Los modelos de lenguaje colocan la respuesta correcta en la primera posición
    mucho más a menudo de lo que saldría por azar, así que hay que barajar.

    La sutileza está en la idempotencia. Si se baraja el orden *actual*, volver a
    ejecutar el script aplica la misma permutación por segunda vez, y una
    permutación al cuadrado tiende a la identidad: la respuesta correcta regresa
    a su posición de origen y reaparece el sesgo. La solución es partir siempre
    de un orden canónico —las opciones ordenadas por el hash de su propio
    texto— y aplicar la permutación sobre él. Así el resultado depende solo del
    contenido, no de cuántas veces se haya ejecutado.
    """
    cambiadas = 0
    for lec in banco["lecciones"]:
        for j, p in enumerate(lec.get("questions", [])):
            correcta = p["options"][p["correct"]]
            # Orden canónico: independiente de cómo estuvieran antes.
            opciones = sorted(p["options"], key=lambda o: hashlib.md5(o.encode()).hexdigest())
            semilla = int(hashlib.md5(f"{lec['id']}:{j}".encode()).hexdigest()[:8], 16)
            random.Random(semilla).shuffle(opciones)
            indice = opciones.index(correcta)
            if opciones != p["options"] or indice != p["correct"]:
                p["options"], p["correct"] = opciones, indice
                cambiadas += 1
    return cambiadas


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fix-shuffle", action="store_true", help="barajar opciones y guardar")
    args = ap.parse_args()

    if not RUTA_BANCO.exists():
        print(f"No existe {RUTA_BANCO}")
        return 1

    banco = json.loads(RUTA_BANCO.read_text(encoding="utf-8"))
    lecciones = banco.get("lecciones", [])

    errores: list[str] = []

    ids = [l.get("id") for l in lecciones]
    for lid, n in Counter(ids).items():
        if n > 1:
            errores.append(f"id duplicado: {lid} ({n} veces)")

    titulos: dict[str, str] = {}
    for l in lecciones:
        clave = f"{l.get('category')}|{normalizar(l.get('title', ''))}"
        if clave in titulos:
            errores.append(f"título duplicado en {l.get('category')}: {l.get('title')!r}")
        titulos[clave] = l.get("id", "")

    for i, lec in enumerate(lecciones):
        errores.extend(validar_leccion(lec, i))

    por_categoria = Counter(l.get("category") for l in lecciones)
    print(f"Banco: {len(lecciones)} lecciones\n")
    for cat, meta in sorted(CATEGORIES.items(), key=lambda kv: kv[1]["orden"]):
        n = por_categoria.get(cat, 0)
        barra = "█" * int(n / meta["objetivo"] * 24) if meta["objetivo"] else ""
        print(f"  {meta['nombre']:<26} {n:>3}/{meta['objetivo']:<3} {barra}")

    dist = Counter(p["correct"] for l in lecciones for p in l.get("questions", []))
    if dist:
        total = sum(dist.values())
        reparto = " ".join(f"{i}:{dist.get(i, 0) / total * 100:.0f}%" for i in range(4))
        print(f"\nPosición de la respuesta correcta → {reparto}")

    if args.fix_shuffle:
        n = barajar_opciones(banco)
        RUTA_BANCO.write_text(json.dumps(banco, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nOpciones barajadas: {n} preguntas modificadas.")

    if errores:
        print(f"\n{len(errores)} problemas:\n")
        for e in errores:
            print(f"  · {e}")
        return 1

    print("\nSin errores.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
