"""CSS inyectado. Todo el aspecto de la app vive aquí.

Paleta: papel envejecido, tinta navy, bronce. Serif para títulos, sans para
cuerpo. El objetivo es que no se reconozca como una app de Streamlit.
"""

import streamlit as st

PALETA = {
    "papel": "#F4F1EA",
    "papel_alto": "#FBF9F5",
    "papel_hundido": "#EBE6DA",
    "tinta": "#1B2A41",
    "tinta_suave": "#5A6474",
    "tinta_tenue": "#8A909C",
    "bronce": "#A67C3D",
    "bronce_claro": "#C9A24B",
    "borde": "#DED7C7",
    "verde": "#2F6B4F",
    "rojo": "#9C3B34",
}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=Inter:wght@400;500;600&display=swap');

:root {
  --papel:        #F4F1EA;
  --papel-alto:   #FBF9F5;
  --papel-hund:   #EBE6DA;
  --tinta:        #1B2A41;
  --tinta-suave:  #5A6474;
  --tinta-tenue:  #8A909C;
  --bronce:       #A67C3D;
  --bronce-claro: #C9A24B;
  --borde:        #DED7C7;
  --verde:        #2F6B4F;
  --rojo:         #9C3B34;
  --serif: 'Fraunces', Georgia, 'Times New Roman', serif;
  --sans:  'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* ---- Chrome de Streamlit fuera ---- */
#MainMenu, footer, header[data-testid="stHeader"] { display: none !important; }
[data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }
[data-testid="stStatusWidget"] { display: none !important; }

/* ---- Lienzo ---- */
.stApp { background: var(--papel); }
.block-container {
  max-width: 780px;
  padding: 1.6rem 1.4rem 5rem;
}
html, body, [class*="css"] { font-family: var(--sans); color: var(--tinta); }

h1, h2, h3, h4 { font-family: var(--serif) !important; color: var(--tinta) !important; letter-spacing: -0.015em; }

/* ---- Cabecera ---- */
.cabecera {
  display: flex; align-items: baseline; justify-content: space-between;
  gap: 1rem; padding-bottom: .7rem; margin-bottom: .5rem;
  border-bottom: 1px solid var(--borde);
}
.marca {
  font-family: var(--serif); font-size: 1.32rem; font-weight: 600;
  letter-spacing: -0.02em; color: var(--tinta);
}
.marca em { font-style: italic; color: var(--bronce); }
.fecha {
  font-size: .74rem; text-transform: uppercase; letter-spacing: .13em;
  color: var(--tinta-tenue); font-weight: 500; white-space: nowrap;
}

/* ---- Sellos de racha ---- */
/* Streamlit inyecta reglas sobre los div hijos de un bloque markdown, así que
   las medidas del sello van con !important para que no las estire. */
.sellos { display: flex; gap: .48rem; align-items: center; margin: .9rem 0 .2rem; }
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
.sello.parcial {
  border-color: var(--bronce); color: var(--bronce);
  background: linear-gradient(180deg, transparent 50%, rgba(166,124,61,.22) 50%);
}
.sello.completo {
  border-color: var(--bronce); background: var(--bronce); color: var(--papel-alto);
  box-shadow: 0 0 0 3px rgba(166,124,61,.14);
}
.sello.hoy { outline: 1px dashed var(--bronce); outline-offset: 3px; }
.racha-txt {
  margin-left: .6rem; font-size: .78rem; color: var(--tinta-suave);
  font-variant-numeric: tabular-nums;
}
.racha-txt b { color: var(--tinta); font-weight: 600; }

/* ---- Barra de completado ---- */
.medidor { margin: 1.1rem 0 1.15rem; }
.medidor-fila {
  display: flex; justify-content: space-between; align-items: baseline;
  font-size: .74rem; color: var(--tinta-suave); margin-bottom: .35rem;
}
.medidor-fila .etiq { text-transform: uppercase; letter-spacing: .11em; font-weight: 500; }
.medidor-fila .cifra { font-variant-numeric: tabular-nums; color: var(--tinta); font-weight: 600; }
.pista { height: 6px; background: var(--papel-hund); border-radius: 3px; overflow: hidden; }
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
    rgba(27,42,65,.22) 0%, rgba(27,42,65,.60) 45%, rgba(27,42,65,.94) 100%);
}
.tarjeta-portada.hecha::after {
  background: linear-gradient(180deg,
    rgba(27,42,65,.62) 0%, rgba(27,42,65,.82) 45%, rgba(27,42,65,.96) 100%);
}
.tp-titulo, .tp-eyebrow { text-shadow: 0 1px 3px rgba(0,0,0,.45); }
.tp-cuerpo { position: relative; z-index: 2; padding: .85rem .9rem; }
.tp-eyebrow {
  font-size: .62rem; text-transform: uppercase; letter-spacing: .15em;
  font-weight: 600; color: var(--bronce-claro); margin-bottom: .3rem;
  display: flex; align-items: center; gap: .35rem;
}
.tp-titulo {
  font-family: var(--serif); font-size: .96rem; line-height: 1.25;
  color: #FBF9F5; font-weight: 600;
}
.tp-estado {
  position: absolute; top: .6rem; right: .7rem; z-index: 3;
  font-size: .6rem; letter-spacing: .1em; text-transform: uppercase;
  padding: .16rem .45rem; border-radius: 20px; font-weight: 600;
}
.tp-estado.pendiente { background: rgba(251,249,245,.9); color: var(--tinta); }
.tp-estado.hecha { background: var(--bronce); color: #FBF9F5; }

/* ---- Lección ---- */
.eyebrow {
  font-size: .68rem; text-transform: uppercase; letter-spacing: .17em;
  font-weight: 600; color: var(--bronce); margin-bottom: .5rem;
}
.leccion-titulo {
  font-family: var(--serif); font-size: 1.86rem; line-height: 1.16;
  font-weight: 600; letter-spacing: -0.02em; margin: 0 0 .45rem;
}
.leccion-subtitulo {
  font-family: var(--serif); font-style: italic; font-size: 1.03rem;
  color: var(--tinta-suave); line-height: 1.45; margin-bottom: 1.3rem;
}
.portada-grande {
  width: 100%; height: 216px; object-fit: cover; border-radius: 10px;
  border: 1px solid var(--borde); display: block;
}
.credito {
  font-size: .65rem; color: var(--tinta-tenue); margin: .35rem 0 1.3rem;
  text-align: right;
}
.credito a { color: var(--tinta-tenue); text-decoration: underline; }

.tarjeta {
  background: var(--papel-alto); border: 1px solid var(--borde);
  border-radius: 10px; padding: 1.5rem 1.6rem; min-height: 190px;
  box-shadow: 0 1px 2px rgba(27,42,65,.045);
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
  border-left: 3px solid var(--bronce); background: rgba(166,124,61,.075);
  border-radius: 0 8px 8px 0; padding: 1rem 1.15rem; margin: 1.6rem 0;
}
.dato-clave .etiq {
  font-size: .63rem; text-transform: uppercase; letter-spacing: .15em;
  color: var(--bronce); font-weight: 700; margin-bottom: .38rem;
}
.dato-clave .txt {
  font-family: var(--serif); font-size: 1.05rem; line-height: 1.5; color: var(--tinta);
}

/* ---- Quiz ---- */
.quiz-cuenta {
  font-size: .7rem; text-transform: uppercase; letter-spacing: .15em;
  color: var(--tinta-tenue); font-weight: 600; margin-bottom: .5rem;
}
.quiz-pregunta {
  font-family: var(--serif); font-size: 1.24rem; line-height: 1.42;
  font-weight: 600; margin: .3rem 0 1.15rem;
}
.veredicto { border-radius: 9px; padding: .95rem 1.1rem; margin: .3rem 0 .2rem; }
.veredicto.bien { background: rgba(47,107,79,.09); border-left: 3px solid var(--verde); }
.veredicto.mal  { background: rgba(156,59,52,.08); border-left: 3px solid var(--rojo); }
.veredicto .cabeza {
  font-size: .68rem; text-transform: uppercase; letter-spacing: .14em;
  font-weight: 700; margin-bottom: .35rem;
}
.veredicto.bien .cabeza { color: var(--verde); }
.veredicto.mal  .cabeza { color: var(--rojo); }
.veredicto .nota { font-size: .945rem; line-height: 1.6; color: var(--tinta); }

/* ---- Resultado ---- */
.marcador { text-align: center; padding: 1.6rem 0 .4rem; }
.marcador .num {
  font-family: var(--serif); font-size: 3.6rem; font-weight: 700;
  line-height: 1; color: var(--bronce);
}
.marcador .de { font-size: 1.05rem; color: var(--tinta-tenue); margin-top: .3rem; }
.marcador .frase {
  font-family: var(--serif); font-style: italic; font-size: 1.06rem;
  color: var(--tinta-suave); margin-top: .9rem;
}

/* ---- Historial ---- */
.fila-hist {
  display: flex; align-items: center; gap: .8rem; padding: .62rem 0;
  border-bottom: 1px solid var(--borde);
}
.fila-hist img, .fila-hist .ph {
  width: 50px; height: 38px; border-radius: 5px; object-fit: cover;
  border: 1px solid var(--borde); flex-shrink: 0;
}
.fila-hist .ph { background: var(--papel-hund); display: grid; place-items: center; color: var(--tinta-tenue); }
.fila-hist .meta { flex: 1; min-width: 0; }
.fila-hist .t {
  font-family: var(--serif); font-size: .93rem; font-weight: 600;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.fila-hist .s { font-size: .7rem; color: var(--tinta-tenue); }
.fila-hist .sc {
  font-variant-numeric: tabular-nums; font-size: .85rem;
  font-weight: 600; color: var(--bronce); white-space: nowrap;
}

.vacio {
  text-align: center; padding: 2.6rem 1rem; color: var(--tinta-tenue);
  font-family: var(--serif); font-style: italic; font-size: 1.02rem;
}
.aviso-banco {
  background: rgba(166,124,61,.09); border: 1px solid rgba(166,124,61,.3);
  border-radius: 8px; padding: .8rem 1rem; margin: 1rem 0;
  font-size: .84rem; color: var(--tinta); line-height: 1.55;
}
.aviso-banco b { color: var(--bronce); }

/* ---- Botones ---- */
.stButton > button {
  font-family: var(--sans); font-size: .875rem; font-weight: 500;
  border-radius: 8px; border: 1px solid var(--borde);
  background: var(--papel-alto); color: var(--tinta);
  padding: .55rem 1rem; transition: all .13s ease; width: 100%;
}
.stButton > button:hover {
  border-color: var(--bronce); color: var(--bronce); background: var(--papel-alto);
}
.stButton > button:focus:not(:active) { color: var(--bronce); border-color: var(--bronce); }
.stButton > button[kind="primary"] {
  background: var(--tinta); color: var(--papel-alto); border-color: var(--tinta);
}
.stButton > button[kind="primary"]:hover {
  background: var(--bronce); border-color: var(--bronce); color: var(--papel-alto);
}
.stButton > button:disabled { opacity: .42; }

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] {
  background: var(--papel-hund); border-right: 1px solid var(--borde);
}
section[data-testid="stSidebar"] .block-container { padding-top: 2rem; }
section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 { font-size: .96rem !important; }

/* ---- Tabs ---- */
.stTabs [data-baseweb="tab-list"] { gap: 1.4rem; border-bottom: 1px solid var(--borde); }
.stTabs [data-baseweb="tab"] {
  font-family: var(--sans); font-size: .78rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: .12em;
  color: var(--tinta-tenue); background: transparent; padding: .4rem 0;
}
.stTabs [aria-selected="true"] { color: var(--bronce) !important; }
.stTabs [data-baseweb="tab-highlight"] { background: var(--bronce); }

hr { border-color: var(--borde); margin: 1.5rem 0; }
[data-testid="stExpander"] { border-color: var(--borde); border-radius: 8px; }

@media (max-width: 640px) {
  .block-container { padding: 1.1rem .9rem 4rem; }
  .leccion-titulo { font-size: 1.5rem; }
  .portada-grande { height: 168px; }
  .tarjeta { padding: 1.2rem 1.1rem; min-height: 170px; }
}
</style>
"""


def inyectar() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
