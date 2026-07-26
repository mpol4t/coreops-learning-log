---
title: "Day 02 — Assertion, Exit Code ve Komut Zincirleri"
tags:
  - coreops
  - python
  - linux
  - docker
  - debugging
  - exit-code
  - assertion
aliases:
  - "Day 02 Assertions ve Exit Codes"
status: completed
duration: "100–110 dakika"
---

# 🧠 Day 02 — Assertion, Exit Code ve Komut Zincirleri

> [!abstract] 🎯 Ana fikir
> Bir programın **değer döndürmesi**, bir işlemin **başarılı tamamlanması** ve bir container’ın **durması** aynı şey değildir.
>
> Bunları ayıran üç temel kavram:
>
> - Python fonksiyonlarında → `return`
>
> - İşletim sistemi seviyesinde → **exit code**
>
> - Docker seviyesinde → container process’inin **exit code’u**
>

---

## ⚡ 2 Dakikalık Geri Çağırma

### 1. Fonksiyonda `return` bulunmazsa ne döner?

Python fonksiyonunda açık bir `return` yoksa veya yalnızca `return` yazılmışsa fonksiyon:

```python
None
```

döndürür.

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

> [!important] Unutma
> `print()` ekrana çıktı üretir, `return` ise fonksiyonun çağrıldığı yere değer gönderir.

---

### 2. Başarılı çalışan bir komutun exit code’u nedir?

```text
0
```

Shell dünyasında genel kural:

|Exit code|Anlam|
|--:|---|
|`0`|İşlem başarılı|
|`0` dışındaki değerler|Bir hata veya başarısızlık meydana geldi|

Son çalışan komutun exit code’unu görmek için:

```bash
echo $?
```

---

### 3. Return değeri ile exit code arasındaki fark

|Kavram|Cevapladığı soru|
|---|---|
|Return değeri|Fonksiyon hangi sonucu üretti?|
|Exit code|Program veya komut başarılı tamamlandı mı?|

```python
def topla(a, b):
    return a + b
```

Bu fonksiyon `5` döndürebilirken Python programı başarıyla tamamlandıysa işletim sistemine `0` exit code’u döner.

> [!danger] Karıştırma
> Fonksiyonun `0` döndürmesi programın başarısız olduğu anlamına gelmez.
>
> Programın exit code’unun `0` olması ise programın başarılı tamamlandığı anlamına gelir.

---

# 🐍 Python — `assert`, Sınır Değerleri ve Exception

## 🔍 `assert` ne yapar?

`assert`, doğru olması gerektiğini düşündüğümüz bir koşulu kontrol eder.

```python
assert 3 * 3 == 9
```

Koşul doğruysa program sessizce devam eder.

```python
assert 3 * 3 == 8
```

Koşul yanlışsa Python:

```text
AssertionError
```

exception’ını fırlatır.

---

## 🧩 `assert` çalışma mantığı

Aşağıdaki kod:

```python
assert kosul
```

zihinsel olarak şuna benzer:

```python
if not kosul:
    raise AssertionError
```

Mesaj da eklenebilir:

```python
assert yas >= 18, "Yaş 18 veya daha büyük olmalıdır."
```

---

## 🚫 `assert` neden kullanıcı girdisini doğrulamak için kullanılmaz?

`assert`, kullanıcının yanlış veri girmesini kontrol etmek için değil, geliştiricinin program içindeki varsayımlarını test etmek için kullanılır.

### Kötü kullanım

```python
yas = int(input("Yaş: "))

assert yas >= 18
```

Bu kontrol güvenilir değildir çünkü Python optimizasyon modunda çalıştırıldığında assertion ifadeleri kaldırılabilir:

```bash
python -O program.py
```

Bu durumda `assert yas >= 18` hiç çalışmayabilir.

### Doğru kullanım

```python
yas = int(input("Yaş: "))

if yas < 18:
    raise ValueError("Yaş 18 veya daha büyük olmalıdır.")
```

> [!warning] Kural
>
> - Kullanıcı girdisi → `if`, `raise`, doğrulama fonksiyonları
>
> - Program içi geliştirici varsayımı → `assert`
>

---

## ⚙️ `python -O` ne yapar?

```bash
python -O dosya.py
```

Python’u optimizasyon modunda çalıştırır.

Bu modda:

- `assert` ifadeleri kaldırılır.

- `__debug__` değeri `False` olur.

- Oluşturulan bytecode dosyasında `.opt-1` etiketi kullanılabilir.


Örnek:

```python
print(__debug__)

assert False

print("Program devam etti.")
```

Normal çalışma:

```bash
python dosya.py
```

Sonuç:

```text
True
Traceback ...
AssertionError
```

Optimizasyon modu:

```bash
python -O dosya.py
```

Sonuç:

```text
False
Program devam etti.
```

> [!danger] Sonuç
> Programın güvenliği `assert` ifadelerine bağlıysa `python -O` kullanıldığında kontrol zinciri bozulabilir.

---

## 📏 Sınır değeri testi

Bir aralık test edilirken yalnızca sınırın kendisini kontrol etmek yetersizdir.

Örneğin sınır `20` ise şu üç değer düşünülmelidir:

```text
19 → sınırın hemen altı
20 → sınırın kendisi
21 → sınırın hemen üstü
```

Bunun sebebi karşılaştırma operatörlerinin kolayca karıştırılabilmesidir:

```python
doluluk < 20
```

ile:

```python
doluluk <= 20
```

aynı koşul değildir.

> [!tip] Üçlü sınır testi
> Her kritik eşikte şunları test et:
>
> ```text
> sınır - 1
> sınır
> sınır + 1
> ```

---

## 🏭 Uygulama — Depo Doluluk Durumu

### Kurallar

|Doluluk|Sonuç|
|--:|---|
|`0`|`"bos"`|
|`1–20`|`"kritik"`|
|`21–80`|`"normal"`|
|`81–100`|`"dolu"`|
|`0` altı veya `100` üstü|`ValueError`|

Burada:

- `20`, kritik aralığına dahildir.

- `80`, normal aralığına dahildir.

- `100`, dolu aralığına dahildir.


### Kod

```python
def depo_durumu(doluluk):
    if doluluk == 0:
        return "bos"
    elif 0 < doluluk <= 20:
        return "kritik"
    elif 20 < doluluk <= 80:
        return "normal"
    elif 80 < doluluk <= 100:
        return "dolu"
    else:
        raise ValueError(
            "Doluluk değeri 0 ile 100 arasında olmalıdır."
        )
```

### Assertion testleri

```python
assert depo_durumu(0) == "bos"
assert depo_durumu(20) == "kritik"
assert depo_durumu(80) == "normal"
assert depo_durumu(100) == "dolu"
```

### Hatalı beklenti testi

```python
assert depo_durumu(100) == "normal"
```

Gerçek sonuç `"dolu"` olduğu için:

```text
AssertionError
```

fırlatılır.

### Geçersiz girişler

```python
depo_durumu(101)
depo_durumu(-1)
```

Her ikisi de:

```text
ValueError
```

fırlatır.

---

## 🧪 Daha sağlam sınır testleri

Yalnızca eşiklerin kendisini test etmek yeterli değildir.

```python
assert depo_durumu(0) == "bos"

assert depo_durumu(1) == "kritik"
assert depo_durumu(19) == "kritik"
assert depo_durumu(20) == "kritik"

assert depo_durumu(21) == "normal"
assert depo_durumu(79) == "normal"
assert depo_durumu(80) == "normal"

assert depo_durumu(81) == "dolu"
assert depo_durumu(99) == "dolu"
assert depo_durumu(100) == "dolu"
```

Geçersiz değerleri kontrol etmek için yalnızca fonksiyonu çağırmak yeterli kanıt üretmez. Exception’ın gerçekten oluştuğu ayrıca doğrulanmalıdır.

Basit manuel kontrol:

```python
try:
    depo_durumu(101)
except ValueError:
    print("Beklenen ValueError oluştu.")
```

---

> [!success] Python yorumu
> Bir assertion’ın geçmesi, fonksiyonun tamamen doğru olduğunu kanıtlamaz.
>
> Yalnızca test edilen giriş için beklenen sonucun üretildiğini gösterir.

---

# 🐧 Linux — `test`, Köşeli Parantez ve `&&`

## 🔇 `test -f` neden ekrana `True` yazmaz?

```bash
test -f day02.py
```

`test` komutu ekrana sonuç yazmak için değil, shell’e exit code göndermek için tasarlanmıştır.

Sonucu görmek için:

```bash
echo $?
```

Dosya varsa:

```text
0
```

Dosya yoksa:

```text
1
```

---

## 📁 `test -f` ve `test -d` farkı

|Kontrol|Anlam|
|---|---|
|`test -f PATH`|Path normal bir dosya mı?|
|`test -d PATH`|Path bir dizin mi?|
|`test -e PATH`|Path herhangi bir türde mevcut mu?|

Örnek:

```bash
test -f day02.py
echo $?
```

Çıktı:

```text
0
```

Aynı path üzerinde dizin testi:

```bash
test -d day02.py
echo $?
```

Çıktı:

```text
1
```

Path mevcuttur fakat doğru türde değildir:

```text
day02.py → dosya olduğu için -f başarılı
day02.py → dizin olmadığı için -d başarısız
```

---

## 🧱 Köşeli parantezlerin çevresinde neden boşluk gerekir?

Bu kullanım:

```bash
[ -f day02.py ]
```

aslında özel bir matematiksel sözdizimi değildir.

`[` shell tarafından bir komut olarak yorumlanır ve `]` bu komutun son argümanıdır.

Shell komutları ve argümanları boşluklarla ayırdığı için şunların hepsi ayrı parçalar olmalıdır:

```text
[
-f
day02.py
]
```

Doğru:

```bash
[ -f day02.py ]
```

Yanlış:

```bash
[-f day02.py]
```

Yanlış:

```bash
[ -f day02.py]
```

> [!important] Zihinsel model
> `[` bir komuttur.
>
> `-f` bir argümandır.
>
> `day02.py` kontrol edilen path’tir.
>
> `]` ise kapanış argümanıdır.

---

## 🔗 `komut1 && komut2`

```bash
komut1 && komut2
```

`komut2`, yalnızca `komut1` başarılı olup `0` exit code’u üretirse çalışır.

Mantık:

```text
Soldaki başarılıysa → sağdakini çalıştır
Soldaki başarısızsa → sağdakini atla
```

Örnek:

```bash
test -f day02.py && python3 day02.py
```

Akış:

```text
day02.py dosya mı?
        │
        ├── Evet → exit code 0 → Python çalışır
        │
        └── Hayır → exit code 1 → Python çalışmaz
```

---

## ⚠️ TIRT Noktası — `test PATH` dosya varlığını kontrol etmez

Aşağıdaki kullanım:

```bash
test "Gelişim/Gelişmiş /day02.py"
```

dosyanın gerçekten mevcut olup olmadığını kontrol etmez.

Tek argümanlı `test STRING`, yalnızca string’in boş olup olmadığını kontrol eder.

Path metni boş olmadığı için dosya mevcut olmasa bile komut başarılı olabilir:

```bash
test "olmayan_dosya.py"
echo $?
```

Muhtemel sonuç:

```text
0
```

Bu nedenle şu kullanım hatalıdır:

```bash
test "Gelişim/Gelişmiş /day02.py" && python3 "Gelişim/Gelişmiş /day02.py"
```

Doğru kontrol:

```bash
test -f "Gelişim/Gelişmiş /day02.py" && \
python3 "Gelişim/Gelişmiş /day02.py"
```

Alternatif:

```bash
[ -f "Gelişim/Gelişmiş /day02.py" ] && \
python3 "Gelişim/Gelişmiş /day02.py"
```

> [!danger] Kafaya kazı
> `test PATH` → string boş mu?
>
> `test -f PATH` → dosya gerçekten var mı ve normal dosya mı?

---

## 🛡️ Path’lerde boşluk kullanımı

Path içinde boşluk varsa tamamını tırnak içine almak en temiz yöntemdir:

```bash
python3 "Gelişim/Gelişmiş /day02.py"
```

Backslash ile de kaçırılabilir:

```bash
python3 Gelişim/Gelişmiş\ /day02.py
```

Ancak uzun veya karmaşık path’lerde tırnak kullanmak daha okunaklıdır.

---

# 🐳 Docker — Container Durumu ve Exit Code

## 🚪 `exited` ne anlama gelir?

Bir container’ın durumunun:

```text
exited
```

olması yalnızca container’ın ana process’inin sona erdiğini gösterir.

Başarılı mı başarısız mı olduğunu tek başına göstermez.

İki container da `exited` olabilir:

```text
container_1 → exited, exit code 0
container_2 → exited, exit code 1
```

Bu yüzden durumla birlikte exit code da kontrol edilmelidir.

---

## 🔎 Container durumunu ve exit code’unu incelemek

```bash
docker inspect \
  --format '{{.State.Status}} {{.State.ExitCode}}' \
  day02_ok
```

Çıktı:

```text
exited 0
```

Şablondaki alanlar:

|Alan|Anlam|
|---|---|
|`.State.Status`|Container’ın mevcut durumu|
|`.State.ExitCode`|Ana process’in çıkış kodu|
|`{{ ... }}`|Go template ifadesi|
|`--format`|Yalnızca seçilen alanları gösterir|

---

## 🔄 `docker run` exit code’u ne zaman terminale taşır?

Container foreground modunda çalıştırıldığında:

```bash
docker run IMAGE KOMUT
```

Docker, container içindeki ana process tamamlanana kadar bekler ve process’in exit code’unu terminale taşır.

```bash
docker run python:3.12-slim \
python -c "assert 3 * 3 == 9"

echo $?
```

Sonuç:

```text
0
```

Başarısız işlem:

```bash
docker run python:3.12-slim \
python -c "assert 3 * 3 == 8"

echo $?
```

Sonuç:

```text
1
```

Detached modda:

```bash
docker run -d IMAGE
```

terminal genellikle container’ın ileride üreteceği exit code’u beklemez. Docker yalnızca container’ın başlatılıp başlatılamadığını bildirir.

---

## 🚨 Docker’ın özel exit code’ları

|Exit code|Anlam|
|--:|---|
|`125`|Docker komutu veya daemon container’ı başlatamadı|
|`126`|Container içindeki komut bulundu fakat çalıştırılamadı|
|`127`|Container içinde çalıştırılmak istenen komut bulunamadı|
|Diğer değerler|Genellikle container process’inin kendi exit code’u|

### Exit code `125`

Örnek durumlar:

- Geçersiz Docker parametresi

- İsim çakışması

- Docker daemon problemi

- Container başlatma hatası


### Exit code `126`

Komut mevcuttur fakat çalıştırma izni veya uygun çalışma biçimi yoktur.

### Exit code `127`

Komut container içinde bulunamamıştır.

> [!important] Ayrım
> `125–127`, Docker’ın başlatma veya komut çalıştırma katmanındaki özel hatalarını ayırmayı kolaylaştırır.

---

## 🗑️ `--rm` neden sonradan inspect yapılmasını engeller?

```bash
docker run --rm IMAGE KOMUT
```

`--rm`, container durduğunda container’ı otomatik olarak siler.

Silinen container üzerinde daha sonra:

```bash
docker inspect CONTAINER
```

veya:

```bash
docker logs CONTAINER
```

çalıştırılamaz çünkü artık container kaydı mevcut değildir.

### Kritik ayrım

`--rm` kullanıldığında çalışırken üretilen traceback’i terminalde görebilirsin.

Ancak container kapandıktan sonra:

- `docker inspect` yapılamaz.

- `docker logs` ile geçmiş çıktı alınamaz.

- Container metadata’sı incelenemez.


Debugging yaparken bu nedenle geçici olarak `--rm` kullanılmayabilir.

---

## 🧪 Başarılı container testi

```bash
docker run --name day02_ok \
python:3.12-slim \
python -c "assert 3 * 3 == 9"
```

Exit code:

```bash
echo $?
```

Çıktı:

```text
0
```

Container incelemesi:

```bash
docker inspect \
  --format '{{.State.Status}} {{.State.ExitCode}}' \
  day02_ok
```

Çıktı:

```text
exited 0
```

---

## 💥 Başarısız container testi

```bash
docker run --name day02_fail \
python:3.12-slim \
python -c "assert 3 * 3 == 8"
```

Çıktı:

```text
Traceback (most recent call last):
  File "<string>", line 1, in <module>
AssertionError
```

Exit code:

```bash
echo $?
```

Çıktı:

```text
1
```

---

## 🧵 Traceback nedir?

Traceback, Python’da bir exception oluştuğunda hatanın:

- Nerede başladığını

- Hangi dosyada meydana geldiğini

- Hangi satırdan geçtiğini

- Son exception türünü


gösteren hata izidir.

```text
Traceback (most recent call last):
  File "<string>", line 1, in <module>
AssertionError
```

Burada:

|Bölüm|Anlam|
|---|---|
|`Traceback`|Hata çağrı zinciri başlıyor|
|`<string>`|Kod bir dosyadan değil, string üzerinden çalıştırıldı|
|`line 1`|Hata birinci satırda oluştu|
|`<module>`|Hata ana program seviyesinde oluştu|
|`AssertionError`|Fırlatılan exception türü|

`python -c` kullanıldığı için dosya adı yerine:

```text
<string>
```

görülür.

---

# 🔗 Entegrasyon — Python Başarılıysa Docker Çalışsın

```bash
python3 day02.py && \
docker run --rm python:3.12-slim \
python -c "print('Yerel kontroller geçti: container çalıştı')"
```

Bu zincirde:

```text
Python testleri
      │
      ├── Exit code 0 → Docker çalışır
      │
      └── Exit code ≠ 0 → Docker hiç çalışmaz
```

---

## ✅ Başarılı senaryo

Python içindeki bütün assertion’lar geçerse:

```text
Yerel kontroller geçti: container çalıştı
```

çıktısı görülür.

Zincirin son komutu da başarılı olduğu için:

```bash
echo $?
```

sonucu:

```text
0
```

olur.

---

## ❌ Başarısız senaryo

Kodda hatalı bir assertion varsa:

```python
assert depo_durumu(100) == "normal"
```

Python:

```text
AssertionError
```

üretir ve `1` exit code’u ile kapanır.

`&&` operatörü nedeniyle Docker komutu çalıştırılmaz.

```bash
echo $?
```

Sonuç:

```text
1
```

> [!success] Entegrasyonun kanıtladığı şey
> Docker’ın çalışması, önceki Python doğrulamalarının başarıyla tamamlandığını gösterir.

---

# 🧯 Hata Avı

## 1. `test PATH` dosya kontrolü sanıldı

TIRT.

```bash
test "day02.py"
```

dosyanın varlığını değil, string’in boş olup olmadığını kontrol eder.

Doğrusu:

```bash
test -f "day02.py"
```

---

## 2. `exited` başarılı anlamına gelmez

```text
exited
```

yalnızca process’in sona erdiğini gösterir.

Mutlaka şuna bakılmalıdır:

```text
State.ExitCode
```

---

## 3. `--rm` traceback’i anında gizlemez

Container foreground çalışıyorsa hata çıktısı terminalde görülür.

`--rm` yalnızca container durduktan sonra metadata ve geçmiş log incelemesini engeller.

---

## 4. Mesajsız `ValueError` zayıf debugging üretir

Şu kullanım çalışır:

```python
raise ValueError
```

Fakat neden hata oluştuğunu anlatmaz.

Daha iyi kullanım:

```python
raise ValueError(
    "Doluluk değeri 0 ile 100 arasında olmalıdır."
)
```

---

# 🧠 Kafaya Kazı

> [!quote]
> Fonksiyonun dönüş değeri, programın exit code’u değildir.

> [!quote]
> `assert`, kullanıcı doğrulaması değil geliştirici varsayımıdır.

> [!quote]
> `python -O`, assertion ifadelerini devre dışı bırakabilir.

> [!quote]
> Sınır testi yalnızca sınırı değil, sınırın altını ve üstünü de kapsar.

> [!quote]
> `test` ekrana `True` yazmaz; sonucu exit code ile bildirir.

> [!quote]
> `&&`, soldaki komut `0` döndürürse sağdaki komutu çalıştırır.

> [!quote]
> Container’ın `exited` olması başarı kanıtı değildir.

> [!quote]
> Docker container process’inin exit code’unu foreground çalışmada terminale taşıyabilir.

---

# 🎓 Cevaplı Ustalık Kontrolü

### `assert` başarısız olduğunda neden yalnızca “sonuç yanlış” denmez?

Çünkü Python yalnızca yanlış bir değer üretmez; program akışını keserek doğrudan:

```text
AssertionError
```

exception’ı fırlatır.

### `python -O` neden assertion tabanlı güvenliği bozar?

Çünkü optimizasyon modunda `assert` ifadeleri kaldırılabilir. Böylece programa eklenen kontrol hiç çalışmadan kod devam edebilir.

### `test -f` neden ekrana çıktı yazmaz?

Çünkü amacı kullanıcıya metin göstermek değil, shell’e başarı veya başarısızlık durumu bildirmektir.

### `&&` neyi kontrol eder?

Soldaki komutun ekrana yazdığı çıktıyı değil, exit code’unu kontrol eder.

### Container `exited` durumundaysa neden exit code’a bakılır?

Çünkü hem başarılı hem de başarısız container process’leri sona erdiğinde `exited` durumuna geçebilir.

---

# 📌 Kısa Özet

|Katman|Başarı nasıl anlaşılır?|
|---|---|
|Python fonksiyonu|Beklenen return değeri|
|Python assertion|Koşul doğruysa sessiz geçiş|
|Linux komutu|Exit code `0`|
|`&&` zinciri|Soldaki komutun exit code’u `0`|
|Docker container|`.State.ExitCode` değeri|
|Başarısız Python kodu|Exception + sıfır dışı exit code|

```text
return → sonuç
exception → hata
exit code → işlem durumu
&& → başarıya bağlı devam
container status → yaşam döngüsü
container exit code → başarı veya başarısızlık
```

---

## 📊 Çalışma Kaydı

|Alan|Değer|
|---|---|
|Yardım seviyesi|`3`|
|Toplam süre|`100–110 dakika`|
|Python|Assertion ve sınır testi|
|Linux|`test`, `$?`, `&&`|
|Docker|Container durumu ve exit code|
|Entegrasyon|Python başarılıysa Docker çalıştırma|
