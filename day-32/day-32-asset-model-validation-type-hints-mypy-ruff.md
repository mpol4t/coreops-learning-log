---
title: "Gün 32 — Asset Model, Validation Pipeline, Type Hint, Mypy ve Ruff"
tags:
  - coreops
  - day32
  - python
  - json
  - validation
  - normalization
  - datamodel
  - type-hints
  - mypy
  - ruff
  - git
aliases:
  - "Gün 32 Asset Model Validation Pipeline"
status: completed
---

# 🧠 Gün 32 — Asset Model, Validation Pipeline, Type Hint, Mypy ve Ruff

> [!abstract] 🎯 Ana fikir
> Bugün dışarıdan gelen güvenilmez JSON verisini direkt sistem içinde kullanmak yerine katmanlardan geçirip güvenilir bir `Asset` modeline dönüştürdüm.
>
> Ana pipeline:
>
>     JSON
>       ↓
>     Parser
>       ↓
>     Normalization
>       ↓
>     Validation
>       ↓
>     Asset Object
>       ↓
>     Serialization
>       ↓
>     JSONL Output
>
> Günün en kritik ayrımı:
>
> **Type hint ne beklediğimi söyler, runtime validation gerçekten gelen veriyi kontrol eder.**

---

# 🔎 Araştırma Rotası

## `Asset(port: int)` yazıyorsa neden runtime'da `"443"` girebiliyor?

Çünkü Python type annotation'ları varsayılan olarak runtime type enforcement yapmaz.

Örneğin:

    port: int

şunu anlatır:

> Burada `int` bekleniyor.

Ama otomatik olarak:

> `str` gelirse programı durdur.

anlamına gelmez.

Bu yüzden modelin constructor'ına:

    port="443"

verildiğinde runtime'da obje yine oluşabilir.

Labda bunu gerçekten gördüm:

    Asset(
        asset_id='server01',
        hostname='web01',
        port='443',
        active=True,
        tags=['web']
    )

Yani:

    annotation
    ≠
    runtime validation

---

# 🧠 Mypy ile Runtime Validator Neden Birbirinin Yerine Geçmez?

## Mypy

Mypy statik analiz yapar.

Yani programı çalıştırmadan source code'a bakar.

Sorusu:

> Kod içerisinde type kullanımları birbiriyle uyumlu mu?

Mypy'nin dışarıdan runtime'da gelecek gerçek JSON verisini otomatik kontrol etmesi gibi bir durum yok.

---

## Runtime Validator

Validator ise uygulama çalışırken gerçekten gelen veriyi kontrol eder.

Örneğin JSON'dan:

    "port": "443"

geldiyse validator:

> Beklenen type `int`, gelen `str`.

deyip reject edebilir.

Kısa model:

    Type Hint
    → beklenti

    Mypy
    → source code üzerinde statik kontrol

    Runtime Validation
    → gerçekten gelen verinin kontrolü

---

# 📥 Parser Katmanı

Parser'ın görevi sadece dosyayı okuyup JSON'u Python objesine çevirmek.

Akış:

    Dosya
      ↓
    open()
      ↓
    file object
      ↓
    json.load(file)
      ↓
    Python object

Parser ayrıca top-level JSON'un liste olmasını bekliyor.

Yani contract:

    Top-Level JSON
    → list

Eğer liste değilse:

    TypeError

üretiliyor.

---

# 🐞 Parser Tarafında Öğrendiğim Nokta

`json.load()` dosya yolu değil, açık bir file object bekler.

Yanlış düşünce:

    json.load(path)

Doğru akış:

    with open(path, encoding="utf-8") as file:
        loaded = json.load(file)

Yani:

    path
    ≠
    file object

---

# 🧹 Normalization Katmanı

Normalization'ın görevi:

> Veriyi canonical / temiz representation'a yaklaştırmak.

Yaptığım şeyler:

- `asset_id` string ise `.strip()`
- `hostname` string ise `.strip()`
- `tags` listeyse içindeki stringlere `.strip()`
- `port` değerini olduğu gibi taşı
- `active` değerini olduğu gibi taşı

Örnek:

    " server01 "

↓

    "server01"

---

# ⚠️ Normalization'da Yaptığım Önemli Hata

Başta bozuk veriyi normalization sırasında silmeye yaklaşmıştım.

Örneğin:

    tags = ["web", 123]

bunu:

    tags = ["web"]

yaparsam `123` değerini sessizce kaybetmiş olurum.

Bu kötü çünkü validator artık gerçek problemi göremez.

Doğru model:

    ["web", 123]
          ↓
    Normalization

    ["web", 123]
          ↓
    Validation

          ↓
    REJECT

> [!important]
> **Normalizer validation'ın görmesi gereken evidence'ı silmemeli.**

---

# ✅ Validation Katmanı

Validation'ın sorusu:

> Bu record gerçekten `Asset` olmaya uygun mu?

Required field'lar:

- `asset_id`
- `hostname`
- `port`
- `active`
- `tags`

---

# `asset_id`

Kontroller:

- Field var mı?
- `str` mi?
- Boş mu?

Geçersiz örnek:

    asset_id = ""

---

# `hostname`

Kontroller:

- Field var mı?
- `str` mi?
- Boş mu?

---

# `port`

Kontroller:

- Tam olarak `int` mi?
- Geçerli aralıkta mı?

Kullanılan kontrol:

    type(port) is int

Bunun sebebi önemli.

Python'da:

    bool

ile:

    int

arasında inheritance ilişkisi var.

Dolayısıyla yalnız:

    isinstance(True, int)

tarzı düşünürsem istemediğim davranış çıkabilir.

`type(port) is int` kullanınca:

    443
    → kabul

    True
    → reject

---

# Port Aralığı

Gerçek kontrol:

    0 < port < 65536

Yani geçerli port:

    1 - 65535

> [!warning]
> Kodun hata mesajında `0-65535` yazıyor ama gerçek condition `1-65535` kabul ediyor.
>
> Hata mesajını gerçek contract ile aynı hale getirmem daha temiz olur.

---

# `active`

Tam olarak boolean olması gerekiyor.

Geçerli:

    True
    False

Geçersiz:

    "true"
    1

---

# `tags`

Önce:

    tags list mi?

Sonra:

    listedeki her eleman str mi?

Son olarak:

    string boş mu?

Geçerli:

    ["web", "linux"]

Geçersiz:

    ["web", 123]

veya:

    ["web", ""]

---

# 🐞 Required Field Kontrolünde Yaptığım Hata

Başta şu mantığı kurmuşum:

    for x in required:
        if x not in required:

Bu hiçbir işe yaramaz.

Çünkü `x` zaten `required` listesinden geliyor.

Yani doğal olarak:

    x in required

olacak.

Gerçek soru:

> Required field normalized record içinde var mı?

Doğru zihinsel model:

    required field
          ↓
    normalized dict içinde ara

---

# ⚠️ TypeError ve ValueError Ayrımı

Bugün exception semantiğini de ayırdım.

## TypeError

Type yanlışsa.

Örneğin:

    Beklenen:
    port = int

    Gelen:
    port = "443"

---

## ValueError

Type doğru ama value geçersizse.

Örneğin:

    port = 70000

Burada:

    type = int ✅
    value range ❌

Dolayısıyla kavramsal olarak `ValueError` daha anlamlı.

---

# 🚨 Mevcut Kodda Dikkatimi Çeken Exception Tutarsızlığı

Burada önemli bir nokta var.

`validation()` içinde validation hatalarının çoğu:

    raise TypeError(...)

ile üretiliyor.

Ama record loop'unda:

    except ValueError as hata:

yakalanıyor.

Yani mevcut kod metnine göre:

    validation()
    ↓
    TypeError
    ↓
    except ValueError yakalayamaz

Bu yüzden kod ile aşağıdaki reject loglarının gösterildiği test sonucu arasında bir tutarsızlık var.

Daha temiz contract:

    Type yanlış
    → TypeError

    Değer yanlış
    → ValueError

ve `main()` hangi failure class'larını record rejection olarak kabul edecekse onları bilinçli şekilde handle etmeli.

---

# 🧱 Asset Model

Validation geçen dict daha sonra `Asset` objesine dönüştürülüyor.

Akış:

    normalized dict
          ↓
       validation
          ↓
        Asset(...)

Bunun amacı dışarıdaki serbest dict yapısından sonra sistem içinde daha belirgin bir veri modeli kullanmak.

Örneğin dict:

    data["asset_id"]

Asset object:

    asset.asset_id

---

# 🐞 Asset'i Dict Sanma Hatası

Başta şöyle düşünmüşüm:

    Asset["asset_id"]

Ama `Asset` dict değil.

Object kullanımı:

    asset.asset_id

Kısa:

    dict
    → data["alan"]

    object
    → object.alan

---

# 🔄 Asset Neden Tekrar Dict'e Dönüyor?

Burada başta kafam karıştı:

> Asset'e çevirdik, neden tekrar dict yapıyoruz?

Çünkü programın iç representation'ı ile dışarı yazılan serialization formatı farklı.

Program içinde:

    Asset Object

JSON'a yazarken:

    Asset
      ↓
    dict
      ↓
    json.dumps()
      ↓
    JSON

JSON standart olarak benim özel Python `Asset` class'ımı tanımaz.

Bu yüzden serialization gerekir.

---

# 📄 JSONL Output

Her accepted record ayrı bir JSON satırı olarak yazılıyor.

Mantık:

    record 1 JSON
    record 2 JSON
    record 3 JSON

Bu format:

    JSON Lines / JSONL

olarak kullanılabilir.

Pipeline'ın son hali:

    JSON Input
        ↓
      Parser
        ↓
    Normalization
        ↓
    Validation
        ↓
    Asset Object
        ↓
    Serialization
        ↓
    JSONL Output

---

# 🧪 Yaptığım Testler

## Geçerli JSON

Sonuç:

    accepted=1
    rejected=0

---

## Eksik `asset_id`

Sonuç:

    record_rejected
    accepted=0
    rejected=1

---

## Boş `asset_id`

Sonuç:

    Asset_id boş olmamalı!

    accepted=0
    rejected=1

---

## Port sınırı

Test:

    port = 65536

Sonuç:

    reject

---

## Bool Port

Test:

    port = true

Sonuç:

    Port field'ının integer olması gerekiyor!

Bu test `bool` / `int` tuzağını kontrol etmiş oldu.

---

## Hatalı Tags

Test:

    ["web", 123]

Sonuç:

    Tags listesi içindeki değerlerin string olması gerekiyor!

---

## Boş Tag

Test:

    ["web", ""]

Sonuç:

    Tags liste içindeki değerler boş olmamalı!

---

# 🧠 Type Hint Testinin En Güzel Kanıtı

Ayrı testte:

    port="443"

vererek `Asset` oluşturdum.

Runtime sonucu:

    Asset(... port='443' ...)

oldu.

Bu deney doğrudan şunu kanıtladı:

> **Annotation tek başına runtime validation yapmıyor.**

---

# 🔎 Mypy

Çalıştırdığım:

    mypy src

Sonuç:

    Success: no issues found in 4 source files

Mypy:

- runtime input validator değildir
- source code üzerinde type analizi yapar
- annotation'lardan yararlanır

Bu yüzden runtime validator'ın yerine geçmez.

---

# 🧹 Ruff

Ruff ile kod kalitesi / lint kontrolleri yaptım.

Çalıştırdığım:

    ruff check . --fix

Sonuç:

    All checks passed!

---

# Ruff ile Öğrendiğim Şeyler

## Kullanılmayan Import

Örneğin:

    import time

eklenmiş ama kullanılmıyorsa Ruff bunu yakalayabilir.

---

## Import Sırası

Örneğin:

    import argparse
    import json
    import sys

gibi düzenli standard-library import sırası oluşabilir.

---

## Logger Kullanımı

Module logger:

    logger = logging.getLogger(__name__)

Sonrasında:

    logger.warning(...)
    logger.info(...)

kullanmak modül bazlı logging açısından daha temiz bir yapı sağlıyor.

---

# 🌳 Git Tarafında Yaşadığım Önemli Incident

Day32 sonunda:

    git add .

kullandım.

Bu komut yalnız Day32'yi değil Working Tree'deki başka değişiklikleri de stage etti.

Stage'e girenler arasında:

- Day29'dan `MARKER`
- Day31 klasörü
- Day32 dosyaları
- Daha önce silinmiş başka bir path

vardı.

Bu bana yine şunu gösterdi:

> **`git add .` kullanmadan önce `git status` ile scope'u kontrol etmem gerekiyor.**

---

# 🚨 Embedded Git Repository Uyarısı

Git şu uyarıyı verdi:

    You've added another git repository inside your current repository.

Sebep:

    Day31/git-conflict-lab

klasörünün içinde ayrı bir `.git` repository olması.

Outer repository bunu normal klasör içeriği gibi değil:

    mode 160000

şeklinde özel bir Git repository entry'si olarak stage etti.

Commit çıktısında:

    create mode 160000 Day31/git-conflict-lab

görmem bunun kanıtı.

> [!warning]
> Bir repository'nin içine yanlışlıkla başka `.git` repository koyarsam Git bunu normal klasör gibi takip etmeyebilir.
>
> Gerçekten submodule istemiyorsam nested `.git` durumunu düzeltmem gerekir.

---

# ⚠️ Git Tarafındaki Asıl Hata

Direkt:

    git add .

yaptığım için istemediğim şeyleri de commit'e aldım.

Örneğin:

    Day29/.../MARKER

bir test artifact'i olmasına rağmen commit'e girdi.

Ayrıca başka bir path'in deletion'ı da aynı commit'e girdi.

Daha iyi akış:

    git status

↓

    git add Day32/

↓

    git diff --staged --name-status

↓

    git commit

Yani:

> **Commit'ten önce Index snapshot'ını kontrol et.**

---

# 🧯 Hata Avı

## 1. `port: int` yazdım, artık string gelemez

TIRT.

Annotation runtime enforcement değildir.

---

## 2. Mypy runtime'da JSON'dan gelen veriyi kontrol eder

TIRT.

Mypy statik analiz aracıdır.

---

## 3. Normalization bozuk değerleri silebilir

TIRT.

Validation evidence'ını kaybetmiş olurum.

---

## 4. Parser validation yapmalı

TIRT.

Parser formatı çözer.

Validator application contract'ını kontrol eder.

---

## 5. `bool` kesinlikle `int` kontrolünden geçmez

TIRT.

Python type modelinde buna dikkat etmek gerekir.

---

## 6. Asset bir dict'tir

TIRT.

Asset object'tir.

---

## 7. Asset direkt JSON'a yazılabilir

Her zaman değil.

Önce serialize edilebilir bir yapıya dönüştürmek gerekir.

---

## 8. `TypeError` raise edip sadece `ValueError` catch etmek yeterli

TIRT.

Exception contract'ı birbiriyle uyumlu olmalı.

---

## 9. Port mesajında `0-65535` yazması doğru

Mevcut condition ile tam uyumlu değil.

Gerçek kabul aralığı:

    1-65535

---

## 10. `git add .` yalnız üzerinde çalıştığım Day32'yi stage eder

TIRT.

Bulunduğum scope altındaki başka değişiklikleri de stage edebilir.

---

## 11. Repository içindeki başka repository normal klasör gibi davranır

TIRT.

Nested `.git` varsa embedded repository / submodule benzeri state ortaya çıkabilir.

---

# 🧠 Kafaya Kazı

> [!quote]
> Parser formatı çözer.

> [!quote]
> Normalization representation'ı temizler.

> [!quote]
> Validation kabul veya rejection kararı verir.

> [!quote]
> Normalizer validator'ın görmesi gereken hatayı gizlememeli.

> [!quote]
> Type annotation runtime type enforcement değildir.

> [!quote]
> Mypy source code'u analiz eder, runtime validator gerçek input'u kontrol eder.

> [!quote]
> Dict ile object aynı veri erişim modeline sahip değildir.

> [!quote]
> Program içindeki model ile dışarıdaki serialization formatı farklı olabilir.

> [!quote]
> Exception type'ları da application contract'ın bir parçasıdır.

> [!quote]
> Commit atmadan önce neyin staged olduğunu kanıtla.

---

# 📌 30 Saniyelik Özet

    INPUT JSON
        ↓
      PARSER
        ↓
    NORMALIZATION
        ↓
     VALIDATION
        ↓
    ASSET OBJECT
        ↓
    SERIALIZATION
        ↓
    JSONL OUTPUT


    TYPE HINT
    → ne beklediğimi söyler

    MYPY
    → source code'u statik kontrol eder

    VALIDATOR
    → runtime'daki gerçek veriyi kontrol eder


    NORMALIZATION
    → temizle

    VALIDATION
    → kabul / reddet


    ASSET
    → sistem içi model

    JSON
    → serialization formatı


    GIT
    git add .
    → scope içindeki birçok değişikliği stage edebilir

    nested .git
    → embedded repository uyarısı

    commit öncesi:
    status
    ↓
    kontrollü add
    ↓
    staged diff
    ↓
    commit

---

# ✅ Günün Kazanımları

- [x] Type annotation ile runtime validation ayrıldı
- [x] Mypy ile runtime validator ayrıldı
- [x] Parser sorumluluğu netleşti
- [x] Top-level JSON contract'ı öğrenildi
- [x] Normalization ve validation ayrıldı
- [x] Bozuk normalization'ın validation evidence'ını silebileceği öğrenildi
- [x] Required field kontrol mantığı düzeltildi
- [x] `bool` / `int` type tuzağı tekrarlandı
- [x] Port range validation yapıldı
- [x] Tags listesi ve elemanları validate edildi
- [x] TypeError / ValueError semantiği öğrenildi
- [x] Asset model mantığı öğrenildi
- [x] Dict ve object farkı öğrenildi
- [x] Asset → dict → JSON serialization zinciri öğrenildi
- [x] JSONL output üretildi
- [x] Valid ve invalid fixture'lar test edildi
- [x] Runtime type hint karşı deneyi yapıldı
- [x] Mypy çalıştırıldı
- [x] Ruff çalıştırıldı
- [x] Logger yapısı öğrenildi
- [x] `git add .` geniş scope riski tekrar görüldü
- [x] Embedded Git repository uyarısı gözlemlendi
- [x] `160000` Git entry'sinin nested repository ile ilişkisi fark edildi
- [x] Commit öncesi staged snapshot kontrolünün önemi tekrarlandı

---

# 🚀 Gün Sonu Sonucu

Bugün veri pipeline'ında artık şu ayrımı daha net yapıyorum:

    Dışarıdan veri geldi
        ↓
    Önce parse et
        ↓
    Temsilini temizle
        ↓
    Gerçek contract'ı kontrol et
        ↓
    Güvenilir modele dönüştür
        ↓
    Kullan / serialize et

En kritik cümle:

> **Type hint benim niyetimi anlatır; runtime validation ise dış dünyadan gelen verinin gerçekten bu niyete uyup uymadığını kontrol eder.**