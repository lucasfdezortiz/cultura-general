#!/bin/bash
# Doble clic en este archivo para levantar la app en la red local.
# Después ábrela desde el móvil con la dirección que aparece en pantalla.
# El Mac tiene que quedarse encendido y en la misma wifi mientras la uses.

cd "$(dirname "$0")" || exit 1

IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null)
PUERTO=8511

if [ -z "$IP" ]; then
  echo "No se detecta una conexión de red. Conéctate a la wifi y vuelve a intentarlo."
  read -r -p "Pulsa Enter para cerrar."
  exit 1
fi

# Si ya había una instancia levantada, se cierra para no ocupar el puerto.
pkill -f "streamlit run app.py" 2>/dev/null
sleep 1

clear
cat <<BANNER

  LF Global Capital

  Abre esta dirección en el móvil:

      http://$IP:$PUERTO

  En iPhone, con la página abierta: Compartir → Añadir a pantalla de inicio.
  Queda como un icono y se abre a pantalla completa, sin barra del navegador.

  Deja esta ventana abierta mientras uses la app.
  Para cerrarla: Control + C

BANNER

exec python3 -m streamlit run app.py \
  --server.port "$PUERTO" \
  --server.address 0.0.0.0 \
  --server.headless true
