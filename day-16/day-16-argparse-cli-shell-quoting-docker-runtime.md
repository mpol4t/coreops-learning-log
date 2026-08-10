---
title: "Gün 16 — Argparse CLI, Shell Quoting ve Docker Runtime Argümanları"
tags:
  - coreops
  - python
  - linux
  - docker
  - argparse
  - cli
  - shell
  - quoting
  - scanner
  - runtime
aliases:
  - "Gün 16 Argparse CLI Shell Quoting ve Docker Runtime Argümanları"
status: completed
duration_minutes: "85-90"
---

# 🧠 Gün 16 — `argparse`, CLI Sözleşmesi, Shell Quoting ve Docker Runtime Argümanları

> [!abstract] 🎯 Ana fikir  
> Bugünün temel veri akışı:
> 
> ```text
> Kullanıcı komutu
>       ↓
> Shell
>       ↓
> sys.argv
>       ↓
> argparse
>       ↓
> Normalize edilmiş Python değerleri
>       ↓
> scanner(root, suffix)
>       ↓
> Filesystem
> ```
> 
> Docker eklenince:
> 
> ```text
> Host path
>     ↓ bind mount
> Container path
>     ↓ WORKDIR
> Process CWD
>     ↓ CLI argümanı
> scanner()
> ```
> 
> En önemli ayrım:
> 
> **Mount ≠ Workdir ≠ CLI argümanı.**

---

# ⚡ 2 Dakikalık Geri Çağırma

Önceki günden:

```python
scanner(".")
```

içindeki:

```text
.
```

process'in mevcut çalışma dizinini yani **CWD'yi** temsil eder.

Scanner recursive arama yaptığı için program başka bir CWD'den çalıştırılırsa `.` farklı bir root anlamına gelir ve bulunan dosya kümesi değişebilir.

---

# 🐍 Python — `argparse` Ne İşe Yarar?

`argparse`, terminalden programa verilen argümanlar için bir **CLI sözleşmesi** tanımlar.

Örneğin:

```bash
python day16.py data --suffix .md
```

Burada:

```text
data
→ root

--suffix .md
→ suffix
```

olur.

Temel akış:

```text
Terminal
   ↓
argparse
   ↓
args.root
args.suffix
   ↓
scanner()
```

Kaynak görevde de `root` positional, `--suffix` optional olarak tanımlandı.

---

# 📍 Positional Argument

```python
parser.add_argument("root")
```

Başında `-` veya `--` olmadığı için positional argümandır.

Örnek:

```bash
python day16.py data
```

sonrasında:

```python
args.root == "data"
```

olur.

Bu tanımda `root` zorunludur.

Hiç verilmezse:

```bash
python day16.py
```

`argparse` kullanım hatası üretir ve varsayılan davranışta process'i exit code `2` ile sonlandırır.

---

# ⚙️ Optional Argument

```python
parser.add_argument(
    "--suffix",
    default=".txt",
)
```

Örnek:

```bash
python day16.py data --suffix .md
```

sonrasında:

```python
args.suffix == ".md"
```

olur.

Hiç verilmezse:

```bash
python day16.py data
```

default devreye girer:

```python
args.suffix == ".txt"
```

> [!important]  
> Optional demek “değer kabul etmiyor” demek değildir.
> 
> Burada `--suffix`, **isteğe bağlı olarak kullanılabilen ve ardından bir değer alan** option'dır.

---

# 📦 `parse_args()` Ne Döndürür?

```python
args = parser.parse_args()
```

sonucunda bir:

```python
argparse.Namespace
```

elde edilir.

Örneğin:

```bash
python day16.py data --suffix .md
```

yaklaşık:

```python
Namespace(
    root="data",
    suffix=".md",
)
```

üretir.

Sonrasında:

```python
args.root
args.suffix
```

ile erişilir.

---

# 🔌 Parser ile Scanner Arasındaki Sınır

Günün en önemli tasarım kararı:

```text
argparse
→ CLI'ı bilir.

scanner
→ CLI'ı bilmez.
```

Scanner:

```python
def scanner(root, suffix):
```

şeklinde normal Python değerleri alır.

Şunları bilmesine gerek yoktur:

```text
--suffix
argparse
Namespace
sys.argv
terminal
```

Kaynak notta bu sorumluluk ayrımı açıkça kurulmuş.

---

# ♻️ Scanner Neden Böyle Daha Tekrar Kullanılabilir?

Scanner:

```python
scanner("data", ".txt")
```

şeklinde çağrılabiliyorsa:

- CLI'dan çağrılabilir.
    
- Testten çağrılabilir.
    
- Başka Python modülünden çağrılabilir.
    
- İleride GUI veya API içinden çağrılabilir.
    

Ama scanner kendi içinde:

```python
parser.parse_args()
```

yapsaydı doğrudan terminal kullanımına bağlanmış olurdu.

> [!success]
> 
> ```text
> CLI katmanı → girdiyi al / normalize et
> Scanner     → taramayı yap
> ```

Bu, tekrar kullanılabilirliği artıran gerçek sorumluluk ayrımıdır.

---

# 🔎 Dinamik Suffix

Önce:

```python
root.rglob("*.txt")
```

hardcoded idi.

Şimdi:

```python
root.rglob(f"*{suffix}")
```

kullanılıyor.

Örneğin:

```python
suffix = ".md"
```

ise:

```python
f"*{suffix}"
```

sonucu:

```text
*.md
```

olur.

Böylece aynı scanner:

```text
.txt
.md
.log
.json
```

gibi farklı suffix'lerle kullanılabilir.

---

# 🧹 Suffix Normalizasyonu

Kullanıcının şunların ikisini de yazabilmesi isteniyor:

```bash
--suffix txt
```

ve:

```bash
--suffix .txt
```

Bunun için:

```python
if not args.suffix.startswith("."):
    args.suffix = "." + args.suffix
```

kullanıldı.

Sonuç:

```text
txt   → .txt
.txt  → .txt
md    → .md
.md   → .md
```

Kaynak implementasyondaki normalizasyon bu şekilde çalışıyor.

---

# 📌 Normalizasyon Nerede Olmalı?

Scanner yerine CLI katmanında olması mantıklı:

```text
Kullanıcı:
md
    ↓
CLI normalize eder:
.md
    ↓
scanner:
.md
```

Scanner her çağrıda:

```text
“Bu kullanıcı noktayı yazdı mı?”
```

diye uğraşmaz.

Scanner'a her zaman standart bir değer gelir.

---

# ♻️ Gereksiz Tekrarı Kaldırmak

TIRT yaklaşım:

```python
if suffix noktalıysa:
    scanner(...)

else:
    suffix = "." + suffix
    scanner(...)
```

Burada scanner çağrısı iki kez yazılıyor.

Daha temiz:

```python
if not suffix.startswith("."):
    suffix = "." + suffix

scanner(root, suffix)
```

Genel refactor kuralı:

> `if/else` dallarında aynı işlem tekrarlanıyorsa ortak işlem çoğu zaman dalların dışına çıkarılabilir.

---

# 🚨 CLI Parse Hatası vs Uygulama Hatası

Bu ikisi farklı katmanlardır.

## CLI hatası

```bash
python day16.py
```

`root` yok.

Burada scanner henüz çağrılmaz.

Akış:

```text
Shell
↓
argparse
↓
CLI sözleşmesi geçersiz
↓
Exit 2
```

---

## Uygulama hatası

```bash
python day16.py olmayan_root
```

CLI açısından geçerli:

```text
root verildi ✅
```

Ama filesystem'de bulunmuyorsa scanner:

```text
FileNotFoundError
```

üretir.

Yani:

```text
argparse
→ Program doğru çağrıldı mı?

scanner
→ Verilen filesystem kaynağı gerçekten kullanılabilir mi?
```

Bu ayrım kaynak notta özellikle vurgulanmış.

---

# 🧠 Önemli `argparse` Ayrıntısı

Kodda:

```python
try:
    ...
    args = parser.parse_args()
```

bulunsa da `argparse` parse hataları senin:

```python
except FileNotFoundError
```

ve:

```python
except NotADirectoryError
```

bloklarına düşmez.

Çünkü bunlar tamamen farklı hata türleridir.

Parse başarısızlığında scanner zaten çalışmamıştır.

---

# 🧪 Gerçek CLI Deneyi

Default `.txt`:

```bash
python day16.py .
```

recursive `.txt` sonuçlarını verdi.

Yanlış kullanım:

```bash
python day16.py . md
```

sonucu:

```text
error: unrecognized arguments: md
```

oldu.

Doğru:

```bash
python day16.py . --suffix md
```

ve sonuçta `.md` dosyaları bulundu.

---

# ❓ Neden `. md` Çalışmadı?

Parser'ın sözleşmesi:

```text
root
--suffix VALUE
```

şeklinde.

Şunu yazınca:

```bash
python day16.py . md
```

shell Python'a yaklaşık:

```text
"."
"md"
```

şeklinde iki positional değer gönderir.

Ama parser yalnız:

```text
1 positional → root
```

bekliyor.

Bu nedenle:

```text
md
→ fazladan / tanınmayan argüman
```

oluyor.

---

# 🐚 Linux / Shell — Python Komutu Doğrudan Görmez

CLI zihinsel modeli:

```text
Terminale yazdığım metin
        ↓
Shell işler
        ↓
Argüman listesi oluşur
        ↓
Python / sys.argv
        ↓
argparse
```

Kaynak nottaki formül:

**Terminal → Shell → `sys.argv` → `argparse` → Uygulama**

---

# ␠ Space Neden Önemli?

Şunu yazarsan:

```bash
python day16.py data folder
```

shell yaklaşık:

```python
[
    "day16.py",
    "data",
    "folder",
]
```

oluşturur.

Space shell için normalde argüman ayırıcıdır.

---

# 🔐 Quoting

Şunu yazarsan:

```bash
python day16.py "data folder"
```

Python tarafına yaklaşık:

```python
[
    "day16.py",
    "data folder",
]
```

gider.

Yani:

```text
"data folder"
→ tek argüman
```

olur.

---

# ❗ Quote Karakterleri Python'a Gider mi?

Normal shell kullanımında hayır.

Terminalde:

```bash
python day16.py "test dizini"
```

yazarsın.

Python:

```python
args.root
```

içinde:

```text
test dizini
```

görür.

Şunları görmez:

```text
"test dizini"
```

Quote karakterleri shell'in tokenization işlemi için kullanılır ve sonra kaldırılır.

---

# 🧪 Gerçek Quoting Deneyi

Önce:

```bash
mkdir "test dizini"
```

oluşturuldu.

Quote olmadan:

```bash
python day16.py test dizini
```

çıktısı:

```text
error: unrecognized arguments: dizini
```

ve:

```text
exit code = 2
```

oldu.

Quote ile:

```bash
python day16.py "test dizini"
```

sonucu:

```text
[]
```

ve:

```text
exit code = 0
```

oldu.

---

# 🎯 Neden İkinci Komut Çalıştı?

Çünkü ilkinde shell:

```text
test
dizini
```

olarak iki argüman oluşturdu.

İkincide:

```text
test dizini
```

tek argüman oldu.

Sonrasında:

```python
args.root == "test dizini"
```

olarak parse edildi.

---

# 🔍 CLI Debugging Sırası

Bir CLI problemi varsa:

```text
1. Shell
2. argparse
3. Uygulama
```

sırasıyla ilerle.

Kaynak notta da debugging zinciri bu şekilde kurulmuş.

---

# 1️⃣ Shell Katmanı

Soru:

> Python'a gerçekten hangi argümanlar geldi?

Geçici kontrol:

```python
import sys

print(repr(sys.argv))
```

Örneğin:

```bash
python main.py data folder
```

ile:

```python
[
    "main.py",
    "data",
    "folder",
]
```

görebilirsin.

---

# 2️⃣ `argparse` Katmanı

Soru:

> Gelen token'lar doğru değişkenlere map edildi mi?

```python
print(args.root)
print(args.suffix)
```

---

# 3️⃣ Uygulama Katmanı

Soru:

> Parse edilmiş değer doğru şekilde scanner'a gönderildi mi?

```python
scanner(
    args.root,
    args.suffix,
)
```

> [!danger]  
> Shell yanlış token üretmişken scanner kodunu değiştirmeye başlamak TIRT debugging olur.

---

# 📤 stdout, stderr ve Exit Code

Üç farklı kanıt:

```text
stdout
→ Normal program çıktısı

stderr
→ Hata / diagnostic

exit code
→ Process başarı/başarısızlık durumu
```

`argparse` yanlış CLI kullanımında varsayılan olarak usage/error mesajını yazar ve exit code `2` kullanır.

---

# 🐳 Docker — Runtime Argümanları

Genel Docker yapısı:

```bash
docker run \
  [DOCKER_OPTIONS] \
  IMAGE \
  [COMMAND] \
  [ARG...]
```

Örnek:

```bash
docker run --rm \
  --mount type=bind,source="$PWD",target=/app \
  -w /app \
  python:3.12-slim \
  python day16.py data --suffix .txt
```

Image'dan sonraki kısım:

```text
python day16.py data --suffix .txt
```

container içinde çalışacak process'e aittir.

---

# 🧩 Komutu Parçala

```text
docker run
→ Container oluştur / çalıştır.

--rm
→ Process bitince container'ı temizle.

--mount ...
→ Host filesystem'i container'a bağla.

-w /app
→ Container process CWD'sini /app yap.

python:3.12-slim
→ Kullanılacak image.

python day16.py . --suffix .md
→ Container içinde çalışacak komut + argümanlar.
```

---

# 🐍 Python Docker İçinde Ne Görür?

Container içinde:

```bash
python day16.py data --suffix .txt
```

çalışıyorsa:

```python
sys.argv
```

yaklaşık:

```python
[
    "day16.py",
    "data",
    "--suffix",
    ".txt",
]
```

olur.

Sonra `argparse`:

```text
root   = data
suffix = .txt
```

eşlemesini yapar.

Docker:

```text
“data root demektir.”
```

diye bilmez.

Bunu parser tanımı belirler.

---

# 📦 Bind Mount Source ve Container Path

```bash
--mount \
  type=bind,source="$PWD",target=/app
```

iki farklı namespace'i bağlar.

Örneğin:

```text
HOST
/Users/polat/project

CONTAINER
/app
```

Aynı dosya ağacı:

```text
Host:
 /Users/polat/project/data

Container:
 /app/data
```

olarak görünebilir.

---

# 🚨 Container'a Host Absolute Path Vermek

Container'daki Python'a:

```bash
python main.py /Users/polat/project/data
```

vermek çoğu durumda yanlıştır.

Python container içinde çalıştığı için bu path'i:

```text
Container filesystem'inde
```

aramaya çalışır.

Container açısından doğru absolute path örneği:

```text
/app/data
```

olabilir.

---

# 📍 `-w /app`

```bash
-w /app
```

şunu yapar:

```text
Process CWD = /app
```

Şunu **yapmaz**:

```text
args.root = "/app"
```

Kaynak notta bu ayrım özellikle vurgulanmış.

---

# 🔗 Relative Root Nasıl Çözülür?

Docker:

```bash
-w /app
```

ve Python:

```text
root = "data"
```

ise filesystem erişiminde:

```text
CWD
/app

+

relative path
data

=

/app/data
```

olur.

Bu çözüm container filesystem'i içinde gerçekleşir.

---

# 🧪 Docker Deneyi

`.txt`:

```bash
docker run --rm \
  --mount type=bind,source="$PWD",target=/app,readonly \
  -w /app \
  python:3.12-slim \
  python day16.py .
```

host ile aynı mantıksal `.txt` sonuçlarını verdi.

`.md`:

```bash
docker run --rm \
  --mount type=bind,source="$PWD",target=/app,readonly \
  -w /app \
  python:3.12-slim \
  python day16.py . --suffix .md
```

sonucunda `.md` dosyaları bulundu.

---

# 🔒 Neden `readonly` Yeterli?

Scanner yalnızca:

```text
Filesystem'i geziyor
Dosya türünü kontrol ediyor
Path listesi oluşturuyor
```

ve mount edilen kaynağı değiştirmiyor.

Bu nedenle:

```bash
readonly
```

yeterli.

Liste oluşturma gibi işlemler RAM'de gerçekleşir.

---

# 🔗 Host ve Docker Entegrasyonu

Host:

```bash
python day16.py \
  "test dizini" \
  --suffix .txt
```

sonucu:

```text
[]
```

Docker:

```bash
docker run --rm \
  --mount type=bind,source="$PWD",target=/app,readonly \
  -w /app \
  python:3.12-slim \
  python day16.py \
  "test dizini" \
  --suffix .txt
```

sonucu yine:

```text
[]
```

oldu.

Burada aynı göreli root:

```text
test dizini
```

host ve container'ın kendi CWD'sine göre doğru şekilde çözüldü.

---

# 🧯 Hata Avı

## 1. Positional argüman ile optional argüman aynı şeydir

TIRT.

```text
root
→ Konumla tanımlanan positional

--suffix
→ İsimli option
```

---

## 2. `default=".txt"` yalnızca `.txt` kabul edildiği anlamına gelir

TIRT.

Default yalnız option verilmezse kullanılacak değerdir.

---

## 3. `python day16.py . md` ile suffix `md` olur

TIRT.

Parser `md`'yi fazladan positional olarak görür.

Doğru:

```bash
python day16.py . --suffix md
```

---

## 4. Argparse hatası scanner tarafından yakalanır

TIRT.

Scanner henüz çağrılmadan CLI parse aşamasında program bitebilir.

---

## 5. Scanner kendi içinde `parse_args()` yapmalı

TIRT.

Scanner'ı CLI'a bağlar ve tekrar kullanılabilirliği azaltır.

---

## 6. Suffix noktasını scanner düzeltmeli

Bu yapılabilir ama mevcut tasarımda kullanıcı girdisini normalize etmek CLI katmanında daha temizdir.

---

## 7. `"data folder"` stringindeki quote'lar Python'a gider

TIRT.

Quote'lar shell tarafından token oluşturmak için kullanılır.

---

## 8. Space'in path içinde olması Python'ın problemi

TIRT.

İlk ayrıştırmayı shell yapar.

---

## 9. CLI problemi varsa önce scanner kodunu incelemeliyim

TIRT.

Önce:

```text
Shell → argparse → uygulama
```

---

## 10. Docker `-w /app` Python'a `/app` root argümanı verir

TIRT.

Sadece CWD'yi değiştirir.

---

## 11. Bind mount source path'i Python'a CLI argümanı olarak gider

TIRT.

Mount ve CLI birbirinden bağımsız mekanizmalardır.

---

## 12. Container'daki Python host absolute path'ini doğal olarak anlar

TIRT.

Path container filesystem namespace'inde çözülür.

---

# 🧠 Kafaya Kazı

> [!quote]  
> Positional argümanın anlamı konumundan gelir.

> [!quote]  
> `--suffix` gibi option'lar isimle belirtilir.

> [!quote]  
> `parse_args()` bir `Namespace` üretir.

> [!quote]  
> Eksik zorunlu positional argüman varsayılan argparse davranışında exit `2` üretebilir.

> [!quote]  
> CLI parse hatası ile filesystem hatası farklı katmanlardadır.

> [!quote]  
> Scanner CLI bilmemeli; normal Python değerleri almalı.

> [!quote]  
> Normalizasyonu bir kez yap, scanner'ı bir kez çağır.

> [!quote]  
> Shell Python'dan önce çalışır.

> [!quote]  
> Space normalde argüman ayırır.

> [!quote]  
> Quote, space'i aynı argümanın içinde tutabilir.

> [!quote]  
> Quote karakterleri normal kullanımda Python string'ine dahil olmaz.

> [!quote]  
> CLI debugging sırası: shell → argparse → uygulama.

> [!quote]  
> Docker image adından sonraki komut container process'ine aittir.

> [!quote]  
> Mount host ile container filesystem'ini bağlar.

> [!quote]  
> `-w` process CWD'sini belirler.

> [!quote]  
> CLI argümanı Python'a gönderilen değeri belirler.

> [!quote]  
> Mount ≠ Workdir ≠ CLI argümanı.

---
# 📌 30 Saniyelik Özet

```text
CLI
root                  → Positional
--suffix              → Optional/option
parse_args()          → Namespace
eksik root            → argparse error / exit 2

AKIŞ
Shell
↓
sys.argv
↓
argparse
↓
normalize
↓
scanner(root, suffix)

SCANNER
argparse bilmez
CLI bilmez
normal Python değerleri alır
tarama yapar
sonucu return eder

SUFFIX
txt                   → .txt
.txt                  → .txt
md                    → .md

SHELL
data folder           → 2 argüman
"data folder"         → 1 argüman
quotes                → Python'a dahil olmaz

DEBUG
1. shell
2. argparse
3. uygulama

DOCKER
--mount               → Host neresi container'da nerede?
-w /app               → Process nereden çalışıyor?
CLI "data"            → Python'a hangi root gönderiliyor?

CWD=/app
root="data"
↓
/app/data

KRİTİK
Mount
≠
Workdir
≠
CLI argümanı
```

---

# ✅ Günün Kazanımları

-  `argparse` ile gerçek CLI sözleşmesi oluşturuldu
    
-  Positional ve optional argüman ayrıldı
    
-  `parse_args()` / `Namespace` mantığı öğrenildi
    
-  Zorunlu positional argüman eksikliği deneyle gözlemlendi
    
-  `argparse` exit code `2` görüldü
    
-  CLI parse hatası ile filesystem hatası ayrıldı
    
-  Scanner iki parametreli hâle getirildi
    
-  `.txt` hardcode'u kaldırılıp dinamik suffix eklendi
    
-  `txt` / `.txt` suffix normalizasyonu uygulandı
    
-  Normalizasyon ile tarama sorumluluğu ayrıldı
    
-  Tekrarlanan scanner çağrısı refactor edildi
    
-  Scanner'ın `argparse`'dan bağımsız tutulmasının nedeni oturdu
    
-  Shell'in Python'dan önce argümanları işlediği öğrenildi
    
-  Space'in argüman ayırıcı olduğu deneyle görüldü
    
-  Shell quoting mantığı uygulandı
    
-  Quote karakterlerinin Python string'ine dahil olmadığı anlaşıldı
    
-  `sys.argv` CLI debugging katmanı olarak öğrenildi
    
-  Shell → argparse → uygulama debug sırası kuruldu
    
-  Docker runtime komut ve argüman yapısı ayrıştırıldı
    
-  Image'dan sonraki argümanların container process'ine ait olduğu öğrenildi
    
-  Bind mount source/target namespace farkı tekrar pekiştirildi
    
-  Host absolute path'in container içinde otomatik geçerli olmadığı kavrandı
    
-  `-w` ile CLI root argümanı ayrıldı
    
-  Relative path'in container CWD'sinde çözülmesi uygulandı
    
-  Host ve Docker'da `.txt` / `.md` taramaları aynı mantıksal sonucu verdi
    
-  Boşluk içeren path host ve Docker ortamında başarıyla kullanıldı
    

> [!success] 🚀 Gün sonu sonucu  
> Gün 16 sonunda CLI artık:
> 
> ```text
> “Python'a birkaç string gönderiyorum.”
> ```
> 
> şeklinde değil, katmanlı bir veri akışı olarak düşünülüyor:
> 
> ```text
> SHELL
> → Komutu token'lara ayırır.
> 
> ARGPARSE
> → Token'ların CLI sözleşmesine uyup uymadığını kontrol eder.
> 
> NORMALIZATION
> → Kullanıcı girdisini uygulamanın beklediği forma getirir.
> 
> SCANNER
> → CLI'dan habersiz şekilde gerçek iş mantığını yürütür.
> ```
> 
> Docker eklendiğinde de üç ayrı soru korunuyor:
> 
> ```text
> MOUNT
> → Dosya container'da nerede?
> 
> WORKDIR
> → Process nereden çalışıyor?
> 
> CLI
> → Programa hangi değer gönderiliyor?
> ```
> 
> Günün en kritik cümlesi:
> 
> **Scanner'ı `argparse`'dan ayırmak yalnız kodu temizlemek değildir; tarama mantığını CLI'dan bağımsız, test edilebilir ve farklı arayüzlerden tekrar kullanılabilir bir fonksiyon hâline getirir.**