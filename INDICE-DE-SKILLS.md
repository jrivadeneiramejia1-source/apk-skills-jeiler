# Índice de skills (cuándo usar cada una)

## A. Del web al APK
| Skill | Cuándo usarla | Origen |
|---|---|---|
| **web-a-apk** | Convertir una web o PWA en app de Android: elegir camino, construir con GitHub Actions, firmar. | Original |
| github-actions | Flujos de GitHub Actions para compilar apps móviles (React Native) en la nube. | Callstack (MIT) |

## B. Probar y verificar
| Skill | Cuándo usarla | Origen |
|---|---|---|
| **verificar-apk** | Hay un APK o AAB listo: instalarlo, intentar romperlo y dar un informe. | Original |
| testing-setup | Armar la estrategia de pruebas de una app de Android: librerías, pruebas unitarias y de interfaz. | Google (Apache-2.0) |
| android-testing | Estándares de pruebas para una app de Android nativa. | lennonpetrick (MIT) |
| security-audit | Auditoría de seguridad de Android basada en OWASP MASVS. | liuyi0808 (MIT) |
| android-permissions-security | Revisar permisos y componentes expuestos en `AndroidManifest.xml`. | Google (Apache-2.0) |
| android-intent-security | Seguridad de los Intents (actividades, servicios y receptores). | Google (Apache-2.0) |
| play-policy-insights | Revisar la app contra las políticas de Google Play y sus declaraciones. Trae scripts; uno descarga la ficha pública de la tienda. | Google (Apache-2.0) |

## C. Apps nativas con Jetpack Compose (Kotlin)
| Skill | Cuándo usarla | Origen |
|---|---|---|
| compose | Primera skill para cualquier tarea de Compose: pantalla nueva, cambio, arreglo o revisión. | Meet-Miyani (MIT) |
| compose-ui | Escribir y revisar pantallas y listas. | Meet-Miyani (MIT) |
| compose-architecture | Organización del proyecto (módulos, MVI, ViewModel). | Meet-Miyani (MIT) |
| compose-data | Repositorios, fuentes de datos y conexión con servidores. | Meet-Miyani (MIT) |
| android-patterns | Patrones de implementación de una función Android (ViewModel, flujo de datos). | lennonpetrick (MIT) |
| kotlin-quality | Revisión de calidad del código Kotlin. | liuyi0808 (MIT) |
| adaptive | Que la interfaz se adapte a móviles, tabletas, plegables y pantallas grandes. | Google (Apache-2.0) |
| jetpack-compose-performance | Encontrar y arreglar lentitud en pantallas de Compose. | Google (Apache-2.0) |
| navigation-3 | Navegación con Jetpack Navigation 3 (instalar y migrar). | Google (Apache-2.0) |
| edge-to-edge | Pantalla completa bajo las barras del sistema. | Google (Apache-2.0) |
| material-design-3-ui | Diseñar y revisar la interfaz con Material Design 3. | skydashnet (MIT) |

## D. Android, extras
| Skill | Cuándo usarla | Origen |
|---|---|---|
| camerax | Cámara con CameraX (por ejemplo, un lector de códigos). | Google (Apache-2.0) |
| anr-audit-and-fix | Encontrar y arreglar bloqueos de la app («la aplicación no responde»). | Google (Apache-2.0) |
| r8-analyzer | Revisar las reglas de R8 que reducen y ofuscan el código. Necesita Python y `protobuf`. | Google (Apache-2.0) |

## E. React Native
| Skill | Cuándo usarla | Origen |
|---|---|---|
| vercel-react-native-skills | Buenas prácticas de React Native y Expo. | Vercel (MIT) |
| react-native-best-practices | Rendimiento: fluidez, tamaño, memoria. | Callstack (MIT) |
| react-navigation | Navegación entre pantallas (pilas, pestañas, menús). | Callstack (MIT) |

## F. Expo (oficiales)
Origen: expo/skills (MIT). Empezar por `expo-overview`: enruta a las demás.

| Skill | Cuándo usarla |
|---|---|
| expo-overview | Punto de entrada para cualquier tarea de Expo o EAS. |
| expo-web-to-native | Convertir una web React en una app nativa con Expo. |
| expo-router | Rutas y navegación. |
| expo-ui | Interfaz nativa (SwiftUI y Jetpack Compose) desde Expo. |
| expo-animation | Animaciones en React Native. |
| expo-data-fetching | Peticiones de red, caché y errores. |
| eas-workflows | Flujos de CI/CD de EAS. |
| eas-app-stores | Compilar y enviar a Google Play o App Store con EAS. |
| eas-update | Actualizaciones por el aire (OTA). |
| expo-upgrade | Subir de versión del SDK de Expo. |

## Plugins recomendados (se instalan desde el directorio de plugins, no desde este repo)
`kotlin-lsp` (oficial de Anthropic, revisa Kotlin) y `Pwa2play` (de la comunidad, empaqueta una PWA para Play Store).

## Revisadas y NO incluidas
- `android-cli` (Google): su instalación ejecuta un script descargado (`curl ... | bash`). Instalarlo a mano desde la página oficial si se necesita.
- `play-store` (liuyi0808): hecha para apps financieras. Se reemplazó por la oficial `play-policy-insights`.
- `privacy-audit` (liuyi0808): hecha para apps de préstamos.
- `kotlin-footguns` (maxrave-dev): licencia GPL-3.0; no se copió para no mezclar licencias.
- Flutter: [zakariaf/Flutter-Skills](https://github.com/zakariaf/Flutter-Skills) (MIT). No se copió porque no sé si se usará Flutter.
- Las skills de interfaz web, pruebas web y fluidez están en `app-skills-jeiler`.
