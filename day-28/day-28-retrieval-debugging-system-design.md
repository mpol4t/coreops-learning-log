---
title: "Gün 28 — Retrieval, Problem Decomposition, Debugging ve System Design"
tags:
  - coreops
  - day28
  - retrieval
  - debugging
  - decomposition
  - python
  - linux
  - git
  - docker
  - storage
  - caasm
  - source-lineage
  - system-design
aliases:
  - "Gün 28 Retrieval Debugging ve System Design"
status: completed
---

# 🧠 Gün 28 — Retrieval, Problem Decomposition, Debugging ve System Design

> [!abstract] 🎯 Ana fikir
> Bugün tek tek Python, Linux, Git, Docker veya CAASM çalışmaktan çok hepsinde ortak olan bir beceriye odaklandım:
>
> **Bir problem geldiğinde direkt çözüm sallamak yerine problemi doğru katmanlara ayırmak.**
>
> Genel model:
>
> Semptom  
> -> Olası sahip katmanlar  
> -> Hipotezler  
> -> Ölçmek istediğim state  
> -> En küçük ayırıcı deney  
> -> Kanıt  
> -> Teknik hüküm

---

# ⚡ D+7 Retrieval

## Dependency declaration != installed environment

`pyproject.toml` içinde dependency yazması:

**"Bu projede bu pakete ihtiyaç var."**

demektir.

Ama:

**"Bu paket şu anda gerçekten kurulu."**

demek değildir.

Örneğin:

    declared dependency ✅
    installed package ❌
    runtime import ❌
    -> ModuleNotFoundError

Kısacası:

> **declared != installed != runtime-visible**

---

## Process debugging

Bir process'i kontrol ederken:

`ps -p PID -o pid,ppid,stat,comm,args`

ile aynı anda şunlara bakabilirim:

- PID gerçekten hâlâ var mı?
- PPID ne?
- STAT ne?
- Beklediğim program mı?
- Hangi argümanlarla çalışıyor?

Önemli:

> **PID'nin var olması uygulamanın sağlıklı şekilde iş yaptığı anlamına gelmez.**

Process `S`, `T` gibi farklı state'lerde olabilir veya bir yerde block olmuş olabilir.

---

## Docker tarafındaki eksiğim

Retrieval sırasında son birkaç gündeki Docker konularında eksiğim olduğunu fark ettim.

Tekrar etmem gereken başlıklar:

- container writable layer
- named volume
- bind mount
- persistence
- cache invalidation

Bu zaten retrieval'ın işe yaradığı nokta:

> **Sadece ne bildiğimi değil, nerede boşluk kaldığını da gösteriyor.**

---

## Graceful shutdown

SIGTERM gelmesine rağmen graceful shutdown başarısız olabilir.

Olası sebepler:

- handler yoktur
- handler yanlış çalışıyordur
- cleanup mantığı bozuktur
- uygulama child process'tir
- signal doğru process'e ulaşmıyordur
- uygulama shutdown sırasında takılıyordur

Kısa model:

    SIGTERM
    -> shutdown isteği

    Graceful shutdown
    -> uygulamanın bu isteğe verdiği kontrollü tepki

Yani SIGTERM graceful shutdown'ın kendisi değildir.

---

## `.gitignore`

Bir dosya daha önce commit edilip tracked olmuşsa:

    dosyayı .gitignore'a eklemek
    !=
    tracking'i kaldırmak

Dosya hâlâ:

- Index'te
- HEAD'de
- eski history'de

bulunabilir.

`.gitignore`ın çalışmasını istiyorsam önce tracked state'i ayrıca değiştirmem gerekir.

---

## Vulnerability != Exposure

Bir asset'te vulnerability bulunması:

**"Bu asset saldırgana açıktır."**

anlamına gelmez.

Ayrıca:

- reachability
- attack surface
- public exposure

gibi bilgiler de gerekir.

Örneğin:

    critical CVE ✅
    internet exposure ?

Buradan direkt:

    internet exposed ✅

sonucu çıkaramam.

---

# 🧩 Decomposition Drill — +450 Asset Nereden Geldi?

Problem:

    Dün canonical inventory = 1420
    Bugün canonical inventory = 1870

    Fark = +450

İlk bakışta:

**"450 yeni asset geldi."**

demek kolay.

Ama bunu henüz kanıtlamadım.

Asıl sorum:

> **Bu +450 gerçekten yeni gerçek asset mi, yoksa source / identity / dedup / state davranışlarından biri mi değişti?**

---

# 🧱 Problemi Katmanlara Ayırdım

1. Source
2. Identity
3. Dedup
4. State

Önemli:

> **Asset sayısının artması root cause değildir. Sadece semptomdur.**

---

# H1 — Source

A ve B source'ları gerçekten farklı asset'ler mi getiriyor?

Yoksa:

    Source A -> Asset X
    Source B -> Asset X

gibi overlap mı var?

Çünkü:

    2 source record
    !=
    2 gerçek asset

---

# H2 — Identity

Identity algoritmasının davranışı değişmiş olabilir.

Örneğin dün:

    Record A + Record B
    -> aynı asset

denirken bugün:

    Record A -> Asset 1
    Record B -> Asset 2

deniyor olabilir.

Bu durumda gerçek dünyada yeni asset gelmeden canonical asset sayısı artabilir.

---

# H3 — Dedup

Aynı gerçek asset iki source'ta bulunuyor olabilir.

Normalde:

    Source A record
    +
    Source B record
    -> tek canonical asset

olması gerekirken dedup bozulduysa:

    Source A record -> Asset 1
    Source B record -> Asset 2

şeklinde sayım şişebilir.

---

# 🔬 İlk Ayırıcı Deney

Bugünkü +450 asset adayını dünkü canonical inventory ile karşılaştırırım.

Soracağım şey:

> **Bu 450 kaydın gerçekten kaçı dün bulunan hiçbir canonical asset ile eşleşmiyor?**

Eğer büyük kısmı eski kayıtlarla eşleşiyorsa:

    +450
    !=
    450 gerçek yeni asset

demektir.

---

# ⚠️ Belirsiz Varsayımlar

Şu anda şunların aynı kaldığını bilmiyorum:

- source kapsamı
- identity algoritması
- dedup politikası
- input kalitesi
- source sayısı

Özellikle:

> **Dün ve bugün aynı source kapsamının kullanıldığını varsaymak kanıtlanmış değil.**

---

# 🧬 Source Lineage

Örnek evidence:

## Source A

    Value: 10.0.0.17
    Source: CMDB
    Observed at: 10:00
    Collection method: unknown
    Source identifier: unknown
    Confidence: henüz belirlenemez

## Source B

    Value: 10.0.0.44
    Source: Cloud Inventory
    Observed at: 10:03
    Collection method: unknown
    Source identifier: i-abc123
    Confidence: henüz belirlenemez

## Source C

    Value: 10.0.0.17
    Source: Scanner
    Observed at: 08:20
    Collection method: unknown
    Source identifier: unknown
    Confidence: henüz belirlenemez

---

# 🔥 Bilmediğim Şeyi Uydurmamak

Buradaki önemli ders:

    collection_method bilmiyorum
    -> unknown

    source_identifier bilmiyorum
    -> unknown

    confidence için kanıtım yok
    -> henüz belirlenemez

> [!important]
> **Eksik evidence'ı kafadan doldurmak yerine unknown bırakmak daha doğru.**

---

# 🗳️ Çoğunluk Her Zaman Truth Değil

İki source aynı IP'yi söylüyor diye:

**"Bu kesin doğru IP."**

diyemem.

Çünkü:

    oy sayısı
    !=
    bağımsız ve kaliteli evidence sayısı

Ayrıca:

    yeni timestamp
    !=
    doğruluk garantisi

ve:

    source authority
    -> field'e göre değişebilir

---

# ⏱️ Temporal Evidence

Timestamp önemlidir.

Ama tek başına karar verdirmez.

Örneğin:

    Source A -> 10:00
    Source B -> 10:03

B daha güncel.

Ama:

    B kesin doğru

diyemem.

Eğer iki source benzer güvenilirlikteyse daha yeni observation'a daha fazla ağırlık verebilirim.

---

# 🏛️ Source Authority

Her source her field için eşit derecede güvenilir olmayabilir.

Örneğin:

    owner bilgisi
    -> CMDB daha anlamlı olabilir

    güncel cloud IP
    -> Cloud Inventory daha anlamlı olabilir

Yani soru:

**"En güvenilir source hangisi?"**

değil.

Daha doğru soru:

> **"Bu field için hangi source daha authoritative?"**

---

# ⚠️ Conflict Bırakmak

İki güçlü source farklı value veriyorsa ve hangisinin doğru olduğunu ayıramıyorsam:

    birini kafama göre seçmek ❌

yerine:

    conflict / unknown ✅

bırakabilirim.

Canonical sistemin her durumda zorla cevap üretmesi gerekmiyor.

---

# False Merge

Gerçekte:

    Asset A
    Asset B

var.

Ama sistem:

    Asset AB

diyor.

Yani iki farklı gerçek asset'i tek asset sandım.

Bu security açısından daha ağır olabilir çünkü gerçek attack surface'in bir kısmını kaybedebilirim.

---

# False Split

Gerçekte:

    Asset A

var.

Ama sistem:

    Asset A1
    Asset A2

diyor.

Örneğin sadece IP değişti diye yeni asset oluşturmak false split yaratabilir.

---

# 🔑 Güçlü Identity Evidence

Daha sağlam correlation için:

- instance ID
- agent ID
- cloud instance ID
- machine ID
- MAC
- serial number

gibi identifier'lar kullanabilirim.

Hostname ve IP tek başına daha zayıf evidence olabilir.

---

# 🐞 Debugging Mini Mock

Bugünkü en önemli kısım buydu.

Her problemde aynı şablonu kullandım:

    İlk sahip katman
    ↓
    Alternatif hipotezler
    ↓
    Ölçmek istediğim state
    ↓
    İlk ayırıcı deney
    ↓
    Deney neyi eliyor?
    ↓
    Teknik hüküm

---

# Incident 1 — Python Config

Semptom:

**Beklediğim config değeri kullanılmıyor.**

İlk sahip katman:

    config / precedence

Hipotezler:

1. CLI argümanı parse ediliyor ama final config'e aktarılmıyor olabilir.
2. Precedence sırası yanlış olabilir.

İlk ayırıcı deney:

    config = 60
    ENV = 15
    CLI = 5

Runtime sonucuna bakarım.

Bu deney:

    CLI hiç işlenmiyor mu?

ile:

    precedence yanlış mı?

sorularını ayırır.

---

# Incident 2 — Linux

Semptom:

    CPU düşük
    program ilerlemiyor

Hipotezler:

1. Process I/O, lock veya başka process bekliyor olabilir.
2. Program kendi isteğiyle `sleep` / `wait` yapıyor olabilir.

İlk ölçmek istediğim:

> **Process hangi runtime state'te ve neyi bekliyor?**

Önemli:

> **Process listede = uygulama sağlıklı çalışıyor demek değildir.**

PID'nin var olması yalnız process'in henüz sonlanmadığını gösterir.

---

# Incident 3 — Git

Semptom:

    git diff boş
    ama değişiklik yaptım

Hipotezler:

1. Değişiklik staged olabilir.
2. Değişiklik untracked bir dosyada olabilir.

Kontrol:

    git status
    git diff
    git diff --staged

Mental model:

    git diff
    -> Working Tree <-> Index

    git diff --staged
    -> Index <-> HEAD

Dolayısıyla:

    git diff boş
    !=
    değişiklik yok

---

# Incident 4 — Docker Cache

Semptom:

    sadece app.py değişti
    ama dependency install tekrar çalıştı

Hipotez 1:

    app.py dependency install'dan önce COPY ediliyor
    ↓
    app.py değişiyor
    ↓
    önceki layer cache miss
    ↓
    dependency RUN tekrar çalışıyor

Hipotez 2:

    dependency metadata gerçekten değişti

İlk sorum:

> **İlk cache miss hangi instruction'da başladı?**

Build log ve Dockerfile sırasına bakarım.

---

# 🧠 Cache Invalidation vs Instruction Order

Bunlar aynı şey değil.

    Cache invalidation
    -> Docker'ın mekanizması

    Instruction-order optimization
    -> Benim bu mekanizmayı bilerek Dockerfile'ı düzenlemem

Örneğin:

    COPY dependency metadata
    ↓
    install dependencies
    ↓
    COPY sık değişen source

Böylece source değişikliği dependency layer'ını gereksiz yere bozmaz.

---

# Incident 5 — Storage

Semptom:

    Container recreate edildi.
    Eski /data verisi yok.

Hipotezler:

1. `/data` volume'a bağlı değildir, writable layer'a yazılmıştır.
2. Volume vardır ama recreate sırasında aynı volume tekrar bağlanmamıştır.

İlk ölçmek istediğim:

> **`/data` şu anda gerçekten hangi backing storage'a bağlı?**

Önemli:

> **Container'ın `/data` içine yazabiliyor olması persistence kanıtı değildir.**

Writable layer'a da gayet güzel yazabilir.

---

# Incident 6 — Security / Identity

Semptom:

    agent_id aynı
    hostname farklı

Hipotezler:

1. Aynı asset olabilir, hostname değişmiş veya source stale olabilir.
2. Agent ID reuse edilmiş olabilir.

İlk ölçmek istediğim:

    agent_id unique mi?
    stable mı?

Sonra:

- MAC
- machine ID
- cloud instance ID
- timestamp

ile cross-check ederim.

Aynı agent ID güçlü evidence olabilir.

Ama:

> **Identifier'ın gerçekten unique ve stabil olduğunu doğrulamadan "kesin aynı asset" diyemem.**

---

# 🎤 Mock Interview — Kısa Cevaplar

## 1. `raise` ile `return` farkı

`return` fonksiyonun normal akışını bitirip değer döndürür.

`raise` normal control flow'u kesip exception üretir.

    return
    -> normal flow

    raise
    -> exception flow

---

## 2. JSON syntax valid olduğu halde neden reject edilir?

Çünkü:

    syntax validity
    !=
    application validity

JSON parse edilebilir ama:

- `port` yanlış tip olabilir
- `asset_id` eksik olabilir
- `tags` yanlış yapıda olabilir

Yani:

    parse
    ↓
    schema / business validation

ayrı aşamalardır.

---

## 3. Config precedence neden application contract?

Aynı ayar birden fazla source'tan gelebilir.

Örneğin:

    CLI > ENV > config file > default

diyorsam bu sıra deterministic olmalı.

Aksi halde kullanıcının dışarıdan gördüğü uygulama davranışı değişir.

---

## 4. `venv` reproducibility'yi garanti eder mi?

Hayır.

`venv` esas olarak Python environment izolasyonu sağlar.

Tek başına şunları garanti etmez:

- aynı package version
- aynı Python version
- aynı OS
- aynı native library

Reproducibility için dependency sürümleri ve gerekirse daha geniş environment tanımı gerekir.

---

## 5. PID neden her zaman yeterli değildir?

PID tekrar kullanılabilir.

Eski process öldükten sonra aynı PID başka process'e verilebilir.

Gerekirse:

- command
- args
- PPID
- start time

gibi ek bilgilerle doğrularım.

---

## 6. SIGTERM ile graceful shutdown ilişkisi

    SIGTERM
    -> kapanma isteği

    Graceful shutdown
    -> uygulamanın kontrollü kapanma davranışı

Uygulama:

- yeni işi durdurmalı
- mevcut işi tamamlamalı
- kaynakları kapatmalı
- state'i persist etmeli
- kontrollü exit etmeli

---

## 7. Writable layer ile named volume farkı

    Writable layer
    -> container lifecycle

    Named volume
    -> container'dan bağımsız lifecycle

Container recreate sonrası kalması gereken veri writable layer'a güvenmemeli.

---

## 8. `git restore --staged`

Git'te:

    Working Tree
    Index
    HEAD

ayrı state'lerdir.

`git restore --staged`:

    Index'i değiştirir

Working Tree'deki dosyayı otomatik silmez.

---

## 9. Docker cache invalidation ile instruction-order optimization farkı

    Cache invalidation
    -> mekanizma

    Instruction-order optimization
    -> mekanizmayı daha verimli kullanmak için yapılan tasarım

Örneğin dependency metadata'yı sık değişen app source'undan ayırmak cache verimini artırabilir.

---

## 10. Source lineage olmadan canonical asset üretmenin riski

Şunları kaybedebilirim:

    Bu value nereden geldi?
    Ne zaman geldi?
    Neden bunu seçtim?
    Hangi identifier'a bağlıydı?

Böyle olunca yanlış merge/split veya conflict kararlarını debug etmek zorlaşır.

---

# 🏗️ Asset Intelligence Collector — System Design

Ana amaç:

> **Farklı source'lardan gelen asset kayıtlarını tek ve güvenilir canonical inventory'ye çevirmek.**

Genel mimari:

    Sources
    ↓
    Adapters
    ↓
    Normalize
    ↓
    Validate
    ↓
    Identity / Correlation
    ↓
    Merge veya Conflict
    ↓
    Canonical Inventory
    ↓
    Persistent Storage
    ↓
    Risk / Findings
    ↓
    Prioritization / Reporting

Ek olarak:

    Source Lineage
    Observability
    Config / Secrets
    Graceful Shutdown

---

# Source Adapter

Her source farklı formatta veri üretebilir.

Örneğin:

- CMDB
- Cloud
- Scanner
- EDR

Adapter source-specific detayları içeride tutar.

Sonraki katmanlar mümkün olduğunca ortak forma bakar.

---

# Normalize

    farklı source representation
    ↓
    canonical representation

---

# Validate

    canonical record
    ↓
    application contract doğru mu?

---

# Identity / Correlation

Asıl soru:

> **İki source record aynı gerçek asset'i mi temsil ediyor?**

Güçlü evidence:

    merge

Evidence yetersiz:

    conflict / ayrı tut

---

# Canonical State

Canonical inventory sadece process memory'de bırakılmamalı.

    canonical inventory
    ↓
    persistent storage

---

# Source Lineage

Canonical value seçerken mümkünse şunlar korunmalı:

- value
- source
- observed_at
- collection_method
- source_identifier
- confidence

Böylece:

**"Bu IP'yi neden canonical seçtik?"**

sorusunun cevabı bulunabilir.

---

# Error Isolation

Tek kötü record:

    bütün pipeline'ı devirmesin

ama failure:

    görünür olsun
    loglansın
    sayılsın

---

# Config / Secrets

Config ve secret'lar source code'dan ayrı tutulmalı.

---

# Graceful Shutdown

Runtime kapanırken:

    shutdown request
    ↓
    current operation boundary
    ↓
    state persist
    ↓
    cleanup
    ↓
    exit

şeklinde kontrollü kapanış olmalı.

---

# 🌳 Pre-Commit Smoke Check

Commit atmadan önce:

1. Working Tree'de ne değişti?
2. Index'te ne stage edildi?
3. HEAD hangi snapshot?
4. Şimdi commit atarsam next commit'e ne girecek?

Ayrıca şunların yanlışlıkla stage edilmediğini kontrol ederim:

- `.log`
- cache
- build output
- `.env`
- runtime/generated artifact

Son kontrol:

    git status
    git diff
    git diff --staged

> **Commit Working Tree'nin tamamını değil, staged Index snapshot'ını kaydeder.**

---

# 🧯 Hata Avı

## 1. Asset sayısı arttı -> kesin yeni asset geldi

TIRT.

Source / identity / dedup / state değişmiş olabilir.

---

## 2. İki source aynı değeri söylüyor -> kesin doğru

TIRT.

Source'lar bağımsız olmayabilir veya aynı stale kaynaktan besleniyor olabilir.

---

## 3. En yeni kayıt her zaman doğrudur

TIRT.

Timestamp temporal evidence'dır, truth garantisi değildir.

---

## 4. Aynı source her field için en güvenilirdir

TIRT.

Authority field-specific olabilir.

---

## 5. Emin değilsem canonical value seçmek zorundayım

TIRT.

Conflict bırakabilirim.

---

## 6. `git diff` boş -> repo değişmedi

TIRT.

Değişiklik staged veya untracked olabilir.

---

## 7. Process listede -> uygulama sağlıklı

TIRT.

Yalnız process hâlâ yaşıyor olabilir.

---

## 8. Dependency install tekrar çalıştı -> dependency kesin değişti

TIRT.

Upstream cache miss olabilir.

---

## 9. Container `/data` içine yazıyor -> veri persistent

TIRT.

Writable layer olabilir.

---

## 10. Aynı agent ID -> kesin aynı asset

Fazla kesin.

Agent ID'nin unique ve stabil olduğundan da emin olmam gerekir.

---

# 🧠 Kafaya Kazı

> [!quote]
> Asset count semptomdur, root cause değildir.

> [!quote]
> Source, identity, dedup ve state ayrı problem katmanlarıdır.

> [!quote]
> Bilmediğin lineage bilgisini uydurma; unknown bırak.

> [!quote]
> Çoğunluk kaliteli ve bağımsız evidence demek değildir.

> [!quote]
> Yeni timestamp doğruluk garantisi değildir.

> [!quote]
> Source authority field-specific olabilir.

> [!quote]
> Evidence yetersizse conflict bırakmak geçerli sonuçtur.

> [!quote]
> Debugging'de önce state'i belirle, sonra aracı seç.

> [!quote]
> `git diff` Git state'lerinin yalnız bir kısmını gösterir.

> [!quote]
> Docker cache debugging'de ilk cache miss'i bul.

> [!quote]
> Bir path'e yazabilmek persistence kanıtı değildir.

> [!quote]
> Güçlü identifier bile uniqueness ve stability varsayımıyla değerlendirilmelidir.

> [!quote]
> Source lineage canonical kararın neden verildiğini açıklamamı sağlar.

> [!quote]
> İyi debugging ve iyi system design aynı yerde başlar: sorumluluk ve state sınırları.

---

# 📌 30 Saniyelik Özet

    +450 canonical asset
    !=
    +450 kesin yeni gerçek asset

    Kontrol:
    Source
    Identity
    Dedup
    State


    SOURCE LINEAGE

    value
    source
    observed_at
    collection_method
    source_identifier
    confidence


    DEBUGGING

    Semptom
    ↓
    Katmanlar
    ↓
    Hipotezler
    ↓
    State
    ↓
    Ayırıcı deney
    ↓
    Kanıt
    ↓
    Root cause


    PYTHON
    -> config / precedence

    LINUX
    -> process / runtime

    GIT
    -> Working Tree / Index / untracked

    DOCKER
    -> cache / mount / persistence

    SECURITY
    -> identity / correlation


    SYSTEM DESIGN

    Sources
    ↓
    Adapters
    ↓
    Normalize
    ↓
    Validate
    ↓
    Identity / Correlation
    ↓
    Merge / Conflict
    ↓
    Canonical State
    ↓
    Persistence
    ↓
    Risk / Reporting

---

# ✅ Günün Kazanımları

- [x] Dependency declaration ile installation tekrar ayrıldı
- [x] Retrieval sayesinde Docker eksiğim ortaya çıktı
- [x] Process identity ve runtime state kontrolü tekrarlandı
- [x] SIGTERM ile graceful shutdown ayrıldı
- [x] `.gitignore` ile tracked state tekrarlandı
- [x] Vulnerability ile exposure tekrar ayrıldı
- [x] +450 asset problemi katmanlara bölündü
- [x] Source / identity / dedup / state ayrıldı
- [x] Asset count'un root cause olmadığı anlaşıldı
- [x] Source overlap hipotezi üretildi
- [x] Identity split hipotezi üretildi
- [x] Dedup failure hipotezi üretildi
- [x] Canonical inventory karşılaştırma deneyi tasarlandı
- [x] Source scope'un belirsiz varsayım olduğu fark edildi
- [x] Source lineage yapısı öğrenildi
- [x] Bilinmeyen alanların `unknown` bırakılması öğrenildi
- [x] Majority vote ile evidence quality ayrıldı
- [x] Temporal evidence'in sınırı öğrenildi
- [x] Source authority'nin field-specific olduğu öğrenildi
- [x] Conflict state'in geçerli sonuç olduğu görüldü
- [x] False merge / false split tekrarlandı
- [x] Debugging incident'ları ortak şablonla analiz edildi
- [x] Config precedence debugging tekrarlandı
- [x] Linux runtime debugging tekrarlandı
- [x] Git staged / untracked ayrımı tekrarlandı
- [x] Docker cache invalidation tekrarlandı
- [x] Storage persistence için mount kontrolü tekrarlandı
- [x] Asset Intelligence Collector system design oluşturuldu
- [x] Source lineage system design'e bağlandı
- [x] Persistent state ihtiyacı eklendi
- [x] Error isolation ve observability eklendi
- [x] Config / secret ayrımı system design'e bağlandı
- [x] Graceful shutdown system design'e bağlandı
- [x] Pre-commit smoke check tekrarlandı

> [!success] 🚀 Gün sonu sonucu
> Bugün Python, Linux, Git, Docker ve CAASM ayrı ayrı konular gibi görünse de hepsinde aynı yöntemi kullandım:
>
> **Problemi katmanlara ayır -> state'i ölç -> hipotezleri ayır -> en küçük deneyi yap -> kanıta göre hüküm ver.**
>
> Artık:
>
> - Asset sayısı arttı
> - Process ilerlemiyor
> - `git diff` boş
> - Docker dependency'yi tekrar kurdu
> - Container data görmüyor
> - İki asset aynı mı?
>
> gibi semptomlarda direkt çözüm atmadan önce şunu soracağım:
>
> **Bu problemin sahibi hangi katman, hangi state'i bilmiyorum ve bunu en ucuz hangi deneyle kanıtlayabilirim?**
>
> Günün en kritik cümlesi:
>
> **İyi debugging ve iyi system design aynı yerden başlar: sorumlulukları ve state sınırlarını doğru çizmek.**