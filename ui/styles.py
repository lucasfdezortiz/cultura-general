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
        "papel": "#F4F1EA",
        "papel_alto": "#FBF9F5",
        "papel_hund": "#EBE6DA",
        "tinta": "#1B2A41",
        "tinta_suave": "#5A6474",
        "tinta_tenue": "#8A909C",
        "bronce": "#A67C3D",
        "bronce_claro": "#C9A24B",
        "borde": "#DED7C7",
        "verde": "#2F6B4F",
        "verde_fondo": "rgba(47,107,79,.09)",
        "rojo": "#9C3B34",
        "rojo_fondo": "rgba(156,59,52,.08)",
        "sombra": "rgba(27,42,65,.045)",
        "velo_1": ".22",
        "velo_2": ".60",
        "velo_3": ".94",
        "primario": "#1B2A41",
        "sobre_primario": "#FBF9F5",
    },
    "oscuro": {
        "nombre": "Oscuro",
        "papel": "#141A22",
        "papel_alto": "#1D2530",
        "papel_hund": "#0F141A",
        "tinta": "#E9E3D6",
        "tinta_suave": "#A6AEBB",
        "tinta_tenue": "#7A8391",
        "bronce": "#D2A65A",
        "bronce_claro": "#E6C588",
        "borde": "#2E3743",
        "verde": "#7FC6A0",
        "verde_fondo": "rgba(127,198,160,.12)",
        "rojo": "#E39A93",
        "rojo_fondo": "rgba(227,154,147,.12)",
        "sombra": "rgba(0,0,0,.28)",
        "velo_1": ".30",
        "velo_2": ".66",
        "velo_3": ".95",
        "primario": "#D2A65A",
        "sobre_primario": "#16202E",
    },
}

TEMA_POR_DEFECTO = "claro"


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
"""


PLANTILLA = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=Inter:wght@400;500;600&display=swap');

:root {
__VARS__
  --serif: 'Fraunces', Georgia, 'Times New Roman', serif;
  --sans:  'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
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
.block-container { max-width: 780px; padding: .4rem 1.4rem 5rem; }
html, body, [class*="css"], .stApp, p, li, span, label, div {
  font-family: var(--sans);
  color: var(--tinta);
}
h1, h2, h3, h4 {
  font-family: var(--serif) !important; color: var(--tinta) !important;
  letter-spacing: -0.015em;
}
a { color: var(--bronce); }

/* ---- Cabecera ---- */
.cabecera {
  display: flex; align-items: baseline; justify-content: space-between;
  gap: 1rem; padding-bottom: .7rem; margin-bottom: .5rem;
  border-bottom: 1px solid var(--borde);
}
.marca {
  font-family: var(--serif); font-size: 1.3rem; font-weight: 600;
  letter-spacing: -0.02em; color: var(--tinta); line-height: 1.15;
}
.marca em { font-style: italic; color: var(--bronce); }
.fecha {
  font-size: .72rem; text-transform: uppercase; letter-spacing: .13em;
  color: var(--tinta-tenue); font-weight: 500; white-space: nowrap;
}

/* ---- Sellos de racha ---- */
.sellos { display: flex; gap: .48rem; align-items: center; margin: .9rem 0 .2rem; flex-wrap: wrap; }
.sellos .sello {
  width: 28px !important; height: 28px !important;
  min-width: 28px !important; max-width: 28px !important;
  min-height: 28px !important; max-height: 28px !important;
  flex: 0 0 28px !important; align-self: center !important;
  box-sizing: border-box !important; border-radius: 50% !important;
  display: grid !important; place-items: center !important;
  font-size: .62rem; font-weight: 600; font-family: var(--sans);
  line-height: 1 !important; padding: 0 !important;
  border: 1.5px solid var(--borde); color: var(--tinta-tenue);
  background: transparent;
}
.sellos .sello.parcial {
  border-color: var(--bronce); color: var(--bronce);
  background: linear-gradient(180deg, transparent 50%, var(--bronce) 50%);
}
.sellos .sello.completo {
  border-color: var(--bronce); background: var(--bronce); color: var(--papel);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--bronce) 20%, transparent);
}
.sellos .sello.hoy { outline: 1px dashed var(--bronce); outline-offset: 3px; }
.racha-txt {
  margin-left: .6rem; font-size: .78rem; color: var(--tinta-suave);
  font-variant-numeric: tabular-nums;
}
.racha-txt b { color: var(--tinta); font-weight: 600; }

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

/* ---- Rejilla de portadas ---- */
.rotulo {
  font-size: .72rem; text-transform: uppercase; letter-spacing: .15em;
  color: var(--tinta-tenue); font-weight: 600; margin: 1.9rem 0 .8rem;
}
.tarjeta-portada {
  position: relative; border-radius: 10px; overflow: hidden;
  border: 1px solid var(--borde); background: var(--papel-alto);
  height: 152px; display: flex; flex-direction: column; justify-content: flex-end;
  background-size: cover; background-position: center;
}
.tarjeta-portada::after {
  content: ""; position: absolute; inset: 0;
  background: linear-gradient(180deg,
    rgba(10,14,20,var(--velo-1)) 0%, rgba(10,14,20,var(--velo-2)) 45%, rgba(10,14,20,var(--velo-3)) 100%);
}
.tarjeta-portada.hecha::after {
  background: linear-gradient(180deg,
    rgba(10,14,20,.66) 0%, rgba(10,14,20,.84) 45%, rgba(10,14,20,.96) 100%);
}
.tp-cuerpo { position: relative; z-index: 2; padding: .85rem .9rem; }
.tp-eyebrow {
  font-size: .62rem; text-transform: uppercase; letter-spacing: .15em;
  font-weight: 600; color: #E6C588; margin-bottom: .3rem;
  display: flex; align-items: center; gap: .35rem;
}
.tp-titulo {
  font-family: var(--serif); font-size: .96rem; line-height: 1.25;
  color: #F7F3EA; font-weight: 600;
}
.tp-titulo, .tp-eyebrow { text-shadow: 0 1px 3px rgba(0,0,0,.55); }
.tp-estado {
  position: absolute; top: .6rem; right: .7rem; z-index: 3;
  font-size: .6rem; letter-spacing: .1em; text-transform: uppercase;
  padding: .16rem .45rem; border-radius: 20px; font-weight: 600;
}
.tp-estado.pendiente { background: rgba(250,247,240,.92); color: #16202E; }
.tp-estado.hecha { background: var(--bronce); color: #16202E; }

/* ---- Lección ---- */
.eyebrow {
  font-size: .68rem; text-transform: uppercase; letter-spacing: .17em;
  font-weight: 600; color: var(--bronce); margin-bottom: .5rem;
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
  border-left: 3px solid var(--bronce);
  background: color-mix(in srgb, var(--bronce) 11%, transparent);
  border-radius: 0 8px 8px 0; padding: 1rem 1.15rem; margin: 1.6rem 0;
}
.dato-clave .etiq {
  font-size: .63rem; text-transform: uppercase; letter-spacing: .15em;
  color: var(--bronce); font-weight: 700; margin-bottom: .38rem;
}
.dato-clave .txt { font-family: var(--serif); font-size: 1.05rem; line-height: 1.5; color: var(--tinta); }

/* ---- Quiz ---- */
.quiz-cuenta {
  font-size: .7rem; text-transform: uppercase; letter-spacing: .15em;
  color: var(--tinta-tenue); font-weight: 600; margin-bottom: .5rem;
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
  font-size: .68rem; text-transform: uppercase; letter-spacing: .14em;
  font-weight: 700; margin-bottom: .35rem;
}
.veredicto.bien .cabeza { color: var(--verde); }
.veredicto.mal  .cabeza { color: var(--rojo); }
.veredicto .nota { font-size: .945rem; line-height: 1.6; color: var(--tinta); }

/* ---- Resultado ---- */
.marcador { text-align: center; padding: 1.6rem 0 .4rem; }
.marcador .num { font-family: var(--serif); font-size: 3.6rem; font-weight: 700; line-height: 1; color: var(--bronce); }
.marcador .de { font-size: 1.05rem; color: var(--tinta-tenue); margin-top: .3rem; }
.marcador .frase { font-family: var(--serif); font-style: italic; font-size: 1.06rem; color: var(--tinta-suave); margin-top: .9rem; }

/* ---- Historial ---- */
.hist-cabecera {
  display: flex; align-items: baseline; justify-content: space-between;
  gap: 1rem; margin: 1.7rem 0 .3rem; padding-bottom: .4rem;
  border-bottom: 1px solid var(--borde);
}
.hist-cabecera .nom {
  font-family: var(--serif); font-size: 1.02rem; font-weight: 600; color: var(--tinta);
  display: flex; align-items: center; gap: .45rem;
}
.hist-cabecera .nom i { font-style: normal; color: var(--bronce); }
.hist-cabecera .cif {
  font-size: .72rem; color: var(--tinta-tenue); font-variant-numeric: tabular-nums;
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
.fila-hist .s { font-size: .7rem; color: var(--tinta-tenue); }
.fila-hist .sc { font-variant-numeric: tabular-nums; font-size: .85rem; font-weight: 600; color: var(--bronce); white-space: nowrap; }

.vacio { text-align: center; padding: 2.6rem 1rem; color: var(--tinta-tenue); font-family: var(--serif); font-style: italic; font-size: 1.02rem; }
.aviso-banco {
  background: color-mix(in srgb, var(--bronce) 12%, transparent);
  border: 1px solid color-mix(in srgb, var(--bronce) 34%, transparent);
  border-radius: 8px; padding: .8rem 1rem; margin: 1rem 0;
  font-size: .84rem; color: var(--tinta); line-height: 1.55;
}
.aviso-banco b { color: var(--bronce); }

/* ---- Botones ---- */
.stButton > button {
  font-family: var(--sans); font-size: .875rem; font-weight: 500;
  border-radius: 8px; border: 1px solid var(--borde);
  background: var(--papel-alto) !important; color: var(--tinta) !important;
  padding: .55rem 1rem; transition: all .13s ease; width: 100%;
}
.stButton > button p { color: var(--tinta) !important; }
.stButton > button:hover { border-color: var(--bronce); background: var(--papel-alto) !important; }
.stButton > button:hover p, .stButton > button:hover { color: var(--bronce) !important; }
.stButton > button:focus:not(:active) { border-color: var(--bronce); }
.stButton > button[kind="primary"] {
  background: var(--primario) !important; border-color: var(--primario);
}
.stButton > button[kind="primary"], .stButton > button[kind="primary"] p {
  color: var(--sobre-primario) !important;
}
.stButton > button[kind="primary"]:hover {
  background: var(--bronce) !important; border-color: var(--bronce);
}
.stButton > button[kind="primary"]:hover, .stButton > button[kind="primary"]:hover p {
  color: __SOBRE_BRONCE__ !important;
}
.stButton > button:disabled, .stButton > button:disabled p { opacity: .42; }

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] {
  background: var(--papel-hund) !important; border-right: 1px solid var(--borde);
}
section[data-testid="stSidebar"] * { color: var(--tinta); }
section[data-testid="stSidebar"] .block-container { padding-top: 2rem; }
section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 { font-size: .96rem !important; }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p { color: var(--tinta-tenue) !important; }

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
  text-align: center; font-size: .76rem; color: var(--tinta-tenue);
  padding-top: .55rem; white-space: nowrap;
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
  .block-container { padding: .2rem .85rem 3rem; }
  .cabecera { flex-direction: column; align-items: flex-start; gap: .1rem; padding-bottom: .5rem; }
  .marca { font-size: 1.15rem; }
  .fecha { font-size: .64rem; }
  .leccion-titulo { font-size: 1.42rem; }
  .leccion-subtitulo { font-size: .96rem; margin-bottom: 1rem; }
  .portada-grande { height: 168px; }
  .tarjeta { padding: 1.15rem 1.05rem; min-height: 0; }
  .tarjeta-texto { font-size: .97rem; line-height: 1.62; }
  .rotulo { margin: 1.3rem 0 .6rem; }
  .medidor { margin: .9rem 0 .9rem; }
  .quiz-pregunta { font-size: 1.1rem; }
  .stButton > button { padding: .62rem .8rem; }
  /* El botón de volver no necesita ocupar todo el ancho en móvil. */
  [data-testid="stHorizontalBlock"]:has(.nav-compacta) .stButton > button {
    padding: .62rem .4rem; font-size: .82rem;
  }
}
</style>
"""


def tema_valido(nombre: str | None) -> str:
    return nombre if nombre in TEMAS else TEMA_POR_DEFECTO


def inyectar(nombre_tema: str = TEMA_POR_DEFECTO) -> None:
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
    )
    st.markdown(css, unsafe_allow_html=True)
