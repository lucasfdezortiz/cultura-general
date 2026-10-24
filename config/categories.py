"""Definición de categorías del banco de conocimiento.

`frecuencia` es el campo que decide **cuántas veces sale una categoría**. Con un
tope diario no caben todas cada día, así que las plazas se reparten en
proporción a este número: una categoría de frecuencia 4 sale cuatro veces más a
menudo que una de frecuencia 1. El reparto lo hace `core.selection._ruleta`.

`objetivo` es el tamaño de banco al que aspiramos para esa categoría, y por
tanto cuánto aguanta antes de agotarse al ritmo al que se la consume.

`por_dia` solo actúa cuando el tope diario está desactivado, caso en el que se
sirve una lección de cada categoría activa.

Reenfoque de 2026-10-24: el temario pasa a girar sobre mercados, economía e
inversión. Arte, Literatura y Mitología se fusionan en **Humanidades**, que
conserva las lecciones ya escritas y las completadas en el historial, pero baja
a frecuencia 1. Las lecciones de las tres categorías nuevas se escriben a partir
del cerebro de LF Global Capital (`wiki/` del repositorio LF Global Capital
Brain), que es material propio y ya verificado.
"""

from __future__ import annotations

CATEGORIES: dict[str, dict] = {
    "economia": {
        "nombre": "Economía y Macro",
        "frecuencia": 4,
        "objetivo": 70,
        "por_dia": 1,
        "activa": True,
        "color": "#6B5B3E",
        "icono": "▲",
        "descripcion": "Cómo se mueve el dinero y por qué los ciclos se repiten.",
        "orden": 1,
    },
    "mercados": {
        "nombre": "Mercados Financieros",
        "frecuencia": 4,
        "objetivo": 70,
        "por_dia": 1,
        "activa": True,
        "color": "#1F5C7A",
        "icono": "◧",
        "descripcion": "Cómo se forman los precios y por qué a veces dejan de informar.",
        "orden": 2,
    },
    "inversion": {
        "nombre": "Inversión y Valoración",
        "frecuencia": 4,
        "objetivo": 70,
        "por_dia": 1,
        "activa": True,
        "color": "#2F5D50",
        "icono": "◆",
        "descripcion": "Qué hace que un negocio valga lo que vale, y cuánto pagar por él.",
        "orden": 3,
    },
    "quant": {
        "nombre": "Quant y Riesgo",
        "frecuencia": 3,
        "objetivo": 50,
        "por_dia": 1,
        "activa": True,
        "color": "#4A3F63",
        "icono": "∿",
        "descripcion": "Medir el riesgo, y los límites de las medidas.",
        "orden": 4,
    },
    "geopolitica": {
        "nombre": "Geopolítica",
        "frecuencia": 2,
        "objetivo": 45,
        "por_dia": 1,
        "activa": True,
        "color": "#3D5A6C",
        "icono": "◉",
        "descripcion": "Poder, territorio y las reglas no escritas entre estados.",
        "orden": 5,
    },
    "matematicas": {
        "nombre": "Matemáticas y Estadística",
        "frecuencia": 2,
        "objetivo": 35,
        "por_dia": 1,
        "activa": True,
        "color": "#8A4A1F",
        "icono": "∑",
        "descripcion": "Contar, medir y no dejarse engañar por los números.",
        "orden": 6,
    },
    "presente": {
        "nombre": "Claves del Presente",
        "frecuencia": 1,
        "objetivo": 30,
        "por_dia": 1,
        "activa": True,
        "color": "#8A5A2B",
        "icono": "◎",
        "descripcion": "Las estructuras duraderas que hacen entender las noticias.",
        "orden": 7,
    },
    "historia": {
        "nombre": "Historia",
        "frecuencia": 1,
        "objetivo": 30,
        "por_dia": 1,
        "activa": True,
        "color": "#7A4B39",
        "icono": "■",
        "descripcion": "Decisiones, accidentes y consecuencias de largo alcance.",
        "orden": 8,
    },
    "ciencia": {
        "nombre": "Ciencia",
        "frecuencia": 1,
        "objetivo": 25,
        "por_dia": 1,
        "activa": True,
        "color": "#2F6B4F",
        "icono": "●",
        "descripcion": "Cómo sabemos lo que sabemos sobre el mundo físico.",
        "orden": 9,
    },
    "fisica": {
        "nombre": "Física",
        "frecuencia": 1,
        "objetivo": 25,
        "por_dia": 1,
        "activa": True,
        "color": "#1F6B6B",
        "icono": "◌",
        "descripcion": "Las reglas que no admiten excepción.",
        "orden": 10,
    },
    "filosofia": {
        "nombre": "Filosofía",
        "frecuencia": 1,
        "objetivo": 25,
        "por_dia": 1,
        "activa": True,
        "color": "#5A4A72",
        "icono": "◈",
        "descripcion": "Las preguntas que no se resuelven pero sí se afinan.",
        "orden": 11,
    },
    "humanidades": {
        "nombre": "Humanidades",
        "frecuencia": 1,
        "objetivo": 45,
        "por_dia": 1,
        "activa": True,
        "color": "#8C3F4D",
        "icono": "✦",
        "descripcion": "Arte, literatura y los relatos con que las culturas se explicaron.",
        "orden": 12,
    },
}

# Prefijo de id para las lecciones **nuevas** de cada categoría.
PREFIJOS: dict[str, str] = {
    "economia": "eco",
    "mercados": "mer",
    "inversion": "inv",
    "quant": "qnt",
    "geopolitica": "geo",
    "matematicas": "mat",
    "presente": "pre",
    "historia": "his",
    "ciencia": "cie",
    "fisica": "fis",
    "filosofia": "fil",
    "humanidades": "hum",
}

# Categorías retiradas y la categoría que absorbió su contenido. Los ids
# antiguos (art-0004, lit-0002, mit-0007...) **no se renombran**: hacerlo
# dejaría huérfano el historial del usuario, que guarda los ids tal cual. Este
# mapa permite seguir resolviendo la categoría de un id heredado.
CATEGORIAS_FUSIONADAS: dict[str, str] = {
    "arte": "humanidades",
    "literatura": "humanidades",
    "mitologia": "humanidades",
}

PREFIJOS_HEREDADOS: dict[str, str] = {
    "art": "humanidades",
    "lit": "humanidades",
    "mit": "humanidades",
}

# Umbral por debajo del cual avisamos de que hay que recargar el banco.
UMBRAL_DIAS_RESTANTES = 15

OBJETIVO_TOTAL = sum(c["objetivo"] for c in CATEGORIES.values())

# Las categorías cuyo contenido es el núcleo del reenfoque. Se usa para medir
# si el reparto diario sigue cumpliendo lo que se pidió.
BLOQUE_FINANCIERO = ("economia", "mercados", "inversion", "quant")


def categorias_ordenadas() -> list[tuple[str, dict]]:
    """Categorías en el orden de presentación definido."""
    return sorted(CATEGORIES.items(), key=lambda kv: kv[1]["orden"])


def nombre(cat_id: str) -> str:
    return CATEGORIES.get(cat_id, {}).get("nombre", cat_id)


def color(cat_id: str) -> str:
    return CATEGORIES.get(cat_id, {}).get("color", "#1B2A41")


def icono(cat_id: str) -> str:
    return CATEGORIES.get(cat_id, {}).get("icono", "◆")


def frecuencia(cat_id: str) -> int:
    return max(1, int(CATEGORIES.get(cat_id, {}).get("frecuencia", 1)))


def ticker(cat_id: str) -> str:
    """Código de tres letras de la categoría, al modo de un símbolo bursátil.

    Reutiliza el prefijo de los ids, de modo que el código que se ve en
    pantalla es literalmente el que llevan las lecciones de esa categoría.
    """
    return PREFIJOS.get(cat_id, cat_id[:3]).upper()


def categoria_vigente(cat_id: str) -> str | None:
    """Traduce una categoría heredada a la que la absorbió.

    Devuelve None si el nombre no corresponde a ninguna categoría, ni actual ni
    fusionada, para que quien llame decida si descartar el registro.
    """
    if cat_id in CATEGORIES:
        return cat_id
    return CATEGORIAS_FUSIONADAS.get(cat_id)
