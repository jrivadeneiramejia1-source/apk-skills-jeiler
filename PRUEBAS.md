# Qué se probó de verdad

Solo se listan las skills de este repo que se ejecutaron o se midieron. Las demás son copias de terceros: solo se revisó que sean válidas y seguras (`SEGURIDAD.md`).

## 2026-11-04 (en `pantilla-apk`, GitHub Actions)
| Qué | Resultado |
|---|---|
| **pruebas-maestro**: APK construido y probado en un emulador de Android 14 con Maestro | Pasó de punta a punta. La primera ejecución falló por la imagen del emulador (`google_apis`) y se corrigió usando `default`. |
| **web-a-apk**: construcción firmada (`release`) con una llave de prueba | APK (v2 y v3) y AAB firmados y verificados. Con tus Secrets reales no se ha probado. |
| Segunda app (`asesor-prompts`) envuelta como APK | 9 pasos de Maestro completados. |
| Activación sola (Haiku, pocas repeticiones) | `verificar-apk` 3 de 3 frases, `web-a-apk` 2 de 3. |

## 2026-11-06: revisor automático `revisar_android.py`
| Qué | Cómo | Resultado |
|---|---|---|
| Proyecto bueno y proyecto malo hechos a propósito | `verificar-apk/ejemplos/` | Bueno: 0 hallazgos. Malo: 25 hallazgos (11 graves), salida 1. |
| 12 cambios puntuales sobre el proyecto bueno | `debuggable`, `exported` ausente, `targetSdk` 34 (desde `variables.gradle` y desde `libs.versions.toml`), release con llave de depuración, contraseña escrita, `.jks` sin ignorar (y luego ignorado), clave escrita (y marcador que debe ignorarse), `server.url`, `capacitor.config.ts`, flujo con acción en `@main`, variable de entorno segura | Cada cambio dispara su regla (y las formas seguras no). |
| Entradas rotas | carpeta inexistente, vacía, XML roto, sin argumentos | Salida 2 o aviso A00, con mensaje claro. |
| El informe no muestra valores | contraseña y dirección del ejemplo malo | No aparecen en la salida. |
| Plantilla real `pantilla-apk` (3 flujos, 2 apps) | corrida completa | 0 graves, 7 avisos bajos (allowBackup, R8, sin caché de Gradle). |
| Proyectos abiertos de Google `android/architecture-samples` y `android/sunflower` | corrida completa | Sin falsos graves en manifiestos ni flujos. Marca `targetSdk` 35 y 34 (correcto: son ejemplos de aprendizaje). |
| Pruebas del repo (`tests/`) | `python -I -m unittest discover -s tests`: grupos, encabezados YAML, `python` y no `python3`, sin correos reales, revisor | 24 pruebas, todas pasan. |
| Las pruebas detectan fallas | Se rompió a propósito la regla de `targetSdk` y la de `echo` de secretos | Fallaron 3 y 1 pruebas (bien); se restauró. |

### Errores que encontró probar
- Las reglas de `release` leían el bloque equivocado (el de `signingConfigs`) y no veían `debuggable` ni la llave de depuración. Lo descubrió el proyecto malo; arreglado con un lector de llaves `{ }`.
- Proyectos con `targetSdk = libs.versions.targetSdk.get().toInt()` (catálogo de versiones) salían como «no pude deducir»; ahora se lee `libs.versions.toml`.

## 2026-11-06, segunda ronda: APK construido y herramientas de terceros
| Qué | Cómo | Resultado |
|---|---|---|
| APK real de la plantilla (`app-debug.apk`, 4,1 MB) | Artefacto de Actions de `pantilla-apk`; huella verificada; decodificado con Apktool 3.0.3 y también con **REA** (`decode-android-resources`) | Manifiesto final leído; `targetSdk` 36; la web interna idéntica a `www/`. `revisar_android.py` sobre lo decodificado: A01 (esperado en un debug) y A03. |
| `revisar_android.py` ahora lee carpetas decodificadas | Ignora el manifiesto binario de `original/` y `smali*`; lee `targetSdkVersion` de `apktool.yml` | 3 pruebas nuevas (ejemplo `apk-decodificado/`). Primer intento: marcaba el manifiesto binario como «XML roto» (A00); corregido. |
| **actionlint 1.7.12 y zizmor 1.32.0** | Sobre el flujo malo, la plantilla nueva y los flujos de `pantilla-apk` | Plantilla `revisar-flujos.yml`: 0 hallazgos con ambos (zizmor pedante). Encontraron que mi ejemplo malo **no era YAML válido**: corregido. |
| Prueba nueva de YAML válido | Cada `.yml` de la skill se lee con PyYAML (si está) | Habría atrapado el error anterior. |
| Flujos propios de este repo | `.github/workflows/pruebas.yml` y `revisar-flujos.yml` | actionlint 0 y zizmor 0 (pedante). |
| gitleaks sobre el **historial** (13 commits) | `--log-opts=--all` | 2 hallazgos, ambos ficticios: el ejemplo de `security-audit/references/storage.md` y un texto viejo de `SEGURIDAD.md` que lo citaba (ya reescrito). |
| Pruebas del repo | `python -I -m unittest discover -s tests` | 30 pruebas pasan. |

## No probado
- **No se miden los minutos ni el efecto de la caché de Gradle** recomendada en `web-a-apk`: no se corrió Actions para eso.
- El camino **TWA** y la **publicación en Play Store**.
- Teléfono real; otro emulador distinto de Android 14.
- El revisor no abre el APK ya construido, solo el proyecto; no sabe si un permiso se usa de verdad.
- `targetSdk` que viene de plugins o de código Gradle complejo.
- Las plantillas de flujos (`revisar-flujos.yml`, `pruebas.yml`) se validaron con actionlint y zizmor en local; su primera corrida en Actions es la de este mismo PR (repo público, sin costo de minutos).
- jadx / `inspect-android-class` de REA (necesitan un JAR aparte), Android Lint, apkleaks y MobSF.
