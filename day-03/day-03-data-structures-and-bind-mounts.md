---
title: "Day 03 — List, Dictionary, Set ve Docker Bind Mount"
tags:
  - coreops
  - python
  - linux
  - docker
  - data-structures
  - bind-mount
  - debugging
aliases:
  - "Day 03 Veri Yapıları ve Bind Mount"
status: completed
duration: "100–110 dakika"
---

# 🧠 Day 03 — List, Dictionary, Set ve Docker Bind Mount

> [!abstract] 🎯 Ana fikir
> Aynı ham veri, farklı amaçlarla kullanılacaksa tek bir veri yapısına zorlanmamalıdır.
>
> Bu görevde:
>
> - Sıralı ve tekrarlı geçmiş için → `list`
>
> - Servis ile son durumu eşlemek için → `dict`
>
> - Tekrarsız hata isimleri için → `set`
>
>
> kullandım.
>
> Ardından aynı Python dosyasını hem hostta hem container içinde çalıştırarak sonuçları `diff` ile karşılaştırdım.

---

# ⚡ 2 Dakikalık Geri Çağırma

## Kaç komut çalışacak?

```text
Toplam 3 komut
```

## Kaç satır çıktı oluşacak?

```text
Toplam 3 satır
```

## `\` karakterinden sonra boşluk koyulursa ne olur?

Shell’de satır devamı için ters bölü işaretinin:

```bash
\
```

satırdaki **son karakter** olması gerekir.

Doğru:

```bash
docker run \
  --rm \
  python:3.12-slim
```

TIRT kullanım:

```bash
docker run \
  --rm
```

Burada `\` karakterinden sonra boşluk bulunduğu için newline kaçırılamaz. İlk satır ayrı bir komut gibi çalıştırılabilir ve alt satır yeni bir komut olarak yorumlanabilir.

> [!danger] Kafaya kazı
> Satır devamında `\` karakterinden sonra görünmeyen boşluk bile bulunmamalıdır.

---

# 🐍 Python — Doğru Veri Yapısını Seçmek

## 📋 List

Liste:

- Sıralıdır.

- Tekrarlı eleman tutabilir.

- İndeks ile erişilebilir.

- Değiştirilebilir.


```python
servisler = ["nginx", "redis", "nginx"]
```

Burada iki farklı `"nginx"` kaydı korunur.

### Sık kullanılan metotlar

|Metot|Görevi|
|---|---|
|`append(x)`|Tek bir elemanı listenin sonuna ekler|
|`extend(iterable)`|Iterable içindeki bütün elemanları ekler|
|`insert(i, x)`|Belirtilen indekse eleman ekler|
|`remove(x)`|İlk eşleşen değeri siler|
|`pop(i)`|Elemanı siler ve döndürür|
|`clear()`|Listeyi temizler|
|`index(x)`|Değerin ilk indeksini döndürür|
|`count(x)`|Değerin kaç kez bulunduğunu döndürür|
|`sort()`|Listeyi yerinde sıralar|
|`reverse()`|Listeyi yerinde ters çevirir|
|`copy()`|Yüzeysel kopya oluşturur|

---

## 🟢 Set

Set:

- Tekrarlı eleman tutmaz.

- İndeksle erişilemez.

- Eleman sırasına güvenilmez.

- Benzersizlik ve üyelik kontrolü için uygundur.


```python
başarısız_servisler = {"nginx", "redis"}
```

Aynı eleman yeniden eklense bile bir kez bulunur:

```python
başarısız_servisler.add("nginx")
başarısız_servisler.add("nginx")
```

Sonuç mantıksal olarak:

```python
{"nginx"}
```

olur.

### Sık kullanılan metotlar

|Metot|Görevi|
|---|---|
|`add(x)`|Tek eleman ekler|
|`update(iterable)`|Birden fazla eleman ekler|
|`remove(x)`|Elemanı siler, yoksa hata verir|
|`discard(x)`|Elemanı siler, yoksa hata vermez|
|`pop()`|Bir elemanı siler ve döndürür|
|`clear()`|Seti temizler|

### Set operatörleri

|Operatör|Anlam|
|---|---|
|`a \| b`|Birleşim|
|`a & b`|Kesişim|
|`a - b`|Fark|
|`a ^ b`|Simetrik fark|

---

## 📖 Dictionary

Dictionary, anahtar-değer ilişkisi tutar.

```python
son_durum = {
    "nginx": "fail",
    "redis": "ok"
}
```

### Temel işlemler

```python
son_durum["nginx"]
```

Bir anahtar ekleme veya güncelleme:

```python
son_durum["nginx"] = "ok"
```

Güvenli okuma:

```python
son_durum.get("mysql")
```

Anahtar yoksa `get()` varsayılan olarak:

```python
None
```

döndürür.

---

## Dictionary anahtarları neden benzersizdir?

Dictionary, her anahtarı tek bir değerle eşleyen bir yapıdır.

```python
son_durum["nginx"] = "ok"
son_durum["nginx"] = "fail"
```

İkinci atama yeni bir `"nginx"` anahtarı oluşturmaz. Mevcut anahtarın değerini günceller:

```python
{"nginx": "fail"}
```

> [!warning] Düzeltilen yorum
> Dictionary anahtarları yalnızca “karmaşıklığı önlemek” veya primary key gibi davranmak için benzersiz değildir.
>
> Dictionary’nin temel veri modeli zaten:
>
> ```text
> Bir anahtar → Bir mevcut değer
> ```
>
> ilişkisidir.

---

# 🆚 `list.append()` ve `set.add()`

İkisi de eleman ekler ancak aynı davranışı göstermez.

## `list.append()`

```python
servisler = []

servisler.append("nginx")
servisler.append("nginx")
```

Sonuç:

```python
["nginx", "nginx"]
```

- Tekrar korunur.

- Eleman listenin sonuna eklenir.

- Ekleme sırası korunur.


## `set.add()`

```python
servisler = set()

servisler.add("nginx")
servisler.add("nginx")
```

Sonuç:

```python
{"nginx"}
```

- Tekrar kaldırılır.

- Sona ekleme kavramı yoktur.

- Görünen sıraya güvenilemez.


---

# 🔄 Listeden Set Oluşturmak

```python
servisler = ["nginx", "redis", "nginx"]

benzersiz_servisler = set(servisler)
```

Sonuç mantıksal olarak:

```python
{"nginx", "redis"}
```

Bu dönüşüm sırasında iki bilgi kaybolabilir:

1. Tekrar sayısı

2. Orijinal sıra


Örneğin aşağıdaki iki liste aynı sete dönüşebilir:

```python
["nginx", "redis", "nginx"]
["redis", "nginx"]
```

---

# 🧭 Hangi Durumda Hangi Veri Yapısı?

|İhtiyaç|Veri yapısı|Sebep|
|---|---|---|
|Komutların çalıştırılma sırası|`list`|Sıra ve tekrar korunur|
|Servis adı → servis durumu|`dict`|Anahtar-değer ilişkisi gerekir|
|Benzersiz başarısız servis adları|`set`|Tekrarlar gereksizdir|
|Dosyadaki bütün hata kayıtları|`list`|Tekrarlar ve sıra korunmalıdır|

> [!important] Soru
> “Bu veri nedir?” diye değil, “Bu veride hangi bilgiyi korumam gerekiyor?” diye düşün.

---

# 🔥 Tuple Unpacking

Elimizde şu tuple olsun:

```python
("nginx", "fail")
```

İndeksle erişilebilir:

```python
x[0]
x[1]
```

Ancak daha okunabilir yöntem tuple unpacking kullanmaktır:

```python
servis, durum = x
```

Bu işlem zihinsel olarak şuna eşittir:

```python
servis = "nginx"
durum = "fail"
```

Döngünün içinde doğrudan da unpack edilebilir:

```python
for servis, durum in kayıtlar:
    print(servis, durum)
```

Bu kullanım:

```python
for x in kayıtlar:
    servis, durum = x
```

ile aynı mantıktadır ancak daha kısadır.

---

# 🔁 Çoklu Return

Python fonksiyonu birden fazla değeri virgülle döndürebilir:

```python
return servis_adları, son_durum, başarısız_servisler
```

Python bunları arka planda bir tuple hâline getirir:

```python
return (
    servis_adları,
    son_durum,
    başarısız_servisler
)
```

Dönen tuple yeniden unpack edilebilir:

```python
servis_adları, son_durum, başarısız_servisler = analiz_et(kayıtlar)
```

---

# 🧪 Servis Kayıtlarını Analiz Etme

## Ham veri

```python
kayıtlar = [
    ("nginx", "ok"),
    ("redis", "fail"),
    ("nginx", "fail"),
    ("mysql", "ok"),
    ("redis", "ok")
]
```

Bu veride:

- `nginx` önce `ok`, sonra `fail`

- `redis` önce `fail`, sonra `ok`

- `mysql` yalnızca `ok`


durumunda görülmüştür.

---

## Temizlenmiş kod

```python
kayıtlar = [
    ("nginx", "ok"),
    ("redis", "fail"),
    ("nginx", "fail"),
    ("mysql", "ok"),
    ("redis", "ok")
]


def analiz_et(kayıtlar):
    servis_adları = []
    son_durum = {}
    hata_görmüş_servisler = set()

    for servis, durum in kayıtlar:
        servis_adları.append(servis)
        son_durum[servis] = durum

        if durum == "fail":
            hata_görmüş_servisler.add(servis)

    return servis_adları, son_durum, hata_görmüş_servisler


servis_adları, son_durum, hata_görmüş_servisler = analiz_et(kayıtlar)

print("Servis adları:", servis_adları)
print("Son durumlar:", son_durum)
print("Hata görmüş servisler:", hata_görmüş_servisler)
```

---

## Beklenen sonuçlar

### Servis adları

```python
["nginx", "redis", "nginx", "mysql", "redis"]
```

Liste:

- Bütün kayıtları korur.

- Sırayı korur.

- Tekrarları korur.


### Son durumlar

```python
{
    "nginx": "fail",
    "redis": "ok",
    "mysql": "ok"
}
```

Dictionary aynı servis tekrar geldiğinde eski durumu günceller.

### Hata görmüş servisler

```python
{"nginx", "redis"}
```

Her iki servis de geçmişte en az bir kez `"fail"` görülmüştür.

---

# 🚨 Kritik Anlam Hatası

Değişkenin adı:

```python
başarısız_servisler
```

olduğunda bu isim, servislerin **şu anda başarısız** olduğunu düşündürebilir.

Ancak mevcut kodun yaptığı şey:

```text
Geçmişte en az bir defa fail olmuş servisleri toplamak
```

Örneğin `redis` için kayıtlar:

```python
("redis", "fail")
("redis", "ok")
```

Son durumda Redis:

```python
"ok"
```

olmasına rağmen setin içinde kalır:

```python
{"redis", "nginx"}
```

Bu nedenle daha doğru değişken adı:

```python
hata_görmüş_servisler
```

veya:

```python
geçmişte_başarısız_servisler
```

olabilir.

> [!danger] Kafaya kazı
> `son_durum`, servisin en güncel durumunu tutar.
>
> Mevcut set ise servisin geçmişte herhangi bir anda fail olup olmadığını tutar.
>
> Bunlar aynı bilgi değildir.

---

## Yalnızca son durumda başarısız servisler istenirse

Önce bütün son durumlar oluşturulur:

```python
son_durum[servis] = durum
```

Daha sonra son durumu `"fail"` olan servisler seçilir:

```python
güncel_başarısız_servisler = {
    servis
    for servis, durum in son_durum.items()
    if durum == "fail"
}
```

Bu veride sonuç:

```python
{"nginx"}
```

olur.

Çünkü Redis geçmişte hata vermiş olsa da son durumu `"ok"` durumundadır.

---

# 🐧 Linux — `sort`, `uniq` ve Tekrarlar

## `uniq` nasıl çalışır?

`uniq`, dosyanın herhangi bir yerindeki bütün tekrarları bulmaz.

Yalnızca **art arda bulunan aynı satırları** birleştirir.

Dosya:

```text
nginx
redis
nginx
redis
```

Komut:

```bash
uniq services.txt
```

Çıktı değişmeyebilir:

```text
nginx
redis
nginx
redis
```

Çünkü aynı satırlar yan yana değildir.

---

## Yan yana tekrar örneği

Dosya:

```text
nginx
nginx
redis
redis
```

Komut:

```bash
uniq services.txt
```

Çıktı:

```text
nginx
redis
```

> [!warning] Düzeltilen yorum
> `uniq`, “diğer değeri bilmediği” için değil, tasarımı gereği yalnızca komşu satırları karşılaştırdığı için bütün tekrarları kaldıramaz.

---

## `sort`

```bash
sort services.txt
```

Satırları sıralar ancak tekrarları tek başına kaldırmaz.

Örnek:

```text
mysql
nginx
nginx
redis
redis
redis
```

---

## `sort | uniq`

```bash
sort services.txt | uniq
```

Önce aynı satırları yan yana getirir, sonra `uniq` tekrarları kaldırır.

---

## `sort -u`

```bash
sort -u services.txt
```

İki işlemi birlikte yapar:

1. Satırları sıralar.

2. Tekrarlı satırları kaldırır.


Şunlar benzer sonuç üretir:

```bash
sort services.txt | uniq
```

```bash
sort -u services.txt
```

---

## Orijinal sıra neden kaybolur?

Dosya:

```text
redis
nginx
mysql
redis
```

Komut:

```bash
sort -u services.txt
```

Çıktı:

```text
mysql
nginx
redis
```

Benzersiz değerler korunur ancak ilk görülme sırası kaybolur.

> [!danger] TIRT yorum
> `sort -u` yalnızca tekrarları kaybettiği için riskli değildir.
>
> Asıl mesele, satırları alfabetik olarak yeniden sıraladığı için orijinal kayıt sırasını yok etmesidir.

---

# 🔗 Linux ve Python Veri Yapıları Arasındaki Benzerlik

|Linux işlemi|Python benzetmesi|
|---|---|
|Orijinal dosya satırları|`list`|
|`sort`|`sorted(list)`|
|`sort -u`|Sıralanmış benzersiz değerler|
|`uniq`|Yalnızca komşu tekrarları kaldırma|
|`set`|Benzersiz elemanlar, sıra garantisi yok|

> [!warning]
> `sort -u` tam anlamıyla Python `set` değildir.
>
> Çünkü `sort -u` çıktıyı sıralar; set ise sıralama garantisi vermez.

---

# 🐳 Docker — Bind Mount

## Container host dosyasını neden otomatik göremez?

Container’ın kendisine ait ayrı bir dosya sistemi vardır.

Hostta:

```text
day03.py
```

dosyasının bulunması, container içinde de otomatik olarak bulunduğu anlamına gelmez.

Dosyayı görünür hâle getirmek için bind mount kullanılabilir:

```bash
docker run \
  -v "$PWD":/app:ro \
  -w /app \
  python:3.12-slim \
  python day03.py
```

---

# 📂 Bind Mount Mantığı

```text
HOST                                CONTAINER

Mevcut klasör      ─────────────▶   /app
day03.py                           /app/day03.py
services.txt                       /app/services.txt
```

Bind mount dosyayı container’a kopyalamaz.

Hosttaki gerçek dosya veya klasörü container içinde görünür hâle getirir.

Bu nedenle:

- Hosttaki değişiklik container tarafından görülebilir.

- Yazılabilir mount kullanılırsa container host dosyasını değiştirebilir.

- Container silinse bile host dosyaları kalır.


---

## Komutun parçaları

```bash
docker run \
  -v "$PWD":/app:ro \
  -w /app \
  python:3.12-slim \
  python day03.py
```

|Parça|Görevi|
|---|---|
|`docker run`|Yeni container oluşturur ve çalıştırır|
|`-v "$PWD":/app:ro`|Mevcut host klasörünü `/app` konumuna salt okunur bağlar|
|`-w /app`|Container’ın çalışma dizinini `/app` yapar|
|`python:3.12-slim`|Kullanılan image|
|`python day03.py`|Container içinde çalıştırılan komut|

---

# 💲 `$PWD` Nedir?

`PWD`, shell tarafından tutulan bir değişkendir.

İçinde bulunulan mevcut klasörün yolunu içerir:

```bash
echo "$PWD"
```

Örnek çıktı:

```text
/Users/username/projects/coreops
```

Shell şu komutu gördüğünde:

```bash
-v "$PWD":/app:ro
```

Docker çalıştırılmadan önce `$PWD` değerini gerçek yola çevirir.

Yaklaşık sonuç:

```bash
-v "/Users/polat/CODING/Gelişim/Gelişmiş":/app:ro
```

> [!important] Sıralama
>
> 1. Shell `$PWD` değişkenini çözer.
>
> 2. Gerçek path’i Docker’a argüman olarak gönderir.
>
> 3. Docker bind mount işlemini gerçekleştirir.
>

---

## `$` ne yapar?

Değişken oluşturmaz.

Değişkenin değerini okur veya genişletir.

Değişken oluşturma:

```bash
isim="User"
```

Değişkeni kullanma:

```bash
echo "$isim"
```

Çıktı:

```text
Polat
```

Şu komut ise:

```bash
echo isim
```

yalnızca:

```text
isim
```

yazar.

---

# 🛡️ Read-Only Mount — `:ro`

Normal bind mount:

```bash
-v "$PWD":/app
```

Container mount edilen klasörde:

- Dosya okuyabilir.

- Dosya oluşturabilir.

- Dosya değiştirebilir.

- Dosya silebilir.


Salt okunur bind mount:

```bash
-v "$PWD":/app:ro
```

Container:

- Dosya okuyabilir.

- Python dosyasını çalıştırabilir.

- Yeni dosya oluşturamaz.

- Dosya değiştiremez.

- Dosya silemez.


---

## `:ro` execute iznini kaldırır mı?

Hayır.

Linux izinleri:

|İzin|Anlam|
|---|---|
|`r`|Okuma|
|`w`|Yazma|
|`x`|Çalıştırma|

`:ro`, mount edilen dosya sistemine yazılmasını engeller.

Python programının RAM üzerinde liste veya dictionary değiştirmesini engellemez.

Çalışır:

```python
servisler = []
servisler.append("nginx")
```

Çünkü değişiklik RAM üzerindedir.

Çalışmaz:

```python
with open("yeni.txt", "w") as dosya:
    dosya.write("Merhaba")
```

Çünkü mount edilen dosya sistemine yazılmaya çalışılır.

---

# 📁 `-w /app` Neden Kullanılır?

Bind mount sonrasında dosya container içinde:

```text
/app/day03.py
```

konumunda bulunur.

Şu komutun çalışabilmesi için:

```bash
python day03.py
```

mevcut çalışma dizininin `/app` olması gerekir:

```bash
-w /app
```

`-w` kullanılmasaydı tam yol verilebilirdi:

```bash
python /app/day03.py
```

---

# 🔬 Host ve Container Çıktılarını Karşılaştırma

## Host çıktısını kaydetme

```bash
python day03.py > host.txt
```

`>` operatörü standart çıktıyı dosyaya yönlendirir.

---

## Container çıktısını kaydetme

```bash
docker run \
  -v "$PWD":/app:ro \
  -w /app \
  python:3.12-slim \
  python day03.py > container.txt
```

Burada:

```text
Container içindeki Python çıktısı
                ↓
Host shell tarafından container.txt dosyasına yazılır
```

Önemli nokta:

```bash
> container.txt
```

işlemini container değil, host shell gerçekleştirir.

Bu nedenle bind mount `/app` konumu `:ro` olsa bile hostta `container.txt` oluşturulabilir.

---

## Dosyaları görüntüleme

```bash
cat host.txt
```

```bash
cat container.txt
```

---

## Çıktıları karşılaştırma

```bash
diff host.txt container.txt
```

`diff` hiçbir çıktı üretmiyorsa dosyalar aynıdır.

Kontrol:

```bash
echo $?
```

Dosyalar aynıysa:

```text
0
```

Farklıysa genellikle:

```text
1
```

döner.

---

# 🚨 Set Çıktısı ile `diff` Kullanma Riski

Set sırasına güvenilemez.

Host şu çıktıyı üretebilir:

```python
{"redis", "nginx"}
```

Container ise mantıksal olarak aynı seti şu sırayla yazabilir:

```python
{"nginx", "redis"}
```

İki set eşit olsa bile metinler farklıdır.

Bu durumda:

```bash
diff host.txt container.txt
```

fark gösterebilir.

Karşılaştırmayı deterministik hâle getirmek için set sıralanarak yazdırılmalıdır:

```python
print(
    "Hata görmüş servisler:",
    sorted(hata_görmüş_servisler)
)
```

Çıktı:

```text
Hata görmüş servisler: ['nginx', 'redis']
```

> [!danger] Kafaya kazı
> Mantıksal eşitlik ile metinsel eşitlik aynı şey değildir.
>
> `diff`, Python veri yapısını anlamaz. Yalnızca karakterleri karşılaştırır.

---

# 🧩 İlk Başarısızlık Sırasını Korumak

Yalnızca `set` kullanırsak:

- Benzersizlik korunur.

- İlk başarısızlık sırası garanti edilmez.


Yalnızca `list` kullanırsak:

- Sıra korunur.

- Aynı servis birden fazla kez eklenebilir.


Hem benzersizlik hem ilk görülme sırası isteniyorsa iki yapı birlikte kullanılabilir:

```python
ilk_hata_sırası = []
görülen_hatalar = set()

for servis, durum in kayıtlar:
    if durum == "fail" and servis not in görülen_hatalar:
        görülen_hatalar.add(servis)
        ilk_hata_sırası.append(servis)
```

Sonuç:

```python
["redis", "nginx"]
```

Bu modelde:

- `set` hızlı üyelik kontrolü yapar.

- `list` ilk başarısızlık sırasını korur.


> [!warning] Düzeltilen ustalık cevabı
> “Sıra gerekiyorsa set yerine list kullanırım” cevabı yarımdır.
>
> Çünkü yalnızca list kullanılırsa tekrarlar geri gelebilir.
>
> Doğru düşünce:
>
> ```text
> Benzersizlik + sıra gerekiyorsa veri modelini yeniden tasarla.
> ```
>
> En açık çözümlerden biri `list + set` ikilisidir.

---

# 🧯 Hata Avı

## 1. Fonksiyon adı

Kodda:

```python
analayzer
```

yazılmış.

Daha okunabilir bir isim:

```python
analiz_et
```

veya:

```python
analyze_records
```

olabilir.

---

## 2. Set sırası

Set çıktısının her zaman:

```python
{"redis", "nginx"}
```

olacağını varsaymak TIRT.

Mantıksal içeriğe güvenilebilir, yazdırılma sırasına güvenilemez.

---

## 3. `uniq` bütün tekrarları kaldırmaz

```bash
uniq dosya.txt
```

yalnızca arka arkaya gelen tekrarları birleştirir.

Bütün tekrarlar için genellikle:

```bash
sort -u dosya.txt
```

kullanılır ancak bu orijinal sırayı değiştirir.

---

## 4. “Başarısız servis” ifadesi belirsiz

Aşağıdakiler farklı kavramlardır:

```text
Geçmişte en az bir kez fail olmuş servis
Son kaydı fail olan servis
İlk kez fail olduğu sıraya göre servisler
Toplam fail sayısı
```

Kod yazmadan önce hangisinin istendiği netleştirilmelidir.

---

# 🧠 Kafaya Kazı

> [!quote]
> Veri yapısını verinin adına göre değil, korunması gereken bilgiye göre seç.

> [!quote]
> List sıra ve tekrarları korur.

> [!quote]
> Dictionary son anahtar-değer eşlemesini tutar.

> [!quote]
> Set benzersizlik sağlar ancak sırasına güvenilmez.

> [!quote]
> `uniq` yalnızca komşu tekrarları birleştirir.

> [!quote]
> `sort -u` tekrarları kaldırır ancak orijinal sırayı bozar.

> [!quote]
> Bind mount dosyayı kopyalamaz; hosttaki gerçek dosyayı bağlar.

> [!quote]
> `$PWD` değerini Docker değil, önce shell çözer.

> [!quote]
> `:ro` RAM’i değil, mount edilen dosya sistemine yazmayı engeller.

> [!quote]
> `diff` veri yapılarını değil, metinleri karşılaştırır.

---

# 🎓 Ustalık Kontrolü

## Neden üç farklı veri yapısı kullanıldı?

Çünkü üç farklı bilgi korunmak istendi:

- Servis geçmişinde sıra ve tekrar → `list`

- Servisin en son durumu → `dict`

- Hata görmüş benzersiz servis isimleri → `set`


Tek bir veri yapısı bu üç ihtiyacı aynı açıklıkta karşılamaz.

---

## İlk başarısızlık sırası da korunacaksa neden set yetersizdir?

Çünkü set benzersizlik sağlar ancak elemanların ilk görülme sırasını temsil etmek için uygun değildir.

Hem benzersizlik hem sıra gerekiyorsa:

```text
List → sırayı tutar
Set → daha önce eklenip eklenmediğini kontrol eder
```

şeklinde iki yapı birlikte kullanılabilir.

---

## `son_durum` ile hata seti neden farklı sonuç verir?

Çünkü `son_durum`, her servisin yalnızca en son kaydını tutar.

Hata seti ise servis geçmişte herhangi bir anda `"fail"` olduğunda onu ekler ve sonraki `"ok"` kaydında otomatik olarak silmez.

---

## Host ve container çıktısı aynıysa ne kanıtlanır?

Aynı kodun iki ortamda aynı metinsel çıktıyı ürettiği kanıtlanır.

Ancak yalnızca bu test:

- Kodun bütün girdilerde doğru olduğunu

- Bütün Python sürümlerinde aynı davranacağını

- Set sırasının her çalıştırmada aynı kalacağını


kanıtlamaz.

---

# 📌 30 Saniyelik Özet

```text
LIST
- Sıralı
- Tekrar korunur
- append()

DICT
- Anahtar → değer
- Aynı anahtar tekrar gelirse değer güncellenir
- Son durum tutmak için uygun

SET
- Benzersiz eleman
- Sıra garantisi yok
- add()

TUPLE UNPACKING
for servis, durum in kayıtlar:

LINUX
uniq       → yalnız komşu tekrarlar
sort       → sırala
sort -u    → sırala ve tekrarları kaldır
diff       → metinsel karşılaştırma

DOCKER
-v "$PWD":/app:ro → read-only bind mount
-w /app           → çalışma dizini
$PWD              → hosttaki mevcut klasör
:ro               → filesystem’e yazmayı engeller

KRİTİK AYRIM
son_durum              → en güncel kayıt
hata_görmüş_servisler   → geçmişte en az bir fail
güncel_başarısızlar     → son durumu fail olanlar
```

---

# ✅ Görev Durumu

-  List kullanıldı

-  Dictionary kullanıldı

-  Set kullanıldı

-  Tuple unpacking uygulandı

-  Fonksiyondan çoklu değer döndürüldü

-  `sort`, `uniq` ve `sort -u` karşılaştırıldı

-  Bind mount kullanıldı

-  Read-only mount uygulandı

-  `$PWD` ve shell expansion kavrandı

-  Host ve container çıktıları karşılaştırıldı

-  `diff` sonucu doğrulandı

-  Set sırasının karşılaştırma üzerindeki riski fark edildi

-  Geçmişte hata verme ile güncel hata durumu ayrıldı
