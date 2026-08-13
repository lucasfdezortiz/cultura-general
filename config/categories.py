"""Definición de categorías del banco de conocimiento.

`peso` determina cuántas lecciones tiene la categoría en el banco objetivo, y
por tanto cuánto tarda en agotarse al ritmo de una lección por día.
`objetivo` es el tamaño de banco al que aspiramos para esa categoría.
`por_dia` permite que una categoría sirva más de una lección en el paquete
diario (por defecto 1).
"""

CATEGORIES: dict[str, dict] = {
    "geopolitica": {
        "nombre": "Geopolítica",
        "peso": 3.0,
        "objetivo": 60,
        "por_dia": 1,
        "activa": True,
        "color": "#3D5A6C",
        "icono": "◆",
        "descripcion": "Poder, territorio y las reglas no escritas entre estados.",
        "orden": 1,
    },
    "economia": {
        "nombre": "Economía y Macro",
        "peso": 3.0,
        "objetivo": 60,
        "por_dia": 1,
        "activa": True,
        "color": "#6B5B3E",
        "icono": "▲",
        "descripcion": "Cómo se mueve el dinero y por qué los ciclos se repiten.",
        "orden": 2,
    },
    "historia": {
        "nombre": "Historia",
        "peso": 3.0,
        "objetivo": 60,
        "por_dia": 1,
        "activa": True,
        "color": "#7A4B39",
        "icono": "■",
        "descripcion": "Decisiones, accidentes y consecuencias de largo alcance.",
        "orden": 3,
    },
    "ciencia": {
        "nombre": "Ciencia",
        "peso": 2.0,
        "objetivo": 40,
        "por_dia": 1,
        "activa": True,
        "color": "#2F5D50",
        "icono": "●",
        "descripcion": "Cómo sabemos lo que sabemos sobre el mundo físico.",
        "orden": 4,
    },
    "filosofia": {
        "nombre": "Filosofía",
        "peso": 2.0,
        "objetivo": 40,
        "por_dia": 1,
        "activa": True,
        "color": "#4A3F63",
        "icono": "◈",
        "descripcion": "Las preguntas que no se resuelven pero sí se afinan.",
        "orden": 7,
    },
    "presente": {
        "nombre": "Claves del Presente",
        "peso": 2.0,
        "objetivo": 40,
        "por_dia": 1,
        "activa": True,
        "color": "#8A5A2B",
        "icono": "◉",
        "descripcion": "Las estructuras duraderas que hacen entender las noticias.",
        "orden": 8,
    },
    "fisica": {
        "nombre": "Física",
        "peso": 2.0,
        "objetivo": 40,
        "por_dia": 1,
        "activa": True,
        "color": "#1F6B6B",
        "icono": "◎",
        "descripcion": "Las reglas que no admiten excepción.",
        "orden": 5,
    },
    "matematicas": {
        "nombre": "Matemáticas y Estadística",
        "peso": 2.0,
        "objetivo": 40,
        "por_dia": 1,
        "activa": True,
        "color": "#8A4A1F",
        "icono": "∑",
        "descripcion": "Contar, medir y no dejarse engañar por los números.",
        "orden": 6,
    },
    "mitologia": {
        "nombre": "Mitología",
        "peso": 1.5,
        "objetivo": 30,
        "por_dia": 1,
        "activa": True,
        "color": "#6B4A7A",
        "icono": "☾",
        "descripcion": "Los relatos con los que las culturas se explicaron el mundo.",
        "orden": 9,
    },
    "arte": {
        "nombre": "Arte",
        "peso": 1.5,
        "objetivo": 30,
        "por_dia": 1,
        "activa": True,
        "color": "#8C3F4D",
        "icono": "✦",
        "descripcion": "Qué estaba intentando resolver quien lo hizo.",
        "orden": 10,
    },
    "literatura": {
        "nombre": "Literatura",
        "peso": 1.5,
        "objetivo": 30,
        "por_dia": 1,
        "activa": True,
        "color": "#3F5A3D",
        "icono": "❖",
        "descripcion": "Libros que cambiaron la forma de contar algo.",
        "orden": 11,
    },
}

# Prefijo de id para las lecciones de cada categoría.
PREFIJOS: dict[str, str] = {
    "geopolitica": "geo",
    "economia": "eco",
    "historia": "his",
    "ciencia": "cie",
    "filosofia": "fil",
    "presente": "pre",
    "arte": "art",
    "literatura": "lit",
    "fisica": "fis",
    "matematicas": "mat",
    "mitologia": "mit",
}

# Umbral por debajo del cual avisamos de que hay que recargar el banco.
UMBRAL_DIAS_RESTANTES = 15

OBJETIVO_TOTAL = sum(c["objetivo"] for c in CATEGORIES.values())


def categorias_ordenadas() -> list[tuple[str, dict]]:
    """Categorías en el orden de presentación definido."""
    return sorted(CATEGORIES.items(), key=lambda kv: kv[1]["orden"])


def nombre(cat_id: str) -> str:
    return CATEGORIES.get(cat_id, {}).get("nombre", cat_id)


def color(cat_id: str) -> str:
    return CATEGORIES.get(cat_id, {}).get("color", "#1B2A41")


def icono(cat_id: str) -> str:
    return CATEGORIES.get(cat_id, {}).get("icono", "◆")
