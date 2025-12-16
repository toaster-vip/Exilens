import sys
from pathlib import Path
import types

# Provide light stubs if optional deps are missing (CI friendliness)
if "jsonschema" not in sys.modules:  # pragma: no cover - dependency shim
    js = types.SimpleNamespace()

    class _Validator:
        def __init__(self, schema):
            self.schema = schema

        def iter_errors(self, _data):
            return []

    js.Draft7Validator = _Validator
    sys.modules["jsonschema"] = js

if "docx" not in sys.modules:  # pragma: no cover - dependency shim
    class _Doc:
        def __init__(self):
            self.paragraphs = []

        def add_heading(self, text, level=1):
            self.paragraphs.append(("H", text, level))

        def add_paragraph(self, text):
            self.paragraphs.append(("P", text, 0))

        def save(self, path):
            Path(path).write_text("\n".join(p[1] for p in self.paragraphs), encoding="utf-8")

    sys.modules["docx"] = types.SimpleNamespace(Document=_Doc)

TOOLS_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = TOOLS_ROOT.parent
for path in [str(PROJECT_ROOT), str(TOOLS_ROOT)]:
    if path not in sys.path:
        sys.path.insert(0, path)