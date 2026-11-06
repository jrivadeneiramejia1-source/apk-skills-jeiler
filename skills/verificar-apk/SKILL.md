---
name: verificar-apk
description: Verifica una app de Android (APK o AAB) antes de entregarla o publicarla. Revisa instalación, permisos, botón Atrás, rotación, pantallas pequeñas, modo oscuro, sin conexión, tamaño, seguridad y privacidad, e intenta romperla. Usar cuando haya un APK listo, cuando el usuario diga "prueba el APK", "revisa la app de Android", "verifica que no falle en el teléfono" o antes de subir a Play Store.
---

# Verificar una app de Android

Objetivo: encontrar los fallos antes que el usuario. Nada se da por bueno sin evidencia (comando corrido, captura, mensaje real).

## Reglas
- Probar solo apps del usuario, en un emulador o en su teléfono. No tocar datos reales sin avisar.
- No pedir ni guardar claves ni contraseñas. Si aparece una clave dentro del APK, avisar sin copiarla.
- Primero el informe; los arreglos se hacen después, con permiso, uno por vez.
- Decir qué NO se pudo probar (por ejemplo: teléfono real, Bluetooth, sensores, llamadas).
- La parte web de la app se prueba también con `verificar-app`.

## Paso 0: revisar el proyecto ANTES de construir (automático)
Si el proyecto está en una carpeta (Capacitor, Compose, React Native…), correr el revisor. Es solo Python, no construye nada, no abre redes y no muestra claves:
```
python -I skills\verificar-apk\scripts\revisar_android.py CARPETA-DEL-PROYECTO
```
Salida 0 = sin hallazgos graves; 1 = hay ALTA; 2 = no encontró un proyecto. Avisa: `debuggable`, `exported` que falta, provider exportado, tráfico http, permisos que Google Play restringe, `targetSdk` menor que el que Play exige (36 desde 2026-08-31), contraseñas de firma escritas, llaves `.jks` sin ignorar, claves escritas, `server.url` de Capacitor, y fallos comunes en los flujos de GitHub Actions (acciones sin versión, `echo` de secretos, inyección por títulos de PR, sin permisos mínimos ni caché de Gradle).
Arreglar las ALTA antes de gastar minutos de Actions. Cada regla y su fuente: `references/reglas.md`. Ejemplos bueno y malo: `ejemplos/`. **No reemplaza** probar el APK ya construido (pasos siguientes).

## Paso 0b: revisar el APK ya construido (lo que de verdad lleva dentro)
El manifiesto final del APK puede traer cosas que no están en tu código (permisos o componentes que agregan las librerías). Para verlo sin ejecutar nada:
1. Decodificar con `apktool` (Apache-2.0; hace falta Java): `apktool d MI-APP.apk -o SALIDA`. Solo APK **tuyos o de código abierto**.
2. `python -I skills\verificar-apk\scripts\revisar_android.py SALIDA` (lee el manifiesto decodificado y `apktool.yml` para el `targetSdk`; ignora el manifiesto binario de `original/`).
3. Alternativa pasiva con **REA** (herramienta de ingeniería inversa de tu fork `rea.-`): `rea decode-android-resources MI-APP.apk` entrega el manifiesto y las cadenas sin escribir archivos (necesita `REA_APKTOOL_COMMAND` apuntando a `apktool`).
4. La web que va dentro está en `SALIDA/assets/public`: compararla con tu carpeta (`diff -rq`) y pasarle `revisar_pwa.py` (en `app-skills-jeiler`).
Un APK **debug** siempre sale con `debuggable=true` (A01): es normal; en el que publicas debe ser `false`. Medido sobre el APK de la plantilla: ver `PRUEBAS.md`. Herramientas, versiones y revisión de seguridad: `references/herramientas.md`.

## Paso 0c: revisar los flujos de GitHub Actions con dos herramientas abiertas
Copiar `plantilla/revisar-flujos.yml` a `.github/workflows/`: corre `actionlint` (errores de escritura) y `zizmor` (seguridad: disparadores peligrosos, inyección, permisos de más, acciones sin fijar a un commit). La plantilla pasa las dos sin hallazgos, incluso con `zizmor --persona pedantic`. Para fijar una acción a su commit: `git ls-remote --tags https://github.com/DUEÑO/ACCION`. Complementan a las reglas W del revisor (que sí conocen Gradle, `timeout-minutes` y `echo` de secretos).

## Proceso
1. **Identificar el archivo.** APK o AAB, `debug` o `release`, versión, tamaño. Si hay herramientas de Android disponibles (`aapt`, `apksigner`), leer el nombre del paquete, la versión y los permisos declarados; si no, decirlo.
2. **Instalar y abrir.** Primer arranque sin datos guardados. ¿Abre rápido? ¿Se cierra solo? ¿Pide permisos al abrir o solo cuando los necesita, con un texto claro?
3. **Recorrer los 3 flujos principales** con capturas.
4. **Intentar romperla:**
   - botón Atrás en cada pantalla (¿sale de la app sin querer? ¿pierde lo escrito?);
   - rotar la pantalla en medio de un formulario;
   - pantalla pequeña y letra grande del sistema;
   - modo oscuro;
   - sin conexión y con conexión lenta;
   - mandarla a segundo plano, volver, y cerrarla y abrirla de nuevo;
   - tocar rápido varias veces;
   - negar un permiso: la app debe seguir funcionando y explicar qué falta.
5. **Seguridad y privacidad.** Usar la skill `security-audit`. Para privacidad, listar qué datos recoge la app y comprobar que exista una política de privacidad y que los textos de la app digan lo mismo que hace el código. Buscar claves o tokens dentro del APK (descomprimirlo y buscar texto como `api_key`, `secret`, `token`, `AIza`), comprobar que la versión `release` no sea depurable (`debuggable`), que el tráfico sea HTTPS y que los permisos pedidos sean solo los necesarios.
6. **Calidad.** `android-testing` y `kotlin-quality` si hay código nativo; `react-native-best-practices` si usa React Native; `compose-ui` si usa Compose.
7. **Antes de publicar.** Pasar la skill `play-policy-insights` (revisión de las políticas de Google Play).
8. **Informe.** Tabla: **Probado y bien**, **Falló**, **No se pudo probar (y por qué)**. Cada fallo con pasos para repetirlo, gravedad (alta, media, baja) y arreglo sugerido.

## Señales de alerta
- «En el emulador funciona» sin haberlo probado en un teléfono real.
- Un permiso peligroso (ubicación, cámara, contactos) que la app no usa.
- Una clave dentro del APK.
- Una app `release` instalada que todavía muestra mensajes de depuración.

## Verificación final
- [ ] Se instaló y abrió el archivo.
- [ ] Se recorrieron los flujos principales.
- [ ] Se intentó romperla con Atrás, rotación, sin conexión y permisos negados.
- [ ] Se revisó seguridad y privacidad.
- [ ] El informe dice qué quedó sin probar.
