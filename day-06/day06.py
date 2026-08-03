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


try:
    sıralı_servisler, son_durum, fail_servisler = ordered(".")

except IsADirectoryError as hata:
    print(
        f"Girdiğiniz path bir dosya değil, dizindir. Hata: {hata}",
        file=sys.stderr
    )
    sys.exit(11)

except FileNotFoundError as hata:
    print(
        f"Girdiğiniz path bulunamadı. Hata: {hata}",
        file=sys.stderr
    )
    sys.exit(21)


print("Sıralı servisler:", sıralı_servisler)
print("Servislerin son durumu:", son_durum)
print("Fail servisler:", fail_servisler)
    
