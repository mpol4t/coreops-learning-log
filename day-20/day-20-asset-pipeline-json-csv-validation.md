---
title: "Gün 20 — Multi-Source Asset Pipeline, Failure Katmanları ve Git Artifact Kontrolü"
tags:
  - coreops
  - python
  - json
  - csv
  - normalization
  - validation
  - jsonl
  - logging
  - git
status: completed
---

# 🧠 Gün 20 — Multi-Source Asset Pipeline, Failure Katmanları ve Git Artifact Kontrolü

> [!abstract] 🎯 Ana fikir  
> Bugün JSON ve CSV gibi **iki farklı veri kaynağını aynı kanonik veri sözleşmesine** getiren gerçek bir pipeline kurdum:
> 
> ```
> JSON ─→ JSON parser ─→ JSON normalizer ─┐
>                                        │
>                                        ├→ ortak validator
> CSV  ─→ CSV parser  ─→ CSV normalizer ─┘
>                                               ↓
>                                    accepted / rejected
>                                      ↓             ↓
>                                  JSONL output   structured log
> ```
> 
> En önemli mimari ayrımlar:
> 
> **Parse ≠ Normalize ≠ Validate**
> 
> **File-level failure ≠ Record-level failure**
> 
> **Input format ≠ Canonical application model**
> 
> **Generated artifact ≠ Source code**

Kaynak programda bu yapı `parse_json`, `parse_csv`, iki ayrı normalization fonksiyonu, ortak `validation()` ve `main()` orkestrasyonu şeklinde kurulmuş.

---

# ⚡ İlk Zihinsel Model

Bir parser'ın veriyi kabul etmesi:

```
“Bu formatı okuyabildim.”
```

demektir.

Şu anlama **gelmez**:

```
“Bu kayıt uygulamam için kesin geçerli.”
```

Örneğin JSON:

```
{
  "asset_id": "srv-001",
  "hostname": "api.internal",
  "port": "443",
  "active": true
}
```

syntax olarak tamamen geçerlidir.

Ama uygulama:

```
port → gerçek int
```

bekliyorsa record geçersizdir.

> [!danger] TIRT  
> “JSON syntax valid → gönül rahatlığıyla veri doğrudur.”
> 
> Hayır.
> 
> **Syntax validity yalnız format katmanının geçtiğini kanıtlar.**

---

# 🧱 Günün Kanonik Record Sözleşmesi

İki farklı kaynak sonunda aynı yapıya ulaşmalı:

```
asset_id
→ boş olmayan str

hostname
→ boş olmayan str

port
→ gerçek int
→ 1..65535

active
→ gerçek bool

source
→ "json" veya "csv"
```

Bu ortak şekil sayesinde validator artık:

```
“Bu kayıt JSON'dan mı geldi, CSV'den mi?”
```

diye düşünmek zorunda kalmıyor.

Kaynak notta da iki formatın ortak canonical sözleşmeye dönüştürülmesi günün temel hedefi olarak tanımlanmış.

---

# 🐍 1. Katman — JSON Parse

```
def parse_json(path):
    with open(
        path,
        encoding="utf-8",
    ) as file:
        return json.load(file)
```

Görevi:

```
JSON syntax
↓
Python nesneleri
```

Örneğin:

```
JSON 443
→ Python int

JSON true
→ Python True

JSON "443"
→ Python str
```

---

# 🧠 JSON Zaten Tip Taşır

Bu yüzden JSON normalizer'ın:

```
"443" → 443
```

diye her şeyi zorla düzeltmesi tehlikeli olabilir.

Çünkü JSON'da:

```
"port": "443"
```

yazılmışsa producer gerçekten yanlış tip göndermiş olabilir.

Dolayısıyla bu görevde:

```
JSON yanlış tip
→ olduğu gibi bırak
→ validator reddetsin
```

yaklaşımı seçildi.

> [!important]  
> **Normalization hatalı veriyi gizlememeli.**

---

# 🐍 2. Katman — CSV Parse

```
reader = csv.DictReader(file)
```

CSV tarafında durum farklı.

Bir satır:

```
srv-101,web.internal,443,true
```

Python tarafında yaklaşık:

```
{
    "asset_id": "srv-101",
    "hostname": "web.internal",
    "port": "443",
    "active": "true",
}
```

olur.

Yani CSV'de:

```
443
true
```

gibi görünen alanların tipini uygulama üretmek zorunda.

---

# 🔥 JSON vs CSV Arasındaki Kritik Fark

```
CSV'de "443"
→ formatın doğal temsil biçimi olabilir
→ int'e çevirmek normalizasyon

JSON'da "443"
→ JSON özellikle string gönderiyor
→ bunu int'e çevirmek hatalı veriyi gizleyebilir
```

Kaynak notta iki ayrı normalizer kullanılmasının ana nedeni de bu temsil farkı.

---

# 📂 `DictReader` ve Dosya Yaşam Süresi

Başta:

```
def parse_csv(path):
    with open(path) as file:
        reader = csv.DictReader(file)
        return reader
```

gibi bir yapı düşünülmüş.

Sorun:

```
with biter
↓
file kapanır
↓
reader daha sonra okumaya çalışır
↓
kapalı kaynağa bağlı kalır
```

Bu yüzden reader dosya açıkken tüketildi:

```
records = []

for record in reader:
    records.append(record)

return records
```

> [!important]  
> `DictReader`'ın kendisi bütün dosyayı anında listeye dönüştürmez.
> 
> Reader'ın arkasındaki dosyanın yaşam süresini düşünmek gerekir.

---

# `newline=""`

CSV dosyası:

```
open(
    path,
    encoding="utf-8",
    newline="",
)
```

ile açıldı.

Bu:

> “Boş satırları kaldır.”

demek değildir.

Amaç, newline yorumlama işini mümkün olduğunca `csv` modülüne bırakmaktır.

---

# 🧹 JSON Normalization

JSON tarafında özellikle string olması beklenen alanlara dikkat edildi.

Örneğin:

```
if "asset_id" in record:
    if isinstance(
        record["asset_id"],
        str,
    ):
        normalized["asset_id"] = (
            record["asset_id"].strip()
        )
    else:
        normalized["asset_id"] = (
            record["asset_id"]
        )
```

Neden?

Çünkü doğrudan:

```
record["asset_id"].strip()
```

yazarsam:

```
asset_id = 123
```

durumunda:

```
123.strip()
```

diye normalization katmanında yanlış sebeple patlarım.

Daha temiz:

```
123
↓
Normalization değeri korur
↓
Validator
↓
“asset_id string değil”
```

Kaynak notta bu hata özellikle yakalanmış.

---

# 🧹 CSV Normalization

CSV normalizer daha agresif:

```
" srv-101 "
→ "srv-101"

" web.internal "
→ "web.internal"

" 443 "
→ 443

" true "
→ True
```

Çünkü burada string temsil formatın kendisinden kaynaklanıyor.

---

# ⚠️ CSV Boolean Dönüşümü

TIRT:

```
bool("false")
```

çünkü:

```
bool("false") == True
```

Boş olmayan string truthy'dir.

Doğru sözleşme:

```
strip + lower

"true"
→ True

"false"
→ False

başka değer
→ ValueError
```

Örneğin:

```
maybe
→ reject
```

---

# 🏷️ `source` Alanı Nereden Geliyor?

Başlangıçtaki kafa karışıklığı:

> Ham input içinde `source` aramak.

Ama `source` input verisinin bir alanı olmak zorunda değil.

Bu pipeline'ın kendi metadata'sı.

JSON normalizer:

```
source = "json"
```

CSV normalizer:

```
source = "csv"
```

ekliyor.

Bu çok önemli bir mimari ayrım:

```
Input data
+
Pipeline metadata
=
Canonical record
```

Kaynakta `source` alanının input'tan değil pipeline tarafından üretildiği özellikle düzeltilmiş.

---

# 🔎 Normalize ≠ Validate

Günün en kritik cümlelerinden biri:

> **İki normalizer kayıtları aynı kanonik şekle getirir; validator ise bu şeklin gerçekten sözleşmeye uyup uymadığını kontrol eder.**

Örneğin normalization sonrası:

```
{
    "asset_id": "srv-002",
    "hostname": "db.internal",
    "port": "443",
    "active": True,
    "source": "json",
}
```

oluşabilir.

Shape doğru:

```
asset_id ✅
hostname ✅
port ✅
active ✅
source ✅
```

Ama:

```
port tipi ❌
```

Dolayısıyla:

> **Canonical shape ≠ valid record**

Kaynak notta bu sınır özellikle netleştirilmiş.

---

# ✅ Ortak Validator

İki ayrı validator yerine:

```
validation(record)
```

kullanıldı.

Çünkü artık normalize edilmiş iki kaynak aynı sözleşmeye bakıyor.

---

# 1️⃣ Required Fields

```
asset_id
hostname
port
active
source
```

hepsi bulunmalı.

Eksik:

```
hostname
```

varsa:

```
ValueError
```

---

# 2️⃣ Tip Kontrolü

```
asset_id → str
hostname → str
port     → exact int
active   → exact bool
source   → str
```

---

# 3️⃣ Değer Kuralları

```
asset_id
→ boş olamaz

hostname
→ boş olamaz

port
→ 1..65535

source
→ json veya csv
```

---

# 🧨 Python `bool` / `int` Mayını

Python'da:

```
isinstance(True, int)
```

sonucu:

```
True
```

Bu yüzden:

```
isinstance(port, int)
```

kullanırsak:

```
port=True
```

yanlışlıkla geçebilir.

Görev “gerçek integer” istediği için:

```
type(port) is int
```

kullanmak bilinçli bir tercih.

Aynı mantık:

```
type(active) is bool
```

için de uygulanıyor.

---

# 🧠 `source` Koşulundaki Mantık Hatası

TIRT:

```
source != "csv" or source != "json"
```

Bu neredeyse her zaman `True`.

Neden?

`source == "csv"` olsa:

```
csv != csv   → False
csv != json  → True

False OR True
→ True
```

Dolayısıyla her durumda reject.

Doğru mantık:

```
source != "csv" and source != "json"
```

yani:

> csv **değilse VE** json **değilse** hata.

Daha okunaklı alternatif:

```
source not in (
    "csv",
    "json",
)
```

Kaynak çalışmada bu mantık hatası ayrıca fark edilip düzeltilmiş.

---

# 💥 Record-Level Failure

Günün en önemli hata politikası:

> **Tek bozuk record bütün batch'i durdurmamalı.**

Yanlış yapı:

```
try
└── for record
      ├── record 1
      ├── record 2 💥
      └── record 3 artık işlenmez
```

Doğru yapı:

```
for record
│
├── try record 1
│     └── success
│
├── try record 2
│     └── reject
│
└── try record 3
      └── success
```

Yani:

```
for → try
```

Kaynak notta başlangıçtaki `try → for` modelinin batch'i erken durduracağı fark edilip değiştirilmiş.

---

# 🧠 Fail-Fast mi Continue-on-Error mı?

Burada seçim **bağlama bağlı**.

Tek bir hatalı record:

```
5 milyon kaydın tamamını
kullanılamaz hale getirmiyorsa
```

record-level:

```
reject
→ logla
→ devam et
```

mantıklı.

Ama örneğin:

```
schema/config dosyası tamamen bozuk
database bağlantısı yok
output yazılamıyor
```

gibi bütün işlemi anlamsızlaştıran hata varsa fail-fast daha doğru olabilir.

> [!warning]  
> “Continue-on-error her zaman daha iyidir.”
> 
> demek de TIRT.
> 
> **Hata scope'u karar verir.**

---

# 🧱 File-Level Failure ≠ Record-Level Failure

## Record-Level

JSON syntax geçerli:

```
{
  "port": "443"
}
```

Parser record üretir.

Sonra:

```
validator
→ yanlış tip
→ record_rejected
```

---

## File-Level

Malformed:

```
[
  {
    "asset_id": "srv-broken"
  }
```

gibi syntax tamamen bozuksa:

```
json.load()
↓
JSONDecodeError
```

ve daha record seviyesine bile ulaşılmaz.

Bu yüzden:

```
event=record_rejected
```

değil:

```
event=file_parse_failed
```

loglandı.

Kaynak testte malformed JSON olduğunda `JSON_accepted=0` ve `JSON_rejected=0` kalması da bu nedenle doğru.

---

# 🔥 Neden `JSON_rejected=0`?

Malformed dosyada:

```
0 accepted
0 rejected
```

ilk bakışta garip gelebilir.

Ama:

```
Dosya parse edilemedi
↓
Record üretilemedi
↓
Reject edilecek record da yok
```

Dolayısıyla:

```
file_parse_failed = 1 olay

record_rejected = 0
```

mantıklıdır.

---

# 📂 CSV File-Level Hataları

CSV tarafında düşünülebilecek dış katman hataları:

```
UnicodeDecodeError
csv.Error
OSError / FileNotFoundError / PermissionError
```

gibi sorunlardır.

Bunlar:

```
Tek bir kötü CSV satırı
```

ile aynı failure scope'unda değildir.

---

# 🧩 Parse Başarısızsa Değişken Tanımsız Kalabilir

Örneğin:

```
try:
    j_records = parse_json(...)
except json.JSONDecodeError:
    ...
```

Parse patlarsa:

```
j_records
```

ataması hiç gerçekleşmemiş olabilir.

Bu yüzden başlangıç:

```
j_records = []
c_records = []
```

şeklinde yapıldı.

Sonra:

```
Parse başarılı
→ gerçek kayıtlar

Parse başarısız
→ []
```

Ve:

```
for record in []:
```

sıfır tur döner.

Böylece JSON kaynağı tamamen patlasa bile CSV işlemeye devam edebilir.

---

# 📦 JSONL Output

Geçerli kayıtlar:

```
normalized.jsonl
```

dosyasına yazılıyor.

Her kayıt:

```
json.dumps(record) + "\n"
```

ile tek satır hâline geliyor.

Örnek:

```
{"asset_id":"srv-001",...}
{"asset_id":"srv-101",...}
{"asset_id":"srv-105",...}
```

Aralarında:

```
[
]
,
```

yok.

Her satır bağımsız JSON değeri.

---

# 🌊 JSONL ve Streaming Konusunda Hassas Düzeltme

Kendi sözlü cevabımda:

> “JSON array varsa milyon kayıt bir anda RAM'e girer, JSONL'de girmez.”

dedim.

Bu biraz fazla kesin.

Daha doğru:

```
Standart json.load()
→ tüm JSON document'i belleğe parse eder.

JSONL
→ doğal olarak satır satır işlenmeye çok uygundur.

Ama:
JSON array de özel streaming parser'larla
stream edilebilir.
```

Yani avantaj:

> **JSONL'nin record boundary'lerinin doğal biçimde satırlarla ayrılmış olmasıdır.**

Kaynak pipeline'da JSONL her record'u bağımsız yazmak için kullanılmış.

---

# 🪵 Structured Logging

Record reject:

```
event=record_rejected
source=json
error=...
```

veya:

```
event=record_rejected
source=csv
error=...
```

File failure:

```
event=file_parse_failed
source=json
...
```

Final summary:

```
event=processing_complete
JSON_accepted=...
JSON_rejected=...
CSV_accepted=...
CSV_rejected=...
TOTAL_accepted=...
TOTAL_rejected=...
```

---

# 📊 Neden Sayaçlar Kaynak Bazında Ayrı?

Sadece:

```
accepted=3
rejected=5
```

bilmek yerine:

```
JSON:
1 accepted
2 rejected

CSV:
2 accepted
3 rejected
```

görmek:

- Hangi kaynakta kalite problemi var?
    
- Hangi parser/producer daha sorunlu?
    
- Hangi format tarafı incelenmeli?
    

sorularına cevap verir.

---

# 🧪 İlk Gerçek Çalıştırma

Normal JSON + CSV:

```
JSON accepted = 1
JSON rejected = 2

CSV accepted = 2
CSV rejected = 3

TOTAL accepted = 3
TOTAL rejected = 5
```

`normalized.jsonl`:

```
3 kayıt
```

üretti.

Gerçek çalıştırma çıktısı da bu sayaçları doğruladı.

---

# 💥 Malformed JSON Testi

Malformed JSON + normal CSV:

```
JSON:
file_parse_failed
accepted = 0
rejected = 0

CSV:
accepted = 2
rejected = 3
```

Output:

```
yalnızca 2 geçerli CSV record
```

oldu.

Bu, bir source failure'ın diğer source'u öldürmediğini kanıtladı.

---

# 🐛 Structured Logging'deki Gerçek Bug

Beklenen:

```
grep -c \
  'event=record_rejected' \
  run.log
```

→ `5`

Ama sonuç:

```
0
```

geldi.

İlk düşünce:

> “Logging bozuk.”

Asıl bug:

```
event=recor_rejected
```

yazılmış.

`record` kelimesindeki:

```
d
```

eksikti.

Düzelttikten sonra:

```
5
```

geldi.

Kaynak debugging bölümünde bu typo özellikle bağımsız ölçümle bulunmuş.

---

# 🎯 Buradaki Büyük Debugging Dersi

Ölçüm beklenmeyen sonuç verdiğinde hemen:

```
Ana program bozuk!
```

deme.

Şunları ayrı kontrol et:

```
1. Üretim doğru mu?
2. Log sözleşmesi doğru mu?
3. Aradığım pattern doğru mu?
4. Ölçüm komutum doğru mu?
```

Yani:

> **Ölçüm aracının ve observability sözleşmesinin kendisi de bug'lı olabilir.**

---

# 🐧 Linux — Artifact'i Bağımsız Kanıtlarla Ölçmek

Bugün yalnız uygulamanın kendi summary loguna güvenilmedi.

Birden fazla kanıt üretildi.

---

# 📏 Output Record Sayısı

```
wc -l normalized.jsonl
```

sonuç:

```
3
```

Bu:

```
Output'ta 3 satır var.
```

kanıtı.

---

# 🔍 Rejection Sayısı

```
grep -c \
  'event=record_rejected' \
  run.log
```

sonuç:

```
5
```

---

# 🔍 Parse Failure Sayısı

```
grep -c \
  'event=file_parse_failed' \
  run.log
```

normal çalıştırmada:

```
0
```

---

# 📜 Final Summary

```
grep \
  'event=processing_complete' \
  run.log
```

ile uygulamanın kendi sayaç özeti çıkarıldı.

---

# 🧩 JSONL'yi `jq` ile İkinci Kez Parse Et

```
jq -c . normalized.jsonl \
  | wc -l
```

sonuç:

```
3
```

Bu çok güçlü:

```
wc
→ 3 satır olduğunu söyledi.

jq
→ Bu satırların parse edilebilir JSON olduğunu doğruladı.

wc
→ jq'dan geçen kayıtların sayısını 3 buldu.
```

Kaynak çalışmada output, rejection logları ve JSON parse edilebilirliği birden fazla bağımsız araçla doğrulanmış.

---

# ❓ 100 Input → 92 Output: Veri Kaybı mı Controlled Rejection mı?

Sözlü turda takıldığım önemli soru.

Sadece:

```
Input = 100
Output = 92
```

bilmek yetmez.

Eksik 8 kayıt:

```
Kayboldu mu?
Reddedildi mi?
Parser hiç okuyamadı mı?
Program yarıda mı kesildi?
```

bilmiyoruz.

Kanıt zinciri:

```
input record count
= 100

accepted output count
= 92

record_rejected count
= 8

processing_complete:
accepted=92
rejected=8
```

ve:

```
92 + 8 = 100
```

ise kontrollü rejection politikasıyla açıklanabilir.

Ama:

```
92 output
3 reject
```

varsa:

```
5 record nerede?
```

sorusunu araştırmak gerekir.

> [!important]  
> **Rejection = pipeline'ın bilinçli olarak geçersiz kabul edip kayıt altına aldığı record.**
> 
> Sessizce kaybolan record rejection değildir.

---

# 🧰 Linux Araç Seçimi

## JSON field/type

```
jq
```

Çünkü veri yapısal.

---

## Log pattern

```
grep -E
```

Çünkü düz metin/event satırı arıyorum.

---

## Son N event

```
tail
```

Çünkü dosyanın konumu önemli.

---

## Basit CSV kolonu

```
awk
```

Çünkü alan/kolon bazlı işlem.

Kaynak çalışmada bu araçların hangi veri problemi için seçileceği ayrıca uygulanmış.

---

# ⚠️ `jq` ile JSONL İlk Record Kontrolü

Kaynakta:

```
jq '.[0].port | type' normalized.jsonl
```

örneği yazılmış.

Burada küçük bir nüans var.

`normalized.jsonl`:

```
tek büyük JSON array
```

değil; art arda bağımsız JSON object'lerdir.

Dolayısıyla her satır object ise daha doğal sorgu:

```
jq -s '.[0].port | type' \
  normalized.jsonl
```

veya ilk satırı seçip:

```
head -n 1 normalized.jsonl \
  | jq '.port | type'
```

mantığıdır.

> [!warning]  
> `. [0]` yaklaşımı array üzerinde doğaldır; JSONL stream'i doğrudan array değildir.

---

# 🌳 Git — Generated Artifact Incident

Program şu dosyaları üretiyor:

```
normalized.jsonl
run.log
```

Bunlar kaynak kod değil, runtime artifact.

Ama başlangıçta Git:

```
?? Day20/normalized.jsonl
?? Day20/run.log
```

gösteriyordu.

Yani:

```
untracked ✅
ignored ❌
```

Kaynak deneyde tüm Day20 dosyaları `--untracked-files=all` ile tek tek görüntülenmiş.

---

# 🔥 Untracked ≠ Ignored

Bu ikisi aynı değil.

## Untracked

Git dosyayı görüyor ama henüz repository history'ye eklenmemiş.

```
??
```

---

## Ignored

Git ignore kuralları nedeniyle normal tracking adaylarının dışında bırakılıyor.

> [!danger]  
> `??` görmek:
> 
> “Bu dosya ignore edilmiş.”
> 
> anlamına gelmez.

---

# 👀 `git status --short --untracked-files=all`

Normal:

```
git status --short Day20/
```

bazen:

```
?? Day20/
```

diye klasörü topluca gösterebilir.

Detay:

```
git status \
  --short \
  --untracked-files=all \
  Day20/
```

ile içerideki untracked dosyalar tek tek görülebilir.

---

# 🧾 `.gitignore`

Mevcut `.gitignore` kontrol edildi:

```
cat .gitignore
```

Day20 artifact kuralları yoktu.

Sonra:

```
Day20/normalized.jsonl
Day20/*.log
```

eklendi.

Burada:

```
Day20/*.log
```

yalnız `run.log` değil, aynı klasörde gelecekte üretilecek `.log` artifact'larını da kapsıyor.

---

# 🔬 `git check-ignore -v`

İlk:

```
git check-ignore -v \
  Day20/normalized.jsonl \
  Day20/run.log
```

çıktı vermedi.

Anlamı:

```
Bu dosyalar aktif bir ignore rule ile eşleşmiyor.
```

Kurallar eklendikten sonra:

```
.gitignore:10:Day20/normalized.jsonl ...
.gitignore:11:Day20/*.log ...
```

çıktısı alındı.

Böylece ignore politikasının gerçekten uygulandığı kanıtlandı.

---

# 🧠 `.gitignore` vs `git check-ignore`

```
.gitignore
→ Politikanın tanımı

git check-ignore
→ Belirli dosya bu politikaya gerçekten uyuyor mu?
```

Yani:

> `.gitignore` dosyasına bakmak başka, Git'in belirli dosyaya nasıl davrandığını ölçmek başka.

---

# 📦 Staging Snapshot'ını Kontrol Et

Sonra:

```
git add .gitignore Day20/
```

yapıldı.

Ardından:

```
git diff \
  --cached \
  --name-status
```

çıktısı:

```
M .gitignore
A Day20/assets.csv
A Day20/assets.json
A Day20/day20.py
A Day20/malformed.json
```

Ama:

```
Day20/normalized.jsonl
Day20/run.log
```

yok.

Bu en güçlü kanıtlardan biri.

Çünkü:

```
“ignore dosyasında yazıyor”
```

değil:

```
“bir sonraki commit snapshot'ına gerçekten girmedi”
```

kanıtlandı.

---

# 💾 Commit

Sonra:

```
git commit -m \
  "day20: add pipeline and ignore generated artifacts"
```

commit edildi.

Son status:

```
temiz
```

oldu.

---

# 🚨 `.gitignore` Daha Önce Tracked Dosyayı Neden Otomatik Untrack Etmez?

Sözlü turda cevaplayamadığım önemli soru.

Çünkü `.gitignore` esas olarak:

> **Untracked dosyaların gelecekte tracking'e alınmasını engellemek için kullanılır.**

Ama dosya daha önce:

```
git add
↓
git commit
```

ile tracked hâle geldiyse Git artık onu history'nin parçası olarak biliyor.

`.gitignore` eklemek:

```
“Bu tracked dosyayı repository'den unut.”
```

komutu değildir.

Zihinsel model:

```
.gitignore
→ Tracking politikasını etkiler.

Git index/history
→ Dosyanın zaten tracked olup olmadığını bilir.
```

Daha önce tracked bir generated artifact için ayrıca index'teki tracking durumunu değiştirmek gerekir.

---

# 🔎 Generated Artifact İçin Doğru Git Kanıt Zinciri

```
1. Git şu anda ne görüyor?
   ↓
git status --short --untracked-files=all

2. Ignore rule gerçekten eşleşiyor mu?
   ↓
git check-ignore -v FILE

3. Stage snapshot'ına ne girdi?
   ↓
git diff --cached --name-status

4. Generated artifact yok mu?
   ↓
Evet

5. Commit
```

Kaynak notta bu dört aşamalı state → ignore → stage → commit modeli günün Git özeti olarak çıkarılmış.

---

# ⏳ Git'te “Şimdi” ve “Geçmiş” Araçları

Sözlü turda takıldığım diğer önemli ayrım:

## Working Tree / Index araçları

Şimdiki hazırlık durumunu sorar:

```
git status
→ Şu anda ne durumda?

git diff
→ Working Tree'de henüz stage edilmemiş ne değişti?

git diff --staged
→ Bir sonraki commit'e ne hazırlanmış?
```

---

## History araçları

Geçmişi sorar:

```
git log
→ Geçmişte hangi commit'ler var?

git show COMMIT
→ O commit ne yaptı?
```

Kısa formül:

```
status / diff / staged
→ ŞİMDİ

log / show
→ GEÇMİŞ
```

---

# 🧯 Hata Avı

## 1. Parser kabul ettiyse record geçerlidir

TIRT.

Parser formatı bilir; validator uygulama sözleşmesini bilir.

---

## 2. JSON ve CSV aynı normalization davranışını istemek zorundadır

TIRT.

Formatların tip temsil biçimi farklı.

---

## 3. JSON `"443"` değerini int'e zorla çevirmek her zaman iyidir

TIRT.

Hatalı producer verisini gizleyebilir.

---

## 4. CSV `"443"` string geldi diye kayıt doğrudan invalid'dir

TIRT.

CSV'nin doğal temsilinden dolayı type conversion gerekebilir.

---

## 5. `source` input'tan gelmek zorundadır

TIRT.

Pipeline-generated metadata olabilir.

---

## 6. `source != "csv" or source != "json"` doğru validation'dır

TIRT.

Koşul her zaman doğruya kayar.

---

## 7. Canonical shape'e geldiyse record valid'dir

TIRT.

Shape doğru olsa bile tip/range/value rule bozuk olabilir.

---

## 8. `try` bütün `for` döngüsünü sarmalı

Record-level continue-on-error politikasında TIRT.

Her kayıt kendi `try/except` sınırına sahip olmalı.

---

## 9. Malformed JSON'daki kayıtlar `record_rejected` sayılmalı

TIRT.

Parser record üretmedi; file-level failure oluştu.

---

## 10. JSONL mutlaka tüm dataset'i RAM dışında işler

Fazla kesin.

JSONL streaming'e doğal olarak uygundur; ama davranış kullandığın okuyucu/yazıcı tasarımına bağlıdır.

---

## 11. `grep 0 döndü → logging sistemi bozuk`

TIRT.

Pattern, event adı veya ölçüm komutu da yanlış olabilir.

---

## 12. 100 input / 92 output varsa 8 record veri kaybıdır

Kanıt olmadan TIRT.

8 kontrollü rejection da olabilir.

---

## 13. JSON field type kontrolünü `grep` ile yapmak yeterlidir

TIRT.

`grep` JSON syntax/structure/type bilmez.

---

## 14. Untracked ile ignored aynı şeydir

TIRT.

```
untracked
→ Git henüz takip etmiyor

ignored
→ Ignore policy nedeniyle tracking adayı değil
```

---

## 15. `.gitignore'a yazdım → kesin çalışıyor`

TIRT.

`git check-ignore` ve staging snapshot ile doğrula.

---

## 16. `.gitignore` daha önce commit edilmiş dosyayı otomatik untrack eder

TIRT.

Tracked state zaten Git index/history tarafından bilinmektedir.

---

## 17. `git log` staged dosyaları gösterir

TIRT.

Commit history'yi gösterir.

---

## 18. `git show` bir sonraki commit'e hazırlanmış değişiklikleri gösterir

TIRT.

Geçmişteki belirli commit'i inceler.

---

# 🧠 Kafaya Kazı

> [!quote]  
> Parser formatı bilir; validator application contract'ı bilir.

> [!quote]  
> JSON tip taşır, CSV alanları çoğunlukla string temsilinden gelir.

> [!quote]  
> Kaynağa özgü representation farkını normalizer çözer.

> [!quote]  
> Ortak canonical contract'ı validator bilir.

> [!quote]  
> Normalization hatalı veriyi gizlememeli.

> [!quote]  
> Canonical shape, valid record demek değildir.

> [!quote]  
> File-level failure'da record henüz oluşmamış olabilir.

> [!quote]  
> Record-level failure tek başına bütün batch'i öldürmek zorunda değildir.

> [!quote]  
> Controlled rejection = bilerek reddedilmiş ve observability ile hesaba katılmış record.

> [!quote]  
> Input count = accepted + rejected gibi invariant'lar veri kaybı araştırmasında çok değerlidir.

> [!quote]  
> Tek bir ölçüme güvenme; artifact + log + bağımsız araç kullan.

> [!quote]  
> `jq` yapı, `grep` pattern, `tail` konum, `awk` basit alan işlemi içindir.

> [!quote]  
> `.gitignore` politika tanımlar; `git check-ignore` politikayı ölçer.

> [!quote]  
> Untracked, ignored ve staged üç farklı Git durumudur.

> [!quote]  
> Bir sonraki commit'i `git diff --cached` ile kanıtla.

> [!quote]  
> `status/diff` şimdiyle, `log/show` history ile ilgilenir.

---

# 📌 30 Saniyelik Özet

```
INPUT
JSON + CSV

PARSE
JSON
→ json.load()
→ tipleri korur

CSV
→ DictReader
→ alanlar string ağırlıklı

NORMALIZE
JSON
→ whitespace temizle
→ yanlış tipi zorla düzeltme

CSV
→ strip
→ int dönüşümü
→ true/false → bool

SOURCE
json normalizer
→ source="json"

csv normalizer
→ source="csv"

VALIDATOR
required fields
↓
exact types
↓
value/range rules

FAILURE
Malformed file
→ file_parse_failed

Invalid parsed record
→ record_rejected

RECORD POLICY
for record
→ try
→ normalize
→ validate
→ accepted / rejected
→ devam

OUTPUT
accepted
→ normalized.jsonl

rejected
→ structured log

OBSERVABILITY
wc
→ output count

grep
→ reject count

jq
→ JSON gerçekten parse oluyor mu?

processing_complete
→ summary

INVARIANT
input
=
accepted + rejected
(+ ayrıca açıklanmış file-level durumlar)

GIT
status
→ state

check-ignore
→ ignore rule eşleşiyor mu?

git add
↓
diff --cached
→ commit snapshot

GENERATED
normalized.jsonl
run.log
→ ignore

TIME
status/diff
→ şimdi

log/show
→ geçmiş
```

---

# ✅ Günün Kazanımları

- JSON ve CSV aynı program içinde iki bağımsız input kaynağı olarak işlendi
    
- Kayıtların birbirleriyle eşleştirilmesi gerekmediği anlaşıldı
    
- Parse → normalize → validate pipeline sınırları kuruldu
    
- JSON ve CSV parser'ları ayrıldı
    
- JSON ve CSV'nin type temsil farkı anlaşıldı
    
- `DictReader` yaşam süresi ve açık file handle ilişkisi fark edildi
    
- `newline=""` kullanım amacı öğrenildi
    
- JSON için conservative normalization uygulandı
    
- CSV için format-specific type conversion uygulandı
    
- String olmayan JSON alanında `.strip()` patlama riski engellendi
    
- `source` pipeline metadata'sı olarak üretildi
    
- İki kaynağa ortak canonical validator kullanıldı
    
- `bool` / `int` subclass nüansı tekrar uygulandı
    
- `source` validation'daki `or` mantık hatası düzeltildi
    
- `for → try` yapısıyla record-level failure izolasyonu kuruldu
    
- Continue-on-error politikasının kapsamı öğrenildi
    
- File-level ve record-level failure ayrıldı
    
- Malformed JSON için ayrı `file_parse_failed` event'i üretildi
    
- Parse failure sonrası diğer source'un işlemeye devam etmesi sağlandı
    
- Parser sonucu değişkenlerin önceden boş listeyle initialize edilmesi uygulandı
    
- JSONL output tek dosyada iki kaynağın accepted kayıtlarını taşıdı
    
- Source bazlı accepted/rejected sayaçları üretildi
    
- Structured logging ile reject nedenleri kaydedildi
    
- Event adı typo'su bağımsız `grep` ölçümüyle yakalandı
    
- Ölçüm aracının kendisinin de debug edilmesi gerektiği öğrenildi
    
- `wc -l` ile accepted artifact sayısı doğrulandı
    
- `grep -c` ile reject event sayısı doğrulandı
    
- `jq` ile JSONL ikinci parser üzerinden kontrol edildi
    
- Controlled rejection ile sessiz veri kaybı ayrıldı
    
- `jq`, `grep`, `tail`, `awk` araç seçim sınırları pekiştirildi
    
- Generated artifact kavramı öğrenildi
    
- Untracked ile ignored ayrıldı
    
- `.gitignore` mevcut içeriği önce kontrol edildi
    
- Day20 output/log artifact'ları ignore edildi
    
- `git check-ignore -v` ile gerçek rule eşleşmesi doğrulandı
    
- `git diff --cached --name-status` ile commit snapshot doğrulandı
    
- Generated artifact'ların commit'e girmediği kanıtlandı
    
- Daha önce tracked edilmiş dosyada `.gitignore` davranışının neden farklı olduğu anlaşıldı
    
- Git'te şimdiye bakan araçlarla history araçları ayrıldı
    

> [!success] 🚀 Gün sonu sonucu  
> Gün 20 sonunda yaptığım şey artık yalnız:
> 
> ```
> “JSON ve CSV okuyup çıktı üretmek”
> ```
> 
> değil.
> 
> Gerçek model:
> 
> ```
> FORMAT-SPECIFIC INPUT
>         ↓
> PARSER
>         ↓
> SOURCE-SPECIFIC NORMALIZATION
>         ↓
> CANONICAL RECORD
>         ↓
> SHARED VALIDATION
>         ↓
> ┌───────────────┬────────────────┐
> │ ACCEPTED      │ REJECTED       │
> ↓               ↓
> JSONL           structured log
> ```
> 
> Üstelik failure scope'u da ayrıldı:
> 
> ```
> FILE bozuk
> → file_parse_failed
> 
> RECORD bozuk
> → record_rejected
> → batch devam eder
> ```
> 
> ve sonuçlar yalnızca programa güvenilerek değil:
> 
> ```
> wc
> grep
> jq
> structured summary
> ```
> 
> gibi bağımsız kanıtlarla doğrulandı.
> 
> Git tarafındaki eşdeğer ders de aynı:
> 
> ```
> “.gitignore'a yazdım.”
> ```
> 
> demek yerine:
> 
> ```
> Git dosyayı nasıl görüyor?
> ↓
> Rule gerçekten eşleşiyor mu?
> ↓
> Stage snapshot'ına girdi mi?
> ```
> 
> sorularını ölçmek gerekiyor.
> 
> Günün en kritik cümlesi:
> 
> **İyi bir veri pipeline'ı yalnız veri dönüştürmez; format farklarını izole eder, geçersiz kayıtların scope'unu doğru belirler, hiçbir record'un sessizce kaybolmamasını sağlar ve ürettiği artifact'ları bağımsız kanıtlarla doğrulanabilir hâle getirir.**