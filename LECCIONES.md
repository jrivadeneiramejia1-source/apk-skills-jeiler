# Lecciones (errores aprendidos)

| Fecha | Qué pasó | Qué se aprendió |
|---|---|---|
| 2026-11-04 | La primera prueba en emulador falló porque la imagen `google_apis` bloqueaba los Play Services. | Usar la imagen `default` para pruebas con Maestro. |
| 2026-11-04 | Una prueba de Maestro «pasaba» comprobando el nombre de la app, que sale en la pantalla de inicio. | Comprobar un texto que solo exista dentro de la app. |
| 2026-11-06 | `revisar_android.py` no veía `debuggable true` en release porque su regla leía el primer `release { }` (el de las firmas). | Un ejemplo malo hecho a propósito destapa estas fallas. Para bloques anidados hay que contar llaves, no usar una expresión regular simple. |
| 2026-11-06 | `targetSdk = libs.versions.targetSdk.get().toInt()` salía como «no pude deducir». | Los proyectos modernos usan un catálogo de versiones: leer `libs.versions.toml`. |
| 2026-11-06 | Google Play exige `targetSdk` 36 desde el 2026-08-31 (ya pasó la prórroga al 1 de noviembre). | El número cambia cada año: el script lo tiene en una constante con fecha y fuente. |
| 2026-11-06 | El repo no tenía `CLAUDE.md`. | Cada repo lleva las reglas de Jeiler en `CLAUDE.md`. |
| 2026-11-06 | Mi ejemplo de flujo malo **no era YAML válido** (un «: » dentro de un `run:`), y mi revisor, que lee texto sin entender YAML, no lo notó. | `actionlint` y `zizmor` sí leen YAML de verdad: lo rechazaron al instante. Un revisor casero no reemplaza a una herramienta que entiende el formato. Ahora hay una prueba con PyYAML. |
| 2026-11-06 | Al decodificar el APK, mi revisor marcó el manifiesto **binario** de `original/` como «XML roto». | Un APK decodificado trae el manifiesto original en binario; solo se lee el decodificado. |
| 2026-11-06 | `zizmor` pide fijar cada acción a su **commit** (no a `@v7`) y poner `persist-credentials: false`; mi revisor aceptaba etiquetas. | Dos herramientas con criterios distintos se complementan: GitHub también recomienda el commit exacto. |
