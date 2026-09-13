---
title: "Gün 44 — Generator, JSONL Streaming ve HTTP Pagination"
tags:
  - coreops
  - day44
  - python
  - generator
  - yield
  - jsonl
  - streaming
  - http
  - pagination
  - urljoin
aliases:
  - "Gün 44 Generator JSONL Streaming HTTP Pagination"
status: completed
---

# 🚰 Day 44 — Generator, JSONL Streaming & HTTP Pagination

> [!abstract] 🎯 Ana fikir
> Bugün iki konu aslında tek noktada birleşti:
>
> **Veriyi topluca beklemek yerine, parça parça üretip ilerletmek.**
>
> Blok 1:
>
>     JSONL dosyası
>          ↓
>     bir satır oku
>          ↓
>        parse
>          ↓
>        yield
>          ↓
>        consumer
>
> Blok 2:
>
>     HTTP Page 1
>          ↓
>        items
>          ↓
>        yield
>          ↓
>         next
>          ↓
>     HTTP Page 2
>          ↓
>        ...
>          ↓
>     next = None
>          ↓
>         STOP
>
> Yani bugünün ortak fikri:
>
> **State'i gerektiğinde ilerlet, veriyi gerektiğinde üret.**

---

# 1️⃣ BLOK 1 — Generator / `yield` / JSONL Streaming

> [!important]
> Generator'ın işi bütün sonuçları önceden hazırlayıp saklamak değil.
>
> **Sıradaki değer istendiğinde üretmek.**

Temel fark:

    return
    → değeri ver
    → fonksiyonu bitir


    yield
    → değeri ver
    → DURAKLA
    → state'i koru
    → sonraki istekte devam et

Generator oluşturmak da generator'ı çalıştırmak demek değil:

    g = iter_records(...)

    ↓

    generator object oluşur

Asıl çalışma:

    next(g)

veya:

    for record in g:

ile değer istendiğinde başlar.

---

# 🧠 `for` ve `next()` Mental Modeli

Şunu:

    for x in generator:
        ...

kabaca şöyle düşünebilirim:

    next()
      ↓
    yield
      ↓
    next()
      ↓
    yield
      ↓
    next()
      ↓
    ...

Generator bittiğinde iteration da biter.

> **`for`, generator'dan sıradaki değeri benim yerime sürekli ister.**

---

# 📄 JSONL Neden Streaming'e Çok Uygun?

JSONL'de her satır bağımsız bir JSON kaydı.

    satır 1 → JSON → dict
    satır 2 → JSON → dict
    satır 3 → JSON → dict

Bu yüzden bütün dosyayı RAM'e almak zorunda değilim.

    DISK
      ↓
    bir satır
      ↓
    strip
      ↓
    kontrol
      ↓
    json.loads
      ↓
    dict
      ↓
    yield
      ↓
    consumer

Labda bunu gerçekten `iter_records()` ile yaptım.

---

# 🧪 `iter_records(path)` Sözleşmem

Fonksiyon:

    iter_records(path)

Input:

    JSONL dosya yolu

Output:

    her iteration'da bir Python dict

Akışım:

    open(path)
       ↓
    satırı oku
       ↓
    strip()
       ↓
    boş mu?
       ↓
    json.loads()
       ↓
    dict mi?
       ↓
    yield record

Boş satır için özellikle **STRICT** politika seçtim:

    boş satır
       ↓
    ValueError
       ↓
    akış DURUR

Bu bilinçli bir contract kararıydı.

---

# 🔗 İkinci Generator — `iter_high_risk()`

İlk generator kayıt üretiyor:

    iter_records()
          ↓
        dict

İkinci generator bunları filtreliyor:

    iter_high_risk(records, minimum)
          ↓
    risk >= minimum?
       /       \
     hayır     evet
      ↓         ↓
    geçme     yield

Komple pipeline:

    assets.jsonl
         ↓
    iter_records()
         ↓
    parsed dict
         ↓
    iter_high_risk()
         ↓
    uygun dict
         ↓
      consumer

Burada iki generator da ayrıca büyük liste oluşturmuyor.

> [!important]
> **Generator'ın asıl gücü tek başına `yield` yazmak değil; generator'ları pipeline halinde birbirine bağlamak.**

---

# 🎯 Threshold Testinde Öğrendiğim Şey

İlk testte:

    minimum = 50

kullandım.

Ama test verilerimde:

    20
    45
    70
    80
    95

vardı.

`50` de `70` de aynı kayıtları geçiriyordu:

    70
    80
    95

Bu yüzden test çok güçlü değildi.

Daha iyi test:

    minimum = 90

Beklenen:

    vpn-01.local → 95

Buradan çıkardığım ders:

> **Test verisi, yanlış implementasyon ile doğru implementasyonu birbirinden ayırabilmeli.**

---

# 💥 Broken JSON — Streaming'i Canlı Gördüm

Dosya:

    doğru kayıt
    bozuk JSON
    doğru kayıt

STRICT davranış:

    ilk kayıt
       ↓
    parse başarılı
       ↓
    yield
       ↓
    consumer print eder ✅

    ikinci kayıt
       ↓
    json.loads()
       ↓
    JSONDecodeError 💥
       ↓
    akış durur

    üçüncü kayıt
       ↓
    HİÇ İŞLENMEZ

Çıktıda önce:

    api-01.local

gördüm.

Sonra JSON hatası geldi ve exit code:

    1

oldu.

Bu bana generator'ın dosyanın tamamını baştan parse etmediğini doğrudan gösterdi.

---

# 🧪 Streaming Kanıtı

Ayrıca sadece:

    first = next(records)

ile ilk kaydı istedim.

Sonuç:

    {'hostname': 'api-01.local', 'risk': 20}

Yani generator:

    "Dosyanın tamamını bitireyim."

demedi.

Sadece:

    "Bir kayıt mı istedin?
     Al ilk kayıt."

dedi.

---

# 🐞 BLOK 1 — Hatalarım

## 1. Fonksiyon zaten `path` alırken içine `argparse` koydum

**TIRT.**

    iter_records(path)

zaten dosya yolunu alıyor.

Doğrusu:

    path
     ↓
    open(path)

`argparse` gerekiyorsa CLI katmanının işi.

---

## 2. `json.loads()`tan sonra `.strip()` yapmaya çalıştım

Yanlış:

    json.loads(line).strip()

Çünkü:

    line
    → str

ama:

    json.loads(line)
    → dict / list / int / ...

olabilir.

Doğru:

    string
      ↓
    strip
      ↓
    json.loads

---

## 3. JSON datasına `.lower()` uyguladım

Parser'ın işi:

    veriyi parse etmek ✅

değil:

    veriyi kafama göre değiştirmek ❌

Dosyada:

    API-01.LOCAL

varsa parse sonrası da öyle kalmalı.

---

## 4. Boşluğu kontrol etmeden `json.loads("")` çalıştırdım

Yanlış sıra:

    strip
      ↓
    json.loads
      ↓
    boş mu?

Doğru:

    strip
      ↓
    boş mu?
      ↓
    değilse json.loads

---

## 5. `json.loads()` her zaman dict verir sandım

**TIRT.**

    {...}    → dict
    [...]    → list
    "abc"    → str
    123      → int
    true     → bool
    null     → None

Bu yüzden contract dict istiyorsa ayrıca:

    isinstance(record, dict)

kontrolü gerekiyor.

---

## 6. `FileNotFoundError` bozuk JSON'u yakalar sandım

Bunlar farklı failure:

    dosya yok
    → FileNotFoundError


    JSON syntax bozuk
    → JSONDecodeError

Hatanın türünü doğru isimlendirmem gerekiyor.

---

# 🧠 BLOK 1 — Kafaya Kazı

> [!tip]
> **`return` = VER + BİT**

> [!tip]
> **`yield` = VER + DURAKLA**

> [!tip]
> **`next()` = kaldığın yerden devam et ve sıradakini üret.**

> [!tip]
> **Generator oluşturmak ≠ generator'ı çalıştırmak.**

> [!tip]
> **`yield` yavaşlatmaz. Lazy üretim yapar.**

> [!tip]
> **`list(generator)` generator'ı tamamen tüketip sonuçları tekrar bellekte toplar.**

> [!tip]
> **JSONL = satır satır streaming için doğal format.**

---

# 2️⃣ BLOK 2 — HTTP Pagination + `next`

> [!abstract] 🎯 Pagination'ın özü
> Client:
>
> **"Kaç sayfa vardır?"**
>
> diye tahmin etmez.
>
> Server'ın döndürdüğü:
>
>     items
>     next
>
> contract'ını takip eder.

Akış:

    start_url
       ↓
    FETCH PAGE
       ↓
      items
       ↓
      yield
       ↓
       next
      /    \
   None     URL
    ↓        ↓
   STOP    urljoin
             ↓
        current_url
             ↓
           tekrar

---

# 🧠 `start_url` ve `current_url`

    start_url
    → başlangıç state'i

    current_url
    → şu anda bulunduğum sayfa

İlk başta:

    current_url = start_url

Sonrasında kontrolü server'dan gelen:

    next

devralıyor.

Yani:

    start
      ↓
    page1
      ↓
    next
      ↓
    page2
      ↓
    next
      ↓
    page3
      ↓
    None
      ↓
    STOP

---

# 🛑 Termination

Son response:

    "next": null

gönderirse Python'da:

    next_value = None

olur.

Contract:

    next != None
    → devam


    next == None
    → pagination bitti

Bu yüzden:

    next_value is None

kontrolü anlam olarak daha net.

Ayrıca:

    {"next": null}

ile:

    {}

aynı şey değil.

Birinde alan var ve değeri null.

Diğerinde alan tamamen eksik.

Contract `next` alanını zorunlu tutuyorsa bu ayrım önemli.

---

# 🌐 `urljoin()` Mental Modeli

Server her zaman absolute URL vermeyebilir.

Base:

    https://api.test.com/v2/assets/list?page=1

### `/assets?page=2`

Başında `/`:

    DOMAIN ROOT

Sonuç:

    https://api.test.com/assets?page=2

---

### `detail?page=2`

Başında `/` yok:

    mevcut directory'ye göre çöz

Sonuç:

    https://api.test.com/v2/assets/detail?page=2

---

### `?page=2`

Sadece query:

    path aynı kalır
    query değişir

Sonuç:

    https://api.test.com/v2/assets/list?page=2

Kafaya kazı:

    /abc
    → domain root


    abc
    → current directory


    ?x=1
    → current path + yeni query

URL'yi:

    base + next

şeklinde string olarak birleştirmek **TIRT**.

URL'nin kendi çözümleme kuralları var.

---

# 📡 `fetch_json()` vs `iter_assets()`

Buradaki responsibility ayrımı çok önemliydi.

## `fetch_json()`

Sadece:

    URL
     ↓
    HTTP request
     ↓
    response
     ↓
    body
     ↓
    JSON parse
     ↓
    dict

bilir.

**Pagination bilmez.**

---

## `iter_assets()`

Pagination state'ini yönetir:

    current_url
       ↓
    fetch_json()
       ↓
    items
       ↓
    yield
       ↓
    next
       ↓
    current_url update / stop

Yani:

    fetch_json()
    → TEK RESPONSE


    iter_assets()
    → SAYFALAR ARASI AKIŞ

Bu ayrımı korudum.

---

# 📨 Request / Header Tarafı

`Request()`:

    isteğin tarifini oluşturur

`urlopen()`:

    isteği gerçekten gönderir

Kısa:

    Request
    → PLAN

    urlopen
    → UYGULA

Header ayrımı:

    Accept: application/json
    → BEN NE İSTİYORUM?


    Content-Type: application/json
    → GELEN BODY NE FORMATTA?

Response yolu:

    bytes
      ↓
    decode UTF-8
      ↓
    string
      ↓
    json.loads
      ↓
    Python dict

---

# 🧪 Neden `mock_api.py` Yaptım?

Gerçek internet API'si:

- değişebilir,
- çökebilir,
- data değiştirebilir,
- rate limit uygulayabilir.

Ben ise kontrollü contract istedim.

Bu yüzden:

    client.py
       │
       │ HTTP
       ▼
    mock_api.py

kurdum.

Contract:

    GET /assets?page=1
         ↓
    api-01.local
    db-01.local
    next=/assets?page=2


    GET /assets?page=2
         ↓
    cache-01.local
    next=None

Başarılı client çıktısı:

    api-01.local
    db-01.local
    cache-01.local

Server çıktısı:

    request #1 -> /assets?page=1
    request #2 -> /assets?page=2

Ve en önemlisi:

    request #3 YOK ✅

Bu hem verilerin geldiğini hem de pagination'ın doğru yerde durduğunu kanıtladı.

---

# 💣 Pagination Broken Case

Doğru kodda:

    next URL varsa
       ↓
    current_url = urljoin(...)

olması gerekiyordu.

Bilerek:

    else:
        pass

yaptım.

Yani:

    next_value

değerini okudum ama:

    current_url

değerini değiştirmedim.

Sonuç:

    current_url = page1

olarak kaldı.

Akış:

    page1
      ↓
    next = page2
      ↓
    current_url DEĞİŞMEDİ ❌
      ↓
    page1 tekrar
      ↓
    page1 tekrar
      ↓
    ...

> [!danger]
> **`next` değerini okumak ile state'i ilerletmek aynı şey değil.**

Doğrusu:

    current_url = urljoin(current_url, next_value)

---

# 🧯 Sonsuz Loop'u Güvenli Test Etmem

Broken case'te programı gerçekten sonsuza kadar döndürmedim.

Mock server request sayısını sayıyordu.

    request #1
    request #2
    request #3

Üçüncü beklenmeyen request geldiğinde server kontrollü olarak:

    500 Internal Server Error

verdi.

Gerçek broken çıktı:

    request #1 -> /assets?page=1
    request #2 -> /assets?page=1
    request #3 -> /assets?page=1

Client:

    api-01.local
    db-01.local
    api-01.local
    db-01.local
    HTTP error: 500 Internal Server Error

Bu bana doğrudan şunu kanıtladı:

    next'i okudum ✅

ama:

    pagination state'ini ilerletmedim ❌

Mock server sayesinde sonsuz loop güvenli şekilde yakalandı.

---

# 🐞 BLOK 2 — Hatalarım

## 1. `pages[current]` içinde `"current"` key'i aranıyor sandım

Yanlış:

    pages[current]
    → "current" key'i

Doğru:

    current = "page-1"

ise:

    pages[current]

aslında:

    pages["page-1"]

demek.

Tırnak farkı:

    pages[current]
    → değişkenin DEĞERİ


    pages["current"]
    → gerçekten "current" isimli key

---

## 2. Eski validation'ı yeni pagination contract'ına taşıdım

Eski labdan:

    asset_id zorunlu

gibi bir kontrol getirmiştik.

Ama yeni item:

    {"hostname": "api-01.local"}

şeklindeydi.

Yani eski contract'ı yeni probleme yapıştırmış olduk.

Düzeltme:

    pagination için gereken boundary:

    items
    → list

    next
    → str veya None

> **Validation contract'a göre yapılmalı; eski projeden kopyalanmamalı.**

---

## 3. `next`i okumayı state update sandım

Yanlış:

    next_value = response["next"]

    ↓

    pagination ilerledi

**TIRT.**

Bu sadece bilgiyi okur.

State'i ilerleten:

    current_url = urljoin(current_url, next_value)

---

## 4. "Page 2 geldi, pagination başarılı" demek

Eksik kanıt.

Şu olabilir:

    Page 1 ✅
    Page 2 ✅
    Page 2 ❌
    Page 2 ❌
    ...

Doğru başarı kanıtı:

    request #1 → page1
    request #2 → page2
    request #3 → YOK

Yani **termination da test edilmeli.**

---

# 🧠 BLOK 2 — Kafaya Kazı

> [!tip]
> **Pagination sayfa sayısını tahmin etmez; `next` contract'ını takip eder.**

> [!tip]
> **`next = URL` → DEVAM.**

> [!tip]
> **`next = None` → DUR.**

> [!tip]
> **`fetch_json()` tek HTTP response bilir.**

> [!tip]
> **`iter_assets()` pagination state'ini bilir.**

> [!tip]
> **`yield item` sayesinde bütün asset'leri önce listeye toplamam gerekmez.**

> [!danger]
> **`next`i okumak ≠ `current_url`yi değiştirmek.**

> [!danger]
> **Pagination'ın doğru olduğunun kanıtı sadece son sayfaya ulaşmak değil, oradan sonra yeni request atmamak.**

---

# 📌 30 Saniyelik Özet

    BLOK 1

    DOSYA
      ↓
    bir satır
      ↓
    strip
      ↓
    validate
      ↓
    json.loads
      ↓
    dict
      ↓
    yield
      ↓
    filtre generator
      ↓
    consumer


    return
    → VER + BİT

    yield
    → VER + DURAKLA


    BLOK 2

    current_url
        ↓
    fetch_json()
        ↓
      items
        ↓
      yield
        ↓
       next
      /    \
    None    URL
     ↓       ↓
    STOP   urljoin
             ↓
        current_url
             ↓
           tekrar


    BAŞARI:

    page1
      ↓
    page2
      ↓
    STOP


    BROKEN:

    page1
      ↓
    next okundu
      ↓
    state değişmedi
      ↓
    page1
      ↓
    page1
      ↓
    mock server 500 💥

---

# ✅ Günün Kazanımları

- [x] `return` ve `yield` farkını oturttum
- [x] Generator'ın lazy çalıştığını anladım
- [x] `next()` ve `for` ilişkisini öğrendim
- [x] JSONL'yi satır satır streaming işledim
- [x] `iter_records()` generator'ını kurdum
- [x] Boş satır için STRICT politika seçtim
- [x] JSON syntax hatası ile yanlış veri tipi hatasını ayırdım
- [x] `json.loads()` sonucunun her zaman dict olmadığını öğrendim
- [x] İkinci generator ile high-risk filtre zinciri kurdum
- [x] Threshold'u hard-code etmedim
- [x] Ayırt edici test verisinin önemini gördüm
- [x] Bozuk JSON vakasında streaming davranışını canlı gördüm
- [x] Pagination'ın `items + next` contract'ını öğrendim
- [x] `next=null → None → STOP` mantığını oturttum
- [x] `urljoin()` relative URL davranışlarını öğrendim
- [x] `Request` ve `urlopen()` ayrımını tekrar ettim
- [x] `Accept` ve `Content-Type` farkını oturttum
- [x] `fetch_json()` ile `iter_assets()` sorumluluklarını ayırdım
- [x] Kontrollü local `mock_api.py` kurdum
- [x] Page 1 → Page 2 → STOP akışını doğruladım
- [x] Eski validation contract'ını yanlış taşıma hatasını fark ettim
- [x] `next` okumak ile state update arasındaki farkı gördüm
- [x] Termination'ı bilerek bozup broken case oluşturdum
- [x] Mock server ile olası sonsuz loop'u üçüncü request'te güvenli şekilde yakaladım
- [x] Finalde doğru akışta üçüncü request oluşmadığını kanıtladım

---

# 🚀 Gün Sonu

> **Bugün iki farklı yerde aynı temel modeli kullandım:**
>
> **Generator'da consumer sıradaki veriyi isteyince state ilerliyor; pagination'da server `next` verince URL state'i ilerliyor.**
>
> İkisinde de kritik nokta:
>
> **Her şeyi önceden hazırlamak yerine, gereken şeyi üret → state'i doğru ilerlet → termination geldiğinde dur.**