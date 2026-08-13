"""Sophia LF — banco de conocimiento diario.

Cero llamadas a IA en tiempo de ejecución: la app solo lee `data/lessons_bank.json`
y escribe el progreso. El banco se amplía desde Claude Code, no desde aquí.
"""

from __future__ import annotations

from datetime import date

import streamlit as st

st.set_page_config(
    page_title="Sophia LF",
    page_icon="◆",
    layout="centered",
    initial_sidebar_state="collapsed",
)

from core import bank as bank_mod  # noqa: E402
from core import progress as prog_mod  # noqa: E402
from ui import components as c  # noqa: E402
from ui import screens  # noqa: E402
from ui.styles import inyectar  # noqa: E402

ESTADO_INICIAL = {
    "pantalla": "hoy",
    "leccion_id": None,
    "tarjeta_idx": 0,
    "quiz_idx": 0,
    "respuestas": [],
    "revelada": False,
    "es_extra": False,
}


@st.cache_data(show_spinner=False)
def cargar_banco_cacheado() -> dict:
    return bank_mod.cargar_banco()


def inicializar() -> None:
    for clave, valor in ESTADO_INICIAL.items():
        st.session_state.setdefault(clave, valor)
    if "prog" not in st.session_state:
        st.session_state.prog = prog_mod.cargar()


def main() -> None:
    inyectar()
    inicializar()

    banco = cargar_banco_cacheado()
    prog = st.session_state.prog
    hoy = date.today()

    if not banco["lecciones"]:
        c.cabecera(hoy)
        c.vacio(
            "El banco está vacío. Genera lecciones en data/lessons_bank.json "
            "y valida con: python scripts/validate_bank.py"
        )
        return

    salud = bank_mod.check_bank_health(
        banco, prog_mod.ids_completadas(prog), prog_mod.categorias_activas(prog)
    )
    screens.sidebar(banco, prog, salud)

    c.cabecera(hoy)

    pantalla = st.session_state.pantalla
    if pantalla == "leccion":
        screens.pantalla_leccion(banco, prog)
    elif pantalla == "quiz":
        screens.pantalla_quiz(banco, prog, hoy)
    elif pantalla == "resultado":
        screens.pantalla_resultado(banco, prog, hoy)
    else:
        screens.pantalla_hoy(banco, prog, hoy)
        c.aviso_banco(salud)


if __name__ == "__main__":
    main()
