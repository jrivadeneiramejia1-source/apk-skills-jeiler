# Revisión de seguridad

Hecha el 2026-11-04.

## Qué se revisó y cómo
1. **gitleaks 8.30.0** (busca claves y tokens escritos en archivos). Se descargó del sitio oficial y se verificó su checksum. Se corrió sobre los archivos y sobre el historial de git.
2. **Búsqueda propia de comandos de riesgo** en los scripts y textos de las skills copiadas: descargar y ejecutar a la vez (`curl ... | sh`), `eval`, `rm -rf /`, `base64 -d`, `nc -e`, `sudo`.
3. **Lectura de los scripts de Python y Node** de las skills oficiales: no usan `subprocess`, `eval` ni `exec`.
4. **No se ejecutó `snyk/agent-scan`.** Pide crear una cuenta en Snyk y un token, y envía el contenido de las skills a su servicio.

## Resultado
- **gitleaks:** 1 hallazgo, en `skills/security-audit/references/storage.md`, línea 10. Es un ejemplo de código que muestra cómo NO guardar un token de sesión, con un valor recortado y ficticio. No es una clave real.
- **Comandos de riesgo en las skills copiadas:** ninguno.
- **Scripts que hacen peticiones de red** (todos de proyectos oficiales):
  - `play-policy-insights/scripts/play_store_scraper.py`: descarga la ficha pública de una app de Google Play (una petición, 10 segundos de límite).
  - `eas-workflows/scripts/fetch.js` (Expo): descarga documentación y la guarda en caché.
- **Scripts que leen archivos locales:** `r8-analyzer` (necesita Python y `protobuf`) y `expo-ui/scripts/list-components.js`.
- **Quitado a propósito:** `android-cli` (su instalación ejecuta `curl ... | bash`).

## Fase 2 (2026-11-06)
- Se agregó `verificar-apk/scripts/revisar_android.py` (original, solo Python estándar): lee archivos, no construye, no abre redes, no ejecuta nada del proyecto revisado y no imprime valores de claves. Sin código de terceros nuevo.
- **gitleaks 8.30.0** (descargado del sitio oficial, checksum `OK`) sobre los archivos: el mismo único hallazgo de antes (`security-audit/references/storage.md`, ejemplo ficticio). Los ejemplos malos usan contraseñas y llaves inventadas a propósito, y no disparan nada.
- Los ejemplos malos traen un archivo `release.jks` que es solo texto de relleno, no una llave.
- Se agregó `CLAUDE.md` con las reglas de Jeiler.

## Fase 3 (2026-11-06, segunda ronda)
- Herramientas de terceros usadas **sin copiarlas**: Apktool 3.0.3 (Apache-2.0; archivo `.jar` de la página oficial, su SHA-256 calculado y anotado en `skills/verificar-apk/references/herramientas.md`, porque el proyecto no publica uno), actionlint 1.7.12 (MIT, huella verificada contra la lista oficial), zizmor 1.32.0 (MIT, `--offline`) y REA 6.5.0 (MIT, construido en una copia temporal). Se corrieron en un entorno aparte, sin claves y sobre archivos propios (el APK es de la plantilla del usuario).
- **gitleaks sobre el historial completo** (13 commits): 2 hallazgos, ambos ficticios.
- Nuevos flujos `pruebas.yml` y `revisar-flujos.yml`: permisos de solo lectura, sin secretos, `actions/checkout` fijado a commit y `persist-credentials: false`.
