---
title: "Gün 11 — pathlib, Recursive Dosya Arama, Linux find ve Docker Path Modeli"
tags:
  - coreops
  - python
  - linux
  - docker
  - pathlib
  - find
  - recursive-search
  - bind-mount
aliases:
  - "Gün 11 Pathlib Recursive Arama ve Find"
status: completed
---

# 🧠 Gün 11 — `pathlib`, Recursive Dosya Arama, Linux `find` ve Docker Path Modeli

> [!abstract] 🎯 Ana fikir  
> Bir **path**, dosyanın kendisi değildir; dosyaya ulaşmak için kullanılan adrestir.
> 
> ```text
> Path oluşturmak   → Bir adresi temsil etmek
> exists()          → O adreste gerçekten bir şey var mı?
> is_file()         → Oradaki şey dosya mı?
> is_dir()          → Oradaki şey dizin mi?
> rglob() / find    → Dizin ağacında recursive arama
> ```
> 
> Docker tarafında aynı dosya ağacı:
> 
> ```text
> Host      → /Users/.../project
> Container → /work
> ```
> 
> gibi farklı path string'leri altında görünebilir.
> 
> **Aynı dosya ağacı ≠ aynı path string'i.**

---

# ⚡ 2 Dakikalık Geri Çağırma

## CWD neden önemli?

Göreli path:

```python
Path("data.txt")
```

veya:

```python
open("data.txt")
```

tek başına tam adres değildir.

Başlangıç noktası process'in:

```text
Current Working Directory — CWD
```

değeridir.

Örneğin:

```text
CWD = /Users/polat/project
```

ise:

```text
data.txt
→ /Users/polat/project/data.txt
```

olarak değerlendirilir.

---

# 🐍 Python — `pathlib`

## `Path` nedir?

```python
from pathlib import Path

p = Path("logs/app.txt")
```

Bu satır yalnızca:

```text
logs/app.txt
```

adresini temsil eden bir `Path` nesnesi oluşturur.

Şunları **oluşturmaz**:

```text
logs/ klasörü ❌
app.txt dosyası ❌
```

Gerçek filesystem durumu ayrıca sorgulanmalıdır.

---

# ➗ `/` Operatörü ile Path Birleştirme

```python
from pathlib import Path

p = Path("logs") / "app.txt"
```

sonuç:

```python
Path("logs/app.txt")
```

olur.

Bunu string birleştirme gibi değil:

```text
Path parçalarını işletim sistemine uygun şekilde birleştirme
```

olarak düşün.

---

# 🔍 `exists()`, `is_file()` ve `is_dir()`

Bunlar aynı soruyu sormaz.

|Metot|Sorduğu soru|
|---|---|
|`exists()`|Bu path'te herhangi bir şey var mı?|
|`is_file()`|Bu path normal bir dosya mı?|
|`is_dir()`|Bu path bir dizin mi?|

Örnek:

```python
root = Path("logs")
```

Eğer `logs` gerçek bir dizinse:

```python
root.exists()   # True
root.is_dir()   # True
root.is_file()  # False
```

---

> [!danger] TIRT düşünce  
> `exists() == True` ise bu kesin dosyadır.
> 
> Yanlış.
> 
> O path:
> 
> - Dosya
>     
> - Dizin
>     
> - Symlink
>     
> - Başka bir filesystem nesnesi
>     
> 
> olabilir.

---

# ⚠️ Metodu Çağırmayı Unutma

TIRT:

```python
if x.is_file:
    ...
```

Burada metoda bakıyorsun; metodu çalıştırmıyorsun.

Doğru:

```python
if x.is_file():
    ...
```

Parantez:

```text
Metodu gerçekten çağır
→ True / False sonucunu al
```

demektir.

---

# 🔎 `glob()` ve `rglob()`

## `glob()`

Belirtilen pattern'e göre arama yapar.

```python
root.glob("*.txt")
```

doğrudan ilgili seviyedeki eşleşmeleri arar.

Recursive davranış pattern ile kurulabilir:

```python
root.glob("**/*.txt")
```

---

## `rglob()`

Recursive arama için daha kısa kullanım:

```python
root.rglob("*.txt")
```

Mantığı:

```text
root
├── data.txt        ✅
├── logs/
│   ├── app.txt     ✅
│   └── old/
│       └── old.txt ✅
└── main.py
```

sonucunda üç `.txt` path'i de bulunabilir.

> [!success] Kısa model
> 
> ```text
> glob("*.txt")      → Pattern araması
> rglob("*.txt")     → Recursive pattern araması
> glob("**/*.txt")   → Recursive glob alternatifi
> ```

---

# 🧱 Guard Clause Mantığı

İlk olarak geçersiz root durumlarını dışarı at:

```python
root = Path(path)

if not root.exists():
    raise FileNotFoundError(
        f"Path bulunamadı: {root}"
    )

if not root.is_dir():
    raise NotADirectoryError(
        f"Path bir dizin değil: {root}"
    )
```

Bu iki kontrolü geçtiğimiz anda:

```text
Root var ✅
Root dizin ✅
```

bilgisine sahibiz.

Artık ana algoritma yalnızca arama işiyle uğraşabilir.

---

## TIRT iç içe yapı

```python
if root.exists():
    if root.is_dir():
        for ...
            if ...
                ...
        else:
            ...
    else:
        ...
else:
    ...
```

Bu yapı gittikçe sağa kayan kod üretir.

Guard clause:

```text
Geçersiz durumları başta reddet.
Normal akışı düz bırak.
```

---

# ✅ Günün `txt_bulucu()` Fonksiyonu

```python
from pathlib import Path


def txt_bulucu(path):
    root = Path(path)

    if not root.exists():
        raise FileNotFoundError(
            f"Path bulunamadı: {root}"
        )

    if not root.is_dir():
        raise NotADirectoryError(
            f"Path bir dizin değil: {root}"
        )

    txtler = []

    for aday in root.rglob("*.txt"):
        if aday.is_file():
            txtler.append(aday)

    txtler.sort()
    return txtler
```

Fonksiyon davranışı:

|Durum|Sonuç|
|---|---|
|Root var + `.txt` var|`[Path(...), ...]`|
|Root var + `.txt` yok|`[]`|
|Root yok|`FileNotFoundError`|
|Root var ama dizin değil|`NotADirectoryError`|

---

# 📭 Boş Sonuç Hata Değildir

Dizin:

```text
logs/
├── app.py
└── config.json
```

olsun.

Arama:

```python
txt_bulucu("logs")
```

sonucu:

```python
[]
```

olabilir.

Bu:

```text
Arama başarısız ❌
```

anlamına gelmez.

Doğru anlam:

```text
Arama başarıyla tamamlandı ✅
Eşleşen dosya sayısı = 0
```

> [!important]
> 
> ```text
> Sonuç bulunamadı
> ≠
> Arama yapılamadı
> ```

---

# 💥 Hangi Exception Nerede?

## Root yok

```python
txt_bulucu("olmayan")
```

→

```text
FileNotFoundError
```

## Root var ama dosya

```python
txt_bulucu("data.txt")
```

→

```text
NotADirectoryError
```

## Dizin var ama `.txt` yok

→

```python
[]
```

Hata yok.

---

# 🚫 Hata Durumunda String Döndürme

TIRT:

```python
def txt_bulucu(path):
    if hata:
        return "Path bulunamadı!"
```

Normal durumda fonksiyon:

```python
list[Path]
```

döndürürken hata durumunda:

```python
str
```

döndürmüş olur.

Çağıran taraf artık sürekli tip kontrolü yapmak zorunda kalır.

Daha temiz:

```python
raise FileNotFoundError(...)
```

Böylece sözleşme:

```text
Başarı → list[Path]
Hata   → exception
```

olarak kalır.

---

# 🚨 `FileExistsError` Nerede Yanlış Kullanılır?

Şunu düşünmek TIRT:

```text
“.txt dosyası bulamadım”
→ FileExistsError
```

`FileExistsError` bununla ilgili değildir.

Bu görevde:

```text
Root yok       → FileNotFoundError
Dizin değil    → NotADirectoryError
Txt yok        → []
```

---

# 🔁 `return` Neden Döngünün Dışında?

TIRT:

```python
for aday in root.rglob("*.txt"):
    txtler.append(aday)
    return txtler
```

İlk bulunan dosyadan sonra:

```text
return
↓
Fonksiyon sona erer
↓
Diğer dosyalar aranmaz
```

Doğru:

```python
for aday in root.rglob("*.txt"):
    txtler.append(aday)

return txtler
```

---

# 🔄 Deterministik Sıralama

Filesystem aramasının dönüş sırasına güvenmek istemeyiz.

Bu yüzden:

```python
txtler.sort()
```

kullanılır.

Örneğin bulma sırası:

```text
services.txt
data.txt
out.txt
```

olsa bile sonuç:

```text
data.txt
out.txt
services.txt
```

şeklinde sabitlenebilir.

---

## Neden önemli?

Özellikle:

- Testlerde
    
- Host/container karşılaştırmasında
    
- Snapshot çıktılarında
    
- `diff` kullanımında
    

aynı mantıksal sonuçların aynı sırada olması işleri kolaylaştırır.

> [!important]  
> Deterministik çıktı:
> 
> **Aynı girdi → öngörülebilir aynı sıralama**

---

# ⚠️ Her `append()` Sonrası `sort()` Yapma

TIRT:

```python
for aday in ...:
    txtler.append(aday)
    txtler.sort()
```

Bu durumda liste tekrar tekrar sıralanır.

Daha mantıklı:

```text
Bütün dosyaları bul
↓
Listeyi oluştur
↓
Bir kere sırala
↓
Return
```

---

# 🧠 Günün Python Hataları

## 1. Parametre alıp kullanmamak

TIRT:

```python
def txt_bulucu(path):
    root = Path("Gelişmiş")
```

Doğru:

```python
root = Path(path)
```

---

## 2. `x.is_file`

TIRT.

Doğru:

```python
x.is_file()
```

---

## 3. Döngü içinde `sort()`

Gereksiz tekrar.

Arama sonunda bir kez sırala.

---

## 4. Döngü içinde `return`

İlk sonuçta fonksiyonu sonlandırır.

---

## 5. Boş listeyi hata sanmak

```python
[]
```

geçerli bir sonuçtur.

---

## 6. Hata durumunda string döndürmek

Fonksiyonun return tipini bozar.

---

# 🐧 Linux — `find`

Temel komut:

```bash
find . -type f -name '*.txt'
```

Bunu şu formülle düşün:

```text
find
=
Nereden başlayacağım?
+
Hangi koşullara uyanları istiyorum?
```

Yani:

```text
find . -type f -name '*.txt'
     │    │          │
     │    │          └─ İsmi nasıl?
     │    └──────────── Türü ne?
     └───────────────── Nereden başla?
```

**`find = Starting Point + Tests`**

---

# 📍 `find .` İçindeki `.`

```bash
find .
```

Buradaki:

```text
.
```

mevcut çalışma dizinidir.

Yani:

> “Buradan başla ve altındaki dizin ağacını recursive tara.”

Başka başlangıç noktası:

```bash
find /tmp
```

Bu kez arama `/tmp` altında başlar.

> [!danger]  
> `find` otomatik olarak bütün diski taramaz.
> 
> Arama kapsamını başlangıç noktası belirler.

---

# 📦 `-type`

```bash
-type f
```

yalnızca normal dosyaları seçer.

|Kullanım|Nesne|
|---|---|
|`-type f`|Normal dosya|
|`-type d`|Dizin|
|`-type l`|Symlink|

---

# 🔎 `-name '*.txt'`

```bash
-name '*.txt'
```

yalnızca **isme** bakar.

Şunların ikisi de ismen eşleşebilir:

```text
rapor.txt      ← dosya
arsiv.txt/     ← dizin
```

Bu nedenle yalnız dosya istiyorsak:

```bash
find . -type f -name '*.txt'
```

kullanılır.

---

# 🔗 `find` Testleri AND Mantığı

```bash
find . -type f -name '*.txt'
```

kabaca:

```text
Normal dosya mı?
     VE
Adı *.txt mi?
```

anlamına gelir.

İki koşul da sağlanırsa sonuç gösterilir.

---

# ❗ `*.txt` Neden Quote Edilir?

Doğru:

```bash
find . -name '*.txt'
```

TIRT/riskli:

```bash
find . -name *.txt
```

Çünkü `*` karakteri shell glob pattern'idir.

Dizinde:

```text
a.txt
b.txt
```

varsa shell daha `find` çalışmadan:

```text
*.txt
```

ifadesini:

```text
a.txt b.txt
```

haline getirebilir.

Quote:

```text
Shell bu pattern'e dokunma.
Aynen find programına gönder.
```

demektir.

Sonrasında wildcard yorumunu `find` yapar.

---

# 🐍 `rglob()` ile `find` Karşılaştırması

Python:

```python
Path(".").rglob("*.txt")
```

Linux:

```bash
find . -name '*.txt'
```

mantıksal olarak benzerdir.

Ancak birebir karşılaştırma için aynı şartları vermek gerekir.

---

## Aynı olması gereken kapsamlar

```text
1. Başlangıç noktası
2. Pattern
3. Recursive kapsam
4. Nesne türü
5. Gerekirse symlink davranışı
```

Örneğin Linux:

```bash
find . -type f -name '*.txt'
```

yalnız dosya arıyor.

Python:

```python
Path(".").rglob("*.txt")
```

pattern'e uyan path'leri getiriyor.

Birebir eşlemek için:

```python
for path in Path(".").rglob("*.txt"):
    if path.is_file():
        ...
```

kullanılır.

---

# 🧪 Gerçek Linux Deneyi

Üst dizinde:

```bash
find . -type f -name '*.txt'
```

çalıştırıldığında yalnız `Gelişmiş` klasörü değil, aynı root altındaki başka proje ve `.venv` dizinlerinden de çok sayıda `.txt` sonucu geldi.

Ardından:

```bash
cd Gelişmiş
```

yapılıp tekrar:

```bash
find . -type f -name '*.txt'
```

çalıştırıldığında arama yalnız bu ağaca daraldı.

> [!success] Kritik ders  
> Aynı `find` komutunun sonucu CWD değiştiğinde değişebilir çünkü `.` farklı başlangıç noktasını temsil eder.

---

# 🔃 Linux Sonucunu Deterministik Yapmak

```bash
find . -type f -name '*.txt' | sort
```

Böylece `find` çıktısı sıralanır.

Python:

```python
txtler.sort()
```

Linux:

```bash
... | sort
```

aynı ihtiyacı karşılar:

```text
Karşılaştırılabilir, deterministik çıktı
```

---

# 🐳 Docker — Aynı Dosya Ağacı, Farklı Path

Hostta proje:

```text
/Users/polat/CODING/Gelişim/Gelişmiş
```

altında bulunabilir.

Container'a:

```bash
--mount type=bind,source="$PWD",target=/work
```

ile bağlandığında aynı içerik container tarafından:

```text
/work
```

olarak görülür.

> [!important]
> 
> ```text
> Path dosyanın kendisi değildir.
> Path, dosyaya kullanılan adrestir.
> ```

---

# 🔗 Source ve Target

```bash
--mount type=bind,source="$PWD",target=/work
```

## `source`

```text
Host filesystem'inde kaynak nerede?
```

## `target`

```text
Container filesystem görünümünde nerede görünsün?
```

Örnek:

```text
HOST                                  CONTAINER

/Users/polat/project       ───────▶   /work
├── day11.py                          ├── day11.py
├── data.txt                          ├── data.txt
└── services.txt                     └── services.txt
```

Bunlar bağımsız kopyalar değildir.

---

# 📍 `-w /work`

```bash
-w /work
```

mount oluşturmaz.

Yalnızca container içinde başlayan process'in:

```text
Current Working Directory
```

değerini `/work` yapar.

Bu nedenle:

```text
target=/work
→ Dosyaları /work'te göster.

-w /work
→ Programı /work'ten başlat.
```

İki seçenek birbirinden bağımsızdır.

---

# 🐍 `Path.cwd()`

Python:

```python
from pathlib import Path

print(Path.cwd())
```

çalıştığı ortamın CWD'sini gösterir.

Host:

```text
/Users/polat/.../Gelişmiş
```

Container:

```text
/work
```

döndürebilir.

Bu sonuçlar farklıdır ama:

```text
Aynı bind mount edilmiş dosya ağacına
```

işaret edebilir.

---

# 🧪 Docker Deneyi

Container:

```bash
docker run --rm -it \
  --mount type=bind,source="$PWD",target=/work,readonly \
  -w /work \
  python:3.12-slim \
  sh
```

İçeride:

```bash
python day11.py
```

ve:

```bash
find . -type f -name '*.txt'
```

çalıştırıldı.

İki araç da aynı 12 `.txt` dosyasını buldu.

---

# ⚠️ `lsa` Hatası

Container içinde:

```bash
lsa
```

çalıştırıldığında:

```text
sh: 1: lsa: not found
```

alındı.

Sebep:

```text
lsa
```

standart bir komut değildir.

Doğru:

```bash
ls
```

Bu hata:

```text
Filesystem veya mount problemi
```

değil, shell'in komutu bulamamasıdır.

---

# 🔒 `readonly`

Mount:

```bash
--mount type=bind,source="$PWD",target=/work,readonly
```

olduğu için container:

```text
Dosyaları okuyabilir ✅
Recursive arayabilir ✅
stat/is_file kullanabilir ✅
Python listesi oluşturabilir ✅

Dosyaları değiştiremez ❌
Mount içine yeni dosya yazamaz ❌
```

Arama yalnızca okuma gerektirdiğinden read-only mount yeterlidir.

---

# 🔗 Entegrasyon

Host Python:

```bash
python day11.py
```

Host Linux:

```bash
find . -type f -name '*.txt' | sort
```

Container Python:

```bash
python day11.py
```

Container Linux:

```bash
find . -type f -name '*.txt' | sort
```

dört kontrolün tamamı aynı mantıksal `.txt` dosya kümesini verdi.

> [!success]  
> Buradaki güçlü nokta yalnızca Python'ın host/container arasında aynı çalışması değil.
> 
> Python sonucu ayrıca **bağımsız Linux `find` aracıyla** doğrulandı.

---

# ⚠️ Aynı Path Çıktısını Bekleme

Python hostta:

```python
Path("data.txt")
```

gösterirken Linux:

```text
./data.txt
```

gösterebilir.

Bunlar string olarak aynı değildir.

Ancak ikisi de aynı CWD içindeki aynı dosyayı gösterebilir.

Karşılaştırma yaparken:

```text
Path gösterim biçimi
```

ile:

```text
Mantıksal dosya kimliği/kümesi
```

karıştırılmamalıdır.

---

# 🧯 Hata Avı

## 1. `Path()` dosya oluşturur

TIRT.

Yalnızca path nesnesi oluşturur.

---

## 2. `exists()` ile `is_file()` aynı şeydir

TIRT.

Biri varlığı, diğeri nesne türünü sorgular.

---

## 3. `x.is_file` dosya kontrolü yapar

TIRT.

Metodu çağırmak gerekir:

```python
x.is_file()
```

---

## 4. `.txt` bulunamadıysa exception gerekir

TIRT.

Geçerli boş sonuç:

```python
[]
```

döndürülebilir.

---

## 5. Hata durumunda string döndürmek temizdir

TIRT.

Normal dönüş tipini bozar.

---

## 6. `FileExistsError` `.txt` bulunamadığında kullanılır

TIRT.

Bu senaryoyla ilgisi yoktur.

---

## 7. `sort()` her eklemeden sonra yapılmalıdır

TIRT.

Bütün sonuçlar toplandıktan sonra bir kez sırala.

---

## 8. `return` döngünün içine yazılır

TIRT.

İlk eşleşmede fonksiyon biter.

---

## 9. `find .` her zaman aynı kapsamı arar

TIRT.

`.` o anki CWD'dir.

CWD değişirse başlangıç noktası değişir.

---

## 10. `-name '*.txt'` yalnızca dosyaları bulur

TIRT.

İsme bakar. Dosya sınırlaması için:

```bash
-type f
```

eklenir.

---

## 11. `*.txt` quote edilmezse daha iyidir

TIRT.

Shell pattern'i `find` çalışmadan genişletebilir.

---

## 12. Bind mount `-w` değerini otomatik ayarlar

TIRT.

İki mekanizma bağımsızdır.

---

## 13. Host ve container aynı dosyayı kullanıyorsa absolute path aynı olmalıdır

TIRT.

Aynı kaynak farklı filesystem görünümlerinde farklı path ile temsil edilebilir.

---

# 🧠 Kafaya Kazı

> [!quote]  
> Path nesnesi, dosyanın kendisi değil adresinin modelidir.

> [!quote]  
> `Path()` oluşturmak ile dosyanın gerçekten var olması iki farklı şeydir.

> [!quote]  
> `exists()` varlığı, `is_file()` türü kontrol eder.

> [!quote]  
> `rglob()` alt dizinlere recursive iner.

> [!quote]  
> Geçersiz girdileri guard clause ile erken reddet.

> [!quote]  
> Boş sonuç hata olmak zorunda değildir.

> [!quote]  
> Başarılı fonksiyon dönüş tipi tutarlı kalmalıdır.

> [!quote]  
> Deterministik sonuç test ve karşılaştırmayı kolaylaştırır.

> [!quote]  
> `find = Starting Point + Tests`.

> [!quote]  
> `.` mevcut çalışma dizinidir.

> [!quote]  
> `-type f` türü, `-name` ismi filtreler.

> [!quote]  
> Pattern quote edilirse wildcard'ı `find` yorumlar.

> [!quote]  
> Python ve Linux sonucunu karşılaştırırken kapsamları eşitle.

> [!quote]  
> Bind mount aynı dosya ağacını farklı container path'inde gösterebilir.

> [!quote]  
> Source, target ve workdir üç farklı soruyu cevaplar.

---
# 📌 30 Saniyelik Özet

```text
PYTHON PATHLIB
Path(...)           → Path nesnesi oluştur
exists()            → Var mı?
is_file()           → Dosya mı?
is_dir()            → Dizin mi?
glob()              → Pattern ara
rglob()             → Recursive ara
sort()              → Deterministik sıra

HATA MODELİ
Root yok            → FileNotFoundError
Root dosya          → NotADirectoryError
Txt yok             → []

TASARIM
Guard clause        → Geçersizi erken reddet
raise               → Hatayı üst katmana taşı
return list[Path]   → Başarılı sonucu tutarlı döndür

LINUX
find .              → Buradan recursive başla
-type f             → Normal dosya
-name '*.txt'       → İsim pattern'i
quotes              → Shell glob expansion engelle
| sort              → Deterministik çıktı

DOCKER
source              → Hostta nerede?
target              → Container'da nerede görünsün?
-w                  → Process nereden çalışsın?
Path.cwd()          → O ortamın CWD'si

KRİTİK
Aynı dosya ağacı
≠
Aynı absolute path
```

---

# ✅ Günün Kazanımları

-  `Path` nesnesi ile gerçek filesystem nesnesi ayrıldı
    
-  `/` operatörüyle path birleştirme öğrenildi
    
-  `exists()`, `is_file()` ve `is_dir()` ayrıldı
    
-  Metot ile metot çağrısı farkı tekrar edildi
    
-  `glob()` ve `rglob()` kapsamları ayrıldı
    
-  Recursive `.txt` arama uygulandı
    
-  Guard clause yaklaşımı kullanıldı
    
-  Root yok ve root dizin değil durumları ayrıldı
    
-  Boş arama sonucunun hata olmadığı kavrandı
    
-  Tutarlı return tipi önemi anlaşıldı
    
-  Döngü içinde yanlış `return` riski görüldü
    
-  Arama sonucu deterministik hâle getirildi
    
-  Linux `find` başlangıç noktası mantığı öğrenildi
    
-  `-type` ve `-name` görevleri ayrıldı
    
-  Shell glob expansion nedeniyle quote kullanımının nedeni anlaşıldı
    
-  Python `rglob()` sonucu `find` ile bağımsız doğrulandı
    
-  CWD değişince `find .` kapsamının değiştiği görüldü
    
-  Host source ile container target path'lerinin farklı olabileceği kavrandı
    
-  Bind mount ile `-w` bir kez daha ayrıldı
    
-  `Path.cwd()` sonucunun ortamdan ortama değişebileceği görüldü
    
-  Farklı absolute path'lerin aynı mantıksal dosya ağacını gösterebildiği kavrandı
    

> [!success] 🚀 Gün sonu sonucu  
> Gün 11 sonunda path artık yalnızca bir string olarak değil, **bir filesystem adres modeli** olarak düşünülmeye başlandı.
> 
> Python `pathlib` ile recursive arama yapılırken Linux `find` bağımsız doğrulama aracı olarak kullanıldı. Docker deneyinde ise aynı dosya ağacının host ve container tarafından farklı absolute path'lerle görülebileceği doğrulandı.
> 
> Günün en önemli modeli:
> 
> ```text
> Path → Adres
> File → O adresteki nesne
> CWD → Göreli adresin başlangıç noktası
> Mount → Aynı kaynağı başka filesystem adresinde gösterme
> ```