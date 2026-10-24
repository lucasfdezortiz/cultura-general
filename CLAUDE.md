# Guía de redacción y ampliación del banco

Este archivo es la referencia para escribir lecciones nuevas. La tarea semanal
programada lo lee y lo sigue, así que **editarlo aquí cambia el criterio de
todas las tandas futuras**.

---

## 0. El temario gira sobre mercados, economía e inversión

Decidido el 2026-10-24. El banco dejó de ser cultura general repartida por igual:
**entre el 60 y el 70 % de cada tanda va a `economia`, `mercados`, `inversion` y
`quant`**, en ese orden de prioridad. El resto aporta contexto, no protagonismo.

Arte, Literatura y Mitología se fusionaron en **`humanidades`**, con frecuencia 1.
Conserva sus 39 lecciones y el historial, pero **no se le escriben lecciones
nuevas hasta que alcance su objetivo por detrás de todo lo demás**.

### Las tres categorías nuevas se escriben desde el cerebro

`economia`, `mercados`, `inversion` y `quant` tienen una fuente propia y mejor que
el conocimiento general: el wiki del repositorio **LF Global Capital Brain**, en
`~/Proyectos/02_LF_Global_Capital/LF Global Capital Brain/wiki/`. Son 84 páginas
ya verificadas, con cifras, páginas de origen y las limitaciones que reconoce cada
autor. Material disponible:

| Carpeta del wiki | Alimenta | Contenido |
|---|---|---|
| `AnalisisFinanciero/` | `mercados`, `economia` | Fama, Minsky, Borio, Dalio, Adrian-Shin, Taylor, Reinhart-Rogoff, Keynes, Lo-MacKinlay, Fama-French |
| `LFGlobalCapital/` | `inversion` | Cartas de Berkshire 1977-2024, Piotroski, y los conceptos `C-*`: moat, float, owner earnings, margen de seguridad, círculo de competencia |
| `QuantFinance/` | `quant` | Sharpe, Black-Scholes, Merton, Markowitz, Jegadeesh-Titman, Gatev, VaR, medidas coherentes de riesgo |

**Procedimiento:** antes de escribir una lección de estas cuatro categorías, lee
la ficha del wiki correspondiente y saca de ahí las cifras. Una ficha da para una
o dos lecciones, no más. Lo que no está en el wiki se puede escribir igual, pero
las cifras tienen que ser verificables.

Dos avisos sobre cómo usar ese material:

- **El wiki está escrito para un inversor que ya sabe; la lección, no.** No
  trasplantes párrafos: una ficha cita página y estadístico t porque sirve de
  referencia, y una lección necesita que el dato signifique algo para quien lo lee
  por primera vez.
- **Respeta las advertencias de la fuente.** Si la ficha anota que una cifra no es
  implementable, que el autor declara sesgo de supervivencia o que un hallazgo no
  sobrevive en empresas grandes, eso **va en la lección**. Es lo que la hace útil
  en lugar de decorativa.

### La frontera de tamaño

El hallazgo mejor establecido del cerebro, y el que más le importa a Lucas porque
solo invierte en empresas de más de 5.000 M€: la ineficiencia explotable aparece
en las empresas pequeñas y se desvanece en las grandes. Tres métodos
independientes lo sitúan ahí —Piotroski (t = 0,872, p = 0,203 en el tercio
superior de capitalización), Lo-MacKinlay (cociente 1,06, z = 1,12 en el quintil
grande) y Jegadeesh-Titman (el enero negativo deja de ser significativo en las
grandes)—. **Cuando una lección toque un hallazgo con dominio de validez
limitado, decirlo es más valioso que el hallazgo.**

---

## 1. Procedimiento de una tanda

```bash
cd ~/lf-global-capital

# 1. Ver qué categorías van más justas
python3 -c "
import sys; sys.path.insert(0,'.')
from core import bank, progress as P
b = bank.cargar_banco(); pr = P.cargar()
print(bank.informe_salud(bank.check_bank_health(b, P.ids_completadas(pr), P.categorias_activas(pr), tope=P.max_por_dia(pr))))"

# 2. Escribir data/tandas/tanda-NN.json  (NN = siguiente número libre)
# 3. Fusionar, validar y resolver portadas
python3 scripts/merge_batch.py data/tandas/tanda-NN.json
python3 scripts/validate_bank.py --fix-shuffle
python3 scripts/fetch_images.py

# 4. Confirmar que queda limpio y commitear
python3 scripts/validate_bank.py
git add -A && git commit -m "Tanda NN: N lecciones"
```

**Tamaño de tanda: 20-24 lecciones.** Reparto orientativo, ajustado al informe de
salud —que ya calcula los días de reserva con el reparto ponderado, no a una
lección por categoría y día:

| Categorías | Por tanda |
|---|---|
| `economia`, `mercados`, `inversion` | 4 cada una |
| `quant` | 3 |
| `geopolitica`, `matematicas` | 2 cada una |
| `presente`, `historia`, `ciencia`, `fisica`, `filosofia` | 1 donde más apriete |
| `humanidades` | 0, salvo que quede por debajo de 10 días de reserva |

Prioridad cuando el informe avise de varias: primero las cuatro financieras,
porque son las que consumen el 60 % del paquete diario y las que más rápido se
agotan. No escribas la tanda entera de una categoría sola.

`validate_bank.py --fix-shuffle` es **obligatorio**. Sin él, la respuesta
correcta se queda casi siempre en la primera posición.

Si `fetch_images.py` se interrumpe por límite de peticiones, vuelve a lanzarlo:
es idempotente y guarda cada diez lecciones.

---

## 2. Antes de escribir: no repetir

Comprueba los títulos que ya existen en la categoría antes de elegir tema.

```bash
python3 -c "
import json
b = json.load(open('data/lessons_bank.json'))
for l in sorted(b['lecciones'], key=lambda x: (x['category'], x['id'])):
    print(f\"{l['category']:<14} {l['id']}  {l['title']}\")"
```

`merge_batch.py` rechaza ids y títulos repetidos, pero no detecta un tema
distinto en las palabras y el mismo en el fondo. Esa comprobación es tuya.

---

## 3. Esquema de una lección

```json
{
  "id": "geo-0006",
  "category": "geopolitica",
  "title": "≤ 80 caracteres",
  "subtitle": "≤ 130 caracteres, una frase evocadora",
  "cover_image": {
    "query": "2-4 palabras EN INGLÉS, concreto y fotografiable",
    "wikipedia": "Título exacto del artículo de Wikipedia en español"
  },
  "cards": [{ "heading": "≤ 5 palabras", "text": "35-90 palabras" }],
  "key_fact": "≤ 220 caracteres",
  "questions": [
    { "q": "…", "options": ["a","b","c","d"], "correct": 0, "note": "1-2 frases" }
  ]
}
```

Los prefijos de `id` por categoría están en `config/categories.py`. Numera
correlativamente a partir del último existente. **No pongas `url`, `credit` ni
`license`**: los rellena `fetch_images.py`.

Pon siempre `"correct": 0` al escribir; el barajado lo reasigna después.

---

## 4. Lector y tono

Adulto, universitario, español. Lee prensa internacional. No sabe nada concreto
del tema pero no es tonto: no le expliques qué es el PIB ni quién fue Napoleón.
Sí explícale cualquier término técnico propio de la materia, la primera vez que
aparezca, en la misma frase y sin paréntesis didácticos.

**Divulgación culta.** El registro de un buen artículo largo de prensa seria:
preciso, con criterio, sin condescendencia. Prosa completa y afirmativa.

Prohibido: «¿Sabías que…?», signos de exclamación, emojis, segunda persona
interpelativa («imagina que estás…»), preguntas retóricas de apertura, y cerrar
la lección con una moraleja o una invitación a reflexionar. El lector saca sus
propias conclusiones.

Una lección se lee en cinco minutos y deja **una idea** que sirva para entender
otra cosa distinta mañana. No es una acumulación de curiosidades.

---

## 5. Las tarjetas

Entre 3 y 5. Cada una es una diapositiva autónoma que se lee en 10-15 segundos:
45-75 palabras es el punto cómodo (el validador acepta 35-90).

**La regla dura:** cada tarjeta es UNA idea completa, no un fragmento de texto
continuo cortado por longitud. Si la tarjeta 3 no se entiende leyéndola sola,
está mal cortada. Prueba: si quitas cualquier tarjeta intermedia, las demás
deben seguir teniendo sentido individual aunque el conjunto pierda.

Arco recomendado: (1) la situación o el problema, (2)-(3) el mecanismo o el
desarrollo, con la sustancia, (4) la consecuencia o lo que cambió, (5) opcional:
la controversia abierta o lo que sigue sin resolverse.

Los `heading` son etiquetas de 2 a 5 palabras, no titulares de periódico.

---

## 6. Rigor

Toda cifra, fecha o nombre propio debe ser correcto. Si no estás seguro de una
cifra exacta, usa el orden de magnitud («cerca de dos millones») en vez de
inventar precisión. Nunca atribuyas una cita si no estás seguro de la autoría.

En temas con disputa historiográfica o científica real, **presenta la disputa
como tal en vez de zanjarla**. Las mejores lecciones del banco lo hacen: la
identificación de Cortés con Quetzalcóatl como probable construcción posterior,
el ruido en los datos del eclipse de 1919, la discusión sobre si Arendt fue
engañada por la estrategia defensiva de Eichmann.

Prioriza lo que explica un mecanismo sobre lo que solo aporta un dato llamativo.

---

## 7. El quiz

Cuatro preguntas que comprueben comprensión, no memoria literal. Al menos dos
deben exigir aplicar o inferir algo, no recuperar un dato.

Las cuatro opciones deben ser plausibles para alguien que no ha leído la
lección: los distractores son errores razonables, no relleno. Prohibido «todas
las anteriores», «ninguna de las anteriores» y opciones de longitud
delatoramente distinta a las demás.

El campo `note` explica en 1-2 frases **por qué** la correcta lo es —
información nueva o un matiz, no una repetición de la tarjeta. Cuando un
distractor sea un error frecuente, aprovéchalo para desmontarlo ahí.

---

## 8. Diversidad

Los temas deben repartirse deliberadamente en geografía y época. **Como mínimo
un tercio fuera de Europa y Norteamérica.** El banco ya tiene el Imperio de
Malí, Haití, Anansi, Quetzalcóatl, el Genji monogatari, Japón y el mar de China
Meridional: mantén esa proporción en lugar de dejar que la tanda derive hacia
lo europeo por inercia.

Mezcla registros dentro de cada categoría: acontecimientos, conceptos, personas,
procesos estructurales y controversias abiertas.

---

## 9. Cosas que no debe hacer la tarea automática

- **No tocar `data/progress.json`.** Es el progreso del usuario.
- **No modificar lecciones ya existentes** salvo para corregir un error de hecho.
- **No cambiar `config/categories.py`**: ni los objetivos, ni las frecuencias, ni
  dar de alta o de baja categorías. Eso lo decide Lucas.
- **No renombrar ids de lecciones.** El progreso del usuario guarda los ids tal
  cual, así que renombrarlos deja huérfano su historial. Los ids `art-*`, `lit-*`
  y `mit-*` siguen existiendo dentro de `humanidades` por esa razón.
- **No hacer `git push`.** Sí hay remoto (`origin` → `cultura-general`), pero el
  push lo hace Lucas desde GitHub Desktop. Deja el commit hecho y nada más.
- Si `validate_bank.py` termina con errores, **corrígelos antes de commitear**.
  Nunca commitees un banco que no valida.
