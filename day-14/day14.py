from pathlib import Path
import sys

def analayzer(root):
    root = Path(root)
    if not root.exists():
        raise FileNotFoundError
    
    if not root.is_dir():
        raise NotADirectoryError
    
    dosyalar = []
    for x in sorted(root.rglob("*.txt")):
        if x.is_file():
            relative = x.relative_to(root)
            dosyalar.append(relative)
    return dosyalar

def main():
    try:
        sonuç = analayzer("gate13")
        print(sonuç)
        return 0
    
    except FileNotFoundError:
        print("Dosya bulunamadı!", file=sys.stderr)
        return 11

    except NotADirectoryError:
        print("Girdiğiniz path bir directory değil!", file=sys.stderr)
        return 22
    
if __name__ == "__main__":
    sys.exit(main())
    