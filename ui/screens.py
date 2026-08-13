"""Pantallas de la aplicación.

Flujo:  hoy → lección → quiz → resultado → hoy

El estado vive en `st.session_state`; estas funciones lo leen, lo mutan a
través de `core.progress` y piden un rerun. Nada de lógica de selección aquí.
"""

from __future__ import annotations

from datetime import date

import streamlit as st

from config.categories import CATEGORIES, categorias_ordenadas, icono, nombre
from core import bank as bank_mod
from core import progress as prog_mod
from core import selection
from ui import components as c
from ui.styles import TEMAS, tema_valido


# --------------------------------------------------------------------------
# Navegación
# --------------------------------------------------------------------------

def ir_a(pantalla: str, **extra) -> None:
    st.session_state.pantalla = pantalla
    for clave, valor in extra.items():
        st.session_state[clave] = valor
    st.rerun()


def abrir_leccion(leccion_id: str, extra: bool = False) -> None:
    ir_a(
        "leccion",
        leccion_id=leccion_id,
        tarjeta_idx=0,
        quiz_idx=0,
        respuestas=[],
        revelada=False,
        es_extra=extra,
    )


def persistir() -> None:
    prog_mod.guardar(st.session_state.prog)


# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------

def sidebar(banco: dict, prog: dict, salud: dict) -> None:
    with st.sidebar:
        st.markdown("### Apariencia")
        claves = list(TEMAS.keys())
        actual = tema_valido(prog.get("tema"))
        elegido = st.radio(
            "Tema",
            claves,
            index=claves.index(actual),
            format_func=lambda k: TEMAS[k]["nombre"],
            horizontal=True,
            label_visibility="collapsed",
            key="tema_radio",
        )
        if elegido != actual:
            prog_mod.fijar_tema(prog, elegido)
            persistir()
            st.rerun()

        st.divider()
        st.markdown("### Categorías")
        st.caption("Desactiva una y deja de aparecer en el paquete del día.")

        activas = set(prog_mod.categorias_activas(prog))
        dominadas = set(prog.get("dominadas", []))
        cambio = False

        for cat_id, meta in categorias_ordenadas():
            detalle = salud["detalle"].get(cat_id, {})
            pendientes = detalle.get("pendientes", 0)
            en_banco = len(banco["por_categoria"].get(cat_id, []))

            activa = st.toggle(
                f"{icono(cat_id)}  {meta['nombre']}",
                value=cat_id in activas,
                key=f"tg_{cat_id}",
            )
            if activa != (cat_id in activas):
                prog_mod.alternar_categoria(prog, cat_id, activa)
                cambio = True

            if activa:
                dom = st.checkbox(
                    "Dominada (baja prioridad)",
                    value=cat_id in dominadas,
                    key=f"dom_{cat_id}",
                )
                if dom != (cat_id in dominadas):
                    prog_mod.alternar_dominada(prog, cat_id, dom)
                    cambio = True
                st.caption(f"{pendientes} pendientes · {en_banco}/{meta['objetivo']} en banco")
            st.markdown("")

        if cambio:
            persistir()
            st.rerun()

        st.divider()
        st.markdown("### Banco")
        st.caption(
            f"Paquete diario completo garantizado durante "
            f"**{salud['dias_paquete_completo']} días**."
        )
        if salud["avisos"]:
            faltan = ", ".join(CATEGORIES[x]["nombre"] for x in salud["avisos"])
            st.warning(f"Recargar: {faltan}")

        from core.storage import obtener_backend

        backend = obtener_backend().nombre
        st.caption(
            "Progreso guardado en Gist privado."
            if backend == "gist"
            else "Progreso en archivo local. Añade `github_token` y `gist_id` "
            "a los secrets para que sobreviva a los reinicios."
        )


# --------------------------------------------------------------------------
# Pantalla: hoy
# --------------------------------------------------------------------------

def pantalla_hoy(banco: dict, prog: dict, hoy: date) -> None:
    hoy_iso = hoy.isoformat()
    paquete, cambio = selection.paquete_del_dia(banco, prog, hoy_iso)
    if cambio:
        persistir()

    c.sellos_racha(prog, hoy)

    completadas = prog_mod.ids_completadas(prog)
    stats = bank_mod.estadisticas(banco, completadas)
    c.medidor("Conocimiento completado", stats["completadas"], stats["total"])

    estado = selection.estado_paquete(prog, paquete, hoy_iso)

    tab_hoy, tab_hist = st.tabs(["Paquete de hoy", "Historial"])

    with tab_hoy:
        if not paquete:
            c.vacio(
                "No quedan lecciones pendientes en las categorías activas. "
                "Activa otra categoría o pide una tanda nueva."
            )
        else:
            if estado["cerrado"]:
                c.rotulo(f"Día cerrado · {estado['total']} de {estado['total']}")
                st.success("Paquete de hoy completado. El sello ya está lleno.")
            else:
                c.rotulo(
                    f"{estado['pendientes']} pendientes de {estado['total']} · "
                    "elige por dónde empezar"
                )

            columnas = st.columns(2, gap="medium")
            for i, lid in enumerate(paquete):
                leccion = banco["lecciones"].get(lid)
                if not leccion:
                    continue
                hecha = lid in completadas
                with columnas[i % 2]:
                    c.tarjeta_portada(leccion, hecha)
                    if st.button(
                        "Repasar" if hecha else "Empezar",
                        key=f"abrir_{lid}",
                        type="secondary" if hecha else "primary",
                    ):
                        abrir_leccion(lid, extra=False)
                    st.markdown("")

            if estado["cerrado"]:
                siguiente = selection.siguiente_extra(banco, prog, hoy_iso)
                st.divider()
                if siguiente:
                    c.rotulo("Seguir aprendiendo")
                    st.caption(
                        "Estas lecciones suman al porcentaje completado, pero no "
                        "afectan al sello de racha del día."
                    )
                    extra = banco["lecciones"][siguiente]
                    c.tarjeta_portada(extra, False)
                    if st.button("Continuar con esta", key="extra", type="primary"):
                        abrir_leccion(siguiente, extra=True)
                else:
                    c.vacio("No queda nada más pendiente en el banco. Toca ampliarlo.")

    with tab_hist:
        tab_historial(banco, prog)


# --------------------------------------------------------------------------
# Pantalla: lección
# --------------------------------------------------------------------------

def pantalla_leccion(banco: dict, prog: dict) -> None:
    leccion = banco["lecciones"].get(st.session_state.leccion_id)
    if not leccion:
        ir_a("hoy")
        return

    tarjetas = leccion.get("cards", [])
    idx = min(st.session_state.get("tarjeta_idx", 0), len(tarjetas) - 1)
    ya_hecha = prog_mod.esta_completada(prog, leccion["id"])

    atras, _ = st.columns([1, 2.4])
    with atras:
        if st.button("← Volver al paquete", key="volver_lec"):
            ir_a("hoy")

    st.markdown(
        f'<div class="eyebrow">{icono(leccion["category"])} {nombre(leccion["category"])}</div>',
        unsafe_allow_html=True,
    )
    c.portada_grande(leccion)
    st.markdown(
        f'<div class="leccion-titulo">{c._e(leccion["title"])}</div>'
        f'<div class="leccion-subtitulo">{c._e(leccion["subtitle"])}</div>',
        unsafe_allow_html=True,
    )

    c.tarjeta_contenido(tarjetas[idx])
    c.puntos(idx, len(tarjetas))

    izq, centro, der = st.columns([1, 1.35, 1])
    with izq:
        if st.button("Anterior", key="tarj_prev", disabled=idx == 0):
            st.session_state.tarjeta_idx = idx - 1
            st.rerun()
    with centro:
        st.markdown(
            f'<div style="text-align:center;font-size:.76rem;color:#8A909C;'
            f'padding-top:.55rem">{idx + 1} de {len(tarjetas)}</div>',
            unsafe_allow_html=True,
        )
    with der:
        if st.button("Siguiente", key="tarj_next", disabled=idx >= len(tarjetas) - 1):
            st.session_state.tarjeta_idx = idx + 1
            st.rerun()

    if idx == len(tarjetas) - 1:
        c.dato_clave(leccion.get("key_fact", ""))

        if ya_hecha:
            resultado = prog_mod.resultado(prog, leccion["id"]) or {}
            st.info(
                f"Ya completaste esta lección "
                f"({resultado.get('aciertos', 0)}/{resultado.get('total', 4)}). "
                "Puedes repasar el contenido, pero el quiz no se repite.",
            )
            if st.button("Volver al paquete", key="fin_repaso", type="primary"):
                ir_a("hoy")
        else:
            if st.button("Continuar al quiz", key="ir_quiz", type="primary"):
                ir_a("quiz", quiz_idx=0, respuestas=[], revelada=False)


# --------------------------------------------------------------------------
# Pantalla: quiz
# --------------------------------------------------------------------------

def pantalla_quiz(banco: dict, prog: dict, hoy: date) -> None:
    leccion = banco["lecciones"].get(st.session_state.leccion_id)
    if not leccion:
        ir_a("hoy")
        return

    preguntas = leccion.get("questions", [])
    idx = st.session_state.get("quiz_idx", 0)
    if idx >= len(preguntas):
        ir_a("resultado")
        return

    pregunta = preguntas[idx]
    respuestas = st.session_state.get("respuestas", [])
    revelada = st.session_state.get("revelada", False)

    st.markdown(
        f'<div class="quiz-cuenta">{icono(leccion["category"])} '
        f'{nombre(leccion["category"])} · Pregunta {idx + 1} de {len(preguntas)}</div>',
        unsafe_allow_html=True,
    )
    st.progress((idx + (1 if revelada else 0)) / len(preguntas))
    st.markdown(
        f'<div class="quiz-pregunta">{c._e(pregunta["q"])}</div>', unsafe_allow_html=True
    )

    if not revelada:
        for i, opcion in enumerate(pregunta["options"]):
            if st.button(opcion, key=f"op_{leccion['id']}_{idx}_{i}"):
                st.session_state.respuestas = respuestas + [i]
                st.session_state.revelada = True
                st.rerun()
    else:
        elegida = respuestas[idx]
        correcta = pregunta["correct"]
        for i, opcion in enumerate(pregunta["options"]):
            if i == correcta:
                estado = "ok"
            elif i == elegida:
                estado = "ko"
            else:
                estado = "neutra"
            c.opcion_revelada(opcion, estado)

        c.veredicto(elegida == correcta, pregunta.get("note", ""), pregunta["options"][correcta])

        ultima = idx == len(preguntas) - 1
        if st.button(
            "Ver resultado" if ultima else "Siguiente pregunta",
            key=f"sig_{idx}",
            type="primary",
        ):
            if ultima:
                prog_mod.registrar_leccion(
                    prog,
                    leccion["id"],
                    st.session_state.respuestas,
                    [p["correct"] for p in preguntas],
                    hoy.isoformat(),
                    extra=st.session_state.get("es_extra", False),
                )
                persistir()
                ir_a("resultado")
            else:
                st.session_state.quiz_idx = idx + 1
                st.session_state.revelada = False
                st.rerun()


# --------------------------------------------------------------------------
# Pantalla: resultado
# --------------------------------------------------------------------------

def pantalla_resultado(banco: dict, prog: dict, hoy: date) -> None:
    leccion = banco["lecciones"].get(st.session_state.leccion_id)
    if not leccion:
        ir_a("hoy")
        return

    resultado = prog_mod.resultado(prog, leccion["id"]) or {}
    aciertos = resultado.get("aciertos", 0)
    total = resultado.get("total", len(leccion.get("questions", [])))

    st.markdown(
        f'<div class="eyebrow">{icono(leccion["category"])} {nombre(leccion["category"])}</div>'
        f'<div class="leccion-titulo">{c._e(leccion["title"])}</div>',
        unsafe_allow_html=True,
    )
    c.marcador(aciertos, total)
    st.divider()

    hoy_iso = hoy.isoformat()
    paquete = prog["dias"].get(hoy_iso, {}).get("paquete", [])
    estado = selection.estado_paquete(prog, paquete, hoy_iso)

    if estado["cerrado"]:
        st.success(
            f"Paquete de hoy completado: {estado['total']} de {estado['total']}. "
            "El sello del día queda lleno.",
        )
    else:
        st.info(
            f"Te quedan {estado['pendientes']} lecciones para cerrar el día.",
        )

    completadas = prog_mod.ids_completadas(prog)
    stats = bank_mod.estadisticas(banco, completadas)
    c.medidor("Conocimiento completado", stats["completadas"], stats["total"])

    izq, der = st.columns(2)
    with izq:
        if st.button("Volver al paquete", key="res_volver", type="primary"):
            ir_a("hoy")
    with der:
        siguiente = selection.siguiente_pendiente_del_paquete(prog, paquete)
        if siguiente:
            if st.button("Siguiente categoría", key="res_siguiente"):
                abrir_leccion(siguiente, extra=False)
        else:
            extra = selection.siguiente_extra(banco, prog, hoy_iso)
            if extra and st.button("Seguir aprendiendo", key="res_extra"):
                abrir_leccion(extra, extra=True)


# --------------------------------------------------------------------------
# Historial
# --------------------------------------------------------------------------

def tab_historial(banco: dict, prog: dict) -> None:
    completadas = prog_mod.ids_completadas(prog)
    if not completadas:
        c.vacio("Todavía no has completado ninguna lección.")
        return

    stats = bank_mod.estadisticas(banco, completadas)
    grupos = prog_mod.historial_por_categoria(prog, banco)

    c.rotulo("Avance por categoría")
    for cat_id, meta in categorias_ordenadas():
        s = stats["por_categoria"].get(cat_id, {})
        if not s.get("total"):
            continue
        acc = prog_mod.accuracy_categoria(grupos.get(cat_id, []))
        sufijo = f" · acierto {acc:.0f}%" if acc is not None else ""
        c.medidor(f"{icono(cat_id)} {meta['nombre']}", s["completadas"], s["total"], sufijo)

    c.rotulo("Lecciones completadas, por tema")

    # El histórico se agrupa por categoría y sobrevive a las ampliaciones del
    # banco: se conserva por id, no por posición.
    hubo_alguna = False
    for cat_id, _meta in categorias_ordenadas():
        entradas = grupos.get(cat_id, [])
        if not entradas:
            continue
        hubo_alguna = True
        en_banco = len(banco["por_categoria"].get(cat_id, []))
        c.cabecera_categoria(
            cat_id, len(entradas), en_banco, prog_mod.accuracy_categoria(entradas)
        )
        for leccion, resultado in entradas:
            c.fila_historial(leccion, resultado)

    if not hubo_alguna:
        c.vacio("Todavía no has completado ninguna lección.")
