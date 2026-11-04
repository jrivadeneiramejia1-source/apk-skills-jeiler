# Revisión de seguridad

Hecha el 2026-11-04.

## Qué se revisó y cómo
1. **gitleaks 8.30.0** (busca claves y tokens escritos en archivos). Se descargó del sitio oficial y se verificó su checksum (`OK`). Se corrió sobre los archivos actuales y sobre todo el historial de git.
2. **Búsqueda propia de comandos de riesgo** en los scripts de las skills copiadas: descargar y ejecutar a la vez (`curl ... | sh`), `eval`, `rm -rf /`, `base64 -d`, `nc -e`, `sudo`.
3. **No se ejecutó `snyk/agent-scan`.** Pide crear una cuenta en Snyk y un token, y envía el contenido de las skills a su servicio. No lo usé por eso. Queda pendiente si decides crear la cuenta tú.

## Resultado
- **gitleaks:** 1 hallazgo, en `skills/security-audit/references/storage.md`. Es un ejemplo de código que muestra cómo NO guardar un token (`putString("auth_token", "eyJhbGciOiJIUzI1NiIs...")`), con un valor recortado y ficticio. No es una clave real.
- **Comandos de riesgo:** ninguno en las 15 skills.
