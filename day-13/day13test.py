from pathlib import Path
from day13 import release_summary

bos_olmayan_txtler, bos_txtler, durum_bilgisi = release_summary("gate13")

assert bos_olmayan_txtler == [
    Path("release/api.txt"),
    Path("release/db.txt"),
    Path("release/nested/cache.txt"),
]

assert bos_txtler == [
    Path("release/nested/empty.txt")
]

assert list(durum_bilgisi.items()) == [
    (Path("release/api.txt"), "Ok"),
    (Path("release/db.txt"), "Fail"),
    (Path("release/nested/cache.txt"), "Ok"),
]

assert Path("release/nested/empty.txt") not in durum_bilgisi

assert Path("release/README.md") not in bos_olmayan_txtler
assert Path("release/README.md") not in bos_txtler
assert Path("release/nested/cache.txt") in bos_olmayan_txtler

try:
    release_summary("başarılı.txt")
    assert False
except NotADirectoryError:
    pass

try:
    release_summary("olmayan_root")
    assert False
except FileNotFoundError:
    pass

bos_olmayan, boslar, durumlar = release_summary("boş_root")

assert bos_olmayan == []
assert boslar == []
assert durumlar == {}