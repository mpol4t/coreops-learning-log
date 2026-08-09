---
title: "Gün 13 — release_summary(), Testler, Linux İzinleri ve Docker Runtime"
tags:
  - coreops
  - python
  - linux
  - docker
  - pathlib
  - testing
  - permissions
  - dockerfile
  - image
  - runtime
aliases:
  - "Gün 13 Release Summary Test ve Docker Runtime"
status: completed
duration_minutes: 100
duration_breakdown:
  python_minutes: 60
  linux_minutes: 10
  docker_minutes: 20
  integration_minutes: 10
---

# 🚦 Gün 13 — `release_summary()`, Testler, Linux İzinleri ve Docker Runtime

> [!abstract] 🎯 Ana fikir  
> Bugünün çalışması üç ayrı katmanı aynı görev üzerinde birleştirdi:
> 
> ```text
> PYTHON
> → Recursive .txt arama
> → Boş / boş olmayan ayrımı
> → Relative path üretimi
> → Deterministik sonuç
> → Exception sözleşmesi
> → Assert testleri
> 
> LINUX
> → find ile bağımsız doğrulama
> → chmod ile okuma izni deneyi
> → Exit code kontrolü
> 
> DOCKER
> → COPY ile image snapshot'ı
> → CMD build/runtime ayrımı
> → docker logs / inspect
> → Rebuild sonrası yeni dosyanın image'a girmesi
> ```

---

# ⚡ 2 Dakikalık Geri Çağırma

## Bind mount vs image içine `COPY`

Bind mount:

```text
Host dosyası
    ↕
Container
```

Hosttaki değişiklik container'a, writable mount durumunda container'daki değişiklik de hosta yansıyabilir.

`COPY` ise:

```text
Host / Build Context
        ↓
       COPY
        ↓
      IMAGE
```

Build anındaki dosyanın image içine alınmış hâlidir.

Sonradan host dosyasını değiştirmek mevcut image'ı değiştirmez. Bu ayrım Gün 13'ün başlangıcında doğru şekilde hatırlanmış.

---

# 🐍 Python — `release_summary()`

Fonksiyonun görevi:

```text
Bir root dizini al
        ↓
Recursive şekilde .txt dosyalarını bul
        ↓
İçeriklerine bak
        ↓
Boş olanları ayır
Boş olmayanları ayır
        ↓
Boş olmayanların durum bilgisini sakla
        ↓
Relative path'lerle sonuç döndür
```

Kaynak implementasyonun ana yapısı:

---

# 📦 Fonksiyonun Döndürdüğü Üç Veri

```python
return (
    boş_olmayan_txtler,
    boş_txtler,
    durum_bilgisi,
)
```

Üçünün görevleri farklı:

|Veri|Tip|Anlam|
|---|---|---|
|`boş_olmayan_txtler`|`list[Path]`|İçeriği bulunan `.txt` dosyaları|
|`boş_txtler`|`list[Path]`|Boş kabul edilen `.txt` dosyaları|
|`durum_bilgisi`|`dict[Path, str]`|Boş olmayan dosya → okunan durum|

Bu yine önceki günlerdeki prensibin devamı:

> **Aynı aramadan çıkan farklı bilgiler için farklı veri yapıları kullanılır.**

---

# 📍 Root'u `Path` Nesnesine Çevirmek

```python
root = Path(root)
```

Bu noktadan sonra:

```python
root.exists()
root.is_dir()
root.rglob(...)
```

gibi `pathlib` metotları kullanılabilir.

---

# 🚪 Root Doğrulama

Kaynak kodun akışı:

```python
if root.exists():
    if root.is_dir():
        ...
    else:
        raise NotADirectoryError
else:
    raise FileNotFoundError
```

Davranış:

```text
Root yok
→ FileNotFoundError

Root var ama dizin değil
→ NotADirectoryError

Root var ve dizin
→ Aramaya devam et
```

---

## Guard Clause Alternatifi

Aynı mantık daha düz okunabilecek şekilde:

```python
if not root.exists():
    raise FileNotFoundError

if not root.is_dir():
    raise NotADirectoryError
```

şeklinde düşünülebilir.

Zihinsel model:

```text
Önce geçersiz girdileri reddet
↓
Sonra ana işe odaklan
```

---

# 🔎 Recursive `.txt` Arama

```python
for x in sorted(root.rglob("*.txt")):
```

Burada iki iş birlikte yapılıyor:

```text
rglob("*.txt")
→ Alt dizinlere de girerek .txt path'lerini bul

sorted(...)
→ Sonuçları deterministik sıraya sok
```

Deterministik sıra özellikle:

- Testlerde
    
- Host/container karşılaştırmasında
    
- Beklenen listelerle `assert` yaparken
    

önemlidir.

---

# 📄 Neden `is_file()`?

```python
if x.is_file():
```

ile eşleşen path'in gerçekten normal dosya olduğu kontrol ediliyor.

Bu sayede yalnız pattern'e uyan isimlere değil, nesnenin türüne de bakılmış oluyor.

---

# 📖 Dosya Okuma

```python
with open(
    x,
    encoding="utf-8",
) as file:
    dosya = file.readline()
```

Burada yalnızca:

```text
ilk satır
```

okunuyor.

Sonrasında:

```python
dosya = dosya.strip()
```

ile newline ve dış whitespace temizleniyor.

---

> [!warning] Kodun mevcut sözleşmesi  
> Bu implementasyon **dosyanın tamamının boş olup olmadığını değil, ilk okunan satırın boş olup olmadığını** temel alıyor.
> 
> Çünkü kullanılan işlem:
> 
> ```python
> file.readline()
> ```
> 
> Örneğin teorik olarak:
> 
> ```text
> ilk satır boş
> ikinci satır "Ok"
> ```
> 
> olan bir dosya mevcut kod tarafından boş sınıfına girebilir.
> 
> Kaynak test verilerinde bu durum görünmediği için testler mevcut davranışla başarılı olmuş.

---

# 🗺️ `relative_to(root)`

Dosya:

```text
gate13/release/nested/cache.txt
```

olsun.

```python
x.relative_to(root)
```

root `gate13` ise:

```text
release/nested/cache.txt
```

üretir.

Bu sayede:

- Hostun uzun absolute path'i sonuçlara girmez.
    
- Testler makineye daha az bağımlı olur.
    
- Çıktılar daha okunabilir olur.
    

---

# 🟢 Boş Olmayan Dosya

```python
if dosya:
    relative = x.relative_to(root)

    boş_olmayan_txtler.append(
        relative
    )

    durum_bilgisi[relative] = dosya
```

Örneğin:

```text
release/api.txt → Ok
release/db.txt  → Fail
```

hem listeye girer hem dictionary içinde durum bilgisi tutulur.

---

# ⚪ Boş Dosya

```python
if not dosya:
    relative = x.relative_to(root)
    boş_txtler.append(relative)
```

Önemli nokta:

```text
Boş dosya
→ boş_txtler listesinde bulunur
→ durum_bilgisi dictionary'sine eklenmez
```

Bu davranış ayrıca testte açıkça doğrulanmış.

---

# 🧪 Test Sözleşmesi

Kaynak testlerde gerçek beklenen sonuçlar açık şekilde belirtilmiş.

## Boş olmayanlar

```python
assert bos_olmayan_txtler == [
    Path("release/api.txt"),
    Path("release/db.txt"),
    Path(
        "release/nested/cache.txt"
    ),
]
```

## Boş olanlar

```python
assert bos_txtler == [
    Path(
        "release/nested/empty.txt"
    )
]
```

## Durum bilgisi

```python
assert list(
    durum_bilgisi.items()
) == [
    (
        Path("release/api.txt"),
        "Ok",
    ),
    (
        Path("release/db.txt"),
        "Fail",
    ),
    (
        Path(
            "release/nested/cache.txt"
        ),
        "Ok",
    ),
]
```

---

# 🚫 `.md` Dosyasının Dahil Olmaması

```python
assert Path(
    "release/README.md"
) not in bos_olmayan_txtler
```

ve:

```python
assert Path(
    "release/README.md"
) not in bos_txtler
```

ile:

```text
rglob("*.txt")
```

filtresinin gerçekten yalnız `.txt` kayıtlarını kapsadığı kontrol edilmiş.

---

# 💥 Exception Testleri

## Root dizin değil

```python
try:
    release_summary(
        "başarılı.txt"
    )
    assert False

except NotADirectoryError:
    pass
```

Mantık:

```text
Fonksiyon exception üretmeli.
        ↓
Üretmezse assert False patlasın.
        ↓
Beklenen exception gelirse test geçsin.
```

---

## Root bulunamadı

```python
try:
    release_summary(
        "olmayan_root"
    )
    assert False

except FileNotFoundError:
    pass
```

Bu da aynı exception sözleşmesini doğrular.

---

# 📭 Boş Root Testi

```python
bos_olmayan, boslar, durumlar = (
    release_summary("boş_root")
)
```

Beklenen:

```python
assert bos_olmayan == []
assert boslar == []
assert durumlar == {}
```

Bu çok önemli bir ayrım:

```text
Root yok
→ HATA

Root var ama içerisinde eşleşme yok
→ BAŞARILI boş sonuç
```

---

# 🎯 Testlerin Asıl Gücü

Testler yalnızca:

```text
“Fonksiyon çalışıyor mu?”
```

sorusunu sormuyor.

Aynı zamanda fonksiyonun sözleşmesini tarif ediyor:

```text
Hangi dosyalar dahil?
Hangileri hariç?
Sıra ne?
Boş dosya ne olacak?
Dictionary ne içerecek?
Root yoksa ne olacak?
Root dosyaysa ne olacak?
Root boşsa ne olacak?
```

> [!success]  
> Test kodu burada fonksiyonun beklenen davranışının makine tarafından çalıştırılabilir tanımı hâline gelmiş.

---

# 🐧 Linux — `find` ile Bağımsız Doğrulama

```bash
find gate13 \
  -type f \
  -name '*.txt'
```

sonucu:

```text
gate13/release/api.txt
gate13/release/db.txt
gate13/release/nested/cache.txt
gate13/release/nested/empty.txt
```

oldu.

Bu, Python'ın recursive `.txt` aramasını Linux `find` ile bağımsız şekilde doğruluyor.

---

# 🔐 Linux İzin Deneyi

Başlangıç:

```text
-rw-r--r-- db.txt
```

Sonra:

```bash
chmod 244 db.txt
```

çıktı:

```text
--w-r--r--
```

Owner izinleri:

```text
-w-
```

oldu.

Owner'ın read biti kaldırıldığı için:

```bash
cat db.txt
```

sonucu:

```text
Permission denied
```

oldu.

---

# 🔢 `244` Nasıl Okunur?

```text
2 → -w-
4 → r--
4 → r--
```

Yani:

```text
owner  → -w-
group  → r--
others → r--
```

Dosyanın owner'ı olan kullanıcı için owner üçlüsü seçildiğinden group veya others read izinleriyle birleştirme yapılmaz.

---

# 🔄 İzni Geri Getirmek

```bash
chmod 644 db.txt
```

sonrasında:

```text
-rw-r--r--
```

ve:

```bash
cat db.txt
```

tekrar başarılı oldu.

---

# 🚪 Python Exit Code Deneyi

Geçerli root:

```bash
python day13.py
echo $?
```

sonuç:

```text
0
```

Root bulunamadığında:

```text
Girdiğin path bulunamadı!
```

ve:

```text
22
```

görüldü.

Yani:

```text
Başarı               → 0
FileNotFoundError     → 22
NotADirectoryError    → 11
```

uygulama sözleşmesi oluşturulmuş.

---

# 🐳 Docker A — `COPY release/ .`

Dockerfile:

```dockerfile
FROM python:3.12-slim

WORKDIR /work

COPY release/ .

CMD ["python", "day13.py"]
```

Kaynak Docker build/run deneyinde bu yapı başarıyla çalışmış.

---

# 📦 `COPY release/ .` Ne Yaptı?

Host build context:

```text
gate13/
├── Dockerfile
└── release/
    ├── day13.py
    ├── api.txt
    ├── db.txt
    ├── README.md
    └── nested/
```

Dockerfile:

```dockerfile
WORKDIR /work
COPY release/ .
```

sonrasında image içeriği kavramsal olarak:

```text
/work/
├── day13.py
├── api.txt
├── db.txt
├── README.md
└── nested/
    ├── cache.txt
    └── empty.txt
```

oldu.

Dikkat:

```text
release/
```

isimli parent klasör image içine aynı seviyede korunmadı; **release klasörünün içeriği `/work` içine kopyalandı.**

---

# 🗺️ Host ile Container Path Farkı

Host çalıştırmasında:

```text
release/api.txt
release/db.txt
release/nested/cache.txt
```

Container'da:

```text
api.txt
db.txt
nested/cache.txt
```

çıktı.

Dolayısıyla:

> [!warning]  
> “Host ile Docker sonuçları aynı geldi.” ifadesi **mantıksal dosya içeriği açısından doğru**, fakat path string'leri birebir aynı değildir.
> 
> Bunun sebebi:
> 
> ```dockerfile
> COPY release/ .
> ```
> 
> ile container tarafındaki arama root'unun farklı filesystem yapısında olmasıdır.

Aynı dosya seti:

```text
Host      → release/api.txt
Container → api.txt
```

olarak temsil edilebilir.

---

# 🧨 Docker B — Bozuk `CMD`

Dockerfile:

```dockerfile
FROM python:3.12-slim

WORKDIR /work

COPY release/ .

CMD ["python", "day.py"]
```

`day.py` image içinde bulunmamasına rağmen:

```bash
docker build -t day13 .
```

başarıyla tamamlandı.

---

# ❓ Build Neden Başarılı Oldu?

Çünkü:

```dockerfile
CMD ["python", "day.py"]
```

build sırasında çalıştırılmadı.

Build'in görevi:

```text
Dockerfile talimatlarından image oluşturmak
```

idi.

`CMD` ise image metadata'sına runtime varsayılan komutu olarak kaydedildi.

---

# ▶️ Hata Runtime'da

```bash
docker run day13
```

sonucu:

```text
python: can't open file
'/work/day.py'
```

ve shell:

```text
exit code 2
```

gördü.

Akış:

```text
Image başarıyla build
        ↓
Container oluşturuldu
        ↓
Python process başladı
        ↓
Python /work/day.py açmaya çalıştı
        ↓
Dosya yok
        ↓
Python exit code 2
        ↓
Container Exited (2)
```

---

# 🔥 Kritik Katman Ayrımı

```text
Docker build hatası ❌
Docker runtime hazırlama hatası ❌
Python process hatası ✅
```

Çünkü hata mesajı:

```text
python: can't open file
```

şeklinde Python'dan geldi.

---

# 📜 `docker logs`

İlk deneme:

```bash
docker logs day13
```

başarısız oldu:

```text
No such container: day13
```

Çünkü:

```text
day13
```

image adıydı.

Container'ın gerçek adı Docker tarafından:

```text
vigilant_mirzakhani
```

olarak atanmıştı.

Container ID ile:

```bash
docker logs cb7ca16c3e9b
```

çalıştı.

---

> [!danger] Kafaya kazı
> 
> ```text
> docker logs
> → Container ister.
> 
> Image adı ile container adı aynı şey değildir.
> ```

---

# 🔬 `docker inspect`

```bash
docker inspect cb7ca16c3e9b
```

çıktısı runtime hakkında güçlü kanıtlar sağladı.

Önemli alanlar:

```text
State.Status   → exited
State.ExitCode → 2

Path           → python
Args           → ["day.py"]

Config.Cmd     → ["python", "day.py"]
WorkingDir     → /work

Image          → day13
```

Yani tek komutla:

```text
Hangi image?
Hangi komut?
Hangi argüman?
Hangi CWD?
Hangi exit code?
```

gibi bilgiler doğrulanabildi.

---

# 🧩 `docker logs` vs `docker inspect`

```text
docker logs
→ Process ne yazdı?

docker inspect
→ Container nasıl yapılandırılmıştı ve ne durumda?
```

Birbirlerinin alternatifi değil, tamamlayıcısıdır.

---

# 🔧 Dockerfile Düzeltildikten Sonra

```dockerfile
CMD ["python", "day13.py"]
```

yapıldı.

Sonra:

```bash
docker build -t day13 .
docker run day13
```

çalıştırıldı.

Program tekrar başarıyla sonuç üretti.

---

# 🧊 Eski Image Yeni Host Dosyasını Görür mü?

Build sonrasında hostta:

```text
release/nested/worker.txt
```

oluşturuldu.

Temel tahmin:

```text
Eski image
→ worker.txt'yi görmez.
```

Çünkü image:

```text
önceki build anındaki
release/
```

snapshot'ını içerir.

---

# ⚠️ `docker rebuild` Diye Komut Yok

Deney:

```bash
docker rebuild day13 .
```

sonucu:

```text
unknown command:
docker rebuild
```

oldu.

Image'ı yeni içerikle üretmek için tekrar:

```bash
docker build -t day13 .
```

kullanılır.

Bu pratikte bizim:

```text
rebuild
```

dediğimiz işlemdir ama Docker CLI alt komutunun adı hâlâ `build`'dir.

---

# 🔄 Rebuild Sonrası `worker.txt`

Yeni build:

```bash
docker build -t day13 .
```

sonrasında:

```bash
docker run day13
```

çıktısına:

```text
nested/worker.txt -> Fail
```

eklendi.

Zincir:

```text
Hostta worker.txt oluştur
        ↓
Build context güncel
        ↓
COPY release/ .
        ↓
Yeni image layer
        ↓
docker run
        ↓
Container worker.txt'yi görür
```

---

# 🔍 Linux `find` ile Son Doğrulama

Host:

```bash
find . \
  -type f \
  -name '*.txt' \
  -maxdepth 3
```

çıktısında:

```text
release/nested/worker.txt
```

da görüldü.

Böylece:

```text
Host filesystem sonucu
↕
Rebuild edilmiş image/container sonucu
```

uyuştu.

---

# 🆚 `COPY` ve Bind Mount — Günün Büyük Karşılaştırması

## `COPY`

```text
BUILD TIME

Host
 ↓
Build Context
 ↓
COPY
 ↓
Image
 ↓
Container
```

Hostta sonradan değişiklik:

```text
Mevcut image'a otomatik yansımaz.
```

---

## Bind Mount

```text
RUNTIME

Host
 ↕
Container
```

Host değişirse:

```text
Container yeni veriyi görebilir.
```

Container writable mount üzerinden değiştirirse:

```text
Host da etkilenebilir.
```

---

# 🎯 Hangi Durumda Hangisi?

```text
Image kendi sabit uygulama dosyalarını taşısın
→ COPY

Geliştirme sırasında host dosyaları canlı görülsün
→ Bind mount
```

---

# 🧯 Hata Avı

## 1. Root var diye dizindir

TIRT.

```python
exists()
```

ve:

```python
is_dir()
```

farklı kontrollerdir.

---

## 2. Boş root hata üretmeli

TIRT.

Geçerli root + sıfır eşleşme:

```python
([], [], {})
```

gibi başarılı boş sonuç üretebilir.

---

## 3. Relative path gereksizdir

TIRT.

Testleri hostun absolute path'inden bağımsızlaştırır ve çıktıyı okunabilir yapar.

---

## 4. Arama sonucu sıralamaya gerek yok

TIRT.

Deterministik test için sıralama önemlidir.

---

## 5. `README.md` de sonuçlara girmeli

TIRT.

Pattern:

```python
"*.txt"
```

yalnız `.txt` eşleşmelerini hedefliyor.

---

## 6. İlk satır boş değilse dosya kesin tamamen doludur

Kaynak fonksiyon yalnız ilk satırı okuyor.

Bu yüzden sınıflandırma mevcut implementasyonda:

```text
İlk satır üzerinden
```

yapılıyor.

---

## 7. Host ve container path çıktıları birebir aynı

TIRT.

`COPY release/ .` nedeniyle hostta:

```text
release/api.txt
```

container'da:

```text
api.txt
```

görüldü.

Mantıksal dosya aynı olabilir, path temsili farklıdır.

---

## 8. Bozuk `CMD` build'i bozmak zorundadır

TIRT.

`CMD` runtime'da çalışır.

---

## 9. `day.py` bulunamadığı için Docker exit code `125` verir

TIRT.

Bu deneyde container/Python process başladı.

Python script'i bulamadığı için:

```text
Exit code 2
```

oluştu.

---

## 10. `docker logs day13` image loglarını verir

TIRT.

`docker logs` container üzerinde çalışır.

---

## 11. Hostta yeni dosya oluşturunca image anında güncellenir

TIRT.

`COPY` canlı bağlantı değildir.

---

## 12. Image'ı yenilemek için `docker rebuild`

TIRT.

Tekrar:

```bash
docker build -t day13 .
```

çalıştırılır.

---

# 🧠 Kafaya Kazı

> [!quote]  
> Root yoksa `FileNotFoundError`, root dizin değilse `NotADirectoryError`.

> [!quote]  
> Boş arama sonucu hata değildir.

> [!quote]  
> Recursive arama sonucunu sıralamak testleri deterministik yapar.

> [!quote]  
> `relative_to(root)` host absolute path bağımlılığını azaltır.

> [!quote]  
> Test sadece kodu kontrol etmez; fonksiyon sözleşmesini tarif eder.

> [!quote]  
> Linux `find`, Python aramasına bağımsız doğrulama sağlayabilir.

> [!quote]  
> Owner read biti yoksa owner group/others izinlerine geçmez.

> [!quote]  
> `COPY release/ .`, release içeriğini WORKDIR içine alır.

> [!quote]  
> `CMD` build-time değil runtime davranışıdır.

> [!quote]  
> Build başarılı olabilir fakat container runtime'da başarısız olabilir.

> [!quote]  
> `docker logs` process çıktısını, `docker inspect` container durum/config bilgisini gösterir.

> [!quote]  
> Image adı ile container adı aynı şey değildir.

> [!quote]  
> `COPY` build snapshot'ıdır.

> [!quote]  
> Bind mount runtime canlı bağlantısıdır.

> [!quote]  
> Yeni host dosyasını image'ın görmesi için yeniden build gerekir.

---

# 📌 30 Saniyelik Özet

```text
PYTHON
Path(root)              → Root'u modelle
exists()                → Root var mı?
is_dir()                → Dizin mi?
rglob("*.txt")          → Recursive txt ara
sorted(...)             → Deterministik sıra
is_file()               → Gerçek dosya mı?
readline()              → İlk satırı oku
strip()                 → Whitespace temizle
relative_to(root)       → Relative path üret

SONUÇ
non_empty list          → Boş olmayan txt
empty list              → Boş txt
dict                    → Path → durum

HATA
Root yok                → FileNotFoundError
Root dosya              → NotADirectoryError
Root boş                → [], [], {}

TEST
assert                   → Beklenen davranışı doğrula
try/except               → Exception sözleşmesini test et

LINUX
find                     → Recursive aramayı doğrula
chmod 244                → Owner read kaldır
chmod 644                → Read iznini geri getir
echo $?                  → Process sonucunu kontrol et

DOCKER
COPY release/ .          → release içeriği image /work'e
CMD                      → Runtime varsayılan komutu
docker logs              → Container stdout/stderr
docker inspect           → Config + state + exit code
docker build             → Image'ı yeniden oluştur

KRİTİK
COPY                     → Build snapshot
Bind mount               → Runtime canlı bağlantı
```

---

# ✅ Günün Kazanımları

-  Önceki günlerin `Path` bilgileri tek fonksiyonda birleştirildi
    
-  Recursive `.txt` arama yapıldı
    
-  Arama deterministik hâle getirildi
    
-  Dosya ve dizin kontrolleri uygulandı
    
-  Boş ve boş olmayan `.txt` dosyaları ayrıldı
    
-  Dictionary ile durum bilgileri tutuldu
    
-  `relative_to()` gerçek görev içinde kullanıldı
    
-  Root yok / dizin değil / boş root senaryoları ayrıldı
    
-  Fonksiyon çıktısı kapsamlı `assert` testleriyle doğrulandı
    
-  `.md` dosyasının dışlandığı test edildi
    
-  Boş dosyanın dictionary'ye girmediği doğrulandı
    
-  Exception testleri yazıldı
    
-  Linux `find` ile Python sonucu bağımsız doğrulandı
    
-  `chmod 244` ile owner read izni kaldırıldı
    
-  Owner/group/others seçim mantığı pratikte gözlemlendi
    
-  Başarı ve hata exit code'ları kontrol edildi
    
-  `COPY release/ .` davranışı uygulandı
    
-  Host ve container relative path farkı gözlemlendi
    
-  Bozuk `CMD` ile build-time/runtime sınırı test edildi
    
-  Python kaynaklı runtime exit code `2` görüldü
    
-  Image adı ile container adı ayrımı pekiştirildi
    
-  `docker logs` kullanıldı
    
-  `docker inspect` ile runtime kanıtları incelendi
    
-  `docker rebuild` diye bir alt komut olmadığı öğrenildi
    
-  Yeni host dosyasının eski image'a otomatik girmediği tekrar doğrulandı
    
-  Yeniden build sonrası `worker.txt` image/container içinde görüldü
    
-  `COPY` snapshot ile bind mount canlı bağlantı farkı oturdu
    

> [!success] 🚀 Gün sonu sonucu  
> Gün 13, önceki günlerde ayrı ayrı öğrenilen kavramların gerçek bir **gate görevi** içinde birleştiği nokta oldu.
> 
> Python tarafında:
> 
> ```text
> Path
> + recursive arama
> + exception
> + deterministic sonuç
> + test
> ```
> 
> birlikte kullanıldı.
> 
> Docker tarafında ise en önemli sınır çok net görüldü:
> 
> ```text
> Dockerfile doğru şekilde image oluşturabilir
>             ↓
> Build başarılı olabilir
>             ↓
> Ama CMD içindeki process runtime'da yine patlayabilir
> ```
> 
> Günün en kritik modeli:
> 
> **Build image'ı hazırlar; runtime process'i sınar. `COPY` geçmişin snapshot'ıdır, bind mount ise host ile yaşayan bağlantıdır.**
