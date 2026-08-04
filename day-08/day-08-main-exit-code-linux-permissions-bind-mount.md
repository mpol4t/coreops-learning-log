---
title: "Gün 08 — main(), Exit Code, Linux İzinleri ve Bind Mount"
tags:
  - coreops
  - python
  - linux
  - docker
  - main
  - exit-code
  - permissions
  - bind-mount
aliases:
  - "Gün 8 Main Exit Code Linux İzinleri ve Bind Mount"
status: completed
assistance_level: 1.5
duration_minutes: 100
---

# 🧠 Gün 8 — `main()`, Exit Code, Linux İzinleri ve Bind Mount

> [!info] Kaynak  
> Bu not, Gün 8 çalışma ve deney kayıtları temel alınarak düzenlendi.

> [!abstract] 🎯 Ana fikir  
> Programın veri işleme mantığı ile process yönetimi birbirinden ayrılmalıdır.
> 
> ```text
> Veri işleme fonksiyonu
> → Veriyi işler.
> → Sonuç döndürür.
> → Gerekirse exception yükseltir.
> 
> main()
> → Program akışını yönetir.
> → Kullanıcıya mesaj gösterir.
> → Exit code döndürür.
> 
> sys.exit(main())
> → main() sonucunu işletim sistemine bildirir.
> ```
> 
> Linux ve Docker tarafında ise dosyanın:
> 
> - Okunabilir olması,
>     
> - Yazılabilir olması,
>     
> - Doğrudan çalıştırılabilir olması,
>     
> - Bind mount’un yazılabilir veya salt okunur olması
>     
> 
> farklı kontrollerdir.

---

# ⚡ 2 Dakikalık Geri Çağırma

## `main()` neden çoğunlukla exit code döndürür?

CLI programlarında asıl veriyi alt fonksiyonlar üretir.

`main()` ise bu sonuçlara bakarak programın nasıl tamamlandığına karar verir:

```python
def main():
    return 0
```

Genel sözleşme:

```text
0       → Başarı
0 dışı  → Hata veya başarısızlık
```

> [!note]  
> `main()` fonksiyonunun mutlaka exit code döndürmesi Python dilinin zorunlu kuralı değildir.
> 
> Bu, komut satırı programları için temiz ve yaygın bir tasarım tercihidir.

---

## `sys.exit(main())` neden daha esnektir?

TIRT kullanım:

```python
main()
sys.exit(0)
```

Bu yapı, `main()` hangi sonucu üretirse üretsin process’i başarı koduyla bitirir.

Daha doğru yapı:

```python
sys.exit(main())
```

Böylece:

```python
def main():
    if hata_var:
        return 21

    return 0
```

sonucu doğrudan process seviyesine taşınır.

---

## Veri işleme fonksiyonu neden `sys.exit()` çağırmamalıdır?

Çünkü veri işleme fonksiyonunu:

- Başka bir programda kullanmak,
    
- Birim testine sokmak,
    
- Hata durumunda başka bir dosyayı denemek,
    
- Ürettiği sonucu başka hesaplarda kullanmak
    

isteyebilirim.

Fonksiyon doğrudan:

```python
sys.exit(21)
```

çağırırsa yalnızca fonksiyondan çıkmaz; yakalanmayan bir `SystemExit` ile bütün process’i kapatmaya çalışır.

---

# 🐍 Python — Temiz Program Katmanları

## Veri işleme katmanı

```python
def ordered(dosya):
    sıralı_servisler = []
    son_durum = {}
    fail_servisler = set()

    with open(dosya) as file:
        for satır in file:
            servis, durum = satır.strip().split(",")

            if servis not in sıralı_servisler:
                sıralı_servisler.append(servis)

            son_durum[servis] = durum

            if durum == "fail":
                fail_servisler.add(servis)

    return sıralı_servisler, son_durum, fail_servisler
```

Bu fonksiyon:

- Terminale çıktı yazmaz.
    
- Process’i kapatmaz.
    
- Exit code seçmez.
    
- Yalnızca veriyi işler ve sonucu döndürür.
    

Dosya bulunamazsa:

```text
FileNotFoundError
```

Path bir dizinse:

```text
IsADirectoryError
```

exception’ı doğal olarak üst katmana çıkar.

---

## Program yönetim katmanı

```python
def main():
    try:
        for dosya in ["services.txt", "services2.txt"]:
            sıralı, son_durum, fail_olanlar = ordered(dosya)

            print(f"\n{dosya}")
            print("Sıralı servisler:", sıralı)
            print("Servislerin son durumu:", son_durum)
            print("Fail servisler:", sorted(fail_olanlar))

    except IsADirectoryError as hata:
        print(
            f"Girilen path bir dosya değil, dizindir: {hata}",
            file=sys.stderr,
        )
        return 11

    except FileNotFoundError as hata:
        print(
            f"Girilen path bulunamadı: {hata}",
            file=sys.stderr,
        )
        return 21

    return 0
```

`main()`:

- Kullanılacak dosyalara karar verir.
    
- `ordered()` fonksiyonunu çağırır.
    
- Exception’ları kullanıcı mesajına dönüştürür.
    
- Başarı veya hata kodu döndürür.
    

---

## Process katmanı

```python
if __name__ == "__main__":
    sys.exit(main())
```

Akış:

```text
main() çalışır
     ↓
0, 11 veya 21 döndürür
     ↓
sys.exit() bu değeri process exit code’u yapar
     ↓
Shell sonucu $? üzerinden görür
```

---

# 🧱 Temizlenmiş Tam Kod

```python
import sys


IS_DIRECTORY = 11
FILE_NOT_FOUND = 21


def ordered(dosya):
    sıralı_servisler = []
    son_durum = {}
    fail_servisler = set()

    with open(dosya) as file:
        for satır in file:
            servis, durum = satır.strip().split(",")

            if servis not in sıralı_servisler:
                sıralı_servisler.append(servis)

            son_durum[servis] = durum

            if durum == "fail":
                fail_servisler.add(servis)

    return sıralı_servisler, son_durum, fail_servisler


def main():
    try:
        for dosya in ["services.txt", "services2.txt"]:
            sıralı, son_durum, fail_olanlar = ordered(dosya)

            print(f"\n{dosya}")
            print("Sıralı servisler:", sıralı)
            print("Servislerin son durumu:", son_durum)
            print("Fail servisler:", sorted(fail_olanlar))

    except IsADirectoryError as hata:
        print(
            f"Girilen path bir dosya değil, dizindir: {hata}",
            file=sys.stderr,
        )
        return IS_DIRECTORY

    except FileNotFoundError as hata:
        print(
            f"Girilen path bulunamadı: {hata}",
            file=sys.stderr,
        )
        return FILE_NOT_FOUND

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

---

# 🧪 Bu Tasarım Testi Neden Kolaylaştırır?

`ordered()` çağrıldığında yalnızca sonuç döner:

```python
sıralı, son_durum, fail_olanlar = ordered("services.txt")
```

Dönen değerler doğrudan test edilebilir:

```python
assert sıralı == [
    "api",
    "db",
    "cache",
    "worker",
]

assert son_durum == {
    "api": "fail",
    "db": "ok",
    "cache": "ok",
    "worker": "fail",
}

assert fail_olanlar == {
    "api",
    "db",
    "worker",
}
```

Set test edilirken yazdırılma sırasına bakılmaz.

TIRT:

```python
assert str(fail_olanlar) == "{'api', 'db', 'worker'}"
```

Doğru:

```python
assert fail_olanlar == {"api", "db", "worker"}
```

---

## Fonksiyonda `print()` olsaydı

Testin yalnızca dönüş değerini değil, terminal çıktısını da yakalaması gerekirdi.

## Fonksiyonda `sys.exit()` olsaydı

Test sırasında:

```text
SystemExit
```

yakalamak gerekirdi.

Bu yüzden:

```text
Değer üretme
Mesaj gösterme
Process kapatma
```

sorumlulukları ayrılmalıdır.

---

# 🔥 `raise`, `return` ve `sys.exit()` Ayrımı

|Yapı|Etki alanı|Görevi|
|---|---|---|
|`return`|Fonksiyon|Değer döndürür ve fonksiyonu bitirir|
|`raise`|Python çağrı zinciri|Exception’ı üst katmana taşır|
|`sys.exit()`|Process|`SystemExit` yükselterek programı sonlandırır|

Önerilen mimari:

```text
Alt fonksiyon
→ return veya raise

main()
→ exception yakala
→ mesaj yaz
→ exit code döndür

sys.exit(main())
→ process sonucunu bildir
```

---

# ⚠️ `try` Bloğunun Kapsamı

Şu yapıda:

```python
try:
    for dosya in ["services.txt", "services2.txt"]:
        ordered(dosya)
except FileNotFoundError:
    ...
```

ilk dosyalardan biri hata verirse döngünün kalan kısmı çalışmaz.

Örnek:

```text
services.txt  → Başarılı
services2.txt → Bulunamadı
               ↓
except çalışır
               ↓
Program hata koduyla biter
```

Bu davranış şartnameye uygunsa sorun yoktur.

Her dosya bağımsız işlenecekse `try` döngünün içine alınabilir:

```python
for dosya in ["services.txt", "services2.txt"]:
    try:
        sonuc = ordered(dosya)
    except FileNotFoundError as hata:
        print(hata, file=sys.stderr)
        continue
```

---

# 🐧 Linux Dosya İzinleri

`ls -l` çıktısındaki ilk 10 karakter:

```text
-rwxr-xr--
```

şu şekilde ayrılır:

```text
- | rwx | r-x | r--
    u     g     o
```

|Bölüm|Anlam|
|---|---|
|İlk karakter|Dosya türü|
|`u`|Owner/user izinleri|
|`g`|Group izinleri|
|`o`|Others izinleri|

---

# 📄 Dosya Türü Karakterleri

|Karakter|Tür|
|---|---|
|`-`|Normal dosya|
|`d`|Dizin|
|`l`|Sembolik bağlantı|

Örnek:

```text
-rw-r--r-- → Normal dosya
drwxr-xr-x → Dizin
lrwxr-xr-x → Symlink
```

---

# 📄 Normal Dosyada `rwx`

## `r` — Read

Dosyanın içeriğini okuyabilme iznidir.

```bash
cat dosya.txt
```

için okuma izni gerekir.

## `w` — Write

Dosya içeriğini değiştirebilme iznidir.

> [!warning]  
> Dosyanın `w` izni, dosyayı silme yetkisi değildir.
> 
> Dosyanın silinmesi büyük ölçüde bulunduğu dizinin izinlerine bağlıdır.

## `x` — Execute

Dosyayı doğrudan program olarak çalıştırabilme iznidir.

```bash
./script.py
```

için genellikle:

- Dosyada `x` izni
    
- Uygun shebang
    
- Yorumlayıcının mevcut olması
    

gerekir.

---

# 📁 Dizinde `rwx`

Dizin izinlerinin anlamı dosyadan farklıdır.

|İzin|Dizindeki anlamı|
|---|---|
|`r`|Dizindeki isimleri listeleyebilmek|
|`w`|Dosya eklemek, silmek veya yeniden adlandırmak|
|`x`|Dizinden geçmek ve içindeki isimlere erişmek|

> [!danger] TIRT düşünce  
> “Dizindeki `x`, dizini çalıştırmak demektir.”
> 
> Yanlış.
> 
> Dizindeki `x`, geçiş ve erişim iznidir.

---

## Dizin izin kombinasyonları

### `r` var, `x` yok

Dosya adlarını görebilirsin ancak dosyalara normal şekilde erişemeyebilirsin.

### `x` var, `r` yok

Dizini listeleyemezsin ancak dosyanın adını biliyorsan ona erişebilirsin.

### `w` var, `x` yok

Dosya ekleme ve silme işlemleri pratikte kullanışsız hâle gelir çünkü dizindeki girişlere erişim yoktur.

---

# 🔢 Sayısal İzinler

```text
r = 4
w = 2
x = 1
```

Toplamlar:

|Sayı|İzin|
|--:|---|
|`7`|`rwx`|
|`6`|`rw-`|
|`5`|`r-x`|
|`4`|`r--`|
|`3`|`-wx`|
|`2`|`-w-`|
|`1`|`--x`|
|`0`|`---`|

Basamaklar:

```text
owner | group | others
```

---

## Örnekler

```bash
chmod 644 file.txt
```

Sonuç:

```text
-rw-r--r--
```

```bash
chmod 755 script.py
```

Sonuç:

```text
-rwxr-xr-x
```

`755` sonrasında:

```bash
chmod u-x script.py
```

Sonuç:

```text
-rw-r-xr-x
```

Yalnızca owner bölümündeki `x` kaldırılır.

---

# 🧪 Yapılan İzin Deneyleri

## `chmod 700 metin.txt`

```text
-rwx------
```

Owner:

```text
rwx
```

Group ve others:

```text
---
```

## `chmod 777 script.py`

```text
-rwxrwxrwx
```

Herkes okuyabilir, yazabilir ve çalıştırabilir.

> [!danger]  
> `777`, çoğu gerçek kullanım için gereksiz ve tehlikeli derecede geniştir.
> 
> Bir Python script’ini çalıştırılabilir yapmak için genellikle:
> 
> ```bash
> chmod u+x script.py
> ```
> 
> veya:
> 
> ```bash
> chmod 755 script.py
> ```
> 
> yeterlidir.

---

## `chmod 000 metin.txt`

```text
----------
```

Hiçbir izin yoktur.

Normal kullanıcı:

```bash
cat metin.txt
```

dediğinde:

```text
Permission denied
```

alır.

---

## `chmod 077 script.py`

Sonuç:

```text
----rwxrwx
```

Ayrımı:

```text
owner  → ---
group  → rwx
others → rwx
```

Dosyanın sahibi `polat` olduğu için kernel önce owner izinlerine bakar.

Owner bölümünde `r` olmadığı için:

```bash
cat script.py
```

başarısız olur.

> [!danger] Kritik ayrım  
> Dosyanın sahibiysen ve owner izinleri yetersizse sistem:
> 
> ```text
> “Group veya others bölümünde izin var, oradan devam edeyim.”
> ```
> 
> demez.
> 
> Uygun izin sınıfı seçildikten sonra yalnızca o sınıfın bitleri değerlendirilir.

---

# 🔧 Sembolik `chmod`

```bash
chmod u+x script.py
```

|Parça|Anlam|
|---|---|
|`u`|Owner izin sınıfı|
|`+`|İzin ekle|
|`x`|Execute izni|

`u`, komutu terminalde yazan kişi demek değildir.

Dosyanın owner izin bölümünü ifade eder.

Diğer örnekler:

```bash
chmod g-w dosya.txt
chmod o=r dosya.txt
chmod a+r dosya.txt
```

|İşaret|Anlam|
|---|---|
|`+`|İzin ekle|
|`-`|İzin kaldır|
|`=`|İzinleri tam olarak belirtilen hâle getir|

---

# 🐍 Python Script’ini Çalıştırma Yöntemleri

## Doğrudan çalıştırmak

```bash
./script.py
```

Gerekenler:

```text
Dosyada x izni
Geçerli shebang
Yorumlayıcının bulunması
```

Örnek shebang:

```python
#!/usr/bin/env python3
```

---

## Yorumlayıcı üzerinden çalıştırmak

```bash
python3 script.py
```

Burada doğrudan çalıştırılan program:

```text
python3
```

olur.

`script.py`, Python’a okunacak veri olarak verilir.

Bu nedenle script üzerinde genellikle:

```text
r izni
```

yeterlidir.

Dosyada `x` bulunması şart değildir.

---

## Karşılaştırma

```text
./script.py
→ Script dosyasını process olarak başlat.
→ x izni gerekir.

python3 script.py
→ Python process’ini başlat.
→ Python script’i okur.
→ Script için temel olarak r izni gerekir.
```

> [!warning]  
> Script’in `x` izni olması tek başına yeterli değildir.
> 
> İçeriği geçerli bir executable formatında veya uygun shebang’e sahip olmalıdır.

---

# 🍎 macOS’ta `@` ve `+`

Bunlar klasik `rwx` izinlerinin parçası değildir.

## `@` — Extended Attributes

```text
-rw-r--r--@
```

Dosyada ek metadata bulunduğunu gösterir.

Örnekler:

- Karantina bilgisi
    
- Finder metadata’sı
    
- İndirilme bilgisi
    
- Uygulama tarafından eklenen özellikler
    

İnceleme:

```bash
ls -l@ dosya
xattr -l dosya
```

## `+` — ACL

```text
-rw-r--r--+
```

Klasik owner/group/others izinlerine ek ACL kuralları bulunduğunu gösterir.

İnceleme:

```bash
ls -le dosya
```

İkisini birlikte incelemek:

```bash
ls -le@ dosya
```

---

# 🐳 Docker — Bind Mount ve Dosya İzinleri

## Temel komut

```bash
docker run --rm -it \
  --mount type=bind,source="$PWD",target=/app \
  -w /app \
  python:3.12-slim \
  sh
```

Bu komut:

1. Hosttaki mevcut klasörü `/app` konumuna bağlar.
    
2. Container CWD’sini `/app` yapar.
    
3. `python:3.12-slim` image’ından container oluşturur.
    
4. Container içinde etkileşimli `sh` açar.
    

---

# 🧩 Komutun Parçaları

|Parça|Görevi|
|---|---|
|`docker run`|Container oluşturur ve başlatır|
|`--rm`|Container durunca kaydını siler|
|`-i`|stdin’i açık tutar|
|`-t`|Pseudo-terminal oluşturur|
|`--mount`|Host path’ini container’a bağlar|
|`-w /app`|Container çalışma dizinini `/app` yapar|
|`python:3.12-slim`|Python kurulu Linux image’ı|
|`sh`|Container içinde çalıştırılan shell|

> [!important]  
> `python:3.12-slim`, Linux yerine kullanılan bir şey değildir.
> 
> Linux tabanlı bir image’dır ve içinde Python hazır kuruludur.

---

# 🚨 `python sh` Hatası

TIRT komut:

```bash
docker run ... python:3.12-slim python sh
```

Image adından sonra gelen bölüm container içinde çalıştırılacak komuttur:

```text
python sh
```

Bu yüzden Python:

```text
sh isimli Python dosyasını aç
```

şeklinde yorumlar.

CWD `/app` ise:

```text
/app/sh
```

aranır.

Sonuç:

```text
python: can't open file '/app/sh'
```

Shell açmak için doğru kullanım:

```bash
docker run ... python:3.12-slim sh
```

Python komutu çalıştırmak için:

```bash
docker run ... python:3.12-slim python day08.py
```

---

# 🔗 Bind Mount Kopyalama Değildir

```bash
--mount type=bind,source="$PWD",target=/app
```

şu bağlantıyı kurar:

```text
HOST                                      CONTAINER

$PWD/day08.py        ──────────────────▶  /app/day08.py
$PWD/services.txt    ──────────────────▶  /app/services.txt
```

Container’da ayrı bir kopya oluşturulmaz.

Container `/app` üzerinden hosttaki gerçek dosyalara erişir.

Bu nedenle:

- Hostta yapılan içerik değişikliği container’da görünür.
    
- Container’da yapılan içerik değişikliği hostta görünür.
    
- Hostta yapılan `chmod` değişikliği container’da görülebilir.
    
- Container’da silinen dosya hosttan da silinebilir.
    

---

# ⚠️ Dosyanın Container’dan Silinmesi

Container içinde:

```bash
rm 1stdout.txt
```

çalıştırıldığında host dosyasının da silinmesinin nedeni mount’un yazılabilir olmasıdır.

Kullanılan mount:

```bash
--mount type=bind,source="$PWD",target=/app
```

varsayılan olarak read-write’dır.

Host dosyalarını korumak için:

```bash
--mount type=bind,source="$PWD",target=/app,readonly
```

veya:

```bash
-v "$PWD":/app:ro
```

kullanılmalıdır.

> [!danger] Kritik ders  
> Bind mount edilen geliştirme klasörünü yazılabilir bağlayıp container içinde:
> 
> ```bash
> rm -rf ...
> ```
> 
> kullanmak host verisini gerçekten silebilir.
> 
> Deneme ve analiz çalışmalarında gerekmiyorsa `readonly` kullan.

---

# 🗑️ Dosya Silme Hangi İzne Bağlıdır?

Dosyayı silebilmek yalnızca dosyanın kendi `w` iznine bağlı değildir.

Silme, dizin kaydını değiştirdiği için temel olarak dosyanın bulunduğu dizindeki:

```text
w + x
```

izinlerine bağlıdır.

Bu nedenle salt okunur bir dosya bile bulunduğu dizinde yeterli izin varsa silinebilir.

> [!warning]
> 
> ```text
> Dosyaya yazmak
> ≠
> Dosyayı dizinden silmek
> ```

---

# 🔐 Host ve Container İzinleri Neden Benzer Göründü?

Hostta:

```bash
chmod 777 1stdout.txt
```

sonrasında:

```text
-rwxrwxrwx
```

görüldü.

Container’da:

```bash
ls -l
```

çalıştırıldığında aynı mode bitleri görüldü:

```text
-rwxrwxrwx
```

Çünkü bind mount aynı dosyanın izin metadata’sını container tarafından erişilebilir hâle getirir.

---

## Sahiplik neden farklı göründü?

Host:

```text
polat staff
```

Container:

```text
root root
```

gösterebilir.

Bu, iki ayrı kopya olduğu anlamına gelmez.

Docker Desktop:

- macOS host dosya sistemini,
    
- Linux container ortamına,
    
- UID/GID ve dosya sistemi çeviri katmanı üzerinden
    

sunar.

Mode bitleri benzer görünürken kullanıcı ve grup adları farklı çözülebilir.

> [!important]  
> Host ve container `ls -l` çıktılarının tamamen aynı olması gerekmez.
> 
> Özellikle:
> 
> - Kullanıcı adı
>     
> - Grup adı
>     
> - macOS extended attributes
>     
> - ACL gösterimi
>     
> 
> Linux container içinde farklı veya eksik görünebilir.

---

# 🍎 `@` İşareti Container’da Neden Görünmeyebilir?

Host macOS çıktısı:

```text
-rw-r--r--@
```

Container Linux çıktısı:

```text
-rw-r--r--
```

olabilir.

`@`, macOS extended attribute bilgisidir.

Linux container’daki `ls`, macOS’un metadata gösterimini aynı biçimde sunmak zorunda değildir.

Bu nedenle:

```text
Mode bitleri aynı
Extended attribute göstergesi farklı
```

olabilir.

---

# ❌ `-it` Neden Dosya Tutarlılığının Sebebi Değildir?

Şu yorum TIRT:

```text
“Host ve Docker aynı sonucu verdi çünkü interaktif bağlantı vardı.”
```

`-it` yalnızca:

- stdin’i açık tutar,
    
- pseudo-terminal sağlar.
    

Dosyaların aynı görünmesinin sebebi:

```text
bind mount
```

kullanılmasıdır.

Program sonuçlarının aynı olmasının sebebi ise:

- Aynı Python kodunun,
    
- Aynı veri dosyalarıyla,
    
- Doğru çalışma dizininde
    

çalıştırılmasıdır.

`-it` olmadan da aynı dosyalar kullanılabilir:

```bash
docker run --rm \
  -v "$PWD":/app:ro \
  -w /app \
  python:3.12-slim \
  python day08.py
```

---

# 🆚 Bind, Volume ve Tmpfs

## Bind mount

```bash
--mount type=bind,source="$PWD",target=/app
```

Hosttaki belirli bir dosya veya klasörü bağlar.

Kullanım:

- Kod geliştirme
    
- Host dosyalarını container içinde kullanma
    
- Yapılandırma dosyaları
    

## Volume

```bash
--mount type=volume,source=uygulama_verisi,target=/data
```

Docker tarafından yönetilen kalıcı depolamadır.

Kullanım:

- Veritabanı verileri
    
- Kalıcı uygulama dosyaları
    
- Host path’inden bağımsız depolama
    

## Tmpfs

```bash
--mount type=tmpfs,target=/tmp/veri
```

RAM üzerinde geçici alan oluşturur.

Container durduğunda veri kaybolur.

```text
Host dosyası kullanılacak → bind
Docker kalıcı veri yönetsin → volume
Geçici ve RAM tabanlı veri → tmpfs
```

---

# 🔗 Host ve Container Entegrasyonu

## Host çalıştırması

```bash
python3 day08.py
echo $?
```

Sonuç:

```text
Program çıktısı üretildi.
Exit code 0.
```

## Docker çalıştırması

```bash
docker run --rm \
  -v "$PWD":/app:ro \
  -w /app \
  python:3.12-slim \
  python day08.py

echo $?
```

Sonuç:

```text
Program aynı veri dosyalarını işledi.
Exit code 0.
```

Set çıktıları farklı sırada görünebilir:

```text
Host      → {'db', 'worker', 'api'}
Container → {'worker', 'api', 'db'}
```

Bunlar aynı set olabilir.

Deterministik çıktı:

```python
print("Fail servisler:", sorted(fail_servisler))
```

---

# 🧯 Hata Avı

## 1. Veri fonksiyonunun `sys.exit()` kullanması

TIRT.

Fonksiyonu process yönetimine bağlar ve test edilmesini zorlaştırır.

## 2. `sys.exit(0)` değerini sabit yazmak

TIRT.

Programın gerçek başarısızlık durumlarını gizleyebilir.

## 3. `main()` döndürürse shell otomatik görür

TIRT.

```python
sys.exit(main())
```

ile process seviyesine taşınmalıdır.

## 4. Dizindeki `x` çalıştırma iznidir

TIRT.

Dizinde `x`, geçiş ve içindeki isimlere erişim iznidir.

## 5. `777` en iyi izindir

TIRT.

Gereksiz geniş yetki verir. En az yetki ilkesi uygulanmalıdır.

## 6. Group veya others izni varsa owner da kullanabilir

TIRT.

Dosyanın sahibiysen owner sınıfı seçilir; izin yoksa diğer sınıflara düşülmez.

## 7. Python dosyası `x` olmadan hiçbir şekilde çalışmaz

TIRT.

```bash
python3 script.py
```

kullanımında script için temel olarak okuma izni yeterlidir.

## 8. `python sh` container içinde shell açar

TIRT.

Python, `sh` isimli bir script dosyası açmaya çalışır.

## 9. Bind mount container’da kopya oluşturur

TIRT.

Hosttaki gerçek dosyayı container içinde görünür yapar.

## 10. Container’da dosya silmek yalnız container’ı etkiler

TIRT.

Yazılabilir bind mount kullanılıyorsa host dosyası da silinir.

## 11. Host ve container çıktısı `-it` yüzünden aynıdır

TIRT.

Dosya bağlantısını bind mount sağlar. `-it`, yalnızca etkileşimli terminal sağlar.

---

# 🧠 Kafaya Kazı

> [!quote]  
> İç fonksiyon işi yapar, `main()` karar verir, `sys.exit()` kararı işletim sistemine bildirir.

> [!quote]  
> `return`, fonksiyondan; `sys.exit()`, process’ten çıkar.

> [!quote]  
> Veri işleme fonksiyonunun `print()` ve `sys.exit()` kullanmaması testi kolaylaştırır.

> [!quote]  
> Dosyada `x` çalıştırma, dizinde `x` geçiş iznidir.

> [!quote]  
> `r = 4`, `w = 2`, `x = 1`.

> [!quote]  
> Owner izinleri yetersizse sistem group veya others izinlerine geçmez.

> [!quote]  
> `./script.py` için `x`, `python3 script.py` için temel olarak `r` gerekir.

> [!quote]  
> Dosya silme yetkisi büyük ölçüde dizinin `w+x` izinlerine bağlıdır.

> [!quote]  
> Bind mount dosyayı kopyalamaz, hosttaki gerçek dosyayı bağlar.

> [!quote]  
> Yazılabilir bind mount üzerinden silinen dosya hosttan da silinebilir.

> [!quote]  
> Host dosyalarını korumak için mount’u `readonly` bağla.

> [!quote]  
> `-it` etkileşim sağlar; dosya senkronizasyonunu sağlamaz.

---

# 📌 30 Saniyelik Özet

```text
PYTHON
ordered()          → Veriyi işler
main()             → Program kararlarını verir
return 0           → Fonksiyon sonucu
sys.exit(main())   → Process exit code’u
raise              → Hatayı üst katmana taşır

DOSYA İZİNLERİ
r                  → Oku
w                  → Yaz
x                  → Doğrudan çalıştır
755                → rwxr-xr-x
644                → rw-r--r--
000                → Hiç izin yok

DİZİN İZİNLERİ
r                  → İsimleri listele
w                  → Ekle, sil, yeniden adlandır
x                  → Geçiş ve erişim

PYTHON SCRIPT
./script.py        → x + shebang
python3 script.py  → Temel olarak r

DOCKER
bind mount         → Host dosyasını bağlar
readonly / :ro     → Container yazamaz ve silemez
-it                → İnteraktif terminal
sh                 → Shell aç
python sh          → Python, sh dosyasını açmaya çalışır

KRİTİK
Yazılabilir bind mount
→ Container değişikliği hosta yansır
→ Container silmesi host dosyasını silebilir
```

---

# ✅ Günün Kazanımları

-  `main()` fonksiyonunun program yönetimindeki rolü anlaşıldı
    
-  `sys.exit(main())` modeli uygulandı
    
-  Veri işleme ve process yönetimi ayrıldı
    
-  Fonksiyon test edilebilirliği artırıldı
    
-  `return`, `raise` ve `sys.exit()` ayrıldı
    
-  Linux owner, group ve others sınıfları öğrenildi
    
-  Dosya ve dizin izinlerinin anlamları ayrıldı
    
-  Sayısal `chmod` hesapları uygulandı
    
-  `chmod 000`, `077`, `700` ve `777` gözlemlendi
    
-  Owner izinlerinin group/others’a düşmediği anlaşıldı
    
-  Doğrudan script çalıştırma ile yorumlayıcı kullanma ayrıldı
    
-  macOS `@` ve `+` göstergeleri öğrenildi
    
-  Bind mount izinlerinin container’da görülebildiği gözlemlendi
    
-  Host ve container kullanıcı adlarının farklı görünebileceği fark edildi
    
-  `python sh` komut hatası anlaşıldı
    
-  Yazılabilir bind mount üzerinden host dosyasının silinebileceği görüldü
    
-  `readonly` mount’un önemi kavrandı
    
-  `-it` ile bind mount’un farklı görevleri ayrıldı
    
-  Bind, volume ve tmpfs türleri karşılaştırıldı
    

> [!success] 🚀 Gün sonu sonucu  
> Gün 8 sonunda program içi sorumluluklarla işletim sistemi seviyesindeki yetkiler aynı zihinsel modelde birleştirildi.
> 
> Python tarafında veri işleme fonksiyonları process yönetiminden ayrıldı. Linux tarafında dosya ve dizin izinlerinin farklı anlamlara geldiği görüldü. Docker tarafında ise bind mount’un kopyalama değil, host dosyalarına doğrudan erişim sağladığı ve bu erişimin yanlış kullanıldığında host verisini gerçekten değiştirebildiği öğrenildi.