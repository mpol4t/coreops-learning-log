from src.scanner import scanner
import sys


def main():
    try:
        sonuç = scanner(".")
        print(sonuç)
        return 0

    except FileNotFoundError:
        print("Girilen path bulunamadı!", file=sys.stderr)
        return 11

    except NotADirectoryError:
        print("Girilen path directory değil!", file=sys.stderr)
        return 22


if __name__ == "__main__":
    sys.exit(main())
