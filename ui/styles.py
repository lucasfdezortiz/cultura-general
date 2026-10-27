"""CSS inyectado y sistema de temas.

Dos paletas completas: `claro` (papel envejecido, tinta navy, bronce) y
`oscuro` (pizarra azulada, tinta cálida, bronce). Todo el CSS se escribe contra
variables, así que cambiar de tema solo cambia los valores de `:root` — no hay
reglas duplicadas por tema.

Se estilan también los componentes propios de Streamlit (botones, sidebar,
pestañas, avisos, barra de progreso, controles) porque de lo contrario en tema
oscuro conservarían su fondo claro.
"""

from __future__ import annotations

import streamlit as st

TEMAS = {
    "claro": {
        "nombre": "Claro",
        "papel": "#F6F5F1",
        "papel_alto": "#FFFFFF",
        "papel_hund": "#EAE7DF",
        "tinta": "#111A26",
        "tinta_suave": "#55606F",
        "tinta_tenue": "#8A9099",
        "bronce": "#9A6E1E",
        "bronce_claro": "#C2922F",
        "borde": "#DCD7CA",
        "verde": "#1C7A4F",
        "verde_fondo": "rgba(28,122,79,.10)",
        "rojo": "#A8322A",
        "rojo_fondo": "rgba(168,50,42,.09)",
        "sombra": "rgba(17,26,38,.06)",
        "velo_1": ".20",
        "velo_2": ".58",
        "velo_3": ".93",
        # El dorado es el color de marca, así que la acción principal es dorada
        # también en claro. Antes era azul marino y el botón de "Empezar"
        # cambiaba de color según el tema, que es justo lo que no debe pasar.
        "primario": "#E2B35A",
        "sobre_primario": "#16202E",
        "rejilla": "rgba(17,26,38,.05)",
        "panel": "#FFFFFF",
    },
    "oscuro": {
        "nombre": "Oscuro",
        "papel": "#0B0F15",
        "papel_alto": "#151C25",
        "papel_hund": "#070A0F",
        "tinta": "#E7EDF4",
        "tinta_suave": "#93A1B2",
        "tinta_tenue": "#64748B",
        "bronce": "#E2B35A",
        "bronce_claro": "#F4D592",
        "borde": "#1F2A37",
        "verde": "#34D399",
        "verde_fondo": "rgba(52,211,153,.13)",
        "rojo": "#F87171",
        "rojo_fondo": "rgba(248,113,113,.13)",
        "sombra": "rgba(0,0,0,.45)",
        "velo_1": ".26",
        "velo_2": ".64",
        "velo_3": ".96",
        "primario": "#E2B35A",
        "sobre_primario": "#0B0F15",
        "rejilla": "rgba(226,179,90,.07)",
        "panel": "#121922",
    },
}

# Oscuro por defecto: es el que Lucas usa, y el que sostiene la lectura de
# cifras sobre fondo apagado que da a la app su aire de terminal.
TEMA_POR_DEFECTO = "oscuro"


def _variables(tema: dict) -> str:
    return f"""
  --papel:        {tema['papel']};
  --papel-alto:   {tema['papel_alto']};
  --papel-hund:   {tema['papel_hund']};
  --tinta:        {tema['tinta']};
  --tinta-suave:  {tema['tinta_suave']};
  --tinta-tenue:  {tema['tinta_tenue']};
  --bronce:       {tema['bronce']};
  --bronce-claro: {tema['bronce_claro']};
  --borde:        {tema['borde']};
  --verde:        {tema['verde']};
  --verde-fondo:  {tema['verde_fondo']};
  --rojo:         {tema['rojo']};
  --rojo-fondo:   {tema['rojo_fondo']};
  --sombra:       {tema['sombra']};
  --velo-1:       {tema['velo_1']};
  --velo-2:       {tema['velo_2']};
  --velo-3:       {tema['velo_3']};
  --primario:       {tema['primario']};
  --sobre-primario: {tema['sobre_primario']};
  --rejilla:        {tema['rejilla']};
  --panel:          {tema['panel']};
"""


PLANTILLA = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
__VARS__
  --serif: 'Fraunces', Georgia, 'Times New Roman', serif;
  --sans:  'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  /* La monoespaciada es la que da el aire de terminal: toda cifra de la app
     pasa por ella, con cifras tabulares para que las columnas cuadren. */
  --mono:  'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
  color-scheme: __SCHEME__;
}

/* ---- Chrome de Streamlit fuera ----
   La cabecera NO se oculta con display:none. En las versiones recientes de
   Streamlit el botón que abre la barra lateral vive dentro de ella, y
   ocultarla dejaba la app desplegada sin acceso a los ajustes. Se vacía
   visualmente y se fuerza la visibilidad de ese botón. */
/* stToolbar NO se oculta: desde Streamlit 1.5x el botón que despliega la barra
   lateral vive dentro de ella. Se ocultan sus piezas una a una. */
#MainMenu, footer, [data-testid="stDecoration"] { display: none !important; }
[data-testid="stStatusWidget"], [data-testid="stAppDeployButton"],
[data-testid="stMainMenu"] { display: none !important; }
[data-testid="stToolbar"] {
  display: flex !important; background: transparent !important;
  visibility: visible !important;
}
/* Streamlit Cloud añade aquí su botón de Fork y el icono de GitHub, dentro de
   stToolbarActions. La regla anterior ocultaba los hijos del toolbar que NO
   contuvieran el botón de la barra lateral, y no servía: en las versiones
   actuales el botón de la barra lateral y las acciones cuelgan del MISMO
   hijo, así que la excepción que protegía a uno protegía también al otro, y
   el Fork seguía viéndose en el despliegue. Se apunta al contenedor de
   acciones, que tiene identificador propio. */
[data-testid="stToolbarActions"] { display: none !important; }
/* La cabecera se hace transparente pero NO se le quita la altura: el botón que
   abre la barra lateral vive dentro, y colapsarla lo dejaba en 0x0. El nombre
   del testid cambia entre versiones de Streamlit (collapsedControl ->
   stSidebarCollapsedControl -> stExpandSidebarButton), así que se apunta a los
   tres. */
header[data-testid="stHeader"] {
  background: transparent !important;
  box-shadow: none !important; border: 0 !important;
}
[data-testid="stExpandSidebarButton"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
  display: flex !important; visibility: visible !important; opacity: 1 !important;
  width: auto !important; height: auto !important;
  min-width: 2.2rem !important; min-height: 2.2rem !important;
  z-index: 950 !important;
}
[data-testid="stExpandSidebarButton"] button,
[data-testid="stSidebarCollapsedControl"] button,
[data-testid="collapsedControl"] button,
[data-testid="stSidebarCollapseButton"] button {
  color: var(--tinta) !important;
  background: var(--papel-alto) !important;
  border: 1px solid var(--borde) !important;
  border-radius: 8px !important;
  width: auto !important; height: auto !important;
}
[data-testid="stExpandSidebarButton"] svg,
[data-testid="stSidebarCollapsedControl"] svg,
[data-testid="collapsedControl"] svg,
[data-testid="stSidebarCollapseButton"] svg {
  fill: var(--tinta) !important; color: var(--tinta) !important;
}

/* La barra lateral es <section> en versiones antiguas y <div> en las nuevas. */
[data-testid="stSidebar"] {
  background: var(--papel-hund) !important; border-right: 1px solid var(--borde);
}
[data-testid="stSidebar"] * { color: var(--tinta); }
[data-testid="stSidebarContent"], [data-testid="stSidebarUserContent"] {
  background: transparent !important;
}

/* ---- Lienzo ---- */
/* html y body también: config.toml fija un backgroundColor claro que asomaría
   por debajo del contenedor cuando el tema es oscuro. */
html, body, .stApp,
[data-testid="stAppViewContainer"], [data-testid="stMain"],
[data-testid="stBottomBlockContainer"] {
  background: var(--papel) !important;
}
.block-container { max-width: 780px; padding: 3.1rem 1.4rem 9rem; }
/* El relleno inferior deja hueco a la barra de navegación fija. */
html, body, [class*="css"], .stApp, p, li, span, label, div {
  font-family: var(--sans);
  color: var(--tinta);
}
h1, h2, h3, h4 {
  font-family: var(--serif) !important; color: var(--tinta) !important;
  letter-spacing: -0.015em;
}
a { color: var(--bronce); }

/* Toda cifra va en monoespaciada y tabular: es lo que hace que la app se lea
   como un panel de mercado y no como una revista. */
.cifra, .valor, .num, .sc, .cif, .tk, .metrica-valor, .racha-txt,
.contador-tarjeta, .quiz-cuenta { font-variant-numeric: tabular-nums; }

/* ---- Cabecera ---- */
.cabecera {
  position: relative;
  display: flex; align-items: center; justify-content: space-between;
  gap: 1rem; padding: .9rem 1rem; margin-bottom: .9rem;
  border: 1px solid var(--borde); border-radius: 12px;
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--bronce) 7%, transparent), transparent 70%),
    repeating-linear-gradient(0deg, var(--rejilla) 0 1px, transparent 1px 22px),
    repeating-linear-gradient(90deg, var(--rejilla) 0 1px, transparent 1px 22px),
    var(--panel);
  overflow: hidden;
}
/* Filo superior en degradado: el detalle que firma la cabecera. */
.cabecera::before {
  content: ""; position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, var(--bronce), var(--bronce-claro), transparent 85%);
}
.marca {
  font-family: var(--serif); font-size: 1.32rem; font-weight: 700;
  letter-spacing: -0.025em; color: var(--tinta); line-height: 1.1;
}
.marca em { font-style: italic; color: var(--bronce); }
.marca-pie {
  font-family: var(--mono); font-size: .56rem; text-transform: uppercase;
  letter-spacing: .22em; color: var(--tinta-tenue); margin-top: .22rem;
}
.fecha {
  font-family: var(--mono); font-size: .66rem; text-transform: uppercase;
  letter-spacing: .1em; color: var(--tinta-suave); font-weight: 500;
  white-space: nowrap; text-align: right; line-height: 1.5;
}
.fecha b { display: block; color: var(--bronce); font-weight: 700; font-size: .78rem; }

/* ---- Panel de métricas ---- */
.panel {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: .5rem;
  margin: 0 0 1.15rem;
}
.metrica {
  position: relative; background: var(--panel);
  border: 1px solid var(--borde); border-radius: 10px;
  padding: .62rem .55rem .58rem; overflow: hidden;
}
.metrica::before {
  content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 2px;
  background: var(--acento, var(--bronce)); opacity: .85;
}
.metrica-etiq {
  font-family: var(--mono); font-size: .53rem; text-transform: uppercase;
  letter-spacing: .13em; color: var(--tinta-tenue); font-weight: 500;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.metrica-valor {
  font-family: var(--mono); font-size: 1.42rem; font-weight: 700;
  line-height: 1.12; color: var(--tinta); margin-top: .18rem;
  letter-spacing: -0.02em;
}
.metrica-valor small { font-size: .62rem; font-weight: 500; color: var(--tinta-tenue); letter-spacing: 0; }
.metrica-pie {
  font-family: var(--mono); font-size: .56rem; color: var(--tinta-tenue);
  margin-top: .1rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.metrica-pie.alza { color: var(--verde); }
.metrica-pie.baja { color: var(--rojo); }

/* ---- Racha como histograma ---- */
/* Las clases de estado llevan prefijo `d-` porque `vacio`, `parcial` y
   `completo` ya se usan en otras partes del CSS. En concreto `.vacio` es el
   mensaje de estado vacío y trae `padding: 2.6rem`: ese relleno inflaba cada
   barra hasta 84px y las hacía desbordar sobre el panel de métricas.
   Las alturas van en píxeles y no en porcentaje: dentro de un contenedor flex
   el porcentaje no resuelve de forma fiable contra el alto del contenedor, y
   las barras se desbordaban hacia arriba tapando el panel de métricas. */
.barras {
  display: flex; align-items: flex-end; gap: 3px; height: 34px;
  padding: 0 0 2px;
}
.barras .b {
  flex: 1 1 0; border-radius: 2px 2px 0 0; min-width: 0;
  background: var(--papel-hund); border: 1px solid var(--borde); border-bottom: 0;
  height: 8px;
}
.barras .b.d-parcial {
  background: color-mix(in srgb, var(--bronce) 45%, transparent);
  border-color: var(--bronce); height: 19px;
}
.barras .b.d-completo {
  background: linear-gradient(180deg, var(--bronce-claro), var(--bronce));
  border-color: var(--bronce); height: 32px;
}
.barras .b.d-hoy { outline: 1px dashed var(--bronce); outline-offset: 1px; }
.barras-pie {
  display: flex; justify-content: space-between; align-items: baseline;
  font-family: var(--mono); font-size: .56rem; color: var(--tinta-tenue);
  text-transform: uppercase; letter-spacing: .1em; margin-top: .3rem;
}

/* ---- Chip de ticker ---- */
.tk {
  font-family: var(--mono); font-size: .58rem; font-weight: 700;
  letter-spacing: .09em; padding: .14rem .36rem; border-radius: 4px;
  background: color-mix(in srgb, var(--tk-color, var(--bronce)) 22%, transparent);
  color: var(--tk-color, var(--bronce));
  border: 1px solid color-mix(in srgb, var(--tk-color, var(--bronce)) 48%, transparent);
  white-space: nowrap; line-height: 1.35;
}

/* ---- Barra de completado ---- */
.medidor { margin: 1.1rem 0 1.15rem; }
.medidor-fila {
  display: flex; justify-content: space-between; align-items: baseline;
  font-size: .74rem; color: var(--tinta-suave); margin-bottom: .35rem; gap: 1rem;
}
.medidor-fila .etiq { text-transform: uppercase; letter-spacing: .11em; font-weight: 500; }
.medidor-fila .cifra { font-variant-numeric: tabular-nums; color: var(--tinta); font-weight: 600; white-space: nowrap; }
.pista { height: 6px; background: var(--papel-hund); border-radius: 3px; overflow: hidden; border: 1px solid var(--borde); }
.relleno { height: 100%; background: linear-gradient(90deg, var(--bronce), var(--bronce-claro)); border-radius: 3px; }

/* ---- Barra de navegación inferior ----
   Streamlit no tiene navegación por pestañas fijas, así que son tres botones
   en una fila de columnas a la que el CSS ancla al borde inferior de la
   ventana. El gancho es el marcador .marca-nav, igual que en .nav-compacta.
   `env(safe-area-inset-bottom)` deja sitio al indicador del iPhone. */
[data-testid="stHorizontalBlock"]:has(.marca-nav) {
  position: fixed !important; left: 0; right: 0; bottom: 0; z-index: 900;
  background: color-mix(in srgb, var(--papel) 94%, transparent);
  backdrop-filter: blur(12px);
  border-top: 1px solid var(--borde);
  margin: 0 !important; gap: 0 !important; flex-wrap: nowrap !important;
  /* El relleno inferior no es decorativo: Streamlit Cloud dibuja su insignia
     («Created by…» y «Hosted with Streamlit») FUERA del iframe de la app, en
     los 46 px inferiores derechos de la ventana. Desde aquí no se puede
     ocultar —es otro documento—, así que los botones se suben por encima y la
     insignia queda sobre la franja vacía de la barra en vez de tapar
     «Avance». */
  padding: .25rem .5rem calc(__PAD_NAV__ + env(safe-area-inset-bottom, 0px));
}
[data-testid="stHorizontalBlock"]:has(.marca-nav) > div {
  min-width: 0 !important; width: auto !important; flex: 1 1 0 !important;
}
[data-testid="stHorizontalBlock"]:has(.marca-nav) .stButton button {
  background: transparent !important; border: 0 !important;
  box-shadow: none !important; padding: .5rem .2rem !important;
  font-size: .72rem !important; font-weight: 500 !important;
  letter-spacing: .04em; color: var(--tinta-tenue) !important;
}
[data-testid="stHorizontalBlock"]:has(.marca-nav) .stButton button p {
  color: var(--tinta-tenue) !important; font-size: .72rem !important;
}
/* La pestaña activa se marca con type="primary", pero aquí no debe pintarse
   como botón sólido: solo cambia de color. */
[data-testid="stHorizontalBlock"]:has(.marca-nav) .stButton button[kind="primary"],
[data-testid="stHorizontalBlock"]:has(.marca-nav) .stButton button[kind="primary"] p {
  background: transparent !important; color: var(--bronce) !important;
  font-weight: 700 !important;
}
.marca-nav { height: 0; overflow: hidden; }

/* Los marcadores invisibles que enganchan el CSS van en su propio
   `st.markdown`, y Streamlit envuelve cada uno en un contenedor con margen
   propio. Aunque el marcador mida 0, el contenedor no: la pestaña «Hoy»
   quedaba 16 px más baja que las otras dos. Se oculta el contenedor entero;
   `:has()` sigue encontrando el marcador porque sigue en el DOM. */
[data-testid="stElementContainer"]:has(.marca-nav),
[data-testid="stElementContainer"]:has(.barra-sup),
[data-testid="stElementContainer"]:has(.mk-lista),
[data-testid="stElementContainer"]:has(.mk-opciones) {
  display: none !important;
}

/* ---- Cabecera compacta de la sesión ---- */
.saludo {
  font-family: var(--serif); font-size: 1.95rem; line-height: 1.1;
  font-weight: 600; letter-spacing: -0.025em; color: var(--tinta);
  margin: .2rem 0 .3rem;
}
.saludo-pie {
  font-family: var(--mono); font-size: .64rem; letter-spacing: .1em;
  text-transform: uppercase; color: var(--tinta-tenue); margin-bottom: .9rem;
}
.racha-chip {
  display: inline-flex; align-items: center; gap: .35rem;
  background: var(--panel); border: 1px solid var(--borde);
  border-radius: 999px; padding: .28rem .6rem .28rem .5rem;
  font-family: var(--mono); font-size: .72rem; font-weight: 700;
  color: var(--bronce);
}

/* ---- Progreso por segmentos ---- */
.segmentos { display: flex; gap: 4px; flex: 1; }
.segmentos .s { flex: 1 1 0; height: 4px; border-radius: 2px; background: var(--borde); }
.segmentos .s.on { background: var(--bronce); }
.segmentos .s.ok { background: var(--verde); }
.seg-fila {
  display: flex; align-items: center; gap: .7rem; margin: .1rem 0 1.1rem;
}
.seg-cuenta {
  font-family: var(--mono); font-size: .7rem; font-weight: 700;
  color: var(--tinta-suave); white-space: nowrap;
}

/* ---- Tarjeta protagonista del día ---- */
.hero {
  border: 1px solid var(--borde); border-bottom: 0;
  border-radius: 20px 20px 0 0; overflow: hidden; background: var(--panel);
}
.hero-cover {
  height: 136px; background-size: cover; background-position: center;
  position: relative; display: flex; align-items: flex-end; padding: .8rem;
}
.hero-cover::after {
  content: ""; position: absolute; inset: 0;
  background: linear-gradient(180deg, rgba(6,9,14,.15) 0%, rgba(6,9,14,.72) 100%);
}
/* Sobre una fotografía oscura el color plano de la categoría no se lee:
   el chip pasa a fondo translúcido oscuro con el tono aclarado. */
.hero-cover .tk, .continuar-cover .tk {
  position: relative; z-index: 2;
  background: rgba(8,12,18,.62);
  border-color: color-mix(in srgb, var(--tk-color) 70%, transparent);
  color: color-mix(in srgb, var(--tk-color) 60%, #FFFFFF);
  backdrop-filter: blur(3px);
}
.hero-cuerpo { padding: .9rem 1.05rem .2rem; }
.hero-cat {
  font-size: .6rem; font-weight: 600; letter-spacing: .13em;
  text-transform: uppercase; color: var(--tinta-tenue); margin-bottom: .4rem;
}
.hero-titulo {
  font-family: var(--serif); font-size: 1.22rem; line-height: 1.26;
  font-weight: 600; color: var(--tinta); margin-bottom: .55rem;
}
.hero-meta {
  display: flex; align-items: center; gap: .7rem;
  font-family: var(--mono); font-size: .64rem; letter-spacing: .06em;
  color: var(--tinta-tenue); text-transform: uppercase;
}
/* El botón que sigue al hero cierra la tarjeta: hereda su fondo, sus bordes
   laterales y el radio inferior, de modo que los dos bloques se leen como
   una sola pieza aunque Streamlit los renderice por separado. */
[data-testid="stVerticalBlock"]:has(> div > [data-testid="stElementContainer"] .hero-cta) {
  gap: 0 !important;
}
.hero-cta { height: 0; overflow: hidden; }
[data-testid="stElementContainer"]:has(.hero-cta) + [data-testid="stElementContainer"] {
  background: var(--panel);
  border: 1px solid var(--borde); border-top: 0;
  border-radius: 0 0 20px 20px;
  padding: .2rem .9rem .9rem;
  margin-bottom: 1.15rem;
}

/* ---- Filas del resto del paquete ---- */
.mini-chip { margin: 0 0 .3rem; display: flex; align-items: center; gap: .4rem; }
.mini-chip .nom {
  font-size: .6rem; font-weight: 600; letter-spacing: .12em;
  text-transform: uppercase; color: var(--tinta-tenue);
}

/* ---- Listas de botones con aspecto de tarjeta ----
   Streamlit centra el texto de sus botones, que para un título largo queda
   mal. Un marcador invisible dentro de un `st.container` permite reestilar
   solo los botones de ese contenedor, sin tocar los del resto de la app. */
[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .mk-lista) .stButton button {
  text-align: left; justify-content: flex-start;
  font-family: var(--serif); font-size: .97rem; font-weight: 600;
  line-height: 1.32; padding: .85rem .95rem; border-radius: 15px;
  background: var(--panel) !important; border: 1px solid var(--borde) !important;
  min-height: 3.4rem;
}
[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .mk-lista) .stButton button p {
  text-align: left; font-family: var(--serif); font-size: .97rem; font-weight: 600;
}
.mk-lista, .mk-opciones { height: 0; overflow: hidden; }
/* El ticker viaja dentro de la etiqueta del botón como código en línea. */
[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .mk-lista) .stButton code,
[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .mk-opciones) .stButton code {
  font-family: var(--mono); font-size: .62rem; font-weight: 700;
  letter-spacing: .06em; padding: .16rem .36rem; border-radius: 5px;
  background: color-mix(in srgb, var(--bronce) 17%, transparent) !important;
  color: var(--bronce) !important; margin-right: .3rem; white-space: nowrap;
}

/* ---- Opciones del quiz ---- */
/* Tarjetas grandes y alineadas a la izquierda: la respuesta se elige tocando
   la opción, sin botón de enviar. */
[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .mk-opciones) .stButton button {
  text-align: left; justify-content: flex-start;
  font-size: .92rem; font-weight: 400; line-height: 1.42;
  padding: .9rem 1rem; border-radius: 16px; min-height: 3.6rem;
  background: var(--panel) !important; border: 1px solid var(--borde) !important;
}
[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .mk-opciones) .stButton button p {
  text-align: left; font-size: .92rem; font-weight: 400; line-height: 1.42;
}
[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .mk-opciones) .stButton button:hover {
  border-color: var(--bronce) !important;
}

/* Opciones ya reveladas: la correcta en verde, la elegida errónea en rojo. */
.op-rev {
  display: flex; align-items: center; gap: .7rem;
  border-radius: 16px; padding: .85rem .95rem; margin-bottom: .55rem;
  border: 1px solid var(--borde); background: var(--panel);
  font-size: .92rem; line-height: 1.42; color: var(--tinta-suave);
}
.op-rev .let {
  display: grid; place-items: center; flex: 0 0 1.65rem;
  width: 1.65rem; height: 1.65rem; border-radius: 50%;
  background: var(--papel-hund); color: var(--tinta-tenue);
  font-family: var(--mono); font-size: .72rem; font-weight: 700;
}
.op-rev.tenue { opacity: .5; }
.op-rev.ok {
  border: 1.5px solid var(--verde); background: var(--verde-fondo);
  color: var(--tinta); font-weight: 500;
}
.op-rev.ok .let { background: var(--verde); color: var(--papel); }
.op-rev.ko {
  border: 1.5px solid var(--rojo); background: var(--rojo-fondo); color: var(--tinta);
}
.op-rev.ko .let { background: var(--rojo); color: var(--papel); }

.quiz-ayuda {
  text-align: center; font-size: .78rem; color: var(--tinta-tenue);
  margin-top: .8rem;
}

/* ---- Barra superior de lección y quiz ----
   Botón de cerrar redondo a la izquierda y progreso ocupando el resto. Sin
   esto Streamlit apila las dos columnas en móvil y la barra se come media
   pantalla. */
[data-testid="stHorizontalBlock"]:has(.barra-sup) {
  flex-wrap: nowrap !important; gap: .65rem !important; align-items: center;
  margin-bottom: .3rem;
}
[data-testid="stHorizontalBlock"]:has(.barra-sup) > div:first-child {
  min-width: 0 !important; width: auto !important; flex: 0 0 2.5rem !important;
}
[data-testid="stHorizontalBlock"]:has(.barra-sup) > div:last-child {
  min-width: 0 !important; width: auto !important; flex: 1 1 auto !important;
}
[data-testid="stHorizontalBlock"]:has(.barra-sup) .stButton button {
  width: 2.5rem !important; height: 2.5rem; min-height: 2.5rem;
  padding: 0 !important; border-radius: 50%; font-size: .95rem;
}
.barra-sup { height: 0; overflow: hidden; }
.leccion-rotulo {
  font-family: var(--serif); font-size: .95rem; line-height: 1.32;
  font-weight: 600; color: var(--tinta-suave); margin: 0 0 1rem;
}

/* ---- Cierre de lección ---- */
.panel.dos { grid-template-columns: repeat(2, 1fr); }
.cierre { text-align: center; padding: 1.4rem 0 .2rem; }
.cierre-sello {
  width: 88px; height: 88px; border-radius: 50%; margin: 0 auto 1.1rem;
  background: linear-gradient(160deg, var(--bronce-claro), var(--bronce));
  display: grid; place-items: center;
  font-size: 2.4rem; line-height: 1; color: var(--sobre-primario);
  box-shadow: 0 10px 30px color-mix(in srgb, var(--bronce) 22%, transparent);
}
.cierre-titulo {
  font-family: var(--serif); font-size: 1.62rem; font-weight: 600;
  letter-spacing: -0.02em; color: var(--tinta); margin-bottom: .35rem;
}
.cierre-sub {
  font-size: .86rem; line-height: 1.5; color: var(--tinta-suave);
  max-width: 19rem; margin: 0 auto 1.3rem;
}
.cierre-aviso {
  display: flex; align-items: center; gap: .6rem;
  background: color-mix(in srgb, var(--bronce) 9%, transparent);
  border: 1px solid color-mix(in srgb, var(--bronce) 30%, transparent);
  border-radius: 14px; padding: .8rem .9rem; margin: .9rem 0 1.2rem;
  font-size: .84rem; line-height: 1.45; color: var(--tinta);
}
.cierre-aviso b { color: var(--bronce); }

/* ---- Biblioteca ---- */
.continuar {
  border: 1px solid var(--borde); border-radius: 18px; overflow: hidden;
  background: var(--panel); margin-bottom: .3rem;
}
.continuar-cover {
  height: 84px; background-size: cover; background-position: center;
  position: relative; display: flex; align-items: flex-end; padding: .65rem;
}
.continuar-cover::after {
  content: ""; position: absolute; inset: 0;
  background: linear-gradient(180deg, rgba(6,9,14,.1) 0%, rgba(6,9,14,.7) 100%);
}
.continuar-cuerpo { padding: .75rem .9rem .85rem; }
.continuar-titulo {
  font-family: var(--serif); font-size: 1rem; line-height: 1.28;
  font-weight: 600; color: var(--tinta); margin-bottom: .55rem;
}

/* ---- Rejilla de portadas ---- */
.rotulo {
  font-family: var(--mono); font-size: .62rem; text-transform: uppercase;
  letter-spacing: .16em; color: var(--tinta-tenue); font-weight: 500;
  margin: 1.7rem 0 .75rem; display: flex; align-items: center; gap: .6rem;
}
/* Filete que prolonga el rótulo hasta el margen: estructura sin añadir peso. */
.rotulo::after {
  content: ""; flex: 1; height: 1px; background: var(--borde);
}
.tarjeta-portada {
  position: relative; border-radius: 12px; overflow: hidden;
  border: 1px solid var(--borde); background: var(--papel-alto);
  height: 176px; display: flex; flex-direction: column; justify-content: flex-end;
  background-size: cover; background-position: center;
  transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease;
}
.tarjeta-portada:hover {
  transform: translateY(-2px);
  border-color: color-mix(in srgb, var(--cat, var(--bronce)) 65%, transparent);
  box-shadow: 0 6px 20px var(--sombra);
}
.tarjeta-portada::after {
  content: ""; position: absolute; inset: 0;
  background: linear-gradient(180deg,
    rgba(6,9,14,var(--velo-1)) 0%, rgba(6,9,14,var(--velo-2)) 42%, rgba(6,9,14,var(--velo-3)) 100%);
}
/* Franja del color de la categoría: identifica el tema de un vistazo, sin
   tener que leer la etiqueta. */
.tarjeta-portada::before {
  content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 3px;
  z-index: 3; background: var(--cat, var(--bronce));
}
.tarjeta-portada.hecha::after {
  background: linear-gradient(180deg,
    rgba(6,9,14,.70) 0%, rgba(6,9,14,.86) 42%, rgba(6,9,14,.97) 100%);
}
.tarjeta-portada.hecha { filter: saturate(.55); }
.tp-cuerpo { position: relative; z-index: 2; padding: .9rem .95rem .95rem; }
.tp-eyebrow {
  margin-bottom: .42rem; display: flex; align-items: center; gap: .4rem;
}
.tp-eyebrow .tk {
  background: rgba(8,12,18,.62); border-color: color-mix(in srgb, var(--tk-color) 70%, transparent);
  color: color-mix(in srgb, var(--tk-color) 72%, #FFFFFF);
  backdrop-filter: blur(3px);
}
.tp-eyebrow .nom {
  font-size: .6rem; text-transform: uppercase; letter-spacing: .13em;
  font-weight: 600; color: rgba(247,243,234,.82);
}
.tp-titulo {
  font-family: var(--serif); font-size: 1rem; line-height: 1.26;
  color: #F8F5EE; font-weight: 600;
}
.tp-titulo, .tp-eyebrow .nom { text-shadow: 0 1px 4px rgba(0,0,0,.7); }
.tp-estado {
  position: absolute; top: .62rem; right: .7rem; z-index: 3;
  font-family: var(--mono); font-size: .54rem; letter-spacing: .1em;
  text-transform: uppercase; padding: .2rem .45rem; border-radius: 4px;
  font-weight: 700;
}
.tp-estado.pendiente {
  background: rgba(8,12,18,.66); color: #F4D592;
  border: 1px solid rgba(226,179,90,.55); backdrop-filter: blur(3px);
}
.tp-estado.hecha { background: var(--bronce); color: #0B0F15; }

/* ---- Lección ---- */
.eyebrow {
  display: flex; align-items: center; gap: .5rem; margin-bottom: .7rem;
}
.eyebrow > span:last-child {
  font-size: .64rem; text-transform: uppercase; letter-spacing: .16em;
  font-weight: 600; color: var(--tinta-tenue);
}
.leccion-titulo {
  font-family: var(--serif); font-size: 1.86rem; line-height: 1.16;
  font-weight: 600; letter-spacing: -0.02em; margin: 0 0 .45rem; color: var(--tinta);
}
.leccion-subtitulo {
  font-family: var(--serif); font-style: italic; font-size: 1.03rem;
  color: var(--tinta-suave); line-height: 1.45; margin-bottom: 1.3rem;
}
.portada-grande {
  width: 100%; height: 216px; object-fit: cover; border-radius: 10px;
  border: 1px solid var(--borde); display: block;
}
.credito { font-size: .65rem; color: var(--tinta-tenue); margin: .35rem 0 1.3rem; text-align: right; }
.credito a { color: var(--tinta-tenue); text-decoration: underline; }

.tarjeta {
  background: var(--papel-alto); border: 1px solid var(--borde);
  border-radius: 10px; padding: 1.5rem 1.6rem; min-height: 190px;
  box-shadow: 0 1px 2px var(--sombra);
}
.tarjeta-heading {
  font-family: var(--serif); font-size: 1.16rem; font-weight: 600;
  margin-bottom: .65rem; color: var(--tinta);
}
.tarjeta-texto { font-size: 1.005rem; line-height: 1.68; color: var(--tinta); }
.puntos { display: flex; gap: .4rem; justify-content: center; margin: .95rem 0 .3rem; }
.punto { width: 6px; height: 6px; border-radius: 50%; background: var(--borde); }
.punto.on { background: var(--bronce); transform: scale(1.28); }

.dato-clave {
  position: relative; border: 1px solid color-mix(in srgb, var(--bronce) 38%, transparent);
  border-left: 3px solid var(--bronce);
  background:
    repeating-linear-gradient(90deg, var(--rejilla) 0 1px, transparent 1px 20px),
    color-mix(in srgb, var(--bronce) 9%, var(--panel));
  border-radius: 0 10px 10px 0; padding: 1rem 1.15rem; margin: 1.6rem 0;
}
.dato-clave .etiq {
  font-family: var(--mono); font-size: .56rem; text-transform: uppercase;
  letter-spacing: .18em; color: var(--bronce); font-weight: 700;
  margin-bottom: .42rem;
}
.dato-clave .txt { font-family: var(--serif); font-size: 1.05rem; line-height: 1.5; color: var(--tinta); }

/* ---- Quiz ---- */
.quiz-cuenta {
  font-family: var(--mono); font-size: .62rem; text-transform: uppercase;
  letter-spacing: .15em; color: var(--tinta-tenue); font-weight: 500;
  margin-bottom: .5rem;
}
.quiz-pregunta {
  font-family: var(--serif); font-size: 1.24rem; line-height: 1.42;
  font-weight: 600; margin: .3rem 0 1.15rem; color: var(--tinta);
}
.opcion-rev { padding: .42rem .2rem; font-size: .95rem; }
.opcion-rev.ok { color: var(--verde); font-weight: 600; }
.opcion-rev.ko { color: var(--rojo); text-decoration: line-through; }
.opcion-rev.neutra { color: var(--tinta-tenue); }
.veredicto { border-radius: 9px; padding: .95rem 1.1rem; margin: .3rem 0 .2rem; }
.veredicto.bien { background: var(--verde-fondo); border-left: 3px solid var(--verde); }
.veredicto.mal  { background: var(--rojo-fondo);  border-left: 3px solid var(--rojo); }
.veredicto .cabeza {
  font-family: var(--mono); font-size: .6rem; text-transform: uppercase;
  letter-spacing: .15em; font-weight: 700; margin-bottom: .35rem;
}
.veredicto.bien .cabeza { color: var(--verde); }
.veredicto.mal  .cabeza { color: var(--rojo); }
.veredicto .nota { font-size: .945rem; line-height: 1.6; color: var(--tinta); }

/* ---- Resultado ---- */
.marcador { text-align: center; padding: 1.6rem 0 .4rem; }
.marcador .num {
  font-family: var(--mono); font-size: 3.9rem; font-weight: 700; line-height: 1;
  color: var(--bronce); letter-spacing: -0.04em;
}
.marcador .de { font-family: var(--mono); font-size: .8rem; text-transform: uppercase; letter-spacing: .12em; color: var(--tinta-tenue); margin-top: .5rem; }
.marcador .frase { font-family: var(--serif); font-style: italic; font-size: 1.06rem; color: var(--tinta-suave); margin-top: .9rem; }

/* ---- Avance por categoría: tabla de barras ---- */
.tabla-cat {
  border: 1px solid var(--borde); border-radius: 10px;
  background: var(--panel); overflow: hidden; margin-bottom: .4rem;
}
.cat-fila {
  display: grid; grid-template-columns: 2.9rem 1fr 4.4rem;
  align-items: center; gap: .6rem;
  padding: .52rem .7rem; border-bottom: 1px solid var(--borde);
}
.cat-fila:last-child { border-bottom: 0; }
.cat-fila:hover { background: color-mix(in srgb, var(--cat) 7%, transparent); }
.cat-nom {
  font-size: .78rem; font-weight: 500; color: var(--tinta);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.cat-pista {
  height: 4px; background: var(--papel-hund); border-radius: 2px;
  overflow: hidden; margin-top: .25rem;
}
.cat-relleno {
  height: 100%; border-radius: 2px;
  background: linear-gradient(90deg,
    color-mix(in srgb, var(--cat) 70%, transparent), var(--cat));
}
.cat-cifras {
  font-family: var(--mono); font-size: .68rem; text-align: right;
  color: var(--tinta-suave); line-height: 1.35; white-space: nowrap;
}
.cat-cifras b { display: block; color: var(--tinta); font-weight: 700; font-size: .74rem; }
.cat-cifras .acc { color: var(--verde); }
.cat-cifras .acc.flojo { color: var(--bronce); }

/* ---- Historial ---- */
.hist-cabecera {
  display: flex; align-items: baseline; justify-content: space-between;
  gap: 1rem; margin: 1.7rem 0 .3rem; padding-bottom: .4rem;
  border-bottom: 1px solid var(--borde);
}
.hist-cabecera .nom {
  font-family: var(--serif); font-size: 1.02rem; font-weight: 600; color: var(--tinta);
  display: flex; align-items: center; gap: .5rem;
}
.hist-cabecera .nom i { font-style: normal; color: var(--cat, var(--bronce)); }
.hist-cabecera .cif {
  font-family: var(--mono); font-size: .68rem; color: var(--tinta-tenue);
  white-space: nowrap;
}
.fila-hist { display: flex; align-items: center; gap: .8rem; padding: .62rem 0; border-bottom: 1px solid var(--borde); }
.fila-hist img, .fila-hist .ph {
  width: 50px; height: 38px; border-radius: 5px; object-fit: cover;
  border: 1px solid var(--borde); flex-shrink: 0;
}
.fila-hist .ph { background: var(--papel-hund); display: grid; place-items: center; color: var(--tinta-tenue); }
.fila-hist .meta { flex: 1; min-width: 0; }
.fila-hist .t { font-family: var(--serif); font-size: .93rem; font-weight: 600; color: var(--tinta); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.fila-hist .s { font-family: var(--mono); font-size: .62rem; color: var(--tinta-tenue); letter-spacing: .02em; }
.fila-hist .sc {
  font-family: var(--mono); font-size: .82rem; font-weight: 700;
  white-space: nowrap; padding: .16rem .4rem; border-radius: 4px;
  background: var(--verde-fondo); color: var(--verde);
}
.fila-hist .sc.medio { background: color-mix(in srgb, var(--bronce) 14%, transparent); color: var(--bronce); }
.fila-hist .sc.bajo  { background: var(--rojo-fondo); color: var(--rojo); }

.vacio { text-align: center; padding: 2.6rem 1rem; color: var(--tinta-tenue); font-family: var(--serif); font-style: italic; font-size: 1.02rem; }
.aviso-banco {
  background: color-mix(in srgb, var(--bronce) 12%, transparent);
  border: 1px solid color-mix(in srgb, var(--bronce) 34%, transparent);
  border-radius: 8px; padding: .8rem 1rem; margin: 1rem 0;
  font-size: .84rem; color: var(--tinta); line-height: 1.55;
}
.aviso-banco b { color: var(--bronce); }

/* ---- Botones ----
   Selector de descendiente y no de hijo directo: cuando un botón lleva
   `help=`, Streamlit lo envuelve en un div de tooltip y `.stButton > button`
   deja de alcanzarlo. Pasó con la ✕ de la barra superior, que salía con el
   fondo claro del tema nativo en mitad de la pantalla oscura. */
.stButton button {
  font-family: var(--sans); font-size: .875rem; font-weight: 500;
  border-radius: 8px; border: 1px solid var(--borde);
  background: var(--papel-alto) !important; color: var(--tinta) !important;
  padding: .55rem 1rem; transition: all .13s ease; width: 100%;
}
.stButton button p { color: var(--tinta) !important; }
.stButton button:hover { border-color: var(--bronce); background: var(--papel-alto) !important; }
.stButton button:hover p, .stButton button:hover { color: var(--bronce) !important; }
.stButton button:focus:not(:active) { border-color: var(--bronce); }
.stButton button[kind="primary"] {
  background: var(--primario) !important; border-color: var(--primario);
}
.stButton button[kind="primary"], .stButton button[kind="primary"] p {
  color: var(--sobre-primario) !important;
}
.stButton button[kind="primary"]:hover {
  background: var(--bronce) !important; border-color: var(--bronce);
}
.stButton button[kind="primary"]:hover, .stButton button[kind="primary"]:hover p {
  color: __SOBRE_BRONCE__ !important;
}
.stButton button:disabled, .stButton button:disabled p { opacity: .42; }

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] {
  background: var(--papel-hund) !important; border-right: 1px solid var(--borde);
}
section[data-testid="stSidebar"] * { color: var(--tinta); }
section[data-testid="stSidebar"] .block-container { padding-top: 2rem; }
section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 { font-size: .96rem !important; }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p { color: var(--tinta-tenue) !important; }

/* ---- Campo de texto ----
   Sin esto conserva el fondo claro de Streamlit y en tema oscuro aparece
   como un recuadro beige en mitad de la pantalla. */
[data-testid="stTextInput"] input,
[data-baseweb="input"], [data-baseweb="base-input"] {
  background: var(--panel) !important; color: var(--tinta) !important;
  border-radius: 13px !important;
}
[data-baseweb="input"] { border: 1px solid var(--borde) !important; }
[data-testid="stTextInput"] input::placeholder { color: var(--tinta-tenue) !important; }
[data-baseweb="input"]:focus-within { border-color: var(--bronce) !important; }

/* ---- Controles ---- */
[data-testid="stWidgetLabel"] p, .stRadio label p, .stCheckbox label p { color: var(--tinta) !important; }
[data-baseweb="checkbox"] div[role="checkbox"] { border-color: var(--borde) !important; }
.stRadio [role="radiogroup"] { gap: .4rem; }

/* ---- Barra de progreso nativa ----
   La pista real cuelga tres niveles por debajo de stProgress y toma su color
   de secondaryBackgroundColor en config.toml, que es fijo. Hay que apuntar al
   elemento exacto para que siga al tema. */
/* Streamlit 1.5x+: la pista tiene testid propio. */
[data-testid="stProgressBarTrack"] { background: var(--papel-hund) !important; }
[data-testid="stProgressBarTrack"] > div { background: var(--bronce) !important; }
/* Streamlit 1.3x: la pista es un div sin testid. */
[data-testid="stProgress"] div[role="progressbar"] > div:not([data-testid]) {
  background: var(--papel-hund) !important;
}
[data-testid="stProgress"] div[role="progressbar"] > div:not([data-testid]) > div {
  background: var(--bronce) !important;
}

/* ---- Avisos ---- */
[data-testid="stAlert"], [data-testid="stNotification"], .stAlert {
  background: var(--papel-alto) !important; border: 1px solid var(--borde) !important;
  border-radius: 9px; color: var(--tinta) !important;
}
[data-testid="stAlert"] p, [data-testid="stNotification"] p, .stAlert p {
  color: var(--tinta) !important; font-size: .9rem;
}
[data-testid="stAlert"] svg, [data-testid="stNotification"] svg { fill: var(--bronce) !important; }

/* ---- Tabs ---- */
.stTabs [data-baseweb="tab-list"] { gap: 1.4rem; border-bottom: 1px solid var(--borde); background: transparent; }
.stTabs [data-baseweb="tab"] {
  font-family: var(--sans); font-size: .78rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: .12em;
  color: var(--tinta-tenue) !important; background: transparent; padding: .4rem 0;
}
.stTabs [data-baseweb="tab"] p { color: var(--tinta-tenue) !important; font-size: .78rem; font-weight: 600; }
.stTabs [aria-selected="true"], .stTabs [aria-selected="true"] p { color: var(--bronce) !important; }
.stTabs [data-baseweb="tab-highlight"] { background: var(--bronce); }
.stTabs [data-baseweb="tab-border"] { background: var(--borde); }

hr, [data-testid="stDivider"] hr { border-color: var(--borde) !important; margin: 1.5rem 0; }
[data-testid="stExpander"] { border-color: var(--borde) !important; border-radius: 8px; background: var(--papel-alto) !important; }

.contador-tarjeta {
  text-align: center; font-family: var(--mono); font-size: .7rem;
  color: var(--tinta-tenue); padding-top: .55rem; white-space: nowrap;
}

/* Streamlit apila las columnas por debajo de ~640px poniendo
   min-width: calc(100% - 24px) en cada una. Para la fila de navegación de
   tarjetas eso deja el botón "Siguiente" a dos pantallas de distancia, así que
   se anula solo en esa fila, localizada por el marcador .nav-compacta. */
[data-testid="stHorizontalBlock"]:has(.nav-compacta) {
  flex-wrap: nowrap !important;
  gap: .5rem !important;
  align-items: center;
}
[data-testid="stHorizontalBlock"]:has(.nav-compacta) > div {
  min-width: 0 !important;
  width: auto !important;
  flex: 1 1 0 !important;
}

@media (max-width: 640px) {
  .block-container { padding: 2.9rem .85rem 8.5rem; }
  /* La cabecera mantiene marca y fecha en la misma línea también en móvil:
     apilarlas desperdiciaba la mitad de la primera pantalla. */
  .cabecera { padding: .75rem .8rem; gap: .6rem; margin-bottom: .75rem; }
  .marca { font-size: 1.08rem; }
  .marca-pie { font-size: .5rem; letter-spacing: .16em; }
  .fecha { font-size: .56rem; }
  .fecha b { font-size: .68rem; }
  /* Cuatro métricas no caben a lo ancho del móvil: dos por fila. */
  .panel { grid-template-columns: repeat(2, 1fr); gap: .45rem; margin-bottom: .95rem; }
  .metrica { padding: .55rem .5rem .5rem; }
  .metrica-valor { font-size: 1.3rem; }
  .tarjeta-portada { height: 164px; }
  .cat-fila { grid-template-columns: 2.7rem 1fr 3.9rem; gap: .5rem; padding: .48rem .55rem; }
  .cat-nom { font-size: .74rem; }
  .cat-cifras { font-size: .62rem; }
  .cat-cifras b { font-size: .7rem; }
  .barras { height: 30px; }
  .barras .b { height: 7px; }
  .barras .b.d-parcial { height: 17px; }
  .barras .b.d-completo { height: 28px; }
  .saludo { font-size: 1.72rem; }
  .hero-cover { height: 124px; }
  .hero-titulo { font-size: 1.14rem; }
  .cierre-sello { width: 78px; height: 78px; font-size: 2.1rem; }
  .cierre-titulo { font-size: 1.44rem; }
  .leccion-titulo { font-size: 1.42rem; }
  .leccion-subtitulo { font-size: .96rem; margin-bottom: 1rem; }
  .portada-grande { height: 168px; }
  .tarjeta { padding: 1.15rem 1.05rem; min-height: 0; }
  .tarjeta-texto { font-size: .97rem; line-height: 1.62; }
  .rotulo { margin: 1.3rem 0 .6rem; }
  .medidor { margin: .9rem 0 .9rem; }
  .quiz-pregunta { font-size: 1.1rem; }
  .stButton button { padding: .62rem .8rem; }
  /* El botón de volver no necesita ocupar todo el ancho en móvil. */
  [data-testid="stHorizontalBlock"]:has(.nav-compacta) .stButton button {
    padding: .62rem .4rem; font-size: .82rem;
  }
}
</style>
"""


def tema_valido(nombre: str | None) -> str:
    return nombre if nombre in TEMAS else TEMA_POR_DEFECTO


def inyectar(nombre_tema: str = TEMA_POR_DEFECTO, compacto: bool = False) -> None:
    """Inyecta el CSS del tema.

    `compacto` quita el hueco que la barra de navegación reserva para la
    insignia de Streamlit Cloud. Solo debe activarse cuando la app se sirve
    incrustada (`?embed=true`), porque entonces Cloud no dibuja esa insignia
    y el hueco sobraría.
    """
    clave = tema_valido(nombre_tema)
    tema = TEMAS[clave]
    # Sustitución por tokens y no con %-formatting: el CSS está lleno de
    # porcentajes literales (width: 100%) que romperían el formateo.
    css = (
        PLANTILLA.replace("__VARS__", _variables(tema))
        .replace("__SCHEME__", "dark" if clave == "oscuro" else "light")
        # Sobre el bronce hace falta un texto con contraste suficiente en
        # ambos temas: el navy oscuro funciona en los dos.
        .replace("__SOBRE_BRONCE__", "#16202E")
        .replace("__PAD_NAV__", ".45rem" if compacto else "3.3rem")
    )
    st.markdown(css, unsafe_allow_html=True)
