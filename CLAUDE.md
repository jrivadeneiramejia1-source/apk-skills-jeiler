# Reglas para trabajar en este repo (es público)
- **Nada de datos de personas ni de clientes.** Los ejemplos son inventados.
- **Nunca pedir ni guardar claves, tokens, contraseñas ni archivos de firma (keystore).** El usuario los crea y los guarda en los Secrets de GitHub.
- Archivos de comunidades indígenas: no se modifican ni se suben a servicios externos.
- Nada que gaste plata o créditos sin el «sí» de Jeiler y una estimación del costo. Un flujo de GitHub Actions gasta minutos: avisar antes de correr uno.
- Nada se publica solo; **nunca a `main` directo** (rama y PR; Jeiler dice «sí» antes de unir).
- Antes de copiar algo de terceros: licencia abierta (MIT, Apache-2.0, BSD, CC0…), revisión de seguridad (`SEGURIDAD.md`) y su licencia en `third-party/`. No copiar apps cerradas.
- Cada regla de una guía lleva una marca: **[F]** fuente abierta citada, **[P]** regla práctica sin verificar, **[E]** hecha y medida aquí.
- Un revisor automático se prueba siempre con un ejemplo bueno y uno malo hecho a propósito. Pruebas: `python -I -m unittest discover -s tests`.
- Responder a Jeiler en español simple y decir siempre qué quedó sin probar.

## Estructura
- `skills/<nombre>/SKILL.md`: una skill. Las originales son `web-a-apk`, `verificar-apk` y `pruebas-maestro`; el resto son de terceros y no se editan.
- `grupos.conf`: qué skills instala cada grupo. `instalar.sh`: copia las skills.
- `INDICE-DE-SKILLS.md`: cuándo usar cada una. `PRUEBAS.md`: qué se probó. `LECCIONES.md`: errores aprendidos.
