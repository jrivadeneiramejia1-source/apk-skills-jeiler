---
name: web-a-apk
description: Guía para convertir una app web o PWA en una app de Android (APK o AAB). Ayuda a elegir el camino (PWA instalable, Capacitor o TWA), preparar la web, construir el APK sin computador propio usando GitHub Actions, firmarlo y probarlo en el teléfono. Usar cuando el usuario diga "quiero esto como APK", "una app para Android", "instalarla en el teléfono sin el navegador", "subirla a Play Store" o "convertir mi web en app".
---

# De app web a APK

Objetivo: que una web que ya funciona se instale en Android como una app, con el menor trabajo y sin tocar claves por accidente.

## Reglas
- Nunca pedir ni guardar contraseñas ni archivos de firma (keystore). El usuario los crea y los guarda él mismo en los «Secrets» (secretos) de GitHub.
- Nunca subir el keystore al repositorio.
- Antes de construir, la web tiene que pasar la skill `verificar-app` (en `app-skills-jeiler`).
- Las versiones cambian: **leer las versiones que genera Capacitor en `android/` y la documentación oficial**, no copiar números de memoria. Los de abajo son los observados el 2026-11-04.
- Aceptar las licencias del SDK de Android en el flujo solo si el dueño del repo lo autorizó.
- Lo que no se pudo construir o probar, decirlo.

## Paso 1: elegir el camino
| Quiero... | Camino |
|---|---|
| Instalarla en mi teléfono, con icono, sin tienda | **PWA instalable** (manifest + service worker + HTTPS). No hace falta APK. Ver `pwa-completa`. |
| Un APK con la web adentro, que abra sin internet o use funciones del teléfono | **Capacitor** (probado, ver abajo) |
| Un APK que solo abre mi sitio ya publicado, para Play Store | **TWA** (Trusted Web Activity) con Bubblewrap o PWABuilder. **No se probó.** Exige un dominio con HTTPS y publicar el archivo `assetlinks.json` en la raíz del dominio (`/.well-known/assetlinks.json`); con una página de proyecto de GitHub Pages (`usuario.github.io/repo`) la raíz no es del proyecto. Confirmar en la documentación de Bubblewrap |
| Una app nativa o con React Native, Flutter o Compose | No es conversión: usar las otras skills de este repo |

Si hay duda, empezar por la PWA instalable: es lo más barato y se puede mejorar después.

## Paso 2: preparar la web
- `manifest.webmanifest` completo: nombre, `start_url`, `display: standalone`, colores, iconos de 192 y 512 px (con versión `maskable`).
- Service worker que deje abrir sin conexión, si hace falta.
- **Rutas relativas.** Dentro del APK la web se sirve desde `https://localhost/`: una ruta que empieza con `/` y asume una subcarpeta se rompe.
- Si la página tiene una política de seguridad de contenido (CSP), debe permitir `'self'` (que dentro del APK es `https://localhost`) y los servidores externos que use.
- Pantallas de 360 px y botones táctiles de 44 px o más.

## Paso 3: Capacitor (probado)
Orden, con los comandos de Capacitor 8:
1. `npm install @capacitor/core @capacitor/android` y `npm install -D @capacitor/cli`.
2. Archivo `capacitor.config.json` con tres datos: `appId` único (por ejemplo `com.nombre.miapp`), `appName` y `webDir` (la carpeta con el `index.html` ya listo).
3. `npx cap add android`: crea la carpeta `android/`. **Se sube al repositorio.**
4. `npx cap sync android`: copia la web al proyecto de Android. Se repite cada vez que cambia la web.
5. Revisar `android/app/src/main/AndroidManifest.xml`: solo debe tener los permisos que la app usa (por defecto, solo `INTERNET`).
6. Construir: dentro de `android/`, `./gradlew assembleDebug`. El APK queda en `android/app/build/outputs/apk/debug/app-debug.apk`.

**Lo que pidió Capacitor 8.6.0** (observado): Node 22 o más, **Java 21**, Gradle 8.14.3 (lo trae el proyecto), plugin de Android de Gradle 8.13.0, `compileSdk` y `targetSdk` 36, `minSdk` 24.

## Paso 4: construir sin computador propio (probado)
El APK se construye en GitHub Actions y se baja como «artefacto». Hay un flujo completo y probado en la plantilla de la skill `pruebas-maestro` (`plantilla/.github/workflows/apk.yml`). Pasos del trabajo de construcción:
1. Descargar el código (`actions/checkout`).
2. Preparar Node 22 (`actions/setup-node`) y Java 21 (`actions/setup-java`, distribución `temurin`).
3. `npm ci` y `npx cap sync android`.
4. Aceptar las licencias del SDK (el servidor de GitHub ya trae el SDK de Android; si hace falta, `sdkmanager --licenses`).
5. `./gradlew assembleDebug --no-daemon` en la carpeta `android/`.
6. Subir el APK con `actions/upload-artifact`.

En la prueba, la construcción tardó **2 minutos y 16 segundos**. Para el servidor de GitHub que pide el repo privado puede haber cola de varios minutos.
Antes de usar versiones de las acciones (`@v7`, etc.), comprobar que existan; las del flujo se verificaron el 2026-11-04.

## Paso 5: firmar y publicar
- **Para probar:** el APK `debug` se instala en el teléfono activando «instalar apps de origen desconocido».
- **Para publicar en Play Store:** Google pide un paquete AAB firmado (`./gradlew bundleRelease`). Conviene activar «Play App Signing», para que Google guarde la clave de la app. Perder el keystore sin eso significa no poder actualizar la app.
- El keystore se crea con `keytool` en el computador o servidor **del usuario**; su contraseña y el archivo (en base64) van a los Secrets de GitHub, nunca al repositorio.
- Usar la skill `play-policy-insights` (revisión de las políticas de Google Play) antes de subir.
- **No se probó** la construcción firmada `release`.

## Paso 6: probar
1. Automáticamente, en un emulador: skill `pruebas-maestro`.
2. A mano, en el teléfono: instalar el APK y pasar la skill `verificar-apk`.

## Señales de alerta
- Rutas que funcionan en el navegador y fallan dentro del APK.
- Un keystore o una contraseña escritos en un archivo del repo.
- Permisos de más (cámara, ubicación, contactos) que la app no usa.
- Una app que solo funciona con internet cuando debía abrir sin conexión.
- Una prueba que «pasa» pero nunca abrió la app (ver `pruebas-maestro`).

## Verificación
- [ ] La web pasó `verificar-app`.
- [ ] El camino elegido está explicado al usuario en pocas palabras.
- [ ] Ningún secreto está dentro del repo.
- [ ] El APK se construyó en Actions y se instaló y abrió en un emulador o teléfono, o se dijo que no se pudo probar.
