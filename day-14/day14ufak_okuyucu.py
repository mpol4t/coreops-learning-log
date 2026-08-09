import sys

def okuyucu(dosya):
    with open(dosya, encoding="utf-8") as file:
        içerik = file.read()
        return içerik
        
def main():
    içerik = okuyucu("state.txt")
    print(içerik)
    return 0

if __name__ == "__main__":
    sys.exit(main())