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
from core.fechas import hoy as hoy_local


def _siguiente_pendiente(
    banco: dict, categoria: str, completadas: set[str], excluir: set[str]
) -> str | None:
    for lid in banco["por_categoria"].get(categoria, []):
        if lid not in completadas and lid not in excluir:
            return lid
    return None


def _rotacion(orden: list[str], hoy: str) -> list[str]:
    """Rota la lista de categorías según el día.

    Con un tope diario, sin rotación las últimas categorías del orden no
    saldrían nunca. Desplazar el punto de partida un puesto por día hace que
    todas entren en el paquete cada pocos días, y sigue siendo determinista:
    depende solo de la fecha.
    """
    if not orden:
        return orden
    dias = date.fromisoformat(hoy).toordinal()
    desfase = dias % len(orden)
    return orden[desfase:] + orden[:desfase]


def construir_paquete(banco: dict, prog: dict, hoy: str) -> list[str]:
    """Ids del paquete de hoy, sin tocar el progreso."""
    completadas = prog_mod.ids_completadas(prog)
    activas = prog_mod.categorias_activas(prog)
    dominadas = set(prog.get("dominadas", []))

    prioritarias = sorted(
        (c for c in activas if c not in dominadas), key=lambda c: CATEGORIES[c]["orden"]
    )
    secundarias = sorted(
        (c for c in activas if c in dominadas), key=lambda c: CATEGORIES[c]["orden"]
    )

    tope = prog_mod.max_por_dia(prog)
    if tope:
        # Solo rotan las prioritarias: las dominadas quedan siempre al final.
        orden = _rotacion(prioritarias, hoy) + secundarias
    else:
        orden = prioritarias + secundarias

    paquete: list[str] = []
    for cat in orden:
        if tope and len(paquete) >= tope:
            break
        for _ in range(max(1, CATEGORIES[cat].get("por_dia", 1))):
            if tope and len(paquete) >= tope:
                break
            lid = _siguiente_pendiente(banco, cat, completadas, set(paquete))
            if lid:
                paquete.append(lid)
    return paquete


def paquete_del_dia(banco: dict, prog: dict, hoy: str | None = None) -> tuple[list[str], bool]:
    """Devuelve (ids, cambio) anclando el paquete si aún no existe.

    `cambio` indica si hubo que escribir en el progreso, para que la capa de UI
    sepa si toca persistir.
    """
    hoy = hoy or hoy_local().isoformat()
    dia = prog["dias"].get(hoy)

    if dia and dia.get("paquete"):
        vigentes = [i for i in dia["paquete"] if i in banco["lecciones"]]
        completadas = prog_mod.ids_completadas(prog)
        tope = prog_mod.max_por_dia(prog)

        # Bajar el tope recorta el día en curso, quitando pendientes por la
        # cola. Si no, el ajuste no surtiría efecto hasta mañana y parecería
        # que el control está roto. Lo ya completado nunca se retira: cuenta
        # para el sello aunque exceda el tope nuevo.
        if tope and len(vigentes) > tope:
            hechas = [i for i in vigentes if i in completadas]
            pendientes = [i for i in vigentes if i not in completadas]
            hueco = max(0, tope - len(hechas))
            recortado = hechas + pendientes[:hueco]
            if recortado != vigentes:
                vigentes = [i for i in dia["paquete"] if i in recortado]
                prog_mod.fijar_paquete(prog, hoy, vigentes)
                return vigentes, True

        # El paquete anclado NO se recalcula: completar una lección no debe
        # traer la siguiente de esa misma categoría al día de hoy. Lo único
        # que puede ampliarlo es activar una categoría que aún no aparezca.
        representadas = {banco["lecciones"][i]["category"] for i in vigentes}
        nuevos: list[str] = []
        for cat in sorted(prog_mod.categorias_activas(prog), key=lambda x: CATEGORIES[x]["orden"]):
            if tope and len(vigentes) + len(nuevos) >= tope:
                break
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
    hoy = hoy or hoy_local().isoformat()
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
    hoy = hoy or hoy_local().isoformat()
    completadas = prog_mod.ids_completadas(prog)
    hechas = [i for i in paquete if i in completadas]
    return {
        "total": len(paquete),
        "completadas": len(hechas),
        "pendientes": len(paquete) - len(hechas),
        "cerrado": bool(paquete) and len(hechas) == len(paquete),
    }
