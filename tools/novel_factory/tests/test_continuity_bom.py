from __future__ import annotations

from pathlib import Path
from novel_factory.continuity import Continuity


def test_continuity_can_read_utf8_bom(tmp_path: Path):
    # Write UTF-8 with BOM explicitly
    p = tmp_path / "continuity.json"
    p.write_bytes(b"\xef\xbb\xbf{}")
    c = Continuity(p)
    assert isinstance(c.data, dict)
