# apk-skills-jeiler

Skills para hacer **apps de Android (APK)**: convertir una web en app, construirla sin computador propio, probarla y publicarla.
Es el tercer repo de la familia: `agent-skills-jeiler` (agentes), `app-skills-jeiler` (apps web) y este (apps de Android).

Cada carpeta de `skills/` es una skill: un archivo `SKILL.md` con instrucciones para que Claude sepa cuándo y cómo usarla.

## Qué hay (15 skills)
| Grupo | Para qué |
|---|---|
| **A. Del web al APK** | Convertir una web o PWA en app de Android y construirla en GitHub Actions. |
| **B. Probar y verificar** | Probar un APK, revisar seguridad y requisitos de Google Play. |
| **C. Jetpack Compose** | Apps nativas en Kotlin. |
| **D. React Native y Expo** | Apps con React Native. |

La lista completa, con cuándo usar cada una y de dónde viene, está en **`INDICE-DE-SKILLS.md`**.

Las 2 skills originales de este repo son **`web-a-apk`** y **`verificar-apk`** (licencia MIT, ver `LICENSE`). Las otras 13 son copias de repos con licencia libre; sus licencias están en `third-party/`.

## Cómo usarlas
Una skill solo funciona si está en la carpeta de skills de Claude (`~/.claude/skills/`). El instalador copia por grupos:

```bash
./instalar.sh --lista        # ver los grupos
./instalar.sh web-a-apk probar-apk   # instalar esos grupos
```

**En sesiones en la nube** se instalan solos los grupos escritos en `grupos-activos.txt` (hoy: `web-a-apk` y `probar-apk`). Lo hace un hook de inicio en `.claude/`, y solo funciona si este repo está cargado como repo de la sesión. Edita ese archivo para cambiar los grupos.

El instalador no pisa una skill que ya exista con el mismo nombre y que no haya instalado él.

Mejor pocos grupos a la vez: cada skill agrega su descripción al contexto y eso gasta tokens.

## Qué falta o no está probado
- **Ninguna skill se ha probado en una tarea real.** Solo se verificó que los archivos son válidos y que no traen comandos de riesgo.
- `web-a-apk` no tiene un APK construido de punta a punta: los pasos de Capacitor y el esqueleto de GitHub Actions están sin probar.
- Las skills de Compose, React Native y Play Store son de terceros; revísalas antes de depender de ellas.
- Revisión de seguridad hecha con gitleaks: ver `SEGURIDAD.md`. Origen y versión de cada skill: ver `FUENTES.md`.
