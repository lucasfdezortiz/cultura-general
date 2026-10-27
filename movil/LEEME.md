# Icono propio en la pantalla de inicio

## El problema, con la causa exacta

El icono que iOS pone al añadir algo a la pantalla de inicio sale de la etiqueta
`apple-touch-icon` **del documento que se añade**. En el despliegue, ese
documento es de Streamlit:

```
<link rel="apple-touch-icon" href="https://…streamlit.app/-/build/favicon_256.png">
```

Y la app se sirve **dentro de un `<iframe>`**, así que su código no puede tocar
la cabecera de fuera. Por eso no hay forma de cambiar el icono desde el
repositorio de la app: no es cuestión de dar con la etiqueta correcta, es que
la etiqueta vive en otra página.

La solución es tener una página propia que sí controlemos, que es esta.

## Qué hace esta carpeta

`index.html` es una página mínima que:

- declara **tu** icono, **tu** nombre (`LF Capital`) y el color de fondo;
- se abre a pantalla completa, sin barra de Safari;
- incrusta la app con `?embed=true`, lo que **elimina el botón Fork y la
  insignia de Streamlit Cloud** (comprobado: con ese parámetro ni
  `stToolbarActions` ni `appCreatorAvatar` existen);
- reserva las zonas seguras del iPhone, porque dentro de un iframe
  `env(safe-area-inset-*)` vale 0 y la barra inferior se metería debajo del
  indicador de inicio;
- añade `compacto=1`, que le dice a la app que no reserve hueco para una
  insignia que ya no está.

## Pasos

### 1. Pon tu imagen

Guarda tu foto en esta carpeta como **`icono.png`**, cuadrada y de **1024×1024**
(vale 512×512). iOS le redondea las esquinas solo, así que no hace falta
prepararlas. Evita márgenes grandes: la imagen se ve pequeña si el motivo está
muy centrado.

### 2. Publícala, gratis

**La vía rápida — Netlify Drop** (sin repositorio, dos minutos):

1. Entra en <https://app.netlify.com/drop>
2. Arrastra **la carpeta `movil` entera**.
3. Te da una dirección del tipo `https://algo-aleatorio.netlify.app`. Esa es la
   que usarás. Puedes renombrarla en *Site settings → Change site name*.

**La vía con GitHub Pages:** el repositorio de la app es privado, y Pages en
repositorios privados es de pago. Así que haz un repositorio **público** nuevo
—solo lleva esta página y tu foto, nada sensible—, sube estos dos archivos y
actívalo en *Settings → Pages → Branch: main*.

### 3. Añádela a la pantalla de inicio

En el iPhone, abre esa dirección **en Safari** (no en Chrome: solo Safari
respeta `apple-touch-icon`) y pulsa **Compartir → Añadir a pantalla de inicio**.

Debe aparecer tu foto y el nombre *LF Capital*. Si sigue saliendo el logo de
Streamlit, es que abriste la dirección de `streamlit.app` en vez de la nueva.

### 4. Borra el icono viejo

El que apunta a `streamlit.app` ya no hace falta.

## La alternativa sin hosting

Con la app **Atajos** de iOS: *Nuevo atajo → Abrir URL* con la dirección de
Streamlit, le pones tu foto como icono y *Añadir a pantalla de inicio*. Icono y
nombre propios en cinco minutos y sin publicar nada.

El inconveniente: abre dentro de Safari, con la barra de direcciones a la vista,
y parpadea la app Atajos al lanzarlo. Por eso la página de esta carpeta es mejor
si no te importan los dos minutos de Netlify.

## Si cambias la dirección de la app

La URL de Streamlit está escrita en `index.html`, en el `src` del iframe.
