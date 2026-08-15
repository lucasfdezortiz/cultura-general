"""Sophia LF — banco de conocimiento diario.

Cero llamadas a IA en tiempo de ejecución: la app solo lee `data/lessons_bank.json`
y escribe el progreso. El banco se amplía desde Claude Code, no desde aquí.
"""

from __future__ import annotations


import streamlit as st

st.set_page_config(
    page_title="LF Global Capital",
    page_icon="◆",
    layout="centered",
    initial_sidebar_state="collapsed",
)

from core import bank as bank_mod  # noqa: E402
from core.fechas import hoy as hoy_local  # noqa: E402
from core import progress as prog_mod  # noqa: E402
from ui import components as c  # noqa: E402
from ui import screens  # noqa: E402
from ui.styles import inyectar, tema_valido  # noqa: E402

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
    inicializar()

    prog = st.session_state.prog
    # El tema se resuelve antes de pintar nada: así no hay parpadeo claro→oscuro.
    inyectar(tema_valido(prog.get("tema")))

    banco = cargar_banco_cacheado()
    hoy = hoy_local()

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

    # El aviso de persistencia va en la pantalla principal, no solo en el
    # sidebar: si el progreso no se está guardando hay que verlo sin tener que
    # abrir nada, porque cada redespliegue borraría la racha.
    from core.storage import en_streamlit_cloud, obtener_backend

    if en_streamlit_cloud() and obtener_backend().nombre != "gist":
        st.error(
            "**El progreso no se está guardando.** Esta app corre en Streamlit "
            "Cloud, cuyo disco se borra en cada reinicio o actualización. "
            "Configura `github_token` y `gist_id` en Settings → Secrets "
            "(instrucciones en DESPLIEGUE.md, paso 3).",
        )
    elif st.session_state.get("guardado_ok") is False:
        st.warning(
            "**No se ha podido guardar el último avance.** Revisa que el token "
            "del Gist siga siendo válido y tenga permiso de Gists.",
        )

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
