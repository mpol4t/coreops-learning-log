---
title: "Gün 46 — Docker Persistence ve PostgreSQL Backup / Restore"
tags:
  - coreops
  - day46
  - docker
  - volume
  - bind-mount
  - postgresql
  - backup
  - restore
  - pg-dump
aliases:
  - "Gün 46 Docker Persistence PostgreSQL Backup Restore"
status: completed
---

# 💾 Day 46 — Docker Persistence & PostgreSQL Backup / Restore

> [!abstract] 🎯 Ana fikir
> Bugün iki şeyi kesin olarak birbirinden ayırdım:
>
>     VOLUME
>     → çalışan database'in kalıcı storage'ı
>
>     BACKUP
>     → geçmiş bir database state'ini yeniden oluşturabilmek için ayrı kopya
>
> Ana zincir:
>
>     ÇALIŞAN DB
>         ↓
>       volume
>     canlı state
>
>
>     ÇALIŞAN DB
>         ↓
>      pg_dump
>         ↓
>     backup.sql
>         ↓
>     BOŞ TEST DB
>         ↓
>       restore
>         ↓
>     doğrulama
>
> **Volume backup değildir. Backup'ın gerçek testi ise dosyanın varlığı değil, restore edilebilmesidir.**

---

# 1️⃣ Docker'da Veri Nerede Yaşıyor?

Bugün üç storage modelini ayırdım:

| Yapı | Nerede yaşar? | Container silinirse? |
|---|---|---|
| Writable layer | Container'a ait | ❌ gider |
| Named volume | Docker yönetir | ✅ kalabilir |
| Bind mount | Host filesystem | ✅ host'ta kalır |

## Writable Layer

Container içine:

    touch /test.txt

yazdım ve bu path herhangi bir mount altında değilse dosya container'ın writable layer'ındadır.

Önemli ayrım:

    docker stop
    → container sadece durur
    → writable layer hâlâ vardır

    docker rm
    → container silinir
    → writable layer da gider

> **STOP ≠ DELETE**

---

# 📁 Bind Mount vs Named Volume

Bind mount:

    ./sql:/lab/sql

Sol taraf gerçek host path.

Mental model:

    HOST
    ./sql
      │
      ▼
    CONTAINER
    /lab/sql

Named volume:

    db_volume:/var/lib/postgresql/data

Sol taraf host path değil, Docker volume adı.

Mental model:

    PostgreSQL container
             │
             ▼
         db_volume

Kısa kural:

    ./data:/app
    → bind mount

    mydata:/app
    → named volume

---

# 🐘 PostgreSQL Volume

PostgreSQL 16'nın canlı database datasını:

    /var/lib/postgresql/data

altında tuttuğu yapı üzerinden çalıştım.

Bu yüzden:

    db_volume:/var/lib/postgresql/data

kullandım.

Okunuşu:

    db_volume
       ↓
    volume adı

    /var/lib/postgresql/data
       ↓
    container içindeki mount noktası

> [!important]
> Volume'u herhangi bir klasöre mount etmek yetmez.
>
> **Uygulamanın gerçekten veri yazdığı path'e mount etmem gerekiyor.**

Mesela:

    db_volume:/muz

Docker açısından geçerli olabilir.

Ama PostgreSQL `/muz` kullanmıyorsa database verileri oraya gitmez.

---

# ⚠️ Volume Dokunulmaz Kasa Değil

İlk düşüncem:

> "Volume container'dan bağımsızsa container içindeki olaylardan etkilenmez."

**TIRT.**

PostgreSQL volume'u aktif olarak kullanıyor.

Ben:

    DELETE ...
    UPDATE ...
    DROP TABLE ...

yaparsam bu değişiklikler canlı volume'a da yazılır.

Yani:

    container silindi
          ↓
    volume kalabilir ✅

ama:

    DROP TABLE
          ↓
    volume içindeki DB değişir ❌

Bu yüzden:

> **Volume persistence sağlar, geçmiş state saklamaz.**

---

# 🔥 `docker compose down -v`

Bu ayrım kritik:

    docker compose down

ile:

    docker compose down -v

aynı değil.

`-v` volume'ları da kaldırabilir.

Database ortamında kafama göre:

    down -v

basmak = **TIRT.**

---

# 🧠 Physical vs Logical

Başta `physical` kelimesini:

> "Gerçek dosya"

gibi düşündüm.

Eksikmiş.

İkisi de gerçek dosya olabilir.

Asıl ayrım:

    PHYSICAL
    → PostgreSQL veriyi NASIL saklıyor?

    LOGICAL
    → Database'in İÇİNDE NE VAR?

Physical tarafta PostgreSQL'in internal storage yapıları var:

    PGDATA/
      ├── base/
      ├── global/
      ├── pg_wal/
      └── ...

Logical tarafta ise:

    tablolar
    kolonlar
    satırlar
    constraint'ler
    ilişkiler

var.

---

# 💾 `pg_dump`

`pg_dump` PostgreSQL'e özel bir **logical backup** aracı.

    PostgreSQL
        ↓
      pg_dump
        ↓
    backup.sql

Plain dump içinde örneğin:

    CREATE TABLE
    COPY
    ALTER TABLE
    CREATE SEQUENCE

gibi database'i yeniden oluşturabilecek bilgiler bulunabilir.

En basit benzetmem:

    Volume
    = çalışan fabrikanın kendisi

    pg_dump
    = fabrikayı yeniden kurma planı

> [!danger]
> **VOLUME != BACKUP**
>
> **VOLUME != PG_DUMP**

---

# 2️⃣ Gerçek Backup → Restore Labı

Bugünkü gerçek hedef:

> **`backup.sql` üretmek değil, o backup'ın gerçekten geri yüklenebildiğini kanıtlamak.**

Lab zincirim:

    coreops
      ↓
    pg_dump
      ↓
    db_backup.sql
      ↓
    coreops_restore_test
      ↓
    restore
      ↓
    SELECT
      ↓
    doğrulama ✅

---

# 🐳 Compose Yapısı

PostgreSQL için:

    schema.sql
    seed.sql
    → bind mount

    db_volume
    → named volume

kullandım.

Mental model:

    HOST
    schema.sql + seed.sql
          │
       bind mount
          ▼
    PostgreSQL container
          │
          ▼
      db_volume
          │
          ▼
    canlı DB datası

Top-level:

    volumes:
      db_volume:

→ volume'u **tanımlar**.

Service içinde:

    volumes:
      - db_volume:/var/lib/postgresql/data

→ volume'u container'a **bağlar**.

Kafaya:

    top-level volume
    → TANIMLA

    service volume
    → BAĞLA

---

# 🔄 Init Script Davranışı

İlk açılış:

    boş db_volume
         ↓
    PostgreSQL initialize
         ↓
    schema.sql
         ↓
    seed.sql

Loglarda:

    running ...01-schema.sql
    CREATE TABLE

    running ...02-seed.sql
    INSERT 0 3

gördüm.

Container'ı durdurup tekrar açtığımda:

    PostgreSQL Database directory appears to contain a database;
    Skipping initialization

geldi.

Bu bana şunu kanıtladı:

    container yeniden başladı
            ↓
    volume hâlâ dolu
            ↓
    database hâlâ mevcut
            ↓
    init scriptleri tekrar çalışmadı

> **`docker-entrypoint-initdb.d` scriptleri her restart'ta çalışmaz.**
>
> Data directory ilk kez initialize edilirken çalışırlar.

---

# 📊 Kaynak DB Baseline

Backup almadan önce kaynak `coreops` DB'yi kontrol ettim.

Tablolar:

    assets
    owners

Veriler:

    assets → 3 satır

    blue-web-01
    blue-db-01
    red-web-01

    owners → 3 satır

    blue-team
    red-team
    empty-team

Bu benim restore sonrası karşılaştıracağım **baseline** oldu.

---

# 📦 Gerçek Dump

Dump:

    docker compose exec -T db pg_dump -U coreops -d coreops > backups/db_backup.sql

Akış:

    container içindeki pg_dump
              ↓
            stdout
              ↓
         host shell >
              ↓
    backups/db_backup.sql

Buradaki önemli detay:

> `pg_dump` container içinde çalışıyor ama `>` host shell tarafından işlendiği için dosya host'ta oluşuyor.

Dump dosyasını da kontrol ettim:

    ls -lh
    → yaklaşık 3.7K

    file
    → ASCII text

Bu dump:

    plain SQL

formatındaydı.

Kural:

    plain SQL
    → psql

    custom archive
    → pg_restore

---

# 🧷 `-T` Neydi?

Bir ara `-d` ile karıştırdım.

    -T
    → pseudo-TTY allocation kapat

Burada stdin/stdout redirect yaptığım için uygun olan:

    docker compose exec -T ...

idi.

`-d` başka şey:

    detached mode

---

# 🧪 Ayrı Restore DB

Çalışan `coreops` DB'nin üstüne restore yapmadım.

Yeni:

    coreops_restore_test

database'i oluşturdum.

Mantık:

    ÇALIŞAN DB
       ↑
    DOKUNMA


    backup.sql
       ↓
    boş test DB
       ↓
     restore

Yeni DB'yi:

    template0

üzerinden oluşturdum.

Ama burada ilk hatam:

    createdb ... -d coreops ...

yazmak oldu.

`psql` alışkanlığını `createdb` aracına taşımışım.

Sonuç:

    invalid option -- 'd'

Öğrendiğim:

> **PostgreSQL CLI araçlarının flag'leri aynı olmak zorunda değil.**

`createdb` tarafında yeni DB adı doğrudan sona geliyor; template için:

    -T template0

kullanılıyor.

---

# ✅ Restore Öncesi Boşluk Kanıtı

Yeni DB'ye bağlanıp:

    \dt

çalıştırdım.

Sonuç:

    Did not find any relations.

Bu çok önemliydi.

Artık biliyorum:

    RESTORE ÖNCESİ
    → hiçbir tablo yok ✅

Dolayısıyla restore sonrası çıkan tabloların dump'tan geldiğini kanıtlayabilirim.

---

# 🔀 `>` ve `<` Sonunda Oturdu

Dump:

    pg_dump > backup.sql

Mental model:

    PROGRAM
       ↓
       >
       ↓
     DOSYA

Restore:

    psql < backup.sql

Mental model:

    DOSYA
      ↓
      <
      ↓
    PROGRAM

Kafaya:

    >  PROGRAMDAN DOSYAYA

    <  DOSYADAN PROGRAMA

---

# ♻️ Restore

Plain SQL dump olduğu için:

    psql

kullandım.

Akış:

    HOST
    db_backup.sql
         ↓
       stdin
         ↓
    docker compose exec -T
         ↓
        psql
         ↓
    coreops_restore_test

Restore sırasında:

    CREATE TABLE
    CREATE SEQUENCE
    COPY 3
    COPY 3
    setval
    ALTER TABLE

çıktılarını gördüm.

`COPY 3` değerlerinin iki kez gelmesi:

    owners → 3
    assets → 3

baseline'ımla uyumluydu.

Ama burada durmadım.

> [!important]
> **Restore command hata vermedi ≠ Backup doğrulandı.**

---

# ✅ Restore Doğrulaması

Restore sonrası:

    \dt

çıktısı:

    assets
    owners

Sonra gerçek verileri sorguladım:

    assets → 3 satır
    owners → 3 satır

ve içerikler kaynak DB ile aynıydı.

Yani:

    SOURCE coreops

    assets = 3
    owners = 3


    RESTORED coreops_restore_test

    assets = 3
    owners = 3

Bu noktada gerçekten:

> **Backup kullanılabilir.**

diyebilirim.

---

# 🐞 Günün Hataları

## 1. `-w` ile persistence'ı karıştırdım

    -w /app

sadece:

    working directory = /app

demek.

Volume veya persistence ile alakası yok.

---

## 2. Her `-v` gördüğümde bind mount sandım

Yanlış.

    -v ./data:/app
    → bind mount

    -v mydata:/app
    → named volume

Sol tarafa bak.

---

## 3. Container stop olunca writable layer gider sandım

    stop
    → container hâlâ var

    rm
    → container silinir

---

## 4. Volume'u backup sandım

En önemli hata.

    volume
    → canlı persistent storage

    backup
    → geçmiş state'i geri getirecek ayrı kopya

---

## 5. `docker compose exec` sonrası service adını unuttum

`exec` şunu bilmek zorunda:

> Hangi service içinde çalışacağım?

Mental model:

    docker compose exec
          ↓
          db
          ↓
        pg_dump

---

## 6. Dump'ı klasöre redirect etmeye çalıştım

Yanlış:

    > backups

Doğru hedef dosya olmalı:

    > backups/db_backup.sql

---

## 7. `\dt` ile database listesi aradım

    \dt
    → tables

    \l
    → databases

---

## 8. `createdb` ile `psql` flag'lerini karıştırdım

    psql -d DATABASE

mantığını `createdb`'ye taşıdım.

**TIRT.**

Her CLI aracının kendi contract'ı var.

---

## 9. Restore redirect yönünü karıştırdım

Dump'ta:

    >

kullandığım için restore'da da ilk anda `>` düşündüm.

Doğrusu:

    dump    → >
    restore → <

---

## 10. Dump dosyasını `psql` argümanı gibi vermeye çalıştım

Dump host'taydı.

Doğru yol:

    < backups/db_backup.sql

ile host shell'in dosyayı stdin üzerinden container içindeki `psql`'ye vermesi.

---

# 💥 SQL Hatası — 3 × 3 = 9

Restore doğrularken:

    SELECT * FROM assets, owners;

yazdım.

Benim kafamdaki:

> "İki tabloyu göster."

SQL'in yaptığı:

> "İki tablodaki bütün satır kombinasyonlarını üret."

Bende:

    assets = 3
    owners = 3

olduğu için:

    3 × 3 = 9 satır

geldi.

Bu restore hatası değildi.

Bu:

    Cartesian product

idi.

İki tabloyu ayrı görmek istersem:

    SELECT * FROM assets;
    SELECT * FROM owners;

Aynı terminal gönderiminde olabilir ama bunlar **iki ayrı SQL statement**.

Eğer her asset'i kendi gerçek owner'ıyla eşleştirmek istersem:

    assets.owner_id
          ↓
        JOIN
          ↓
      owners.id

mantığına geçmem gerekir.

---

# 🔠 SQL Büyük / Küçük Harf

Şunu da fark ettim:

    SELECT * FROM owners;

ve:

    select * from owners;

ikisi de çalışıyor.

SQL keyword'leri bu kullanımda case-insensitive.

Ama okunabilirlik için:

    SELECT
    FROM
    WHERE

gibi keyword'leri büyük yazmak daha temiz.

---

# 🧭 Bundan Sonraki Backup Kontrol Sıram

    1. Kaynak DB'yi doğrula
           ↓
    2. Baseline al
           ↓
    3. pg_dump
           ↓
    4. Backup dosyasını kontrol et
           ↓
    5. Ayrı + boş test DB oluştur
           ↓
    6. Boş olduğunu kanıtla
           ↓
    7. Restore et
           ↓
    8. Tablolar var mı?
           ↓
    9. Satırlar doğru mu?
           ↓
    10. İçerik kaynakla aynı mı?
           ↓
       BACKUP ✅

> **Backup'ın varlığını değil, geri yüklenebilirliğini test et.**

---

# 🧠 Kafaya Kazı

> [!tip]
> **Writable layer = container'a bağlı.**

> [!tip]
> **Bind mount = host path container'a bağlı.**

> [!tip]
> **Named volume = Docker'ın yönettiği persistent storage.**

> [!danger]
> **Volume ≠ Backup**

> [!tip]
> **Volume = çalışan DB'nin canlı storage'ı.**

> [!tip]
> **`pg_dump` = PostgreSQL logical backup.**

> [!tip]
> **Plain SQL → `psql`**

> [!tip]
> **Custom dump → `pg_restore`**

> [!tip]
> **`>` = programdan dosyaya.**

> [!tip]
> **`<` = dosyadan programa.**

> [!tip]
> **`\dt` = tablolar, `\l` = database'ler.**

> [!danger]
> **Restore hata vermedi diye backup sağlam kabul edilmez. Veriyi sorgula.**

---

# 📌 30 Saniyelik Özet

    POSTGRESQL
        ↓
    /var/lib/postgresql/data
        ↓
     db_volume
        ↓
    CANLI STATE


    POSTGRESQL
        ↓
      pg_dump
        ↓
       >
        ↓
    backup.sql


    backup.sql
        ↓
        <
        ↓
       psql
        ↓
    EMPTY TEST DB
        ↓
      RESTORE
        ↓
       \dt
        ↓
      SELECT
        ↓
    VERIFY ✅


    VOLUME
    → persistence

    BACKUP
    → recovery


    assets = 3
    owners = 3

    SELECT * FROM assets, owners;
              ↓
             3×3
              ↓
          9 satır ❌

    Ayrı sorgular:
    SELECT * FROM assets;
    SELECT * FROM owners;

---

# ✅ Günün Kazanımları

- [x] Writable layer / bind mount / named volume ayrımını oturttum
- [x] `-w` seçeneğinin persistence olmadığını öğrendim
- [x] Container stop ve delete farkını netleştirdim
- [x] PostgreSQL data path ile volume mount path'in eşleşmesi gerektiğini öğrendim
- [x] Volume'un backup olmadığını oturttum
- [x] Physical / logical database ayrımını öğrendim
- [x] `pg_dump` mantığını öğrendim
- [x] Compose'ta named volume tanımlayıp PostgreSQL'e bağladım
- [x] Bind mount ile named volume'u `docker compose config` üzerinden ayırdım
- [x] Init scriptlerinin yalnızca boş data directory'de çalıştığını gördüm
- [x] Kaynak DB için baseline aldım
- [x] Gerçek plain SQL dump oluşturdum
- [x] `-T` ile non-interactive redirect mantığını uyguladım
- [x] `>` ile dump çıktısını host dosyasına yazdım
- [x] Ayrı `coreops_restore_test` DB oluşturdum
- [x] Restore öncesi DB'nin gerçekten boş olduğunu kanıtladım
- [x] `<` ile dump'ı `psql` stdin'ine verdim
- [x] Restore sonrası tabloları doğruladım
- [x] Kaynak ve restore DB'de 3'er satırın aynı olduğunu kontrol ettim
- [x] Cartesian product hatasını gördüm
- [x] İki tabloyu ayrı sorgulama ile JOIN mantığını birbirinden ayırdım
- [x] Backup'ın gerçek testinin **restore + verification** olduğunu oturttum

---

# 🚀 Gün Sonu

> **Container'ın silinmesine karşı volume kullanırım. Database'in yanlışlıkla silinmesine, bozulmasına veya geçmiş state'e dönme ihtiyacına karşı backup kullanırım.**
>
> Ve artık:
>
> **`backup.sql var` demek yerine `backup ayrı ve boş DB'ye restore edildi, tablolar ve veriler doğrulandı` diyebilirim.**