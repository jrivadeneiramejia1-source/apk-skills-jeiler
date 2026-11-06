"""Pruebas del repo: estructura, grupos, encabezados y datos personales. Correr: python -I -m unittest discover -s tests"""
import re
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SKILLS = RAIZ / "skills"
ORIGINALES = ["web-a-apk", "verificar-apk", "pruebas-maestro"]

try:
    import yaml  # opcional
except ImportError:
    yaml = None


def grupos():
    g = {}
    for linea in (RAIZ / "grupos.conf").read_text(encoding="utf-8").splitlines():
        if linea.strip() and not linea.lstrip().startswith("#"):
            nombre, _, resto = linea.partition(":")
            g[nombre.strip()] = resto.split()
    return g


def encabezado(skill_md):
    m = re.match(r"^---\n(.*?)\n---\n", skill_md.read_text(encoding="utf-8"), re.S)
    return m.group(1) if m else None


class TestEstructura(unittest.TestCase):
    def test_grupos_apuntan_a_skills_que_existen(self):
        for g, lista in grupos().items():
            for s in lista:
                self.assertTrue((SKILLS / s / "SKILL.md").is_file(), f"grupo {g}: falta la skill {s}")

    def test_cada_skill_esta_en_algun_grupo(self):
        en_grupos = {s for lista in grupos().values() for s in lista}
        en_disco = {p.name for p in SKILLS.iterdir() if (p / "SKILL.md").is_file()}
        self.assertEqual(en_disco - en_grupos, set(), "skills que ningún grupo instala")

    def test_encabezados_validos(self):
        for lista in grupos().values():
            for s in lista:
                h = encabezado(SKILLS / s / "SKILL.md")
                self.assertIsNotNone(h, f"{s}: sin encabezado --- ---")
                nombre = re.search(r"(?m)^name:\s*(\S+)", h)
                self.assertTrue(nombre and nombre.group(1) == s, f"{s}: name no coincide con la carpeta")
                desc = re.search(r"(?m)^description:\s*(.+)$", h)
                self.assertTrue(desc and desc.group(1).strip(), f"{s}: sin description")
                v = desc.group(1).strip()
                if not v.startswith(("'", '"', ">", "|")):
                    self.assertNotIn(": ", v, f"{s}: la description tiene «: » sin comillas (YAML la rompe)")

    @unittest.skipIf(yaml is None, "PyYAML no está instalado (pip install pyyaml)")
    def test_encabezados_son_yaml_valido(self):
        for lista in grupos().values():
            for s in lista:
                try:
                    datos = yaml.safe_load(encabezado(SKILLS / s / "SKILL.md"))
                except yaml.YAMLError as e:
                    self.fail(f"{s}: el encabezado no es YAML válido ({str(e)[:80]})")
                self.assertTrue(datos.get("description"), s)

    def test_claude_md_con_reglas(self):
        t = (RAIZ / "CLAUDE.md").read_text(encoding="utf-8")
        for frase in ("claves", "main", "indígenas", "[F]"):
            self.assertIn(frase, t)


class TestSinDatosPersonales(unittest.TestCase):
    CORREO = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
    OK = ("example.", "ejemplo.invalid", "noreply")

    def archivos(self):
        for s in ORIGINALES:
            for p in (SKILLS / s).rglob("*"):
                if p.is_file() and p.suffix in {".md", ".json", ".py", ".yml", ".yaml", ".xml", ".gradle"}:
                    yield p
        for n in ("README.md", "CLAUDE.md", "INDICE-DE-SKILLS.md", "PRUEBAS.md", "LECCIONES.md"):
            if (RAIZ / n).is_file():
                yield RAIZ / n

    def test_sin_correos_reales(self):
        for p in self.archivos():
            for m in self.CORREO.findall(p.read_text(encoding="utf-8", errors="replace")):
                self.assertTrue(any(o in m for o in self.OK), f"{p.relative_to(RAIZ)}: correo {m}")

    def test_documentos_usan_python_no_python3(self):
        for p in self.archivos():
            if p.suffix == ".md":
                self.assertNotIn("python3 ", p.read_text(encoding="utf-8"), f"{p.relative_to(RAIZ)} usa python3 (Jeiler usa python)")


if __name__ == "__main__":
    unittest.main()
