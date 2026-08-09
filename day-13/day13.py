from pathlib import Path
import sys

def release_summary(root):
    root = Path(root)
    boş_olmayan_txtler = []
    boş_txtler = []
    durum_bilgisi = {}
    if root.exists():
        if root.is_dir():
            for x in sorted(root.rglob("*.txt")):
                if x.is_file():
                    with open(x, encoding="utf-8") as file:
                        dosya = file.readline()
                        dosya = dosya.strip()
                        if not dosya:
                            relative = x.relative_to(root)
                            boş_txtler.append(relative)
                        else:
                            relative = x.relative_to(root)
                            boş_olmayan_txtler.append(relative)
                            durum_bilgisi[relative] = dosya
            return boş_olmayan_txtler, boş_txtler, durum_bilgisi

        else:
            raise NotADirectoryError
    else:
        raise FileNotFoundError

def main():
    try:
        sonuç = release_summary("gate13")
        boş_olmayan_txtler, boş_txtler, durum_bilgisi = sonuç
        print(f"Boş olamayan txlter: {boş_olmayan_txtler}")
        print(f"Boş olan txlter: {boş_txtler}")
        for yol, durum in durum_bilgisi.items():
            print(f"{yol} -> {durum}")
        return 0
        
    except NotADirectoryError as hata:
        print("Girdiğiniz path bir directory değil!", file=sys.stderr)
        return 11
    
    except FileNotFoundError as hata:
        print("Girdiğin path bulunamadı!", file=sys.stderr)
        return 22
        

if __name__ == "__main__":
    sys.exit(main())