"""Pruebas de revisar_android.py: proyecto bueno, proyecto malo y cambios puntuales hechos a propósito."""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

try:
    import yaml  # opcional
except ImportError:
    yaml = None

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / "skills/verificar-apk/scripts/revisar_android.py"
EJ = RAIZ / "skills/verificar-apk/ejemplos"


def correr(carpeta, *extra):
    r = subprocess.run([sys.executable, "-I", str(SCRIPT), str(carpeta), *extra], capture_output=True, text=True, timeout=60)
    return r.returncode, r.stdout, r.stderr


def ids(out):
    return {h["id"] for h in json.loads(out)}


class TestRevisorAndroid(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.p = self.tmp / "proyecto"
        shutil.copytree(EJ / "proyecto-bueno", self.p)
        self.manifest = self.p / "android/app/src/main/AndroidManifest.xml"
        self.gradle = self.p / "android/app/build.gradle"
        self.vars = self.p / "android/variables.gradle"
        self.cap = self.p / "capacitor.config.json"
        self.wf = self.p / ".github/workflows/apk.yml"

    def cambiar(self, archivo, viejo, nuevo):
        t = archivo.read_text(encoding="utf-8")
        self.assertIn(viejo, t, f"el ejemplo bueno ya no contiene «{viejo}»")
        archivo.write_text(t.replace(viejo, nuevo), encoding="utf-8")

    def esperar(self, regla, grave=None):
        c, out, _ = correr(self.p, "--json")
        self.assertIn(regla, ids(out), f"no saltó {regla}")
        if grave is not None:
            self.assertEqual(c, 1 if grave else 0)

    def test_bueno_sale_limpio(self):
        c, out, _ = correr(EJ / "proyecto-bueno", "--json")
        self.assertEqual((c, json.loads(out)), (0, []))

    def test_malo_detecta_todo(self):
        c, out, _ = correr(EJ / "proyecto-malo", "--json")
        self.assertEqual(c, 1)
        esperadas = {"A01", "A02", "A03", "A04", "A05", "A06", "A07", "C01", "C02", "C03", "C05", "G01", "G04", "G05", "G06", "G07",
                     "K01", "W01", "W02", "W03", "W04", "W05", "W07", "W08"}
        self.assertTrue(esperadas <= ids(out), f"faltan: {esperadas - ids(out)}")

    def test_no_muestra_valores_secretos(self):
        _, out, _ = correr(EJ / "proyecto-malo")
        for secreto in ("contrasena-inventada-123", "192.168.0.10"):
            self.assertNotIn(secreto, out)

    def test_cambios_a_proposito(self):
        self.cambiar(self.manifest, 'android:allowBackup="false"', 'android:allowBackup="false" android:debuggable="true"')
        self.esperar("A01", True)

    def test_exported_obligatorio(self):
        self.cambiar(self.manifest, 'android:name=".MainActivity" android:exported="true"', 'android:name=".MainActivity"')
        self.esperar("A04", True)

    def test_target_sdk_desde_variables(self):
        self.cambiar(self.vars, "targetSdkVersion = 36", "targetSdkVersion = 34")
        self.esperar("G01", True)

    def test_target_sdk_desde_catalogo_de_versiones(self):
        (self.p / "android/gradle").mkdir()
        (self.p / "android/gradle/libs.versions.toml").write_text('[versions]\ntargetSdk = "34"\n', encoding="utf-8")
        self.cambiar(self.gradle, "targetSdkVersion rootProject.ext.targetSdkVersion", "targetSdk = libs.versions.targetSdk.get().toInt()")
        self.esperar("G01", True)

    def test_target_sdk_36_o_mas_pasa(self):
        self.cambiar(self.vars, "targetSdkVersion = 36", "targetSdkVersion = 37")
        c, out, _ = correr(self.p, "--json")
        self.assertNotIn("G01", ids(out))

    def test_release_con_llave_de_depuracion_y_debuggable(self):
        self.cambiar(self.gradle, "signingConfig signingConfigs.release", "signingConfig signingConfigs.debug\n            debuggable true")
        c, out, _ = correr(self.p, "--json")
        self.assertTrue({"G06", "G07"} <= ids(out))

    def test_contrasena_escrita_en_gradle(self):
        self.cambiar(self.gradle, "storePassword System.getenv(\"KEYSTORE_PASSWORD\")", 'storePassword "algo-inventado"')
        self.esperar("G04", True)

    def test_llave_de_firma_en_el_proyecto(self):
        (self.p / "android/app/mi.jks").write_text("relleno", encoding="utf-8")
        (self.p / ".gitignore").write_text("node_modules/\n", encoding="utf-8")
        self.esperar("K01", True)
        (self.p / ".gitignore").write_text("*.jks\n", encoding="utf-8")
        _, out, _ = correr(self.p, "--json")
        self.assertNotIn("K01", ids(out))

    def test_clave_escrita_y_marcador(self):
        (self.p / "www").mkdir()
        (self.p / "www/app.js").write_text('const t = "000000000:' + "A" * 35 + '";\n', encoding="utf-8")
        self.esperar("K02", True)
        (self.p / "www/app.js").write_text('const t = "<YOUR_KEY>"; // sk-your-key-goes-here-xxxxxxxxxxxxxxxx\n', encoding="utf-8")
        _, out, _ = correr(self.p, "--json")
        self.assertNotIn("K02", ids(out))

    def test_capacitor_server_url(self):
        self.cambiar(self.cap, '"webDir": "www"', '"webDir": "www", "server": {"url": "http://192.168.0.5:8100"}')
        self.esperar("C01", True)

    def test_capacitor_ts(self):
        self.cap.unlink()
        (self.p / "capacitor.config.ts").write_text("const config = { appId: 'io.ionic.starter', server: { url: 'http://x', cleartext: true } };\nexport default config;\n", encoding="utf-8")
        c, out, _ = correr(self.p, "--json")
        self.assertTrue({"C01", "C02", "C05"} <= ids(out))

    def test_flujo_de_actions(self):
        self.cambiar(self.wf, "actions/checkout@v7", "actions/checkout@main")
        self.cambiar(self.wf, "permissions:\n  contents: read\n", "")
        self.cambiar(self.wf, "    timeout-minutes: 30\n", "")
        self.cambiar(self.wf, "      - uses: gradle/actions/setup-gradle@v6\n        with:\n          cache-provider: basic\n", "")
        c, out, _ = correr(self.p, "--json")
        self.assertTrue({"W01", "W02", "W03", "W07"} <= ids(out))

    def test_variable_de_entorno_es_la_forma_segura(self):
        """Pasar el título por una variable de entorno es lo correcto: no debe saltar W08."""
        self.cambiar(self.wf, "        run: ./gradlew assembleDebug --no-daemon", "        env:\n          TITULO: ${{ github.event.pull_request.title }}\n        run: ./gradlew assembleDebug --no-daemon")
        _, out, _ = correr(self.p, "--json")
        self.assertNotIn("W08", ids(out))

    # ---- APK ya construido y decodificado con apktool
    def test_apk_decodificado(self):
        c, out, _ = correr(EJ / "apk-decodificado", "--json")
        self.assertEqual(c, 1)
        self.assertTrue({"A01", "A03"} <= ids(out))
        self.assertNotIn("A00", ids(out), "el manifiesto binario de original/ no debe leerse como XML")

    def test_apk_decodificado_con_target_sdk_bajo(self):
        dec = self.tmp / "dec"
        shutil.copytree(EJ / "apk-decodificado", dec)
        y = dec / "apktool.yml"
        y.write_text(y.read_text(encoding="utf-8").replace("targetSdkVersion: 36", "targetSdkVersion: 34"), encoding="utf-8")
        _, out, _ = correr(dec, "--json")
        self.assertIn("G01", ids(out))

    def test_manifiesto_binario_se_ignora(self):
        (self.p / "otro").mkdir()
        (self.p / "otro/AndroidManifest.xml").write_bytes(b"\x03\x00\x08\x00binario")
        _, out, _ = correr(self.p, "--json")
        self.assertNotIn("A00", ids(out))

    # ---- Plantilla de revisión de flujos (actionlint y zizmor)
    def test_plantilla_revisar_flujos_es_segura_y_fijada(self):
        t = (RAIZ / "skills/verificar-apk/plantilla/revisar-flujos.yml").read_text(encoding="utf-8")
        for usos in re.findall(r"uses:\s*(\S+)", t):
            self.assertRegex(usos, r"@[0-9a-f]{40}$", f"acción sin commit fijo: {usos}")
        self.assertIn("persist-credentials: false", t)
        self.assertIn("sha256sum -c", t)
        self.assertIn("--offline", t)
        self.assertRegex(t, r"(?m)^permissions:\n  contents: read")

    @unittest.skipIf(yaml is None, "PyYAML no está instalado")
    def test_los_flujos_de_los_ejemplos_son_yaml_valido(self):
        for f in (RAIZ / "skills/verificar-apk").rglob("*.yml"):
            try:
                yaml.safe_load(f.read_text(encoding="utf-8"))
            except yaml.YAMLError as e:
                self.fail(f"{f.relative_to(RAIZ)} no es YAML válido: {str(e)[:80]} (GitHub lo rechazaría)")

    def test_la_plantilla_pasa_el_propio_revisor(self):
        (self.p / ".github/workflows/apk.yml").unlink()
        shutil.copy(RAIZ / "skills/verificar-apk/plantilla/revisar-flujos.yml", self.p / ".github/workflows/revisar-flujos.yml")
        c, out, _ = correr(self.p, "--json")
        self.assertEqual((c, json.loads(out)), (0, []))

    def test_errores_de_entrada(self):
        self.assertEqual(correr(self.tmp / "no-existe")[0], 2)
        vacia = self.tmp / "vacia"; vacia.mkdir()
        self.assertEqual(correr(vacia)[0], 2)
        roto = self.tmp / "roto"; (roto / "app").mkdir(parents=True); (roto / "app/AndroidManifest.xml").write_text("<manifest", encoding="utf-8")
        c, out, _ = correr(roto, "--json")
        self.assertIn("A00", ids(out))
        self.assertEqual(subprocess.run([sys.executable, "-I", str(SCRIPT)], capture_output=True).returncode, 2)


if __name__ == "__main__":
    unittest.main()
