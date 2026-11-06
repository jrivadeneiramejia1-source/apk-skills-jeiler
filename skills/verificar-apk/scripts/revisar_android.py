#!/usr/bin/env python3
"""Revisa un proyecto de Android (Capacitor, Compose, React Native...) ANTES de construirlo.

Uso:   python -I revisar_android.py CARPETA_DEL_PROYECTO [--json]
Salida: 0 = sin hallazgos graves, 1 = hay hallazgos ALTA, 2 = no se pudo leer.

Solo lee archivos de texto: no construye, no abre redes, no ejecuta nada del proyecto y NUNCA
imprime el valor de una clave. Busca patrones; que salga limpio NO prueba que la app sea segura
ni que Google Play la acepte.
"""
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# Nivel de API (targetSdk) que Google Play exige a apps nuevas y actualizaciones desde el 2026-08-31.
# Fuente: developer.android.com/google/play/requirements/target-sdk (consultada el 2026-11-06).
# Si pasa un año, volver a mirar esa página y cambiar este número.
TARGET_SDK_PLAY = 36

ANDROID = "{http://schemas.android.com/apk/res/android}"
SALTAR = {"node_modules", ".git", "build", ".gradle", ".idea", "__pycache__", ".cxx", "Pods", "original", "unknown", "kotlin"}
TEXTO = {".xml", ".gradle", ".kts", ".json", ".properties", ".kt", ".java", ".js", ".ts", ".html", ".yml", ".yaml", ".toml", ".env"}
MAX_ARCHIVO, MAX_ARCHIVOS = 1_000_000, 6000

CLAVES = [
    ("token de bot de Telegram", re.compile(r"(?<!\d)\d{8,10}:[A-Za-z0-9_-]{35}(?![A-Za-z0-9_-])")),
    ("clave tipo sk-...", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}")),
    ("clave de Google (AIza...)", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("token de GitHub", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}")),
    ("clave de AWS", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("llave privada", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
]
MARCADOR = re.compile(r"(?i)(your[_ -]|insert|replace|change[_-]?me|xxx|<[^<>]{2,}>|example|placeholder)")

# Permisos que Google Play restringe o mira con lupa (piden formulario de declaración).
PERMISOS_RESTRINGIDOS = {"READ_SMS", "SEND_SMS", "RECEIVE_SMS", "RECEIVE_MMS", "READ_CALL_LOG", "WRITE_CALL_LOG", "PROCESS_OUTGOING_CALLS",
                         "MANAGE_EXTERNAL_STORAGE", "QUERY_ALL_PACKAGES", "REQUEST_INSTALL_PACKAGES", "SYSTEM_ALERT_WINDOW",
                         "BIND_ACCESSIBILITY_SERVICE", "ACCESS_BACKGROUND_LOCATION", "READ_MEDIA_IMAGES", "READ_MEDIA_VIDEO",
                         "USE_EXACT_ALARM", "USE_FULL_SCREEN_INTENT"}
PERMISOS_SENSIBLES = {"CAMERA", "RECORD_AUDIO", "READ_CONTACTS", "WRITE_CONTACTS", "ACCESS_FINE_LOCATION", "ACCESS_COARSE_LOCATION",
                      "READ_PHONE_STATE", "CALL_PHONE", "READ_EXTERNAL_STORAGE", "WRITE_EXTERNAL_STORAGE", "READ_CALENDAR", "WRITE_CALENDAR",
                      "BODY_SENSORS", "READ_MEDIA_AUDIO"}
COMPONENTES = ("activity", "activity-alias", "service", "receiver", "provider")
IDS_POR_DEFECTO = ("io.ionic.starter", "com.example", "com.ionicframework")


def listar(raiz):
    salida = []
    for dp, dirs, files in os.walk(raiz):
        dirs[:] = [d for d in dirs if d not in SALTAR and not d.startswith("smali")]
        for f in files:
            salida.append(Path(dp) / f)
            if len(salida) >= MAX_ARCHIVOS:
                return salida
    return salida


def leer(p):
    try:
        if p.stat().st_size > MAX_ARCHIVO:
            return ""
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def bloque(texto, patron, desde=0):
    """Devuelve el texto entre llaves del primer «patron {» desde la posición dada (con llaves anidadas), o None."""
    m = re.compile(patron + r"\s*\{").search(texto, desde)
    if not m:
        return None
    i, nivel = m.end(), 1
    while i < len(texto) and nivel:
        nivel += {"{": 1, "}": -1}.get(texto[i], 0)
        i += 1
    return texto[m.end():i - 1] if nivel == 0 else None


def norm(nombre):
    return re.sub(r"[-_.]", "", nombre).lower()


def resolver_sdk(texto, variables, catalogo=""):
    """Devuelve el número de targetSdk si se puede deducir, o None."""
    m = re.search(r"(?m)^\s*targetSdk(?:Version)?\s*[= ]\s*(\d+)\s*$", texto)
    if m:
        return int(m.group(1))
    m = re.search(r"targetSdk\s*\{[^}]*?release\((\d+)\)", texto, re.S)
    if m:
        return int(m.group(1))
    m = re.search(r"targetSdk(?:Version)?\s*=\s*libs\.versions\.([\w.]+?)(?:\.get\(\))?(?:\.toInt\(\))?\s*$", texto, re.M)
    if m and catalogo:
        for linea in re.finditer(r'(?m)^\s*([\w.-]+)\s*=\s*"(\d+)"', catalogo):
            if norm(linea.group(1)) == norm(m.group(1)):
                return int(linea.group(2))
    m = re.search(r"targetSdk(?:Version)?\s*[= ]\s*rootProject\.ext\.(\w+)", texto)
    nombre = m.group(1) if m else None
    if nombre:
        v = re.search(r"(?m)^\s*" + re.escape(nombre) + r"\s*=\s*(\d+)", variables or "")
        if v:
            return int(v.group(1))
    return None


def revisar(raiz):
    raiz = Path(raiz)
    if not raiz.is_dir():
        raise ValueError(f"no encuentro la carpeta: {raiz}")
    archivos = listar(raiz)
    rel = lambda p: str(p.relative_to(raiz))  # noqa: E731
    h = []

    def add(id_, grav, donde, texto):
        h.append({"id": id_, "gravedad": grav, "donde": donde, "texto": texto})

    manifests = [p for p in archivos if p.name == "AndroidManifest.xml"]
    gradles = [p for p in archivos if p.name in ("build.gradle", "build.gradle.kts")]
    caps = [p for p in archivos if p.name.startswith("capacitor.config.") and p.suffix in (".json", ".ts", ".js")]
    flujos = [p for p in archivos if p.suffix in (".yml", ".yaml") and ".github" in p.parts and "workflows" in p.parts]
    if not (manifests or gradles or caps or flujos or any(p.name == "apktool.yml" for p in archivos)):
        raise ValueError("no encontré un proyecto de Android (ni AndroidManifest.xml, ni build.gradle, ni capacitor.config, ni flujos de Actions)")

    # ---- Manifiesto (del proyecto, o el ya construido si la carpeta viene de «apktool d»)
    for mf in manifests:
        if not leer(mf).lstrip().startswith("<"):  # manifiesto binario (AXML): solo se lee el decodificado
            continue
        try:
            raiz_xml = ET.fromstring(leer(mf))
        except ET.ParseError:
            add("A00", "MEDIA", rel(mf), "El AndroidManifest.xml no se pudo leer como XML.")
            continue
        app = raiz_xml.find("application")
        if app is not None:
            if app.get(ANDROID + "debuggable") == "true":
                add("A01", "ALTA", rel(mf), "android:debuggable=\"true\": nunca se publica así; cualquiera podría depurar la app. (Los APK «debug» lo traen por diseño: en el APK que publicas debe ser false.)")
            if app.get(ANDROID + "usesCleartextTraffic") == "true":
                add("A02", "MEDIA", rel(mf), "usesCleartextTraffic=\"true\": permite tráfico http sin cifrar. Usa https.")
            if app.get(ANDROID + "allowBackup") != "false":
                add("A03", "BAJA", rel(mf), "allowBackup no está en false: los datos de la app pueden salir en una copia de seguridad. Pon false si guarda datos sensibles.")
            if app.get(ANDROID + "testOnly") == "true":
                add("A09", "ALTA", rel(mf), "android:testOnly=\"true\": Google Play rechaza estas apps.")
            for tag in COMPONENTES:
                for c in app.iter(tag):
                    nombre = (c.get(ANDROID + "name") or "?").split(".")[-1]
                    exp = c.get(ANDROID + "exported")
                    filtros = c.findall("intent-filter")
                    es_launcher = any(
                        any(a.get(ANDROID + "name") == "android.intent.action.MAIN" for a in f.findall("action")) for f in filtros)
                    if filtros and exp is None:
                        add("A04", "ALTA", rel(mf), f"{tag} «{nombre}» tiene intent-filter pero no declara android:exported (obligatorio al apuntar a Android 12 o más).")
                    elif exp == "true" and not es_launcher:
                        if tag == "provider":
                            add("A05", "ALTA", rel(mf), f"El provider «{nombre}» está exportado: otras apps pueden leer sus datos.")
                        elif c.get(ANDROID + "permission") is None:
                            add("A05", "MEDIA", rel(mf), f"{tag} «{nombre}» está exportado sin permiso: cualquier app puede llamarlo.")
        permisos = {(p.get(ANDROID + "name") or "").rsplit(".", 1)[-1] for p in raiz_xml.iter("uses-permission")}
        for p in sorted(permisos & PERMISOS_RESTRINGIDOS):
            add("A06", "MEDIA", rel(mf), f"Permiso {p}: Google Play pide declararlo en Play Console con un formulario (y solo lo acepta para usos permitidos). Quítalo si no es imprescindible.")
        sens = sorted(permisos & PERMISOS_SENSIBLES)
        if sens:
            add("A07", "BAJA", rel(mf), "Permisos sensibles (" + ", ".join(sens) + "): pide cada uno solo si la app lo usa, y explícalo en la política de privacidad.")

    # ---- APK ya decodificado con apktool: el nivel de API sale de apktool.yml
    for y in (p for p in archivos if p.name == "apktool.yml"):
        m = re.search(r"(?m)^\s*targetSdkVersion:\s*['\"]?(\d+)", leer(y))
        if m and int(m.group(1)) < TARGET_SDK_PLAY:
            add("G01", "ALTA", rel(y), f"targetSdk {m.group(1)}: desde el 2026-08-31 Google Play pide {TARGET_SDK_PLAY} o más para apps nuevas y actualizaciones.")

    # ---- Gradle
    variables = next((leer(p) for p in archivos if p.name == "variables.gradle"), "")
    catalogo = next((leer(p) for p in archivos if p.name == "libs.versions.toml"), "")
    for g in gradles:
        t = leer(g)
        if "com.android.application" in t or "applicationId" in t:
            sdk = resolver_sdk(t, variables, catalogo)
            if sdk is None:
                add("G01", "BAJA", rel(g), "No pude deducir el targetSdk. Compruébalo a mano (Google Play pide %d o más)." % TARGET_SDK_PLAY)
            elif sdk < TARGET_SDK_PLAY:
                add("G01", "ALTA", rel(g), f"targetSdk {sdk}: desde el 2026-08-31 Google Play pide {TARGET_SDK_PLAY} o más para apps nuevas y actualizaciones.")
        for m in re.finditer(r"(?im)^\s*(storePassword|keyPassword|keystorePassword)\s*[= ]\s*[\"']([^\"']+)[\"']", t):
            add("G04", "ALTA", rel(g), f"{m.group(1)} escrito con un valor fijo en el archivo de Gradle. Léelo de variables de entorno o de los Secrets del CI.")
        tipos = bloque(t, r"\bbuildTypes")
        b = bloque(tipos, r"\b(?:release|getByName\([\"']release[\"']\))") if tipos else None
        if b is not None:
            if re.search(r"debuggable\s*[= ]\s*true", b):
                add("G06", "ALTA", rel(g), "El tipo release tiene debuggable true.")
            if re.search(r"signingConfig\s*[= ]\s*signingConfigs\.(getByName\(\W*debug\W*\)|debug)", b):
                add("G07", "ALTA", rel(g), "El release se firma con la llave de depuración: Google Play no lo acepta y cualquiera puede re-firmarlo.")
            if re.search(r"minifyEnabled\s*[= ]\s*false|isMinifyEnabled\s*=\s*false", b):
                add("G05", "BAJA", rel(g), "El release no usa R8 (minifyEnabled false): el APK queda más grande y sin ofuscar. Normal en apps Capacitor; piénsalo en apps nativas.")

    # ---- Llaves de firma en el árbol
    ignorados = leer(raiz / ".gitignore")
    for p in archivos:
        if p.suffix.lower() in (".jks", ".keystore", ".p12", ".pfx") or p.name in ("keystore.properties", "key.properties"):
            if not re.search(r"(?m)^\s*(\*\.(jks|keystore|p12|pfx)|keystore\.properties|key\.properties|" + re.escape(p.name) + r")\s*$", ignorados):
                add("K01", "ALTA", rel(p), "Archivo de llave de firma dentro del proyecto y .gitignore no lo ignora: se subiría a GitHub. Si ya se subió, esa llave ya no es secreta.")

    # ---- Claves escritas
    for p in archivos:
        if p.suffix.lower() in TEXTO or p.name.startswith(".env"):
            t = leer(p)
            vistos = set()
            for etiqueta, rx in CLAVES:
                m = rx.search(t)
                if m and not MARCADOR.search(m.group(0)) and etiqueta not in vistos:
                    vistos.add(etiqueta)
                    add("K02", "ALTA", rel(p), f"Parece haber un {etiqueta} escrito en el archivo. Quítalo, cámbialo en el servicio y guárdalo como secreto.")

    # ---- Capacitor
    for c in caps:
        t = leer(c)
        cfg = None
        if c.suffix == ".json":
            try:
                cfg = json.loads(t)
            except json.JSONDecodeError:
                add("C00", "MEDIA", rel(c), "capacitor.config.json no es un JSON válido.")
        srv = (cfg or {}).get("server") or {} if cfg is not None else {}
        droid = (cfg or {}).get("android") or {} if cfg is not None else {}
        if cfg is not None:
            url, cleartext, mixto, debug, appid = srv.get("url"), srv.get("cleartext"), droid.get("allowMixedContent"), droid.get("webContentsDebuggingEnabled"), cfg.get("appId", "")
        else:
            url = re.search(r"\burl\s*:\s*[\"']", t) and True
            cleartext = re.search(r"\bcleartext\s*:\s*true", t) and True
            mixto = re.search(r"allowMixedContent\s*:\s*true", t) and True
            debug = re.search(r"webContentsDebuggingEnabled\s*:\s*true", t) and True
            m = re.search(r"appId\s*:\s*[\"']([^\"']+)", t)
            appid = m.group(1) if m else ""
        if url:
            add("C01", "ALTA", rel(c), "server.url está puesto: la app carga una web externa en vez de los archivos del APK. Capacitor dice que es solo para desarrollo, no para producción.")
        if cleartext or mixto:
            add("C02", "MEDIA", rel(c), "server.cleartext o allowMixedContent activo: permite http sin cifrar (la documentación de Capacitor lo reserva para desarrollo).")
        if debug:
            add("C03", "MEDIA", rel(c), "webContentsDebuggingEnabled en true: se puede depurar la web de la app desde fuera. Déjalo en false al publicar.")
        if re.search(r"(?i)keystore(Alias)?Password\W*[:=]\W*[\"'][^\"'$]{4,}", t):
            add("C04", "ALTA", rel(c), "Contraseña de la llave escrita en la configuración de Capacitor. Léela de variables de entorno.")
        if appid and any(appid.startswith(x) for x in IDS_POR_DEFECTO):
            add("C05", "MEDIA", rel(c), "El appId es el de ejemplo (io.ionic.starter, com.example…): cámbialo por uno propio antes de publicar; después ya no se puede cambiar en Play.")

    # ---- Flujos de GitHub Actions
    for f in flujos:
        t = leer(f)
        nombre = rel(f)
        lineas = t.splitlines()
        for i, l in enumerate(lineas, 1):
            m = re.match(r"^\s*-?\s*uses:\s*([^\s#]+)", l)
            if m and "@" not in m.group(1) and not m.group(1).startswith("./"):
                add("W01", "MEDIA", f"{nombre}:{i}", f"La acción {m.group(1)} no tiene versión fija (@vX o commit).")
            elif m and re.search(r"@(main|master|latest)$", m.group(1)):
                add("W01", "MEDIA", f"{nombre}:{i}", f"La acción {m.group(1)} sigue una rama: puede cambiar sin avisar. Fija una versión.")
            if re.search(r"(?i)\becho\b[^\n]*\$\{\{\s*secrets\.", l):
                add("W04", "ALTA", f"{nombre}:{i}", "Imprime un secreto con echo: quedaría en el registro público del flujo.")
            if re.search(r"\$\{\{\s*github\.(head_ref|event\.(pull_request|issue|comment|review|head_commit)[\w.\[\]-]*\.(title|body|message|ref|label|name))\s*\}\}", l) \
                    and not re.match(r"^\s*(-\s*)?(if:|[A-Za-z_][A-Za-z0-9_]*:\s*\$\{\{)", l):
                add("W08", "ALTA", f"{nombre}:{i}", "Usa texto que escribe otra persona (título, rama, mensaje) dentro de un comando: permite inyectar comandos. Pásalo por una variable de entorno y úsala entre comillas.")
        if re.search(r"(?m)^\s*pull_request_target\s*:", t) and re.search(r"head\.(sha|ref)|github\.head_ref", t):
            add("W05", "ALTA", nombre, "pull_request_target junto con el código del PR: ese código corre con permisos de escritura y secretos.")
        if not re.search(r"(?m)^permissions\s*:", t):
            add("W02", "BAJA", nombre, "Sin «permissions:» al inicio: el flujo recibe permisos más amplios de los necesarios. Pon contents: read.")
        if "gradlew" in t:
            if not re.search(r"setup-gradle|cache:\s*gradle|actions/cache", t):
                add("W07", "BAJA", nombre, "Construye con Gradle sin caché: cada ejecución baja todo otra vez. Usa gradle/actions/setup-gradle (con cache-provider: basic si quieres solo código abierto) o setup-java con cache: gradle.")
            if "timeout-minutes" not in t:
                add("W03", "BAJA", nombre, "Sin timeout-minutes: una construcción colgada gasta minutos hasta las 6 horas.")
    return h


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        print("Uso: python -I revisar_android.py CARPETA_DEL_PROYECTO [--json]", file=sys.stderr)
        return 2
    try:
        hallazgos = revisar(args[0])
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    orden = {"ALTA": 0, "MEDIA": 1, "BAJA": 2}
    hallazgos.sort(key=lambda x: (orden[x["gravedad"]], x["id"], x["donde"]))
    if "--json" in argv:
        print(json.dumps(hallazgos, ensure_ascii=False, indent=2))
    else:
        if not hallazgos:
            print("Sin hallazgos. (No prueba que la app sea segura ni que Google Play la acepte.)")
        for x in hallazgos:
            print(f"[{x['gravedad']}] {x['id']} · {x['donde']}: {x['texto']}")
        print(f"\n{len(hallazgos)} hallazgo(s), {sum(1 for x in hallazgos if x['gravedad'] == 'ALTA')} grave(s).")
    return 1 if any(x["gravedad"] == "ALTA" for x in hallazgos) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
