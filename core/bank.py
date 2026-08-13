"""Carga del banco de lecciones y métricas de cobertura.

El banco es un único JSON versionado en git. La app solo lo lee: nunca escribe
en él. Se amplía desde Claude Code, no desde la aplicación.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from config.categories import (
    CATEGORIES,
    OBJETIVO_TOTAL,
    UMBRAL_DIAS_RESTANTES,
)

RUTA_BANCO = Path(__file__).resolve().parent.parent / "data" / "lessons_bank.json"


def _orden_estable(leccion_id: str, categoria: str) -> str:
    """Clave de orden determinista pero no alfabética.

    Un hash de (categoría, id) reparte los temas de forma reproducible: la
    lección número 12 de geopolítica es siempre la misma, hoy y dentro de un
    año, pero el recorrido no sigue el orden en que las escribimos.
    """
    return hashlib.md5(f"{categoria}:{leccion_id}".encode()).hexdigest()


def cargar_banco(ruta: Path = RUTA_BANCO) -> dict[str, Any]:
    """Devuelve {'lecciones': {id: leccion}, 'por_categoria': {cat: [ids ordenados]}}."""
    if not ruta.exists():
        return {"lecciones": {}, "por_categoria": {c: [] for c in CATEGORIES}}

    crudo = json.loads(ruta.read_text(encoding="utf-8"))
    lecciones: dict[str, dict] = {}
    por_categoria: dict[str, list[str]] = {c: [] for c in CATEGORIES}

    for lec in crudo.get("lecciones", []):
        lid, cat = lec.get("id"), lec.get("category")
        if not lid or cat not in CATEGORIES:
            continue
        lecciones[lid] = lec
        por_categoria[cat].append(lid)

    for cat, ids in por_categoria.items():
        ids.sort(key=lambda i: _orden_estable(i, cat))

    return {"lecciones": lecciones, "por_categoria": por_categoria}


# --------------------------------------------------------------------------
# Cobertura y salud del banco
# --------------------------------------------------------------------------

def estadisticas(banco: dict, completadas: set[str]) -> dict[str, Any]:
    """Completado global y por categoría, más el avance hacia el banco objetivo."""
    total = len(banco["lecciones"])
    hechas = len(completadas & set(banco["lecciones"]))

    por_categoria = {}
    for cat, ids in banco["por_categoria"].items():
        n = len(ids)
        h = sum(1 for i in ids if i in completadas)
        objetivo = CATEGORIES[cat]["objetivo"]
        por_categoria[cat] = {
            "total": n,
            "completadas": h,
            "pendientes": n - h,
            "pct": (h / n * 100) if n else 0.0,
            "objetivo": objetivo,
            "pct_banco": (n / objetivo * 100) if objetivo else 0.0,
        }

    return {
        "total": total,
        "completadas": hechas,
        "pendientes": total - hechas,
        "pct": (hechas / total * 100) if total else 0.0,
        "objetivo_total": OBJETIVO_TOTAL,
        "pct_banco": (total / OBJETIVO_TOTAL * 100) if OBJETIVO_TOTAL else 0.0,
        "por_categoria": por_categoria,
    }


def check_bank_health(
    banco: dict,
    completadas: set[str],
    activas: list[str],
    umbral: int = UMBRAL_DIAS_RESTANTES,
) -> dict[str, Any]:
    """Días de banco restantes por categoría al ritmo de consumo configurado.

    Devuelve `avisos` con las categorías por debajo del umbral: son las que
    hay que recargar desde Claude Code.
    """
    detalle, avisos = {}, []

    for cat in activas:
        ids = banco["por_categoria"].get(cat, [])
        pendientes = sum(1 for i in ids if i not in completadas)
        por_dia = max(1, CATEGORIES[cat].get("por_dia", 1))
        dias = pendientes // por_dia
        detalle[cat] = {
            "pendientes": pendientes,
            "dias_restantes": dias,
            "objetivo": CATEGORIES[cat]["objetivo"],
            "faltan_para_objetivo": max(0, CATEGORIES[cat]["objetivo"] - len(ids)),
        }
        if dias < umbral:
            avisos.append(cat)

    dias_paquete = min((d["dias_restantes"] for d in detalle.values()), default=0)
    return {
        "detalle": detalle,
        "avisos": avisos,
        "dias_paquete_completo": dias_paquete,
        "umbral": umbral,
    }


def informe_salud(salud: dict) -> str:
    """Resumen en texto plano de check_bank_health(), para consola o README."""
    lineas = [
        f"Paquete diario completo garantizado: {salud['dias_paquete_completo']} días",
        "",
    ]
    for cat, d in sorted(salud["detalle"].items(), key=lambda kv: kv[1]["dias_restantes"]):
        marca = "!" if cat in salud["avisos"] else " "
        lineas.append(
            f" {marca} {CATEGORIES[cat]['nombre']:<22} "
            f"{d['pendientes']:>3} pendientes · {d['dias_restantes']:>3} días · "
            f"faltan {d['faltan_para_objetivo']:>3} para el objetivo"
        )
    if salud["avisos"]:
        nombres = ", ".join(CATEGORIES[c]["nombre"] for c in salud["avisos"])
        lineas += ["", f"Recargar banco: {nombres}"]
    return "\n".join(lineas)
