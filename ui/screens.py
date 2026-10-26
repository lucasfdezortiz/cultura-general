"""Pantallas de la aplicación.

Flujo:  hoy → lección → quiz → resultado → hoy

El estado vive en `st.session_state`; estas funciones lo leen, lo mutan a
través de `core.progress` y piden un rerun. Nada de lógica de selección aquí.
"""

from __future__ import annotations

from datetime import date

import streamlit as st

from config.categories import (
    CATEGORIES,
    categorias_ordenadas,
    frecuencia,
    icono,
    nombre,
    ticker,
)
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


PESTANAS = (("hoy", "Hoy"), ("biblioteca", "Biblioteca"), ("avance", "Avance"))


def nav_inferior(activa: str) -> None:
    """Tres pestañas ancladas al borde inferior de la ventana.

    Streamlit no tiene navegación fija, así que son botones en una fila de
    columnas que el CSS fija abajo (ver .marca-nav en ui/styles.py). El
    marcador va dentro de la primera columna para quedar en el mismo bloque
    horizontal al que apunta el selector.
    """
    columnas = st.columns(len(PESTANAS), gap="small")
    for i, (col, (clave, etiqueta)) in enumerate(zip(columnas, PESTANAS)):
        with col:
            if i == 0:
                st.markdown('<div class="marca-nav"></div>', unsafe_allow_html=True)
            if st.button(
                etiqueta,
                key=f"nav_{clave}",
                type="primary" if clave == activa else "secondary",
                width="stretch",
            ):
                st.session_state.pestana = clave
                st.rerun()


def persistir() -> None:
    """Guarda el progreso y deja constancia si el guardado falla.

    Sin esto, un Gist inaccesible o un token caducado harían perder la lección
    recién completada sin que nada lo indicara.
    """
    st.session_state.guardado_ok = prog_mod.guardar(st.session_state.prog)


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
        st.markdown("### Ritmo diario")
        n_activas = len(prog_mod.categorias_activas(prog))
        tope_actual = prog_mod.max_por_dia(prog)
        tope = st.slider(
            "Lecciones por día",
            min_value=0,
            max_value=max(n_activas, 1),
            value=min(tope_actual, n_activas),
            help="0 = todas las categorías activas cada día.",
            key="tope_dia",
        )
        if tope != tope_actual:
            prog_mod.fijar_max_por_dia(prog, tope)
            persistir()
            st.rerun()
        if tope:
            # El reparto es ponderado por frecuencia, no por turnos iguales, así
            # que no hay un "cada N días" común a todas. Se anuncia el ritmo de
            # las que más salen y el de las que menos, que es la información
            # que de verdad describe lo que el usuario va a ver.
            activas = prog_mod.categorias_activas(prog)
            suma = sum(frecuencia(c) for c in activas) or 1
            ritmos = {c: suma / (tope * frecuencia(c)) for c in activas}
            mas, menos = min(ritmos, key=ritmos.get), max(ritmos, key=ritmos.get)
            st.caption(
                f"{tope} de {n_activas} categorías al día, repartidas por peso: "
                f"{nombre(mas)} sale una vez cada {ritmos[mas]:.0f} días "
                f"y {nombre(menos)} cada {ritmos[menos]:.0f}. "
                f"Unas {tope * 4} preguntas por jornada."
            )
        else:
            st.caption(
                f"Las {n_activas} categorías cada día, unas {n_activas * 4} preguntas."
            )

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

            # La casilla se renderiza SIEMPRE, deshabilitada si la categoría
            # está apagada. Si se deja de dibujar al desactivarla, Streamlit
            # 1.6x lanza KeyError sobre el widget huérfano al siguiente rerun.
            dom = st.checkbox(
                "Dominada (baja prioridad)",
                value=cat_id in dominadas,
                key=f"dom_{cat_id}",
                disabled=not activa,
            )
            if activa and dom != (cat_id in dominadas):
                prog_mod.alternar_dominada(prog, cat_id, dom)
                cambio = True
            if activa:
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

        from core.storage import en_streamlit_cloud, obtener_backend

        backend = obtener_backend().nombre
        if backend == "gist":
            st.caption("Progreso guardado en Gist privado.")
        elif en_streamlit_cloud():
            # Disco efímero y sin Gist: el progreso se perderá en el próximo
            # reinicio. Hay que decirlo alto, no en un pie de página gris.
            st.error(
                "**El progreso NO se está guardando.** La app corre en "
                "Streamlit Cloud, donde el disco se borra al reiniciarse. "
                "Añade `github_token` y `gist_id` en Settings → Secrets.",
            )
        else:
            st.caption(
                "Progreso en archivo local. Añade `github_token` y `gist_id` "
                "a los secrets para que sobreviva a los reinicios."
            )


# --------------------------------------------------------------------------
# Pantalla: hoy
# --------------------------------------------------------------------------

def tab_hoy(banco: dict, prog: dict, hoy: date, salud: dict) -> None:
    """Paquete del día: una lección protagonista y el resto en filas."""
    hoy_iso = hoy.isoformat()
    paquete, cambio = selection.paquete_del_dia(banco, prog, hoy_iso)
    if cambio:
        persistir()

    completadas = prog_mod.ids_completadas(prog)
    estado = selection.estado_paquete(prog, paquete, hoy_iso)

    c.saludo(hoy, estado, prog_mod.racha_actual(prog, hoy))
    if estado["total"]:
        c.progreso_dia(estado)

    if not paquete:
        c.vacio(
            "No quedan lecciones pendientes en las categorías activas. "
            "Activa otra categoría o pide una tanda nueva."
        )
        c.aviso_banco(salud)
        return

    pendientes = [i for i in paquete if i not in completadas]
    hechas = [i for i in paquete if i in completadas]

    if pendientes:
        principal, resto = pendientes[0], pendientes[1:]
        c.hero_leccion(banco["lecciones"][principal])
        if st.button(
            "Empezar", key=f"hero_{principal}", type="primary", width="stretch"
        ):
            abrir_leccion(principal)
    else:
        resto = []
        st.success("Paquete de hoy completado. El sello del día queda lleno.")

    if resto:
        c.rotulo("También hoy")
        _lista_lecciones(banco, resto, prefijo="fila")

    if hechas:
        c.rotulo("Ya hechas hoy")
        _lista_lecciones(banco, hechas, prefijo="rep", prog=prog)

    if estado["cerrado"]:
        siguiente = selection.siguiente_extra(banco, prog, hoy_iso)
        if siguiente:
            c.rotulo("Seguir aprendiendo")
            st.caption(
                "Suma al porcentaje completado, pero no afecta al sello del día."
            )
            _lista_lecciones(banco, [siguiente], prefijo="extra", extra=True)

    c.aviso_banco(salud)


def _lista_lecciones(
    banco: dict,
    ids: list[str],
    prefijo: str,
    prog: dict | None = None,
    extra: bool = False,
) -> None:
    """Filas tocables de lección. El contenedor acota el CSS a esta lista."""
    with st.container():
        st.markdown('<div class="mk-lista"></div>', unsafe_allow_html=True)
        for lid in ids:
            leccion = banco["lecciones"].get(lid)
            if not leccion:
                continue
            # El ticker va como código en línea: Streamlit lo renderiza en un
            # <code> al que el CSS da forma de chip dentro del propio botón.
            etiqueta = f"`{ticker(leccion['category'])}`  {leccion['title']}"
            if prog is not None:
                r = prog_mod.resultado(prog, lid) or {}
                etiqueta += f"  ·  {r.get('aciertos', 0)}/{r.get('total', 4)}"
            if st.button(etiqueta, key=f"{prefijo}_{lid}", width="stretch"):
                abrir_leccion(lid, extra=extra)


# --------------------------------------------------------------------------
# Pestaña: biblioteca
# --------------------------------------------------------------------------

def tab_biblioteca(banco: dict, prog: dict, hoy: date) -> None:
    c.cabecera(hoy)
    st.markdown('<div class="saludo">Biblioteca</div>', unsafe_allow_html=True)

    completadas = prog_mod.ids_completadas(prog)

    # Lección a medias: la que se abrió y aún no tiene resultado registrado.
    en_curso = st.session_state.get("leccion_id")
    if en_curso and en_curso in banco["lecciones"] and en_curso not in completadas:
        leccion = banco["lecciones"][en_curso]
        c.rotulo("Continúa donde lo dejaste")
        c.continuar_card(
            leccion,
            st.session_state.get("tarjeta_idx", 0) + 1,
            len(leccion.get("cards", [])) or 1,
        )
        if st.button("Reanudar", key="reanudar", type="primary", width="stretch"):
            ir_a("leccion")

    busqueda = st.text_input(
        "Buscar",
        placeholder="Buscar una lección…",
        label_visibility="collapsed",
        key="buscar_biblio",
    ).strip().lower()

    if not completadas:
        c.vacio("Todavía no has completado ninguna lección.")
        return

    grupos = prog_mod.historial_por_categoria(prog, banco)
    c.rotulo("Lecciones completadas, por tema")

    hubo = False
    for cat_id, _meta in categorias_ordenadas():
        entradas = grupos.get(cat_id, [])
        if busqueda:
            entradas = [e for e in entradas if busqueda in e[0].get("title", "").lower()]
        if not entradas:
            continue
        hubo = True
        en_banco = len(banco["por_categoria"].get(cat_id, []))
        c.cabecera_categoria(
            cat_id, len(entradas), en_banco, prog_mod.accuracy_categoria(entradas)
        )
        for leccion, resultado in entradas:
            c.fila_historial(leccion, resultado)

    if not hubo:
        c.vacio(
            f"Ninguna lección completada coincide con «{busqueda}»."
            if busqueda
            else "Todavía no has completado ninguna lección."
        )


# --------------------------------------------------------------------------
# Pestaña: avance
# --------------------------------------------------------------------------

def tab_avance(banco: dict, prog: dict, hoy: date) -> None:
    c.cabecera(hoy)
    st.markdown('<div class="saludo">Tu avance</div>', unsafe_allow_html=True)

    completadas = prog_mod.ids_completadas(prog)
    stats = bank_mod.estadisticas(banco, completadas)
    hoy_iso = hoy.isoformat()
    paquete = prog["dias"].get(hoy_iso, {}).get("paquete", [])
    estado = selection.estado_paquete(prog, paquete, hoy_iso)

    c.panel_metricas(prog, hoy, stats, estado)
    c.racha_barras(prog, hoy)

    if not completadas:
        c.vacio("Completa una lección y aquí verás tu avance por categoría.")
        return

    grupos = prog_mod.historial_por_categoria(prog, banco)
    c.rotulo("Avance por categoría")
    filas = []
    for cat_id, _meta in categorias_ordenadas():
        s = stats["por_categoria"].get(cat_id, {})
        if not s.get("total"):
            continue
        filas.append({
            "id": cat_id,
            "hechas": s["completadas"],
            "total": s["total"],
            "pct": s["pct"],
            "accuracy": prog_mod.accuracy_categoria(grupos.get(cat_id, [])),
        })
    c.tabla_categorias(filas)


# --------------------------------------------------------------------------
# Pantalla: lección
# --------------------------------------------------------------------------

def _barra_superior(
    llenos: int, total: int, key: str, ok: bool = False, texto: str | None = None
) -> None:
    """Cerrar a la izquierda, progreso por tramos a la derecha.

    `llenos` son los tramos ya pintados y `texto` lo que dice el contador. Se
    separan porque en el quiz no coinciden: al abrir la pregunta 1 no hay
    ninguna respondida, pero el contador debe decir 1/4 y no 0/4.
    """
    izq, der = st.columns([0.17, 1], gap="small")
    with izq:
        st.markdown('<div class="barra-sup"></div>', unsafe_allow_html=True)
        if st.button("✕", key=key, help="Volver al paquete"):
            ir_a("hoy")
    with der:
        cuenta = texto or f"{llenos}/{total}"
        st.markdown(
            f'<div class="seg-fila">{c.segmentos(llenos, total, cuenta, ok)}</div>',
            unsafe_allow_html=True,
        )


def pantalla_leccion(banco: dict, prog: dict) -> None:
    leccion = banco["lecciones"].get(st.session_state.leccion_id)
    if not leccion:
        ir_a("hoy")
        return

    tarjetas = leccion.get("cards", [])
    idx = min(st.session_state.get("tarjeta_idx", 0), len(tarjetas) - 1)
    ya_hecha = prog_mod.esta_completada(prog, leccion["id"])

    _barra_superior(idx + 1, len(tarjetas), "cerrar_lec")

    c.portada_grande(leccion)

    # El título completo solo en la primera tarjeta: a partir de ahí estorba,
    # y basta con un recordatorio tenue de qué se está leyendo.
    if idx == 0:
        st.markdown(
            f'<div class="leccion-titulo">{c._e(leccion["title"])}</div>'
            f'<div class="leccion-subtitulo">{c._e(leccion["subtitle"])}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="leccion-rotulo">{c._e(leccion["title"])}</div>',
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
        # 'nav-compacta' impide que esta fila se apile en móvil (ui/styles.py).
        st.markdown(
            f'<div class="nav-compacta contador-tarjeta">{idx + 1} de {len(tarjetas)}</div>',
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
            if st.button(
                "Continuar al quiz", key="ir_quiz", type="primary", width="stretch"
            ):
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
    acierto = revelada and respuestas[idx] == pregunta["correct"]

    _barra_superior(
        idx + (1 if revelada else 0),
        len(preguntas),
        "cerrar_quiz",
        ok=acierto,
        texto=f"{idx + 1}/{len(preguntas)}",
    )

    st.markdown(
        c.chip(leccion["category"])
        + f'<div class="quiz-pregunta">{c._e(pregunta["q"])}</div>',
        unsafe_allow_html=True,
    )

    if not revelada:
        with st.container():
            st.markdown('<div class="mk-opciones"></div>', unsafe_allow_html=True)
            for i, opcion in enumerate(pregunta["options"]):
                etiqueta = f"`{c.LETRAS[i]}`  {opcion}"
                if st.button(
                    etiqueta, key=f"op_{leccion['id']}_{idx}_{i}", width="stretch"
                ):
                    st.session_state.respuestas = respuestas + [i]
                    st.session_state.revelada = True
                    st.rerun()
        st.markdown(
            '<div class="quiz-ayuda">Toca una respuesta para comprobarla</div>',
            unsafe_allow_html=True,
        )
    else:
        elegida = respuestas[idx]
        correcta = pregunta["correct"]
        for i, opcion in enumerate(pregunta["options"]):
            if i == correcta:
                estado = "ok"
            elif i == elegida:
                estado = "ko"
            else:
                estado = "tenue"
            c.opcion_revelada(opcion, estado, i)

        c.veredicto(elegida == correcta, pregunta.get("note", ""), pregunta["options"][correcta])

        ultima = idx == len(preguntas) - 1
        if st.button(
            "Ver resultado" if ultima else "Siguiente pregunta",
            key=f"sig_{idx}",
            type="primary",
            width="stretch",
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
    cat = leccion["category"]

    c.cierre(leccion, aciertos, total)
    c.tiles_cierre(aciertos, total, prog_mod.racha_actual(prog, hoy))

    completadas = prog_mod.ids_completadas(prog)
    ids_cat = banco["por_categoria"].get(cat, [])
    c.avance_categoria(cat, sum(1 for i in ids_cat if i in completadas), len(ids_cat))

    hoy_iso = hoy.isoformat()
    paquete = prog["dias"].get(hoy_iso, {}).get("paquete", [])
    estado = selection.estado_paquete(prog, paquete, hoy_iso)
    c.aviso_dia(estado)

    siguiente = selection.siguiente_pendiente_del_paquete(prog, paquete)
    if siguiente:
        if st.button(
            "Siguiente lección", key="res_siguiente", type="primary", width="stretch"
        ):
            abrir_leccion(siguiente, extra=False)
    else:
        extra = selection.siguiente_extra(banco, prog, hoy_iso)
        if extra and st.button(
            "Seguir aprendiendo", key="res_extra", type="primary", width="stretch"
        ):
            abrir_leccion(extra, extra=True)

    if st.button("Volver al paquete", key="res_volver", width="stretch"):
        ir_a("hoy")
