"""Selección diaria: qué lecciones toca hoy.

Reglas:
1. De cada categoría se toma la siguiente lección **no vista**, según el orden
   estable de `bank._orden_estable`. No hay azar: recargar la página el mismo
   día devuelve exactamente lo mismo.
2. Qué categorías entran cada día lo decide una **ruleta ponderada** por el
   campo `frecuencia` de cada categoría, no un reparto por igual. Es lo que
   hace que Mercados salga cuatro veces más a menudo que Humanidades.
3. El paquete se **ancla** en el progreso la primera vez que se consulta ese
   día. Así, completar una lección a media mañana no reordena el resto del día.
4. Las categorías marcadas como "dominadas" bajan al final del paquete, pero
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


def _ruleta(categorias: list[str]) -> list[str]:
    """Secuencia cíclica donde cada categoría ocupa tantas plazas como su frecuencia.

    Las apariciones de una categoría se reparten a intervalos regulares dentro
    del ciclo —la i-ésima de una categoría de frecuencia `f` va en la posición
    `(i + desplazamiento) / f`— de modo que una categoría de frecuencia 4 queda
    distribuida por el ciclo en vez de agrupada al principio. El
    desplazamiento, derivado del orden de presentación, separa entre sí a las
    categorías que comparten frecuencia para que no caigan en el mismo punto.
    """
    marcas: list[tuple[float, int, str]] = []
    total = len(categorias) or 1
    for idx, cat in enumerate(categorias):
        f = max(1, int(CATEGORIES[cat].get("frecuencia", 1)))
        for i in range(f):
            marcas.append(((i + idx / total) / f, CATEGORIES[cat]["orden"], cat))
    marcas.sort()
    return [cat for _, _, cat in marcas]


def _orden_del_dia(prioritarias: list[str], hoy: str, tope: int) -> list[str]:
    """Categorías del día, de mayor a menor prioridad, según la ruleta ponderada.

    Del ciclo se toman `tope` posiciones **separadas entre sí**, no consecutivas:
    así un día no se lleva tres categorías contiguas de la ruleta y el paquete
    sale variado. El punto de partida avanza una plaza por día, lo que recorre
    el ciclo completo y mantiene las proporciones a medio plazo. Detrás van las
    plazas restantes como reserva, para que una categoría sin lecciones
    pendientes ceda su sitio en lugar de dejar el día corto.
    """
    ruleta = _ruleta(prioritarias)
    if not ruleta:
        return []

    desfase = date.fromisoformat(hoy).toordinal() % len(ruleta)
    salto = max(1, len(ruleta) // max(1, tope))

    elegidas: list[str] = []
    usadas: set[int] = set()
    for k in range(max(1, tope)):
        pos = (desfase + k * salto) % len(ruleta)
        usadas.add(pos)
        # Una categoría ocupa varias plazas del ciclo, así que dos posiciones
        # distintas pueden caer en la misma: se descarta la repetida y su hueco
        # lo cubre la reserva. Sin esto el paquete serviría dos lecciones de
        # Economía el mismo día y en pantalla parecería un error.
        if ruleta[pos] not in elegidas:
            elegidas.append(ruleta[pos])

    reserva: list[str] = []
    for i in range(len(ruleta)):
        pos = (desfase + i) % len(ruleta)
        cat = ruleta[pos]
        if pos not in usadas and cat not in elegidas and cat not in reserva:
            reserva.append(cat)
    return elegidas + reserva


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
    paquete: list[str] = []

    if not tope:
        # Sin tope caben todas, así que se sirve una lección de cada categoría
        # activa y la frecuencia no interviene: solo decide a quién le toca
        # cuando hay que repartir plazas escasas.
        for cat in prioritarias + secundarias:
            for _ in range(max(1, CATEGORIES[cat].get("por_dia", 1))):
                lid = _siguiente_pendiente(banco, cat, completadas, set(paquete))
                if lid:
                    paquete.append(lid)
        return paquete

    # Con tope manda la ruleta ponderada. Las dominadas quedan siempre al final,
    # detrás incluso de la reserva.
    for cat in _orden_del_dia(prioritarias, hoy, tope) + secundarias:
        if len(paquete) >= tope:
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
