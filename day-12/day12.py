import sys

def summarizer(metin):
    with open(metin, encoding="utf-8") as file:
        metin = file.read()
        kelimeler = metin.split()
        ilk_20 = kelimeler[:20]
        özet = " ".join(ilk_20)
        if len(kelimeler) > 20:
            return özet + "..."
        else: 
            return metin

def main():
    try:
        print(summarizer("input.txt"))
        return 0
    
    except FileNotFoundError as hata:
        print(f"Dosya bulunamadı!: {hata}", file=sys.stderr)
        return 11
    
    except IsADirectoryError as hata:
        print(f"Girdiğiniz path bir dizin: {hata}", file=sys.stderr)
        return 22
    
if __name__ == "__main__":
    sys.exit(main())




    