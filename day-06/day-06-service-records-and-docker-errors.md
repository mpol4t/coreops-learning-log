---
title: "Gün 06 — Dosyadan Veri İşleme, Koleksiyonlar ve Docker Hata Katmanları"
tags:
  - coreops
  - python
  - linux
  - docker
  - collections
  - file-io
  - exit-code
  - bind-mount
aliases:
  - "Gün 6 Servis Kayıtları ve Hata Katmanları"
status: completed
duration: "100-110 dakika"
---

# 🧠 Gün 6 — Dosyadan Veri İşleme, Koleksiyonlar ve Docker Hata Katmanları

> [!info] Kaynak  
> Bu not, Gün 6 çalışma ve test kayıtları temel alınarak düzenlendi.

> [!abstract] 🎯 Ana fikir  
> Aynı ham veri üzerinde farklı bilgileri korumak istiyorsam tek bir veri yapısını her işe zorlamam.
> 
> Bu görevde:
> 
> - İlk görülme sırası → `list`
>     
> - Her servisin son durumu → `dict`
>     
> - Geçmişte en az bir kez başarısız olanlar → `set`
>     
> 
> kullanıldı.
> 
> Programın ürettiği normal sonuçlar `stdout`’a, hata açıklamaları `stderr`’a gönderildi. Programın başarı veya başarısızlığı ise **exit code** ile bildirildi.

---

# ⚡ 2 Dakikalık Geri Çağırma

## `return` ile `sys.exit()` farkı

```text
return
→ Fonksiyondan değer döndürür.
→ Yalnızca ilgili fonksiyonu bitirir.

sys.exit()
→ Process’i sonlandırma isteği oluşturur.
→ Belirtilen değeri process exit code’u yapar.
```

## `abspath()` ne yapar?

```python
os.path.abspath("services.txt")
```

Göreli path’i mevcut çalışma dizinine göre mutlaklaştırır.

Dosyanın gerçekten var olduğunu kanıtlamaz.

## `stderr`’da mesaj bulunması başarısızlığı kanıtlar mı?

Hayır.

Program:

```text
stderr’a mesaj yazıp exit code 0 döndürebilir.
```

Bu nedenle otomasyon için asıl kontrol:

```bash
echo $?
```

ile görülen **exit code**’dur.

---

# 🧩 Neden Tek Koleksiyon Yetmedi?

Aynı servis kayıtlarından üç farklı bilgi üretilmek istendi:

```text
api,ok
db,fail
api,fail
db,ok
worker,fail
```

Bu veriden üç ayrı soru soruluyor:

1. Servisler ilk kez hangi sırayla görüldü?
    
2. Her servisin en son durumu nedir?
    
3. Hangi servisler geçmişte en az bir kere `fail` oldu?
    

Bu üç sorunun istediği özellikler farklıdır.

|İstenen bilgi|Veri yapısı|Korunan özellik|
|---|---|---|
|İlk görülme sırası|`list`|Sıra|
|Son durum eşlemesi|`dict`|Anahtar-değer ilişkisi|
|Daha önce fail olanlar|`set`|Benzersizlik|

> [!danger] TIRT düşünce  
> “Veri aynıysa tek koleksiyonda tutulmalıdır.”
> 
> Yanlış.
> 
> Önemli olan ham verinin aynı olması değil, o veriden hangi bilgiyi çıkarmak istediğimdir.

---

# 🐍 Python — Dosyadan Servis Kayıtlarını Okuma

## Dosya yolu parametresi

```python
def servisleri_analiz_et(path):
    ...
```

Buradaki `path`, dosyanın kendisi değildir.

Dosyanın konumunu taşıyan parametredir.

```python
servisleri_analiz_et("services.txt")
```

çağrıldığında:

```text
path = "services.txt"
```

olur.

Fonksiyon içinde sabit dosya adı kullanılırsa parametre anlamsızlaşır.

TIRT:

```python
def servisleri_analiz_et(path):
    open("services.txt")
```

Doğru:

```python
def servisleri_analiz_et(path):
    open(path)
```

---

# 📖 Dosyadan Gelen Satırın Gerçek Tipi

Kod içinde hazırlanmış kayıt:

```python
("api", "ok")
```

bir tuple’dır.

Bu yüzden doğrudan unpack edilebilir:

```python
servis, durum = ("api", "ok")
```

Ancak dosyadan okunan satır:

```python
"api,ok\n"
```

şeklinde tek bir `str` değeridir.

Dolayısıyla:

```python
servis, durum = satır
```

yazmak TIRT.

Python string’i iki kelimeye değil, karakterlere ayırmaya çalışır.

---

# ✂️ `strip()` ve `split(",")`

Dosyadaki satır:

```text
api,fail
```

Python tarafından genellikle:

```python
"api,fail\n"
```

şeklinde okunur.

## Yalnızca `split(",")`

```python
satır.split(",")
```

sonucu:

```python
["api", "fail\n"]
```

olabilir.

Bu durumda:

```python
durum == "fail"
```

kontrolü:

```python
"fail\n" == "fail"
```

olduğu için `False` döner.

## Doğru akış

```python
servis, durum = satır.strip().split(",")
```

Adımlar:

```text
"api,fail\n"
      ↓ strip()
"api,fail"
      ↓ split(",")
["api", "fail"]
      ↓ unpacking
servis = "api"
durum = "fail"
```

---

## `strip()` ne temizler?

String’in başında ve sonunda bulunan:

- Boşlukları
    
- `\n` satır sonunu
    
- `\t` tab karakterini
    
- Benzer whitespace karakterlerini
    

temizler.

String’in ortasındaki karakterleri silmez.

```python
" api,fail \n".strip()
```

sonucu:

```python
"api,fail"
```

olur.

---

## `split(",")` ne yapar?

String’i virgüllerin bulunduğu noktalardan böler.

```python
"api,fail".split(",")
```

sonucu:

```python
["api", "fail"]
```

olur.

Dosya formatı şu olsaydı:

```text
api fail
```

boşluk üzerinden ayırmak için:

```python
split()
```

kullanılabilirdi.

Ancak format:

```text
api,fail
```

olduğu için ayırıcı açıkça verilmelidir:

```python
split(",")
```

---

# 📋 `ORDER` — İlk Görülme Sırası

```python
sıralı_servisler = []
```

Her servis yalnızca ilk kez görüldüğünde listeye eklenir:

```python
if servis not in sıralı_servisler:
    sıralı_servisler.append(servis)
```

Kayıt sırası:

```text
api
db
api
cache
db
worker
```

Sonuç:

```python
["api", "db", "cache", "worker"]
```

İkinci `api` ve `db` yeniden eklenmez.

Liste:

- İlk görülme sırasını korur.
    
- İndeksle erişim sağlar.
    
- `append()` ile sona eleman ekler.
    

---

# 🗂️ `LATEST` — Servislerin Son Durumu

```python
son_durum = {}
```

Her yeni kayıt geldiğinde:

```python
son_durum[servis] = durum
```

çalıştırılır.

Dictionary mantığı:

```text
Anahtar yoksa → Yeni kayıt eklenir.
Anahtar varsa → Eski değer güncellenir.
```

Örnek:

```text
api,ok
api,fail
```

İlk kayıt:

```python
{"api": "ok"}
```

İkinci kayıt:

```python
{"api": "fail"}
```

Dictionary geçmişteki bütün durumları tutmaz.

Yalnızca her anahtarın en son değerini tutar.

---

# 🚨 `EVER_FAILED` — En Az Bir Kez Fail Olanlar

```python
fail_servisler = set()
```

O an okunan kaydın durumu `fail` ise:

```python
if durum == "fail":
    fail_servisler.add(servis)
```

kullanılır.

Örnek:

```text
db,fail
db,ok
```

Sonuçlar:

```python
son_durum = {
    "db": "ok"
}
```

```python
fail_servisler = {
    "db"
}
```

Bunlar çelişkili değildir.

```text
son_durum
→ DB’nin en güncel durumu ok.

fail_servisler
→ DB geçmişte en az bir kez fail olmuş.
```

---

## Yanlış değişken kontrolü

TIRT:

```python
if son_durum == "fail":
```

`son_durum` bir dictionary’dir.

`"ok"` veya `"fail"` değerini taşıyan değişken:

```python
durum
```

değişkenidir.

Doğrusu:

```python
if durum == "fail":
```

---

# ➕ `append()`, `add()` ve Dictionary Ataması

|Veri yapısı|Ekleme yöntemi|
|---|---|
|`list`|`append()`|
|`set`|`add()`|
|`dict`|`sozluk[anahtar] = değer`|

## Liste

```python
sıralı_servisler.append(servis)
```

Elemanı listenin sonuna ekler.

## Set

```python
fail_servisler.add(servis)
```

Elemanı kümeye ekler.

Aynı değer tekrar eklenirse ikinci bir kopya oluşmaz.

## Dictionary

```python
son_durum[servis] = durum
```

Anahtar yoksa ekler, varsa değerini günceller.

> [!important] Kafaya kazı
> 
> ```text
> list → append
> set  → add
> dict → [key] = value
> ```

---

# ⚠️ Set Çıktı Sırası

Host çıktısı:

```python
{"api", "db", "worker"}
```

Container çıktısı:

```python
{"worker", "api", "db"}
```

olabilir.

Bu iki set mantıksal olarak aynıdır.

Set sırası garanti edilmediği için yalnız yazdırılma sırasına bakılarak sonuçların farklı olduğu söylenemez.

Deterministik çıktı isteniyorsa:

```python
print("Fail servisler:", sorted(fail_servisler))
```

kullanılabilir.

Bu durumda çıktı liste olarak sıralanır:

```python
["api", "db", "worker"]
```

> [!danger]  
> Aynı setin birkaç çalıştırmada aynı sırada görünmesi, set sırasının garanti edildiğini kanıtlamaz.

---

# 🧱 Fonksiyon Neden Programı Doğrudan Bitirmemeli?

Fonksiyonun temel görevi bir iş yapmak ve sonuç üretmektir.

Fonksiyonun içinde doğrudan:

```python
sys.exit(69)
```

kullanılırsa fonksiyon:

- Başka kodlardan tekrar kullanılamaz hâle gelir.
    
- Test edilmesi zorlaşır.
    
- Çağıran tarafın hatayı farklı şekilde yönetmesini engeller.
    
- Tüm programın kapanmasına karar vermiş olur.
    

Daha temiz sorumluluk ayrımı:

```text
Fonksiyon
→ Veriyi işler.
→ Sonuç veya hata bilgisi üretir.

main()
→ Kullanıcıya mesaj yazar.
→ Process exit code’una karar verir.
```

---

# ✅ Daha Temiz Program Yapısı

```python
import sys


DOSYA_BULUNAMADI = 3
PATH_DIZIN = 4


def servisleri_analiz_et(path):
    sıralı_servisler = []
    son_durum = {}
    fail_servisler = set()

    with open(path) as dosya:
        for satır in dosya:
            servis, durum = satır.strip().split(",")

            if servis not in sıralı_servisler:
                sıralı_servisler.append(servis)

            son_durum[servis] = durum

            if durum == "fail":
                fail_servisler.add(servis)

    return sıralı_servisler, son_durum, fail_servisler


def main():
    try:
        sıralı, son_durum, fail_olanlar = servisleri_analiz_et(
            "services.txt"
        )

    except IsADirectoryError as hata:
        print(
            f"Verilen path bir dosya değil, dizin: {hata}",
            file=sys.stderr,
        )
        return PATH_DIZIN

    except FileNotFoundError as hata:
        print(
            f"Dosya bulunamadı: {hata}",
            file=sys.stderr,
        )
        return DOSYA_BULUNAMADI

    print("Sıralı servisler:", sıralı)
    print("Servislerin son durumu:", son_durum)
    print("Fail servisler:", sorted(fail_olanlar))

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

---

## Bu yapı neden daha temiz?

```text
servisleri_analiz_et()
→ Yalnızca servis verisini işler.

main()
→ Hataları kullanıcıya bildirir.
→ Exit code seçer.

sys.exit(main())
→ main() dönüşünü process exit code’una taşır.
```

Fonksiyon artık başka bir Python modülünden çağrıldığında bütün programı aniden kapatmaz.

---

# 🚨 Exit Code `31` ve `69`

Şunlar teknik olarak çalışır:

```python
sys.exit(31)
sys.exit(69)
```

Fakat bu sayıların ne anlama geldiği açıklanmıyorsa rastgele görünür.

Daha iyi yaklaşım:

```python
FILE_NOT_FOUND = 3
IS_DIRECTORY = 4
```

veya şartname özel olarak `31` ve `69` istiyorsa:

```python
FILE_NOT_FOUND = 69
IS_DIRECTORY = 31
```

şeklinde anlamlı isimlerle belgelemektir.

> [!important]  
> Exit code sayısı ezbere veya komik olduğu için seçilmez.
> 
> Bir sözleşmenin parçası olarak seçilir ve belgelenir.

---

# 🧨 Bozuk Satır Formatı Tuzağı

Şu kod:

```python
servis, durum = satır.strip().split(",")
```

satır tam olarak iki parçaya ayrılmıyorsa:

```text
api
api,fail,extra
```

`ValueError` üretebilir.

Daha kontrollü ayrıştırma:

```python
parçalar = satır.strip().split(",")

if len(parçalar) != 2:
    raise ValueError(
        f"Geçersiz kayıt formatı: {satır!r}"
    )

servis, durum = parçalar
```

Alternatif olarak yalnız ilk virgülde bölmek:

```python
servis, durum = satır.strip().split(",", maxsplit=1)
```

Ancak hangi yaklaşımın doğru olduğu dosya formatı şartnamesine bağlıdır.

---

# 🐧 Linux — `stdout`, `stderr` ve Yönlendirme

Standart file descriptor’lar:

|FD|Kanal|
|--:|---|
|`0`|`stdin`|
|`1`|`stdout`|
|`2`|`stderr`|

## Normal çıktıyı dosyaya yönlendirme

```bash
python3 day06.py > out.txt
```

`>` varsayılan olarak:

```bash
1>
```

anlamına gelir.

## Hata çıktısını yönlendirme

```bash
python3 day06.py 2> err.txt
```

Buradaki `2`, `stderr` file descriptor’ıdır.

## İkisini ayırmak

```bash
python3 day06.py \
  > out.txt \
  2> err.txt
```

Başarılı senaryo:

```text
out.txt → Normal sonuçlar
err.txt → Boş
exit code → 0
```

Hata senaryosu:

```text
out.txt → Boş
err.txt → Hata açıklaması
exit code → Sıfır dışı
```

---

# 🔗 `2>&1`

```bash
python3 day06.py > all.txt 2>&1
```

Anlamı:

```text
Önce stdout → all.txt
Sonra stderr → stdout’un mevcut hedefi
```

Sonuç:

```text
stdout → all.txt
stderr → all.txt
```

`stderr`, stdout verisine dönüşmez.

Yalnızca iki kanalın hedefi aynı olur.

---

# ❗ `$?` Neden Hemen Kontrol Edilir?

```bash
python3 day06.py
echo $?
```

`$?`, yalnızca en son çalışan komutun exit code’unu tutar.

TIRT:

```bash
python3 day06.py
cat err.txt
echo $?
```

Son `echo $?`, Python’ın değil:

```bash
cat err.txt
```

komutunun exit code’unu gösterir.

Daha güvenli yöntem:

```bash
python3 day06.py > out.txt 2> err.txt
kod=$?

cat out.txt
cat err.txt

echo "Python exit code: $kod"
```

---

# ⚠️ Yalnızca `out.txt` ve `err.txt` Yeterli mi?

Hayır.

Şu yorum eksiktir:

```text
“out.txt doluysa başarılı, err.txt doluysa başarısız.”
```

Çünkü:

- Program uyarı mesajını `stderr`’a yazıp `0` ile bitebilir.
    
- Program hiçbir mesaj yazmadan sıfır dışı kodla bitebilir.
    
- Kod yanlışlıkla hatayı `stdout`’a yazabilir.
    

Doğru değerlendirme:

```text
stdout + stderr + exit code
```

üçü birlikte incelenmelidir.

> [!danger] Kafaya kazı  
> Mesajlar teşhis içindir.
> 
> Otomasyonun asıl karar sinyali exit code’dur.

---

# 🐳 Docker — Hata Katmanlarını Ayırmak

```text
Host shell
    ↓
Docker CLI
    ↓
Docker Engine / runtime
    ↓
Mount kurulması
    ↓
Container process’inin başlatılması
    ↓
Python uygulaması
```

Bir hata görüldüğünde önce hangi katmanda oluştuğu belirlenmelidir.

---

# 🔢 Docker Exit Code `125`, `126` ve `127`

|Kod|Genel anlam|
|--:|---|
|`125`|Docker container’ı çalıştıramadı|
|`126`|Komut bulundu fakat çalıştırılamadı|
|`127`|Çalıştırılacak komut bulunamadı|

## `125`

Docker çalıştırma katmanındaki hatadır.

Örnekler:

- Geçersiz `docker run` seçeneği
    
- Kurulamayan bind mount
    
- Runtime hatası
    
- Container hazırlanırken oluşan hata
    

Container içindeki Python uygulaması hiç başlamamış olabilir.

## `126`

Çalıştırılmak istenen dosya bulunmuştur ancak çalıştırılamamıştır.

Örnek:

```text
Permission denied
Execute izni bulunmaması
```

## `127`

Çalıştırılmak istenen executable bulunamamıştır.

```bash
docker run --rm busybox olmayan_komut
```

Python script’inin normal şekilde başlayıp hata vermesiyle aynı şey değildir.

---

> [!warning] Hassas ayrım  
> `127` durumunda Docker container yapısını hazırlamış olabilir fakat istenen ana komut başarıyla `exec` edilememiştir.
> 
> Bu nedenle:
> 
> ```text
> “Uygulama başladı ve sonra hata verdi.”
> ```
> 
> demek her zaman doğru değildir.
> 
> Daha doğru ifade:
> 
> ```text
> Container komutu bulunamadığı için uygulama process’i başlayamadı.
> ```

---

# 🧱 Bind Mount Hata Türleri

## 1. Mount hiç verilmezse

```bash
docker run --rm \
  -w /app \
  python:3.12-slim \
  python day06.py
```

Burada `-w /app` yalnızca çalışma dizinini belirler.

Host dosyalarını `/app` içine getirmez.

Akış:

```text
Container başladı
→ Python başladı
→ /app/day06.py bulunamadı
→ Python hata verdi
```

Bu bir bind mount kurulum hatası değildir.

Çünkü bind mount hiç istenmemiştir.

---

## 2. Yanlış ama mevcut klasör mount edilirse

```bash
-v "/yanlış/ama/mevcut/klasör":/app:ro
```

Docker mount’u başarıyla kurabilir.

Fakat yanlış içerik `/app` içinde görünür.

Akış:

```text
Mount başarılı
→ Container başladı
→ Python başladı
→ day06.py bulunamadı
→ Python/process hatası
```

Kök neden yanlış mount olsa da görünen hata uygulama katmanından gelebilir.

---

## 3. Geçersiz kaynak `--mount` ile verilirse

```bash
docker run --rm \
  --mount type=bind,src="$PWD/olmayan-klasor",dst=/app \
  python:3.12-slim \
  true
```

Akış:

```text
Kaynak bulunamadı
→ Mount kurulamadı
→ true başlamadı
→ Docker/runtime hatası
→ Exit code 125
```

---

# 🆚 `-v` ve `--mount`

## `-v`

```bash
-v "$PWD":/app:ro
```

Kısa ve yaygın kullanımdır.

Bazı durumlarda olmayan host dizinini oluşturabilir.

## `--mount`

```bash
--mount type=bind,src="$PWD",dst=/app,readonly
```

Daha açık sözdizimidir.

Olmayan source path için genellikle doğrudan hata verir.

Kontrollü mount hatası testi için daha uygundur.

---

# 🧪 Neden `true` Komutu Kullanıldı?

```bash
docker run ... python:3.12-slim true
```

`true`:

- Normalde çıktı üretmez.
    
- İşini başarıyla tamamlayınca `0` döndürür.
    
- Python kodunu denklemden çıkarır.
    

Test mantığı:

```text
Mount başarılıysa
→ true çalışır
→ exit code 0

Mount başarısızsa
→ true başlamaz
→ Docker exit code 125
```

Böylece hatanın Python’dan gelmediği kanıtlanır.

---

# 📂 Yönlendirme Dosyalarını Kim Oluşturur?

```bash
docker run ... > out.txt 2> err.txt
```

`out.txt` ve `err.txt` dosyalarını container oluşturmaz.

Host shell oluşturur.

İşlem sırası:

```text
Shell yönlendirme dosyalarını hazırlar.
        ↓
docker run çalıştırılır.
        ↓
Docker CLI çıktıları shell akışlarına gelir.
        ↓
Shell bunları dosyalara yazar.
```

Bu nedenle container’daki `/app` mount’u `readonly` olsa bile hostta:

```text
out.txt
err.txt
```

oluşturulabilir.

---

# 🔬 Host ve Container Sonuçlarını Karşılaştırma

## Host

```bash
python3 day06.py > host-out.txt 2> host-err.txt
host_code=$?
```

## Container

```bash
docker run --rm \
  -v "$PWD":/app:ro \
  -w /app \
  python:3.12-slim \
  python day06.py \
  > container-out.txt \
  2> container-err.txt

container_code=$?
```

Karşılaştırma:

```bash
diff host-out.txt container-out.txt
diff host-err.txt container-err.txt

echo "Host: $host_code"
echo "Container: $container_code"
```

---

## Set sırası karşılaştırmayı bozabilir

Host:

```text
{'api', 'db', 'worker'}
```

Container:

```text
{'worker', 'api', 'db'}
```

yazabilir.

İçerikler aynı olsa da `diff` metinleri farklı görür.

Çözüm:

```python
print("Fail servisler:", sorted(fail_servisler))
```

> [!important]  
> `diff`, Python veri yapılarının mantıksal eşitliğini bilmez.
> 
> Yalnızca karakterleri karşılaştırır.

---

# 🧯 Hata Avı

## 1. Fonksiyon içinde `sys.exit()`

Çalışır ama tekrar kullanılabilirlik açısından zayıftır.

Daha temiz model:

```text
Fonksiyon sonuç döndürür.
main() exit code’a karar verir.
```

## 2. `split(",")` kullanıp newline’ı unutmak

```python
durum = "fail\n"
```

oluşabilir.

Doğrusu:

```python
satır.strip().split(",")
```

## 3. Sete `append()` yapmak

TIRT.

```python
set.add()
```

kullanılır.

## 4. Dictionary’yi `"fail"` ile karşılaştırmak

TIRT.

Kontrol edilmesi gereken o anki:

```python
durum
```

değeridir.

## 5. `stderr` doluysa kesin hata demek

TIRT.

Exit code ayrıca kontrol edilmelidir.

## 6. `-w /app` dosyaları mount eder sanmak

TIRT.

`-w`, yalnızca container CWD’sini belirler.

## 7. Yanlış klasör mount edilince kesin `125` beklemek

TIRT.

Path mevcutsa yanlış klasör başarıyla mount edilebilir. Daha sonra Python dosyayı bulamayabilir.

## 8. Set sırasını host-container eşitliği için kullanmak

TIRT.

Set çıktısı deterministik hâle getirilmelidir.

---

# 🧠 Kafaya Kazı

> [!quote]  
> Aynı ham veri, farklı bilgi ihtiyaçları için farklı koleksiyonlarda tutulabilir.

> [!quote]  
> Dosyadan okunan satır tuple değil, string’dir.

> [!quote]  
> `strip()` dış boşlukları ve newline’ı temizler.

> [!quote]  
> `split(",")` satırı virgülden böler.

> [!quote]  
> Liste sıra, dictionary son eşleme, set benzersizlik tutar.

> [!quote]  
> `LATEST` ile `EVER_FAILED` aynı bilgi değildir.

> [!quote]  
> Fonksiyonun işi veri üretmek, ana programın işi process sonucuna karar vermektir.

> [!quote]  
> `stderr` mesaj kanalı, exit code process sonucudur.

> [!quote]  
> `-w` çalışma dizinidir; mount değildir.

> [!quote]  
> Yanlış mount ile geçersiz mount aynı şey değildir.

> [!quote]  
> Exit code `125`, Docker çalıştırma katmanına işaret eder.

> [!quote]  
> Exit code `127`, çalıştırılacak komutun bulunamadığını belirtir.

> [!quote]  
> Host ve container path’leri aynı değildir; mount onları birbirine bağlar.

---
# 📌 30 Saniyelik Özet

```text
PYTHON
list  → ilk görülme sırası
dict  → son durum
set   → geçmişte en az bir fail

DOSYA
satır tipi              → str
strip()                 → dış whitespace temizle
split(",")              → virgülden böl
servis, durum = ...     → unpacking

PROGRAM
return                  → fonksiyon değeri
sys.exit()              → process exit code
stderr                  → hata/teşhis mesajı
stdout                  → normal sonuç

LINUX
>                       → stdout yönlendirme
2>                      → stderr yönlendirme
2>&1                    → stderr’i stdout hedefine bağla
$?                      → son komutun exit code’u

DOCKER
-v / --mount            → Host içeriğini container’a bağla
-w                      → Container çalışma dizini
125                     → Docker çalıştıramadı
126                     → Komut var, çalıştırılamadı
127                     → Komut bulunamadı
true                    → Başarılı test komutu
```

---

# ✅ Günün Kazanımları

-  Aynı veri için birden fazla koleksiyon kullanıldı
    
-  List, dictionary ve set sorumlulukları ayrıldı
    
-  Dosyadan gelen satırın `str` olduğu anlaşıldı
    
-  `strip()` ve `split(",")` birlikte kullanıldı
    
-  Tuple unpacking uygulandı
    
-  İlk görülme sırası korundu
    
-  Son durum eşlemesi üretildi
    
-  Geçmişte fail olan servisler benzersiz tutuldu
    
-  `append()`, `add()` ve dictionary ataması ayrıldı
    
-  Fonksiyon ile process sonlandırma sorumluluğu ayrıldı
    
-  `stdout`, `stderr` ve exit code birlikte test edildi
    
-  `$?` değerinin hemen saklanması öğrenildi
    
-  Docker hata katmanları ayrıldı
    
-  Yanlış ve geçersiz bind mount farkı anlaşıldı
    
-  `125`, `126` ve `127` kodları ayrıldı
    
-  `true` ile saf mount testi yapıldı
    
-  Host ve container çıktılarındaki set sırası riski görüldü
    

> [!success] 🚀 Gün sonu sonucu  
> Gün 6 sonunda yalnızca dosya okuyan bir Python programı yazılmadı.
> 
> Aynı kayıt akışından farklı veri modelleri üretildi, fonksiyon sonucu ile process exit code’u ayrıldı ve bir hatanın Python uygulamasından mı yoksa Docker runtime katmanından mı geldiğini teşhis etme mantığı kuruldu.