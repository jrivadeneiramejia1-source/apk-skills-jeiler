# Reglas del revisor de proyectos Android

Marcas: **[F]** fuente abierta citada · **[P]** regla práctica sin verificar en una fuente · **[E]** hecha y medida aquí.
Fuentes consultadas el 2026-11-06 (ver `fuentes.md`). No se copió texto: solo frases cortas citadas.

| Id | Gravedad | Regla | Marca | Base |
|---|---|---|---|---|
| A01 | ALTA | `android:debuggable="true"` nunca en lo que se publica. | [F] | Android Developers, «android:debuggable»: «Always make sure to set the android:debuggable flag to false when shipping your application.» |
| A02 | MEDIA | `usesCleartextTraffic="true"` permite http sin cifrar. | [F] | Android Developers, «Cleartext communications»: cualquiera que vigile la red puede ver y manipular el tráfico. Desde API 28 los clientes comunes bloquean http por defecto. |
| A03 | BAJA | `allowBackup` distinto de false deja que los datos salgan en copias de seguridad. | [P] | La página oficial de riesgos de backup no se pudo leer (404 el 2026-11-06). Regla práctica. |
| A04 | ALTA | Si un componente tiene `intent-filter`, debe declarar `android:exported`. | [F] | Android Developers, «Target API level requirements»: «you must explicitly declare the android:exported attribute» (Android 12, API 31). |
| A05 | ALTA/MEDIA | Un provider exportado deja leer datos a otras apps; un service o receiver exportado sin permiso lo puede llamar cualquiera. | [P] | Regla general de seguridad de componentes. |
| A06 | MEDIA | Permisos que Google Play restringe (SMS, registro de llamadas, `MANAGE_EXTERNAL_STORAGE`, `QUERY_ALL_PACKAGES`, `REQUEST_INSTALL_PACKAGES`, ubicación en segundo plano, `READ_MEDIA_IMAGES/VIDEO`…) piden formulario de declaración. | [F] | Ayuda de Play Console, «Use of high risk or sensitive permissions» (answer/9888170). |
| A07 | BAJA | Permisos sensibles (cámara, micrófono, contactos, ubicación…): pedir solo los que se usan. | [P] | Regla general. |
| A09 | ALTA | `android:testOnly="true"`: Play rechaza estos paquetes. | [P] | Regla práctica; no verificada en la documentación. |
| G01 | ALTA | `targetSdk` menor que 36. | [F] | Android Developers, «Target API level requirements»: desde el 2026-08-31, apps nuevas y actualizaciones deben apuntar a Android 16 (API 36) o más. **Cambiar `TARGET_SDK_PLAY` en el script cada año.** |
| G04 | ALTA | Contraseñas de la llave de firma escritas en `build.gradle`. | [P] | Misma razón que K02; Capacitor dice lo mismo de `keystorePassword` en su configuración (ver C04). |
| G05 | BAJA | `minifyEnabled false` en release. | [P] | Normal en apps Capacitor; en apps nativas conviene R8. |
| G06 G07 | ALTA | `debuggable true` en release; release firmado con la llave de depuración. | [F]/[P] | G06 como A01; G07 es regla práctica (Play no acepta la llave de depuración). |
| K01 | ALTA | Archivos `.jks`, `.keystore`, `.p12` o `keystore.properties` en el proyecto sin estar en `.gitignore`. | [P] | Perder el secreto de la firma = otra persona puede publicar «actualizaciones» de tu app. |
| K02 | ALTA | Claves escritas en cualquier archivo de texto. | [P] | Los marcadores (`<YOUR_KEY>`, `xxx`, `example`) se ignoran. |
| C01 | ALTA | `server.url` en Capacitor. | [F] | capacitorjs.com/docs/config: es para recarga en vivo, «This is not intended for use in production.» |
| C02 C03 | MEDIA | `server.cleartext`/`allowMixedContent` y `webContentsDebuggingEnabled`. | [F] | Misma página: valores por defecto `false`, reservados para desarrollo. |
| C04 | ALTA | Contraseñas de `android.buildOptions` escritas en la configuración. | [P] | Capacitor las acepta en texto; mejor variables de entorno. |
| C05 | MEDIA | `appId` de ejemplo (`io.ionic.starter`, `com.example…`). | [P] | El `applicationId` no se puede cambiar una vez publicada la app (regla de Play, no verificada en la ayuda). |
| W01 | MEDIA | Acciones de GitHub sin versión o apuntando a una rama. | [F] | docs.github.com, «Secure use»: lo más seguro es fijar a un commit SHA completo; una versión `@vX` es lo mínimo. El revisor no exige SHA. |
| W02 | BAJA | Sin `permissions:` al inicio. | [F] | Misma página: dar al `GITHUB_TOKEN` los permisos mínimos. |
| W03 | BAJA | Sin `timeout-minutes`. | [P] | Evita gastar minutos hasta el tope de 6 horas. |
| W04 | ALTA | `echo ${{ secrets.X }}`. | [P] | GitHub enmascara secretos en el registro, pero no todas las transformaciones; no hay motivo para imprimirlos. |
| W05 | ALTA | `pull_request_target` junto con el código del PR. | [F] | Misma página: estos flujos «must not explicitly check out untrusted code». |
| W07 | BAJA | `./gradlew` sin caché. | [F] | Documentación de `gradle/actions/setup-gradle`; el proveedor `basic` es MIT, el `enhanced` es una biblioteca comercial. En ramas distintas de `main` no guarda caché. |
| W08 | ALTA | Título, mensaje o rama de un PR dentro de un `run:`. | [F] | Misma página: pasarlo por «an intermediate environment variable». El revisor da por buena la forma `VARIABLE: ${{ ... }}`. |

## Medido aquí **[E]**
- Plantilla real `pantilla-apk` (3 flujos, 2 apps): 0 graves; 7 avisos bajos (allowBackup, R8, sin caché de Gradle).
- Proyectos abiertos de Google `android/architecture-samples` y `android/sunflower`: sin falsos graves en manifiestos y flujos. Al leer `targetSdk` desde `libs.versions.toml`, el revisor los marca con `targetSdk` 35 y 34 (son ejemplos de aprendizaje, no apps publicadas).

## Límites
- Lee texto: no abre el APK ya construido (ahí siguen valiendo los pasos de `SKILL.md`).
- No resuelve el `targetSdk` si viene de un plugin o de código Gradle complicado: avisa con BAJA «no pude deducir».
- No sabe si un permiso se usa de verdad.
