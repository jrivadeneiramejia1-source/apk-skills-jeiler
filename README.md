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

Las 2 skills originales de este repo son **`web-a-apk`** y **`verificar-apk`**. Las otras 13 son copias de repos con licencia libre; sus licencias están en `third-party/`.

## Cómo usarlas
Una skill solo funciona si está en la carpeta de skills de Claude (`~/.claude/skills/`). Copia solo las que necesites:

```bash
cp -r skills/web-a-apk ~/.claude/skills/
```

Mejor cargar por grupos y no todas a la vez: cada skill agrega su descripción al contexto y eso gasta tokens.

## Qué falta o no está probado
- **Ninguna skill se ha probado en una tarea real.** Solo se verificó que los archivos son válidos y que no traen comandos de riesgo.
- `web-a-apk` no tiene un APK construido de punta a punta: los pasos de Capacitor y el esqueleto de GitHub Actions están sin probar.
- Las skills de Compose, React Native y Play Store son de terceros; revísalas antes de depender de ellas.
