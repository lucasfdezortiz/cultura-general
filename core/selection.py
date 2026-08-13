"""Selección diaria: qué lecciones toca hoy.

Reglas:
1. Para cada categoría activa se toma la siguiente lección **no vista**, según
   el orden estable de `bank._orden_estable`. No hay azar: recargar la página
   el mismo día devuelve exactamente lo mismo.
2. El paquete se **ancla** en el progreso la primera vez que se consulta ese
   día. Así, completar una lección a media mañana no reordena el resto del día.
3. Las categorías marcadas como "dominadas" bajan al final del paquete, pero
   siguen apareciendo.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from config.categories import CATEGORIES
from core import progress as prog_mod


def _siguiente_pendiente(
    banco: dict, categoria: str, completadas: set[str], excluir: set[str]
) -> str | None:
    for lid in banco["por_categoria"].get(categoria, []):
        if lid not in completadas and lid not in excluir:
            return lid
    return None


def construir_paquete(banco: dict, prog: dict, hoy: str) -> list[str]:
    """Ids del paquete de hoy, sin tocar el progreso."""
    completadas = prog_mod.ids_completadas(prog)
    activas = prog_mod.categorias_activas(prog)
    dominadas = set(prog.get("dominadas", []))

    prioritarias = [c for c in activas if c not in dominadas]
    secundarias = [c for c in activas if c in dominadas]
    orden = sorted(prioritarias, key=lambda c: CATEGORIES[c]["orden"]) + sorted(
        secundarias, key=lambda c: CATEGORIES[c]["orden"]
    )

    paquete: list[str] = []
    for cat in orden:
        for _ in range(max(1, CATEGORIES[cat].get("por_dia", 1))):
            lid = _siguiente_pendiente(banco, cat, completadas, set(paquete))
            if lid:
                paquete.append(lid)
    return paquete


def paquete_del_dia(banco: dict, prog: dict, hoy: str | None = None) -> tuple[list[str], bool]:
    """Devuelve (ids, cambio) anclando el paquete si aún no existe.

    `cambio` indica si hubo que escribir en el progreso, para que la capa de UI
    sepa si toca persistir.
    """
    hoy = hoy or date.today().isoformat()
    dia = prog["dias"].get(hoy)

    if dia and dia.get("paquete"):
        vigentes = [i for i in dia["paquete"] if i in banco["lecciones"]]

        # El paquete anclado NO se recalcula: completar una lección no debe
        # traer la siguiente de esa misma categoría al día de hoy. Lo único
        # que puede ampliarlo es activar una categoría que aún no aparezca.
        representadas = {banco["lecciones"][i]["category"] for i in vigentes}
        completadas = prog_mod.ids_completadas(prog)
        nuevos: list[str] = []
        for cat in sorted(prog_mod.categorias_activas(prog), key=lambda x: CATEGORIES[x]["orden"]):
            if cat in representadas:
                continue
            lid = _siguiente_pendiente(banco, cat, completadas, set(vigentes) | set(nuevos))
            if lid:
                nuevos.append(lid)

        if nuevos or len(vigentes) != len(dia["paquete"]):
            prog_mod.fijar_paquete(prog, hoy, vigentes + nuevos)
            return vigentes + nuevos, True
        return vigentes, False

    paquete = construir_paquete(banco, prog, hoy)
    prog_mod.fijar_paquete(prog, hoy, paquete)
    return paquete, True


def siguiente_extra(banco: dict, prog: dict, hoy: str | None = None) -> str | None:
    """Siguiente lección pendiente fuera del paquete, para "Seguir aprendiendo".

    Recorre las categorías activas por orden y devuelve la primera pendiente que
    no esté ya en el paquete de hoy. Cuenta para el % de completado pero no
    para el sello de racha.
    """
    hoy = hoy or date.today().isoformat()
    completadas = prog_mod.ids_completadas(prog)
    del_dia = set(prog["dias"].get(hoy, {}).get("paquete", []))
    activas = sorted(prog_mod.categorias_activas(prog), key=lambda c: CATEGORIES[c]["orden"])

    for cat in activas:
        lid = _siguiente_pendiente(banco, cat, completadas, del_dia)
        if lid:
            return lid
    return None


def siguiente_pendiente_del_paquete(prog: dict, paquete: list[str]) -> str | None:
    """Primera lección del paquete de hoy que siga sin completar."""
    completadas = prog_mod.ids_completadas(prog)
    return next((i for i in paquete if i not in completadas), None)


def estado_paquete(prog: dict, paquete: list[str], hoy: str | None = None) -> dict[str, Any]:
    hoy = hoy or date.today().isoformat()
    completadas = prog_mod.ids_completadas(prog)
    hechas = [i for i in paquete if i in completadas]
    return {
        "total": len(paquete),
        "completadas": len(hechas),
        "pendientes": len(paquete) - len(hechas),
        "cerrado": bool(paquete) and len(hechas) == len(paquete),
    }
