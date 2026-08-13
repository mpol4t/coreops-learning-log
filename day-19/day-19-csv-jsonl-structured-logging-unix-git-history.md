---
title: "Gün 19 — CSV → JSONL Pipeline, Structured Logging, Unix Araçları ve Git History"
tags:
  - coreops
  - python
  - csv
  - jsonl
  - logging
  - linux
  - jq
  - grep
  - awk
  - tee
  - git
aliases:
  - "Gün 19 CSV JSONL Structured Logging Linux Araçları ve Git History"
status: completed
---

# 🧠 Gün 19 — CSV → JSONL Pipeline, Structured Logging, Unix Araçları ve Git History

> [!abstract] 🎯 Ana fikir  
> Bugün tek bir CSV dosyasını yalnızca “okumak” yerine gerçek bir veri pipeline'ı gibi işlemeye başladım:
> 
> ```
> CSV
> ↓
> DictReader
> ↓
> Normalize
> ↓
> Validate
> ↓
> Kabul / Red
> ↓
> JSONL + Structured Log
> ```
> 
> Ardından çıktıları Unix araçlarıyla analiz ettim ve Git geçmişinden **“bir özellik hangi commit'te geldi?”** sorusuna kanıt ürettim.
> 
> Günün üç büyük ayrımı:
> 
> ```
> Normalize ≠ Validate
> Business Output ≠ Diagnostic Log
> Şimdiki durum ≠ Git History
> ```

---

# ⚡ 2 Dakikalık Geri Çağırma

CSV içindeki:

```
443
true
```

gibi değerler bize mantıksal olarak sayı ve boolean gibi görünse de `csv.DictReader` bunları otomatik olarak `int` veya `bool` yapmaz.

CSV satırı pratikte string alanlardan gelir ve tip dönüşümünü uygulama yapar.

---

# 🐍 Python — Günün Pipeline'ı

Kaynak kodun ana akışı:

```
CSV satırı
   ↓
basic_normalize()
   ↓
validate()
   ↓
json.dumps()
   ↓
stdout / JSONL
```

Hatalı kayıt:

```
ValueError
   ↓
record_rejected
   ↓
WARNING log
   ↓
Sonraki satıra devam
```

Gerçek implementasyonda kayıt bazlı hata yönetimi ve sayaçlar birlikte kullanılmış.

---

# 📄 `csv.DictReader`

```
icerik = csv.DictReader(dosya)
```

her satırı yaklaşık:

```
{
    "asset_id": "srv-001",
    "hostname": "api.internal",
    "port": "443",
    "active": "true",
}
```

şeklinde verir.

Burada dikkat:

```
"443"  → str
"true" → str
```

`DictReader` kolon isimlerini key yapar ama iş alanı tiplerini bilmez.

---

# 🧯 Yaptığım İlk Hata — `DictReader` Nesnesini Bastırmak

Şunu bastırınca:

```
print(icerik)
```

satırları değil:

```
<csv.DictReader object ...>
```

benzeri bir nesne gösterimi görürüm.

Çünkü `icerik` tek bir kayıt değil, üzerinde iterate edilen reader nesnesidir.

Doğru:

```
for satir in icerik:
```

ile satırları tek tek almak.

---

# 🧱 Sorumluluk Ayrımı

İlk zihinsel hata:

```
basic_normalize()
→ dosyayı açsın
→ CSV reader oluştursun
→ satırı temizlesin
```

şeklindeydi.

Bu fonksiyona gereğinden fazla sorumluluk yükler.

Daha temiz sınır:

```
main()
→ dosyayı açar
→ DictReader oluşturur
→ satır akışını yönetir

basic_normalize()
→ yalnızca bir satırı normalize eder

validate()
→ normalize edilmiş satırı doğrular
```

Kaynak notta bu refactor özellikle yapılmış.

---

# 🔄 Kaynak → İşlem → Hedef

Şu yapı:

```
normalized["hostname"] = (
    satir["hostname"].strip()
)
```

şöyle okunmalı:

```
satir["hostname"]
→ Ham kaynak değer

.strip()
→ İşlem

normalized["hostname"]
→ Temiz sonucu yazdığım hedef
```

Yani:

> **KAYNAK → İŞLEM → HEDEF**

Bu model dict dönüşümlerinde çok kullanışlı.

---

# 🧹 `basic_normalize()`

Alanlar:

```
asset_id
→ strip()

hostname
→ strip()

port
→ strip()
→ int()

active
→ strip()
→ lower()
→ bool sözleşmesine dönüştür
```

---

# 🔢 Port Normalizasyonu

CSV:

```
"443"
```

olarak verir.

Kod:

```
int(satir["port"].strip())
```

ile:

```
" 443 "
↓
"443"
↓
443
```

olur.

---

# 💥 `port="abc"`

```
int("abc")
```

başarısızdır.

Burada hata **normalize aşamasında** oluşur:

```
CSV string
↓
int'e çevrilemedi
↓
ValueError
```

Henüz range validation'a bile ulaşılmaz.

---

# 📏 `port="70000"`

Burada:

```
int("70000")
```

başarılıdır:

```
70000
```

Yani normalize:

```
✅
```

Ama:

```
1 <= port <= 65535
```

kuralı başarısızdır:

```
Validation ❌
```

> [!important]  
> **Doğru tipe dönüşebilmek ≠ geçerli değer olmak.**

Kaynak notta normalize/validate ayrımı bu iki örnekle doğru şekilde kurulmuş.

---

# ⚠️ `bool("false")` Tuzağı

TIRT yaklaşım:

```
bool("false")
```

Sonuç:

```
True
```

Çünkü Python açısından boş olmayan string truthy'dir.

Yani:

```
"true"  → True
"false" → True
"abc"   → True
```

olabilir.

---

# ✅ Doğru Boolean Sözleşmesi

Önce:

```
value = satir["active"].strip().lower()
```

sonra açık mapping:

```
"true"  → True
"false" → False
diğer   → ValueError
```

Bu noktada veri formatının ne kabul ettiğini biz tanımlıyoruz.

---

# ✅ Validation

Normalize edilmiş kayıtta:

```
asset_id
→ boş olamaz

hostname
→ boş olamaz

port
→ 1..65535
```

kontrol ediliyor.

Kaynak implementasyonda bunlar bağımsız kurallar olarak ayrı `if` bloklarında tutulmuş.

---

# 🔀 Neden `elif` Yerine Ayrı `if`?

Şöyle kurallar:

```
asset_id dolu mu?
hostname dolu mu?
port range doğru mu?
```

birbirlerinin alternatifi değildir.

Bu yüzden zihinsel model:

```
if kural_1_hatalı:
    raise ...

if kural_2_hatalı:
    raise ...

if kural_3_hatalı:
    raise ...
```

daha doğrudur.

---

# 🧯 Kayıt Bazlı Hata Politikası

Bugünün önemli tasarım kararı:

> **Bir kötü kayıt yüzünden bütün CSV'yi çöpe atma.**

Akış:

```
Satır 1 ✅
→ kabul et

Satır 2 ✅
→ kabul et

Satır 3 ❌
→ reject log
→ devam

Satır 4 ✅
→ kabul et
```

Bu yüzden `try/except` bütün dosyanın değil, **satır döngüsünün içinde**.

---

# 🧠 Fail-Slow vs Fail-Fast

Kayıt seviyesinde:

```
ValueError
→ veri problemi
→ reject
→ sonraki kayıt
```

Ama örneğin gerçek bir kod bug'ı:

```
KeyError
TypeError
NameError
```

olursa bunu yanlışlıkla “bozuk CSV kaydı” diye yutmak istemeyiz.

---

# 🐛 Gerçek Bug — `active` / `acitve`

Kodda typo:

```
active
→ acitve
```

yapılmış.

İlk `true` kayıtlarında ilgili bug görünmeyebildi.

`false` dalına gelince:

```
KeyError: 'acitve'
```

oluştu.

Burada:

```
except ValueError:
```

`KeyError`'ı yakalamadı.

Bu **iyi bir şeydi**.

Çünkü:

```
ValueError
→ beklenen veri hatası

KeyError
→ büyük ihtimalle kod bug'ı
```

Kaynak deneyde bu ayrım debugging açısından kritik ders olmuş.

---

> [!danger] TIRT
> 
> ```
> except Exception:
>     reject_et()
> ```
> 
> kullanmak gerçek programlama bug'larını “kötü kullanıcı verisi” sanarak gizleyebilir.

---

# 📦 JSONL Nedir?

JSONL:

```
{"asset_id":"srv-001", ...}
{"asset_id":"srv-002", ...}
{"asset_id":"srv-003", ...}
```

Her satır bağımsız bir JSON değeridir.

Bir JSON array ise:

```
[
  {...},
  {...},
  {...}
]
```

şeklinde bütün kayıtları tek JSON yapısı altında tutar.

---

# 🌊 JSONL ve Streaming

Bugün:

```
satırı oku
↓
normalize et
↓
validate et
↓
JSON yaz
↓
sonraki satır
```

modeli kullanıldı.

TIRT:

```
list(reader)
```

ile bütün CSV'yi önce RAM'e almak.

JSONL özellikle satır-bazlı pipeline'larda doğal bir çıktı biçimidir.

---

# 🔄 `json.dumps()` vs `json.dump()`

```
json.dumps(obj)
```

→ JSON **string** döndürür.

```
json.dump(obj, file)
```

→ JSON'u doğrudan bir file-like object'e yazar.

Bu programda:

```
print(json.dumps(normalized))
```

kullanıldığı için:

```
dict
↓
JSON string
↓
stdout
```

oluyor.

---

# 📤 Business Output vs Log

Bu ayrım günün en önemli production mantıklarından biri.

## Business output

```
print(json.dumps(normalized))
```

Bu programın asıl ürettiği veri.

```
stdout
```

üzerinden gider.

---

## Diagnostic log

```
logging.info(...)
logging.warning(...)
```

Programın içeride ne yaptığını anlatır.

Python logging'in varsayılan handler'ı tipik olarak:

```
stderr
```

üzerine yazar.

Kaynak notta bu ayrım doğru şekilde gözlemlenmiş.

---

# 💡 Neden Log Business Output'un Yerini Almamalı?

Makine tüketicisi şöyle bir çıktı bekleyebilir:

```
{"asset_id":"srv-001","port":443}
```

Ama araya:

```
INFO: kayıt işlendi
```

girerse veri stream'i bozulabilir.

İdeal:

```
stdout
→ tüketilecek veri

stderr
→ diagnostics / logs
```

---

# 🪵 `logging.basicConfig()`

```
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
```

log üretmez.

Logging sisteminin:

```
hangi seviyeleri?
hangi formatta?
hangi handler üzerinden?
```

işleyeceğini ayarlar.

Gerçek log üreticileri:

```
logging.debug()
logging.info()
logging.warning()
logging.error()
logging.critical()
```

---

# 📊 Logging Seviyeleri

```
DEBUG
<
INFO
<
WARNING
<
ERROR
<
CRITICAL
```

```
level=logging.INFO
```

ise:

```
DEBUG     ❌
INFO      ✅
WARNING   ✅
ERROR     ✅
CRITICAL  ✅
```

---

# 🧩 Logging Format

```
%(levelname)s
%(message)s
%(asctime)s
```

gibi alanlar logging sisteminin placeholder'larıdır.

Örneğin:

```
format="%(levelname)s: %(message)s"
```

çıktı:

```
INFO: event=record_accepted...
```

olabilir.

---

# `%s` Placeholder Mantığı

```
logging.info(
    "asset_id=%s",
    normalized["asset_id"],
)
```

burada:

```
1. %s
↓
normalized["asset_id"]
```

ile doldurulur.

Birden fazla:

```
logging.warning(
    "event=%s, asset_id=%s, reason=%s",
    "record_rejected",
    satir.get("asset_id"),
    hata,
)
```

ise sırayla eşleşir.

Kaynak çalışmada bu yapı gerçek structured log satırlarında kullanılmış.

---

# 🧱 Structured Logging

Serbest metin:

```
Üçüncü kayıtta garip bir hata oldu.
```

yerine:

```
event=record_rejected
asset_id=srv-003
reason=...
```

gibi sabit anahtarlar kullanmak:

- grep etmeyi
    
- makineyle parse etmeyi
    
- dashboard üretmeyi
    
- incident analizi yapmayı
    

kolaylaştırır.

---

# ✅ Kabul Edilen Kayıt

```
INFO:
event=record_accepted
asset_id=srv-001
```

ve:

```
accepted += 1
```

---

# ⚠️ Reddedilen Kayıt

```
WARNING:
event=record_rejected
asset_id=srv-003
reason=...
```

ve:

```
rejected += 1
```

---

# 🔐 Neden Rejected Logunda `normalized` Değil Ham `satir`?

Normalize işlemi ortasında:

```
int("abc")
```

patlarsa:

```
normalized
```

değişkeni henüz hiç oluşmamış olabilir.

Bu nedenle:

```
satir.get("asset_id")
```

kullanılması daha güvenli.

Ayrıca `.get()` key yoksa loglama kodunun kendi `KeyError` üretmesini engeller.

---

# 🏁 `processing_complete`

Sayaçlar:

```
accepted = 0
rejected = 0
```

döngüden önce oluşturulur.

Her kayıt sonunda artırılır.

Döngü bittikten sonra:

```
event=processing_complete
accepted=...
rejected=...
```

loglanır.

> [!danger]  
> Bunu loop içine koymak her kayıt sonrası “işlem tamamen bitti” demek olurdu.

---

# 🧪 Negatif Test — `port_abc.csv`

Gerçek deney:

```
srv-001
→ accepted

srv-002
→ accepted

srv-003 / abc
→ int conversion ValueError
→ rejected
```

Final log:

```
accepted=2
rejected=1
```

şeklinde çıktı.

Bu deney şunları tek seferde doğruladı:

```
Bozuk kayıt JSONL'ye girmedi ✅
Reject loglandı ✅
Reason loglandı ✅
Pipeline devam etti ✅
Sayaç doğru ✅
```

---

# 🐧 Linux — Unix Araçlarını Doğru İşe Seçmek

Bugünün eşleştirmesi:

```
tee
→ AKIŞ

tail
→ KONUM

grep
→ SATIR İÇERİĞİ

awk
→ ALAN / KOLON

jq
→ JSON YAPISI
```

Kaynak notun Linux bölümünün ana modeli buydu.

---

# 🔀 `tee`

```
python day19.py geçerli.csv \
  | tee json.json
```

`tee` kendisine gelen stream'i:

```
1. terminale gösterir
2. dosyaya yazar
```

---

# 🤔 Neden Dosyada Yalnız JSON Vardı?

Terminalde:

```
INFO logları
+
JSON kayıtları
```

birlikte görünüyordu.

Ama:

```
cat json.json
```

yalnız JSON gösterdi.

Çünkü:

```
print()
→ stdout

logging
→ stderr

|
→ yalnız stdout'u pipe eder
```

Gerçek deneyde de dosyada yalnız JSON kayıtları bulunmuş.

---

# 🔗 `2>&1`

Hem stdout hem stderr aynı pipe'a girsin:

```
python day19.py geçerli.csv \
  2>&1 \
  | tee output.txt
```

Burada:

```
1
→ stdout

2
→ stderr

2>&1
→ stderr'i stdout'un mevcut hedefine bağla
```

Sonrasında:

```
JSON + logs
→ tee
→ output.txt
```

---

# ➕ `tee -a`

```
tee -a output.txt
```

mevcut dosyanın üzerine yazmak yerine sonuna ekler.

---

# 🧩 `jq`

JSON yapısının kendisiyle çalışır.

Genel form:

```
jq 'FILTER' FILE
```

TIRT:

```
jq json.json
```

Burada `json.json` filtre gibi yorumlanabilir.

Doğru:

```
jq . json.json
```

Identity filter:

```
.
```

JSON değerini olduğu gibi işler.

---

# 🔑 Alan Çıkarmak

```
jq '.hostname' json.json
```

çıktı:

```
"api.internal"
"db.internal"
"old.internal"
```

Gerçek deneyde üç JSONL kaydından hostname alanları çıkarılmış.

---

# `select()` Her Zaman Gerekmez

Sadece alan istiyorsam:

```
.hostname
```

Koşula göre kayıt seçmek istiyorsam:

```
select(.active == true)
```

Hem filtrele hem alan çıkar:

```
select(.active == true)
| .hostname
```

---

# 🔎 `grep -E`

```
grep -E \
  'record_rejected|processing_complete' \
  output.txt
```

buradaki regex:

```
A|B
```

→ A **veya** B.

Ama `grep`:

```
olmayan bir event'i üretmez.
```

Yalnız dosyada bulunan satırlardan pattern'e uyanları geçirir.

Kaynak deneyde `rejected=0` olduğu için yalnız `processing_complete` eşleşmiş.

---

# 📍 `tail`

```
tail -n 2 output.txt
```

dosyanın **son iki satırını** getirir.

Ayrım:

```
grep
→ İçerikte ne yazıyor?

tail
→ Dosyada hangi konumda?
```

---

# 👀 `tail -f`

```
tail -f run.log
```

dosyaya sonradan eklenen satırları takip etmeye devam eder.

Canlı log izleme için çok kullanışlıdır.

---

# 🧮 `awk`

CSV:

```
asset_id,hostname,port,active
```

ise:

```
awk -F',' '{print $2}' geçerli.csv
```

şöyle okunur:

```
-F','
→ field separator = virgül

$1
→ birinci alan

$2
→ ikinci alan

{print $2}
→ her kaydın ikinci alanını bas
```

Gerçek çıktıda:

```
hostname
api.internal
db.internal
old.internal
```

alınmış.

---

# ⚠️ `awk` ve Gerçek CSV

Bugünkü basit CSV'de:

```
-F','
```

işe yarıyor.

Ama genel CSV formatında:

```
srv-1,"api,internal",443,true
```

gibi quoted comma bulunabilir.

Bu durumda basit `awk -F','` tam bir CSV parser değildir.

> [!important]  
> Basit kolonlu metin için `awk` süperdir; gerçek CSV semantics gerekiyorsa CSV-aware parser daha güvenlidir.

---

# 🧠 Araç Seçim Matrisi

|İhtiyaç|Araç|
|---|---|
|JSON field / structure|`jq`|
|Text / regex satır filtresi|`grep -E`|
|Dosyanın son N satırı|`tail`|
|Basit kolon / field|`awk`|
|Akışı hem göster hem kaydet|`tee`|

Kaynakta bu karşılaştırma deney sonunda doğrudan çıkarılmış.

---

# 🌳 Git — History Sorgulamak

Önceki gün:

```
Working Tree
↓
Index
↓
Commit
```

öğrenilmişti.

Bugün soru değişti:

> **Geçmişte ne olmuş?**

Ana komutlar:

```
git status
→ Şu an ne durumda?

git log
→ Hangi commit'ler var?

git show COMMIT
→ Bu commit ne yaptı?

git diff A B
→ İki snapshot arasında ne değişti?
```

Kaynak notta bu ayrım Git history bölümünün temeli olarak kurulmuş.

---

# 📜 `git log --oneline`

```
git log --oneline
```

commit'leri kısa formatta gösterir:

```
8d02a15 day19-baseline
6cc95ce day18-baseline
```

Gerçek history:

```
HEAD → day19
       ↓
      day18
```

şeklinde oluşmuş.

---

# 🧭 `HEAD -> master`

```
8d02a15 (HEAD -> master)
```

şunu anlatır:

```
HEAD
↓
master
↓
8d02a15
```

Şu anda master branch'indeyim ve master bu commit'i gösteriyor.

---

# 🔬 `git show <commit>`

```
git show 6cc95ce
```

belirli commit hakkında:

- Tam hash
    
- Author
    
- Date
    
- Commit mesajı
    
- Patch/diff
    

gibi bilgiler verir.

Gerçek `day18-baseline` commit'i bu şekilde incelenmiş.

---

# `git show` vs `git diff`

## `git show B`

Soru:

> **B commit'i ne getirdi?**

Çoğu normal commit için kabaca:

```
B'nin parent'ı
↕
B
```

değişikliğini gösterir.

---

## `git diff A B`

Soru:

> **A snapshot'ı ile B snapshot'ı arasında ne farklı?**

İki snapshot'ı bilinçli olarak karşılaştırırım.

Kaynak notta bu zaman/snapshot ayrımı doğru şekilde formüle edilmiş.

---

# 🗂️ Yaptığım Repo Hatası — İç İçe Ayrı Repo'lar

Başlangıçta:

```
day18/.git
day19/.git
```

vardı.

Bu:

```
Day18 → ayrı Git repository
Day19 → ayrı Git repository
```

demektir.

Sonuç:

```
Day19 reposu
→ Day18 history'sini bilmez.
```

Çünkü Git geçmişleri tamamen ayrıdır.

---

# ✅ Düzeltilen Yapı

Ortak root:

```
Gelişmiş/
├── .git/
├── day18/
├── day19/
└── ...
```

olarak düzenlendi.

Böylece:

```
Day18 commit
↓
Day19 commit
↓
Day20 commit
```

aynı history üzerinde ilerleyebilir.

Bu düzeltme kaynak notta Git deneyinin önemli parçası olmuş.

---

# 🎯 Commit Ne Alır?

> Commit klasördeki bütün dosyaları otomatik almaz.

Commit:

```
Index / Staging Area
```

içindekileri alır.

Bu yüzden:

```
git add day18
git commit -m "day18-baseline"
```

ile yalnız Day18 hazırlanmış.

Sonra:

```
git add day19
git commit -m "day19-baseline"
```

ile Day19 ayrı commit olmuş.

---

# 🧾 `git status --short`

Örneğin:

```
A  day19/day19.py
?? day17.py
```

burada:

```
A
→ Added / staged

??
→ Untracked
```

Bu kısa format commit'e ne gireceğini hızlı görmek için çok kullanışlıdır.

---

# ⚠️ `git add .` Konusunda Dikkat

Root repository'de:

```
git add .
```

bütün uygun değişiklikleri stage edebilir.

Ama yalnız:

```
Day19
```

commit'i oluşturmak istiyorsan:

```
git add day19
```

daha kontrollüdür.

---

# 📝 `git commit day19` Hatası

Şunu yazmak:

```
git commit day19
```

commit mesajını:

```
day19
```

olarak vermek demek değildir.

Git commit mesajı almak için editor açmaya çalıştı ve mevcut ortamda:

```
there was a problem with the editor 'vi'
```

hatası oluştu.

Doğru:

```
git commit -m "day19-baseline"
```

Kaynak deneyde bu hata yaşanıp düzeltilmiş.

---

# 🔍 Structured Logging Hangi Commit'te Geldi?

Tahmin:

```
“Galiba Day19.”
```

Git açısından kanıt değildir.

Kanıt zinciri:

```
git log --oneline
↓
Day19 commit hash'ini bul

git show HASH
↓
Patch'i incele

record_accepted
processing_complete
logging.basicConfig
↓
+ ile eklenmiş mi?
```

Gerçek Day19 commit'inde logging satırları history'de görünmüş.

---

# 🔎 `less` İçinde Arama

Uzun `git show` çıktısı pager içinde açılırsa:

```
/kelime
→ ileri ara

n
→ sonraki eşleşme

N
→ önceki eşleşme

q
→ çık
```

Örneğin:

```
/logging
/record_accepted
/processing_complete
```

ile ilgili satırlar bulunabilir.

---

# ⚠️ Git History Deneyindeki İncelik

Day18 ve Day19:

```
day18/day18.py
day19/day19.py
```

şeklinde farklı dosyalardı.

Dolayısıyla Git:

```
day18.py değişti ve day19.py oldu
```

demiyor.

Daha çok:

```
Commit 1
→ Day18 dosyaları eklendi

Commit 2
→ Day19 dosyaları eklendi
```

diyor.

Bu nedenle:

> Structured logging'in **repository'ye hangi commit'te girdiğini** kanıtlayabilirim.

Ama:

> Aynı dosyanın zaman içindeki evrimini incelemek için aynı dosyayı commit'ler arasında değiştirmek daha doğal deney olur.

Kaynak notta bu nüans özellikle doğru şekilde fark edilmiş.

---

# 🔗 Entegrasyon Deneyi

Entegrasyon CSV:

```
srv-001 → valid
srv-002 → valid
srv-003 → invalid boolean
srv-004 → invalid port range
```

Program:

```
python day19.py entegrasyon.csv \
  >accepted.jsonl \
  2>run.log
```

ile çalıştırıldı.

Sonuç:

```
accepted.jsonl
→ yalnız 2 geçerli kayıt

run.log
→ 2 accepted
→ 2 rejected
→ processing_complete accepted=2 rejected=2
```

Ardından:

```
wc -l accepted.jsonl
```

sonucu:

```
2
```

ve:

```
grep -E 'record_rejected' run.log
```

iki reject kaydını gösterdi.

---

# 🔥 Bu Entegrasyon Ne Kanıtladı?

```
CSV input
↓
Normalize
↓
Validate
↓
JSONL stdout
+
Structured log stderr
↓
Shell redirection
↓
wc / grep bağımsız doğrulama
```

Yani artık test:

```
“Ekranda doğru görünüyor.”
```

seviyesinden çıkıp:

```
Business output doğru mu?
Log doğru mu?
Sayaç doğru mu?
Reject edilen kayıt output'a girmiş mi?
```

seviyesine geldi.

---

# 🧯 Hata Avı

## 1. `DictReader` port değerini otomatik `int` yapar

TIRT.

CSV'den gelen alanlar string ağırlıklıdır; dönüşüm uygulama işidir.

---

## 2. `bool("false") == False`

TIRT.

Boş olmayan string olduğu için `True`.

---

## 3. Normalize ile validate aynı aşamadır

TIRT.

```
Normalize
→ standardize / convert

Validate
→ business rule kontrolü
```

---

## 4. `port="70000"` normalize aşamasında kesin patlar

TIRT.

`int("70000")` başarılıdır; range validation patlar.

---

## 5. Tek bozuk kayıt bütün dosyayı durdurmak zorundadır

TIRT.

Kayıt-bazlı pipeline'da reject + devam politikası uygulanabilir.

---

## 6. `except Exception` her durumda daha güvenlidir

TIRT.

Gerçek kod bug'larını gizleyebilir.

---

## 7. JSONL tek bir JSON array'dir

TIRT.

Her satır bağımsız JSON value'dur.

---

## 8. Log ve business output aynı stream'de olmalı

TIRT.

Makine tüketimi için ayrılması çoğu zaman çok daha sağlıklıdır.

---

## 9. `logging.basicConfig()` log mesajı üretir

TIRT.

Logging sistemini yapılandırır.

---

## 10. Pipe `|` stderr'i de otomatik taşır

TIRT.

Varsayılan olarak stdout taşınır.

---

## 11. `jq hostname json.json` doğru zihinsel modeldir

TIRT.

Genel yapı:

```
jq 'FILTER' FILE
```

---

## 12. `grep` bulunmayan event'i oluşturur

TIRT.

Yalnız mevcut satırları filtreler.

---

## 13. `tail` pattern'e göre satır seçer

TIRT.

Dosyadaki konuma göre son N satırı seçer.

---

## 14. `awk -F','` her türlü CSV'yi eksiksiz parse eder

TIRT.

Quoted commas gibi gerçek CSV özelliklerinde basit field splitting yetersiz kalabilir.

---

## 15. `git log` şu anki unstaged değişiklikleri gösterir

TIRT.

Commit geçmişini gösterir.

---

## 16. `git show` iki istediğim snapshot'ı karşılaştırmak içindir

TIRT.

Tipik olarak tek commit'in metadata + yaptığı değişikliği inceler.

İki explicit snapshot için:

```
git diff A B
```

---

## 17. Farklı `.git` klasörleri aynı history'yi paylaşır

TIRT.

Her `.git` ayrı repository geçmişidir.

---

## 18. `git commit` klasördeki her şeyi otomatik commit eder

TIRT.

Temel olarak staging area'daki değişiklikleri commit eder.

---

## 19. `git commit day19` mesajı `day19` yapar

TIRT.

Commit mesajı için:

```
git commit -m "day19-baseline"
```

---

## 20. “Logging Day19'da geldi galiba” Git kanıtıdır

TIRT.

History'den:

```
log → commit'i bul
show → diff'i incele
```

ile kanıt üretmek gerekir.

---

# 🧠 Kafaya Kazı

> [!quote]  
> `DictReader` satırı yapılandırır, tip dönüşümünü uygulama yapar.

> [!quote]  
> Normalize verinin biçimini düzeltir; validate iş kuralını kontrol eder.

> [!quote]  
> `bool("false")` tuzaktır.

> [!quote]  
> Tek bozuk kayıt bütün stream'i öldürmek zorunda değildir.

> [!quote]  
> Beklenen veri hatası ile kod bug'ını aynı exception altında gizleme.

> [!quote]  
> JSONL = satır başına bağımsız JSON kaydı.

> [!quote]  
> `json.dumps()` string döndürür; `json.dump()` file-like object'e yazar.

> [!quote]  
> stdout business output, stderr diagnostic log için ayrılabilir.

> [!quote]  
> Structured logging serbest metinden çok sabit alanlara dayanır.

> [!quote]  
> `tee` akış, `tail` konum, `grep` içerik, `awk` alan, `jq` yapı.

> [!quote]  
> Pipe varsayılan olarak stdout taşır.

> [!quote]  
> Git status bugünü, log geçmişi anlatır.

> [!quote]  
> `git log` commit'i bulur; `git show` commit'i inceler; `git diff` iki snapshot'ı karşılaştırır.

> [!quote]  
> Tek history istiyorsan tek mantıksal repository kökü kullan.

> [!quote]  
> Commit yalnız stage edilmiş değişiklikleri kaydeder.

> [!quote]  
> Tahmin history değildir; commit diff'i kanıttır.

---

# 📌 30 Saniyelik Özet

```
CSV
↓
DictReader
↓
row = dict[str, str]
↓
normalize
↓
validate
↓
JSONL

NORMALIZE
asset_id → strip
hostname → strip
port → int
active → explicit true/false mapping

VALIDATE
asset_id dolu
hostname dolu
1 <= port <= 65535

HATA POLİTİKASI
ValueError
→ reject
→ WARNING
→ devam

Gerçek kod bug'ı
→ gizleme

JSONL
1 satır
=
1 JSON kayıt

OUTPUT
stdout
→ JSONL

stderr
→ logs

LOG
record_accepted
record_rejected
processing_complete

LINUX
tee
→ akışı kopyala

jq
→ JSON yapısı

grep
→ pattern

tail
→ son N satır

awk
→ basit alan/kolon

GIT HISTORY
git status
→ şimdi ne var?

git log --oneline
→ hangi commit'ler?

git show HASH
→ bu commit ne getirdi?

git diff A B
→ A ve B arasında ne değişti?

KRİTİK
Working Tree
↓ git add
Index
↓ git commit
History
```

---

# ✅ Günün Kazanımları

- `csv.DictReader` satırlarının string tabanlı geldiği öğrenildi
    
- Reader nesnesi ile tek kayıt ayrıldı
    
- Dosya okuma ile normalize etme sorumlulukları ayrıldı
    
- Kaynak → işlem → hedef dict modeli oturdu
    
- `asset_id` ve `hostname` temizlendi
    
- Port string'den integer'a dönüştürüldü
    
- `bool("false")` tuzağı öğrenildi
    
- Açık `"true"` / `"false"` boolean mapping uygulandı
    
- Normalize ile validate ayrıldı
    
- Port conversion failure ile range failure ayrıldı
    
- Bağımsız validation kuralları ayrı `if` bloklarına ayrıldı
    
- Satır bazlı reject + devam hata politikası uygulandı
    
- Geniş `except Exception` kullanımının gerçek bug gizleyebileceği deneyle görüldü
    
- Typo kaynaklı `KeyError` ile veri kaynaklı `ValueError` ayrıldı
    
- JSONL formatı öğrenildi
    
- Satır-bazlı streaming pipeline uygulandı
    
- `json.dumps()` / `json.dump()` ayrıldı
    
- Business output ile diagnostic log ayrıldı
    
- Logging seviyeleri öğrenildi
    
- `basicConfig()` ile log olayı ayrıldı
    
- `%s` logging placeholder mantığı oturdu
    
- Structured logging event alanları oluşturuldu
    
- Accepted/rejected sayaçları uygulandı
    
- `processing_complete` event'i üretildi
    
- `tee` ile stdout aynı anda görüntülenip kaydedildi
    
- `2>&1` ile stderr/stdout akışları birleştirildi
    
- `jq` ile JSONL field extraction yapıldı
    
- `select()` ile field extraction ayrıldı
    
- `grep -E` ile event filtreleme yapıldı
    
- `tail -n` ile son satırlar incelendi
    
- `awk -F` ile basit CSV kolonu çıkarıldı
    
- Unix araçlarının görev bazlı seçimi oturdu
    
- Ortak Git repository yapısı oluşturuldu
    
- Day18 ve Day19 ayrı commit'ler olarak kaydedildi
    
- `git status --short` durum kodları kullanıldı
    
- `git log --oneline` ile commit history incelendi
    
- `git show` ile belirli commit diff'i incelendi
    
- `git show` ve `git diff` arasındaki zaman/snapshot farkı öğrenildi
    
- İç içe ayrı `.git` repository hatası düzeltildi
    
- `git commit -m` kullanımı pekiştirildi
    
- Structured logging'in hangi commit'te repository'ye girdiği history üzerinden kanıtlandı
    
- stdout/stderr ayrımı gerçek entegrasyon testiyle doğrulandı
    
- `wc -l` ile accepted kayıt sayısı bağımsız kontrol edildi
    
- `grep` ile reject event'leri bağımsız kontrol edildi
    

> [!success] 🚀 Gün sonu sonucu  
> Gün 19 sonunda program artık:
> 
> ```
> “CSV okuyup birkaç şey print eden script”
> ```
> 
> değil, daha production'a yakın bir veri işleme pipeline'ı gibi davranıyor:
> 
> ```
> CSV
> ↓
> STREAM
> ↓
> NORMALIZE
> ↓
> VALIDATE
> ↓
> ACCEPT / REJECT
> ↓
> JSONL stdout
> +
> Structured stderr logs
> ```
> 
> Ardından Unix araçlarıyla:
> 
> ```
> jq / grep / tail / awk / tee
> ```
> 
> kullanılarak çıktılar bağımsız biçimde incelenebiliyor.
> 
> Git tarafında da artık yalnız:
> 
> ```
> add → commit
> ```
> 
> değil:
> 
> ```
> “Bu özellik history'ye TAM OLARAK hangi commit'te girdi?”
> ```
> 
> sorusuna:
> 
> ```
> git log
> ↓
> git show
> ↓
> diff içindeki gerçek eklenen satırlar
> ```
> 
> üzerinden kanıt üretilebiliyor.
> 
> Günün en kritik cümlesi:
> 
> **İyi bir pipeline yalnız doğru kayıt üretmez; hatalı kayıtları kontrollü ayırır, ne yaptığını loglar, stdout/stderr sözleşmesini korur ve Git history sayesinde değişikliklerin ne zaman geldiğini sonradan kanıtlanabilir hâle getirir.**