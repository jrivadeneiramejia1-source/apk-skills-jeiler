---
name: web-a-apk
description: Guía para convertir una app web o PWA en una app de Android (APK o AAB). Ayuda a elegir el camino (PWA instalable, Capacitor o TWA), preparar la web, construir el APK sin computador propio usando GitHub Actions, firmarlo y probarlo en el teléfono. Usar cuando el usuario diga "quiero esto como APK", "una app para Android", "instalarla en el teléfono sin el navegador", "subirla a Play Store" o "convertir mi web en app".
---

# De app web a APK

Objetivo: que una web que ya funciona se instale en Android como una app, con el menor trabajo y sin tocar claves por accidente.

## Reglas
- Nunca pedir ni guardar contraseñas ni archivos de firma (keystore). El usuario los crea y los guarda él mismo en los «Secrets» (secretos) de GitHub.
- Nunca subir el keystore al repositorio.
- Antes de construir, la web tiene que pasar la skill `verificar-app`.
- Las versiones (Java, Gradle, Capacitor, Android) cambian: leer la documentación oficial de la versión elegida y no copiar números de memoria.
- Lo que no se pudo construir o probar, decirlo.

## Paso 1: elegir el camino
| Quiero... | Camino |
|---|---|
| Instalarla en mi teléfono, con icono, sin tienda | **PWA instalable** (manifest + service worker + HTTPS). No hace falta APK. |
| Un APK con la web adentro, que abra sin internet o use funciones del teléfono (archivos, cámara, Bluetooth) | **Capacitor** |
| Un APK que solo abre mi sitio ya publicado, para Play Store | **TWA** (Trusted Web Activity) con Bubblewrap o PWABuilder; exige sitio con HTTPS y archivo `assetlinks.json` |
| Una app nativa o con React Native, Flutter o Compose | No es conversión: usar las otras skills de este repo |

Si hay duda, empezar por la PWA instalable: es lo más barato y se puede mejorar después.

## Paso 2: preparar la web
- `manifest.webmanifest` completo: nombre, `start_url`, `display: standalone`, colores, iconos de 192 y 512 px (con versión `maskable`).
- Service worker que deje la app abrir sin conexión, si el usuario lo necesita.
- Rutas relativas: una web en GitHub Pages vive en una subcarpeta y las rutas que empiezan con `/` se rompen.
- Diseño para pantallas de 360 px y botones táctiles de 44 px o más.

## Paso 3: Capacitor (el camino más común)
Orden general (confirmar los comandos exactos en la documentación de Capacitor):
1. Instalar `@capacitor/core`, `@capacitor/cli` y `@capacitor/android` en el proyecto.
2. Iniciar Capacitor con un nombre, un `appId` único (por ejemplo `com.nombre.miapp`) y la carpeta `webDir` donde está el `index.html` ya listo.
3. Agregar la plataforma Android y sincronizar los archivos web.
4. Revisar los permisos en `AndroidManifest.xml`: solo los que la app usa de verdad.
5. Iconos y pantalla de inicio: usar la herramienta de activos de Capacitor, siguiendo su documentación.
6. Construir con Gradle: la variante `debug` sirve para probar; la `release` firmada, para publicar.

## Paso 4: construir sin computador propio
El APK se puede construir en GitHub Actions y bajarlo como «artefacto» (archivo generado). Esqueleto del flujo, **sin probar**:
1. Descargar el código.
2. Preparar Node y Java (la versión de Java que pida la versión de Capacitor).
3. Instalar dependencias, construir la web, sincronizar Capacitor.
4. Ejecutar Gradle en la carpeta `android`.
5. Subir el APK como artefacto.

La firma se hace con secretos de GitHub, nunca con archivos dentro del repo.

## Paso 5: firmar y publicar
- **Para probar:** el APK `debug` se instala en el teléfono activando «instalar apps de origen desconocido».
- **Para publicar en Play Store:** Google pide un paquete AAB firmado. Conviene activar «Play App Signing», para que Google guarde la clave de la app. Perder el keystore sin eso significa no poder actualizar la app.
- Usar la skill `play-store` (lista de requisitos y políticas) antes de subir.

## Paso 6: probar en el teléfono
Instalar el APK y pasar la skill `verificar-apk`.

## Señales de alerta
- Rutas que funcionan en el navegador y fallan dentro del APK.
- Un keystore o una contraseña escritos en un archivo del repo.
- Permisos de más (cámara, ubicación, contactos) que la app no usa.
- Una app que solo funciona con internet cuando debía abrir sin conexión.

## Verificación
- [ ] La web pasó `verificar-app`.
- [ ] El camino elegido está explicado al usuario en pocas palabras.
- [ ] Ningún secreto está dentro del repo.
- [ ] El APK se instaló y abrió en un teléfono, o se dijo que no se pudo probar.
