---
title: "Gün 14 — Testi Gerçekten Çalıştırmak, Permission Kanıtı ve COPY vs Bind Mount"
tags:
  - coreops
  - python
  - linux
  - docker
  - testing
  - assert
  - permissions
  - bind-mount
  - copy
aliases:
  - "Gün 14 Test Kanıtı Permission ve COPY Bind Mount"
status: completed
duration_minutes: 75
---

# 🧠 Gün 14 — Testi Gerçekten Çalıştırmak, Permission Kanıtı ve `COPY` vs Bind Mount

> [!abstract] 🎯 Ana fikir  
> Bugünün ortak teması **“kodda yazıyor” ile “gerçekte kanıtlandı” arasındaki fark** oldu.
> 
> ```text
> Test yazmak
> ≠
> Testi çalıştırmak
> ≠
> Testin geçmesi
> 
> chmod yazmak
> ≠
> İznin gerçekten değiştiğini doğrulamak
> 
> Image'da dosya bulunması
> ≠
> Runtime'da görünen dosyanın mutlaka image'dan gelmesi
> ```
> 
> Güçlü debugging modeli:
> 
> **Beklenti → Deney → Gerçek çıktı → Exit code → Açıklama**

---

# ⚡ 2 Dakikalık Geri Çağırma

Daha önce build edilmiş bir image:

```text
Host dosyası
   ↓ COPY
IMAGE
```

zinciriyle oluşturulmuşsa host dosyasının sonraki değişiklikleri image'a otomatik yansımaz.

Image artık build anındaki kendi filesystem durumunu taşır.

Bind mount ise runtime'da canlı host kaynağını gösterir.

---

# 🐍 Python — Testin Kodda Olması Yeterli Değildir

## `assert` nasıl çalışır?

```python
assert sonuc == beklenen
```

Koşul:

```text
True
→ Program devam eder.

False
→ AssertionError
```

Mantıksal olarak:

```python
if not koşul:
    raise AssertionError
```

Ancak dosyada bu satırın bulunması:

> **Assert'in gerçekten execute edildiğini kanıtlamaz.**

Kaynak görevde bu ayrım özellikle test edilmiş.

---

# 🧪 Test Kanıt Zinciri

Doğru akış:

```text
Test kodunu yaz
      ↓
Test dosyasını çalıştır
      ↓
Assert'ler execute edilir
      ↓
Assertion / exception oluşuyor mu?
      ↓
Process exit code'unu kontrol et
```

Görevde:

```bash
python day14test.py
echo $?
```

çalıştırıldı.

Sonuç:

```text
0
```

oldu.

Bunun verdiği ek kanıt:

```text
Test dosyası gerçekten çalıştırıldı ✅
Beklenmeyen exception oluşmadı ✅
AssertionError oluşmadı ✅
Process başarıyla tamamlandı ✅
```

---

> [!danger] Kafaya kazı
> 
> ```text
> Test dosyasında 10 assert görmek
> → Testlerin YAZILDIĞINI kanıtlar.
> 
> Testi çalıştırıp exit 0 görmek
> → O çalıştırmada testlerin BAŞARISIZ OLMADIĞINI kanıtlar.
> ```

---

# 📂 Boş Sonuç ile Geçersiz Root Aynı Değil

Fonksiyonun sözleşmesi:

## Root var ama `.txt` yok

```python
[]
```

Bu başarılı bir aramadır.

Anlamı:

> “Aramayı yaptım fakat eşleşme bulamadım.”

## Root hiç yok

```text
FileNotFoundError
```

Anlamı:

> “Aramayı başlatacağım yer mevcut değil.”

Bu iki duruma da:

```python
[]
```

dönmek bilgi kaybettirirdi.

---

# 🔎 `analayzer()` Fonksiyonunun Amacı

Kaynak fonksiyonun hedef davranışı:

```text
Root al
  ↓
Path nesnesine çevir
  ↓
Root var mı?
  ↓
Dizin mi?
  ↓
Recursive *.txt ara
  ↓
Normal dosyaları al
  ↓
Root'a göre relative path üret
  ↓
Deterministik liste döndür
```

---

# 🚨 Kaynak Koddaki İki Kritik Hata

Gerçek kaynak kodunda şu satırlar bulunuyor:

```python
if not root.is_dir:
```

ve:

```python
if x.is_file:
```

Bunlar metodun **kendisine** bakıyor.

Metodu çalıştırmak için parantez gerekir.

Doğru:

```python
if not root.is_dir():
    raise NotADirectoryError
```

ve:

```python
if x.is_file():
    ...
```

> [!danger] Neden sinsi?  
> Method object'leri truthy olduğu için kod bazı test verilerinde “çalışıyor gibi” görünebilir.
> 
> Yani:
> 
> ```text
> Test exit 0
> ```
> 
> görmek mevcut testlerin geçtiğini gösterir ama **test edilmemiş bir mantık hatasının bulunmadığını garanti etmez.**

Bu tam olarak test kapsamının neden önemli olduğunu gösteren güzel bir örnek.

---

# ✅ Düzeltilmiş Fonksiyon

```python
from pathlib import Path


def analyzer(root):
    root = Path(root)

    if not root.exists():
        raise FileNotFoundError

    if not root.is_dir():
        raise NotADirectoryError

    dosyalar = []

    for path in sorted(root.rglob("*.txt")):
        if path.is_file():
            dosyalar.append(
                path.relative_to(root)
            )

    return dosyalar
```

---

# 🔄 Deterministik Sonuç

```python
sorted(root.rglob("*.txt"))
```

kullanılması sonucu sabit sıraya getirir.

Bu özellikle:

```python
assert sonuc == [
    Path(...),
    Path(...),
]
```

gibi liste karşılaştırmalarında önemlidir.

Aksi halde aynı dosya kümesi farklı sırada dönerse test gereksiz yere patlayabilir.

---

# 🧪 Üç Temel Test Senaryosu

Kaynakta üç farklı sözleşme sınanmış.

## 1. Normal root

```python
sonuc = analyzer("gate13")

assert sonuc == [...]
```

Kontrol edilenler:

- Recursive arama
    
- `.txt` filtresi
    
- Relative path
    
- Beklenen dosyalar
    
- Sıra
    

---

## 2. Geçerli boş root

```python
sonuc = analyzer("boş_root")

assert sonuc == []
```

Burada hata beklenmez.

---

## 3. Olmayan root

```python
try:
    analyzer("olmayan_root")
    assert False

except FileNotFoundError:
    pass
```

`assert False` şunu söyler:

> “Beklediğim exception gelmedi ve program buraya ulaştıysa test başarısız olmalı.”

---

# 🧠 Testlerin Bize Söylediği Şey

Test kodu aslında fonksiyonun davranış sözleşmesini tarif ediyor:

```text
Normal root       → Liste
Boş root          → []
Olmayan root      → FileNotFoundError
Dizin olmayan root→ NotADirectoryError
```

> [!important]  
> İyi test yalnız “happy path” denemez.
> 
> En azından:
> 
> ```text
> Normal durum
> Sınır / boş durum
> Geçersiz durum
> ```
> 
> düşünülmelidir.

---

# 🐧 Linux — Permission Deneyinde Tahmin Değil Kanıt

Başlangıç dosyası:

```text
-rw-r--r--
```

Yani:

```text
644
```

Sonra:

```bash
chmod 244 day14.txt
```

uygulandı.

Gerçek çıktı:

```text
--w-r--r--
```

oldu.

---

# 🔢 `244` Nasıl Okunur?

```text
2 → -w-
4 → r--
4 → r--
```

Sonuç:

```text
owner  → -w-
group  → r--
others → r--
```

Owner read biti yok.

---

# 🔐 Neden `cat` Çalışmadı?

Dosyanın sahibi komutu çalıştırıyorsa kernel owner sınıfını kullanır:

```text
owner → -w-
```

Burada:

```text
r yok ❌
```

Dolayısıyla:

```bash
cat day14.txt
```

sonucu:

```text
Permission denied
```

oldu.

Exit code:

```text
1
```

çıktı.

---

# ♻️ Permission Geri Getirme

Sonra:

```bash
chmod 644 day14.txt
```

ile eski izin geri getirildi.

```bash
cat day14.txt
echo $?
```

sonucu:

```text
0
```

oldu.

Bu deney:

```text
Mode değişti
     ↓
Erişim davranışı değişti
     ↓
Mode eski hâline geldi
     ↓
Davranış tekrar düzeldi
```

zincirini gösterdi.

---

# 🔎 `chmod` ve `stat` Rolleri

```text
chmod
→ Dosyanın mode bilgisini DEĞİŞTİR.

stat
→ Dosyanın mevcut metadata/mode bilgisini ÖLÇ.
```

Örnek:

```bash
stat -c '%a %A' dosya.txt
```

Linux/GNU `stat` ortamında:

```text
644 -rw-r--r--
```

gibi sonuç verir.

> [!note]  
> macOS'taki `stat` seçenekleri GNU/Linux `stat` ile birebir aynı değildir; komut sözdizimini bulunduğun ortama göre düşün.

---

# 🚪 `$?` Neden Hemen Saklanmalı?

```bash
cat dosya.txt
rc=$?
```

çünkü:

```text
$?
→ En son çalışan komutun exit status'ü
```

Başka komut çalıştırırsan eski değer gider.

TIRT:

```bash
cat dosya.txt
echo "Kontrol ediyorum"
echo $?
```

Buradaki `$?`, artık `cat` değil `echo` sonucudur.

---

# ✅ Güvenilir Deney Modeli

```text
1. Başlangıç durumunu ölç
2. Eski değeri sakla
3. Tek bir şeyi değiştir
4. Tekrar ölç
5. Davranışı test et
6. Exit code'u sakla
7. Sonucu açıkla
8. Eski durumu geri getir
```

Bu yaklaşım deneyin tekrar üretilebilir olmasını sağlar.

---

# 🧩 Aynı Komutun Davranışını Açıklamak İçin Üç Bilgi

Örneğin:

```bash
cat dosya.txt
```

bir durumda çalışıyor, diğerinde çalışmıyorsa üç temel bilgi gerekir:

```text
1. Dosyanın mode / izin durumu
2. Process'in UID/GID + grup üyelikleri
3. Owner / group / others sınıflarından hangisi uygulanıyor?
```

Kaynak notta bu üçlü doğru şekilde çıkarılmış.

---

# 🐳 Docker — `COPY` vs Bind Mount

En önemli soru:

> **Container şu anda bu dosyayı nereden görüyor?**

İki ihtimal:

```text
IMAGE filesystem
veya
HOST bind mount
```

---

# 🏗️ `COPY` Ne Zaman Çalışır?

Dockerfile:

```dockerfile
COPY state.txt /app/state.txt
```

işlemi:

```text
BUILD-TIME
```

sırasında yapılır.

Akış:

```text
Host / Build Context
      state.txt
          ↓
        COPY
          ↓
        IMAGE
   /app/state.txt
```

Dosyanın build anındaki hâli image'a alınır.

---

# 🔗 Bind Mount Ne Zaman Çalışır?

Bind mount:

```bash
docker run \
  --mount type=bind,... \
  IMAGE
```

sırasında uygulanır.

Yani:

```text
RUNTIME
```

özelliğidir.

Akış:

```text
HOST
 ↕
CONTAINER
```

Image oluştururken host dosyasını image'a kopyalamaz.

---

# 🙈 Mount Image İçeriğinin Üzerine Gelirse?

Image içinde:

```text
/app/state.txt
→ BUILD_A
```

bulunsun.

Runtime sırasında host dizinini:

```text
/app
```

üzerine bind mount edersen:

```text
IMAGE /app
   ↓
GİZLENİR
----------------
BIND MOUNT /app
   ↓
HOST İÇERİĞİ
```

Container mount edilen host içeriğini görür.

Image'daki dosya:

- Silinmez.
    
- Değişmez.
    
- Yalnızca mount aktifken görünmez hâle gelir.
    

---

# 🧪 `BUILD_A → HOST_B` Deneyi

İlk host dosyası:

```text
state.txt = BUILD_A
```

Image build edildi:

```bash
docker build -t day14 .
```

Mountsuz çalıştırma:

```bash
docker run day14
```

çıktısı:

```text
BUILD_A
```

oldu.

---

# ✏️ Host Dosyası Değiştirildi

Sonra host:

```text
state.txt = HOST_B
```

yapıldı.

Ama aynı eski image:

```bash
docker run day14
```

ile tekrar çalıştırılınca:

```text
BUILD_A
```

görmeye devam etti.

Neden?

```text
Container'ın kaynağı
→ Eski IMAGE

Host state.txt
→ Artık image ile canlı bağlı değil
```

---

# 🔥 Aynı Eski Image + Bind Mount

Bu sefer runtime'da host klasörü bağlandı.

Program:

```text
HOST_B
```

gördü.

Çünkü veri kaynağı değişti:

```text
Önce:
IMAGE / state.txt

Şimdi:
HOST / bind mount / state.txt
```

Image aynı olabilir.

**Görünen filesystem kaynağı farklıdır.**

---

# 🔄 Rebuild Sonrası

Hostta hâlâ:

```text
HOST_B
```

varken:

```bash
docker build -t day14 .
```

tekrar yapıldı.

Sonrasında mountsuz:

```bash
docker run day14
```

çıktısı:

```text
HOST_B
```

oldu.

Çünkü yeni build:

```text
HOST_B
↓
COPY
↓
Yeni IMAGE
```

oluşturdu.

---

# 🎯 Üç Senaryoyu Tek Tabloda Gör

|Durum|Dosyanın kaynağı|Görülen|
|---|---|---|
|Eski image + mount yok|Image|`BUILD_A`|
|Eski image + bind mount|Host|`HOST_B`|
|Rebuild + mount yok|Yeni image|`HOST_B`|

---

# 🧠 Asıl Soru

Docker'da bir dosyanın içeriği şaşırtıcı görünüyorsa ilk soru:

> **Bu dosya şu anda image filesystem'inden mi geliyor, yoksa runtime mount tarafından mı sağlanıyor?**

Bu soruyu çözmeden:

```text
Docker cache bozuk
COPY çalışmadı
Container yanlış
```

demek TIRT debugging olur.

---

# 🧯 Hata Avı

## 1. Test dosyasında `assert` varsa test geçmiştir

TIRT.

Dosyanın gerçekten çalıştırılması gerekir.

---

## 2. Exit `0` bütün olası davranışların doğru olduğunu kanıtlar

TIRT.

Yalnızca **çalıştırılan test senaryolarının** başarısız olmadığını kanıtlar.

---

## 3. Kaynak koddaki `root.is_dir` doğrudur

TIRT.

Metot çağrısı gerekir:

```python
root.is_dir()
```

---

## 4. `x.is_file` gerçek dosya kontrolü yapar

TIRT.

Doğru:

```python
x.is_file()
```

---

## 5. Boş root ile olmayan root aynı sonucu vermelidir

TIRT.

```text
Boş root    → []
Olmayan root→ FileNotFoundError
```

---

## 6. `chmod` yaptıysam mode kesin değişmiştir

TIRT.

Ölç:

```bash
stat ...
```

veya uygun ortamda:

```bash
ls -l
```

---

## 7. `$?` istediğim eski komutun sonucunu tutar

TIRT.

Yalnız **en son komutu** tutar.

---

## 8. `244` iken owner group read iznini kullanabilir

TIRT.

Owner eşleşiyorsa owner üçlüsü seçilir:

```text
-w-
```

Group ve others ile birleştirme yapılmaz.

---

## 9. Host dosyası değişirse eski image değişir

TIRT.

`COPY` canlı bağlantı değildir.

---

## 10. Bind mount image içeriğini siler

TIRT.

İçeriği yalnızca mount aktifken gizler.

---

## 11. Aynı image her çalıştırmada aynı dosyayı görmek zorundadır

TIRT.

Runtime mount'ları farklıysa aynı image farklı içerik görebilir.

---

# 🧠 Kafaya Kazı

> [!quote]  
> Test kodunun bulunması, testin çalıştırıldığı anlamına gelmez.

> [!quote]  
> `assert False` beklenen exception gelmezse testi bilinçli olarak patlatabilir.

> [!quote]  
> Exit code test çalıştırmasının makine tarafından okunabilir sonucudur.

> [!quote]  
> `is_dir()` ve `is_file()` metotlardır; çağırmak için `()` gerekir.

> [!quote]  
> Boş sonuç hata değildir; geçersiz root hatadır.

> [!quote]  
> Permission debugging beklenti değil ölçüm işidir.

> [!quote]  
> `chmod` değiştirir, `stat` doğrular.

> [!quote]  
> `$?` yalnızca en son komutun sonucudur.

> [!quote]  
> Permission sonucu = mode + process kimliği + seçilen izin sınıfı.

> [!quote]  
> `COPY` build-time'dır.

> [!quote]  
> Bind mount runtime'dır.

> [!quote]  
> Bind mount, image içeriğini değiştirmeden üstünü gizleyebilir.

> [!quote]  
> Eski image + mount yok → eski snapshot.

> [!quote]  
> Eski image + bind mount → güncel host içeriği.

> [!quote]  
> Rebuild → güncel host içeriğini yeni image snapshot'ına alır.

---

# 📌 30 Saniyelik Özet

```text
PYTHON TEST
assert False          → AssertionError
test yazmak           ≠ test çalıştırmak
python test.py        → Testi gerçekten execute et
echo $?               → Process sonucunu doğrula

PATH
exists()              → Var mı?
is_dir()              → Dizin mi?
is_file()             → Dosya mı?
rglob()               → Recursive ara
relative_to()         → Relative path
sorted()              → Deterministik sıra

SÖZLEŞME
Geçerli boş root      → []
Olmayan root          → FileNotFoundError

LINUX
chmod                 → Mode'u değiştir
stat / ls -l          → Gerçek mode'u gözle
cat                   → Erişimi dene
$?                    → Exit status
644                    → rw-r--r--
244                    → -w-r--r--

DOCKER
COPY                  → Build-time snapshot
Bind mount            → Runtime host bağlantısı
Mount aynı path'e     → Image içeriğini gizler

BUILD_A / HOST_B
Eski image mountsuz   → BUILD_A
Eski image + mount    → HOST_B
Rebuild mountsuz      → HOST_B
```

---

# ✅ Günün Kazanımları

-  Test yazmak ile test çalıştırmak ayrıldı
    
-  `assert` başarısızlığının `AssertionError` ürettiği öğrenildi
    
-  Test sonucu exit code ile doğrulandı
    
-  Testlerin normal / boş / hata senaryolarını kapsaması uygulandı
    
-  Boş sonuç ile geçersiz root ayrıldı
    
-  Deterministik recursive dosya listesi test edildi
    
-  Kaynak koddaki `is_dir` / `is_file` parantez hatası fark edildi
    
-  Test geçmesinin test kapsamı dışındaki bug'ları dışlamadığı görüldü
    
-  `chmod 244` ile owner read biti kaldırıldı
    
-  `Permission denied` gerçek deneyle gözlemlendi
    
-  Exit `1` ile permission başarısızlığı doğrulandı
    
-  `chmod 644` ile başlangıç durumu geri getirildi
    
-  `$?` değerinin neden hemen saklanması gerektiği öğrenildi
    
-  Permission debugging için gerekli üç kanıt netleştirildi
    
-  `COPY` build-time ile bind mount runtime ayrıldı
    
-  Eski image'ın host değişikliğini görmediği doğrulandı
    
-  Bind mount'un image path'ini gizleyebildiği görüldü
    
-  Aynı image'ın farklı mount ayarlarıyla farklı içerik görebildiği doğrulandı
    
-  Rebuild sonrası yeni host içeriğinin image'a girdiği deneyle kanıtlandı
    

> [!success] 🚀 Gün sonu sonucu  
> Gün 14'ün ortak dersi **kanıt üretmek** oldu.
> 
> ```text
> Kodda test var mı?
> → Yetmez.
> 
> Test çalıştı mı?
> → Exit code ile kanıtla.
> 
> chmod yaptım mı?
> → Yetmez.
> 
> Mode gerçekten değişti mi?
> → Ölç.
> 
> Container bir dosya görüyor mu?
> → Yetmez.
> 
> Dosya IMAGE'dan mı geliyor,
> yoksa BIND MOUNT'tan mı?
> → Kaynağı belirle.
> ```
> 
> Günün en kritik modeli:
> 
> **Aynı kod veya aynı image, çevresindeki runtime koşulları değiştiğinde farklı davranabilir; doğru debugging bunun nedenini varsayımla değil, gözlemlenebilir kanıtlarla ayırmaktır.**
