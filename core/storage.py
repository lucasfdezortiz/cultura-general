"""Persistencia del progreso con doble backend.

- `LocalBackend`  : archivo JSON en disco. Funciona siempre, pero en Streamlit
                    Community Cloud el disco es efímero: se pierde cuando la app
                    se duerme o se redespliega.
- `GistBackend`   : Gist privado de GitHub. Sobrevive a reinicios y despliegues.
                    Se activa solo si existen los secrets `github_token` y
                    `gist_id`.

La app elige el backend automáticamente. No hace falta cambiar nada de código
para pasar de uno a otro: basta con añadir los secrets.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Protocol

import requests

RUTA_LOCAL = Path(__file__).resolve().parent.parent / "data" / "progress.json"
NOMBRE_ARCHIVO_GIST = "progress.json"
TIMEOUT = 10


class Backend(Protocol):
    nombre: str

    def load(self) -> dict[str, Any] | None: ...
    def save(self, data: dict[str, Any]) -> bool: ...


class LocalBackend:
    nombre = "local"

    def __init__(self, ruta: Path = RUTA_LOCAL):
        self.ruta = ruta

    def load(self) -> dict[str, Any] | None:
        if not self.ruta.exists():
            return None
        try:
            return json.loads(self.ruta.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None

    def save(self, data: dict[str, Any]) -> bool:
        try:
            self.ruta.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.ruta.with_suffix(".json.tmp")
            tmp.write_text(
                json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            tmp.replace(self.ruta)
            return True
        except OSError:
            return False


class GistBackend:
    nombre = "gist"

    def __init__(self, token: str, gist_id: str):
        self.token = token
        self.gist_id = gist_id
        self.url = f"https://api.github.com/gists/{gist_id}"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        # Respaldo local: si el Gist falla puntualmente no perdemos la sesión.
        self._espejo = LocalBackend()

    def load(self) -> dict[str, Any] | None:
        try:
            r = requests.get(self.url, headers=self.headers, timeout=TIMEOUT)
            r.raise_for_status()
            archivos = r.json().get("files", {})
            entrada = archivos.get(NOMBRE_ARCHIVO_GIST)
            if not entrada:
                return None
            # Gists grandes vienen truncados y hay que ir al raw_url.
            if entrada.get("truncated") and entrada.get("raw_url"):
                raw = requests.get(entrada["raw_url"], timeout=TIMEOUT)
                raw.raise_for_status()
                return json.loads(raw.text)
            return json.loads(entrada["content"])
        except Exception:
            # Persistir nunca debe tumbar la app: ante cualquier fallo se cae
            # al espejo local y la interfaz avisa de que no se está guardando.
            return self._espejo.load()

    def save(self, data: dict[str, Any]) -> bool:
        self._espejo.save(data)
        cuerpo = {
            "files": {
                NOMBRE_ARCHIVO_GIST: {
                    "content": json.dumps(data, ensure_ascii=False, indent=2)
                }
            }
        }
        try:
            r = requests.patch(
                self.url, headers=self.headers, json=cuerpo, timeout=TIMEOUT
            )
            r.raise_for_status()
            return True
        except Exception:
            return False


# Streamlit busca los secrets en el directorio de trabajo y en el home. En
# Streamlit Cloud el directorio de trabajo es el del repo, así que las tres
# rutas cubren tanto el local como el despliegue.
RUTAS_SECRETS = (
    Path.home() / ".streamlit" / "secrets.toml",
    Path(__file__).resolve().parent.parent / ".streamlit" / "secrets.toml",
    Path.cwd() / ".streamlit" / "secrets.toml",
)


def en_streamlit_cloud() -> bool:
    """Detecta Streamlit Community Cloud, que despliega bajo /mount/src.

    Importa porque allí el disco es efímero: si la app corre en la nube y el
    backend acaba siendo el local, el progreso se pierde en cada reinicio sin
    dar ningún aviso. La interfaz usa esto para señalarlo de forma visible.
    """
    return Path("/mount/src").exists()


def _hay_secrets() -> bool:
    """Comprueba el archivo antes de tocar st.secrets.

    Acceder a `st.secrets` sin archivo pinta un aviso en la interfaz, y como el
    backend se consulta varias veces por render aparecería repetido. Mirar el
    disco primero evita el aviso por completo.
    """
    return any(p.exists() for p in RUTAS_SECRETS)


def _leer_secret(clave: str) -> str | None:
    if not _hay_secrets():
        return None
    try:
        import streamlit as st

        valor = st.secrets.get(clave)
        return str(valor) if valor else None
    except Exception:
        return None


_BACKEND: Backend | None = None


def obtener_backend(recargar: bool = False) -> Backend:
    """GistBackend si hay credenciales, LocalBackend si no. Se resuelve una vez."""
    global _BACKEND
    if _BACKEND is not None and not recargar:
        return _BACKEND

    token = _leer_secret("github_token")
    gist_id = _leer_secret("gist_id")
    _BACKEND = GistBackend(token, gist_id) if (token and gist_id) else LocalBackend()
    return _BACKEND
