---
title: "Gün 40 — Logging, Correlation ve Failure Diagnosis"
tags:
  - coreops
  - day40
  - python
  - logging
  - diagnosis
  - correlation
  - docker
  - postgresql
  - debugging
aliases:
  - "Gün 40 Logging Correlation Failure Diagnosis"
status: completed
---

# 🧠 Gün 40 — Logging, Correlation & Failure Diagnosis

> [!abstract] 🎯 Ana fikir
> Bugün loglara sadece `"hata mesajı"` olarak bakmayı bırakıp, bir işlemin başından sonuna kadar **hikâyesini yeniden kurmak** için kullanmayı öğrendim.
>
> Ana mental modelim:
>
>     Request
>        ↓
>     request_id
>        ↓
>     event zinciri
>        ↓
>     ilk kırılan nokta
>        ↓
>     failure boundary
>        ↓
>     evidence
>        ↓
>     root cause
>
> **ERROR satırını görmek teşhis değildir. O ERROR'a nasıl geldiğimi kanıtlamak teşhistir.**

---

# 📝 Log = Gelişmiş `print()` Değil

`print()` temelde metin basar.

Logging ise sistemde gerçekleşen bir **event'i context'iyle beraber kaydeder.**

Örneğin:

    level=ERROR
    request_id=req-42
    event=db_query_failed
    owner=blue-team

Buradan artık:

| Alan | Cevapladığı soru |
|---|---|
| `timestamp` | Ne zaman oldu? |
| `event` | Ne oldu? |
| `level` | Ne kadar ciddi? |
| `request_id` | Hangi işlemin başına geldi? |
| context | O işlem hakkında başka ne biliyorum? |

> [!important]
> **Log = event kaydı.**

---

# 🏗️ Python Logging Mimarisi

Bugün şu ayrımı netleştirdim:

    Logger
      ↓
    LogRecord
      ↓
    Handler
      ↓
    Formatter
      ↓
    stdout / stderr / file

- **Logger** → event'i logging sistemine gönderir.
- **LogRecord** → event'in bilgi paketidir.
- **Handler** → logun nereye gideceğini belirler.
- **Formatter** → logun nasıl görüneceğini belirler.

Severity tarafında:

    DEBUG    → teşhis ayrıntısı
    INFO     → normal lifecycle
    WARNING  → anormal ama işlem devam ediyor
    ERROR    → operasyon başarısız
    CRITICAL → ciddi sistem problemi

Her şeyi `ERROR` yapmak **TIRT**; o zaman severity'nin hiçbir anlamı kalmıyor.

---

# 🔗 Request ID / Correlation

Birden fazla işlem aynı anda çalışıyorsa timestamp tek başına yeterli değil.

    timestamp
       ↓
    NE ZAMAN?

    request_id
       ↓
    HANGİ İŞLEM?

Aynı saniyede iki request çalışabilir.

Bu yüzden:

> **Timestamp zaman verir, kimlik vermez.**

Her request başında tek bir `request_id` oluşturup bütün lifecycle boyunca aynı ID'yi taşıyorum.

    request_id=A
       │
       ├── request_started
       ├── db_connect_started
       ├── db_query_started
       ├── db_query_ok
       └── request_completed

Farklı request:

    request_id=B
       │
       └── kendi event zinciri

Böylece loglar birbirine karışsa bile hangi satırın hangi işleme ait olduğunu ayırabiliyorum.

---

# 🧰 `LoggerAdapter`

Her log çağrısında:

    extra={"request_id": request_id}

yazmak tekrarlı ve unutmaya açık.

Bu yüzden `LoggerAdapter` ile ortak context'i logger'a bir kere bağladım.

Benim worker'da ortak context:

- `request_id`
- `owner`

oldu.

Sonra her event kendi ekstra bilgisini taşıdı:

    request_started

    db_query_ok
    row_count=2

    db_query_failed
    error_type=UndefinedColumn

> [!note]
> `LoggerAdapter` = aynı contextual bilgiyi bütün loglara tekrar tekrar elle eklememek.

---

# 🐳 Bugünkü Sistem

Labda:

    app container
    Python
       │
       │ psycopg
       ▼
     db:5432
       │
       ▼
    PostgreSQL

kurdum.

Uygulamanın normal lifecycle'ı:

    request_started
          ↓
    db_connect_started
          ↓
      DB connection
          ↓
    db_query_started
          ↓
        SQL query
          ↓
      db_query_ok
          ↓
    request_completed

Compose tarafında `db` hostname'ini kullandım.

App container içinde:

    localhost → app'ın kendisi
    db        → PostgreSQL container

Ayrıca healthcheck sayesinde:

    container running
          ≠
    PostgreSQL hazır

ayrımını tekrar gördüm.

`depends_on + service_healthy` ile app'in DB hazır olmadan başlamamasını sağladım.

---

# 🐞 Yaptığım Hatalar ve Nasıl Düzelttim

## 1. Compose indentation

`app:` yanlış seviyedeydi ve Compose:

    services.db additional properties ...

hatası verdi.

### Düzeltme

`db:` ve `app:` servislerini `services:` altında aynı seviyeye aldım.

> **YAML'da indentation görüntü değil, yapının kendisi.**

---

## 2. `seed.sql` içinde `;` hatası

Şuna benzer yazdım:

    ('blue-team');
    ('red-team');

İlk `;` SQL statement'i bitirdiği için sadece ilk kayıt düzgün işlendi.

Düzelttim:

    ('blue-team'),
    ('red-team');

Mental model:

    , → aynı statement içindeki kayıtları ayır
    ; → statement'i bitir

---

## 3. Seed'i düzeltince DB otomatik güncellenir sandım

**TIRT.**

`/docker-entrypoint-initdb.d/` altındaki init scriptleri her container restart'ında tekrar çalışmıyor.

Database ilk initialize edilirken çalışıyor.

Lab ortamını:

    docker compose down -v

ile sıfırlayıp tekrar initialize ettim.

> [!danger]
> `down -v` veri silebilir. Prod DB'de kafama göre kullanılacak komut değil.

---

## 4. Function signature uyuşmazlığı

Repository bir ara:

    assets_for_owner(owner)

beklerken worker:

    assets_for_owner(connection, owner)

çağırıyordu.

İkisini aynı contract'ta buluşturdum:

    assets_for_owner(connection, owner)

---

## 5. Log sırası gerçek lifecycle'ı yansıtmıyordu

Query başlamadan önce connection kurulmuş olması gerekiyor.

Yanlış bir event sırası bana:

    db_query_started

dedirtebilirken ortada connection bile olmayabilirdi.

Düzelttiğim sıra:

    db_connect_started
          ↓
    get_connection()
          ↓
    db_query_started
          ↓
         query

> [!important]
> **Loglar güzel bir hikâye uydurmamalı; sistemde gerçekten gerçekleşen sırayı anlatmalı.**

---

# ✅ Önce Çalışan Baseline

Broken case oluşturmadan önce sistemi doğru haliyle çalıştırdım.

`blue-team`:

    request_started
          ↓
    db_connect_started
          ↓
    db_query_started
          ↓
    db_query_ok row_count=2
          ↓
    request_completed
          ↓
        exit 0

Sonra tek seferlik başka bir request olarak `red-team` çalıştırdım:

    owner=red-team
    row_count=1

Blue ve red request'lerinin `request_id` değerleri farklıydı.

Böylece pratikte:

    aynı request
        ↓
    aynı request_id

    farklı request
        ↓
    farklı request_id

olduğunu gördüm.

> [!important]
> **Broken case yaratmadan önce çalışan baseline'ı kanıtla.**
>
> Yoksa sistem zaten bozuk muydu, benim yaptığım değişiklik mi bozdu anlayamam.

---

# 💣 Broken Case — SQL'i Bilerek Bozdum

Çalışan query'deki:

    assets.hostname

alanını bilerek:

    assets.hostname_broken

yaptım.

Böyle bir column olmadığı için gerçek log:

    request_started
          ↓
    db_connect_started
          ↓
    db_query_started
          ↓
    db_query_failed
          ↓
    error_type=UndefinedColumn

şeklinde oluştu.

Process de:

    exit code = 1

ile kapandı.

Exit code'u ayrıca:

    docker inspect day40-app-1 --format '{{.State.ExitCode}}'

ile kontrol edip gerçekten `1` olduğunu kanıtladım.

---

# 🔎 Diagnosis — Asıl Öğrendiğim Kısım

Buradaki en önemli hata şu olurdu:

> `db_query_failed gördüm → PostgreSQL çöktü.`

**TIRT.**

Benim elimdeki kanıtlar:

    request_started        ✅
    db_connect_started     ✅
    db_query_started       ✅
    db_query_failed        ❌
    UndefinedColumn
    exit=1

Connection aşamasını geçmişim.

Dolayısıyla:

- DB'ye ulaşılamıyor ❌
- PostgreSQL kesin down ❌
- connection kurulamadı ❌

diyemem.

Son başarılı event:

    db_query_started

İlk başarısız event:

    db_query_failed

Aradaki mekanizma:

    SQL QUERY EXECUTION

Bu yüzden diagnosis:

    affected_request_id:
    5ddc819e-...

    last_successful_event:
    db_query_started

    first_failed_event:
    db_query_failed

    error_type:
    UndefinedColumn

    failure_boundary:
    SQL query execution

oldu.

> [!danger]
> **ERROR SATIRI ≠ ROOT CAUSE**
>
> Error satırı sadece araştırmaya nereden devam edeceğimi söyler.

---

# 🧭 Diagnosis Sıram

Bir hata olduğunda artık:

    Hangi request?
          ↓
    Event zinciri ne?
          ↓
    Son başarılı event?
          ↓
    İlk başarısız event?
          ↓
    Failure boundary?
          ↓
    Error / exception ne?
          ↓
    Diğer servis logları?
          ↓
    Root cause

şeklinde ilerleyeceğim.

Rastgele:

> "DB bozuk herhalde."

demek yok.

---

# 🔍 Compose Loglarıyla Çalışmak

Kullandığım önemli komut mantıkları:

    docker compose logs --timestamps
    → ne zaman?

    docker compose logs --since 5m
    → zaman aralığını daralt

    docker compose logs --tail 50
    → son N log

    docker compose logs -f
    → canlı takip

Request ID biliyorsam:

    docker compose logs ...
        |
        grep 'request_id=...'

ile tek bir request'in bütün hikâyesini ayırabiliyorum.

Bu correlation'ın asıl operasyonel değeri.

---

# 🔧 Fix + Regression Test

Broken SQL'i tekrar:

    assets.hostname

haline getirdim.

Fix sonrasında lifecycle tekrar:

    request_started
          ↓
    db_connect_started
          ↓
    db_query_started
          ↓
    db_query_ok row_count=2
          ↓
    request_completed
          ↓
        exit 0

oldu.

Yani sadece:

> "Düzelttim galiba."

demedim.

Broken:

    db_query_failed
    UndefinedColumn
    exit 1

Fixed:

    db_query_ok
    request_completed
    exit 0

karşılaştırmasını yaptım.

Bu benim **regression kanıtım** oldu.

Fixed logları da:

    docker compose logs --timestamps --tail 50 app > evidence/fixed.log

ile evidence olarak kaydettim.

---

# 🧠 Kafaya Kazı

> [!important]
> **Log = event kaydı.**

> [!important]
> **Timestamp = ne zaman?**

> [!important]
> **Request ID = hangi işlem?**

> [!important]
> **Aynı request → aynı request_id.**

> [!important]
> **Event = ne oldu, severity = ne kadar ciddi, context = kimin başına geldi?**

> [!important]
> **`db_query_failed` PostgreSQL çöktü demek değildir.**

> [!important]
> **ERROR satırı root cause değildir.**

> [!important]
> **Log event sırası gerçek program lifecycle'ını yansıtmalı.**

> [!important]
> **Önce çalışan baseline'ı kanıtla, sonra sistemi kontrollü şekilde boz.**

> [!important]
> **Fix yaptıktan sonra regression testiyle tekrar başarıyı kanıtla.**

---

# 📌 30 Saniyelik Özet

    NORMAL BASELINE
          ↓
    request_id oluştur
          ↓
    event zincirini logla
          ↓
    sistemi bilerek boz
          ↓
    broken request'i seç
          ↓
    last successful event
          ↓
    first failed event
          ↓
    failure boundary
          ↓
    error/evidence
          ↓
         FIX
          ↓
    regression test
          ↓
      tekrar başarı ✅

---

# ✅ Günün Kazanımları

- [x] Logging ile `print()` arasındaki gerçek farkı oturttum
- [x] Logger / LogRecord / Handler / Formatter ayrımını öğrendim
- [x] Event, severity ve context ayrımını yaptım
- [x] Request ID / correlation mantığını kullandım
- [x] Timestamp'in kimlik olmadığını gördüm
- [x] `LoggerAdapter` ile ortak context taşıdım
- [x] Compose + PostgreSQL + Python labını kurdum
- [x] Compose indentation hatasını çözdüm
- [x] Seed SQL'deki `;` hatasını çözdüm
- [x] PostgreSQL init script lifecycle'ını öğrendim
- [x] Function signature uyuşmazlığını düzelttim
- [x] Log sırasını gerçek lifecycle'a göre düzelttim
- [x] Blue/red request'lerini ayrı correlation ID'lerle takip ettim
- [x] Çalışan baseline oluşturdum
- [x] SQL'i bilerek `UndefinedColumn` ile kırdım
- [x] Exit code `1` ile failure'ı ayrıca kanıtladım
- [x] Last successful / first failed event ile failure boundary buldum
- [x] Hatayı düzelttim
- [x] Regression testinde tekrar `db_query_ok + request_completed + exit 0` aldım
- [x] Diagnosis ve fixed logları evidence olarak sakladım

---

# 🚀 Gün Sonu

> **Bugün `"çalıştı / çalışmadı"` seviyesinden çıktım. Önce çalışan sistemi kanıtladım, sistemi kontrollü şekilde kırdım, request bazında loglardan nerede kırıldığını buldum, kanıtlarla failure boundary çıkardım, hatayı düzelttim ve regression testiyle sistemin tekrar doğru çalıştığını doğruladım.**