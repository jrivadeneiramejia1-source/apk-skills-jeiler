# Herramientas de terceros para revisar apps y flujos Android

Marcas: **[F]** fuente abierta citada · **[P]** regla práctica sin verificar · **[E]** hecha y medida aquí. Consultado el 2026-11-06.
Ninguna se copia a este repo: se descargan al usarlas. Solo licencias abiertas.

| Herramienta | Versión | Licencia | Origen | Para qué |
|---|---|---|---|---|
| Apktool | 3.0.3 | Apache-2.0 (`LICENSE.md` leído) | github.com/iBotPeaches/Apktool | Decodificar el manifiesto y los recursos de un APK |
| REA | 6.5.0 | MIT | tu fork `rea.-` (origen morluto/rea) | Mirar el APK y las páginas web por dentro, de forma pasiva |
| actionlint | 1.7.12 | MIT | github.com/rhysd/actionlint | Errores de escritura en flujos de Actions |
| zizmor | 1.32.0 | MIT (PyPI) | github.com/zizmorcore/zizmor | Seguridad de flujos de Actions |

## Apktool [E]
- `apktool_3.0.3.jar` (15.478.013 bytes) bajado de la página de versiones; **no publica una huella oficial**, así que se calculó la suya: `dbf930b076c6b9be08d57c449cacefc3bdd6b71ebd59b3066fc0e1f5b14f9423`. Comprobar que el archivo viene de la página oficial antes de usarlo.
- Proyecto muy conocido (miles de estrellas, activo en 2026). Se corre sin red y sobre APK propios.
- Se usó sobre el APK `debug` que construyó GitHub Actions para `pantilla-apk` (huella del artefacto verificada contra la que da GitHub). Resultado: `package com.jeiler.pantilla`, `minSdk` 24, `targetSdk` 36, permiso `INTERNET` más un permiso interno que agrega androidx (`DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION`, de firma, no peligroso), `allowBackup=true`, `debuggable=true` (APK debug). `revisar_android.py` sobre la carpeta decodificada: A01 (ALTA, esperado en un debug) y A03 (BAJA).
- La web que lleva el APK (`assets/public`) es **idéntica** a `www/` de la plantilla, más `cordova.js` y `cordova_plugins.js` que agrega Capacitor.

## REA con Apktool [E]
`export REA_APKTOOL_COMMAND=/ruta/a/apktool` y `rea inspect-apktool-client` (confirma versión 3.0.3). `rea decode-android-resources MI-APP.apk` devolvió el mismo manifiesto, `targetSdk` 36 y la huella del APK. REA **no instala** Apktool ni Java. Para ver el código (jadx, `inspect-android-class`…) hace falta un JAR aparte (`REA_JADX_MCP_JAR`): **no se probó**.

## actionlint y zizmor [E]
Medición el 2026-11-06 sobre los flujos de `pantilla-apk` antes de fijar las acciones: actionlint 0 avisos; zizmor **28 `unpinned-uses` y 9 `artipacked`**. Después de fijar cada acción a su commit y poner `persist-credentials: false`: zizmor **0**. Sobre el flujo malo de este repo (`ejemplos/proyecto-malo`) encuentran, entre los dos, lo que mi revisor también marca (`pull_request_target`, inyección por el título del PR, permisos de más, acciones sin fijar) y además dos cosas que **mi revisor no veía**: `artipacked` (el `checkout` deja las credenciales guardadas) y que la etiqueta `@v7` **no** es un commit fijo. Mi revisor, a su vez, marca lo propio de Android (Gradle sin caché, `timeout-minutes`, `echo` de secretos). Son complementarios.
- Tropiezo útil: mi ejemplo malo **no era YAML válido** (un «: » dentro de un `run:`); `actionlint` y `zizmor` lo rechazaron y mi revisor no lo había notado. Se corrigió el ejemplo y se agregó una prueba que lo valida con un lector de YAML.
- zizmor se usa con `--offline` (sin llamadas a GitHub).

## Android Lint y otras (no probadas)
Android Lint viene con el SDK de Android (no está en el entorno de la nube) y `apkleaks`/MobSF necesitan jadx o tienen licencias más restrictivas: **no se probaron**. Si algún día se prueban, medirlas sobre el mismo APK y el mismo ejemplo malo.
