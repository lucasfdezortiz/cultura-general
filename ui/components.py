"""Piezas visuales reutilizables. Solo renderizan: no deciden nada."""

from __future__ import annotations

import html
from datetime import date

import streamlit as st

from config.categories import CATEGORIES, color, icono, nombre
from core import progress as prog_mod

MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]
DIAS_SEM = ["L", "M", "X", "J", "V", "S", "D"]


def _e(texto: str) -> str:
    """Escapa contenido antes de meterlo en el HTML de una plantilla."""
    return html.escape(str(texto or ""), quote=True)


def fecha_larga(d: date) -> str:
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


# --------------------------------------------------------------------------

def cabecera(hoy: date) -> None:
    st.markdown(
        f"""<div class="cabecera">
              <div class="marca">Sophia <em>LF</em></div>
              <div class="fecha">{_e(fecha_larga(hoy))}</div>
            </div>""",
        unsafe_allow_html=True,
    )


def sellos_racha(prog: dict, hoy: date, dias: int = 7) -> None:
    actual = prog_mod.racha_actual(prog, hoy)
    maxima = prog_mod.racha_maxima(prog, hoy)

    piezas = []
    for fecha_iso, estado in prog_mod.ultimos_dias(prog, dias, hoy):
        d = date.fromisoformat(fecha_iso)
        clases = f"sello {estado}" + (" hoy" if d == hoy else "")
        piezas.append(f'<div class="{clases}">{DIAS_SEM[d.weekday()]}</div>')

    plural = "días" if actual != 1 else "día"
    st.markdown(
        f"""<div class="sellos">
              {''.join(piezas)}
              <span class="racha-txt">Racha <b>{actual}</b> {plural} · máxima <b>{maxima}</b></span>
            </div>""",
        unsafe_allow_html=True,
    )


def medidor(etiqueta: str, hechas: int, total: int, sufijo: str = "") -> None:
    pct = (hechas / total * 100) if total else 0.0
    st.markdown(
        f"""<div class="medidor">
              <div class="medidor-fila">
                <span class="etiq">{_e(etiqueta)}</span>
                <span class="cifra">{hechas} / {total}{_e(sufijo)} · {pct:.0f}%</span>
              </div>
              <div class="pista"><div class="relleno" style="width:{min(pct, 100):.1f}%"></div></div>
            </div>""",
        unsafe_allow_html=True,
    )


def rotulo(texto: str) -> None:
    st.markdown(f'<div class="rotulo">{_e(texto)}</div>', unsafe_allow_html=True)


def tarjeta_portada(leccion: dict, hecha: bool) -> None:
    cat = leccion["category"]
    url = (leccion.get("cover_image") or {}).get("url")
    fondo = (
        f"background-image:url('{_e(url)}');"
        if url
        else f"background:linear-gradient(145deg,{color(cat)},{color(cat)}bb);"
    )
    etiqueta = "Completada" if hecha else "Pendiente"
    st.markdown(
        f"""<div class="tarjeta-portada {'hecha' if hecha else ''}" style="{fondo}">
              <div class="tp-estado {'hecha' if hecha else 'pendiente'}">{etiqueta}</div>
              <div class="tp-cuerpo">
                <div class="tp-eyebrow">{icono(cat)} {_e(nombre(cat))}</div>
                <div class="tp-titulo">{_e(leccion['title'])}</div>
              </div>
            </div>""",
        unsafe_allow_html=True,
    )


def portada_grande(leccion: dict) -> None:
    cover = leccion.get("cover_image") or {}
    url = cover.get("url")
    if url:
        st.markdown(
            f'<img class="portada-grande" src="{_e(url)}" alt="{_e(leccion["title"])}">',
            unsafe_allow_html=True,
        )
        credito, fuente = cover.get("credit"), cover.get("source_url")
        if credito:
            texto = _e(credito)
            if cover.get("license"):
                texto += f" · {_e(cover['license'])}"
            enlace = f'<a href="{_e(fuente)}" target="_blank">{texto}</a>' if fuente else texto
            st.markdown(f'<div class="credito">{enlace}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="credito">Wikimedia Commons</div>', unsafe_allow_html=True)
    else:
        cat = leccion["category"]
        st.markdown(
            f"""<div class="portada-grande" style="background:linear-gradient(145deg,{color(cat)},{color(cat)}aa);
                 display:grid;place-items:center;font-size:2.6rem;color:#FBF9F5;">{icono(cat)}</div>
                <div class="credito">&nbsp;</div>""",
            unsafe_allow_html=True,
        )


def puntos(indice: int, total: int) -> None:
    piezas = "".join(
        f'<div class="punto {"on" if i == indice else ""}"></div>' for i in range(total)
    )
    st.markdown(f'<div class="puntos">{piezas}</div>', unsafe_allow_html=True)


def tarjeta_contenido(tarjeta: dict) -> None:
    st.markdown(
        f"""<div class="tarjeta">
              <div class="tarjeta-heading">{_e(tarjeta.get('heading', ''))}</div>
              <div class="tarjeta-texto">{_e(tarjeta.get('text', ''))}</div>
            </div>""",
        unsafe_allow_html=True,
    )


def dato_clave(texto: str) -> None:
    st.markdown(
        f"""<div class="dato-clave">
              <div class="etiq">Dato clave</div>
              <div class="txt">{_e(texto)}</div>
            </div>""",
        unsafe_allow_html=True,
    )


def veredicto(acierto: bool, nota: str, correcta: str) -> None:
    # La opción correcta ya aparece marcada en verde encima, así que repetirla
    # aquí sobra: la caja solo aporta la explicación.
    cabeza = "Correcto" if acierto else "Incorrecto"
    cuerpo = nota
    st.markdown(
        f"""<div class="veredicto {'bien' if acierto else 'mal'}">
              <div class="cabeza">{cabeza}</div>
              <div class="nota">{_e(cuerpo)}</div>
            </div>""",
        unsafe_allow_html=True,
    )


def marcador(aciertos: int, total: int) -> None:
    frases = {
        4: "Dominado. Esta ya es tuya.",
        3: "Sólido. Se te ha quedado lo importante.",
        2: "A medias. Merece un repaso.",
        1: "Poco ha calado. Vuelve a las tarjetas.",
        0: "Empezamos de cero con esta.",
    }
    st.markdown(
        f"""<div class="marcador">
              <div class="num">{aciertos}</div>
              <div class="de">de {total} respuestas correctas</div>
              <div class="frase">{_e(frases.get(aciertos, ''))}</div>
            </div>""",
        unsafe_allow_html=True,
    )


def fila_historial(leccion: dict, resultado: dict) -> None:
    url = (leccion.get("cover_image") or {}).get("url")
    cat = leccion["category"]
    miniatura = (
        f'<img src="{_e(url)}" alt="">'
        if url
        else f'<div class="ph" style="background:{color(cat)}22">{icono(cat)}</div>'
    )
    st.markdown(
        f"""<div class="fila-hist">
              {miniatura}
              <div class="meta">
                <div class="t">{_e(leccion['title'])}</div>
                <div class="s">{_e(nombre(cat))} · {_e(resultado.get('fecha', ''))}</div>
              </div>
              <div class="sc">{resultado.get('aciertos', 0)}/{resultado.get('total', 4)}</div>
            </div>""",
        unsafe_allow_html=True,
    )


def vacio(texto: str) -> None:
    st.markdown(f'<div class="vacio">{_e(texto)}</div>', unsafe_allow_html=True)


def aviso_banco(salud: dict) -> None:
    if not salud["avisos"]:
        return
    nombres = ", ".join(CATEGORIES[c]["nombre"] for c in salud["avisos"])
    st.markdown(
        f"""<div class="aviso-banco">
              <b>El banco se está agotando.</b> Quedan menos de {salud['umbral']} días en:
              {_e(nombres)}. Pídele a Claude una tanda nueva para estas categorías.
            </div>""",
        unsafe_allow_html=True,
    )
