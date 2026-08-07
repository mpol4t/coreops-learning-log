---
title: "Gün 10 — with, Dosya Okuma, Satır Sayımı ve Read-Only Docker"
tags:
  - coreops
  - python
  - linux
  - docker
  - file-io
  - context-manager
  - text-processing
  - wc
  - readonly-mount
aliases:
  - "Gün 10 Dosya Okuma With ve Bağımsız Doğrulama"
status: completed
duration_minutes: 100
---

# 🧠 Gün 10 — `with`, Dosya Okuma, Satır Sayımı ve Read-Only Docker

> [!abstract] 🎯 Ana fikir  
> Dosya işlemlerinde üç ayrı şeyi net ayır:
> 
> ```text
> open()  → Dosya kaynağını açar.
> read()  → Veriyi okur.
> with    → Kaynağın yaşam döngüsünü güvenli yönetir.
> ```
> 
> Ayrıca iki aracın sonuçlarını karşılaştırmadan önce **aynı şeyi ölçüp ölçmediklerini** kontrol et.
> 
> ```text
> Python kodu → Boş olmayan satırları sayıyor.
> wc -l       → Newline karakterlerini sayıyor.
> ```
> 
> Bu yüzden sonuçlarının farklı olması otomatik olarak bug değildir.

---

# ⚡ 2 Dakikalık Geri Çağırma

## İzin sorusundaki kritik düzeltme

Senaryo:

```text
Dosya owner UID → 501
Process UID     → 1000
Mode            → 644
```

Yalnızca bunlarla hangi izin üçlüsünün kullanılacağını kesin söyleyemeyiz.

Ama sebep:

> “Dosya owner UID’sini bilmiyoruz.”

değildir; **owner UID zaten 501 olarak verilmiş.**

Eksik olan bilgi:

```text
Dosyanın GID’si
+
Process’in grup üyelikleri
```

Çünkü:

```text
Process UID 1000 != Owner UID 501
        ↓
Owner sınıfı değil.
        ↓
Process dosyanın grubunda mı?
        ↓
Bunu bilmiyoruz.
```

Grup eşleşirse:

```text
group → r--
```

eşleşmezse:

```text
others → r--
```

kullanılır.

Bu özel `644` örneğinde group ve others zaten aynı `r--` olduğu için **fiilî okuma sonucu aynı çıkabilir**, fakat hangi permission sınıfının seçildiğini yine de grup bilgisi olmadan söyleyemeyiz.

---

# 🐍 Python — `open()`, `with` ve File Object

Dosya açmak:

```python
file = open("data.txt", encoding="utf-8")
```

şu anlama gelmez:

```text
Dosyanın tamamı RAM’e yüklendi.
```

`open()`:

```text
Dosya kaynağını açar
        ↓
Bir file object üretir
```

Veriyi gerçekten okumak için:

```python
file.read()
```

veya:

```python
for line in file:
```

gibi işlemler gerekir.

---

# 🔐 Neden `with open(...)`?

Manuel kullanım:

```python
file = open(
    "data.txt",
    encoding="utf-8",
)

veri = file.read()

file.close()
```

Arada exception oluşursa:

```text
file.close()
```

satırına hiç ulaşılamayabilir.

Ayrıca programcı `close()` yazmayı unutabilir.

Daha sağlam kullanım:

```python
with open(
    "data.txt",
    encoding="utf-8",
) as file:
    veri = file.read()
```

Akış:

```text
Kaynağı aç
    ↓
Dosyayı kullan
    ↓
Normal bitiş veya exception
    ↓
Cleanup
    ↓
Dosyayı kapat
```

> [!important]  
> `with`, oluşan exception’ı otomatik çözmez.
> 
> Asıl sağladığı şey kaynağın güvenilir şekilde temizlenmesidir.

---

# 🚪 `with` Bloğundan Çıkınca Ne Olur?

```python
with open(
    "data.txt",
    encoding="utf-8",
) as file:
    veri = file.read()

print(file.closed)
```

Sonuç:

```text
True
```

Burada önemli ayrım:

```text
file değişkeni hâlâ var
        ≠
Dosya hâlâ açık
```

Tekrar:

```python
file.read()
```

denersen:

```text
ValueError:
I/O operation on closed file
```

oluşabilir.

---

# 📖 `file.read()` ile `for line in file`

## `file.read()`

```python
veri = file.read()
```

Dosyanın kalan içeriğini tek bir:

```python
str
```

olarak döndürür.

Zihinsel model:

```text
Dosyanın kalan içeriği
        ↓
Tek bir büyük str
        ↓
Program
```

Küçük dosyalarda gayet kullanışlıdır.

---

## `for line in file`

```python
for line in file:
    print(line)
```

Program seviyesinde dosyayı satır satır tüketir:

```text
Satırı al
   ↓
İşle
   ↓
Sonraki satırı al
   ↓
İşle
```

Özellikle büyük:

- Log
    
- CSV
    
- Metin
    

dosyalarında tamamını tek seferde bellekte tutmaya göre daha uygun olabilir.

> [!note]  
> Python arkada buffering yapabilir.
> 
> Bu nedenle fiziksel diskten mutlaka tek tek satır okunduğunu düşünme.
> 
> Doğru zihinsel model:
> 
> **Program dosyayı satır satır tüketiyor.**

---

# 📝 Text Mode vs Binary Mode

## Text mode

```python
open(
    "data.txt",
    "r",
    encoding="utf-8",
)
```

Python tarafında:

```python
str
```

elde edilir.

Akış:

```text
Dosyadaki bytes
       ↓
Encoding ile decode
       ↓
Python str
```

---

## Binary mode

```python
open("foto.jpg", "rb")
```

Python tarafında:

```python
bytes
```

elde edilir.

Akış:

```text
Dosyadaki bytes
       ↓
Python bytes
```

Karakter decoding işlemi yapılmaz.

Kısaca:

```text
TEXT   → bytes ↔ str
BINARY → bytes ↔ bytes
```

---

# 🔤 `encoding="utf-8"`

Text mode’da Python’ın byte ile karakter arasında nasıl dönüşüm yapacağını belirtir.

## Okuma

```text
bytes
  ↓
UTF-8 decode
  ↓
str
```

## Yazma

```text
str
 ↓
UTF-8 encode
 ↓
bytes
```

Örnek:

```python
with open(
    "isimler.txt",
    encoding="utf-8",
) as file:
    veri = file.read()
```

Yanlış encoding:

- Türkçe karakterleri bozabilir.
    
- Anlamsız karakterler oluşturabilir.
    
- `UnicodeDecodeError` üretebilir.
    

---

# 🧪 Günün Python Uygulaması

```python
def okuyucu(dosya):
    with open(
        dosya,
        encoding="utf-8",
    ) as file:
        satır_sayısı = 0
        benzersizler = set()

        for satır in file:
            satır = satır.strip()

            if satır:
                satır_sayısı += 1
                benzersizler.add(satır)

    return satır_sayısı, benzersizler
```

Fonksiyonun yaptığı:

```text
Dosyayı aç
    ↓
Satır satır dolaş
    ↓
strip()
    ↓
Boş satır mı?
    ├── Evet → Sayma
    └── Hayır → Sayaç +1
               Sete ekle
```

---

# 📏 Buradaki `satır_sayısı` Tam Olarak Neyi Sayıyor?

Kod:

```python
satır = satır.strip()

if satır:
    satır_sayısı += 1
```

kullandığı için:

> **Fiziksel satır sayısını değil, boş olmayan satırların sayısını** tutuyor.

Bu isim daha açıklayıcı bile olabilir:

```python
bos_olmayan_satir_sayisi
```

---

# 🧩 `strip()` Yüzünden Ne Oluyor?

Örneğin:

```python
"\n".strip()
```

sonucu:

```python
""
```

olur.

Boş string:

```python
if "":
```

koşulunda `False` kabul edilir.

Dolayısıyla boş satır sayılmaz.

---

# ♻️ Benzersiz İçerik

```python
benzersizler = set()
```

ve:

```python
benzersizler.add(satır)
```

sayesinde tekrar eden aynı satırlar yalnızca bir kez tutulur.

Örneğin dosya:

```text
linux
docker
python
python

linux
```

ise sonuç mantıksal olarak:

```python
{
    "linux",
    "docker",
    "python",
}
```

olur.

> [!warning]  
> Set yazdırma sırası garanti edilmez.

Host:

```text
{'linux', 'python', 'docker'}
```

Container:

```text
{'docker', 'linux', 'python'}
```

yazabilir.

Bunlar aynı set olabilir.

Deterministik çıktı gerekiyorsa:

```python
print(sorted(benzersizler))
```

kullan.

---

# 📭 Boş Dosya Kontrolü

```python
satır_sayısı, benzersizler = okuyucu(
    "boş.txt"
)

if benzersizler:
    ...
else:
    print("Dosya boş.")
```

Boş set Python’da falsy olduğu için:

```python
bool(set())
```

sonucu:

```python
False
```

olur.

---

# 🐧 Linux — `wc -l` Gerçekte Neyi Sayar?

```bash
wc -l data.txt
```

doğrudan:

```text
“Gözümle gördüğüm satırları”
```

saymaz.

Esas olarak dosyadaki:

```text
\n
```

newline karakterlerini sayar.

Bu önemli bir farktır.

---

# ⚠️ Son Satır Newline ile Bitmiyorsa

Dosya görsel olarak:

```text
linux
docker
python
```

şeklinde üç satır içerebilir.

Ama son satırın sonunda `\n` yoksa:

```bash
wc -l
```

sonucu beklediğin fiziksel satır sayısından düşük çıkabilir.

> [!important]
> 
> ```text
> wc -l = newline sayısı
> ```
> 
> şeklinde düşünmek daha doğru.

---

# ⬜ Boş Satır Sayılır mı?

Evet.

Boş satır:

```text
\n
```

içerdiği için `wc -l` açısından bir newline’dır.

Bu nedenle:

```text
Toplam newline sayısı
≠
Boş olmayan içerik satırı sayısı
```

---

# 🧪 Gerçek Deney

Linux:

```bash
wc -l data.txt
```

sonucu:

```text
5 data.txt
```

Python:

```text
Satır sayısı: 4
```

verdi.

Bu otomatik olarak bug değildir.

Çünkü iki araç farklı tanımlar kullanıyor.

```text
Python kodu
→ strip sonrası boş olmayan satırları sayıyor.

wc -l
→ newline karakterlerini sayıyor.
```

---

# 🔃 `sort`

```bash
sort data.txt
```

satırları sıralar.

Sayısal sıralama gerekiyorsa:

```bash
sort -n sayilar.txt
```

kullanılabilir.

---

# ♻️ `uniq`

`uniq` dosyanın her yerindeki tekrarları otomatik bulmaz.

Yalnızca:

```text
Yan yana bulunan aynı satırları
```

algılar.

Örneğin:

```text
python
linux
python
```

üzerinde doğrudan:

```bash
uniq
```

iki `python` satırını kaldırmaz çünkü yan yana değildir.

---

# 🔗 Neden `sort | uniq`?

```bash
sort data.txt | uniq
```

Akış:

```text
sort
↓
Aynı satırları yan yana getir

uniq
↓
Yan yana tekrarları kaldır
```

Tek komut alternatifi:

```bash
sort -u data.txt
```

Tekrar sayılarını görmek:

```bash
sort data.txt | uniq -c
```

---

# 🧠 Linux Araçlarının Zihinsel Modeli

```text
wc    → Kaç tane?
grep  → Hangileri koşula uyuyor?
sort  → Hangi sıradalar?
uniq  → Komşu tekrarlar var mı?
```

> [!danger] TIRT düşünce  
> “`uniq` bütün dosyadaki tekrarları bulur.”
> 
> Yanlış.
> 
> **Yalnızca komşu tekrarları işler.**

---

# 🧪 Python'ı Linux ile Bağımsız Doğrulamak

Python sonucunu yine aynı Python fonksiyonuyla kontrol etmek çok güçlü bir doğrulama değildir.

Daha iyi yaklaşım:

```text
Python sonucu
        ↕
Linux araçları
```

Örneğin:

```bash
wc -l data.txt
sort data.txt | uniq
```

ile farklı bir araç zincirinden kanıt elde edilir.

> [!important]  
> Fakat karşılaştırmadan önce araçların aynı metriği ölçtüğünü doğrula.
> 
> Farklı tanımların farklı sonuç üretmesi normaldir.

---

# 🐳 Docker — Read-Only Bind Mount

Komut:

```bash
docker run --rm \
  --mount type=bind,source="$PWD",target=/app,readonly \
  -w /app \
  python:3.12-slim \
  python day10.py
```

Burada üç ayrı kavram var:

```text
Bind mount → Dosya nerede?
readonly   → Yazılabilir mi?
-w         → Program nereden çalışıyor?
```

---

# 📦 Bind Mount

```bash
--mount type=bind,source="$PWD",target=/app
```

anlamı:

```text
Host $PWD
   ↓
Container /app
```

Dosya kopyalanmaz.

Hosttaki kaynak container içinde `/app` altında görünür hâle gelir.

---

# 🔒 `readonly` / `:ro`

```bash
--mount type=bind,source="$PWD",target=/app,readonly
```

veya:

```bash
-v "$PWD":/app:ro
```

Container açısından mount:

```text
Okuma         ✅
Değiştirme    ❌
Yeni dosya    ❌
Silme         ❌
```

durumuna gelir.

---

# 🧠 `ro` Python'ın RAM İşlemlerini Engeller mi?

Hayır.

Program:

```python
liste = []
benzersizler = set()
```

oluşturabilir.

Çünkü bunlar:

```text
RAM
```

içinde gerçekleşir.

`ro` yalnızca:

```text
Mount edilen filesystem kaynağına yazmayı
```

engeller.

> [!success]
> 
> ```text
> ro ≠ Python hiçbir şeyi değiştiremez
> 
> ro = Bu mount üzerinden filesystem'e yazamaz
> ```

---

# 📂 `-w /app`

```bash
-w /app
```

kabaca:

```bash
cd /app
python day10.py
```

mantığını sağlar.

Kod:

```python
open("data.txt")
```

dediğinde göreli path:

```text
/app/data.txt
```

olarak çözülür.

---

> [!danger] Kafaya kazı
> 
> ```text
> Dosyaları /app içine getiren
> → Bind mount
> 
> Process’i /app içinden çalıştıran
> → -w /app
> ```

`-w` dosya taşımaz.

---

# 🐍 Program Yalnızca Okuyorsa Neden `ro` Yeterli?

Programın filesystem işlemi:

```text
data.txt dosyasını oku
```

ile sınırlı.

Devamında:

```text
strip()
set()
if
for
sayaç
```

gibi işlemler RAM’de gerçekleşir.

Dolayısıyla writable mount gereksizdir.

Hatta `readonly` kullanmak daha güvenlidir çünkü kodun yanlışlıkla host dosyalarını değiştirmesini önler.

---

# 🧪 Host ve Docker Sonucu

Host:

```bash
python3 day10.py
```

Container:

```bash
docker run --rm \
  --mount type=bind,source="$PWD",target=/app,readonly \
  -w /app \
  python:3.12-slim \
  python day10.py
```

Her ikisi de:

```text
Boş olmayan satır → 4
Benzersiz değerler → linux, docker, python
```

sonucunu üretti.

Set yazdırma sırası farklıydı ama içerik aynıydı.

---

# ⚠️ Aynı Sonuç Neyi Kanıtlar?

Doğru çıkarım:

> Bu kod, bu girdiler ve bu container ortamında aynı mantıksal sonucu üretti.

Yanlış çıkarım:

> Kod her ortamda ve her girdide kesinlikle aynı çalışır.

Tek başarılı test:

```text
Bütün olası koşulların kanıtı değildir.
```

---

# 🔗 Günün Entegrasyonu

Tahmin:

```text
Python → 4 boş olmayan satır
Linux  → 5 newline
Docker → Python ile aynı mantıksal sonuç
```

Gerçek deney de bunu doğruladı.

```text
Python:
4

wc -l:
5

Docker:
4
```

Benzersiz içerik:

```text
docker
linux
python
```

olarak üç değerden oluştu.

---

# 🧯 Hata Avı

## 1. `open()` dosyanın tamamını RAM’e yükler

TIRT.

`open()` dosya kaynağını açıp file object oluşturur.

---

## 2. `with` exception'ı çözer

TIRT.

Kaynağın güvenli şekilde kapatılmasını sağlar.

---

## 3. `with` bloğundan sonra `file` değişkeni tamamen yok olur

TIRT.

Değişken varlığını sürdürebilir fakat dosya nesnesi kapalıdır.

---

## 4. `file.read()` ile `for line in file` aynı kullanım modelidir

TIRT.

Biri kalan veriyi tek sonuç olarak okur, diğeri program seviyesinde satır satır tüketir.

---

## 5. `wc -l` görünen satırların tamamını sayar

TIRT.

Newline karakterlerini sayar.

---

## 6. Boş satırlar `wc -l` tarafından sayılmaz

TIRT.

Newline içerdiği için sayılır.

---

## 7. `uniq` bütün tekrarları bulur

TIRT.

Yalnızca yan yana tekrarları işler.

---

## 8. Python 4, `wc -l` 5 verdi; kod bozuk

TIRT.

Önce ölçülen kavramların tanımını karşılaştır.

---

## 9. `readonly`, Python'ın set/list oluşturmasını engeller

TIRT.

RAM işlemlerini etkilemez.

---

## 10. `-w /app` host dosyalarını `/app` içine getirir

TIRT.

Bunu bind mount yapar.

---

# 🧠 Kafaya Kazı

> [!quote]  
> `open()` kaynağı açar; `read()` veriyi okur.

> [!quote]  
> `with`, kaynak yaşam döngüsünü güvenli yönetir.

> [!quote]  
> `file` değişkeninin var olması dosyanın hâlâ açık olduğu anlamına gelmez.

> [!quote]  
> Text mode `str`, binary mode `bytes` üretir.

> [!quote]  
> Encoding, bytes ile karakter arasındaki dönüşüm kuralıdır.

> [!quote]  
> `file.read()` kalan içeriği tek sonuç olarak alır.

> [!quote]  
> `for line in file` dosyayı program seviyesinde satır satır tüketir.

> [!quote]  
> `wc -l`, newline sayar.

> [!quote]  
> Boş olmayan satır sayısı ile `wc -l` aynı ölçüm değildir.

> [!quote]  
> `uniq` yalnızca komşu tekrarları yakalar.

> [!quote]  
> `sort`, tekrarları `uniq` için yan yana getirir.

> [!quote]  
> Bind mount dosyanın konumunu belirler.

> [!quote]  
> `ro`, mount’un yazılabilirliğini belirler.

> [!quote]  
> `-w`, process’in CWD’sini belirler.

> [!quote]  
> Bir testin başarılı olması bütün koşulların kanıtı değildir.

---
# 📌 30 Saniyelik Özet

```text
PYTHON FILE I/O
open()             → Kaynağı aç
read()             → Veriyi oku
close()            → Kaynağı bırak
with               → Yaşam döngüsünü yönet

TEXT
text mode          → str
binary mode        → bytes
utf-8              → encode/decode kuralı

OKUMA
file.read()        → Kalan içerik tek sonuç
for line in file   → Satır satır tüket

DAY10
strip()            → Dış whitespace temizle
if satır           → Boşları atla
set.add()          → Benzersiz içerik
Python sayacı      → Boş olmayan satırlar

LINUX
wc -l              → Newline sayısı
sort               → Satırları sırala
uniq               → Komşu tekrarları ayıkla
sort | uniq        → Sırala + tekrarları ayıkla
sort -u            → Aynı işin kısa yolu

DOCKER
bind mount         → Dosya nerede?
readonly / :ro     → Yazılabilir mi?
-w /app            → Process nereden çalışıyor?

KRİTİK
Python sonucu ≠ wc sonucu
→ Önce tanım farkını kontrol et.
```

---

# ✅ Günün Kazanımları

-  `open()`, `read()` ve `close()` görevleri ayrıldı
    
-  `with` ile context manager mantığı öğrenildi
    
-  Exception durumunda kaynak temizliğinin önemi kavrandı
    
-  `with` sonrasında file object’in kapandığı görüldü
    
-  `file.read()` ile satır iterasyonu ayrıldı
    
-  Text ve binary mode ayrıldı
    
-  `str` ve `bytes` farkı tekrar edildi
    
-  `encoding="utf-8"` amacı öğrenildi
    
-  Boş olmayan satır sayımı yapıldı
    
-  Set ile benzersiz içerik çıkarıldı
    
-  Set yazdırma sırasının garanti edilmediği hatırlandı
    
-  `wc -l` komutunun newline saydığı öğrenildi
    
-  Boş satırların `wc -l` sonucuna dahil olduğu görüldü
    
-  `sort`, `uniq` ve `sort -u` rolleri ayrıldı
    
-  Python sonucu Linux araçlarıyla bağımsız doğrulandı
    
-  İki farklı aracın farklı tanım kullanabileceği kavrandı
    
-  Read-only bind mount ile program başarıyla çalıştırıldı
    
-  `readonly`, bind mount ve `-w` görevleri ayrıldı
    
-  RAM işlemleri ile filesystem yazma izinleri ayrıldı
    
-  Tek başarılı testin evrensel doğruluk kanıtı olmadığı kavrandı
    

> [!success] 🚀 Gün sonu sonucu  
> Gün 10 sonunda dosya okumak yalnızca `open()` çağırmak olarak değil, bir **kaynak yaşam döngüsü** olarak düşünülmeye başlandı.
> 
> Aynı zamanda test konusunda daha önemli bir refleks oluştu:
> 
> ```text
> İki sonuç farklıysa hemen “bug” deme.
> 
> Önce iki aracın gerçekten aynı şeyi ölçüp ölçmediğini kontrol et.
> ```
> 
> Python’ın boş olmayan satır sayısı ile Linux `wc -l` sonucunun farklı çıkması bunun doğrudan örneği oldu.