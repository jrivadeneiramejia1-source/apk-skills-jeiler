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
