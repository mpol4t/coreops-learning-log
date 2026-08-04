import sys


def ordered(dosya):
    sıralı_servisler = []
    son_durum = {}
    fail_servisler = set()

    with open(dosya) as file:
        for x in file:
            servis, durum = x.strip().split(",")

            if servis not in sıralı_servisler:
                sıralı_servisler.append(servis)

            son_durum[servis] = durum

            if durum == "fail":
                fail_servisler.add(servis)

    return sıralı_servisler, son_durum, fail_servisler


def main():
    try:
        for dosya in ["services.txt", "services2.txt"]:
            sıralı_servisler, son_durum, fail_servisler = ordered(dosya)
            
            print(f"\n{dosya}")
            print("Sıralı servisler:", sıralı_servisler)
            print("Servislerin son durumu:", son_durum)
            print("Fail servisler:", fail_servisler)
            
    except IsADirectoryError as hata:
        print(
            f"Girdiğiniz path bir dosya değil, dizindir. Hata: {hata}",
            file=sys.stderr
        )
        return 11

    except FileNotFoundError as hata:
        print(
            f"Girdiğiniz path bulunamadı. Hata: {hata}",
            file=sys.stderr
        )
        return 21
    
    return 0

if __name__ == "__main__":
    sys.exit(main())