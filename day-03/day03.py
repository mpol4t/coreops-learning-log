kayitlar = [
    ("nginx", "ok"),
    ("redis", "fail"),
    ("nginx", "fail"),
    ("mysql", "ok"),
    ("redis", "ok")
]

def analayzer(kayıtlar):
    servis_adları = []
    son_durum = {}
    başarısız_servisler = set()
    for x in kayıtlar:
        servis, durum = x
        servis_adları.append(servis)
        son_durum[servis] = durum
        if durum == "fail":
            başarısız_servisler.add(servis)

    return servis_adları, son_durum, başarısız_servisler

servis_adları, son_durum, başarısız_servisler = analayzer(kayitlar)

print("Servis adları:", servis_adları)
print("Son durumlar:", son_durum)
print("Başarısız servisler:", başarısız_servisler)
