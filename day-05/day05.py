import sys

def dosya_satır_sayısı(path):
    try:
        satır_sayısı = 0
        with open(path) as file:
            for x in file:
                satır_sayısı += 1
        return satır_sayısı
    except IsADirectoryError as hata:
        print(f"Path is a dir not a file: {hata}", file=sys.stderr)
    except FileNotFoundError as hata:
        print(f"File does not exists: {hata}", file=sys.stderr)
        
# dosya_satır_sayısı("data.txt") -> Varken doğru çalışıyor 2 dönüyor.
# dosya_satır_sayısı("day06.py") -> Var olmayan bir dosya belirlediğim exit code dönüyor
sonuç = dosya_satır_sayısı("asd") # -> Dizin path'i çalıştırılıyor.
if sonuç is None:
    sys.exit(131)
else:
    print(sonuç)