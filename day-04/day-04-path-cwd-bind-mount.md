---
title: "Gün 04 — Dosya Okuma, Relative Path, CWD ve Docker Bind Mount"
tags:
  - coreops
  - python
  - linux
  - docker
  - relative-path
  - cwd
  - bind-mount
  - symlink
aliases:
  - "Gün 4 Path CWD ve Bind Mount"
status: completed
---

# 🧭 Gün 4 — Dosya Okuma, Relative Path, CWD ve Docker Bind Mount

> [!abstract] 🎯 Ana fikir
> `"data.txt"` sabit bir adres değildir.
>
> Python, göreli path’i kaynak kod dosyasının yanına göre değil, process’in **mevcut çalışma dizinine — CWD’ye** göre çözer.
>
> ```text
> Göreli path + CWD = Python’ın aradığı mutlak path
> ```

---

# ⚡ 2 Dakikalık Geri Çağırma

## Set sırasına neden güvenilmez?

Set, eleman sırası garantisi vermez.

```python
servisler = {"nginx", "redis", "apache"}
```

Çıktının hangi sırayla gösterileceğine güvenilmemelidir.

> [!danger] Kritik düzeltme
> Programı birkaç kez çalıştırıp aynı sırayı görmek, setin sıralı olduğunu kanıtlamaz.
>
> Deney yalnızca gözlem sağlar. Dilin garanti vermediği bir davranışa kod bağlanmaz.

Sıra gerekiyorsa:

```python
list
```

kullanılır.

Hem sıra hem benzersizlik gerekiyorsa:

```text
list + set
```

birlikte kullanılabilir.

---

# 🐍 Python — Dosya Okuma ve Path Mantığı

## Relative path nedir?

Göreli path, başlangıç noktası tek başına belli olmayan path’tir.

```text
data.txt
./data.txt
../data.txt
dosyalar/data.txt
```

Bunların anlamını belirlemek için hangi dizine göre değerlendirildiklerini bilmek gerekir.

---

## Absolute path nedir?

Dosyanın kökten başlayan tam adresidir.

```text
/Users/polat/CODING/Gelişim/Gelişmiş/data.txt
```

Bunu ev adresine benzetebiliriz:

```text
Relative path → “Yan odadaki dosya”
Absolute path → “Şehir, sokak, bina, daire”
```

---

# 📍 `open("data.txt")` Dosyayı Nerede Arar?

```python
open("data.txt")
```

Python bu dosyayı `day04.py` dosyasının bulunduğu klasörde otomatik olarak aramaz.

Arama başlangıç noktası:

```python
os.getcwd()
```

sonucudur.

```python
import os

print(os.getcwd())
```

Örnek:

```text
CWD:
/Users/polat/CODING/Gelişim
```

Kod:

```python
open("data.txt")
```

Python’ın aradığı yer:

```text
/Users/polat/CODING/Gelişim/data.txt
```

olur.

---

> [!danger] TIRT düşünce
> “`day04.py` ile `data.txt` yan yana, kesin bulunur.”
>
> Yanlış.
>
> Önemli olan dosyaların yan yana olması değil, process’in hangi çalışma dizininden başlatıldığıdır.

---

# 📌 `os.getcwd()` ve `__file__`

Bu ikisi aynı şeyi göstermez.

|İfade|Gösterdiği şey|
|---|---|
|`os.getcwd()`|Process’in mevcut çalışma dizini|
|`__file__`|Çalıştırılan Python dosyasının path’i|

Örnek dosya yapısı:

```text
Gelişim/
└── Gelişmiş/
    ├── day04.py
    └── data.txt
```

Üst klasörden çalıştırma:

```bash
cd Gelişim
python3 "Gelişmiş/day04.py"
```

Python içinde:

```python
import os

print("CWD:", os.getcwd())
print("Script:", __file__)
```

Muhtemel çıktı:

```text
CWD: /Users/polat/CODING/Gelişim
Script: /Users/polat/CODING/Gelişim/Gelişmiş/day04.py
```

Buna rağmen:

```python
open("data.txt")
```

şurada arama yapar:

```text
/Users/polat/CODING/Gelişim/data.txt
```

Script’in yanında aramaz.

---

# 🧱 Script’in Yanındaki Dosyaya Güvenli Erişim

Dosyanın daima Python script’inin yanında aranması isteniyorsa CWD’ye bağlanmak yerine script’in konumu temel alınabilir.

```python
from pathlib import Path

script_dizini = Path(__file__).resolve().parent
data_path = script_dizini / "data.txt"

print(data_path.read_text())
```

Burada:

```text
__file__
    ↓
day04.py dosyasının path’i
    ↓
.parent
    ↓
day04.py dosyasının bulunduğu klasör
    ↓
/ "data.txt"
    ↓
Script’in yanındaki data.txt
```

> [!important] İki farklı tasarım
>
> ```text
> open("data.txt")
> → Dosyayı CWD’ye göre ara
>
> Path(__file__).resolve().parent / "data.txt"
> → Dosyayı script’in yanına göre ara
> ```
>
> Hangisinin doğru olduğu programın şartnamesine bağlıdır.

---

# 📖 `dosya_oku()` Fonksiyonu

```python
def dosya_oku(path):
    with open(path) as file:
        return file.read()
```

Bu fonksiyonun adımları:

```text
1. Verilen path’i aç.
2. Dosyanın içeriğini oku.
3. İçeriği string olarak döndür.
4. with bloğu bitince dosyayı kapat.
```

Tam kullanım:

```python
import os

path = "data.txt"


def dosya_oku(path):
    with open(path) as file:
        return file.read()


print("CWD:", os.getcwd())
print("Absolute path:", os.path.abspath(path))
print(dosya_oku(path))
```

---

# 🔥 `return file` ile `return file.read()` Farkı

## `return file`

```python
def dosya_ac(path):
    with open(path) as file:
        return file
```

Çağıran taraf dosyanın içeriğini değil, bir dosya nesnesi alır.

Fakat daha önemli sorun şudur:

```text
return çalışır
    ↓
with bloğundan çıkılır
    ↓
dosya otomatik kapatılır
    ↓
çağıran taraf kapanmış dosya nesnesi alır
```

Örnek:

```python
dosya = dosya_ac("data.txt")

print(dosya.closed)
```

Sonuç:

```python
True
```

Ardından:

```python
dosya.read()
```

çalıştırılırsa şu tür bir hata oluşabilir:

```text
ValueError: I/O operation on closed file
```

---

## `return file.read()`

```python
def dosya_oku(path):
    with open(path) as file:
        return file.read()
```

Burada dosya açıkken içeriği okunur.

`read()` sonucu bir string’dir:

```python
icerik = dosya_oku("data.txt")

print(type(icerik))
```

Sonuç:

```python
<class 'str'>
```

Dosya kapansa bile okunan string RAM’de yaşamaya devam eder.

> [!success] Kafaya kazı
>
> ```text
> return file
> → Kapanmış dosya nesnesi dönebilir
>
> return file.read()
> → Dosya açıkken okunan metni döndürür
> ```

---

# ⚠️ `file.read` ile `file.read()`

```python
file.read
```

Metodu çalıştırmaz. Metot nesnesinin kendisini ifade eder.

```python
file.read()
```

Metodu çağırır ve dosyanın içeriğini döndürür.

|Kullanım|Sonuç|
|---|---|
|`file.read`|Metodun kendisi|
|`file.read()`|Dosyanın okunmuş içeriği|

---

# 🗺️ `os.path.abspath()`

```python
os.path.abspath("data.txt")
```

Göreli path’i mevcut çalışma dizinine göre mutlak hâle getirir.

Örneğin CWD:

```text
/Users/polat/CODING/Gelişim
```

ise:

```python
os.path.abspath("data.txt")
```

şunu üretebilir:

```text
/Users/polat/CODING/Gelişim/data.txt
```

---

## `abspath()` Dosyanın Varlığını Kontrol Eder mi?

Hayır.

```python
import os

path = os.path.abspath("olmayan.txt")

print(path)
print(os.path.exists(path))
```

Çıktı:

```text
/Users/polat/CODING/Gelişim/olmayan.txt
False
```

`abspath()` yalnızca şu soruyu cevaplar:

```text
“Bu göreli path, mevcut CWD’ye göre mutlak yazılsaydı nasıl görünürdü?”
```

Dosyanın gerçekten var olup olmadığını cevaplamaz.

---

## İlgili fonksiyonlar

|Fonksiyon|Görevi|
|---|---|
|`os.path.abspath(path)`|Mutlak path üretir|
|`os.path.exists(path)`|Path mevcut mu?|
|`os.path.isfile(path)`|Path normal dosya mı?|
|`os.path.isdir(path)`|Path dizin mi?|
|`os.path.realpath(path)`|Symlink’leri de çözerek fiziksel path üretir|

---

# 🧪 Aynı Script, Farklı Çalışma Dizinleri

Dosya yapısı:

```text
Gelişim/
└── Gelişmiş/
    ├── day04.py
    └── data.txt
```

## ✅ Deneme 1 — Script klasöründen çalıştırmak

```bash
cd "Gelişim/Gelişmiş"
python3 day04.py
```

CWD:

```text
/Users/polat/CODING/Gelişim/Gelişmiş
```

Göreli path:

```text
data.txt
```

Çözülen mutlak path:

```text
/Users/polat/CODING/Gelişim/Gelişmiş/data.txt
```

Dosya bulunduğu için program çalışır.

---

## ❌ Deneme 2 — Üst klasörden çalıştırmak

```bash
cd Gelişim
python3 "Gelişmiş/day04.py"
```

CWD:

```text
/Users/polat/CODING/Gelişim
```

Göreli path:

```text
data.txt
```

Çözülen mutlak path:

```text
/Users/polat/CODING/Gelişim/data.txt
```

Gerçek dosya ise:

```text
/Users/polat/CODING/Gelişim/Gelişmiş/data.txt
```

konumundadır.

Sonuç:

```text
FileNotFoundError
```

---

> [!success] Ana yorum
> `data.txt` yazısı değişmedi.
>
> Ancak CWD değiştiği için Python’ın ürettiği mutlak path değişti.

---

# 🐧 Linux — `pwd`, `ls`, `.` ve `..`

## `pwd`

Şu soruya cevap verir:

```text
“Şu anda hangi dizindeyim?”
```

```bash
pwd
```

Örnek:

```text
/Users/polat/CODING/Gelişim
```

---

## `ls`

Şu soruya cevap verir:

```text
“Bu dizinin içinde neler var?”
```

```bash
ls
```

`ls` tek başına şu kullanıma denktir:

```bash
ls .
```

---

## Fark

|Komut|Cevapladığı soru|
|---|---|
|`pwd`|Neredeyim?|
|`ls`|Burada neler var?|

---

# 📍 `.` ve `..`

```text
.  → Mevcut dizin
.. → Bir üst dizin
```

Örnek:

```bash
cat ./day04/data.txt
```

Buradaki `.` mevcut dizini temsil eder.

```bash
cat ../data.txt
```

Bir üst dizindeki `data.txt` dosyasını hedefler.

> [!warning]
> `..`, daha önce bulunduğun dizin değildir.
>
> Bir üst dizindir.
>
> Önceki çalışma dizinine dönmek için:
>
> ```bash
> cd -
> ```

kullanılır.

---

# 🛣️ Path ile `$PATH` Aynı Şey Değildir

## Path

Dosya veya dizinin adresidir:

```text
day04.py
./day04.py
../day04.py
/Users/polat/day04.py
```

## `$PATH`

Shell’in komut aradığı dizinlerin listesidir:

```bash
echo "$PATH"
```

Örnek:

```text
/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin
```

---

# ▶️ `day04.py`, `./day04.py` ve `python3 day04.py`

## `day04.py`

```bash
day04.py
```

Shell, bu isimde çalıştırılabilir bir komutu `$PATH` içindeki dizinlerde arar.

Mevcut dizin varsayılan olarak `$PATH` içinde olmayabilir.

---

## `./day04.py`

```bash
./day04.py
```

Mevcut dizindeki dosyanın doğrudan çalıştırılmasını ister.

Genellikle şunlar gerekir:

```bash
chmod +x day04.py
```

ve dosyanın ilk satırında shebang:

```python
#!/usr/bin/env python3
```

---

## `python3 day04.py`

```bash
python3 day04.py
```

Burada shell’in doğrudan çalıştırdığı program:

```text
python3
```

olur.

`day04.py`, Python yorumlayıcısına argüman olarak verilir.

```text
1. Shell python3 komutunu $PATH içinde bulur.
2. Python yorumlayıcısını çalıştırır.
3. day04.py path’ini Python’a verir.
4. Python dosyayı okuyup çalıştırır.
```

Bu kullanımda `day04.py` dosyasının execute iznine veya shebang’e ihtiyacı yoktur.

---

# 🧾 Shebang

Shebang, script’in hangi yorumlayıcıyla çalıştırılacağını belirten ilk satırdır.

```python
#!/usr/bin/env python3

print("Merhaba")
```

Burada:

```text
#!                   → Shebang başlangıcı
/usr/bin/env python3 → $PATH içindeki python3 yorumlayıcısını bul
```

Ardından:

```bash
chmod +x day04.py
./day04.py
```

ile doğrudan çalıştırılabilir.

---

# 🔗 Symlink

Symlink, başka bir path’i gösteren sembolik bağlantıdır.

Gerçek dizin:

```bash
mkdir -p /tmp/pathlab/real/project
```

Symlink:

```bash
ln -s /tmp/pathlab/real/project /tmp/pathlab/shortcut
```

Genel yapı:

```bash
ln -s HEDEF LINK_ADI
```

|Bölüm|Anlam|
|---|---|
|`ln`|Bağlantı oluştur|
|`-s`|Sembolik bağlantı oluştur|
|`HEDEF`|Bağlantının göstereceği path|
|`LINK_ADI`|Oluşturulacak bağlantının adı|

Kontrol:

```bash
ls -l /tmp/pathlab
```

Çıktı:

```text
shortcut -> /tmp/pathlab/real/project
```

Symlink hedefin kopyası değildir. Hedef path’i gösteren ayrı bir bağlantıdır.

---

# 🧭 Logical ve Physical Path

Symlink üzerinden dizine girildiğinde mantıksal ve fiziksel path farklı olabilir.

```bash
cd /tmp/pathlab/shortcut
```

## Mantıksal path

```bash
pwd -L
```

Çıktı:

```text
/tmp/pathlab/shortcut
```

Buraya gelirken kullandığın path’i gösterir.

## Fiziksel path

```bash
pwd -P
```

Çıktı:

```text
/tmp/pathlab/real/project
```

Symlink çözülünce ulaşılan gerçek path’i gösterir.

---

## `realpath`

```bash
realpath /tmp/pathlab/shortcut
```

Çözülmüş fiziksel path’i gösterebilir:

```text
/tmp/pathlab/real/project
```

Genel olarak:

- Göreli path’i mutlaklaştırır.

- `.` ve `..` parçalarını çözer.

- Symlink’leri fiziksel hedeflerine kadar takip eder.


> [!note]
> `realpath` seçenekleri ve var olmayan path’lerdeki davranış kullanılan işletim sistemine göre değişebilir.
>
> macOS üzerinde logical–physical ayrımını test etmek için en güvenilir temel araçlar:
>
> ```bash
> pwd -L
> pwd -P
> ```

---

# 🐳 Docker — Bind Mount, Source, Target ve `-w`

## Temel komut

```bash
docker run --rm \
  -v "$PWD":/app:ro \
  -w /app \
  python:3.12-slim \
  python day04.py
```

---

## Komutun parçaları

|Parça|Görevi|
|---|---|
|`docker run`|Container oluşturur ve çalıştırır|
|`--rm`|Process bitince container’ı siler|
|`-v "$PWD":/app:ro`|Hosttaki mevcut klasörü `/app` konumuna salt okunur bağlar|
|`-w /app`|Container process’inin çalışma dizinini `/app` yapar|
|`python:3.12-slim`|Kullanılan image|
|`python day04.py`|Container içinde çalıştırılan komut|

---

# 🗺️ Source ve Target

Uzun kullanım:

```bash
--mount type=bind,source="$PWD",target=/app
```

|Alan|Ait olduğu sistem|
|---|---|
|`source`|Host|
|`target`|Container|

Kısa kullanım:

```bash
-v "$PWD":/app
```

Burada:

```text
Sol taraf  → Host
Sağ taraf → Container
```

Görsel:

```text
HOST                                      CONTAINER

$PWD/day04.py       ───────────────────▶  /app/day04.py
$PWD/data.txt       ───────────────────▶  /app/data.txt
```

Dosyalar container’a kopyalanmaz. Hosttaki gerçek dosyalar container içinde görünür hâle gelir.

---

# 📂 Göreli Host Path Neden Risklidir?

```bash
-v ./proje:/app
```

Buradaki:

```text
./proje
```

host shell’in mevcut çalışma dizinine göre çözülür.

Örneğin:

```text
CWD: /Users/polat
→ /Users/polat/proje

CWD: /Users/polat/CODING
→ /Users/polat/CODING/proje
```

Aynı komut farklı klasörlerden çalıştırıldığında farklı host dizinleri mount edilebilir.

Daha açık kullanım:

```bash
-v "$PWD":/app
```

veya:

```bash
--mount type=bind,source="$PWD",target=/app
```

---

> [!warning] `-v` ve `--mount`
> Host source path yanlış yazılırsa `-v` bazı durumlarda boş bir dizin oluşturup mount edebilir.
>
> `--mount` ise bulunmayan source için genellikle doğrudan hata verir.
>
> Hataları erken görmek açısından `--mount` daha açıklayıcı olabilir.

---

# 📍 `-w /app` Ne Yapar?

```bash
-w /app
```

Container process’inin başlangıç çalışma dizinini `/app` yapar.

Bu nedenle:

```bash
python day04.py
```

şuna göre çözülür:

```text
/app/day04.py
```

Python kodunun içindeki:

```python
open("data.txt")
```

ise `/app` CWD’sine göre:

```text
/app/data.txt
```

olarak çözülür.

---

> [!danger] TIRT düşünce
> “`-w /app`, host dosyalarını `/app` içine taşır.”
>
> Yanlış.
>
> `-w` hiçbir dosyayı getirmez veya kopyalamaz.
>
> Yalnızca process’in hangi dizinden başlayacağını belirler.

---

# ❓ Mount Yapılmazsa Neden Dosya Bulunmaz?

Şu komutta bind mount yoktur:

```bash
docker run --rm \
  -w /app \
  python:3.12-slim \
  python day04.py
```

Container yalnızca `python:3.12-slim` image’ının kendi dosya sistemiyle başlar.

Mac’te bulunan:

```text
/Users/polat/CODING/Gelişim/Gelişmiş/day04.py
```

container içinde otomatik olarak mevcut değildir.

Python şurada arar:

```text
/app/day04.py
```

Ancak dosya orada olmadığı için:

```text
python: can't open file '/app/day04.py':
No such file or directory
```

hatası oluşur.

---

# 🧱 `/workspace` ve `/app` Uyumsuzluğu

Host klasörü şuraya mount edilirse:

```bash
-v "$PWD":/workspace:ro
```

ama çalışma dizini:

```bash
-w /app
```

olursa iki farklı dizin kullanılmış olur.

## Senaryo 1

Komut:

```bash
python day04.py
```

Python şurada arar:

```text
/app/day04.py
```

Fakat dosya:

```text
/workspace/day04.py
```

konumundadır.

Sonuç:

```text
day04.py bulunamaz
```

## Senaryo 2

Komut açıkça:

```bash
python /workspace/day04.py
```

olarak verilirse script bulunup çalışabilir.

Ancak script içindeki:

```python
open("data.txt")
```

hâlâ CWD olan:

```text
/app/data.txt
```

konumunda arama yapar.

Dosya ise:

```text
/workspace/data.txt
```

konumundadır.

Sonuç:

```text
FileNotFoundError
```

> [!important] Kafaya kazı
> Mount target ile çalışma dizini birbirinden bağımsızdır.
>
> ```text
> Mount target → Dosyalar container içinde nerede görünsün?
> -w           → Process hangi dizinden çalışsın?
> ```

---

# 🛡️ `:ro` — Read-Only Mount

```bash
-v "$PWD":/app:ro
```

Container `/app` içindeki dosyaları:

- Okuyabilir.

- Python ile çalıştırabilir.

- Değiştiremez.

- Silemez.

- Yeni dosya oluşturamaz.


Çalışır:

```python
with open("data.txt") as file:
    print(file.read())
```

Çalışmaz:

```python
with open("data.txt", "w") as file:
    file.write("Yeni içerik")
```

---

## `:ro` Python’ı Kısıtlar mı?

Hayır.

Şu kod çalışır:

```python
servisler = []
servisler.append("nginx")
```

Çünkü liste RAM üzerinde değişir.

Engellenen şey mount edilen dosya sistemine yazmaktır.

```text
RAM değişikliği → Serbest
/app içine yazma → Engelli
```

---

# 🧪 Docker İçinde CWD ve Dosyaları Görme

```bash
docker run --rm \
  -v "$PWD":/app:ro \
  -w /app \
  python:3.12-slim \
  sh -c 'pwd && ls'
```

Çıktı:

```text
/app
data.txt
day01.py
day02.py
day03.py
day04.py
```

Burada:

```bash
pwd
```

container’ın CWD’sini gösterir.

```bash
ls
```

container içindeki `/app` dizininde görünen mount edilmiş dosyaları listeler.

---

# 🔗 Entegrasyon Deneyleri

## 1. Script’in bulunduğu klasörden host çalıştırması

```bash
cd "Gelişim/Gelişmiş"
python3 day04.py
```

CWD:

```text
/Users/polat/CODING/Gelişim/Gelişmiş
```

Aranan dosya:

```text
/Users/polat/CODING/Gelişim/Gelişmiş/data.txt
```

Sonuç:

```text
Başarılı
```

---

## 2. Üst klasörden host çalıştırması

```bash
cd Gelişim
python3 "Gelişmiş/day04.py"
```

CWD:

```text
/Users/polat/CODING/Gelişim
```

Aranan dosya:

```text
/Users/polat/CODING/Gelişim/data.txt
```

Gerçek dosya:

```text
/Users/polat/CODING/Gelişim/Gelişmiş/data.txt
```

Sonuç:

```text
FileNotFoundError
```

---

## 3. Docker içinde çalıştırma

```bash
cd "Gelişim/Gelişmiş"

docker run --rm \
  -v "$PWD":/app:ro \
  -w /app \
  python:3.12-slim \
  python day04.py
```

Container CWD:

```text
/app
```

Aranan dosya:

```text
/app/data.txt
```

Bind mount nedeniyle dosya burada görünür.

Sonuç:

```text
Başarılı
```

---

## Üç deneyin karşılaştırması

|Deney|CWD|`data.txt` hangi path’e çözülür?|Sonuç|
|---|---|---|---|
|Host — script klasörü|`.../Gelişmiş`|`.../Gelişmiş/data.txt`|✅|
|Host — üst klasör|`.../Gelişim`|`.../Gelişim/data.txt`|❌|
|Docker|`/app`|`/app/data.txt`|✅|

> [!warning] Dil düzeltmesi
> Hostta `Gelişmiş`, container’da `/app` çalışma dizinidir.
>
> Bunlar aynı path değildir.
>
> Ancak bind mount sayesinde aynı host klasörünün içeriğini temsil ederler.

---

# 🧯 Hata Avı

## 1. `return file`

TIRT.

`with` bloğu bittiğinde dosya kapanır. Çağıran taraf kapanmış dosya nesnesi alır.

Doğrusu:

```python
return file.read()
```

---

## 2. `return file.read`

TIRT.

Parantez olmadığı için metot çalıştırılmaz.

Doğrusu:

```python
return file.read()
```

---

## 3. `os.path.abspath() + "data.txt"`

TIRT.

`abspath()` çevrilecek path’i argüman olarak ister:

```python
os.path.abspath("data.txt")
```

---

## 4. `abspath()` dosyanın varlığını kanıtlar

TIRT.

```python
os.path.abspath(path)
```

yalnızca mutlak path üretir.

Varlık kontrolü:

```python
os.path.exists(path)
```

---

## 5. Python dosyasıyla veri dosyası yan yanaysa bulunur

TIRT.

Göreli path’in başlangıç noktası script’in klasörü değil CWD’dir.

---

## 6. `/Users/polat/...` container içinde çalışır

Genellikle TIRT.

Bu, host path’idir.

Container içindeki karşılığı bind mount target’ına göre örneğin:

```text
/app/data.txt
```

olur.

---

## 7. Container içinde `data.txt`, `/app/day04` path’indedir

TIRT.

Mount edilen klasör `/app` ise dosyanın yolu:

```text
/app/data.txt
```

olur.

`day04.py` bir klasör değildir.

---

# 🧠 Kafaya Kazı

> [!quote]
> Relative path sabit adres değildir; bir başlangıç dizinine ihtiyaç duyar.

> [!quote]
> Python göreli path’leri CWD’ye göre çözer.

> [!quote]
> `os.getcwd()` process’in çalışma dizinini gösterir.

> [!quote]
> `__file__`, Python dosyasının path’ini gösterir.

> [!quote]
> `abspath()` path üretir, varlık kontrolü yapmaz.

> [!quote]
> `return file` ile kapanmış dosya nesnesi döndürülebilir.

> [!quote]
> `return file.read()` dosyanın içeriğini string olarak döndürür.

> [!quote]
> `$PATH`, shell’in komut aradığı dizinlerin listesidir.

> [!quote]
> `./dosya`, mevcut dizindeki dosyayı açıkça hedefler.

> [!quote]
> Source hosta, target container’a aittir.

> [!quote]
> Mount dosyaları gösterir, `-w` çalışma dizinini belirler.

> [!quote]
> Host path’i ile container path’i aynı olmak zorunda değildir.

---

# 🎓 Mini Sınav

## 1. `open("data.txt")` dosyayı hangi dizine göre arar?

Process’in mevcut çalışma dizinine, yani `os.getcwd()` sonucuna göre arar.

---

## 2. `os.path.abspath()` dosyanın var olduğunu garanti eder mi?

Hayır. Yalnızca path’in CWD’ye göre mutlak hâlini üretir.

---

## 3. `return file` neden sorun çıkarabilir?

`with` bloğu bittiğinde dosya kapanır. Çağıran taraf kapanmış bir dosya nesnesi alabilir ve okumaya çalıştığında hata oluşur.

---

## 4. `return file.read()` ne döndürür?

Dosyanın okunmuş içeriğini, genellikle `str` olarak döndürür.

---

## 5. `-w /app` host dosyalarını `/app` içine getirir mi?

Hayır. Yalnızca container process’inin çalışma dizinini `/app` yapar. Dosyaları görünür yapmak için mount veya `COPY` gerekir.

---

## 6. Host klasörü `/workspace` içine mount edilip `-w /app` verilirse ne olur?

`python day04.py`, `/app/day04.py` dosyasını arar ve bulamaz. Script `/workspace/day04.py` olarak çalıştırılsa bile `open("data.txt")`, CWD `/app` olduğu için `/app/data.txt` arar.

---

# 📌 30 Saniyelik Özet

```text
PYTHON
open("data.txt") → CWD/data.txt
os.getcwd()      → Çalışma dizini
__file__         → Script path’i
abspath()        → Mutlak path üretir
exists()         → Varlık kontrol eder
file.read()      → İçeriği okur
return file      → Kapanmış file nesnesi dönebilir

LINUX
pwd              → Neredeyim?
ls               → Burada ne var?
.                → Mevcut dizin
..               → Üst dizin
$PATH            → Komut arama dizinleri
day04.py         → $PATH içinde ara
./day04.py       → Mevcut dosyayı çalıştır
python3 day04.py → Python’a dosyayı okut

SYMLINK
ln -s            → Sembolik bağlantı
pwd -L           → Mantıksal path
pwd -P           → Fiziksel path
realpath         → Çözülmüş gerçek path

DOCKER
source           → Host path’i
target           → Container path’i
-v               → Bind mount
-w               → Container CWD
:ro              → Mount’a yazmayı engeller
/app/data.txt    → Container içindeki dosya
```

---

# ✅ Günün Kazanımları

-  Relative ve absolute path ayrıldı

-  Göreli path’in CWD’ye göre çözüldüğü anlaşıldı

-  `os.getcwd()` ve `__file__` ayrıldı

-  `abspath()` ile varlık kontrolü ayrıldı

-  `return file` hatası kavrandı

-  `file.read()` kullanımı öğrenildi

-  Aynı script farklı CWD’lerden test edildi

-  `pwd`, `ls`, `.`, `..` uygulandı

-  Path ile `$PATH` ayrıldı

-  Shebang ve execute izni öğrenildi

-  Symlink, logical ve physical path ayrıldı

-  Docker source ve target ayrıldı

-  Bind mount ile `-w` farkı kavrandı

-  Read-only mount uygulandı

-  Host ve container path’lerinin farklı olduğu görüldü

-  Mount target ile workdir uyumsuzluğunun iki farklı hata üretebileceği anlaşıldı


---

> [!success] 🚀 Gün sonu sonucu
> Gün 4 sonunda path’in yalnızca yazılmış bir metin olmadığı; **hangi process tarafından, hangi dosya sisteminde ve hangi çalışma dizinine göre çözüldüğünün** bilinmesi gerektiği öğrenildi.
>
> Aynı `"data.txt"` ifadesinin hostta farklı dizinlere, container içinde ise `/app/data.txt` konumuna çözülmesi bu mantığı somutlaştırdı.
