"""Piezas visuales reutilizables. Solo renderizan: no deciden nada."""

from __future__ import annotations

import html
from datetime import date

import streamlit as st

from config.categories import CATEGORIES, color, icono, nombre, ticker
from core import progress as prog_mod

MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]
MESES_CORTOS = [
    "ENE", "FEB", "MAR", "ABR", "MAY", "JUN",
    "JUL", "AGO", "SEP", "OCT", "NOV", "DIC",
]


def _e(texto: str) -> str:
    """Escapa contenido antes de meterlo en el HTML de una plantilla."""
    return html.escape(str(texto or ""), quote=True)


def fecha_larga(d: date) -> str:
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


# --------------------------------------------------------------------------

def cabecera(hoy: date) -> None:
    st.markdown(
        f"""<div class="cabecera">
              <div>
                <div class="marca">LF <em>Global Capital</em></div>
                <div class="marca-pie">Cultura de mercados · sesión diaria</div>
              </div>
              <div class="fecha">
                <b>{hoy.day:02d} {MESES_CORTOS[hoy.month - 1]}</b>
                {hoy.year}
              </div>
            </div>""",
        unsafe_allow_html=True,
    )


def panel_metricas(prog: dict, hoy: date, stats: dict, estado: dict) -> None:
    """Las cuatro cifras que resumen la sesión, al modo de un panel de mercado.

    Sustituye a la barra de progreso suelta: el mismo dato pesa más junto a los
    otros tres, y la lectura es de un vistazo en lugar de una frase.
    """
    actual = prog_mod.racha_actual(prog, hoy)
    maxima = prog_mod.racha_maxima(prog, hoy)

    aciertos = sum(r.get("aciertos", 0) for r in prog["lecciones"].values())
    preguntas = sum(r.get("total", 0) for r in prog["lecciones"].values())
    acc = (aciertos / preguntas * 100) if preguntas else None

    hechas, total_dia = estado["completadas"], estado["total"]
    dia_cerrado = estado["cerrado"]

    tarjetas = [
        {
            "etiq": "Hoy",
            "valor": f"{hechas}<small>/{total_dia}</small>" if total_dia else "—",
            "pie": "sesión cerrada" if dia_cerrado else f"{estado['pendientes']} pendientes",
            "clase_pie": "alza" if dia_cerrado else "",
            "acento": "var(--verde)" if dia_cerrado else "var(--bronce)",
        },
        {
            "etiq": "Racha",
            "valor": f"{actual}<small>d</small>",
            "pie": f"máxima {maxima}",
            "clase_pie": "",
            "acento": "var(--bronce)" if actual else "var(--borde)",
        },
        {
            "etiq": "Acierto",
            "valor": f"{acc:.0f}<small>%</small>" if acc is not None else "—",
            "pie": f"{aciertos}/{preguntas}" if preguntas else "sin datos",
            "clase_pie": "alza" if acc is not None and acc >= 80 else "",
            "acento": "var(--verde)" if acc is not None and acc >= 80 else "var(--bronce)",
        },
        {
            "etiq": "Cartera",
            "valor": f"{stats['pct']:.0f}<small>%</small>",
            "pie": f"{stats['completadas']}/{stats['total']} lecciones",
            "clase_pie": "",
            "acento": "var(--bronce)",
        },
    ]

    piezas = "".join(
        f"""<div class="metrica" style="--acento:{t['acento']}">
              <div class="metrica-etiq">{t['etiq']}</div>
              <div class="metrica-valor">{t['valor']}</div>
              <div class="metrica-pie {t['clase_pie']}">{_e(t['pie'])}</div>
            </div>"""
        for t in tarjetas
    )
    st.markdown(f'<div class="panel">{piezas}</div>', unsafe_allow_html=True)


def racha_barras(prog: dict, hoy: date, dias: int = 14) -> None:
    """Las últimas dos semanas como histograma: lleno, a medias o vacío.

    Catorce barras caben donde antes cabían siete círculos, así que se ve el
    doble de historia en menos altura.
    """
    piezas = []
    for fecha_iso, estado in prog_mod.ultimos_dias(prog, dias, hoy):
        d = date.fromisoformat(fecha_iso)
        clases = f"b d-{estado}" + (" d-hoy" if d == hoy else "")
        titulo = f"{d.day:02d}/{d.month:02d} · {estado}"
        piezas.append(f'<div class="{clases}" title="{titulo}"></div>')

    primero = (hoy.toordinal() - dias + 1)
    desde = date.fromordinal(primero)
    st.markdown(
        f"""<div class="barras">{''.join(piezas)}</div>
            <div class="barras-pie">
              <span>{desde.day:02d} {MESES_CORTOS[desde.month - 1]}</span>
              <span>Constancia · {dias} días</span>
              <span>Hoy</span>
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


def _fondo(leccion: dict) -> str:
    """Estilo de fondo de una portada: la imagen si existe, si no el color."""
    url = (leccion.get("cover_image") or {}).get("url")
    if url:
        return f"background-image:url('{_e(url)}');"
    cat = leccion["category"]
    return f"background-image:linear-gradient(145deg,{color(cat)},{color(cat)}99);"


def chip(cat_id: str) -> str:
    """El ticker de una categoría, con su color."""
    return f'<span class="tk" style="--tk-color:{color(cat_id)}">{ticker(cat_id)}</span>'


def saludo(hoy: date, estado: dict, racha: int) -> None:
    """Cabecera de la pantalla de hoy: marca, racha, titular y fecha."""
    pendientes = estado["pendientes"]
    if not estado["total"]:
        pie = "SIN LECCIONES DISPONIBLES"
    elif estado["cerrado"]:
        pie = f"{fecha_corta(hoy)} · DÍA CERRADO"
    else:
        plural = "PENDIENTES" if pendientes != 1 else "PENDIENTE"
        pie = f"{fecha_corta(hoy)} · {pendientes} DE {estado['total']} {plural}"

    st.markdown(
        f"""<div class="cabecera">
              <div>
                <div class="marca">LF <em>Global Capital</em></div>
                <div class="marca-pie">Cultura de mercados · sesión diaria</div>
              </div>
              <span class="racha-chip">▲ {racha}</span>
            </div>
            <div class="saludo">Tu sesión<br>de hoy</div>
            <div class="saludo-pie">{pie}</div>""",
        unsafe_allow_html=True,
    )


def fecha_corta(d: date) -> str:
    return f"{d.day:02d} {MESES_CORTOS[d.month - 1]}"


def segmentos(hechas: int, total: int, cuenta: str | None = None, ok: bool = False) -> str:
    """Barra de progreso por tramos. Devuelve HTML para componerlo con otros."""
    clase = "s ok" if ok else "s on"
    piezas = "".join(
        f'<div class="{clase if i < hechas else "s"}"></div>' for i in range(max(total, 1))
    )
    cola = f'<span class="seg-cuenta">{_e(cuenta)}</span>' if cuenta else ""
    return f'<div class="segmentos">{piezas}</div>{cola}'


def progreso_dia(estado: dict) -> None:
    st.markdown(
        f'<div class="seg-fila">{segmentos(estado["completadas"], estado["total"])}</div>',
        unsafe_allow_html=True,
    )


def hero_leccion(leccion: dict) -> None:
    """Tarjeta protagonista del día. El botón lo pone quien la llama.

    La tarjeta se cierra por abajo con el contenedor del botón siguiente, al
    que el CSS da el mismo fondo y el radio inferior (ver .hero-cta).
    """
    cat = leccion["category"]
    n_tarjetas = len(leccion.get("cards", []))
    n_preguntas = len(leccion.get("questions", []))
    st.markdown(
        f"""<div class="hero">
              <div class="hero-cover" style="{_fondo(leccion)}">{chip(cat)}</div>
              <div class="hero-cuerpo">
                <div class="hero-cat">{_e(nombre(cat))}</div>
                <div class="hero-titulo">{_e(leccion['title'])}</div>
                <div class="hero-meta">
                  <span>{n_tarjetas} tarjetas</span>
                  <span>·</span>
                  <span>{n_preguntas} preguntas</span>
                </div>
              </div>
            </div>
            <div class="hero-cta"></div>""",
        unsafe_allow_html=True,
    )


def mini_chip(cat_id: str) -> None:
    """Línea de categoría sobre una fila compacta del paquete."""
    st.markdown(
        f'<div class="mini-chip">{chip(cat_id)}'
        f'<span class="nom">{_e(nombre(cat_id))}</span></div>',
        unsafe_allow_html=True,
    )


def cierre(leccion: dict, aciertos: int, total: int) -> None:
    """Sello y titular de la pantalla de lección completada."""
    frases = {
        4: "Dominado. Esta ya es tuya.",
        3: "Sólido. Se te ha quedado lo importante.",
        2: "A medias. Merece un repaso.",
        1: "Poco ha calado. Vuelve a las tarjetas.",
        0: "Empezamos de cero con esta.",
    }
    st.markdown(
        f"""<div class="cierre">
              <div class="cierre-sello">✓</div>
              <div class="cierre-titulo">Lección completada</div>
              <div class="cierre-sub">{_e(leccion['title'])}</div>
            </div>""",
        unsafe_allow_html=True,
    )
    st.caption(frases.get(aciertos, ""))


def tiles_cierre(aciertos: int, total: int, racha: int) -> None:
    """Las dos cifras del cierre: acierto de este quiz y racha resultante."""
    pleno = aciertos == total
    st.markdown(
        f"""<div class="panel dos">
              <div class="metrica" style="--acento:{'var(--verde)' if pleno else 'var(--bronce)'}">
                <div class="metrica-etiq">Acierto</div>
                <div class="metrica-valor" style="color:{'var(--verde)' if pleno else 'var(--tinta)'}">
                  {aciertos}<small>/{total}</small></div>
                <div class="metrica-pie">en este quiz</div>
              </div>
              <div class="metrica" style="--acento:var(--bronce)">
                <div class="metrica-etiq">Racha</div>
                <div class="metrica-valor">{racha}<small>d</small></div>
                <div class="metrica-pie">días seguidos</div>
              </div>
            </div>""",
        unsafe_allow_html=True,
    )


def avance_categoria(cat_id: str, hechas: int, total: int) -> None:
    """Barra de avance de la categoría recién practicada."""
    pct = (hechas / total * 100) if total else 0
    st.markdown(
        f"""<div class="tabla-cat">
              <div class="cat-fila" style="--cat:{color(cat_id)}">
                {chip(cat_id)}
                <div>
                  <div class="cat-nom">{_e(nombre(cat_id))}</div>
                  <div class="cat-pista"><div class="cat-relleno"
                       style="width:{min(pct, 100):.0f}%"></div></div>
                </div>
                <div class="cat-cifras"><b>{hechas}/{total}</b></div>
              </div>
            </div>""",
        unsafe_allow_html=True,
    )


def aviso_dia(estado: dict) -> None:
    if estado["cerrado"]:
        texto = "<b>Día cerrado.</b> El paquete de hoy está completo."
    else:
        n = estado["pendientes"]
        plural = "lecciones" if n != 1 else "lección"
        texto = f"Te quedan <b>{n} {plural}</b> para cerrar el día."
    st.markdown(f'<div class="cierre-aviso">◷ {texto}</div>', unsafe_allow_html=True)


def continuar_card(leccion: dict, hechas: int, total: int) -> None:
    """Tarjeta de 'continúa donde lo dejaste' de la biblioteca."""
    cat = leccion["category"]
    st.markdown(
        f"""<div class="continuar">
              <div class="continuar-cover" style="{_fondo(leccion)}">{chip(cat)}</div>
              <div class="continuar-cuerpo">
                <div class="continuar-titulo">{_e(leccion['title'])}</div>
                <div class="cat-pista"><div class="cat-relleno"
                     style="width:{(hechas / total * 100) if total else 0:.0f}%;
                            --cat:{color(cat)}"></div></div>
              </div>
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
    etiqueta = "Hecha" if hecha else "Pendiente"
    st.markdown(
        f"""<div class="tarjeta-portada {'hecha' if hecha else ''}"
                 style="{fondo} --cat:{color(cat)};">
              <div class="tp-estado {'hecha' if hecha else 'pendiente'}">{etiqueta}</div>
              <div class="tp-cuerpo">
                <div class="tp-eyebrow">
                  <span class="tk" style="--tk-color:{color(cat)}">{ticker(cat)}</span>
                  <span class="nom">{_e(nombre(cat))}</span>
                </div>
                <div class="tp-titulo">{_e(leccion['title'])}</div>
              </div>
            </div>""",
        unsafe_allow_html=True,
    )


def eyebrow_categoria(cat_id: str) -> str:
    """Identificador de categoría para las pantallas de lección y resultado.

    Devuelve HTML en vez de pintarlo, porque quien lo usa lo concatena con el
    título en un solo `st.markdown`.
    """
    return (
        f'<div class="eyebrow">'
        f'<span class="tk" style="--tk-color:{color(cat_id)}">{ticker(cat_id)}</span>'
        f'<span>{_e(nombre(cat_id))}</span>'
        f"</div>"
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


LETRAS = ["A", "B", "C", "D", "E", "F"]


def opcion_revelada(texto: str, estado: str, indice: int = 0) -> None:
    """estado: 'ok' (correcta) | 'ko' (elegida y errónea) | 'tenue'."""
    marca = {"ok": "✓", "ko": "✕"}.get(estado, LETRAS[indice % len(LETRAS)])
    st.markdown(
        f'<div class="op-rev {estado}">'
        f'<span class="let">{marca}</span>'
        f'<span>{_e(texto)}</span></div>',
        unsafe_allow_html=True,
    )


def tabla_categorias(filas: list[dict]) -> None:
    """Avance por categoría como tabla de barras, no como medidores apilados.

    Doce medidores seguidos obligaban a desplazarse media pantalla para ver el
    conjunto. En una sola tabla las barras se comparan entre sí de un vistazo,
    que es justo lo que se quiere saber.
    """
    piezas = []
    for f in filas:
        acc = f["accuracy"]
        if acc is None:
            acc_html = '<span class="acc" style="color:var(--tinta-tenue)">—</span>'
        else:
            flojo = " flojo" if acc < 80 else ""
            acc_html = f'<span class="acc{flojo}">{acc:.0f}%</span>'
        piezas.append(
            f"""<div class="cat-fila" style="--cat:{color(f['id'])}">
                  <span class="tk" style="--tk-color:{color(f['id'])}">{ticker(f['id'])}</span>
                  <div>
                    <div class="cat-nom">{_e(nombre(f['id']))}</div>
                    <div class="cat-pista">
                      <div class="cat-relleno" style="width:{min(f['pct'], 100):.1f}%"></div>
                    </div>
                  </div>
                  <div class="cat-cifras">
                    <b>{f['hechas']}/{f['total']}</b>{acc_html}
                  </div>
                </div>"""
        )
    st.markdown(f'<div class="tabla-cat">{"".join(piezas)}</div>', unsafe_allow_html=True)


def cabecera_categoria(cat_id: str, hechas: int, total: int, accuracy: float | None) -> None:
    """Separador de sección para el historial agrupado por tema."""
    detalle = f"{hechas} de {total}"
    if accuracy is not None:
        detalle += f" · acierto {accuracy:.0f}%"
    st.markdown(
        f"""<div class="hist-cabecera" style="--cat:{color(cat_id)}">
              <div class="nom">
                <span class="tk" style="--tk-color:{color(cat_id)}">{ticker(cat_id)}</span>
                {_e(nombre(cat_id))}
              </div>
              <div class="cif">{detalle}</div>
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
    ok = resultado.get("aciertos", 0)
    de = resultado.get("total", 4) or 4
    # El color de la nota hace legible el historial sin leer las cifras: pleno
    # en verde, un fallo en bronce, dos o más en rojo.
    clase = "" if ok == de else ("medio" if de - ok == 1 else "bajo")
    st.markdown(
        f"""<div class="fila-hist">
              {miniatura}
              <div class="meta">
                <div class="t">{_e(leccion['title'])}</div>
                <div class="s">{ticker(cat)} · {_e(resultado.get('fecha', ''))}</div>
              </div>
              <div class="sc {clase}">{ok}/{de}</div>
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
