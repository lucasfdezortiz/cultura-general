# Guía de redacción y ampliación del banco

Este archivo es la referencia para escribir lecciones nuevas. La tarea semanal
programada lo lee y lo sigue, así que **editarlo aquí cambia el criterio de
todas las tandas futuras**.

---

## 1. Procedimiento de una tanda

```bash
cd ~/lf-global-capital

# 1. Ver qué categorías van más justas
python3 -c "
import sys; sys.path.insert(0,'.')
from core import bank, progress as P
b = bank.cargar_banco(); pr = P.cargar()
print(bank.informe_salud(bank.check_bank_health(b, P.ids_completadas(pr), P.categorias_activas(pr))))"

# 2. Escribir data/tandas/tanda-NN.json  (NN = siguiente número libre)
# 3. Fusionar, validar y resolver portadas
python3 scripts/merge_batch.py data/tandas/tanda-NN.json
python3 scripts/validate_bank.py --fix-shuffle
python3 scripts/fetch_images.py

# 4. Confirmar que queda limpio y commitear
python3 scripts/validate_bank.py
git add -A && git commit -m "Tanda NN: N lecciones"
```

**Tamaño de tanda: 20-24 lecciones.** Reparto: al menos una por categoría, y el
resto para las que menos días de reserva tengan según el informe de salud. No
escribas la tanda entera de una categoría sola.

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
- **No cambiar `config/categories.py`** ni los objetivos por categoría.
- **No hacer `git push`.** No hay remoto configurado; los commits quedan locales.
- Si `validate_bank.py` termina con errores, **corrígelos antes de commitear**.
  Nunca commitees un banco que no valida.
