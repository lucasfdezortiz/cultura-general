"""Fusiona una tanda de lecciones nuevas en el banco.

Escribir cada tanda en su propio archivo bajo `data/tandas/` y fusionarla
después evita reescribir el banco completo en cada ampliación, y deja un
rastro de qué entró en cada momento.

    python scripts/merge_batch.py data/tandas/tanda-02.json
    python scripts/merge_batch.py data/tandas/*.json
    python scripts/merge_batch.py data/tandas/tanda-02.json --dry-run

Nunca sobrescribe una lección ya presente ni toca el progreso: el histórico se
guarda por id y sobrevive a cualquier ampliación.
"""

from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from config.categories import CATEGORIES  # noqa: E402

RUTA_BANCO = RAIZ / "data" / "lessons_bank.json"


def normalizar(texto: str) -> str:
    sin_tildes = "".join(
        c
        for c in unicodedata.normalize("NFD", (texto or "").lower())
        if unicodedata.category(c) != "Mn"
    )
    return " ".join(sin_tildes.split())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("tandas", nargs="+", help="archivos JSON con lecciones nuevas")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    banco = json.loads(RUTA_BANCO.read_text(encoding="utf-8"))
    existentes = {l["id"] for l in banco["lecciones"]}
    titulos = {f"{l['category']}|{normalizar(l['title'])}" for l in banco["lecciones"]}

    nuevas: list[dict] = []
    saltadas: list[str] = []

    for ruta_txt in args.tandas:
        ruta = Path(ruta_txt)
        if not ruta.exists():
            print(f"No existe: {ruta}")
            return 1
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        lote = datos["lecciones"] if isinstance(datos, dict) else datos

        for lec in lote:
            lid = lec.get("id")
            clave = f"{lec.get('category')}|{normalizar(lec.get('title', ''))}"
            if lid in existentes:
                saltadas.append(f"{lid} (id repetido)")
                continue
            if clave in titulos:
                saltadas.append(f"{lid} (título repetido: {lec.get('title')!r})")
                continue
            lec.setdefault("cover_image", {}).setdefault("url", None)
            nuevas.append(lec)
            existentes.add(lid)
            titulos.add(clave)

        print(f"{ruta.name}: {len(lote)} leídas")

    if saltadas:
        print(f"\nSaltadas {len(saltadas)}:")
        for s in saltadas:
            print(f"  · {s}")

    banco["lecciones"].extend(nuevas)
    por_cat = Counter(l["category"] for l in banco["lecciones"])

    print(f"\nAñadidas: {len(nuevas)} · Banco: {len(banco['lecciones'])} lecciones\n")
    total_obj = 0
    for cat, meta in sorted(CATEGORIES.items(), key=lambda kv: kv[1]["orden"]):
        n, obj = por_cat.get(cat, 0), meta["objetivo"]
        total_obj += obj
        barra = "█" * int(n / obj * 26) if obj else ""
        print(f"  {meta['nombre']:<22} {n:>3}/{obj:<3} {barra}")
    hechas = len(banco["lecciones"])
    print(f"\n  {'TOTAL':<22} {hechas:>3}/{total_obj:<3} ({hechas / total_obj * 100:.0f}% del objetivo)")

    if args.dry_run:
        print("\n--dry-run: no se ha escrito el banco.")
        return 0

    RUTA_BANCO.write_text(
        json.dumps(banco, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nBanco actualizado. Siguiente paso:")
    print("  python scripts/validate_bank.py --fix-shuffle")
    print("  python scripts/fetch_images.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
