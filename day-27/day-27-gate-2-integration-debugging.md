---
title: "Gate 2 — Data Pipeline, Failure Policy, Process Debugging, Git State, Docker Persistence ve CAASM"
tags:
  - coreops
  - gate2
  - python
  - data-pipeline
  - json
  - normalization
  - validation
  - failure-policy
  - linux
  - process
  - signals
  - git
  - docker
  - persistence
  - caasm
aliases:
  - "Gate 2 Entegrasyon ve Debugging Notu"
  - "Gün 27 Gate 2"
status: completed
---

# 🧠 Gate 2 — Data Pipeline, Failure Policy, Process Debugging, Git State, Docker Persistence ve CAASM

> [!abstract] 🎯 Ana fikir  
> Bu çalışmada artık tek tek komut veya Python fonksiyonu öğrenmekten ziyade **bir sistemin katmanlarını ayırıp her problemi doğru sahibine bağlamaya** başladım.
> 
> Genel zihinsel model:
> 
> ```
> INPUT
> ↓
> PARSE
> ↓
> NORMALIZE
> ↓
> VALIDATE
> ↓
> ACCEPT / REJECT
> ↓
> PERSIST
> ↓
> OBSERVE / DEBUG
> ```
> 
> Runtime tarafında:
> 
> ```
> Process identity
> ↓
> Runtime state
> ↓
> Signal / shutdown
> ```
> 
> Git tarafında:
> 
> ```
> Working Tree
> ↓
> Index
> ↓
> HEAD
> ```
> 
> Docker tarafında:
> 
> ```
> Image
> ↓
> Container
> ↓
> Mount / Volume
> ↓
> Persistent data
> ```
> 
> CAASM tarafında:
> 
> ```
> Source records
> ↓
> Identity evidence
> ↓
> Correlation
> ↓
> Merge / Split decision
> ```

---

# ⚡ Başlangıç Retrieval

## `.gitignore` ve tracked dosya

Dosya daha önce commit edildiyse sonradan `.gitignore` içine yazmak tracked state'i otomatik kaldırmaz. Kaynak cevabımın ana fikri doğruydu.

Ama cümleyi daha doğru kurmam gerek:

```
Dosya tracked
↓
.gitignore rule ekle
↓
dosya hâlâ tracked
```

Tracking'i ayrıca Index'ten çıkarmam gerekir.

Örneğin mantıksal olarak:

```
Index'ten tracking kaldır
↓
commit et
↓
Working Tree'deki dosya kalabilir
↓
.gitignore nedeniyle artık normal untracked adaylar arasında gösterilmez
```

> [!warning]  
> “Tracking'den çıkınca dosya untracked olarak görünür.”
> 
> her zaman tam doğru ifade değil.
> 
> `.gitignore` kuralı eşleşiyorsa dosya **ignored** olur.

---

# Working Tree / Index / HEAD

Verilen state:

```
HEAD         = A
INDEX        = A
WORKING TREE = B
```

doğru.

Dolayısıyla:

```
git diff
→ Working Tree ↔ Index

git diff --staged
→ Index ↔ HEAD
```

---

# 100 Input → 92 Output

Direkt:

```
8 kayıt kayboldu
```

diyemem.

Kanıt zinciri:

```
Input count
→ gerçekten 100 mü?

Output count
→ gerçekten 92 accepted mı?

Rejected records
→ kalan 8 kayıt gerçekten rejection olarak hesaplandı mı?
```

Kaynak cevabım da input, output ve rejection kanıtlarını ayrı ayrı istemiş.

İdeal invariant:

```
input
=
accepted
+
rejected
```

Dosya-level parse failure gibi ayrı failure class'ları varsa onları da ayrıca hesaba katmam gerekir.

---

# ⚖️ Continue-on-Error Kararım

Recordlar birbirinden bağımsızsa:

```
record 1 ✅
record 2 ❌
record 3 ✅
```

tek bir validation failure yüzünden bütün batch'i bırakmak istemiyorum.

Kararım:

```
record-level validation failure
→ reject
→ logla
→ devam et
```

Trade-off:

```
100 input
→ 92 success
→ 8 failure
```

gibi partial success üretilebilir.

Bu yüzden observability şart:

- hangi record?
    
- neden reddedildi?
    
- kaç tane?
    
- retry gerekir mi?
    

Kaynak kararımda da continue-on-error bu gerekçeyle seçilmiş.

---

# 🏗️ Gate 2 Problem Tanımı

İhtiyaç:

> JSON ve CSV asset kayıtlarını al, işle, accepted/rejected çıktı üret ve SIGTERM geldiğinde current record'u yarım bırakmadan kontrollü kapan.

Kaynak problem tanımı, invariant ve sorumluluk ayrımı bu şekilde kurulmuş.

Ana invariant:

> **SIGTERM geldiği sırada işlenen record yarım kalmamalı veya sessizce kaybolmamalı.**

Bu Gate 2'nin en kritik runtime contract'ı.

---

# 🧱 Tasarladığım Katmanlar

## 1. Parser

Bilmesi gereken:

```
Input format
→ nasıl parse edilir?
```

Bilmemesi gereken:

- validation policy
    
- shutdown
    
- logging policy
    
- main orchestration
    
- output persistence policy
    

---

## 2. Normalizer

Görevi:

> Source-specific representation'ı canonical forma yaklaştır.

Bilmemesi gereken:

```
parser orchestration
SIGTERM policy
output destination
```

---

## 3. Validator

Görevi:

> Canonical record application contract'ına uyuyor mu?

Validator:

```
normalized record
+
validation rules
```

bilir.

Parser'ın dosyayı nasıl okuduğunu bilmesine gerek yok.

---

# 🌊 Tasarlanan Veri Akışı

```
                    MAIN
                     │
          ┌──────────┴──────────┐
          ↓                     ↓
       JSON                    CSV
          ↓                     ↓
     JSON Parser           CSV Parser
          ↓                     ↓
   JSON Normalizer       CSV Normalizer
          └──────────┬──────────┘
                     ↓
                 Validation
                     ↓
               valid / invalid
                ↙         ↘
       accepted.jsonl   rejected.jsonl
```

Bu tasarım kaynakta açıkça çizilmiş.

---

# ⚠️ Tasarım ile Mevcut Implementasyonu Ayır

Burada önemli bir gerçek var:

## Tasarım

```
JSON + CSV
accepted.jsonl
rejected.jsonl
SIGTERM graceful shutdown
```

## Şu anki live Python implementasyonu

Kaynakta görünen kod:

```
JSON parser ✅
normalization ✅
validation ✅
output.jsonl ✅
record reject logging ✅
file parse failure ✅
CSV parser ❌ henüz görünmüyor
rejected.jsonl ❌ henüz yazılmıyor
SIGTERM handler ❌ Gate2 koduna henüz entegre değil
```

Mevcut `main()` yalnız bir JSON dosyası alıyor ve valid kayıtları `output.jsonl` içine yazıyor; rejection'lar log üzerinden tutuluyor.

> [!important]  
> **Planlanan architecture ile bugün gerçekten çalışan implementation aynı şey değil.**
> 
> Not tutarken yapmayı planladığım şeyi yapılmış gibi yazmamalıyım.

---

# 🔄 State Machine

Tasarladığım önemli state'ler:

```
READY
↓
PROCESSING_RECORD
↓
READY
```

Shutdown geldiğinde:

```
PROCESSING_RECORD
+
SIGTERM
↓
shutdown requested
↓
current record tamamla
↓
CLEANUP
↓
STOPPED
```

Kaynak state geçişlerinde bu akış belirtilmiş.

---

# 🧠 Daha Temiz Shutdown State Modeli

Kafamda bunu şöyle tutmak daha kolay:

```
READY
│
├── record geldi
│      ↓
│  PROCESSING
│      ↓
│   commit record
│      ↓
│    READY
│
└── SIGTERM
       ↓
   SHUTDOWN_REQUESTED
       ↓
     CLEANUP
       ↓
     STOPPED
```

Eğer SIGTERM processing sırasında gelirse:

```
PROCESSING
+
SHUTDOWN_REQUESTED
↓
current record atomic boundary tamamlanır
↓
yeni record alınmaz
↓
cleanup
```

---

# 💥 Failure Model

## Failure 1 — Parse

```
JSON / CSV syntax-format problemi
↓
Parser katmanı
```

---

## Failure 2 — Normalization

```
Parse edildi
↓
canonical forma dönüşüm yapılamıyor
↓
Normalizer
```

---

## Failure 3 — Validation

```
Normalized record
↓
application contract başarısız
↓
Validator
```

Kaynak failure modeli bunları ayrı sahip katmanlara bağlamış.

---

# 🔎 Uygulama / Teşhis Sıram

En başta shutdown koduyla uğraşmak yerine içten dışa doğrulamak daha doğru:

```
1. Parser gerçekten çalışıyor mu?

2. Normalizer canonical form üretiyor mu?

3. Validator doğru ayırıyor mu?

4. Accepted/rejected persistence doğru mu?

5. Runtime config doğru mu?

6. Normal veri akışı oturduktan sonra SIGTERM ekle.

7. Idle state'te SIGTERM test et.

8. Record processing sırasında SIGTERM test et.

9. Docker + persistent storage altında test et.
```

Kaynak planım da bu sırayla ilerliyor.

> [!success]  
> Güzel debugging/refactor refleksi:
> 
> **Normal data path çalışmadan shutdown complexity ekleme.**

---

# 🐍 Mevcut JSON Pipeline

## Parser

```
file
↓
json.load()
↓
Python object
```

---

# Normalization

Alanlar:

```
asset_id
→ str ise strip

hostname
→ str ise strip

port
→ koru

active
→ koru

tags
→ list ise string elemanlara strip
→ string olmayan elemanları kaybetme
```

Kaynak normalizer bu mantıkla yazılmış.

---

# 🔥 `tags` Alanındaki Gerçek Hatam

Başlangıçta `append()` yerleşimi yüzünden string olmayan tag değerlerini düşürme riski vardı.

Örneğin:

```
["prod", 53, "api"]
```

normalizer:

```
53
```

değerini sessizce kaybederse validator artık problemi göremez.

Doğru yaklaşım:

```
string
→ strip
→ append

string değil
→ aynen append
→ validator'a kadar taşı
```

Kaynakta AI'dan alınan yardım da tam olarak bu hatayı fark ettirmiş.

> [!important]  
> **Normalizer hatalı veriyi gizlememeli.**
> 
> Validation'ın görmesi gereken evidence'ı silmek kötü normalization'dır.

---

# ✅ Validator Contract

Required:

```
asset_id
hostname
port
active
tags
```

Tipler:

```
asset_id → str
hostname → str
port → exact int
active → exact bool
tags → list[str]
```

Range:

```
1 <= port <= 65535
```

Kaynak validator bunları açık şekilde kontrol ediyor.

---

# 🧨 `port=True` Testi

Python'daki klasik tuzak:

```
bool
→ int ile inheritance ilişkisine sahip
```

Bu nedenle:

```
isinstance(True, int)
```

istenmeyen sonucu verebilir.

Validator:

```
type(port) is int
```

kullandığı için:

```
"port": true
```

reddedildi.

Gerçek test:

```
WARNING:
port integer olması gerekiyor!

accepted=0
rejected=1
```

oldu.

---

# 🧪 Gerçek Test Sonuçları

## Geçerli Dataset

```
accepted=3
rejected=0
```

ve üç canonical record output'a yazıldı.

---

## Eksik Hostname

```
accepted=1
rejected=1
```

ve geçersiz record output'a girmedi.

---

## Malformed JSON

```
event=file_parse_failed
exit code=47
```

oldu.

Bu:

```
record-level failure
```

değil:

```
file-level parse failure
```

---

# ⚖️ Fail-Fast vs Continue-on-Error

Kararım:

```
Malformed file
→ fail-fast

Invalid individual record
→ continue-on-error
```

Gerekçe:

```
Malformed JSON
→ record sınırlarına güvenemiyorum
→ parser data üretmedi

Invalid record
→ diğer recordlardan bağımsız olabilir
→ reject edip devam edebilirim
```

Kaynak kararımda da bu ayrım açıkça belirtilmiş.

---

# 🔥 `string indices must be integers` Hatası

Aldığım hata:

```
TypeError:
string indices must be integers, not 'str'
```

Sebep:

`main()`:

```
for record in parsered:
```

diyor.

Kod burada:

```
parsered
→ list[record]
```

bekliyor.

Ama test JSON'unda top-level tek object olunca:

```
parsered
→ dict
```

oluyor.

Dict üzerinde döngü:

```
record
→ "asset_id"
→ "hostname"
→ ...
```

gibi key string'leri getiriyor.

Sonra:

```
normalization("asset_id")
```

içinde:

```
loaded["asset_id"]
```

denmeye çalışılıyor.

Ama `loaded` artık string.

Sonuç:

```
string indices must be integers
```

Kaynakta bu hata top-level input shape'in beklenen liste olmamasına bağlanmış.

---

# 🧠 Buradan Çıkardığım Daha Büyük Ders

Parser contract yalnız:

```
“geçerli JSON”
```

olmamalı.

Ayrıca:

```
Top-level shape ne?
list mi?
object mi?
```

tanımlanmalı.

Örneğin Gate2 batch contract:

```
top-level JSON
→ list[record]
```

ise bunu explicit doğrulamak daha temiz olur.

---

# 🐧 Linux Incident — PID Var Ama Program İlerlemiyor

Semptom:

> PID hâlâ mevcut ama heartbeat/output ilerlemiyor.

Üç hipotez:

```
H1
→ Process STOP state'e geçti.

H2
→ Process yaşıyor ama sleeping/blocking.

H3
→ Elimdeki PID yanlış/eski process'e ait.
```

Kaynak Linux teşhis planı bu üç farklı state/identity hipotezini ayırıyor.

---

# 🔬 İlk Ayırıcı Deney

```
ps -p PID -o pid,ppid,stat,comm,args
```

Tek komutla:

```
PID hâlâ var mı?
↓
PPID ne?
↓
STAT ne?
↓
Gerçek command ne?
↓
Args beklediğim uygulama mı?
```

görebilirim.

---

# Beklenen Sonuçlar

## H1 — Stop

```
STAT
→ T / T+
```

---

## H2 — Waiting

```
STAT
→ örneğin S
```

ve command doğru uygulamadır.

---

## H3 — Identity

```
PID yok
```

veya:

```
comm/args
→ beklediğim uygulamayla eşleşmiyor
```

---

# 🧪 Controlled STOP Lab

Python parent process:

```
Parent PID: 10677
Child PID: 10678
```

ve child:

```
sleep 100000
```

olarak başlatıldı.

İlk `ps`:

```
STAT = S+
```

gösterdi.

Sonra:

```
kill -STOP 10677
```

uygulandı.

Yeni `ps`:

```
STAT = T
```

ve:

```
/proc/10677/status
→ State: T (stopped)
```

çıktısını verdi.

---

# `/proc` ve `pstree` Kanıtları

```
/proc/PID/status
→ process state

/proc/PID/cmdline
→ gerçek invocation

pstree -p PID
→ process-child ilişkisi
```

Deney:

```
python(10677)
└── sleep(10678)
```

olarak görüldü.

---

# 🌳 Git Live Failure

Başlangıç commit'i:

```
app.py
→ print("v1")

config.json
→ tracked
```

Sonra Working Tree:

```
app.py
→ print("v2")

app.log
→ untracked runtime artifact
```

oldu.

---

# `git add app.py`

Sonra:

```
HEAD
→ app.py v1

INDEX
→ app.py v2

WORKING TREE
→ app.py v2
```

Bu yüzden:

```
git diff
→ boş

git diff --cached
→ v1 → v2
```

Gerçek diff de bunu gösterdi.

---

# 🎯 `git show HEAD:app.py`

Sonuç:

```
print("v1")
```

Bu çok temiz bir kanıt:

```
HEAD
→ hâlâ v1

INDEX
→ v2
```

---

# 🧯 Yanlışlıkla `app.log` Stage Ettim

İstediğim:

```
Index'i değiştir
Working Tree'deki app.log dosyasını koru
```

Bu yüzden:

```
git restore --staged app.log
```

kullandım.

Sonuç:

```
app.py
→ staged

app.log
→ Working Tree'de duruyor
→ artık staged değil
```

Kaynak canlı deneyde de tam bu state oluşmuş.

---

# 🧠 `git restore --staged`

Zihinsel anlam:

> **Index'i değiştir, Working Tree içeriğine dokunma.**

Bu özellikle yanlışlıkla stage edilen runtime artifact'leri geri almak için güçlü.

---

# 🐳 Docker Persistence Incident

Semptom:

> Yeni container `/data` altında eski veriyi göremiyor.

Üç hipotez:

```
H1
→ yanlış named volume

H2
→ doğru volume ama yanlış destination path

H3
→ veri volume'a hiç gitmedi,
   eski container writable layer'daydı
```

Kaynak Docker teşhisinde bu üç sahip katman ayrılmış.

---

# 🔬 İlk Ayırıcı Deney

```
docker inspect
↓
Mounts
```

özellikle:

```
Source
Destination
Type
RW
```

kontrol edilir.

Beklediğim:

```
Source
→ coreops-data

Destination
→ /data
```

---

# 🧪 Persistence Lab

Writer:

```
coreops-data
→ /data
```

mount'u ile:

```
/data/state.txt
→ ESKI VERI
```

yazdı.

Reader aynı volume'u bağlayınca:

```
Bulunan veri: ESKI VERI
```

gördü.

---

# 💥 Hatalı Reader

Yanlışlıkla:

```
coreops-data-wrong
→ /data
```

bağlandı.

Sonuç:

```
VERI BULUNAMADI
```

`docker inspect`:

```
reader-ok
→ coreops-data → /data

reader-bad
→ coreops-data-wrong → /data
```

kanıtını verdi.

---

# 🧪 Storage'ın Gerçekten Sağlam Olduğunu Kanıtlama

Application container'ından bağımsız Alpine container'a:

```
coreops-data
```

mount edildi.

```
/data/state.txt
→ ESKI VERI
```

hâlâ vardı.

Yanlış volume ise boştu.

Böylece:

```
“veri silindi”
```

hipotezi zayıfladı.

Root cause:

> **Yeni container yanlış named volume ile oluşturulmuş.**

Kaynak teşhis de aynı sonuca ulaşıyor.

---

# 🎯 Persistence Debugging Modeli

```
Yeni container data görmüyor
↓
Doğru image mı?
↓
Doğru container path mi?
↓
Doğru volume mu?
↓
docker inspect Mounts
↓
Storage'ı bağımsız container ile kontrol et
```

---

# 👻 Mount Shadowing Countercase

Image'ın içinde:

```
/data/example.txt
```

oluşturuldu.

Mount olmadan:

```
IMAGE ICINDEKI DOSYA
```

göründü.

Sonra boş host directory:

```
empty-data
→ /data
```

bind mount edildi.

Bu kez:

```
/data/example.txt
→ görünmedi
```

Ama mount olmadan yeni container açınca dosya tekrar göründü.

Sonuç:

> **Dosyanın silindiğini değil, runtime filesystem görünümünün değiştiğini kanıtladım.**

---

# 🛡️ CAASM System Design

İki record:

```
aynı hostname
ama IP farklı
ve bir source'un agent_id bilgisi eksik
```

ise direkt merge etmeme kararı verdim.

---

# 🔑 Identity Mekanizması

Merge kararı:

```
hostname aynı
→ otomatik merge
```

değil.

Daha sağlam:

```
hostname
+
agent_id
+
cloud instance ID
+
serial
+
MAC
+
IP timeline
+
source lineage
```

gibi birden fazla identity sinyali.

---

# ⚠️ False Merge

İki gerçek asset'i:

```
tek asset
```

sanmak.

Security açısından ağır sonuç:

> Bir attack surface veya exposure ayrı asset olarak görünmeyebilir.

---

# ⚠️ False Split

Tek gerçek asset'i:

```
iki asset
```

sanmak.

Sonuç:

- duplicate kayıt
    
- operasyon maliyeti
    
- bakım/izlenebilirlik yükü
    

---

# 🎯 Kararım

Identity evidence zayıfsa:

```
false merge riskini almamak
↓
geçici false split'i kabul etmek
```

Kaynak trade-off'um da bunu söylüyor.

---

# 🧬 Source Lineage

Source lineage:

> Bir bilginin hangi kaynaktan, ne zaman ve hangi yöntemle geldiğinin izlenebilmesi.

Kaynaklar çelişirse:

```
Source A:
IP = X

Source B:
IP = Y
```

şu sorular önemli olur:

```
hangi source?
hangi timestamp?
hangi yöntem?
hangi confidence?
```

Kaynak cevabım source lineage'i bu güven problemiyle ilişkilendiriyor.

---

# 🔗 Gate 2'de Öğrendiğim Ortak Debugging Modeli

Bütün alanların ortak fikri:

```
SEMPTOM
↓
3 ayrı sahip katman ihtimali
↓
en küçük ayırıcı deney
↓
gerçek state'i ölç
↓
hipotezleri zayıflat/güçlendir
↓
root cause
```

Örneğin:

## Python

```
Output yanlış
↓
parser?
normalizer?
validator?
```

## Linux

```
PID var ama ilerlemiyor
↓
STOP?
blocking?
yanlış PID?
```

## Git

```
Yanlış dosya commit'e girecek
↓
Working Tree?
Index?
HEAD?
```

## Docker

```
Data görünmüyor
↓
wrong volume?
wrong mount path?
writable layer?
```

## CAASM

```
İki record aynı asset mi?
↓
hostname?
agent ID?
cloud ID?
timeline?
```

Kaynak kapalı oral kısmında da üç hipotezin amacının rastgele tahmin değil katmanları ayırmak olduğu özellikle belirtilmiş.

---

# 🧯 Hata Avı

## 1. `.gitignore` tracked dosyayı otomatik untrack eder

TIRT.

Tracked state ayrıca değiştirilmelidir.

---

## 2. `git diff` HEAD ile Working Tree'yi doğrudan kıyaslar

Eksik model.

Normal:

```
Working Tree ↔ Index
```

---

## 3. 100 input / 92 output → 8 kayıt kesin kayboldu

TIRT.

Rejection accounting kontrol edilmeden hüküm veremem.

---

## 4. Her hata fail-fast olmalı

TIRT.

Failure scope ve batch semantics karar verir.

---

## 5. Continue-on-error her durumda iyidir

TIRT.

Batch atomic ise veya bir record hatası bütün dataset güvenini bozuyorsa fail-fast gerekebilir.

---

## 6. Tasarladığım CSV parser şu anda Gate2 kodunda çalışıyor

Kaynak bunu desteklemiyor.

Şu an görünen live implementation JSON tarafında.

---

## 7. Tasarlanan `rejected.jsonl` şu anda yazılıyor

Kaynak live kod bunu yapmıyor.

Record reject'ler şu anda structured log olarak görülüyor.

---

## 8. SIGTERM graceful shutdown Gate2 pipeline'a entegre edildi

Kaynakta henüz bu entegrasyonu gösteren Gate2 kodu yok.

Signal çalışmaları ayrı process labında yapılıyor.

---

## 9. Normalizer yanlış tipleri temizleyip atmalı

TIRT.

Validator'ın görmesi gereken hatayı gizleyebilir.

---

## 10. JSON geçerliyse top-level shape de doğrudur

TIRT.

Valid JSON object ile expected batch list farklı şeylerdir.

---

## 11. PID var → process doğru uygulamadır

TIRT.

`comm/args` ile identity doğrulanmalı.

---

## 12. PID var ama output yok → process stopped

TIRT.

Sleeping/blocking de olabilir.

---

## 13. `S` ve `T` aynı bekleme durumudur

TIRT.

```
S
→ waiting/sleeping

T
→ externally stopped
```

---

## 14. Runtime artifact'i stage'den çıkarırsam file silinir

TIRT.

`git restore --staged` Index state'ini değiştirir, Working Tree file'ını koruyabilir.

---

## 15. Yeni container eski veriyi göremiyor → data silindi

TIRT.

Mount selection/path önce doğrulanmalı.

---

## 16. Aynı destination `/data` kullanılıyorsa storage da aynıdır

TIRT.

Aynı:

```
Destination=/data
```

farklı:

```
Source volume
```

ile tamamen farklı data gösterebilir.

---

## 17. Mount sonrası image file görünmüyor → image'dan silindi

TIRT.

Shadowing/obscuring olabilir.

---

## 18. Aynı hostname → aynı asset

TIRT.

Hostname tek başına immutable identity değildir.

---

# 🧠 Kafaya Kazı

> [!quote]  
> Parse formatı, normalize representation'ı, validation contract'ı yönetir.

> [!quote]  
> Tasarım ile gerçekten çalışan implementation'ı birbirine karıştırma.

> [!quote]  
> Normalizer validation evidence'ını kaybetmemeli.

> [!quote]  
> File-level parse failure ile record-level validation failure aynı scope değildir.

> [!quote]  
> Independent records varsa continue-on-error geçerli bir policy olabilir.

> [!quote]  
> Atomic batch gerekiyorsa aynı policy yanlış olabilir.

> [!quote]  
> JSON syntax valid olmak, expected top-level shape'in doğru olduğunu kanıtlamaz.

> [!quote]  
> PID identity için başlangıç kanıtıdır; command/state/parent hakkında ayrıca ölçüm gerekir.

> [!quote]  
> `ps` ile identity ve runtime state'i aynı anda kontrol edebilirim.

> [!quote]  
> Working Tree, Index ve HEAD ayrı snapshot/state'lerdir.

> [!quote]  
> `git restore --staged` Index'i değiştirip Working Tree'yi korumak için kullanılabilir.

> [!quote]  
> Docker persistence debugging'de önce `Source → Destination` mount mapping'ini ölç.

> [!quote]  
> Aynı container path, aynı backing storage anlamına gelmez.

> [!quote]  
> Mount alttaki image data'yı silmeden görünümünü gölgeleyebilir.

> [!quote]  
> CAASM correlation'da zayıf evidence ile merge etmek false merge riskini büyütür.

> [!quote]  
> Üç hipotezin amacı tahmin üretmek değil, farklı sahip katmanlarını deneyle ayırmaktır.

---

# 📌 30 Saniyelik Özet

```
GATE 2

INPUT
JSON
CSV [tasarımda]

↓
PARSER

↓
NORMALIZER

↓
VALIDATOR

↓
ACCEPT / REJECT


FAILURE POLICY

malformed file
→ file-level
→ fail-fast

invalid record
→ record-level
→ reject + continue


CURRENT IMPLEMENTATION

JSON parser ✅
normalizer ✅
validator ✅
output.jsonl ✅
structured rejection log ✅

CSV integration
→ henüz gösterilmedi

rejected.jsonl
→ tasarımda

SIGTERM integration
→ tasarım/lab aşamasında


LINUX

PID var ama ilerleme yok
↓
ps -p PID -o pid,ppid,stat,comm,args

T
→ stopped

S
→ sleeping/waiting


GIT

HEAD  = v1
INDEX = v2
WT    = v2

git diff
→ WT ↔ Index
→ boş

git diff --cached
→ HEAD ↔ Index
→ v1 → v2

restore --staged
→ Index'i değiştir
→ WT'yi koru


DOCKER

writer
coreops-data → /data

reader-ok
coreops-data → /data
→ data var

reader-bad
coreops-data-wrong → /data
→ data yok

ROOT CAUSE
→ wrong named volume


MOUNT

image /data/example.txt
+
empty bind → /data

→ file görünmez
≠ file silindi


CAASM

same hostname
≠ definite identity

weak evidence
→ conservative split

strong agent/cloud/serial evidence
→ merge kararı güçlenir
```

---

# ✅ Günün Kazanımları

- `.gitignore` ile tracked state arasındaki ayrım tekrar edildi
    
- Working Tree / Index / HEAD modeli pekiştirildi
    
- Input/output/rejection invariant yaklaşımı tekrar edildi
    
- Continue-on-error için gerekçe/trade-off/karşı koşul çıkarıldı
    
- Gate2 problem ve success criteria tanımlandı
    
- Current-record atomicity invariant'ı belirlendi
    
- Parser / normalizer / validator sorumlulukları ayrıldı
    
- JSON + CSV canonical pipeline tasarlandı
    
- Processing / shutdown / cleanup state modeli çıkarıldı
    
- Parse / normalize / validate failure sahipleri ayrıldı
    
- Uygulama teşhis sırası belirlendi
    
- SIGTERM entegrasyonundan önce normal data path'i doğrulama kararı verildi
    
- JSON parser implementasyonu test edildi
    
- Normalizer yanlış veriyi gizlemeyecek şekilde düzeltildi
    
- `tags` içindeki non-string değerleri validation'a taşıma düzeltmesi yapıldı
    
- Required field/type/range validation uygulandı
    
- `port=true` exact-type testi geçti
    
- Valid dataset 3/0 sonucu verdi
    
- Invalid record 1/1 sonucu verdi
    
- Malformed JSON file-level failure ve exit 47 üretti
    
- Fail-fast vs record continue-on-error ayrıldı
    
- Top-level JSON object/list contract hatası debugging ile bulundu
    
- `string indices must be integers` hatasının gerçek nedeni anlaşıldı
    
- Linux runtime incident üç hipoteze ayrıldı
    
- Exact PID + `ps` ile identity/state kontrolü yapıldı
    
- `S` ile `T` farkı tekrar deneyle görüldü
    
- `/proc/PID/status` ile STOP state doğrulandı
    
- `/proc/PID/cmdline` ile invocation incelendi
    
- `pstree` ile parent-child ilişkisi gözlemlendi
    
- Git live failure repository'si oluşturuldu
    
- `git diff` vs `git diff --cached` gerçek state üzerinden doğrulandı
    
- `git show HEAD:file` ile HEAD snapshot kontrol edildi
    
- Runtime artifact stage edilip geri çıkarıldı
    
- `git restore --staged` ile Index değiştirilirken Working Tree korundu
    
- Docker persistence incident üç storage hipotezine ayrıldı
    
- Named volume oluşturuldu
    
- Aynı volume ile writer/reader persistence doğrulandı
    
- Yanlış named volume ile failure kontrollü şekilde üretildi
    
- `docker inspect .Mounts` ile Source/Destination farkı kanıtlandı
    
- Volume bağımsız Alpine container ile kontrol edildi
    
- Gerçek root cause'un wrong named volume olduğu kanıtlandı
    
- Mount shadowing countercase tekrar üretildi
    
- “File görünmüyor = silindi” hükmü çürütüldü
    
- CAASM correlation kararında same-hostname'in yetersiz olduğu tekrarlandı
    
- False merge ve false split trade-off'u uygulandı
    
- Source lineage'in confidence kararındaki önemi tekrarlandı
    
- Agent ID / cloud ID / serial gibi daha güçlü identity evidence'ları seçildi
    
- Üç hipotez + en küçük ayırıcı deney debugging modeli farklı alanlarda tekrar kullanıldı
    

> [!success] 🚀 Gate 2'de geldiğim nokta  
> Bu çalışmanın en büyük kazanımı tek bir Python script yazmak değil.
> 
> Artık sistemi:
> 
> ```
> INPUT
> ↓
> PARSE
> ↓
> NORMALIZE
> ↓
> VALIDATE
> ↓
> PERSIST
> ↓
> RUNTIME
> ↓
> STORAGE
> ```
> 
> şeklinde katmanlara bölebiliyorum.
> 
> Bir hata geldiğinde de:
> 
> ```
> “Bir şey bozuk.”
> ```
> 
> demek yerine:
> 
> ```
> Bu semptomun 3 farklı sahip katmanı ne?
> ↓
> Bunları en ucuz hangi deney ayırır?
> ↓
> Gerçek state ne?
> ↓
> Hangi hipotez kaldı?
> ```
> 
> diye ilerliyorum.
> 
> Python'da:
> 
> ```
> parser / normalizer / validator
> ```
> 
> Linux'ta:
> 
> ```
> identity / runtime state
> ```
> 
> Git'te:
> 
> ```
> Working Tree / Index / HEAD
> ```
> 
> Docker'da:
> 
> ```
> image / writable layer / mount / volume
> ```
> 
> CAASM'da:
> 
> ```
> source record / identity evidence / correlation
> ```
> 
> aynı yöntemle ayrılıyor.
> 
> Günün en kritik cümlesi:
> 
> **Root cause tahmin edilmez; sahip katmanlar ayrılır, state ölçülür ve en küçük ayırıcı deneyle kanıtlanır.**