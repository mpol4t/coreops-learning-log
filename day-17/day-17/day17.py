import sys
import argparse

def read_limit(path):
    with open(path, encoding="utf-8") as file:
        sayı = file.read()
        sayı = sayı.strip()
        sayı = int(sayı)
        if sayı <= 0:
            raise ValueError
        return sayı
            

def main():
    try: 
        parser = argparse.ArgumentParser()
        parser.add_argument("path")
        args = parser.parse_args()
        sonuç = read_limit(args.path)
        print(sonuç)
        return 0
    except ValueError:
        print(f"Hatalı değer!!", file=sys.stderr)
        return(11)
    except FileNotFoundError:
        print("Girdiğiniz path bulunamadı!!", file=sys.stderr)
        return(22)
    
if __name__ == "__main__":
    sys.exit(main())