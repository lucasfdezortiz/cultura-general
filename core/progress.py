"""Estado del usuario: qué ha completado, con qué acierto y desde cuándo.

Estructura de `progress.json`:

    {
      "version": 1,
      "dias": {
        "2026-08-13": {"paquete": ["geo-0001", ...], "completadas": ["geo-0001"]}
      },
      "lecciones": {
        "geo-0001": {"fecha": "2026-08-13", "aciertos": 3, "total": 4,
                      "respuestas": [0, 2, 1, 3], "extra": false}
      },
      "racha_maxima": 12,
      "categorias_activas": ["geopolitica", ...],
      "dominadas": ["arte"]
    }

La racha actual y la máxima se **calculan** a partir de `dias` en vez de
almacenarse como contador incremental: así no pueden desincronizarse si una
escritura se pierde.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from config.categories import CATEGORIES, PREFIJOS
from core.storage import obtener_backend

VERSION = 1

# prefijo de id -> categoría, para recuperar la categoría de un registro
# huérfano cuya lección ya no está en el banco.
_PREFIJO_A_CAT = {prefijo: cat for cat, prefijo in PREFIJOS.items()}


def progreso_vacio() -> dict[str, Any]:
    return {
        "version": VERSION,
        "dias": {},
        "lecciones": {},
        "racha_maxima": 0,
        "categorias_activas": [c for c, v in CATEGORIES.items() if v["activa"]],
        "dominadas": [],
        "tema": "claro",
        # Con 11 categorias, servirlas todas cada dia son 44 preguntas y unos
        # 35 minutos. Seis es un dia sostenible; se ajusta desde el sidebar.
        "max_por_dia": 6,
    }


def migrar(data: dict[str, Any]) -> dict[str, Any]:
    """Rellena claves que falten para tolerar progresos de versiones antiguas."""
    base = progreso_vacio()
    for clave, valor in base.items():
        data.setdefault(clave, valor)
    data["version"] = VERSION
    return data


def cargar() -> dict[str, Any]:
    backend = obtener_backend()
    data = backend.load()
    return migrar(data) if data else progreso_vacio()


def guardar(data: dict[str, Any]) -> bool:
    return obtener_backend().save(data)


# --------------------------------------------------------------------------
# Consultas
# --------------------------------------------------------------------------

def esta_completada(prog: dict, leccion_id: str) -> bool:
    return leccion_id in prog["lecciones"]


def ids_completadas(prog: dict) -> set[str]:
    return set(prog["lecciones"].keys())


def resultado(prog: dict, leccion_id: str) -> dict | None:
    return prog["lecciones"].get(leccion_id)


def categorias_activas(prog: dict) -> list[str]:
    activas = [c for c in prog.get("categorias_activas", []) if c in CATEGORIES]
    return activas or [c for c, v in CATEGORIES.items() if v["activa"]]


def estado_dia(prog: dict, fecha: str) -> str:
    """'vacio' | 'parcial' | 'completo' — para el sello de racha."""
    dia = prog["dias"].get(fecha)
    if not dia or not dia.get("paquete"):
        return "vacio"
    hechas = len(dia.get("completadas", []))
    if hechas == 0:
        return "vacio"
    return "completo" if hechas >= len(dia["paquete"]) else "parcial"


# --------------------------------------------------------------------------
# Racha
# --------------------------------------------------------------------------

def racha_actual(prog: dict, hoy: date | None = None) -> int:
    """Días consecutivos con el paquete completo, terminando hoy o ayer.

    Se admite que hoy esté a medias sin romper la racha: mientras el usuario
    tenga el día en curso, la racha cuenta hasta ayer.
    """
    hoy = hoy or date.today()
    if estado_dia(prog, hoy.isoformat()) == "completo":
        cursor = hoy
    else:
        cursor = hoy - timedelta(days=1)

    racha = 0
    while estado_dia(prog, cursor.isoformat()) == "completo":
        racha += 1
        cursor -= timedelta(days=1)
    return racha


def racha_maxima(prog: dict, hoy: date | None = None) -> int:
    """Máximo histórico, recalculado y contrastado con el valor almacenado."""
    fechas = sorted(f for f in prog["dias"] if estado_dia(prog, f) == "completo")
    mejor = actual = 0
    anterior: date | None = None
    for f in fechas:
        d = date.fromisoformat(f)
        actual = actual + 1 if anterior and (d - anterior).days == 1 else 1
        mejor = max(mejor, actual)
        anterior = d
    return max(mejor, prog.get("racha_maxima", 0), racha_actual(prog, hoy))


def ultimos_dias(prog: dict, n: int = 7, hoy: date | None = None) -> list[tuple[str, str]]:
    """(fecha_iso, estado) para los últimos n días, del más antiguo al de hoy."""
    hoy = hoy or date.today()
    salida = []
    for i in range(n - 1, -1, -1):
        f = (hoy - timedelta(days=i)).isoformat()
        salida.append((f, estado_dia(prog, f)))
    return salida


# --------------------------------------------------------------------------
# Mutaciones
# --------------------------------------------------------------------------

def fijar_paquete(prog: dict, fecha: str, ids: list[str]) -> dict:
    """Ancla el paquete del día para que no cambie al recargar la página."""
    dia = prog["dias"].setdefault(fecha, {"paquete": [], "completadas": []})
    dia["paquete"] = ids
    dia.setdefault("completadas", [])
    return prog


def registrar_leccion(
    prog: dict,
    leccion_id: str,
    respuestas: list[int],
    correctas: list[int],
    fecha: str,
    extra: bool = False,
) -> dict:
    """Guarda el resultado de un quiz. Idempotente: no sobrescribe un intento previo."""
    if leccion_id in prog["lecciones"]:
        return prog

    aciertos = sum(1 for r, c in zip(respuestas, correctas) if r == c)
    prog["lecciones"][leccion_id] = {
        "fecha": fecha,
        "aciertos": aciertos,
        "total": len(correctas),
        "respuestas": respuestas,
        "extra": extra,
    }

    dia = prog["dias"].setdefault(fecha, {"paquete": [], "completadas": []})
    if leccion_id in dia["paquete"] and leccion_id not in dia["completadas"]:
        dia["completadas"].append(leccion_id)

    prog["racha_maxima"] = racha_maxima(prog)
    return prog


def alternar_categoria(prog: dict, cat_id: str, activa: bool) -> dict:
    actuales = set(categorias_activas(prog))
    actuales.add(cat_id) if activa else actuales.discard(cat_id)
    prog["categorias_activas"] = [c for c in CATEGORIES if c in actuales]
    return prog


def max_por_dia(prog: dict) -> int:
    """Tope de lecciones del paquete diario. 0 significa sin tope."""
    try:
        return max(0, int(prog.get("max_por_dia", 0)))
    except (TypeError, ValueError):
        return 0


def fijar_max_por_dia(prog: dict, tope: int) -> dict:
    prog["max_por_dia"] = max(0, int(tope))
    return prog


def fijar_tema(prog: dict, tema: str) -> dict:
    prog["tema"] = tema
    return prog


def historial_por_categoria(prog: dict, banco: dict) -> dict[str, list[tuple[dict, dict]]]:
    """Lecciones completadas agrupadas por categoría, cada grupo por fecha desc.

    Tolera lecciones que ya no estén en el banco: conserva la entrada con los
    datos mínimos para que ampliar o reordenar el banco nunca borre histórico.
    """
    grupos: dict[str, list[tuple[dict, dict]]] = {c: [] for c in CATEGORIES}

    for leccion_id, resultado in prog["lecciones"].items():
        leccion = banco["lecciones"].get(leccion_id)
        if leccion is None:
            # Registro huérfano: la lección salió del banco pero el histórico
            # sigue siendo válido y debe seguir contando.
            cat = _PREFIJO_A_CAT.get(leccion_id.split("-")[0])
            if cat is None:
                continue
            leccion = {
                "id": leccion_id,
                "category": cat,
                "title": "(lección retirada del banco)",
                "cover_image": {},
            }
        grupos.setdefault(leccion["category"], []).append((leccion, resultado))

    for lista in grupos.values():
        lista.sort(key=lambda par: par[1].get("fecha", ""), reverse=True)
    return grupos


def accuracy_categoria(entradas: list[tuple[dict, dict]]) -> float | None:
    total = sum(r.get("total", 0) for _, r in entradas)
    if not total:
        return None
    return sum(r.get("aciertos", 0) for _, r in entradas) / total * 100


def alternar_dominada(prog: dict, cat_id: str, dominada: bool) -> dict:
    actuales = set(prog.get("dominadas", []))
    actuales.add(cat_id) if dominada else actuales.discard(cat_id)
    prog["dominadas"] = [c for c in CATEGORIES if c in actuales]
    return prog
