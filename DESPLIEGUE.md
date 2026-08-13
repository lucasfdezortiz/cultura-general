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
redespliega**. Sin esto perderías la racha y el porcentaje cada pocos días.

### 3a. Crear el Gist

1. Entra en <https://gist.github.com>.
2. Nombre del archivo: `progress.json`
3. Contenido: `{}`  (dos llaves, nada más)
4. Botón **Create secret gist** (secret, no público).
5. Copia el **id** de la URL: en
   `https://gist.github.com/lucasfdezortiz/a1b2c3d4e5f6...`
   el id es `a1b2c3d4e5f6...`

### 3b. Crear el token

1. Entra en <https://github.com/settings/tokens?type=beta> →
   **Generate new token**.
2. Token name: `lf-global-capital`
3. Expiration: **No expiration** (si no, tendrás que rehacerlo cada pocos meses).
4. Repository access: **Public Repositories (read-only)** basta.
5. En **Account permissions**, busca **Gists** y ponlo en **Read and write**.
   Es el único permiso que necesita.
6. **Generate token** y copia el valor. Solo se muestra una vez.

### 3c. Pegarlos en Streamlit

1. En <https://share.streamlit.io>, en tu app: **⋮ → Settings → Secrets**.
2. Pega exactamente esto, sustituyendo los valores:

   ```toml
   github_token = "github_pat_TU_TOKEN_AQUI"
   gist_id = "TU_GIST_ID_AQUI"
   ```

3. **Save**. La app se reinicia sola.

Comprobación: el aviso rojo desaparece y la barra lateral dice
*"Progreso guardado en Gist privado"*.

> Ese token es tuyo y no debe salir de ahí. No lo pegues en el repositorio ni me
> lo mandes por chat: `.gitignore` ya bloquea `.streamlit/secrets.toml` para que
> no se suba por accidente.

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
