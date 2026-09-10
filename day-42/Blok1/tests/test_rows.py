import pytest

from Blok1.src.rows import classify_rows

@pytest.fixture
def normal_assets():
    return [1,2,3]

def test_normal(normal_assets):
    result = classify_rows(normal_assets)
    assert result == "normal"
    
@pytest.mark.parametrize(
    "value, expected", 
    [
        ([], "empty"),
        ([1], "normal"),
        ([1,2,3,4,5,6,7,8,9,10], "large"),    
    ]
)
def test_boş_and_large(value, expected):
   result = classify_rows(value)
   assert result == expected
   