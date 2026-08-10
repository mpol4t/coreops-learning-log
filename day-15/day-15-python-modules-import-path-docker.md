---
title: "Gün 15 — Python Modülleri, Import Path ve Docker"
tags:
  - coreops
  - python
  - linux
  - docker
  - modules
  - import
  - sys-path
  - cwd
  - workdir
aliases:
  - "Gün 15 Python Modülleri Import Path ve Docker"
status: completed
---

# 🧩 Gün 15 — Python Modülleri, `import`, `__name__`, CWD ve Docker Import Zinciri

> [!abstract] 🎯 Ana fikir  
> Bugünün en önemli ayrımı:
> 
> ```text
> Dosyanın filesystem'de var olması
> ≠
> Python'ın onu import edebilmesi
> ```
> 
> Bir import problemi yaşandığında üç ayrı katmanı düşün:
> 
> ```text
> 1. Dosya gerçekten image/filesystem içinde mi?
> 2. Program hangi dizinden çalışıyor?
> 3. Python hangi dizinlerde modül arıyor?
> ```
> 
> Docker için kısa formül:
> 
> **Build context + COPY → Container filesystem/CWD → Python `sys.path`**

---

# ⚡ 2 Dakikalık Geri Çağırma

## `Path.is_file` ile `Path.is_file()` aynı şey değildir

```python
path.is_file
```

→ Metodun kendisine referanstır.

```python
path.is_file()
```

→ Metodu gerçekten çağırır ve dosyanın normal dosya olup olmadığını kontrol eder.

> [!danger] TIRT  
> Metot çağrısını unutup:
> 
> `if path.is_file:`
> 
> yazmak gerçek filesystem kontrolü yapmaz.

---

# 🐍 Python — Modül Nedir?

Bir `.py` dosyası başka Python kodları tarafından import edilip kullanılabiliyorsa **modül** olarak düşünülebilir.

Örneğin:

```text
scanner.py
```

bir Python modülü olabilir.

Başka bir dosyada:

```python
import scanner
```

ile yüklenebilir.

---

# 📥 İki Import Biçimi

## Modülü import etmek

```python
import scanner
```

Namespace'e:

```text
scanner
```

adı gelir.

Kullanım:

```python
scanner.find_txt_files()
```

---

## Modülden belirli bir şeyi import etmek

```python
from scanner import find_txt_files
```

Namespace'e doğrudan:

```text
find_txt_files
```

adı gelir.

Kullanım:

```python
find_txt_files()
```

Kaynak nottaki temel ayrım da budur.

---

# 🧠 Namespace Nedir?

Basit model:

```text
import scanner
```

sonrasında:

```text
scanner
```

adı benim mevcut kodumda kullanılabilir hâle gelir.

Ama:

```python
from scanner import find_txt_files
```

yaparsam doğrudan:

```text
find_txt_files
```

adı gelir.

Kısaca:

```text
import modül
→ modül.fonksiyon()

from modül import fonksiyon
→ fonksiyon()
```

---

# ⚙️ Import Sırasında Ne Olur?

Python bir modülü ilk kez import ederken kabaca:

```text
Modül daha önce yüklenmiş mi?
        ↓
Import sistemi modülü bulabilir mi?
        ↓
Modülün üst seviye kodu çalıştırılır
        ↓
Fonksiyon / class tanımları oluşturulur
        ↓
Modül kullanıma hazır hâle gelir
```

Önemli ayrım:

```python
def tara():
    print("Tarama")
```

import sırasında fonksiyonun **gövdesini çalıştırmaz**.

Yalnızca `tara` fonksiyonunu tanımlar.

Ama:

```python
print("scanner yüklendi")
```

gibi modül seviyesindeki kod import sırasında çalışır.

---

# 🏷️ Her Modülün Kendi `__name__` Değeri Vardır

Bu kritik.

```text
main.py
scanner.py
```

olsun.

Terminal:

```bash
python main.py
```

ile başlatıldığında:

```text
main.py
→ __name__ == "__main__"

scanner.py
→ import edildiği modül adı
```

olur.

Örneğin package yapısında:

```text
src.scanner
```

olabilir.

> [!important]  
> `__name__`, bütün programın paylaştığı tek ortak değişken değildir.
> 
> **Her modülün kendi `__name__` değeri vardır.**

---

# 🚪 `if __name__ == "__main__":`

```python
if __name__ == "__main__":
    main()
```

şu anlama gelmez:

> “Python kodu buradan okumaya başlasın.”

Python dosyayı yine **yukarıdan aşağıya işler.**

Gerçek anlam:

> “Bu modül doğrudan çalıştırıldıysa `main()` fonksiyonunu çağır.”

---

# 🔄 Çalışma Sırası

```python
import scanner


def main():
    print("Program başladı")


if __name__ == "__main__":
    main()
```

Akış:

```text
import scanner
      ↓
scanner modülü yüklenir
      ↓
main fonksiyonu tanımlanır
      ↓
if satırına ulaşılır
      ↓
__name__ == "__main__" ?
      ↓
True
      ↓
main() çağrılır
```

Kaynak notta bu ayrım açık şekilde kurulmuş.

---

# 🧱 `def main()` vs `main()`

```python
def main():
    ...
```

→ Fonksiyonu **tanımlar**.

```python
main()
```

→ Fonksiyonu **çalıştırır**.

Bu yüzden Python'ın dosyayı yukarıdan aşağı işlemesi ile `main()` fonksiyonunun daha sonra çalışması çelişmez.

---

# 🔄 Scanner Import Edilince Main'in `__name__` Değeri Değişir mi?

Hayır.

```python
import scanner

print(__name__)
print(scanner.__name__)
```

Doğrudan `main.py` çalıştırılırsa örneğin:

```text
__main__
scanner
```

görülebilir.

Package yapısına göre scanner'ın tam adı:

```text
src.scanner
```

da olabilir.

Scanner'ı import etmek main modülünün `__name__` değerini scanner yapmaz.

---

# 📂 Alt Klasörden Import

Proje:

```text
day15/
├── main.py
└── src/
    ├── __init__.py
    └── scanner.py
```

Filesystem yolu:

```text
src/scanner.py
```

Python modül yolu:

```text
src.scanner
```

> [!danger] TIRT
> 
> ```python
> from /src/scanner import scanner
> ```
> 
> Python import sözdizimi değildir.

Doğru örnek:

```python
from src.scanner import scanner
```

Kaynak kodda kullanılan yapı da buydu.

---

# 📁 Dosya Yolu vs Modül Yolu

```text
FILESYSTEM
src/scanner.py

PYTHON IMPORT
src.scanner
```

Filesystem tarafında:

```text
/
```

kullanılır.

Python modül yolunda:

```text
.
```

kullanılır.

---

# 📦 `__init__.py`

Örneğin:

```text
src/
├── __init__.py
└── scanner.py
```

şeklinde kullanmak `src` dizininin bir Python package'ı olarak açık ve klasik biçimde tanımlanmasını sağlar.

> [!note]  
> Modern Python'da bazı package yapıları `__init__.py` olmadan da namespace package olarak çalışabilir.
> 
> Ancak eğitim ve klasik proje yapısında `__init__.py` kullanmak package sınırını açık hâle getirir.

---

# 🧱 Günün Modüler Yapısı

```text
main.py
│
├── Program akışını yönetir
├── scanner fonksiyonunu çağırır
├── Sonucu kullanıcıya gösterir
├── Exception'ları yorumlar
└── Exit code üretir

src/scanner.py
│
├── Root kontrolünü yapar
├── Recursive arama yapar
├── .txt dosyalarını bulur
└── Sonucu return eder
```

Bu yalnızca:

> “Kodu iki dosyaya böldüm.”

değildir.

Gerçek kazanım:

```text
Sorumluluk sınırı
```

oluşturmaktır.

---

# 🎻 `main.py` Orkestra Şefi

Kaynak ustalık cevabındaki iyi zihinsel model:

> Scanner kendi işini yapar; `main.py` ise modülleri birleştirip uygulamayı çalıştıran orkestra şefidir.

Yani:

```text
scanner.py
→ NASIL tarayacağını bilir.

main.py
→ NE ZAMAN tarama yapılacağını
  ve sonuçla ne yapılacağını bilir.
```

---

# ✅ Günün `scanner.py` Yapısı

```python
from pathlib import Path


def scanner(root):
    root = Path(root)

    if not root.exists():
        raise FileNotFoundError

    if not root.is_dir():
        raise NotADirectoryError

    dosyalar = []

    for path in sorted(
        root.rglob("*.txt")
    ):
        if path.is_file():
            relative = path.relative_to(
                root
            )
            dosyalar.append(relative)

    return dosyalar
```

Bu fonksiyon:

```text
Print yapmıyor
Exit code seçmiyor
sys.exit çağırmıyor
```

Yalnızca işini yapıp sonucu döndürüyor.

---

# ✅ Günün `main.py` Yapısı

```python
from src.scanner import scanner
import sys


def main():
    try:
        sonuc = scanner(".")
        print(sonuc)
        return 0

    except FileNotFoundError:
        print(
            "Girilen path bulunamadı!",
            file=sys.stderr,
        )
        return 11

    except NotADirectoryError:
        print(
            "Girilen path directory değil!",
            file=sys.stderr,
        )
        return 22


if __name__ == "__main__":
    sys.exit(main())
```

---

# ⚠️ Kaynak Koddaki Küçük Exit Code Detayı

Kaynak kodun başarı tarafında:

```python
return
```

bulunuyordu.

Bu:

```python
return None
```

ile aynıdır.

Sonrasında:

```python
sys.exit(None)
```

process açısından başarı (`0`) ile sonuçlanabilir.

Yani mevcut kod çalışabilir.

Ama sözleşmeyi açık yazmak daha okunaklıdır:

```python
return 0
```

Böylece:

```text
Başarı → 0
FileNotFoundError → 11
NotADirectoryError → 22
```

doğrudan koddan okunabilir.

---

# 🐧 Linux — CWD ile Script Dizini Aynı Değil

## `pwd`

```bash
pwd
```

script'in bulunduğu klasörü değil:

```text
Process'in CWD'sini
```

gösterir.

Örnek:

```bash
cd /tmp
python /project/main.py
```

Burada:

```text
CWD        → /tmp
Script     → /project/main.py
Script dir → /project
```

Dolayısıyla:

```text
CWD ≠ Script directory
```

olabilir.

---

# 🔎 `find` Ne Kanıtlar?

```bash
find . -name 'scanner.py'
```

şunu kanıtlar:

> CWD'den başlayan filesystem ağacında `scanner.py` adında bir dosya var.

Ama şunu kanıtlamaz:

> Python `import scanner` dediğimde bu modülü bulabilir.

Çünkü `find` ve Python import sistemi farklı mekanizmalardır.

---

# 🧠 İki Ayrı Path Katmanı

## 1. Filesystem Path

Soru:

> Dosya fiziksel olarak nerede?

Araçlar:

```bash
pwd
find .
ls
```

Python:

```python
Path.cwd()
```

---

## 2. Python Import Path

Soru:

> Python modülü hangi dizinlerde arıyor?

Kontrol:

```bash
python -c \
'import sys; print(*sys.path, sep="\n")'
```

Temel veri:

```python
sys.path
```

---

> [!danger] TIRT
> 
> ```text
> find scanner.py dosyasını buldu
>          ↓
> Python kesin import eder
> ```
> 
> Yanlış.
> 
> ```text
> find     → Filesystem araması
> import   → Python import sistemi
> ```

Kaynak notta bu iki katman özellikle ayrılmış.

---

# 🧪 CWD Değiştirme Deneyi

Day15 içinden:

```bash
python main.py
```

sonucu:

```text
data/a.txt
data/nested/c.txt
```

oldu.

Sonra parent dizinden:

```bash
python day15/main.py
```

çalıştırıldı.

Import yine başarılı oldu ancak `scanner(".")` nedeniyle tarama root'u artık parent CWD oldu ve çok daha fazla `.txt` dosyası bulundu.

---

# 🔥 Deneyden Çıkan Kritik Ders

İlk tahmin:

> “Başka CWD'den çalıştırırsam `src.scanner` bulunamaz.”

yanlış çıktı.

Asıl olan:

```text
Import başarılı kaldı ✅

scanner(".") davranışı değişti ✅
```

Neden?

Çünkü burada iki farklı mekanizma var:

```text
from src.scanner import scanner
→ Python import sistemi

scanner(".")
→ "." relative filesystem path
→ Process CWD
```

---

# 📌 Göreli Path'in Değişen Anlamı

Day15 dizinindeyken:

```text
.
→ day15/
```

Parent'tayken:

```text
.
→ Gelişmiş/
```

Bu yüzden aynı kod:

```python
scanner(".")
```

çok farklı dosya kümeleri döndürdü.

> [!important]  
> Import'un çalışmasıyla fonksiyona verdiğin relative filesystem path'in aynı mekanizma olduğunu düşünme.

---

# 🔧 Import Hatasında Hızlı Kontrol

```bash
pwd
find . -name 'scanner.py'
python -c \
'import sys; print(*sys.path, sep="\n")'
```

Sorular:

```text
pwd
→ Ben nereden çalışıyorum?

find
→ Dosya fiziksel olarak nerede?

sys.path
→ Python nerelerde modül arıyor?
```

Bu üçlü çok güçlü bir debug başlangıcıdır.

---

# 🐳 Docker — Python Modül Yapısını Image'a Taşımak

Host:

```text
day15/
├── main.py
├── data/
└── src/
    └── scanner.py
```

Container:

```text
/day15_work/
├── main.py
├── data/
└── src/
    └── scanner.py
```

olabilir.

Host absolute path:

```text
/Users/polat/.../day15/src/scanner.py
```

Container:

```text
/day15_work/src/scanner.py
```

olabilir.

Absolute path'lerin aynı olması gerekmez.

Önemli olan gerekli proje yapısının container'a taşınmasıdır.

---

# 📄 Günün Dockerfile'ı

```dockerfile
FROM python:3.12-slim

WORKDIR /day15_work

COPY . .

CMD ["python", "main.py"]
```

Build:

```bash
docker build -t day15 .
```

Run:

```bash
docker run --rm day15
```

Container sonucu:

```text
data/a.txt
data/nested/c.txt
```

Host sonucu ile aynı mantıksal dosya kümesini verdi.

---

# 📂 `WORKDIR`

```dockerfile
WORKDIR /day15_work
```

şunu yapar:

```text
Process / sonraki relative işlemler için
çalışma dizini = /day15_work
```

Ama dosya kopyalamaz.

> [!danger] TIRT
> 
> ```text
> WORKDIR /day15_work
> → Host kodunu buraya getirir
> ```
> 
> Yanlış.

Dosyaların image'a gelmesi:

```dockerfile
COPY ...
```

işidir.

---

# 📦 `COPY . .`

İlk `.`:

```text
Build context içeriği
```

İkinci `.`:

```text
Image içindeki mevcut WORKDIR
```

Burada:

```text
Build context
      ↓
COPY
      ↓
/day15_work
```

olur.

Bu yüzden:

```text
main.py
src/scanner.py
data/a.txt
data/nested/c.txt
```

container filesystem'ine geldi.

---

# 💥 `src/` Image'a Alınmazsa

Örneğin:

```dockerfile
WORKDIR /app

COPY main.py .

CMD ["python", "main.py"]
```

ama `main.py`:

```python
from src.scanner import scanner
```

diyorsa image içinde `src/` yoksa runtime'da tipik olarak:

```text
ModuleNotFoundError:
No module named 'src'
```

görülebilir.

---

# ⚠️ Build Neden Yine Başarılı Olabilir?

Bu çok önemli.

Docker build sırasında:

```text
main.py kopyalandı mı?
Dockerfile talimatları geçerli mi?
```

gibi build işleri yapılır.

Ama build sırasında:

```text
main.py mutlaka execute edilmek zorunda değildir.
```

Dolayısıyla:

```text
src/scanner.py image'da yok
```

olsa bile Dockerfile'da bunu build sırasında doğrulayan bir `RUN` adımı yoksa image build edilebilir.

Hata:

```text
docker run
→ CMD
→ python main.py
→ import
→ ModuleNotFoundError
```

zincirinde **runtime** sırasında ortaya çıkabilir.

> [!important] Ustalık sorusunun daha net cevabı  
> Scanner'ın olmaması gerçekten **build context / COPY kaynaklı bir image içeriği problemidir**, fakat bunun **görünür hata verdiği aşama runtime olabilir**.
> 
> Yani:
> 
> ```text
> Kök neden → Build sırasında scanner image'a alınmadı.
> Hatanın görüldüğü yer → Runtime import.
> ```
> 
> Bu ikisini ayırmak önemli.

---

# 🔎 Hostta Import Çalışıyor, Container'da Patlıyor: 3 Katman

Kaynak nottaki en güçlü debug modeli:

## 1. Build Context + `COPY`

Sor:

```text
scanner.py build context içinde miydi?
.dockerignore dışladı mı?
COPY gerçekten src/ dizinini image'a aldı mı?
```

---

## 2. Container Filesystem + CWD

Container'da:

```bash
pwd
find . -maxdepth 3 -type f
```

Sor:

```text
main.py nerede?
scanner.py nerede?
WORKDIR ne?
Dizin ilişkisi doğru mu?
```

---

## 3. Python `sys.path`

```bash
python -c \
'import sys; print(*sys.path, sep="\n")'
```

Sor:

> Python `src` package'ının parent dizinine bakıyor mu?

---

# 🧠 Üç Katmanlık Formül

```text
Dosya IMAGE'A GELDİ Mİ?
        ↓
Container'da DOĞRU YERDE Mİ?
        ↓
Python O YERİ ARIYOR MU?
```

Daha teknik:

```text
Build context / COPY
        ↓
Filesystem / WORKDIR / CWD
        ↓
sys.path / package / import
```

---

# 🧯 Hata Avı

## 1. `.py` dosyası başka klasördeyse import edilemez

TIRT.

Package yapısı ve import yolu doğruysa alt klasörden import edilebilir.

---

## 2. Python import yolunda `/` kullanılır

TIRT.

Filesystem:

```text
src/scanner.py
```

Python import:

```text
src.scanner
```

---

## 3. `__name__` bütün program için tek değerdir

TIRT.

Her modülün kendi `__name__` değeri vardır.

---

## 4. `if __name__ == "__main__"` Python'ın başlangıç satırıdır

TIRT.

Python yine dosyayı yukarıdan aşağı işler.

Guard yalnızca dosyanın doğrudan mı çalıştırıldığını kontrol eder.

---

## 5. `def main()` main fonksiyonunu çalıştırır

TIRT.

Yalnızca tanımlar.

```python
main()
```

çalıştırır.

---

## 6. `find scanner.py` buluyorsa `import scanner` kesin çalışır

TIRT.

Filesystem ve import sistemi farklı katmanlardır.

---

## 7. CWD ile script klasörü daima aynıdır

TIRT.

Başka bir dizinden script absolute/relative path ile çalıştırılabilir.

---

## 8. Başka CWD'den çalışınca import kesin bozulur

TIRT.

Deneyde import çalışmaya devam etti.

Ama:

```python
scanner(".")
```

farklı root taradı.

---

## 9. `WORKDIR` dosyaları image'a taşır

TIRT.

Bu `COPY` işidir.

---

## 10. Host absolute path ile container absolute path aynı olmalı

TIRT.

Filesystem görünümleri farklıdır.

---

## 11. Build başarılıysa bütün importlar kesin çalışır

TIRT.

Import problemi runtime'da ortaya çıkabilir.

---

## 12. Scanner image'a gelmediyse sorun yalnız Python kodundadır

TIRT.

Sorunun kökü build context / `COPY` olabilir.

---

# 🧠 Kafaya Kazı

> [!quote]  
> Bir `.py` dosyası import edilebilen bir Python modülü olabilir.

> [!quote]  
> `import scanner` → `scanner.fonksiyon()`.

> [!quote]  
> `from scanner import fonksiyon` → doğrudan `fonksiyon()`.

> [!quote]  
> Her modülün kendi `__name__` değeri vardır.

> [!quote]  
> Doğrudan çalıştırılan modülde `__name__ == "__main__"` olur.

> [!quote]  
> `if __name__ == "__main__"` başlangıç satırı değil, execution guard'dır.

> [!quote]  
> Filesystem path ile Python import path aynı kavram değildir.

> [!quote]  
> `pwd` CWD'yi, `find` fiziksel dosyayı, `sys.path` Python'ın arama alanını gösterir.

> [!quote]  
> Relative dosya yolu CWD'den etkilenir.

> [!quote]  
> Import sistemi `sys.path` üzerinden çalışır.

> [!quote]  
> `WORKDIR` çalışma dizinini belirler, `COPY` dosyayı image'a getirir.

> [!quote]  
> Host ve container absolute path'lerinin aynı olması gerekmez.

> [!quote]  
> Import hatasında yalnız Python satırına bakmak TIRT.

> [!quote]  
> Build context → filesystem/CWD → `sys.path` zincirini takip et.

---

# 📌 30 Saniyelik Özet

```text
PYTHON MODÜL
.py dosyası          → Modül olabilir
import modül         → modül.fonksiyon()
from ... import ...  → fonksiyon()

__name__
doğrudan çalıştır    → "__main__"
import edilen modül  → modül/package adı
if __name__ ...      → Execution guard

PATH KATMANLARI
pwd                  → Process CWD
find                 → Dosya filesystem'de nerede?
sys.path             → Python nerede modül arıyor?

RELATIVE PATH
scanner(".")
→ "." process CWD'sine göre değişir

IMPORT
src/scanner.py       → Filesystem yolu
src.scanner          → Python modül yolu

DOCKER
build context        → Docker hangi dosyalara ulaşabilir?
COPY                 → Hangileri image'a girer?
WORKDIR              → Process nereden çalışır?
sys.path             → Python nerelerde import arar?

DEBUG
Dosya image'a geldi mi?
↓
Doğru yerde mi?
↓
Python o yeri arıyor mu?
```

---

# ✅ Günün Kazanımları

-  Python modülü kavramı öğrenildi
    
-  `import modül` ile `from modül import isim` ayrıldı
    
-  Namespace mantığı pekiştirildi
    
-  Import sırasında üst seviye kodun çalışabileceği öğrenildi
    
-  Fonksiyon tanımlamak ile fonksiyon çalıştırmak ayrıldı
    
-  Her modülün kendi `__name__` değerinin olduğu anlaşıldı
    
-  `if __name__ == "__main__"` guard mantığı oturdu
    
-  `src/scanner.py` filesystem yolu ile `src.scanner` import yolu ayrıldı
    
-  Alt klasörden modül import edildi
    
-  `scanner.py` ve `main.py` arasında sorumluluk sınırı oluşturuldu
    
-  Başarı tarafında açık `return 0` kullanımının avantajı görüldü
    
-  CWD ile script dizini ayrıldı
    
-  `find` sonucu ile import edilebilirlik ayrıldı
    
-  Filesystem path ve Python import path iki ayrı katman olarak düşünüldü
    
-  `sys.path` import debugging aracı olarak öğrenildi
    
-  Farklı CWD'den çalıştırma deneyi yapıldı
    
-  Import'un çalışırken relative filesystem sonucunun değişebileceği görüldü
    
-  Docker'da host/container absolute path farkı tekrar pekiştirildi
    
-  `WORKDIR` ile `COPY` ayrıldı
    
-  Package dizini image'a taşındı
    
-  Host ve Docker aynı mantıksal sonucu üretti
    
-  Build'in başarılı olmasının runtime import başarısını garanti etmediği öğrenildi
    
-  Docker import sorunları için üç katmanlı debug modeli kuruldu
    

> [!success] 🚀 Gün sonu sonucu  
> Gün 15 sonunda program artık yalnızca tek `.py` dosyası olarak düşünülmüyor.
> 
> Kod:
> 
> ```text
> main.py
> → Uygulama akışı / karar / kullanıcı arayüzü
> 
> scanner.py
> → Belirli iş mantığı / dosya tarama
> ```
> 
> şeklinde modüler sorumluluklara ayrıldı.
> 
> En önemli yeni debugging modeli ise:
> 
> ```text
> DOSYA FİZİKSEL OLARAK NEREDE?
>            ↓
> PROCESS NEREDEN ÇALIŞIYOR?
>            ↓
> PYTHON NERELERDE MODÜL ARIYOR?
> ```
> 
> Docker'a taşındığında bunun karşılığı:
> 
> **Build context + `COPY` → Container filesystem / `WORKDIR` → Python `sys.path`.**