"""La fecha "de hoy" desde el punto de vista del usuario.

Streamlit Cloud ejecuta en UTC. Con Madrid en UTC+1 o UTC+2, usar `date.today()`
significa que entre medianoche y las dos de la madrugada el servidor sigue en el
día anterior: el paquete no cambiaría, y una lección hecha a la una contaría
como del día previo. Como la app se usa sobre todo antes de dormir, eso cae
justo en la franja peor.
"""

from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

ZONA = ZoneInfo("Europe/Madrid")


def hoy() -> date:
    """Fecha actual en la zona del usuario, no la del servidor."""
    return datetime.now(ZONA).date()
