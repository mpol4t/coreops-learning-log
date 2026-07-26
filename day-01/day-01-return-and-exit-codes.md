---
title: "Gün 01 — Şartname, return, Exit Code ve Docker Temeli"
tags:
  - coreops
  - python
  - linux
  - docker
  - return
  - exit-code
  - specification
aliases:
  - "Gün 1 Return Exit Code Docker Temeli"
status: completed
---

# 🧠 Gün 1 — Şartname, `return`, Exit Code ve Docker Temeli

> [!abstract] 🎯 Ana fikir
> Bir kodun yalnızca çalışması yeterli değildir.
>
> Kod:
>
> - Yazılı şartnameye uymalı,
>
> - Doğru değeri döndürmeli,
>
> - Hatalı girdilerde beklenen davranışı göstermeli,
>
> - İşletim sistemine doğru başarı veya hata durumunu bildirmelidir.
>

---

# ⚡ 2 Dakikalık Geri Çağırma

## `print()` ne yapar?

Bir değeri ekrana yazar.

```python
print("Merhaba")
```

Çıktı:

```text
Merhaba
```

Ancak değeri fonksiyonun dışına göndermez.

---

## `return` ne yapar?

Fonksiyonun ürettiği değeri çağrıldığı yere gönderir.

```python
def topla(a, b):
    return a + b


sonuc = topla(3, 5)
print(sonuc)
```

Çıktı:

```text
8
```

---

## Açıkça değer döndürmeyen fonksiyon ne döndürür?

```python
None
```

```python
def selamla():
    print("Selam")


sonuc = selamla()
print(sonuc)
```

Çıktı:

```text
Selam
None
```

> [!important] Kafaya kazı
> `print()` ekrana yazar.
>
> `return` çağrıldığı yere değer gönderir.
>
> Bunlar aynı şey değildir.

---

# 🐍 Python — `return`, `print()` ve `None`

## `print()` ile `return` farkı

```python
def yanlış_topla(a, b):
    print(a + b)
```

Bu fonksiyon sonucu ekrana yazar fakat dışarıya değer döndürmez:

```python
sonuc = yanlış_topla(2, 3)

print(sonuc)
```

Çıktı:

```text
5
None
```

Doğru yaklaşım:

```python
def topla(a, b):
    return a + b


sonuc = topla(2, 3)
print(sonuc)
```

Çıktı:

```text
5
```

|Kavram|Görevi|
|---|---|
|`print()`|Kullanıcıya veya terminale çıktı gösterir|
|`return`|Fonksiyonun sonucunu dışarı gönderir|
|`None`|Değer bulunmadığını ifade eden özel Python nesnesidir|

---

## `return` çalışınca ne olur?

Fonksiyon, `return` satırına ulaştığı anda sona erer.

```python
def kontrol_et(sayi):
    return sayi * 2

    print("Bu satır çalışmaz.")
```

`return` sonrasındaki satır erişilemez durumdadır.

---

## Bir fonksiyonda birden fazla `return`

Bir fonksiyonda birden fazla `return` bulunabilir:

```python
def sayi_durumu(sayi):
    if sayi > 0:
        return "pozitif"

    if sayi < 0:
        return "negatif"

    return "sıfır"
```

Ancak tek fonksiyon çağrısında yalnızca ulaşılan ilk `return` çalışır.

```python
sayi_durumu(5)
```

Akış:

```text
5 > 0 doğru
      ↓
"pozitif" döndürülür
      ↓
fonksiyon sona erer
```

---

## `None` hata mıdır?

Hayır.

Bir fonksiyonun `None` döndürmesi tek başına hata değildir.

```python
def kayit_yaz():
    print("Kayıt oluşturuldu.")
```

Bu fonksiyon açıkça değer döndürmediği için otomatik olarak `None` döndürür.

Problem, fonksiyondan bir değer beklediğimiz hâlde yanlışlıkla `None` almamızdır.

```python
sonuc = kayit_yaz()

print(sonuc + 10)
```

Bu durumda hata oluşur çünkü `None` ile sayı toplanamaz.

---

# 🧩 Parametre ve Argüman

## Parametre

Fonksiyon tanımında bulunan değişkendir.

```python
def kargo_ucreti(sepet_tutari):
    pass
```

Buradaki:

```python
sepet_tutari
```

bir **parametredir**.

---

## Argüman

Fonksiyon çağrılırken parametreye gönderilen gerçek değerdir.

```python
kargo_ucreti(500)
```

Buradaki:

```python
500
```

bir **argümandır**.

---

## Zihinsel model

```text
Fonksiyon tanımı:

def kargo_ucreti(sepet_tutari):
                    ↑
                 parametre


Fonksiyon çağrısı:

kargo_ucreti(500)
               ↑
            argüman
```

> [!tip]
> Parametre, fonksiyonun beklediği değişkenin adıdır.
>
> Argüman, fonksiyona gerçekten verilen değerdir.

---

# 📋 Şartname Mantığı

Kod yazmadan önce fonksiyonun davranışı açıkça tanımlanmalıdır.

## Sorulması gereken sorular

1. Fonksiyonun amacı nedir?

2. Hangi girdiler geçerlidir?

3. Hangi girdiler geçersizdir?

4. Sınır değerleri nelerdir?

5. Fonksiyon ne döndürmelidir?

6. Dönüş tipi ne olmalıdır?

7. Hatalı girdide ne yapılmalıdır?

8. Hangi exception kullanılmalıdır?


---

> [!danger] Ana ders
> Kodun çalışması, doğru olduğu anlamına gelmez.
>
> Kod ancak yazılı şartnameyle aynı davranışı gösteriyorsa doğrudur.

---

## Şartname örneği

### Fonksiyon

```text
kargo_ucreti
```

### Amaç

Sepet tutarına göre müşterinin ödeyeceği toplam tutarı hesaplamak.

### Geçerli girdiler

```text
0 ve daha büyük sayılar
```

### Geçersiz girdiler

```text
Negatif sayılar
```

### Sınır değerleri

```text
-1
0
499.99
500
```

### Beklenen dönüş tipi

```python
float
```

### Hata davranışı

Negatif değer girildiğinde:

```python
ValueError
```

fırlatılmalıdır.

---

# 📦 `kargo_ucreti()` Fonksiyonu

## Son şartname

|Sepet tutarı|Davranış|
|--:|---|
|Negatif|`ValueError`|
|`0 <= tutar < 500`|`49.90` kargo eklenir|
|`tutar >= 500`|Ücretsiz kargo|
|Başarılı sonuç|`float` döner|

---

## Temizlenmiş kod

```python
def kargo_ucreti(sepet_tutari):
    if sepet_tutari < 0:
        raise ValueError(
            "Sepet tutarı negatif olamaz."
        )

    if sepet_tutari < 500:
        return float(sepet_tutari + 49.90)

    return float(sepet_tutari)
```

---

## Doğrulanan sınırlar

```python
kargo_ucreti(0)
```

Sonuç:

```python
49.9
```

---

```python
kargo_ucreti(500)
```

Sonuç:

```python
500.0
```

---

```python
kargo_ucreti(-1)
```

Sonuç:

```text
ValueError
```

---

## İlk hatam

İlk kontrolde:

```python
if sepet_tutari <= 0:
    raise ValueError
```

kullanılmıştı.

Bu şart:

```text
Negatif sayıları reddeder.
Sıfırı da reddeder.
```

Fakat şartnameye göre:

```text
0 geçerli bir sepet tutarıdır.
```

Bu yüzden doğru koşul:

```python
if sepet_tutari < 0:
```

olmalıdır.

---

> [!warning] Sınır hatası
> `<` ile `<=` arasındaki tek karakterlik fark, şartnamenin tamamen bozulmasına neden olabilir.

---

# 🧪 Sınır Değeri Testleri

Bir sınır test edilirken yalnızca sınırın kendisi kontrol edilmemelidir.

`500` sınırı için:

```text
499.99 → sınırın hemen altı
500    → sınır
500.01 → sınırın hemen üstü
```

Örnek testler:

```python
assert kargo_ucreti(0) == 49.90
assert kargo_ucreti(499.99) == 549.89
assert kargo_ucreti(500) == 500.0
assert kargo_ucreti(500.01) == 500.01
```

> [!tip] Ek not
> Ondalıklı para işlemlerinde gerçek projelerde `float` hassasiyet sorunları oluşturabilir.
>
> Bu görevde şartname `float` istediği için `float` kullanıldı. Finansal uygulamalarda çoğunlukla `Decimal` tercih edilir.

---

# 🐧 Linux — `stdout`, `stderr` ve Exit Code

Bir process çalıştığında üç temel çıktı kanalı bulunur:

|Kanal|Anlam|
|---|---|
|`stdin`|Programa giren veri|
|`stdout`|Normal çıktı|
|`stderr`|Hata ve teşhis çıktısı|

---

## `stdout`

Programın normal çıktısıdır.

```bash
echo "Merhaba"
```

Çıktı:

```text
Merhaba
```

---

## `stderr`

Hata veya teşhis mesajlarının gönderildiği kanaldır.

```bash
cat olmayan_dosya.txt
```

Muhtemel çıktı:

```text
cat: olmayan_dosya.txt: No such file or directory
```

Bu mesaj normal çıktıdan ayrı olarak `stderr` kanalına gönderilir.

---

# 🚦 Exit Code

Her process sona erdiğinde işletim sistemine sayısal bir durum kodu döndürür.

Genel kural:

|Exit code|Anlam|
|--:|---|
|`0`|Başarı|
|`0` dışı|Hata veya başarısızlık|

Son çalışan komutun exit code’unu görmek için:

```bash
echo $?
```

---

## Başarılı komut

```bash
cat mevcut_dosya.txt
echo $?
```

Dosya okunabiliyorsa:

```text
0
```

---

## Başarısız komut

```bash
cat olmayan_dosya.txt
echo $?
```

Sonuç sıfır dışında bir değer olur.

Genellikle:

```text
1
```

görülebilir.

---

## `$?` neyi tutar?

`$?`, yalnızca **hemen önce tamamlanan komutun** exit code’unu tutar.

```bash
cat olmayan_dosya.txt
echo "Araya başka komut girdi"
echo $?
```

Son `echo $?`, artık `cat` komutunun değil:

```bash
echo "Araya başka komut girdi"
```

komutunun exit code’unu gösterir.

Doğru kullanım:

```bash
cat olmayan_dosya.txt
echo $?
```

---

> [!danger] Kafaya kazı
> Exit code’u görmek istiyorsan `echo $?` komutunu test ettiğin komuttan hemen sonra çalıştır.

---

## Exit code tek başına yeterli midir?

Hayır.

Exit code:

```text
Başarılı mı?
Başarısız mı?
```

sorusuna cevap verir.

Ancak hatanın nedenini tam olarak anlamak için:

- Hata mesajı,

- `stderr`,

- Loglar,

- Komutun bağlamı


da incelenmelidir.

```text
Exit code → Hata var mı?
Hata mesajı → Hata neden oldu?
```

---

# 🐳 Docker — Image ve Container

## Image nedir?

Image, container oluşturmak için kullanılan salt okunur çalışma şablonudur.

İçinde şunlar bulunabilir:

- İşletim sistemi katmanları,

- Programlama dili,

- Kütüphaneler,

- Uygulama dosyaları,

- Varsayılan komutlar.


Örnek image:

```text
python:3.12-slim
```

---

## Container nedir?

Container, bir image’dan oluşturulan çalışan örnektir.

```text
IMAGE
  │
  ├── Container 1
  ├── Container 2
  └── Container 3
```

Aynı image’dan birden fazla container oluşturulabilir.

---

## Image ve container farkı

|Image|Container|
|---|---|
|Şablondur|Çalışan örnektir|
|Salt okunur katmanlardan oluşur|Çalışma sırasında değişebilir|
|Birden fazla container üretebilir|Belirli bir image’dan oluşturulur|
|Container silinse de kalabilir|Silindiğinde container kaydı gider|

---

## Image yerelde yoksa ne olur?

```bash
docker run hello-world
```

Docker önce image’ın yerelde bulunup bulunmadığını kontrol eder.

Bulamazsa gerekli image’ı registry’den çekebilir:

```text
Yerel image var mı?
        │
        ├── Evet → Container oluştur
        │
        └── Hayır → Registry’den çek → Container oluştur
```

---

# 🗑️ `--rm` Nedir?

```bash
docker run --rm hello-world
```

`--rm`, container’ın ana process’i tamamlandıktan sonra container nesnesini otomatik siler.

Böylece durmuş container kayıtları gereksiz yere birikmez.

> [!warning]
> `--rm` image’ı silmez.
>
> Yalnızca oluşturulan container’ı kaldırır.

---

# 🛠️ Temel Docker Komutları

## Container çalıştırmak

```bash
docker run --rm hello-world
```

---

## Yerel image’ları listelemek

```bash
docker image ls
```

---

## Çalışan container’ları listelemek

```bash
docker ps
```

---

## Durmuş container’lar dahil bütün container’ları listelemek

```bash
docker ps -a
```

---

## `--rm` davranışını gözlemlemek

```bash
docker run --rm hello-world
docker ps -a
```

Container tamamlandıktan sonra listede görünmüyorsa `--rm` tarafından silinmiştir.

Image ise hâlâ görülebilir:

```bash
docker image ls
```

---

# 🔀 Python Return Değeri ve Process Exit Code

Fonksiyonun döndürdüğü değer ile işletim sisteminin gördüğü exit code farklı kavramlardır.

## Fonksiyonun `None` döndürmesi

```python
def yazdir():
    print("Çalıştı")


yazdir()
```

Fonksiyon:

```python
None
```

döndürür.

Ancak programda yakalanmamış bir hata olmadığı için process başarıyla tamamlanabilir.

Shell:

```bash
python program.py
echo $?
```

sonucunda:

```text
0
```

görebilir.

---

## Yakalanmamış exception

```python
raise ValueError("Geçersiz değer")
```

Exception yakalanmazsa Python programı genellikle sıfır dışı exit code ile sona erer.

```bash
python program.py
echo $?
```

Muhtemel sonuç:

```text
1
```

---

## Yakalanan exception

```python
try:
    raise ValueError("Geçersiz değer")
except ValueError as hata:
    print("Hata yakalandı:", hata)
```

Exception yakalandığı ve program normal şekilde tamamlandığı için exit code tekrar:

```text
0
```

olabilir.

> [!important] Ek not
> Exception’ı yakalamak, olayın gerçekten başarılı olduğu anlamına gelmez.
>
> Program hatayı yakalayıp kendisi sıfır dışı bir kodla çıkabilir:

```python
import sys

try:
    raise ValueError("Geçersiz değer")
except ValueError as hata:
    print(hata)
    sys.exit(1)
```

---

# 🧭 Kavramların Birbirinden Ayrılması

|Kavram|Cevapladığı soru|
|---|---|
|`print()`|Ekranda ne gösterilecek?|
|`return`|Fonksiyon hangi değeri üretti?|
|`None`|Fonksiyon anlamlı bir değer döndürdü mü?|
|Exception|Programda olağan dışı durum oluştu mu?|
|Exit code|Process başarılı mı tamamlandı?|
|`stderr`|Hata hakkında hangi mesaj üretildi?|
|Docker image|Container hangi şablondan oluşacak?|
|Docker container|Hangi çalışan örnek oluşturuldu?|

---

# 🧯 Hata Avı

## 1. `print()` ile `return` karıştırıldı

TIRT.

```python
def topla(a, b):
    print(a + b)
```

Bu fonksiyon hesaplama sonucunu dışarı döndürmez.

Doğrusu:

```python
def topla(a, b):
    return a + b
```

---

## 2. Sıfır geçersiz kabul edildi

Şartname:

```text
Negatif değerler geçersizdir.
```

Kod:

```python
if sepet_tutari <= 0:
```

Bu kod sıfırı da reddeder ve şartnameyi bozar.

Doğrusu:

```python
if sepet_tutari < 0:
```

---

## 3. `None` doğrudan hata sanıldı

`None`, Python’daki geçerli bir değerdir.

Problem yalnızca kodun bir sayı, string veya başka sonuç beklediği yerde `None` almasıdır.

---

## 4. Exit code hata nedeni sanıldı

Exit code hatanın varlığını bildirir, nedenini her zaman açıklamaz.

Hatanın nedenini anlamak için hata mesajı ve bağlam incelenmelidir.

---

## 5. `--rm` image’ı siler sanıldı

`--rm` image’ı değil, process tamamlandıktan sonra container nesnesini siler.

---

# 🧠 Kafaya Kazı

> [!quote]
> `print()` gösterir, `return` değer gönderir.

> [!quote]
> Açıkça değer döndürmeyen fonksiyon `None` döndürür.

> [!quote]
> `return` çalıştığı anda fonksiyon sona erer.

> [!quote]
> Parametre tanımda, argüman çağrıda bulunur.

> [!quote]
> Kodun çalışması yetmez; şartnameye uyması gerekir.

> [!quote]
> Sınır değerlerinde `<` ve `<=` farkı kritiktir.

> [!quote]
> Exit code `0` başarı, sıfır dışı değer genellikle başarısızlıktır.

> [!quote]
> `$?` yalnızca son çalışan komutun exit code’unu tutar.

> [!quote]
> Image şablondur, container çalışan örnektir.

> [!quote]
> `--rm` container’ı siler, image’ı değil.

> [!quote]
> Fonksiyon return değeri ile process exit code’u aynı şey değildir.

---

# 🎓 Mini Sınav

## 1. Aşağıdaki fonksiyon ne döndürür?

```python
def mesaj():
    print("Merhaba")
```

```python
None
```

`"Merhaba"` yalnızca ekrana yazılır.

---

## 2. Aşağıdaki kodda `500` nedir?

```python
kargo_ucreti(500)
```

`500` bir argümandır.

---

## 3. Negatif değerler geçersiz, sıfır geçerliyse hangi koşul kullanılmalıdır?

```python
sepet_tutari < 0
```

---

## 4. `echo $?` neyi gösterir?

Hemen önce tamamlanan komutun exit code’unu gösterir.

---

## 5. Fonksiyon `None` döndürürse process kesin başarısız mıdır?

Hayır.

Program hatasız tamamlandıysa process exit code `0` olabilir.

---

## 6. `docker run --rm` neyi otomatik siler?

Ana process sona erdikten sonra oluşturulan container nesnesini siler.

Image’ı silmez.

---

# 📌 30 Saniyelik Özet

```text
PYTHON
print()       → ekrana yazar
return        → değer döndürür
return çalışır → fonksiyon biter
return yok     → None döner

FONKSİYON
parametre → tanımda
argüman   → çağrıda

ŞARTNAME
amaç
geçerli girdiler
geçersiz girdiler
sınırlar
dönüş değeri
dönüş tipi
hata davranışı

KARGO
tutar < 0     → ValueError
0–499.99      → 49.90 ekle
500 ve üzeri  → ücretsiz
sonuç         → float

LINUX
stdout  → normal çıktı
stderr  → hata çıktısı
0       → başarı
0 dışı  → başarısızlık
$?      → son komutun exit code’u

DOCKER
image      → şablon
container  → çalışan örnek
--rm       → biten container’ı siler
docker ps  → çalışan container’lar
docker ps -a → bütün container’lar
docker image ls → image’lar
```

---

# ✅ Günün Ana Kazanımları

-  `return` ile `print()` ayrıldı

-  `None` davranışı anlaşıldı

-  Parametre ve argüman ayrımı yapıldı

-  Fonksiyon şartnamesi yazıldı

-  Geçerli ve geçersiz girdiler belirlendi

-  Sınır değerleri test edildi

-  Şartname-kod çelişkisi bulundu

-  `<= 0` hatası `< 0` olarak düzeltildi

-  `stdout`, `stderr` ve exit code ayrıldı

-  `$?` davranışı uygulandı

-  Docker image ve container ayrımı yapıldı

-  `--rm` davranışı gözlemlendi

-  Fonksiyon dönüş değeri ile process exit code’u ayrıldı


---

> [!success] 🚀 Gün sonu sonucu
> Gün 1 sonunda yalnızca çalışan bir fonksiyon yazılmadı.
>
> Fonksiyonun şartnamesi oluşturuldu, sınırları test edildi, hata davranışı belirlendi ve aynı kodun işletim sistemi seviyesinde nasıl başarı veya başarısızlık ürettiği öğrenildi.
