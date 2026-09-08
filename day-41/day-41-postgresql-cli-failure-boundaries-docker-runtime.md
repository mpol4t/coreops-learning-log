---
title: "Gün 41 — PostgreSQL CLI, Failure Boundaries ve Docker Runtime"
tags:
  - coreops
  - day41
  - python
  - postgresql
  - docker
  - logging
  - cli
  - debugging
  - psycopg
aliases:
  - "Gün 41 PostgreSQL CLI Failure Boundaries Docker Runtime"
status: completed
---

# 🐘 Gün 41 — PostgreSQL CLI, Failure Boundaries & Docker Runtime

> [!abstract] 🎯 Ana fikir
> Bugün küçük bir CLI programında şu zinciri bağımsız olarak kurdum:
>
>     CLI input
>        ↓
>     PostgreSQL connection
>        ↓
>     Repository query
>        ↓
>     Sonuç
>        ↓
>     Structured logging
>
> Asıl öğrendiğim şey ise sadece `"başarılı / başarısız"` ayrımı değil:
>
> **Hata tam olarak hangi boundary'de oluştu?**

---

# 🧩 Programın Akışı

Programı:

    python check_owner.py blue-team

şeklinde çalıştırıyorum.

Akış:

    CLI
     ↓
    owner
     ↓
    DB connection
     ↓
    parameterized query
     ↓
    rows
     ↓
    kullanıcı çıktısı + log

Repository tarafında owner değerini SQL'e gömmek yerine:

    WHERE owners.name = %s

ve:

    (owner,)

şeklinde ayrı gönderiyorum.

> [!important]
> **SQL yapısı ile kullanıcı verisini birbirinden ayrı tutuyorum.**

---

# 📜 Logging Lifecycle

Başarılı durumda event zincirim:

    request_started
          ↓
    db_connect_started
          ↓
    db_connect_ok
          ↓
    query_started
          ↓
    query_ok
          ↓
    request_completed

Loglarda ayrıca:

- `request_id`
- `owner`
- `row_count`
- `error_type`

taşıyorum.

Böylece sadece hata olduğunu değil, **hangi aşamada ve hangi request'te olduğunu** görebiliyorum.

---

# 🚨 Günün En Önemli Ayrımı

Başta connection ve query'yi aynı `try/except` içine koymuştum.

Yaklaşık:

    try:
        connection = get_connection()
        rows = assets_for_owner(...)

    except:
        query_failed

Bu **TIRT**.

Çünkü connection kurulurken hata olursa query daha başlamadan:

    query_failed

loglamış olacaktım.

Yani log teknik olarak yalan söyleyecekti.

## Düzeltme

Boundary'leri ayırdım:

    DB CONNECTION
       │
       ├── failure
       │     ↓
       │ db_connect_failed
       │
       └── success
             ↓
         db_connect_ok
             ↓
           QUERY
             │
             ├── failure
             │     ↓
             │ query_failed
             │
             └── success
                   ↓
                query_ok

> [!important]
> **Log, hatanın fark edildiği gerçek katmanı söylemeli.**

---

# ✅ Test A — Owner Var + Asset Var

`blue-team` için çalıştırdım.

Sonuç:

    query_ok
    row_count=2

Kullanıcı çıktısı:

    owner=blue-team assets=2
    hostname=blue-web-01 risk=20
    hostname=blue-db-01 risk=60

Yani:

    connection ✅
    query      ✅
    rows       2
    result     ✅

---

# ✅ Test B — Owner Var + Asset Yok

`empty-team` için sorgu çalıştırdım.

Sonuç:

    query_ok
    row_count=0

Çıktı:

    owner=empty-team assets=0

Buradaki kritik ayrım:

    rows = []

demek:

    DB connection ✅
    SQL çalıştı    ✅
    DB cevap verdi ✅
    kayıt sayısı   0

demek.

> [!important]
> **0 satır dönmesi query failure değildir.**

Query başarılı şekilde:

> "Eşleşen kayıt yok."

demiş olabilir.

---

# 💥 Test C — Connection Failure

Bu sefer yalnız o çalıştırma için:

    DB_PORT=9999

verdım.

Akış:

    request_started
          ↓
    db_connect_started
          ↓
    db_connect_failed
          ↓
    OperationalError
          ↓
       exit 1

Burada özellikle:

    db_connect_ok ❌
    query_started ❌
    query_failed  ❌

görmedim.

Çünkü query aşamasına hiç ulaşmadım.

> **Connection failure ≠ Query failure**

---

# 🐞 Hatalarım ve Nasıl Düzelttim

## 1. Dosya adını typo ile oluşturdum

Gerçek dosya:

    chechk_owner.py ❌

Ben çağırıyordum:

    check_owner.py

Sonuç:

    No such file or directory

Düzelttim:

    check_owner.py ✅

### Ders

`Errno 2` görünce önce kodu suçlamak yerine:

    pwd
    ls
    ls -l

ile:

> Neredeyim, dosya burada mı, adı doğru mu?

kontrol et.

---

## 2. Connection ve Query failure'ı aynı hata gibi logladım

Connection patlasa bile:

    query_failed

üretecek yapı kurmuştum.

### Düzeltme

İki ayrı boundary:

    connection try/except
    query try/except

### Ders

> **Hata mesajı gerçek failure layer'ı temsil etmeli.**

---

## 3. Host environment ile Container environment'ı karıştırdım

Mac'te:

    env | grep '^DB_'

boştu.

Ama container içinde:

    DB_HOST=db
    DB_PORT=5432
    DB_NAME=coreops
    ...

vardı.

Mental model:

    Mac process environment
             ≠
    Container process environment

Environment variable Docker'a değil, **çalışan process'e** aittir.

---

## 4. `docker compose exec` ile çalışmayan container'a girmeye çalıştım

Kullandım:

    docker compose exec app ...

ama `app` running değildi.

Sonuç:

    service "app" is not running

### Öğrendiğim

    exec
    → zaten çalışan container içinde komut çalıştır

    run
    → service config'inden yeni geçici container oluştur

Benim CLI tek seferlik olduğu için:

    docker compose run --rm app ...

daha mantıklı.

---

## 5. Mac `.venv` ile Docker Python environment'ını karıştırdım

Container:

    import psycopg

dediğinde:

    ModuleNotFoundError

aldım.

Mac'teki `.venv` içinde paket olsa bile container bunu görmez.

Mental model:

    Mac .venv
       │
       X
       │
    Docker Python

> **Host Python packages ≠ Container Python packages**

---

## 6. `docker compose run` varsayılan `command:`ı override etti

Compose'ta normalde:

    pip install psycopg
        ↓
    python ...

çalışıyordu.

Ama ben:

    docker compose run --rm app python src/check_owner.py ...

yazınca service'in varsayılan `command:`ını değiştirmiş oldum.

Sonuç:

    pip install çalışmadı
        ↓
    psycopg yok
        ↓
    ModuleNotFoundError

Lab için:

    sh -c "pip install ... && python ..."

ile çözdüm.

> [!warning]
> Gerçek projede her container başlatıldığında `pip install` yapmak **TIRT**.
>
> Dependency image build aşamasında Dockerfile içine alınmalı.

---

## 7. `rows=[]` sonucunu hata sanmamak

    fetchall() == []

şu anlama gelmez:

    query failed ❌

Şu anlama gelebilir:

    query başarılı ✅
    eşleşen kayıt yok ✅

Bu ayrımı netleştirdim.

---

# 🧹 Connection Cleanup

Query başarılı olsa da patlasa da connection açık kalmasın diye:

    finally:
        connection.close()

mantığını kullandım.

Mental model:

    QUERY
     /  \
    /    \
   ✅    ❌
    \    /
     \  /
    finally
       ↓
    connection.close()

> **Cleanup başarı durumuna bağlı olmamalı.**

---

# 🐳 Docker Runtime Mental Modeli

Container içindeki gerçek ortamı ayrıca kontrol ettim:

    docker compose run --rm app pwd
    → /lab

    docker compose run --rm app ls
    → src

Environment:

    DB_HOST=db
    DB_PORT=5432
    DB_NAME=coreops
    DB_USER=coreops
    DB_PASSWORD=coreops

Network:

    app container
         ↓
      DB_HOST=db
         ↓
     Compose DNS
         ↓
     db container
         ↓
    PostgreSQL :5432

Host tarafından bağlanmak ise farklı:

    Mac
     ↓
    localhost:<published-port>

Yani:

    container → container
    db:5432

ile:

    host → container
    localhost:<port>

aynı bağlantı yolu değil.

---

# ⚠️ Küçük Ama Önemli Ayrım

Şu komut:

    docker compose config --services

bana:

> Hangi servisler Compose dosyasında tanımlı?

sorusunun cevabını verir.

Ama:

    docker compose ps

bana:

> Şu anda hangi container'lar çalışıyor?

sorusunun cevabını verir.

Yani:

    service defined
         ≠
    container running

---

# 🔁 Test DB Reproducibility

Bugün kendime şu soruyu sordum:

> Boş bir test database alsam repo içindeki dosyalardan tekrar oluşturabilir miyim?

Cevap:

# EVET ✅

Çünkü elimde:

    schema.sql
       ↓
    owners + assets tabloları

ve:

    seed.sql
       ↓
    başlangıç verileri

var.

Mental model:

    boş DB
      ↓
    schema.sql
      ↓
    tablolar
      ↓
    seed.sql
      ↓
    başlangıç state'i

> [!important]
> `/docker-entrypoint-initdb.d/` scriptleri her restart'ta değil, yeni/boş data directory ilk initialize edilirken çalışır.

---

# 📊 Üç Ana Davranış

| Durum | Connection | Query | Rows | Sonuç |
|---|---|---|---:|---|
| `blue-team` | ✅ | ✅ | 2 | `assets=2` |
| `empty-team` | ✅ | ✅ | 0 | `assets=0` |
| `DB_PORT=9999` | ❌ | çalışmadı | — | `db_connect_failed`, exit `1` |

Bu tablo bugünün ana mantığını tek başına özetliyor.

---

# 🧠 Kafaya Kazı

> [!tip]
> **Connection failure ile Query failure aynı şey değildir.**

> [!tip]
> **0 row = başarılı sorgunun geçerli sonucu olabilir.**

> [!tip]
> **Environment variable çalışan process'e aittir.**

> [!tip]
> **Host environment ≠ Container environment.**

> [!tip]
> **Mac `.venv` ≠ Docker Python environment.**

> [!tip]
> **`exec` çalışan container ister, `run` yeni container oluşturur.**

> [!tip]
> **`docker compose run ... COMMAND`, service'in varsayılan command'ını override edebilir.**

> [!tip]
> **Containerlar arasında Compose service adı DNS hostname olarak kullanılabilir.**

> [!tip]
> **Log, gerçek failure boundary'yi doğru anlatmalı.**

---

# 📌 30 Saniyelik Özet

    CLI input
       ↓
    config/env
       ↓
    DB connection
       ↓
    repository query
       ↓
    result
       ↓
    logging/output


    CONNECTION PATLAR
          ↓
    db_connect_failed


    QUERY PATLAR
          ↓
      query_failed


    QUERY → []
          ↓
    başarı, 0 kayıt


    HOST ENV
       ≠
    CONTAINER ENV


    HOST PYTHON
       ≠
    CONTAINER PYTHON


    exec
    → çalışan container

    run
    → yeni geçici container

---

# ✅ Günün Kazanımları

- [x] CLI → PostgreSQL → Repository zincirini kurdum
- [x] Parameterized query kullandım
- [x] Structured logging lifecycle oluşturdum
- [x] Connection ve query failure boundary'lerini ayırdım
- [x] `blue-team` için 2 kayıtla başarılı testi yaptım
- [x] `empty-team` için 0 kayıt durumunun başarılı olduğunu kanıtladım
- [x] Yanlış port ile gerçek connection failure oluşturdum
- [x] `OperationalError + exit 1` aldım
- [x] Dosya adı typo hatasını çözdüm
- [x] Host/container environment ayrımını gördüm
- [x] `exec` / `run` farkını uyguladım
- [x] Host `.venv` / Docker Python ayrımını gördüm
- [x] Compose `command:` override davranışını öğrendim
- [x] Connection cleanup için `finally` kullandım
- [x] Compose DNS ile `db:5432` bağlantısını doğruladım
- [x] Test DB'nin repo içinden yeniden üretilebilir olduğunu doğruladım

---

# 🚀 Gün Sonu

> **Bugün `"program patladı"` demek yerine hangi boundary'nin patladığını ayırmayı öğrendim: config mi, connection mı, query mi, yoksa sonuç sadece 0 kayıt mı? Aynı zamanda Docker'da host ve container'ın environment, Python paketleri ve runtime açısından ayrı dünyalar olduğunu uygulamalı olarak gördüm.**