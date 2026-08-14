---
title: "Gün 21 — CAASM: Asset, Inventory, Attack Surface, Exposure ve Correlation"
tags:
  - coreops
  - caasm
  - asset-management
  - inventory
  - attack-surface
  - exposure
  - vulnerability
  - correlation
  - deduplication
  - identity
  - debugging
aliases:
  - "Gün 21 CAASM Asset Inventory Exposure Correlation"
status: completed
---

# 🛡️ Gün 21 — CAASM: Asset, Inventory, Attack Surface, Exposure ve Correlation

> [!abstract] 🎯 Ana fikir  
> Bugün CAASM tarafında en önemli öğrendiğim şey kavramları birbirine yapıştırmamak oldu:
> 
> ```
> Asset
> ≠
> Inventory Entry
> ≠
> Attack Surface
> ≠
> Exposure
> ≠
> Vulnerability
> ```
> 
> CAASM'ın asıl problemi yalnızca:
> 
> ```
> “Kaç kayıt var?”
> ```
> 
> değildir.
> 
> Daha doğru soru:
> 
> ```
> “Bu farklı kaynaklardaki kayıtlar
> hangi gerçek asset'leri temsil ediyor?”
> ```
> 
> Sonra:
> 
> ```
> Bu asset nereden görünüyor?
> ↓
> Hangi attack surface noktaları var?
> ↓
> Exposure sinyali var mı?
> ↓
> Vulnerability var mı?
> ↓
> Hangi bilgi hangi kaynaktan geldi?
> ```

---

# ⚡ D+1 Geri Çağırma — Önceki Günün Kritik Düzeltmeleri

## `.gitignore` eşleşiyor ama dosya hâlâ tracked olabilir mi?

Evet.

Buradaki daha doğru sebep:

```
Dosya daha önce Git index/history'ye alınmış
↓
Git onu artık tracked olarak biliyor
↓
Sonradan .gitignore'a yazmak
tracked durumunu otomatik kaldırmaz
```

Yani mesele yalnızca:

```
“eski commit duruyor”
```

değil.

Asıl kavram:

> **Ignore policy, mevcut tracked state'i otomatik değiştirmez.**

---

## `git diff` ve `git diff --staged`

```
git diff
→ Index ↔ Working Tree

git diff --staged
→ HEAD ↔ Index
```

Bu kısım doğru hatırlanmış.

---

# 🧠 Git State Modelini Temiz Çiz

Başlangıç:

```
HEAD          INDEX          WORKING TREE
 A              A                 A
```

Working Tree değiştirilirse:

```
HEAD          INDEX          WORKING TREE
 A              A                 B
```

Burada:

```
git diff
→ A ↔ B
```

Sonra:

```
git add dosya
```

yaparsam:

```
HEAD          INDEX          WORKING TREE
 A              B                 B
```

Burada:

```
git diff --staged
→ A ↔ B
```

Commit sonrası:

```
HEAD          INDEX          WORKING TREE
 B              B                 B
```

---

# 🔢 100 Input → 92 Output

Direkt:

```
8 kayıt kayboldu
```

diyemem.

Önce:

```
Input count
Output count
Rejected count
Final summary
```

ölçülmeli.

Örneğin:

```
Input     = 100
Accepted  = 92
Rejected  = 8
```

ve:

```
92 + 8 = 100
```

ise bu **controlled rejection** ile açıklanabilir.

---

# 🛡️ CAASM Nedir?

**CAASM = Cyber Asset Attack Surface Management**

CAASM farklı IT ve security kaynaklarından gelen asset bilgilerini bir araya getirip organizasyonun daha birleşik ve güvenilir bir asset görünümünü oluşturmaya çalışır.

Örneğin kaynaklar:

```
CMDB
AWS / Azure
EDR
Vulnerability Scanner
Intune
Active Directory
Cloud Inventory
```

Kabaca:

```
Kaynaklar
↓
Normalize
↓
Correlate
↓
Deduplicate
↓
Unified Asset View
```

Kaynak notta bu model farklı sistemlerdeki kayıtları gerçek asset görünümüne bağlama problemi olarak kurulmuş.

---

# 🖥️ Asset Nedir?

**Asset**, gerçekten var olan ve organizasyon açısından takip edilmesi veya korunması gereken varlıktır.

Örneğin:

- Sunucu
    
- Laptop
    
- VM
    
- EC2 instance
    
- Database
    
- API
    
- Cloud resource
    
- Service account
    

Kritik:

```
Asset
→ gerçek dünyadaki varlık

Inventory entry
→ o varlık hakkındaki kayıt
```

> [!danger] TIRT  
> Database satırını doğrudan asset'in kendisi sanmak.

---

# 📚 Inventory Nedir?

Inventory:

> Asset'ler hakkında sistemlerde tuttuğumuz kayıtların bütünüdür.

Örnek:

```
web01
10.0.0.5
Ubuntu
Backend Team
```

Bu gerçek sunucu değil.

Sunucu hakkında tutulan bilgidir.

Inventory:

```
eski olabilir
eksik olabilir
yanlış olabilir
duplicate olabilir
stale olabilir
```

Dolayısıyla:

> **Asset ≠ Inventory Entry**

Kaynak çalışmada bu temel ayrım doğru kurulmuş.

---

# 🔄 Bir Asset'in Birden Fazla Kaydı Olabilir

Örneğin aynı gerçek makine:

```
CMDB
→ web01 / 10.0.0.5

EDR
→ web01 / agent-774

AWS
→ i-123 / web01 / 10.0.0.5
```

şeklinde üç farklı kayıtta bulunabilir.

Dolayısıyla:

```
3 record
≠
3 asset
```

---

# 🧩 Asset Correlation

CAASM'ın kritik problemlerinden biri:

> Hangi kayıtlar aynı gerçek asset'i temsil ediyor?

Bunun için sinyaller:

- Hostname
    
- IP
    
- MAC
    
- Serial number
    
- Cloud resource ID
    
- Agent ID
    
- Account
    
- Region
    
- Timestamp/context
    

gibi alanlar birlikte değerlendirilebilir.

---

# ⚠️ Hostname Tek Başına Identity Değildir

Örneğin:

```
Bugün:
web01 → VM-A

Yarın:
VM-A silindi

Yeni:
web01 → VM-B
```

Hostname aynı.

Gerçek asset farklı.

Dolayısıyla:

```
hostname aynı
→ correlation sinyali ✅

hostname aynı
→ kesin aynı asset ❌
```

---

# 🌐 Attack Surface

Attack surface:

> Saldırganın sistemle etkileşim kurabileceği toplam yüzey.

Örneğin:

- Public web server
    
- SSH service
    
- API endpoint
    
- Login panel
    
- Açık servisler
    
- Internet-facing cloud resource
    
- DNS/domain
    

Kaynak notta da attack surface'in yalnız vulnerable sistemlerden oluşmadığı doğru şekilde ayrılmış.

---

# 🚨 Vulnerability Olmadan Attack Surface Olabilir

Örneğin:

```
Internet
↓
443
↓
Tam güncel HTTPS server
```

Bilinen CVE olmayabilir.

Ama saldırgan:

```
443 endpoint'iyle etkileşebiliyor
```

Dolayısıyla hâlâ attack surface'in parçası.

> [!important]  
> Attack surface'in varlığı için vulnerability şart değildir.

---

# 🚪 Exposure

Exposure:

> Bir asset'in veya servisinin saldırgana ulaşılabilir olmasına ya da saldırı yoluna açık hâle gelmesine neden olan durum.

Örnek sinyaller:

- Public IP
    
- Public service
    
- `0.0.0.0/0` network rule
    
- Public admin panel
    
- Public bucket
    
- Aşırı geniş IAM yetkisi
    
- Internet reachability
    

Örneğin:

```
Internal Network
↓
PostgreSQL:5432
```

ile:

```
Internet
↓
Public IP:5432
↓
PostgreSQL
```

aynı exposure değildir.

---

# ⚠️ Önemli Düzeltme — Exposure İçin Vulnerability Şart Değil

İlk araştırma cevabında şu mantığa yaklaşılmış:

```
Exposed olması için
dışarıdan erişilebilir
+
vulnerability
```

Bu fazla dar.

Daha doğru:

```
Exposure
→ ulaşılabilirlik / saldırıya açık konum

Vulnerability
→ içerideki zayıflık
```

Dolayısıyla:

```
Vulnerability ❌
Exposure ✅
```

gayet mümkündür.

Nitekim notun ilerleyen kısmında bu model doğru şekilde kurulmuş.

---

# 🐛 Vulnerability

Vulnerability:

> Sistemde bulunan exploit edilebilir zayıflık.

Örneğin:

```
Eski yazılım
↓
Bilinen CVE
↓
Exploit edilebilir zayıflık
```

Ama:

```
Vulnerability var
```

demek:

```
Internet'ten erişilebilir
```

demek değildir.

---

# ⚠️ Bir Başka Küçük Düzeltme

Sözlü cevapta vulnerability örneği olarak:

```
“açık bırakılmış port”
```

denmiş.

Portun açık olması tek başına vulnerability değildir.

Daha doğru ayrım:

```
Açık/reachable port
→ attack surface / exposure sinyali

Portun arkasındaki vulnerable service
→ vulnerability
```

Örneğin:

```
443 açık
→ vulnerability demek değil

443'te vulnerable nginx sürümü
→ vulnerability olabilir
```

---

# 🧠 Exposure / Vulnerability Matrisi

|Vulnerability|Exposure|Yorum|
|---|---|---|
|❌|❌|Kapalı/güncel sistem olabilir|
|❌|✅|Güncel fakat internete açık servis|
|✅|❌|Vulnerable fakat dışarıdan ulaşılamayan servis|
|✅|✅|Risk açısından çok önemli kombinasyon|

---

# 🔥 En Kritik Ayrım

```
CVE
→ Vulnerability

Public IP / Reachability
→ Exposure

Internet-facing endpoint
→ Attack Surface
```

Bunları birbirine dönüştürme.

---

# 🏛️ CMDB

**CMDB = Configuration Management Database**

IT ortamındaki configuration item'lar ve ilişkileri hakkında kayıt tutan sistemdir.

Örnek:

```
server01
10.0.0.8
Ubuntu
Production
IT
```

Ama CMDB:

```
mutlak gerçeklik
```

değildir.

Kayıt:

- stale
    
- eksik
    
- duplicate
    
- yanlış
    

olabilir.

---

# 🔄 CMDB vs CAASM

```
CMDB
→ Asset/configuration kayıtlarını tutan kaynaklardan biri

CAASM
→ CMDB dahil birçok kaynağı birleştirir
```

Örneğin:

```
CMDB
+
AWS
+
Nessus
+
CrowdStrike
↓
CAASM
↓
Unified Asset View
```

Kaynak notta bu fark ve CAASM'ın sorduğu kontrol/vulnerability/internet-facing soruları açıkça ayrılmış.

---

# 🏛️ NIST

Kafadaki kısa model:

```
NIST
→ standart / framework / rehber üreten kurum
```

CAASM ürünü veya inventory sistemi değildir.

---

# 🧪 Acme Mini Lab

Labda üç farklı veri kaynağı:

```
CMDB
Cloud Inventory
Vulnerability Scanner
```

kullanılmış.

Veri:

```
CMDB
A-101 → api-01
A-102 → db-01

Cloud
i-aaa → api-01
i-bbb → worker-01

Vulnerability Scanner
api-01 → CVE-LAB-001
db-01  → CVE-LAB-002
```

Kaynak labın başlangıç görünümü bu şekilde verilmiş.

---

# 1️⃣ Asset Adayları

Çıkardığım gerçek varlık adayları:

```
api-01
db-01
worker-01
```

Buna karşı:

```
A-101
A-102
i-aaa
i-bbb
```

source-system record/resource ID'leri.

---

# 🧠 Asset vs Record ID

```
A-101
→ CMDB record

api-01
→ gerçek asset'i temsil eden hostname
```

ve:

```
i-aaa
→ Cloud Inventory record ID

api-01
→ asset adayı
```

> [!danger]  
> Exposure bulunan asset sorulurken `i-aaa` demek yerine `api-01` demem gerekir.

---

# 2️⃣ Yalnız Inventory Bilgisi Taşıyan Kayıtlar

```
A-101
A-102
i-bbb
```

yalnız inventory bilgisi taşıyor şeklinde değerlendirilebilir.

`i-aaa` ise:

```
inventory
+
public_ip
+
service_port
```

taşıdığı için attack surface/exposure hakkında da sinyal veriyor.

Kaynak labda özellikle **“yalnız inventory”** kelimesinin ayrımı bu şekilde yapılmış.

---

# `null` Görünce Yaptığım Hata

`i-bbb`:

```
public_ip = null
service_port = null
```

gösteriyor.

İlk çıkarım:

```
Asset silinmiş olabilir.
```

Bu desteklenmiyor.

`null` burada yalnız:

```
Bu alan için değer yok /
bilinmiyor /
atanmamış
```

demektir.

Tek başına:

```
deleted
terminated
inactive
stale
```

kanıtı değildir.

Kaynak notta bu varsayım özellikle düzeltilmiş.

---

> [!important]  
> **Verinin söylemediği şeyi tamamlayıp gerçekmiş gibi kabul etme.**

---

# 3️⃣ Attack Surface Bilgisi Hangi Kayıtta?

`i-aaa`:

```
public_ip: 203.0.113.10
service_port: 443
```

taşıyor.

Bu yüzden:

```
i-aaa
→ attack surface hakkında bilgi taşıyor
```

demek mantıklı.

Ama:

```
Kesin internetten erişilebilir
```

hükmü için:

- Firewall
    
- ACL
    
- Routing
    
- Reachability
    

gibi bilgiler eksik olabilir.

Daha sağlam ifade:

> **Dışarıdan erişilebilirliğe dair güçlü sinyal var.**

---

# 4️⃣ Hangi Asset'te Exposure İhtimali Var?

Record:

```
i-aaa
```

Asset:

```
api-01
```

Kanıt:

```
Public IP
+
443 service port
```

Dolayısıyla:

> `**api-01**` **için exposure ihtimali vardır.**

---

# 💥 Buradaki İlk Hata — CVE'yi Exposure'a Bağlamak

Yanlış:

```
CVE var
↓
Exposure var
```

Doğru:

```
CVE
→ Vulnerability

Public IP / Reachability
→ Exposure
```

Kaynak çalışmada bu bağlantı açık biçimde düzeltilmiş.

---

# 5️⃣ Vulnerability Bulunan Asset'ler

Scanner:

```
api-01
→ CVE-LAB-001
→ high

db-01
→ CVE-LAB-002
→ critical
```

Dolayısıyla:

```
api-01 ✅
db-01 ✅
```

vulnerability bilgisine sahip.

`high` ve `critical` burada:

```
Vulnerability severity
```

bilgisidir.

---

# 🚨 Severity ≠ Exposure

```
Critical vulnerability
```

şu anlama gelmez:

```
Critical exposure
```

veya:

```
Internet-facing
```

Bunlar farklı özelliklerdir.

---

# 6️⃣ `db-01` Critical → Internet Exposed mı?

Hayır, mevcut dataset'ten bunu söyleyemem.

Elimizde:

```
critical CVE ✅

public IP ?
external port ?
routing ?
firewall ?
reachability ?
```

yok.

Bu yüzden en sağlam cümle:

> **Mevcut veride** `**db-01**`**'in internet-exposed olduğunu kanıtlayan bilgi bulunmuyor.**

Kaynak notta da “internete açık değil” ile “internete açık olduğuna dair kanıt yok” ayrımı özellikle düzeltilmiş.

---

# 🧠 Kanıt Yokluğu ≠ Yokluğun Kanıtı

```
Public IP bilgisi yok
```

demek:

```
Kesin public IP'si yok
```

demek değildir.

Dataset:

```
Eksik olabilir.
```

Bu CAASM'da çok önemli çünkü zaten farklı kaynaklardaki eksik/çelişkili bilgileri uzlaştırmaya çalışıyoruz.

---

# 🧩 Asset Görünümü Oluşturma — Merge mi Split mi?

İki kayıt:

```
A-101 → api-01
i-aaa → api-01
```

Hostname aynı.

Ama başka güçlü identifier yok.

Kararım:

> Şimdilik ayrı tut.

Gerekçe:

```
Tek ortak sinyal = hostname
```

ve hostname immutable unique ID değil.

Kaynak kararında da kayıtlar ayrı tutulmuş ve ek identifier ihtiyacı belirtilmiş.

---

# ⚖️ Correlation Trade-off

## False Merge

Gerçekte farklı iki asset'i:

```
tek asset
```

sanmak.

Risk:

```
Asset A
+
Asset B
↓
yanlış birleşme
```

---

## False Split

Gerçekte aynı asset'in iki kaydını:

```
iki farklı asset
```

sanmak.

Risk:

```
Tek asset
↓
2 asset gibi görünür
```

---

# 🎯 Benim Tercihim

Yetersiz identity sinyalinde:

```
merge etmeyerek
false merge riskini azaltıyorum
```

ama karşılığında:

```
false split ihtimalini
kabul ediyorum
```

Bu bilinçli bir trade-off.

---

# 🔑 Daha Güçlü Identity Sinyalleri

Doğrulama için:

- Agent ID
    
- Cloud resource ID
    
- Serial
    
- MAC
    
- Account/region
    
- IP + zaman
    
- Instance metadata
    

gibi daha güçlü sinyaller aranabilir.

---

# 🧪 Failure Vaka A — Yalnız Hostname ile Dedup

İki kayıt:

```
hostname aynı
cloud account farklı
```

ise direkt merge etmem.

Çünkü account farkı:

```
farklı asset ihtimalini
```

artırır.

Ek kimlik sinyali isterim.

---

# 🧪 Failure Vaka B — Critical Vulnerability vs Critical Exposure

Aynı şey değiller.

```
Critical vulnerability
→ zayıflığın severity'si

Exposure
→ ulaşılabilirlik / saldırı yüzeyindeki durum
```

Aynı hükme çevrilemez.

---

# 🧪 Failure Vaka C — Vulnerability Yoksa Attack Surface Dışı mı?

Hayır.

```
Internet-facing güncel API
```

attack surface olabilir.

Bilinen CVE:

```
0
```

olabilir.

---

# 🐞 Ayırıcı Debugging — “6 Kayıt = 6 Asset” Hatası

Semptom:

```
3 kaynak
↓
toplam 6 inventory record
↓
“6 asset var”
```

sonucu çıkarılmış.

Bu yanlış olabilir.

Kaynak debugging bölümünde üç ayrı hipotez kurulmuş.

---

# Hipotez 1 — Deduplication

```
Aynı gerçek asset'e ait kayıtlar
birleştirilmedi.
```

Sonuç:

```
false split
```

Katman:

```
deduplication
```

---

# Hipotez 2 — Identity Confidence

Sistem:

```
aynı asset olduklarından
yeterince emin olmadığı için
merge etmedi.
```

Katman:

```
identity / correlation
```

---

# Hipotez 3 — Missing Data

Correlation için gereken:

```
agent ID
cloud ID
MAC
serial
```

gibi bilgiler source'larda eksik.

Katman:

```
data completeness
```

---

# 🔬 En Küçük Deney

Aynı hostname'li kayıtları seç:

```
api-01
api-01
```

sonra:

```
agent ID?
cloud resource ID?
MAC?
serial?
account?
timestamp?
```

gibi ortak güçlü identifier'ları karşılaştır.

Bu deney:

```
“sistem neden merge etmedi?”
```

sorusunu doğrudan identity/correlation katmanında test eder.

---

# 🧬 Source Lineage

CAASM'da önemli bir başka kavram:

> **Bu bilgi nereden geldi?**

Örneğin asset:

```
api-01
```

için:

```
hostname
→ CMDB

public_ip
→ Cloud Inventory

CVE
→ Vulnerability Scanner

agent status
→ EDR
```

gibi farklı kaynaklar olabilir.

---

# Neden Source Lineage Önemli?

Çünkü iki kaynak çelişebilir:

```
CMDB:
owner = Team A

Cloud:
owner = Team B
```

Bu durumda:

```
Hangi bilgi?
Hangi kaynaktan?
Ne zaman?
Ne kadar güvenilir?
```

sorularını cevaplamak gerekir.

Sözlü turdaki “bilginin nereden, nasıl geldiğini takip etmek” cevabı doğru yönde.

---

# 🧯 Hata Avı

## 1. Asset = inventory satırı

TIRT.

Asset gerçek varlık, inventory onun kaydı.

---

## 2. 1000 + 900 + 500 record = 2400 asset

TIRT.

Aynı asset farklı kaynaklarda tekrar bulunabilir.

---

## 3. Aynı hostname = kesin aynı asset

TIRT.

Hostname değiştirilebilir ve tekrar kullanılabilir.

---

## 4. Vulnerability bulunan her asset exposed'dur

TIRT.

Vulnerable ama unreachable olabilir.

---

## 5. Exposure olması için vulnerability gerekir

TIRT.

Güncel ama public servis de exposed olabilir.

---

## 6. Vulnerability yoksa attack surface yoktur

TIRT.

Attack surface, interaction surface kavramıdır.

---

## 7. Açık port tek başına vulnerability'dir

TIRT.

Açık/reachable port attack surface veya exposure sinyali olabilir.

---

## 8. `public_ip=null` → asset silinmiş

TIRT.

Yalnız ilgili alan için veri yok.

---

## 9. CVE exposure kanıtıdır

TIRT.

CVE vulnerability kanıtıdır.

---

## 10. `i-aaa` exposure bulunan asset'tir

TIRT.

`i-aaa` inventory record ID.

Asset:

```
api-01
```

---

## 11. Critical CVE → internet exposed

TIRT.

Severity ile reachability farklı eksenler.

---

## 12. Public IP bilgisi yok → kesin internete kapalı

TIRT.

Mevcut dataset exposure'ı kanıtlamıyor diyebiliriz.

---

## 13. Correlation'da false merge tek risktir

TIRT.

False split de ciddi bir hatadır.

---

## 14. CAASM yalnız asset listeler

TIRT.

Asıl değer:

```
correlation
deduplication
coverage
exposure
vulnerability
control gaps
source lineage
```

gibi bilgileri unified asset view üzerinde birleştirmektir.

---

# 🧠 Kafaya Kazı

> [!quote]  
> Asset gerçek şeydir; inventory onun hakkındaki kayıttır.

> [!quote]  
> Record sayısı asset sayısı değildir.

> [!quote]  
> Aynı hostname güçlü bir sinyal olabilir ama identity garantisi değildir.

> [!quote]  
> Attack surface saldırganın etkileşebileceği yüzeydir.

> [!quote]  
> Exposure ulaşılabilirlik veya saldırı yoluna açıklıkla ilgilidir.

> [!quote]  
> Vulnerability sistemin içindeki zayıflıktır.

> [!quote]  
> CVE → vulnerability; public reachability → exposure.

> [!quote]  
> Vulnerability olmadan exposure olabilir.

> [!quote]  
> Exposure olmadan vulnerability olabilir.

> [!quote]  
> Attack surface'te olmak vulnerability gerektirmez.

> [!quote]  
> `null`, alanın bilinmediğini gösterebilir; asset'in silindiğini değil.

> [!quote]  
> Kanıt yokluğu, yokluğun kanıtı değildir.

> [!quote]  
> False merge ve false split correlation'ın iki farklı riskidir.

> [!quote]  
> Güçlü identity birden fazla sinyalden kurulmalıdır.

> [!quote]  
> Source lineage, unified kayıttaki her bilginin nereden geldiğini izlemeyi sağlar.

---

# 📌 30 Saniyelik Özet

```
CAASM
→ farklı kaynakları birleştir
→ correlate
→ deduplicate
→ unified asset view

ASSET
→ gerçek varlık

INVENTORY
→ asset hakkındaki kayıt

ATTACK SURFACE
→ saldırgan nerede etkileşebilir?

EXPOSURE
→ saldırganın ulaşabilmesini/
  saldırı yoluna girmesini sağlayan durum

VULNERABILITY
→ sistemdeki zayıflık

CVE
→ vulnerability

PUBLIC IP / SERVICE / REACHABILITY
→ exposure sinyali

IDENTITY
hostname tek başına yetmez

Daha güçlü:
agent ID
cloud ID
serial
MAC
account/region
timestamp

CORRELATION RİSKLERİ
false merge
→ iki asset'i bir sanmak

false split
→ bir asset'i iki sanmak

LAB
asset:
api-01
db-01
worker-01

inventory IDs:
A-101
A-102
i-aaa
i-bbb

attack surface sinyali:
i-aaa

exposure adayı:
api-01

vulnerability:
api-01
db-01

db-01 critical CVE
≠
internet exposure kanıtı
```

---

# ✅ Günün Kazanımları

- Asset ile inventory entry kesin olarak ayrıldı
    
- Record sayısı ile gerçek asset sayısının aynı olmadığı öğrenildi
    
- CAASM'ın correlation/deduplication problemi anlaşıldı
    
- CMDB ile CAASM farkı netleşti
    
- Attack surface ile vulnerability ayrıldı
    
- Exposure ile vulnerability ayrıldı
    
- Vulnerability olmadan exposure olabileceği düzeltildi
    
- Vulnerable fakat internet-exposed olmayan asset senaryosu öğrenildi
    
- Açık portun tek başına vulnerability olmadığı netleştirildi
    
- Hostname'in kesin identity key olmadığı öğrenildi
    
- MAC / agent ID / cloud ID / serial gibi güçlü correlation sinyalleri öğrenildi
    
- `null` değerlerden aşırı çıkarım yapmama prensibi pekiştirildi
    
- Record ID ile gerçek asset ayrıldı
    
- CVE'nin exposure değil vulnerability kanıtı olduğu oturdu
    
- Public IP + servis bilgisinin exposure sinyali olduğu görüldü
    
- Severity ile exposure'ın farklı eksenler olduğu öğrenildi
    
- “İnternete kapalı” ile “internet exposure kanıtım yok” ayrıldı
    
- Kanıt yokluğu ≠ yokluğun kanıtı modeli pekiştirildi
    
- False merge ve false split trade-off'u öğrenildi
    
- Yetersiz identity durumunda conservative split yaklaşımı uygulandı
    
- “6 record → 6 asset” hatası için katmanlı debugging hipotezleri kuruldu
    
- Dedup, identity ve missing-data katmanları ayrıldı
    
- En küçük correlation deneyi tasarlandı
    
- Source lineage kavramı öğrenildi
    
- Git D+1 retrieval'daki `.gitignore` tracked-state yanılgısı düzeltildi
    
- Controlled rejection için input = accepted + rejected kanıt modeli tekrar edildi
    

> [!success] 🚀 Gün sonu sonucu  
> Günün başında CAASM kavramları ayrı tanımlar gibi görünüyordu.
> 
> Gün sonunda hepsi tek bir karar zincirine oturdu:
> 
> ```
> SOURCE RECORDS
> ↓
> Bu kayıt hangi gerçek asset'e ait?
> ↓
> Correlate / Deduplicate
> ↓
> UNIFIED ASSET
> ↓
> Attack surface bilgisi var mı?
> ↓
> Exposure sinyali var mı?
> ↓
> Vulnerability var mı?
> ↓
> Bilginin kaynağı ne?
> ```
> 
> Artık yeni bir CAASM kaydı gördüğümde:
> 
> ```
> “Bu nedir?”
> ```
> 
> demek yerine şu sırayla düşünmeliyim:
> 
> ```
> 1. Asset hangisi?
> 2. Record hangisi?
> 3. Identity ne kadar güçlü?
> 4. Merge edersem false merge riski?
> 5. Split edersem false split riski?
> 6. Attack surface sinyali var mı?
> 7. Exposure kanıtı var mı?
> 8. Vulnerability kanıtı var mı?
> 9. Bu bilgi hangi source'tan geldi?
> ```
> 
> Günün en kritik cümlesi:
> 
> **CAASM'ın özü asset saymak değil; farklı kaynakların aynı gerçek dünya hakkında verdiği eksik, tekrar eden ve bazen çelişkili kayıtları güvenilir bir asset kimliğine bağlayıp saldırı yüzeyi bağlamında anlamlandırmaktır.**