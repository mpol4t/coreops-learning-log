---
title: "Gün 07 — Refaktör, main(), Test Edilebilirlik, CWD ve Docker Teşhisi"
tags:
  - coreops
  - python
  - linux
  - docker
  - refactoring
  - testability
  - cwd
  - bind-mount
aliases:
  - "Gün 7 Refaktör ve Docker Teşhisi"
status: completed
---

# 🧠 Gün 7 — Refaktör, `main()`, Test Edilebilirlik, CWD ve Docker Teşhisi

> [!info] Kaynak  
> Bu not, Gün 7 çalışma ve deney kayıtları temel alınarak düzenlendi.

> [!abstract] 🎯 Ana fikir  
> Sağlam bir programda veri işleme, kullanıcıya çıktı gösterme ve process’i sonlandırma kararları aynı fonksiyona yığılmaz.
> 
> ```text
> Alt katman → Veriyi işler, sonuç döndürür veya exception yükseltir.
> Üst katman → Mesajı doğru kanala yazar ve exit code’a karar verir.
> ```
> 
> Docker tarafında ise:
> 
> ```text
> -v / --mount → Dosyaların container içinde nerede görüneceği
> -w           → Process’in hangi dizinden çalışacağı
> ```
> 
> sorularını cevaplar.

---

# ⚡ 2 Dakikalık Geri Çağırma

## Bir fonksiyon neden `stdout`’a yazmak zorunda değildir?

Çünkü fonksiyonun görevi her zaman kullanıcıya çıktı göstermek değildir.

Fonksiyon yalnızca değer üretebilir:

```python
def topla(a, b):
    return a + b
```

Bu fonksiyon:

- `stdout`’a yazmaz.
    
- `stderr`’a yazmaz.
    
- Yalnızca çağıran tarafa değer döndürür.
    

Çağıran taraf sonucu istediği şekilde kullanabilir:

```python
sonuc = topla(3, 5)

print(sonuc)
```

veya:

```python
assert sonuc == 8
```

veya başka bir hesaba aktarabilir.

> [!important]  
> Bir fonksiyonun çıktı üretmesi ile ekrana yazı yazması aynı şey değildir.
> 
> `return` da bir çıktıdır fakat terminal kanalına yazılmaz.

---

## `raise` ile `sys.exit()` hangi katmanlarda kullanılır?

Mimari olarak önerilen model:

```text
Alt katmanlar → raise
En üst program katmanı → sys.exit()
```

Örnek:

```python
def dosya_oku(path):
    with open(path) as dosya:
        return dosya.read()
```

Dosya bulunamazsa fonksiyon:

```text
FileNotFoundError
```

exception’ını yukarı gönderir.

Üst katman:

```python
def main():
    try:
        icerik = dosya_oku("data.txt")
    except FileNotFoundError as hata:
        print(hata, file=sys.stderr)
        return 2

    print(icerik)
    return 0
```

Son olarak:

```python
sys.exit(main())
```

kullanılır.

> [!warning]  
> Bu, Python dilinin zorunlu kuralı değildir.
> 
> `raise` herhangi bir katmanda kullanılabilir. Buradaki ayrım, daha temiz ve sürdürülebilir bir mimari tercihidir.

---

## Test yazmayı hangi tasarım kolaylaştırır?

Şu tür fonksiyonlar:

```text
Girdi → İşlem → Return değeri
```

daha kolay test edilir.

Örnek:

```python
sonuc = ordered("services.txt")

assert sonuc[0] == ["api", "db"]
```

Fonksiyon:

- `print()` yapmıyorsa,
    
- `sys.exit()` çağırmıyorsa,
    
- Sonucu açıkça döndürüyorsa,
    

test sırasında program kapanmaz ve terminal çıktısı yakalamak zorunda kalınmaz.

---

# ♻️ Refaktör Nedir?

Refaktör:

> Programın dışarıdan gözlenen davranışını değiştirmeden kodun iç tasarımını iyileştirmektir.

Refaktör sırasında amaç yeni özellik eklemek değil:

- Sorumlulukları ayırmak
    
- Okunabilirliği artırmak
    
- Tekrarı azaltmak
    
- Test yazmayı kolaylaştırmak
    
- Kodun tekrar kullanılabilirliğini artırmak
    

olmalıdır.

---

# ❌ Refaktör Öncesi Sorun

Tek fonksiyonun şunların hepsini yaptığını düşün:

```text
Dosyayı açıyor
Veriyi ayrıştırıyor
Liste oluşturuyor
Dictionary oluşturuyor
Set oluşturuyor
Hata mesajı yazıyor
Programı sys.exit() ile kapatıyor
```

Bu fonksiyon çok fazla sorumluluk taşır.

Örneğin test sırasında dosya bulunamazsa:

```python
sys.exit(21)
```

çalışır ve bütün test process’i kapanabilir.

Fonksiyonu başka bir program içinde kullanmak isteyen çağıran tarafın:

```text
Hatayı farklı şekilde yönetme
Başka bir dosyayı deneme
Kullanıcıya farklı mesaj gösterme
Log yazma
```

şansı azalır.

---

# ✅ Refaktör Sonrası Sorumluluklar

## `ordered()`

Yalnızca:

- Dosyayı açar.
    
- Satırları ayrıştırır.
    
- Veriyi işler.
    
- Sonuçları `return` eder.
    

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

## `main()`

- Fonksiyonu çağırır.
    
- Kullanılacak dosyalara karar verir.
    
- Exception’ları yakalar.
    
- Kullanıcıya çıktı gösterir.
    
- Process exit code’unu belirler.
    

---

# 🧱 Daha Temiz Program Yapısı

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

# 🚨 Mevcut Koddaki Sinsi Eksik

Kaynak koddaki yapı:

```python
if __name__ == "__main__":
    main()
```

çalışır.

Ancak `main()` yalnızca çağrılırsa döndürdüğü exit code process seviyesine otomatik taşınmaz.

Daha sağlam kullanım:

```python
if __name__ == "__main__":
    sys.exit(main())
```

Böylece:

```python
return 0
```

process exit code `0` olur.

```python
return 21
```

process exit code `21` olur.

> [!danger] Kafaya kazı
> 
> ```text
> main() içindeki return
> → Fonksiyon dönüş değeridir.
> 
> sys.exit(main())
> → Bu değeri process exit code’una dönüştürür.
> ```

---

# 🧪 Test Edilebilirlik Neden Arttı?

## Önceki yapı

Fonksiyon çağrıldığında:

- Terminale çıktı yazabiliyordu.
    
- Hata mesajı yazabiliyordu.
    
- Programı kapatabiliyordu.
    

Test şunlarla uğraşmak zorundaydı:

- `stdout` yakalama
    
- `stderr` yakalama
    
- `SystemExit` yakalama
    

## Refaktör sonrası

Fonksiyonun dönüşü doğrudan incelenebilir:

```python
sıralı, son_durum, fail_olanlar = ordered("services.txt")

assert sıralı == ["api", "db", "cache", "worker"]

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

Set sırası garanti edilmediği için set testi:

```python
assert fail_olanlar == {"api", "db", "worker"}
```

şeklinde mantıksal eşitlikle yapılmalıdır.

Şu kullanım TIRT:

```python
assert str(fail_olanlar) == "{'api', 'db', 'worker'}"
```

Çünkü string sırası değişebilir.

---

# 🧼 Daha İleri Test Edilebilirlik

`ordered()` artık `print()` ve `sys.exit()` kullanmıyor; bu ciddi bir gelişmedir.

Ancak hâlâ doğrudan dosya açtığı için tamamen saf bir fonksiyon değildir.

Bir adım daha ileri gidilirse dosya okuma ile veri işleme ayrılabilir:

```python
def parse_records(satırlar):
    sıralı_servisler = []
    son_durum = {}
    fail_servisler = set()

    for satır in satırlar:
        servis, durum = satır.strip().split(",")

        if servis not in sıralı_servisler:
            sıralı_servisler.append(servis)

        son_durum[servis] = durum

        if durum == "fail":
            fail_servisler.add(servis)

    return sıralı_servisler, son_durum, fail_servisler


def ordered(dosya):
    with open(dosya) as file:
        return parse_records(file)
```

Artık veri işleme testi için gerçek dosya bile gerekmez:

```python
satırlar = [
    "api,ok\n",
    "db,fail\n",
    "api,fail\n",
]

sonuc = parse_records(satırlar)
```

> [!success] Ek güçlendirme  
> Dosya açma ile veri işleme ayrıldığında:
> 
> - Test daha hızlı olur.
>     
> - Test için disk dosyası hazırlamak gerekmez.
>     
> - Ayrıştırma mantığı farklı veri kaynaklarıyla kullanılabilir.
>     

---

# 🔁 Aynı Fonksiyonu Farklı Girdilerle Çağırmak

Görev:

```text
“Aynı fonksiyonu en az iki farklı girişle çağır.”
```

dediğinde fonksiyona yeni parametre eklemek gerekmez.

Fonksiyon zaten bir dosya parametresi alır:

```python
ordered("services.txt")
ordered("services2.txt")
```

Tekrarlı kodu azaltmak için:

```python
for dosya in ["services.txt", "services2.txt"]:
    ordered(dosya)
```

kullanılabilir.

---

# 🔄 `for` Döngüsü Nasıl Çalışır?

```python
for sayi in [10, 20, 30]:
    print(sayi)
```

mantıksal olarak:

```python
sayi = 10
print(sayi)

sayi = 20
print(sayi)

sayi = 30
print(sayi)
```

gibi düşünülebilir.

Dosya örneği:

```python
for dosya in ["services.txt", "services2.txt"]:
    ordered(dosya)
```

## Birinci tur

```python
dosya = "services.txt"
ordered(dosya)
```

## İkinci tur

```python
dosya = "services2.txt"
ordered(dosya)
```

Fonksiyon iki kez çağrılır.

---

## Döngü değişkeni yeniden atanır

```python
sonuc = ordered(dosya)
```

ilk turda bir değer alır.

İkinci turda aynı değişken yeni sonuçla değiştirilir.

Eski sonuç otomatik saklanmaz.

Bütün sonuçlar saklanacaksa:

```python
sonuclar = []

for dosya in ["services.txt", "services2.txt"]:
    sonuclar.append(ordered(dosya))
```

kullanılabilir.

---

# ⚠️ `try` Bloğunun Kapsamı

Kaynak koddaki yapı:

```python
try:
    for dosya in ["services.txt", "services2.txt"]:
        ordered(dosya)
except FileNotFoundError:
    ...
```

şu davranışı oluşturur:

```text
services.txt başarılı
services2.txt bulunamadı
        ↓
except çalışır
        ↓
döngü tamamen sona erer
```

Bu davranış şartnameye göre doğru olabilir.

Ancak amaç bir dosya hata verse bile diğerlerini işlemeye devam etmekse `try` döngünün içine alınmalıdır:

```python
for dosya in ["services.txt", "services2.txt"]:
    try:
        sonuc = ordered(dosya)
    except FileNotFoundError as hata:
        print(hata, file=sys.stderr)
        continue
```

> [!important]  
> `try` bloğunun konumu yalnız görünümü değil, programın hata sonrası devam edip etmeyeceğini de belirler.

---

# 🛡️ `if __name__ == "__main__":`

```python
if __name__ == "__main__":
    sys.exit(main())
```

şu ayrımı sağlar:

## Dosya doğrudan çalıştırılırsa

```bash
python3 day07.py
```

Python:

```python
__name__ == "__main__"
```

olduğu için `main()` çalışır.

## Dosya import edilirse

```python
import day07
```

Python:

```python
__name__ == "day07"
```

olduğu için `main()` otomatik çalışmaz.

Böylece:

```python
day07.ordered("services.txt")
```

başka koddan güvenli şekilde çağrılabilir.

---

# 🐧 Linux — CWD ve Script Konumu

## `pwd`

```bash
pwd
```

şu anda bulunduğun çalışma dizinini gösterir.

Açılımı:

```text
Print Working Directory
```

Örnek:

```text
/Users/polat/CODING/Gelişim/Gelişmiş
```

---

## Script’in dizini ile CWD aynı mıdır?

Her zaman değil.

Örneğin terminal CWD’si:

```text
/Users/polat/CODING/Gelişim
```

script ise:

```text
/Users/polat/CODING/Gelişim/Gelişmiş/day07.py
```

konumunda olabilir.

Şu komut script’i başlatabilir:

```bash
python3 "Gelişmiş/day07.py"
```

Ancak process’in CWD’si hâlâ:

```text
/Users/polat/CODING/Gelişim
```

olur.

---

# 📍 Göreli Path Neden CWD’ye Göre Çözülür?

```python
ordered("services.txt")
```

içindeki:

```text
services.txt
```

eksik bir adrestir.

Başlangıç noktası yazılmamıştır.

Python bunu CWD ile birleştirir:

```text
CWD + services.txt
```

Örneğin CWD:

```text
/Users/polat/CODING/Gelişim
```

ise Python şurada arar:

```text
/Users/polat/CODING/Gelişim/services.txt
```

Script’in bulunduğu klasörde otomatik olarak aramaz.

---

# 🧪 Üç Farklı Host Deneyi

## 1. Doğru dizinden çalıştırmak

```bash
cd "/Users/polat/CODING/Gelişim/Gelişmiş"
python3 day07.py
```

Burada:

```text
Script → CWD/day07.py
Dosyalar → CWD/services.txt ve CWD/services2.txt
```

bulunur.

Sonuç:

```text
Exit code 0
```

---

## 2. Üst dizinden yalnız dosya adını kullanmak

```bash
cd "/Users/polat/CODING/Gelişim"
python3 day07.py
```

Python şurada script arar:

```text
/Users/polat/CODING/Gelişim/day07.py
```

Script burada olmadığı için Python yorumlayıcısı:

```text
can't open file
```

hatası verir.

Sonuç:

```text
Exit code 2
```

Burada `day07.py` hiç çalışmamıştır.

---

## 3. Üst dizinden script path’ini vermek

```bash
python3 "Gelişmiş/day07.py"
```

Script bulunur ve çalışmaya başlar.

Ancak CWD üst dizin olduğu için:

```python
ordered("services.txt")
```

şurada arama yapar:

```text
/Users/polat/CODING/Gelişim/services.txt
```

Dosya burada bulunmadığı için uygulamanın kendi hata yönetimi çalışır:

```text
Exit code 21
```

> [!danger] Kritik ayrım
> 
> ```text
> Exit code 2
> → Python script’i başlatamadı.
> 
> Exit code 21
> → Script başladı, ancak uygulama services.txt dosyasını bulamadı.
> ```

---

# 🔍 CWD Sorununu Doğrulamak İçin İlk Üç Komut

Teşhis için doğrudan programı rastgele çalıştırmak yerine önce ortamı gör:

```bash
pwd
```

```bash
ls -la
```

```bash
python3 -c '
import os

print("CWD:", os.getcwd())
print("services.txt:", os.path.abspath("services.txt"))
print("services2.txt:", os.path.abspath("services2.txt"))
'
```

Bu üç adım şunları gösterir:

1. Hangi dizindeyim?
    
2. Bu dizinde hangi dosyalar var?
    
3. Python göreli dosya adlarını hangi mutlak path’lere çözüyor?
    

Ardından:

```bash
python3 "Gelişmiş/day07.py"
```

çalıştırılarak tahmin doğrulanabilir.

> [!warning]  
> Yalnızca:
> 
> ```bash
> python day07.py
> ```
> 
> çalıştırmak CWD problemini teşhis etmez; script dosyasının kendisi de bulunamıyor olabilir.

---

# 🐳 Docker — Mount ve Çalışma Dizini

Docker’da iki farklı soru bulunur:

## Mount

```text
Dosyalar container içinde nerede görünecek?
```

## Workdir

```text
Process hangi dizinden çalışacak?
```

Bunlar aynı şey değildir.

---

# 📦 `-v` Ne Yapar?

```bash
-v "$PWD":/app:ro
```

Parçaları:

```text
"$PWD" → Hosttaki mevcut klasör
/app   → Container içindeki hedef
:ro    → Salt okunur
```

Host:

```text
$PWD/day07.py
$PWD/services.txt
$PWD/services2.txt
```

Container:

```text
/app/day07.py
/app/services.txt
/app/services2.txt
```

olarak görünür.

`-v`:

- Dosyaları image’a kopyalamaz.
    
- Host dosyalarını container içinde görünür hâle getirir.
    
- Çalışma dizinini değiştirmez.
    

---

# 📍 `-w` Ne Yapar?

```bash
-w /app
```

Container process’inin çalışma dizinini `/app` yapar.

Bu nedenle:

```bash
python day07.py
```

şuna çözülür:

```text
/app/day07.py
```

Kod içindeki:

```python
ordered("services.txt")
```

ise:

```text
/app/services.txt
```

yoluna çözülür.

---

# ✅ Başarılı Docker Komutu

```bash
docker run --rm \
  -v "$PWD":/app:ro \
  -w /app \
  python:3.12-slim \
  python day07.py \
  > başarılı.txt \
  2> başarısız.txt
```

Akış:

```text
Host klasörü /app içine mount edilir.
        ↓
Container CWD’si /app yapılır.
        ↓
python day07.py → /app/day07.py
        ↓
services.txt → /app/services.txt
        ↓
services2.txt → /app/services2.txt
```

Sonuç:

```text
başarılı.txt → Program sonuçları
başarısız.txt → Boş
exit code → 0
```

---

# ❌ Mount Doğru, `-w` Yanlış

```bash
docker run --rm \
  -v "$PWD":/app:ro \
  -w /tmp \
  python:3.12-slim \
  python day07.py
```

Dosyalar container içinde:

```text
/app/day07.py
/app/services.txt
```

konumundadır.

Ancak CWD:

```text
/tmp
```

olduğu için Python şurada arar:

```text
/tmp/day07.py
```

Sonuç:

```text
python: can't open file '/tmp/day07.py'
exit code 2
```

Python script’i başlamamıştır.

---

## Script mutlak yolla verilirse ne olur?

```bash
python /app/day07.py
```

script başlatılabilir.

Ancak CWD hâlâ `/tmp` olduğu için kod içindeki:

```python
ordered("services.txt")
```

şurada arar:

```text
/tmp/services.txt
```

Dolayısıyla bu kez script çalışır fakat uygulama dosyayı bulamayabilir.

> [!important]  
> Script path’ini düzeltmek, kod içindeki göreli path’lerin başlangıç noktasını değiştirmez.

---

# ❌ Mount Kaynağı Geçersiz

```bash
docker run --rm \
  --mount type=bind,source="$PWD/olmayanklasör",target=/app,readonly \
  -w /app \
  python:3.12-slim \
  python day07.py
```

Host source bulunmadığı için mount kurulamaz.

Akış:

```text
Docker source path’i kontrol eder.
        ↓
Source bulunamaz.
        ↓
Mount kurulamaz.
        ↓
Container process’i başlamaz.
        ↓
Python hiç çalışmaz.
```

Sonuç:

```text
Docker hata mesajı
Exit code 125
```

---

# 🚨 Satır Devamı Uyarısı

Shell satır devamında:

```bash
\
```

karakterinden sonra boşluk bulunmamalıdır.

Doğru:

```bash
--mount type=bind,source="$PWD",target=/app,readonly \
-w /app
```

TIRT:

```bash
--mount type=bind,source="$PWD",target=/app,readonly \ 
-w /app
```

İkinci kullanımda `\` newline karakterini kaçırmak yerine boşluğu kaçırabilir ve komut beklenmedik şekilde parçalanabilir.

---

# 🆚 Yanlış Mount ve Geçersiz Mount

## Yanlış ama mevcut kaynak

```bash
-v "/başka/mevcut/klasör":/app
```

Docker mount’u başarıyla kurabilir.

Ancak `/app` içinde yanlış dosyalar görünür.

Daha sonra Python:

```text
day07.py bulunamadı
```

hatası verebilir.

## Geçersiz kaynak

```bash
--mount type=bind,source="/olmayan/yol",target=/app
```

Mount hiç kurulamaz.

Container process’i başlamaz.

Genellikle:

```text
Exit code 125
```

oluşur.

> [!danger] Kafaya kazı  
> Yanlış içeriği başarıyla mount etmek ile mount’u hiç kuramamak aynı hata değildir.

---

# 🧪 Mount ve Workdir İçin En Küçük Ayırıcı Testler

## 1. Host dosyaları gerçekten var mı?

```bash
pwd
ls -la
```

## 2. Mount doğru mu?

```bash
docker run --rm \
  -v "$PWD":/app:ro \
  python:3.12-slim \
  ls -la /app
```

Bu komut yalnızca `/app` içeriğini kontrol eder.

## 3. Workdir doğru mu?

```bash
docker run --rm \
  -v "$PWD":/app:ro \
  -w /app \
  python:3.12-slim \
  pwd
```

Beklenen:

```text
/app
```

## 4. İkisini birlikte incele

```bash
docker run --rm \
  -v "$PWD":/app:ro \
  -w /app \
  python:3.12-slim \
  sh -c 'pwd && ls -la'
```

Beklenen:

```text
/app
day07.py
services.txt
services2.txt
```

---

# 🧭 Python Dosyası Bulunamadığında Teşhis Sırası

```text
1. Hostta doğru dizinde miyim?
2. Script ve veri dosyaları hostta gerçekten var mı?
3. Doğru host dizini mount edilmiş mi?
4. Mount doğru container hedefine bağlanmış mı?
5. Container’ın CWD’si neresi?
6. Python komutunda göreli mi mutlak mı script path’i kullanılıyor?
7. Kod içindeki göreli veri path’i hangi mutlak yola çözülüyor?
8. Hata Docker’dan mı Python’dan mı geliyor?
9. Exit code kaç?
```

> [!danger]  
> Dosya bulunamadığında doğrudan Python kodunu değiştirmeye başlamak TIRT teşhistir.
> 
> Önce hangi katmanda yanlış adres kullanıldığını belirle.

---

# 🔗 Entegrasyon Sonuçları

|Çalıştırma|Sonuç|Exit code|Sebep|
|---|--:|--:|---|
|`python3 day07.py` doğru klasörde|Başarılı|`0`|Script ve veri dosyaları CWD’de|
|Docker, doğru mount + doğru `-w`|Başarılı|`0`|Dosyalar `/app`, CWD `/app`|
|Üst dizinden `python3 day07.py`|Başarısız|`2`|Script CWD’de bulunamadı|
|Üst dizinden script path’iyle|Başarısız|`21`|Script başladı, `services.txt` CWD’de yok|
|Doğru mount + `-w /tmp`|Başarısız|`2`|`/tmp/day07.py` bulunamadı|
|Olmayan bind source|Başarısız|`125`|Docker container’ı hazırlayamadı|

---

# 🧯 Hata Avı

## 1. Fonksiyonun her zaman ekrana yazması gerekir

TIRT.

Fonksiyon yalnızca değer döndürebilir.

## 2. Fonksiyon içinde `sys.exit()` test yazmayı kolaylaştırır

TIRT.

Programın tamamını kapatma kararı alt fonksiyonu gereksiz şekilde üst katmana bağlar.

## 3. `main()` dönüşü otomatik exit code olur

TIRT.

```python
sys.exit(main())
```

ile process seviyesine taşınmalıdır.

## 4. `raise` yalnızca alt katmanda kullanılabilir

TIRT.

Bu bir dil kısıtı değil, temiz mimari tercihidir.

## 5. `python "Gelişmiş/day07.py"` kullanınca CWD script klasörü olur

TIRT.

CWD, komutu başlattığın terminal dizini olarak kalır.

## 6. Mount doğruysa `-w` önemsizdir

TIRT.

Göreli script ve veri path’leri `-w` ile belirlenen CWD’ye göre çözülür.

## 7. `-w /app` dosyaları `/app` içine getirir

TIRT.

Dosyaları mount getirir; `-w` yalnızca çalışma dizinini seçer.

## 8. Exit code `125` Python hatasıdır

TIRT.

Bu deneyde Python hiç başlamamıştır. Hata Docker/runtime katmanındadır.

## 9. Set çıktıları farklı sıradaysa sonuçlar farklıdır

TIRT.

Set sırası garanti edilmez. Mantıksal eşitlik veya `sorted()` kullanılmalıdır.

---

# 🧠 Kafaya Kazı

> [!quote]  
> Fonksiyonun terminale yazması şart değildir; değer döndürmesi yeterli olabilir.

> [!quote]  
> Alt katman hatayı yükseltir, üst katman kullanıcıya gösterir ve exit code’a karar verir.

> [!quote]  
> Refaktör, davranışı değil tasarımı iyileştirir.

> [!quote]  
> `ordered()` veriyi işler; `main()` program akışını yönetir.

> [!quote]  
> `sys.exit(main())`, `main()` dönüşünü process exit code’una taşır.

> [!quote]  
> `for`, aynı kodu farklı girdiler üzerinde tekrar çalıştırır.

> [!quote]  
> Script konumu ile CWD aynı şey değildir.

> [!quote]  
> Göreli path CWD’ye göre çözülür.

> [!quote]  
> `-v` dosyaları görünür yapar, `-w` çalışma dizinini belirler.

> [!quote]  
> Mount doğru olsa bile workdir yanlışsa göreli path bozulabilir.

> [!quote]  
> Exit code `2`, Python’ın script’i başlatamadığını gösterebilir.

> [!quote]  
> Exit code `21`, uygulamanın kendi dosya bulunamadı sözleşmesidir.

> [!quote]  
> Exit code `125`, Docker’ın container process’ini başlatamadığını gösterir.

---

# 📌 30 Saniyelik Özet

```text
REFAKTÖR
ordered()       → Veriyi işle, return et
main()          → Hataları yakala, çıktı yaz, kod döndür
sys.exit(main())→ Return değerini process exit code yap

TEST
print() az      → Çıktı yakalama ihtiyacı azalır
sys.exit() dışarı → Test process’i kapanmaz
return          → Doğrudan assert edilebilir
raise           → Çağıran taraf yönetebilir

FOR
Her turda yeni girdi
Aynı değişken yeniden atanır
Eski sonuç saklanacaksa koleksiyona eklenir

LINUX
pwd             → CWD
Script path’i   → Script’in konumu
CWD             → Göreli path başlangıcı
Script konumu ≠ CWD

DOCKER
-v / --mount    → Dosyalar nerede görünür?
-w              → Process nereden çalışır?
2               → Python script’i bulamadı
21              → Uygulama veri dosyasını bulamadı
125             → Docker container’ı başlatamadı
```

---

# ✅ Günün Kazanımları

-  Fonksiyonların `stdout`’a yazmak zorunda olmadığı anlaşıldı
    
-  `raise` ve `sys.exit()` sorumlulukları ayrıldı
    
-  Refaktör kavramı uygulandı
    
-  Veri işleme ve kullanıcı etkileşimi ayrıldı
    
-  `ordered()` fonksiyonundan `print()` ve `sys.exit()` çıkarıldı
    
-  `main()` program akışının sahibi yapıldı
    
-  `sys.exit(main())` modeli öğrenildi
    
-  Fonksiyon dönüşleri doğrudan test edilebilir hâle getirildi
    
-  Aynı fonksiyon iki farklı dosyayla çağrıldı
    
-  `for` döngüsündeki yeniden atama mantığı anlaşıldı
    
-  `try` bloğunun konumunun program akışını değiştirdiği görüldü
    
-  Script konumu ile CWD ayrıldı
    
-  Göreli path’in CWD’ye göre çözüldüğü doğrulandı
    
-  Hostta exit code `2` ile uygulama kodu `21` ayrıldı
    
-  Docker mount ile workdir ayrıldı
    
-  Doğru mount + yanlış workdir denendi
    
-  Geçersiz bind source ile Docker `125` hatası üretildi
    
-  Python’ın hiç başlamadığı hata katmanı tespit edildi
    
-  Mount ve CWD için küçük ayırıcı testler oluşturuldu
    

> [!success] 🚀 Gün sonu sonucu  
> Gün 7 sonunda çalışan kod yalnızca parçalara bölünmedi; sorumluluk sınırları netleştirildi.
> 
> Veri işleme fonksiyonu sonuç üretmeye, `main()` program akışını yönetmeye başladı. Aynı zamanda host ve container ortamlarında dosyanın bulunmasının yalnızca kodla değil; CWD, mount target’ı, çalışma dizini ve kullanılan path türüyle belirlendiği kavrandı.