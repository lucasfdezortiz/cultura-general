# LF Global Capital

Banco de conocimiento diario. Cada día sirve una lección por categoría activa:
portada, tres a cinco tarjetas de contenido, un dato clave y un quiz de cuatro
preguntas con corrección inmediata. Lleva racha, porcentaje de completado y
accuracy por categoría.

**Coste de funcionamiento: 0 €.** No hay llamadas a ninguna API de pago, ni en
despliegue ni en tiempo de ejecución. La app solo lee un JSON y escribe el
progreso.

---

## Cómo funciona

```
data/lessons_bank.json  →  la app lo lee (nunca lo escribe)
data/progress.json      →  la app lo escribe (local o Gist privado)
```

El banco se amplía **desde Claude Code**, no desde la aplicación. Cuando el
porcentaje de completado se acerca al 100 % o el sidebar avisa de que quedan
menos de 15 días en alguna categoría, se le pide a Claude una tanda nueva y se
añade al JSON.

La selección diaria es determinista: para cada categoría activa se toma la
siguiente lección no vista según un orden estable derivado de un hash de
`(categoría, id)`. Recargar la página el mismo día devuelve exactamente lo
mismo, y el paquete queda anclado en `progress.json` la primera vez que se
consulta, de modo que completar una lección no reordena el resto del día.

---

## Ejecutar en local

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Desplegar en Streamlit Community Cloud

1. Sube el repo a GitHub.
2. En share.streamlit.io: **New app** → elige el repo → archivo principal `app.py`.
3. Despliega. No hace falta configurar nada más para que funcione.

### Que el progreso sobreviva a los reinicios

El disco de Streamlit Cloud es **efímero**: cuando la app se duerme por
inactividad o se redespliega, `data/progress.json` vuelve al estado del último
commit y se pierden la racha y el avance.

Para evitarlo, la app usa un Gist privado si encuentra las credenciales. Es
gratis y son cinco minutos:

1. Crea un Gist **privado** en <https://gist.github.com> con un archivo llamado
   exactamente `progress.json` y contenido `{}`. Apunta el id (la parte final
   de la URL).
2. Crea un token en <https://github.com/settings/tokens> con el permiso `gist`
   y nada más.
3. En la app desplegada: **Settings → Secrets**, y pega:

   ```toml
   github_token = "ghp_tu_token"
   gist_id = "el_id_del_gist"
   ```

Sin esos secrets la app funciona igual, pero guardando en disco local. El
sidebar indica en todo momento qué backend está en uso.

> El token es tuyo y no debe compartirse ni subirse al repo. `.gitignore` ya
> excluye `.streamlit/secrets.toml`.

---

## Ampliar el banco

El flujo es: escribir lecciones → validar → resolver portadas → commit.

### 1. Escribir

Se añaden objetos al array `lecciones` de `data/lessons_bank.json`:

```json
{
  "id": "geo-0003",
  "category": "geopolitica",
  "title": "…",
  "subtitle": "…",
  "cover_image": { "query": "palabras en inglés", "wikipedia": "Artículo de Wikipedia" },
  "cards": [{ "heading": "…", "text": "…" }],
  "key_fact": "…",
  "questions": [{ "q": "…", "options": ["a","b","c","d"], "correct": 0, "note": "…" }]
}
```

Los prefijos de `id` por categoría están en `config/categories.py`.

### 2. Validar

```bash
python scripts/validate_bank.py
```

Comprueba esquema, ids y títulos duplicados, número y longitud de tarjetas,
headings demasiado largos, opciones repetidas, fórmulas prohibidas y reparto de
la posición de la respuesta correcta.

```bash
python scripts/validate_bank.py --fix-shuffle
```

Baraja las opciones de cada pregunta con una semilla derivada del `id`. **Esto
hay que ejecutarlo siempre**: los modelos de lenguaje colocan la respuesta
correcta en la primera posición mucho más a menudo de lo que saldría por azar.
En el lote inicial el reparto era 100 % en la posición 0 y quedó en 17/27/30/27.

### 3. Portadas

```bash
python scripts/fetch_images.py            # solo las que falten
python scripts/fetch_images.py --only historia
python scripts/fetch_images.py --force    # rehacer todas
```

Resuelve la imagen en cuatro pasos, deteniéndose en el primero que acierte:

1. Imagen principal del artículo de Wikipedia indicado en `cover_image.wikipedia`.
2. Búsqueda por `query` en Wikipedia (español y luego inglés).
3. Búsqueda por `query` en Wikimedia Commons.
4. Búsqueda por `query` en Openverse, que suele cubrir los conceptos abstractos
   donde las anteriores fallan.

Guarda la URL, la autoría, la licencia y el enlace a la ficha del archivo, que
es lo que exige la atribución. Si ninguna vía acierta, la app pinta un degradado
con el color de la categoría; nunca se rompe por una imagen ausente.

**Wikimedia limita las peticiones por segundo, no el total.** No hay techo en
el tamaño del banco: pedir 360 portadas solo tarda más que pedir 16. El script
hace una pausa de un segundo entre llamadas y reintenta con espera creciente
ante un `429`. Es idempotente y guarda cada diez lecciones, así que si se corta
basta con volver a lanzarlo. Para 360 lecciones cuenta con 20-30 minutos
desatendidos.

### 4. Salud del banco

```python
from core.bank import cargar_banco, check_bank_health, informe_salud
```

`check_bank_health()` calcula, para cada categoría activa, cuántas lecciones
quedan pendientes y cuántos días de paquete diario garantizan. Devuelve
`avisos` con las que están por debajo del umbral de 15 días. La app muestra ese
aviso en el sidebar y bajo el paquete del día.

---

## Estructura

```
app.py                  Router de pantallas
config/categories.py    Categorías, pesos, objetivos, colores
core/bank.py            Carga del banco, estadísticas, salud
core/selection.py       Paquete del día, orden determinista, anclaje
core/progress.py        Racha, accuracy, histórico
core/storage.py         Backend local o Gist
ui/styles.py            CSS inyectado
ui/components.py        Piezas visuales
ui/screens.py           Pantallas: hoy, lección, quiz, resultado, historial
scripts/                Validador y resolutor de portadas
data/                   Banco y progreso
```

`core/` no importa `streamlit`: la lógica de selección y racha se puede probar
con un script suelto sin levantar la app.

---

## Personalización

Desde el sidebar, en caliente:

- **Tema claro u oscuro.** Dos paletas completas, no un filtro: cada una define
  sus propios colores de texto, bordes, fondos, verdes y rojos del quiz, y se
  aplican también a los componentes nativos de Streamlit (botones, pestañas,
  avisos, barra de progreso). La elección se guarda en el progreso, así que
  persiste entre sesiones.
- Activar o desactivar categorías. Una categoría desactivada deja de aparecer
  en el paquete del día.
- Marcar una categoría como **dominada**: sigue apareciendo, pero al final del
  paquete.

Desde `config/categories.py`, editando el archivo:

- `objetivo`: cuántas lecciones debería tener esa categoría en el banco.
- `peso`: intención relativa, usada para dimensionar las tandas nuevas.
- `por_dia`: cuántas lecciones de esa categoría entran en el paquete diario
  (por defecto 1).

---

## Notas de diseño

- **El paquete del día no se recalcula.** Una vez anclado, completar una
  lección no trae la siguiente de esa misma categoría al mismo día. Lo único
  que puede ampliarlo es activar una categoría que aún no estuviera
  representada.
- **La racha se calcula, no se acumula.** `racha_actual` y `racha_maxima` se
  derivan del histórico de días en cada consulta, de modo que una escritura
  perdida no puede dejar el contador desincronizado.
- **Las lecciones "extra"** (las de *Seguir aprendiendo*, más allá del paquete
  diario) suman al porcentaje de completado pero no afectan al sello de racha.
- **El historial sobrevive a las ampliaciones del banco.** Se guarda por id de
  lección, no por posición, y se agrupa por tema al mostrarlo. Añadir una tanda
  nueva al banco no toca nada de lo ya completado; incluso si una lección se
  retirase del banco, su registro seguiría contando en el histórico y en el
  porcentaje.
