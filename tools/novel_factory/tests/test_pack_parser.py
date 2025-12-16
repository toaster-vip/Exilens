import json
import pytest

from novel_factory.pack_parser import parse_pack, PackValidationError


def test_invalid_pack_raises():
    bad = {"chapter_title": "x"}
    with pytest.raises(PackValidationError):
        parse_pack(json.dumps(bad))