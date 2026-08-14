# Pasos para tener la app en el móvil

Todo lo demás está hecho. Esto es lo único que queda, y son unos veinte minutos.
Sigue el orden: cada paso depende del anterior.

El proyecto está en **`~/lf-global-capital`** (hay un acceso directo en el
Escritorio). Coste total: **0 €**.

---

## 1 · Subir el código a GitHub  ·  ~5 min

La vía sin escribir ningún token:

1. Descarga **GitHub Desktop** de <https://desktop.github.com> e instálalo.
2. Ábrelo y **Sign in to GitHub.com**. Se abre el navegador, inicias sesión ahí
   y vuelve solo. No hay que copiar ni pegar nada.
3. **File → Add Local Repository…** → elige la carpeta `lf-global-capital`
   (está en tu carpeta de usuario, no en el Escritorio).
   Debería detectar que ya es un repositorio git con 7 commits.
4. Arriba aparece **Publish repository**. Púlsalo.
   - Name: `lf-global-capital`
   - **Deja marcada la casilla `Keep this code private`.**
5. **Publish repository**.

Comprobación: en <https://github.com/lucasfdezortiz> debe aparecer el
repositorio con el candado de privado.

---

## 2 · Desplegar en Streamlit  ·  ~5 min

1. Entra en <https://share.streamlit.io> y **Continue with GitHub**. Autoriza el
   acceso cuando lo pida.
2. **Create app** → **Deploy a public app from a repository**.
3. Rellena:
   - Repository: `lucasfdezortiz/lf-global-capital`
   - Branch: `main`
   - Main file path: `app.py`
4. **Deploy**. Tarda dos o tres minutos en instalar dependencias.

Te queda una dirección del tipo
`https://lf-global-capital-xxxxx.streamlit.app`.

Al abrirla verás la app funcionando **y un aviso rojo en la barra lateral**
diciendo que el progreso no se está guardando. Es correcto: lo arregla el paso
siguiente.

---

## 3 · Que el progreso no se borre  ·  ~5 min

Streamlit Cloud **borra el disco cada vez que la app se duerme o se
redespliega**, y cada push provoca un redespliegue. Sin esto pierdes la racha y
el porcentaje constantemente. Es el paso que falta.

### 3a. Crear el Gist  (1 min)

1. Entra en <https://gist.github.com>.
2. **Gist description**: `progreso lf global capital` (da igual).
3. **Filename including extension**: `progress.json` ← el nombre importa, tiene
   que ser exactamente ese.
4. En el cuadro de contenido escribe dos llaves: `{}`
5. Despliega el botón verde de abajo y elige **Create secret gist**
   (secreto, no público).
6. Mira la URL. Será algo así:
   `https://gist.github.com/lucasfdezortiz/`**`4f3a9b2c1d8e7f6a5b4c3d2e1f0a9b8c`**
   Copia esa última parte: ese es el **gist_id**.

### 3b. Crear el token  (2 min)

Usa un token **clásico**, no uno de los nuevos de acceso preciso: para Gists es
un solo permiso y funciona seguro.

1. Entra en <https://github.com/settings/tokens/new>
2. **Note**: `lf global capital`
3. **Expiration**: `No expiration`
   (si pones caducidad, el día que expire dejará de guardarse el progreso)
4. En la lista de permisos marca **solo la casilla `gist`**. Nada más.
   No hace falta `repo` ni ningún otro.
5. Abajo del todo: **Generate token**.
6. Copia el valor que aparece. Empieza por `ghp_` y **solo se muestra una vez**.

### 3c. Pegarlos en Streamlit  (2 min)

1. Entra en <https://share.streamlit.io>, busca tu app y pulsa los tres puntos
   **⋮ → Settings → Secrets**.
2. Pega esto tal cual, cambiando los dos valores por los tuyos:

   ```toml
   github_token = "ghp_loquesea"
   gist_id = "4f3a9b2c1d8e7f6a5b4c3d2e1f0a9b8c"
   ```

   Con comillas dobles, un espacio a cada lado del `=`, y sin nada más.
3. **Save**. La app se reinicia sola en unos segundos.

### Comprobar que ha funcionado

Recarga la app. **El aviso rojo debe desaparecer.** Si abres la barra lateral y
bajas del todo, dirá *"Progreso guardado en Gist privado"*.

Prueba definitiva: completa una lección, recarga la página y comprueba que
sigue marcada como completada.

### Si sigue saliendo el aviso

| Qué pasa | Qué mirar |
|---|---|
| Sigue el aviso rojo | Los nombres de las claves: `github_token` y `gist_id`, en minúscula y tal cual |
| Sigue el aviso rojo | Que guardaste con **Save** y la app terminó de reiniciarse |
| Avisa de que no pudo guardar | El token no tiene el permiso `gist`, o caducó |
| Avisa de que no pudo guardar | El `gist_id` está mal copiado, o el Gist se creó sin el archivo `progress.json` |

> El token es tuyo y no debe salir de los ajustes de Streamlit. No lo pegues en
> el repositorio ni me lo mandes por chat: no lo necesito para nada.

---

## 4 · Ponerlo en la pantalla de inicio  ·  ~1 min

En el iPhone, abre la dirección de Streamlit en Safari y:

**Compartir → Añadir a pantalla de inicio**

Queda como un icono y se abre a pantalla completa, sin barra del navegador.
Ya funciona desde cualquier sitio, sin depender del Mac.

---

## 5 · Avísame

Cuando esté publicado, dímelo y activo el `git push` automático en la tarea
semanal. Sin eso, las lecciones que escriba los domingos se quedan en el Mac y
no llegan a la app del móvil.

---

## Si algo falla

| Síntoma | Causa probable |
|---|---|
| El despliegue falla al instalar | Revisa que `requirements.txt` esté en la raíz del repo |
| La app carga pero sin lecciones | `data/lessons_bank.json` no se subió: comprueba que no esté en `.gitignore` |
| Sigue el aviso rojo tras poner los secrets | Revisa que las claves se llamen exactamente `github_token` y `gist_id` |
| El progreso se pierde igual | El token no tiene permiso de **Gists: Read and write**, o el id del Gist está mal |
| "This app has gone to sleep" | Normal tras días sin usarla. Se despierta pulsando el botón; el progreso sigue en el Gist |

---

## Lo que ya está hecho y no tienes que tocar

- La app arranca sola con el Mac y se relanza si se cae
  (agente `com.lfglobalcapital.app`). Sirve en la red local mientras tanto.
- Cada domingo a las 8:48 se escribe una tanda de 20-24 lecciones nuevas,
  se validan, se resuelven las portadas y se commitea.
- El banco tiene 55 lecciones de 11 categorías, objetivo 470.
- El historial se conserva íntegro cada vez que el banco se amplía.
