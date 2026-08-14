#!/bin/bash
# Sube al repositorio los commits pendientes (las tandas semanales de lecciones).
# La PRIMERA vez pedirá usuario y token; macOS los guarda y ya no vuelve a pedirlos.

cd "$(dirname "$0")" || exit 1
clear
echo ""
echo "  LF Global Capital · subir cambios"
echo ""

pendientes=$(git log origin/main..HEAD --oneline 2>/dev/null | wc -l | tr -d ' ')

if [ "$pendientes" = "0" ]; then
  echo "  No hay nada pendiente de subir."
  echo ""
  read -r -p "  Pulsa Enter para cerrar."
  exit 0
fi

echo "  $pendientes commit(s) pendientes:"
echo ""
git log origin/main..HEAD --oneline | sed 's/^/      /'
echo ""
echo "  Si pide credenciales:"
echo "      Username: lucasfdezortiz"
echo "      Password: un token de github.com/settings/tokens con permiso 'repo'"
echo "                (NO la contraseña de GitHub: eso ya no funciona)"
echo ""

if git push; then
  echo ""
  echo "  Subido. Streamlit Cloud se actualizará en unos minutos."
else
  echo ""
  echo "  No se pudo subir. Alternativa: GitHub Desktop → Push origin."
fi

echo ""
read -r -p "  Pulsa Enter para cerrar."
