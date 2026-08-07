from pathlib import Path


def txt_bulucu(path):
    root = Path(path)
    
    if not root.exists():
        raise FileNotFoundError(f"Path bulunamadı: {root}")

    if not root.is_dir():
        raise NotADirectoryError(f"Path bir dizin değil: {root}")

    txtler = []

    for x in root.rglob("*.txt"):
        if x.is_file():
            txtler.append(x)

    txtler.sort()
    return txtler


try:
    sonuc = txt_bulucu(".")
    print(sonuc)

except FileNotFoundError as hata:
    print(f"Hata: {hata}")

except NotADirectoryError as hata:
    print(f"Hata: {hata}")