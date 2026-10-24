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

from config.categories import (
    CATEGORIAS_FUSIONADAS,
    CATEGORIES,
    PREFIJOS,
    PREFIJOS_HEREDADOS,
    categoria_vigente,
)
from core.fechas import hoy as hoy_local
from core.storage import obtener_backend

VERSION = 2

# prefijo de id -> categoría, para recuperar la categoría de un registro
# huérfano cuya lección ya no está en el banco. Incluye los prefijos de las
# categorías fusionadas: los ids antiguos no se renombran, así que `art-0004`
# tiene que seguir resolviéndose a Humanidades.
_PREFIJO_A_CAT = {prefijo: cat for cat, prefijo in PREFIJOS.items()}
_PREFIJO_A_CAT.update(PREFIJOS_HEREDADOS)


def progreso_vacio() -> dict[str, Any]:
    return {
        "version": VERSION,
        "dias": {},
        "lecciones": {},
        "racha_maxima": 0,
        "categorias_activas": [c for c, v in CATEGORIES.items() if v["activa"]],
        "dominadas": [],
        # Debe coincidir con ui.styles.TEMA_POR_DEFECTO. No se importa de allí
        # para que `core` no dependa de `ui`: la capa de datos no debe saber
        # nada de la de presentación.
        "tema": "oscuro",
        # Con 12 categorias, servirlas todas cada dia son 48 preguntas y mas de
        # media hora. Tres es un dia sostenible y lo que el reparto ponderado
        # necesita para que el bloque financiero domine; se ajusta en el sidebar.
        "max_por_dia": 3,
    }


# Las once categorías que existían en la versión 1 del progreso. Hace falta la
# lista explícita para distinguir dos cosas que de otro modo se confunden: una
# categoría ausente de `categorias_activas` porque el usuario la desactivó —que
# no se debe reactivar— y una ausente porque aún no existía —que sí hay que dar
# de alta.
_CATEGORIAS_V1 = frozenset({
    "geopolitica", "economia", "historia", "ciencia", "filosofia", "presente",
    "fisica", "matematicas", "mitologia", "arte", "literatura",
})


def _migrar_categorias_fusionadas(data: dict[str, Any]) -> None:
    """Traduce los nombres de categoría retirados y da de alta las nuevas.

    Se ejecuta una sola vez, al subir de la version 1 a la 2. Las listas de
    categorias activas y dominadas guardan **nombres**, no ids de leccion, así
    que al fusionar Arte, Literatura y Mitologia en Humanidades hay que
    traducirlas o `categorias_activas()` las descartaria por desconocidas. Y
    como las categorias nuevas no estaban en la lista, habria que activarlas a
    mano: se dan de alta aqui las que vienen marcadas como activas.
    """
    for clave in ("categorias_activas", "dominadas"):
        traducidas: list[str] = []
        for cat in data.get(clave) or []:
            vigente = categoria_vigente(cat)
            if vigente and vigente not in traducidas:
                traducidas.append(vigente)
        data[clave] = [c for c in CATEGORIES if c in traducidas]

    # Alta de las categorias que no existian cuando se guardo este progreso.
    # Quedan fuera las de la version 1 (una ausente es una que el usuario
    # desactivo) y las que absorbieron a otras: Humanidades solo entra si venia
    # activa alguna de las tres que fusiono, cosa que resuelve el paso anterior.
    absorbentes = set(CATEGORIAS_FUSIONADAS.values())
    activas = set(data["categorias_activas"])
    nuevas = {
        c for c, v in CATEGORIES.items()
        if v["activa"] and c not in _CATEGORIAS_V1 and c not in absorbentes
    }
    if nuevas - activas:
        data["categorias_activas"] = [c for c in CATEGORIES if c in activas | nuevas]


def _soltar_paquete_sin_empezar(data: dict[str, Any]) -> None:
    """Desancla el paquete de hoy si aún no se ha tocado, para que se rehaga.

    Un paquete anclado no se recalcula nunca: es lo que impide que completar una
    lección reordene el resto del día. Pero el de hoy se armó con el reparto
    anterior, y dejarlo haría que el reenfoque pareciera no haber surtido
    efecto hasta mañana. Se suelta solo si no hay ninguna lección completada en
    él, de modo que no se pierde nada.
    """
    hoy = hoy_local().isoformat()
    dia = data.get("dias", {}).get(hoy)
    if dia and dia.get("paquete") and not dia.get("completadas"):
        del data["dias"][hoy]


def migrar(data: dict[str, Any]) -> dict[str, Any]:
    """Rellena claves que falten para tolerar progresos de versiones antiguas."""
    base = progreso_vacio()
    for clave, valor in base.items():
        data.setdefault(clave, valor)
    if int(data.get("version", 1)) < 2:
        _migrar_categorias_fusionadas(data)
        _soltar_paquete_sin_empezar(data)
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
    hoy = hoy or hoy_local()
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
    hoy = hoy or hoy_local()
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
        # `categoria_vigente` absorbe los nombres retirados, para que una
        # lección marcada como "arte" siga contando bajo Humanidades en vez de
        # abrir un grupo fantasma que la interfaz no sabría dibujar.
        cat = categoria_vigente(leccion.get("category", ""))
        if cat is None:
            continue
        grupos.setdefault(cat, []).append((leccion, resultado))

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
