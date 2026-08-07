def okuyucu(dosya):
    with open(dosya, encoding="utf-8") as f:
        satır_sayısı = 0
        benzersizler = set()
        for x in f:
            x = x.strip()
            if x:
                satır_sayısı += 1
                benzersizler.add(x)
            
    return satır_sayısı, benzersizler

for x in ["data.txt", "boş.txt"]: 
    satır_sayısı, benzersizler = okuyucu(x)
    if benzersizler:
        print(f"Satır sayısı: {satır_sayısı}")
        print(f"Benzersiz metinler: {benzersizler}")
    else:
        print("-----------00000------------")
        print(f"{x} dosyası boş.")