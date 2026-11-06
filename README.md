# apk-skills-jeiler

Skills para hacer **apps de Android (APK)**: convertir una web en app, construirla sin computador propio, probarla y publicarla.
Es el tercer repo de la familia: `agent-skills-jeiler` (agentes), `app-skills-jeiler` (apps web) y este (apps de Android).

Cada carpeta de `skills/` es una skill: un archivo `SKILL.md` con instrucciones para que Claude sepa cuándo y cómo usarla.

## Qué hay (37 skills)
| Grupo | Para qué |
|---|---|
| **A. Del web al APK** | Convertir una web o PWA en app de Android y construirla en GitHub Actions. |
| **B. Probar y verificar** | Probar un APK, revisar seguridad, permisos y políticas de Google Play. |
| **C. Jetpack Compose** | Apps nativas en Kotlin. |
| **D. Android, extras** | Cámara, bloqueos de la app y reglas de R8. |
| **E. React Native** | Apps con React Native. |
| **F. Expo** | Skills oficiales de Expo y EAS. |

La lista completa, con cuándo usar cada una y de dónde viene, está en **`INDICE-DE-SKILLS.md`**.

Las 3 skills originales de este repo son **`web-a-apk`**, **`verificar-apk`** y **`pruebas-maestro`** (licencia MIT, ver `LICENSE`). Las otras 34 son copias de repos con licencia libre (11 son oficiales de Google y 10 oficiales de Expo); sus licencias están en `third-party/`.

## Cómo usarlas
Una skill solo funciona si está en la carpeta de skills de Claude (`~/.claude/skills/`). El instalador copia por grupos:

```bash
./instalar.sh --lista        # ver los grupos
./instalar.sh web-a-apk probar-apk   # instalar esos grupos
```

**En sesiones en la nube** se instalan solos los grupos escritos en `grupos-activos.txt` (hoy: `web-a-apk` y `probar-apk`). Lo hace un hook de inicio en `.claude/`, y solo funciona si este repo está cargado como repo de la sesión. Edita ese archivo para cambiar los grupos.

El instalador no pisa una skill que ya exista con el mismo nombre y que no haya instalado él.

Mejor pocos grupos a la vez: cada skill agrega su descripción al contexto y eso gasta tokens.

## Revisor automático antes de construir
```
python -I skills\verificar-apk\scripts\revisar_android.py CARPETA-DEL-PROYECTO
```
Solo Python (corre igual en Windows y en la nube). Lee el proyecto y avisa errores **antes** de gastar minutos de GitHub Actions: `targetSdk` menor que el que Google Play exige, `debuggable`, `exported` que falta, permisos restringidos, contraseñas o llaves de firma expuestas, `server.url` de Capacitor y fallos comunes de los flujos. Salida 0 = sin graves, 1 = hay graves. Probado con un proyecto bueno, uno malo hecho a propósito y 3 proyectos reales (ver `PRUEBAS.md`). Que salga limpio **no** prueba que la app sea segura ni que Google Play la acepte.

### También sirve sobre un APK ya construido
`apktool d MI-APP.apk -o SALIDA` y luego `python -I skills\verificar-apk\scripts\revisar_android.py SALIDA` revisa el manifiesto **final** (con lo que agregan las librerías). Alternativa pasiva con REA. Y `skills/verificar-apk/plantilla/revisar-flujos.yml` revisa tus flujos de GitHub Actions con `actionlint` y `zizmor` (herramientas abiertas). Versiones, licencias y mediciones: `skills/verificar-apk/references/herramientas.md`.

## Probar este repo
```
python -I -m unittest discover -s tests
```

## Qué falta o no está probado
- Solo se verificó que los archivos son válidos y que no traen comandos de riesgo, salvo lo de abajo. Se abrieron solas al pedirlo: `verificar-apk` en 3 de 3 frases y `web-a-apk` en 2 de 3 (con Haiku; pocas repeticiones, solo una señal).
- **Probado de verdad (2026-11-04), en el repo de prueba `pantilla-apk`:** el APK se construyó en GitHub Actions y se probó en un emulador de Android 14 con Maestro: abrió la app, tocó el botón y comprobó el contador (pasó de punta a punta). La primera ejecución falló por un problema del emulador y se corrigió; ver `pruebas-maestro`.
- **Construcción firmada (`release`), probada el 2026-11-04 en GitHub Actions** con una llave de prueba: APK (v2 y v3) y AAB firmados y verificados; ver `web-a-apk`. Con tus Secrets reales no se ha probado.
- **No se probó:** el camino TWA ni la publicación en Play Store.
- Las skills de Compose, React Native y Play Store son de terceros; revísalas antes de depender de ellas.
- Revisión de seguridad hecha con gitleaks: ver `SEGURIDAD.md`. Origen y versión de cada skill: ver `FUENTES.md`.
