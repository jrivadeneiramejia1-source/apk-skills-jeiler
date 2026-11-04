---
name: pruebas-maestro
description: Prueba una app de Android (APK) automáticamente en un emulador dentro de GitHub Actions, con flujos de Maestro escritos en YAML, sin computador propio. Instala Maestro con versión y huella fijas, arranca el emulador, instala el APK, corre los flujos y guarda el informe y las capturas. Usar cuando el usuario diga "prueba el APK solo", "pruebas automáticas de la app", "Maestro", "que se pruebe en un emulador" o después de construir un APK con web-a-apk.
---

# Pruebas de Android con Maestro en GitHub Actions

Maestro es una herramienta que maneja una app como lo haría una persona: la abre, toca botones, escribe y comprueba lo que se ve. Los flujos son archivos YAML cortos en la carpeta `.maestro/`.

La plantilla está en `plantilla/` dentro de esta skill (un flujo de Actions y un flujo de Maestro de ejemplo). Se probó en un repo de prueba (ver «Qué se probó»).

## Reglas
- **No comprobar el nombre de la app.** El nombre también aparece en la pantalla de inicio del teléfono: la prueba pasa aunque la app ni abra. Comprobar un texto que **solo existe dentro de la app**.
- **Tras cada prueba, mirar la captura y la jerarquía** del informe, no solo el «pasó» o «falló».
- No pedir ni guardar claves. Las pruebas usan datos inventados.
- **Maestro con versión y huella fijas.** Maestro no publica una huella oficial: se calcula la del archivo de la versión elegida (`sha256sum maestro.zip`) y se anota en el flujo. Si se cambia la versión, hay que calcular una nueva.
- Aceptar la licencia del SDK de Android en el flujo solo si el dueño del repo lo autorizó.
- Decir qué no se pudo probar (teléfono real, Bluetooth, cámara, notificaciones).

## Proceso
1. **Tener un APK `debug`** (skill `web-a-apk`). El flujo de la plantilla lo construye y lo pasa al trabajo de pruebas como «artefacto».
2. **Copiar la plantilla:** `.github/workflows/apk.yml` y `.maestro/abrir-app.yaml`. Cambiar `appId` por el de la app (está en `capacitor.config.json` o en `build.gradle`).
3. **Escribir el flujo.** Lo mínimo: abrir, esperar contenido propio de la app, usar el botón principal y comprobar el resultado.
   ```yaml
   appId: com.ejemplo.miapp
   ---
   - launchApp
   - extendedWaitUntil:
       visible: "Texto que solo existe dentro de la app"
       timeout: 30000
   - tapOn: "Botón principal"
   - assertVisible: "Resultado esperado"
   - takeScreenshot: despues-del-toque
   ```
4. **Subir a una rama y abrir un PR.** Nunca directo a `main`.
5. **Leer el resultado en la pestaña Actions.** Si falla, bajar el artefacto `informe-maestro`: trae `commands.json` (qué hizo Maestro y qué paso falló), `screenshots/` (la pantalla en el fallo), `screen-hierarchy/` (los elementos que Maestro veía) y `device-logcat.txt` (el registro del teléfono).
6. **Informe corto:** qué flujos pasaron, qué falló y por qué, y qué quedó sin probar.

## Qué se probó (2026-11-04, estado provisional)
- **Funcionó:** instalar Maestro 2.12.1 con la comprobación de la huella, activar KVM, arrancar un emulador de Android 14 en 59 segundos, instalar el APK (`Success`) y correr el flujo.
- **Falló (primera ejecución):** el flujo no pudo tocar el botón porque la app se cerró (ver abajo). Se corrigió la imagen del emulador y el flujo.
- **Pendiente de confirmar:** que la versión corregida de la plantilla (la de esta carpeta) pase de punta a punta. Este archivo se actualiza con el resultado.

## Lo aprendido al probarla
- **Emulador:** con la imagen «google_apis», un bloqueo de los Google Play Services (ANR) hizo que Android **matara la app** mientras se probaba. Usar la imagen `target: default` (sin Play Services).
- **Falso positivo:** la primera prueba pasó el paso «ver "Plantilla APK"» porque ese texto era el icono en la pantalla de inicio. La app ya estaba cerrada.
- **Tiempos:** el emulador arrancó en 59 segundos con aceleración (KVM); instalar el SDK y la imagen en el servidor de GitHub tardó unos 55 segundos más.
- **Cola:** en un repo privado, GitHub puede tardar varios minutos en asignar un servidor.
- **Costo:** el flujo completo usa varios minutos del servidor. En un repo privado esos minutos cuentan para el límite gratuito mensual del dueño; verificar el límite vigente.

## Señales de alerta
- Una prueba que «pasa» sin que la app esté en pantalla.
- Comprobar textos que también existen fuera de la app.
- Esperar siempre con tiempos fijos en vez de `extendedWaitUntil`.
- Cambiar la versión de Maestro sin recalcular la huella.

## Verificación
- [ ] El flujo comprueba un texto que solo existe dentro de la app.
- [ ] Se miró la captura del informe.
- [ ] La versión y la huella de Maestro coinciden.
- [ ] Se dijo qué no se probó.
