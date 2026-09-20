---
title: "Gün 49 — Build-Time Dependency, Multi-Stage ve Non-Root Runtime"
tags:
  - coreops
  - day49
  - docker
  - dockerfile
  - compose
  - build-cache
  - multi-stage
  - non-root
  - least-privilege
aliases:
  - "Gün 49 Docker Multi-Stage Non-Root Runtime"
status: completed
---

# 🐳 Day 49 — Build-Time Dependency, Multi-Stage & Non-Root Runtime

> [!note] 20 Eylül arşiv denetimi
> Bu labda `/usr/local` bütünü kopyalanıyor; bu yol Python yorumlayıcısı ve başka dosyaları da içerir. Multi-stage geçişi çalışıyor, fakat “yalnız minimum dependency” veya “ölçülmüş image küçülmesi” kanıtlanmış değildir. Host bind mount kullanıldığında image içindeki chown host dizininin izinlerini belirlemez.

> [!abstract] 🎯 Ana fikir
> Bugün Docker'da image'ı sadece **çalışabilen** değil, **çalışmaya hazır ve minimum yetkili** hale getirdim.
>
>     BLOK 1
>     dependency
>         ↓
>     BUILD TIME
>         ↓
>       IMAGE
>         ↓
>     container açılır
>         ↓
>     uygulama direkt çalışır
>
>
>     BLOK 2
>       BUILDER
>         ↓
>     gerekli artifact
>         ↓
>       RUNTIME
>         ↓
>      appuser
>         ↓
>     least privilege
>
> Day49'un ana ayrımı:
>
> **Image hazırlamak ≠ Container çalıştırmak.**

---

# 1️⃣ BLOK 1 — Dependency'yi Runtime'dan Build-Time'a Taşımak

Day41'de:

    container başlıyor
        ↓
    pip install psycopg
        ↓
    uygulama başlıyor

modelini kullanıyordum.

Problem:

    startup
      ↓
    DNS
    network
    PyPI
    download
    install
      ↓
    uygulama

Yani container'ın başlaması gereksiz yere dış dünyaya bağlıydı.

Yeni model:

    docker build
        ↓
    RUN pip install
        ↓
    dependency IMAGE içinde
        ↓
    docker compose up
        ↓
    CMD
        ↓
    uygulama direkt başlar

> **Hazırlık build-time'da, çalışma runtime'da.**

---

# 🧠 `RUN` vs `CMD`

    RUN
    → BUILD TIME
    → image hazırlanırken gerçekten çalışır


    CMD
    → RUNTIME
    → container başlatıldığında kullanılacak
      varsayılan komutu tanımlar

Örneğin:

    RUN pip install -r requirements.txt

dependency'yi image filesystem'ine kurar.

Ama:

    CMD ["python", "src/check_owner.py", "blue-team"]

build sırasında Python scriptini çalıştırmaz.

Sadece:

> "Bu image normal şekilde çalıştırılırsa bunu başlat."

der.

Mental model:

    RUN
    → arabaya fabrikada motoru tak

    CMD
    → arabaya binince motoru çalıştır

---

# 📦 `requirements.txt` + Docker Cache

Doğru sıra:

    COPY requirements.txt .
          ↓
    RUN pip install -r requirements.txt
          ↓
    COPY src/ ./src/

Sebep:

    requirements aynı
          ↓
    dependency layer CACHE ✅

    source değişti
          ↓
    sadece source COPY tekrar

Bunu gerçek build'de gördüm.

İlk build:

    pip install → ~2.5s

Sadece `app.py` değiştikten sonraki build:

    CACHED COPY requirements
    CACHED RUN pip install
    COPY app.py yeniden

Toplam build:

    ~3.6s
      ↓
    ~0.2s

Yani pahalı ve az değişen dependency adımlarını yukarı koymak cache avantajı sağlıyor.

---

# ⚠️ İki Farklı Cache

Bunları da ayırdım:

    pip install --no-cache-dir
    → pip'in kendi package cache'i


    docker build --no-cache
    → Docker build layer cache'i

Aynı şey değiller.

---

# 🐳 Day41 Uygulamasını Dockerfile'a Taşıdım

Yeni yapı:

    Blok1/
    ├── Dockerfile
    ├── requirements.txt
    ├── compose.yaml
    ├── src/
    │   ├── check_owner.py
    │   └── repository.py
    └── sql/
        ├── schema.sql
        └── seed.sql

Final Dockerfile:

    FROM python:3.13-slim

    WORKDIR /lab

    COPY requirements.txt .

    RUN pip install --no-cache-dir -r requirements.txt

    COPY src/ ./src/

    CMD ["python", "src/check_owner.py", "blue-team"]

Buradaki kritik nokta:

    CMD içinde pip install ❌

Dependency zaten image'ın içinde.

---

# 🧩 Dockerfile vs Compose vs Volume

Burayı da netleştirdim:

    Dockerfile
    → IMAGE NASIL hazırlanacak?


    Compose
    → CONTAINER'LAR NASIL birlikte çalışacak?


    Volume / bind mount
    → Compose'un kullanabileceği özelliklerden biri

Yani:

> **Compose = volume yapan şey**

demek **TIRT.**

Bu labda Compose:

    app image build
    postgres container
    app container
    network
    environment
    healthcheck
    depends_on
    bind mount

işlerini organize etti.

---

# 🗄️ App Source vs SQL

App source:

    COPY src/ ./src/

ile doğrudan **image'ın içine** girdi.

SQL dosyaları ise app image'a girmedi.

Onlar:

    ./sql/schema.sql
          ↓ bind mount
    PostgreSQL init directory

şeklinde DB container'a bağlandı.

Kısa:

    src/
    → app image


    sql/
    → db bind mount

---

# 🆚 Named Volume / Bind Mount

Named volume:

    app_data:/data

ve top-level:

    volumes:
      app_data:

gerekir.

Bind mount:

    ./sql/schema.sql:/container/path

Host path kullandığı için ayrıca top-level named volume tanımı gerekmez.

---

# 🩺 Healthcheck

DB için:

    pg_isready

kullandım.

Çünkü:

    container running
          ≠
    PostgreSQL ready

Compose akışı:

    db başlar
       ↓
    healthcheck
       ↓
    Healthy
       ↓
    app başlayabilir

---

# ✅ BLOK 1 Kanıt Zinciri

    docker compose config
        ↓
    Compose syntax ✅

    docker compose build --no-cache app
        ↓
    RUN pip install gerçekten çalıştı ✅

    docker compose up app
        ↓
    DB Healthy ✅

        ↓
    db_connect_ok ✅

        ↓
    query_ok ✅

        ↓
    blue-team assets=2 ✅

        ↓
    exit code 0 ✅

Runtime loglarında:

    pip install
    Collecting psycopg
    Installing...

yoktu.

Ama:

    db_connect_ok
    query_ok

vardı.

Yani dependency runtime'da kurulmadı; image'ın içinden geldi.

---

# 🐞 BLOK 1 Hatalarım

### `requirements.txt` typo

Yanlış dosya adı yazdım.

Docker:

    requirements.txt

arıyor ama dosya başka isimdeyse build context'te yokmuş gibi davranır.

---

### `FROM` syntax

Yanlış:

    FROM python 3.13-slim

Doğru:

    FROM python:3.13-slim

Image ile tag arasında:

    :

var.

---

### `COPY` hedefini unuttum

Yanlış:

    COPY requirements.txt

Doğru:

    COPY requirements.txt .

`COPY`:

    source + destination

ister.

---

### CMD path'i yanlış yazdım

Yanlış:

    python check_owner.py

Ama gerçek yapı:

    /lab/src/check_owner.py

Doğru:

    python src/check_owner.py blue-team

Ayrıca `blue-team` argümanını da unutmamam gerekiyordu.

---

### Compose environment syntax'ını karıştırdım

Mapping kullanacaksam:

    environment:
      POSTGRES_USER: coreops

şeklinde olmalı.

List ile mapping syntax'ını birbirine yapıştırmak **TIRT.**

---

# 2️⃣ BLOK 2 — Multi-Stage Build

Tek-stage image çalışıyordu.

Ama artık:

    BUILDER
       ↓
    sadece gerekli artifact
       ↓
    temiz RUNTIME

modeline geçtim.

Builder:

    FROM python:3.13-slim AS builder

    WORKDIR /lab

    COPY requirements.txt .

    RUN pip install --no-cache-dir -r requirements.txt

Görevi:

    requirements
        ↓
    pip install
        ↓
    dependency çıktıları

---

# 🎯 Builder'ı Tek Başına Test Ettim

    docker build --target builder ...

Buradaki:

    --target builder

demek:

> Dockerfile'ı `builder` stage'ine kadar build et.

Sonra builder image içinde:

    import psycopg

test ettim.

Sonuç:

    psycopg 3.3.5 ✅

Build başarılı diye varsaymadım; artifact'i ayrıca kanıtladım.

---

# 🧠 `docker run` vs `docker exec`

Burada da karıştırdım.

    docker run
    → IMAGE'dan YENİ container oluştur


    docker exec
    → zaten ÇALIŞAN container içinde komut çalıştır

Builder container sürekli çalışan bir container değildi.

Bu yüzden test için:

    docker run --rm ...

doğru seçimdi.

---

# 🌍 Host / Builder / Runtime

Artık bunları üç farklı filesystem olarak düşünüyorum:

    HOST
    → Mac


    BUILDER
    → Linux filesystem


    RUNTIME
    → başka Linux filesystem

Normal:

    COPY requirements.txt .
    HOST → STAGE

Ama:

    COPY --from=builder ...
    BUILDER → RUNTIME

---

# 🧱 `FROM builder` vs `COPY --from=builder`

En kritik multi-stage ayrımı:

    FROM builder AS runtime
    → builder'ın TAMAMINI temel al


    COPY --from=builder
    → builder'dan SEÇTİĞİM şeyi taşı

Ben:

    temiz python runtime
           +
    gerekli dependency artifact

istediğim için:

    FROM python:3.13-slim AS runtime

kullandım.

Sonra:

    COPY --from=builder /usr/local/ /usr/local/

ile sadece gerekli dependency çıktısını taşıdım.

---

# 🐞 `FROM` ile Path Kullanmaya Çalıştım

Bir ara kafamda:

    FROM builder/usr/local/...

gibi bir şey oluştu.

**TIRT.**

`FROM`:

    image
    veya
    stage adı

ister.

Filesystem path taşıma işi:

    COPY --from=

ile yapılır.

---

# 📦 Neden `/usr/local` Taşıdım?

`psycopg`:

    /usr/local/lib/python3.13/site-packages

altındaydı.

Ama sadece `site-packages` yerine:

    /usr/local/

taşıdım.

Çünkü pip bazı dependency'ler için:

    /usr/local/bin

gibi ek runtime artifact'leri de oluşturabilir.

Doğru eşleşme:

    builder:/usr/local/
             ↓
    runtime:/usr/local/

Yanlış düşündüğüm:

    COPY --from=builder /usr/local/ .

Bu dependency'leri `/lab` altına yanlış şekilde dağıtırdı.

---

# 🏗️ İlk Çalışan Multi-Stage Yapı

    BUILDER
    python:3.13-slim
        ↓
    pip install
        ↓
    /usr/local
        │
        │ COPY --from
        ▼
    RUNTIME
    python:3.13-slim
        ↓
    /usr/local
        +
    src/
        +
    CMD

Runtime test:

    import psycopg
    → 3.3.5 ✅

Filesystem:

    src/ ✅
    requirements.txt ❌

Bu çok önemliydi.

`requirements.txt` builder'daydı ama runtime'a taşınmadı.

Yani stage filesystem'leri otomatik birleşmiyor.

---

# 🔀 CMD Override

Dockerfile'da:

    CMD ["python", "src/check_owner.py", "blue-team"]

olmasına rağmen:

    docker run IMAGE find ...

çalıştırabildim.

Çünkü image adından sonra verdiğim komut o run için:

    CMD'yi override eder

Bu sayede image içinde debug/inspection komutları çalıştırabildim.

---

# 🔐 Non-Root Runtime

Multi-stage çalıştıktan sonra runtime hâlâ root'tu.

Yeni hedef:

    runtime process
          ↓
       appuser
      uid=10001

Ayrıca:

    /lab/runtime
    → writable ✅


    /lab/src
    → writable değil ✅

Bunun için runtime stage'e `appuser` ekledim ve yalnızca:

    /lab/runtime

klasörünün ownership'ini ona verdim.

Sonra:

    USER appuser

ile runtime process'lerini non-root çalıştırdım.

---

# 🛡️ Least Privilege

Şunu yapabilirdim:

    chown -R appuser /lab

Ama bu:

    /lab/src

kaynak kodunu da writable yapardı.

Gereksiz yetki.

Doğru:

    /lab/src
    → source
    → write yok


    /lab/runtime
    → runtime data
    → write var

Prensip:

> **Uygulamaya sadece gerçekten ihtiyaç duyduğu yetkiyi ver.**

---

# 🧪 Security Testleri

### Root değil mi?

    id

Çıktı:

    uid=10001(appuser)

✅

### Runtime path yazılabilir mi?

    touch /lab/runtime/test.txt

✅

Dosya owner:

    appuser appuser

### Source değiştirilebilir mi?

    touch /lab/src/should-fail.txt

Sonuç:

    Permission denied

✅

Burada `Permission denied` hata değil.

**Beklediğim güvenlik davranışı.**

---

# 🔁 Final Regression Test

Security hardening sonrası tekrar:

    docker compose up --build

çalıştırdım.

Sonuç:

    PostgreSQL Healthy ✅
    db_connect_ok ✅
    query_ok ✅
    row_count=2 ✅
    blue-team assets=2 ✅
    exit code 0 ✅

Yani:

> **Güvenliği artırdım ama uygulamanın çalışan davranışını bozmadım.**

Final kanıt zinciri de non-root UID, writable runtime path ve yazılamayan source path dahil başarılıydı.

---

# 🐞 BLOK 2 Hatalarım

- `COPY requirements.txt` yazıp destination'ı unuttum.
- `requirements.txt` dosya adını typo yaptım.
- `docker run` ile `docker exec`i karıştırdım.
- Builder image adını yanlış yazdım.
- `FROM` içine filesystem path vermeye çalıştım.
- `FROM builder` ile `COPY --from=builder` farkını karıştırdım.
- `/usr/local`ı runtime'da `.` altına kopyalamaya çalıştım.
- CMD'de `/lab/src/check_owner.py` yolunu unuttum.

---

# 🧠 Kafaya Kazı

> [!tip]
> **RUN = BUILD TIME**

> [!tip]
> **CMD = RUNTIME default command**

> [!tip]
> **Dependency zorunluysa image'ın içinde hazır olmalı.**

> [!tip]
> **Dockerfile = image nasıl yapılacak?**

> [!tip]
> **Compose = container'lar nasıl birlikte çalışacak?**

> [!tip]
> **Volume = Compose'un özelliklerinden sadece biri.**

> [!tip]
> **Normal COPY = HOST → STAGE**

> [!tip]
> **COPY --from = STAGE → STAGE**

> [!danger]
> **FROM builder = builder'ın tamamını miras al**

> [!tip]
> **COPY --from=builder = sadece ihtiyacım olan artifact'i seç**

> [!tip]
> **docker run = yeni container**

> [!tip]
> **docker exec = çalışan container**

> [!danger]
> **uid=0 = root**

> [!tip]
> **uid=10001(appuser) = non-root**

> [!danger]
> **Permission denied her zaman problem değildir.**
>
> Kaynak koduna yazmayı engelliyorsam başarı kanıtı olabilir.

---

# 📌 30 Saniyelik Özet

    BLOK 1

    requirements.txt
          ↓
    RUN pip install
          ↓
       IMAGE
          ↓
        CMD
          ↓
     CONTAINER
          ↓
    uygulama direkt çalışır


    CACHE

    requirements aynı
          ↓
    pip layer cached

    source değişti
          ↓
    sadece source yeniden COPY


    BLOK 2

           BUILDER
              ↓
        pip install
              ↓
         /usr/local
              ↓
    COPY --from=builder
              ↓
           RUNTIME
              ↓
            src/
              ↓
          appuser
              ↓
       çalışan uygulama


    PERMISSIONS

    /lab/runtime
    → writable ✅

    /lab/src
    → writable değil ✅


    FINAL

    DB healthy
        ↓
    db_connect_ok
        ↓
    query_ok
        ↓
    2 records
        ↓
    exit 0 ✅

---

# ✅ Günün Kazanımları

- [x] Build-time / runtime ayrımını oturttum
- [x] `RUN` ve `CMD` farkını netleştirdim
- [x] Runtime `pip install` yaklaşımını kaldırdım
- [x] Dependency'leri image build sırasında kurdum
- [x] Docker build cache davranışını canlı gördüm
- [x] pip cache ile Docker layer cache'i ayırdım
- [x] Dockerfile / Compose / volume rollerini ayırdım
- [x] App source'u image içine aldım
- [x] SQL dosyalarını DB'ye bind mount ettim
- [x] PostgreSQL healthcheck kullandım
- [x] Runtime'da `pip install` olmadığını kanıtladım
- [x] Multi-stage builder/runtime yapısı kurdum
- [x] `--target builder` ile stage'i ayrı test ettim
- [x] `COPY --from=builder` mantığını oturttum
- [x] Host / builder / runtime filesystem'lerini ayırdım
- [x] Runtime'da dependency var, builder dosyası yok diye doğruladım
- [x] Container'ı root yerine `appuser` ile çalıştırdım
- [x] UID 10001 olduğunu doğruladım
- [x] Sadece `/lab/runtime` path'ini writable yaptım
- [x] `/lab/src` yazma denemesinin fail olmasını güvenlik kanıtı olarak kullandım
- [x] Non-root değişikliğinden sonra regression testi yaptım

---

# 🚀 Gün Sonu

> **Day49'da image'ın sadece çalışan bir paket değil, runtime'a hazır bir ürün olması gerektiğini oturttum.**
>
> İlk aşamada:
>
> **Dependency'yi runtime'dan build-time'a taşıdım.**
>
> Sonra:
>
> **Builder'da hazırlayıp yalnızca gerekli artifact'leri temiz runtime'a taşıdım.**
>
> Son olarak:
>
> **Runtime'ı root'tan çıkarıp yalnızca gereken filesystem yetkilerini verdim.**
>
> Final model:
>
> **Build'te hazırla → runtime'a sadece gerekeni taşı → minimum yetkiyle çalıştır.**
