import pytest

from Blok1.src.assets_gösterilmiş import normalize_hostname


@pytest.fixture
def raw_hostname():
    return "  SERVER-01.LOCAL  "


def test_normalize_hostname(raw_hostname):
    result = normalize_hostname(raw_hostname)

    assert result == "server-01.local"


@pytest.mark.parametrize(
    "value",
    ["", " ", "     "],
)
def test_normalize_hostname_rejects_empty(value):
    with pytest.raises(ValueError):
        normalize_hostname(value)