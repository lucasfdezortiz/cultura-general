#!/bin/bash
# La app arranca sola con el Mac (agente launchd com.lfglobalcapital.app).
# Este archivo solo sirve para consultar la dirección y comprobar que responde.
# Si estuviera parada, la vuelve a levantar.

AGENTE="com.lfglobalcapital.app"
PUERTO=8511
IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null)

clear
echo ""
echo "  LF Global Capital"
echo ""

if [ -z "$IP" ]; then
  echo "  No hay conexión de red. Conéctate a la wifi y vuelve a abrir esto."
  echo ""
  read -r -p "  Pulsa Enter para cerrar."
  exit 1
fi

estado=$(curl -s -o /dev/null -w "%{http_code}" --max-time 4 "http://127.0.0.1:$PUERTO")

if [ "$estado" != "200" ]; then
  echo "  La app no responde. Reiniciándola..."
  launchctl bootout "gui/$(id -u)/$AGENTE" 2>/dev/null
  sleep 1
  launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/$AGENTE.plist" 2>/dev/null
  for _ in $(seq 1 15); do
    sleep 1
    estado=$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 "http://127.0.0.1:$PUERTO")
    [ "$estado" = "200" ] && break
  done
fi

if [ "$estado" = "200" ]; then
  echo "  Funcionando. Ábrela en el móvil, estando en la misma wifi:"
  echo ""
  echo "      http://$IP:$PUERTO"
  echo ""
  echo "  En iPhone: Compartir → Añadir a pantalla de inicio."
  echo "  Queda como un icono y se abre a pantalla completa."
  echo ""
  echo "  No hace falta dejar esta ventana abierta: la app arranca sola"
  echo "  con el Mac y se relanza si se cae."
else
  echo "  No arranca. Revisa el registro:"
  echo "      ~/lf-global-capital/data/servidor.log"
fi

echo ""
read -r -p "  Pulsa Enter para cerrar."
