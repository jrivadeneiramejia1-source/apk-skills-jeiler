# Fuentes de las skills copiadas

Cada fila dice de dónde viene una skill, qué versión se copió y con qué licencia. Sirve para saber si hay una versión nueva en el origen (se compara el commit).
Verificado el 2026-11-04.

| Skills | Origen | Commit copiado | Fecha | Licencia |
|---|---|---|---|---|
| `testing-setup`, `android-permissions-security`, `android-intent-security`, `edge-to-edge`, `adaptive`, `jetpack-compose-performance`, `anr-audit-and-fix`, `r8-analyzer`, `play-policy-insights`, `camerax`, `navigation-3` | android/skills | bf68e2d | 2026-11-04 | Apache-2.0 |
| `expo-overview`, `expo-web-to-native`, `expo-router`, `expo-ui`, `expo-animation`, `expo-data-fetching`, `eas-workflows`, `eas-app-stores`, `eas-update`, `expo-upgrade` | expo/skills | a9e5bd3 | 2026-11-01 | MIT |
| `material-design-3-ui` | skydashnet/material-design-3-ui-skill (sin scripts de instalación ni pruebas) | 82783f7 | 2026-10-01 | MIT |
| `react-native-best-practices`, `react-navigation`, `github-actions` | callstackincubator/agent-skills | 59e9d17 | 2026-10-08 | MIT |
| `compose`, `compose-ui`, `compose-architecture`, `compose-data` | Meet-Miyani/compose-skill | dbaa268 | 2026-10-23 | MIT |
| `security-audit`, `kotlin-quality` | liuyi0808/android-review | 26fbdc8 | 2026-08-27 | MIT |
| `android-testing`, `android-patterns` | lennonpetrick/android-engineering-skills | b1468d1 | 2026-11-03 | MIT |
| `vercel-react-native-skills` | vercel-labs/agent-skills (tu fork `agent-skills-jeiler`) | 063bee9 | 2026-08-28 | MIT (declarada en su SKILL.md) |
| `web-a-apk`, `verificar-apk`, `pruebas-maestro` | Originales de este repo | — | — | MIT (ver LICENSE) |

## Revisar si hay versiones nuevas (cada mes)
```bash
python3 -I comparar-fuentes.py
```
Es de solo lectura: compara cada commit de esta tabla con el más nuevo del repo de origen y dice «igual» o «HAY CAMBIOS» (o no pudo consultar). Salida 0 = todo igual, 1 = hay cambios, 2 = no se pudo consultar alguno. Que haya cambios no obliga a actualizar: primero mirar qué cambió, volver a revisar su seguridad (`SEGURIDAD.md`) y actualizar la fila de esta tabla. Probado el 2026-11-04.

