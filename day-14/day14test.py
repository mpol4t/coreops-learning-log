from pathlib import Path
from day14 import analayzer

sonuç = analayzer("gate13")

assert sonuç == [
    Path("release/api.txt"),
    Path("release/db.txt"),
    Path("release/nested/cache.txt"),
    Path("release/nested/empty.txt"),
    Path("release/nested/late.txt")
]

sonuç2 = analayzer("boş_root")

assert sonuç2 == []

try:
    sonuç3 = analayzer("olamayan_root")
    assert False
except FileNotFoundError:
    pass

try:
    sonuç4 = analayzer("day14.py")
    assert False
except NotADirectoryError:
    pass