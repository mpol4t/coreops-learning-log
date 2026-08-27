---
title: "Gün 38 — PostgreSQL, SQL, Transaction, Docker Volume, Mount, Backup ve findmnt"
tags:
  - coreops
  - day38
  - postgresql
  - sql
  - docker
  - docker-compose
  - volumes
  - mount
  - persistence
  - transaction
  - join
  - group-by
  - pg-dump
  - findmnt
  - gitignore
aliases:
  - "Gün 38 PostgreSQL SQL Docker Storage ve Backup"
status: completed
---

# 🐘 Gün 38 — PostgreSQL, SQL, Transaction, Docker Volume, Mount, Backup ve `findmnt`

> [!abstract] 🎯 Günün ana fikri
> Bugün PostgreSQL, SQL ve Docker storage tarafını tek mimaride birleştirdim.
>
> En büyük farkındalığım:
>
> **PostgreSQL, Docker volume ve mount aynı katman değil.**
>
> Ana zincirim:
>
>     SQL
>      ↓
>     PostgreSQL process
>      ↓
>     tables / logical database state
>      ↓
>     PostgreSQL database files
>      ↓
>     container path
>      ↓
>     MOUNT
>      ↓
>     named volume
>      ↓
>     persistent storage
>
> SQL tarafında ise:
>
>     FROM / JOIN
>          ↓
>        WHERE
>          ↓
>      GROUP BY
>          ↓
>     AGGREGATE
>          ↓
>        SELECT

---

# 🐘 PostgreSQL Aslında Nedir?

PostgreSQL'i sadece soyut olarak `database` diye düşünmek yerine container açısından şöyle düşünüyorum:

    PostgreSQL container
            ↓
    PostgreSQL process

PostgreSQL çalışan bir server/program.

Ben SQL gönderiyorum:

    SQL
     ↓
    PostgreSQL
     ↓
    database state'i oku/değiştir

Kısa model:

> **SQL = PostgreSQL'e verdiğim emir**

> **PostgreSQL = bu emirleri işleyen database motoru**

---

# 🧠 Table ile Database Dosyaları Aynı Şey Değil

Ben SQL'de şöyle bir yapı görüyorum:

| id | name | balance |
|---:|---|---:|
| 1 | Polat | 1000 |
| 2 | Ahmet | 500 |

Bu mantıksal database state'i.

Ama PostgreSQL bunun fiziksel karşılığını kendi database dosyalarında tutuyor.

    TABLE
      ↓
    PostgreSQL
      ↓
    database files
      ↓
    filesystem

Database dosyasını açınca `Polat=1000` gibi basit text görmek zorunda değilim.

PostgreSQL kendi storage formatını yönetiyor.

> **Table = mantıksal veri yapısı**

> **Database files = bunun fiziksel storage karşılığı**

---

# 💀 Database'i Container Writable Layer'da Bırakmak

Volume yoksa:

    CONTAINER
    ├── PostgreSQL process
    └── database files

Database dosyaları container writable layer'ında kalabilir.

Container silindiğinde:

    container silindi
          ↓
    writable layer silindi
          ↓
    database files kaybolabilir

Database state'inin container lifecycle'ına bağlı olmasını istemiyorum.

---

# 📦 Named Volume Neden Var?

Amaç database dosyalarını container'dan bağımsız storage'da tutmak.

    PostgreSQL container
            │
            ↓
    /var/lib/postgresql
            │
          MOUNT
            │
            ↓
        pgdata
      named volume

Container gider:

    PostgreSQL container 💀

Ama volume kalabilir:

    pgdata ✅

Yeni container aynı volume'ü mount ederse:

    yeni PostgreSQL container
              ↓
           pgdata
              ↓
    eski database files
              ↓
          database ✅

Buna **persistence** deniyor.

> **Container recreate edildiği halde state yaşamaya devam ediyorsa persistence var.**

---

# 🆚 Container vs Volume

    CONTAINER
    = programın çalıştığı runtime ortam

    VOLUME
    = storage

Container PostgreSQL'i çalıştırır.

Volume PostgreSQL'in fiziksel database dosyalarını tutabilir.

> **Container database'in kendisi değildir.**

---

# 🐘 PostgreSQL 18 Path Konusu

Labda:

`postgres:18`

kullandım.

Volume target:

`/var/lib/postgresql`

olarak kullanıldı.

PostgreSQL 18 bunun altında version-specific bir data directory kullanabiliyor:

`/var/lib/postgresql/18/docker`

Eski tutoriallarda sık gördüğüm:

`/var/lib/postgresql/data`

path'ini sürüm farkını düşünmeden körlemesine kopyalamamam gerekiyor.

> **PostgreSQL image sürümünü kontrol et → image'ın beklediği storage path'ine göre mount yap.**

---

# 🗂️ Mount Nedir?

Bugün storage tarafında asıl eksik olan kavram mount'muş.

Önemli:

> **Mount Docker'a özgü değil.**

Linux/Unix filesystem mekanizması.

Docker da bundan yararlanıyor.

Mount:

> **Bir storage/filesystem/directory tree'yi belirli bir path üzerinden erişilebilir hale getirmek.**

---

# 💾 USB Örneğiyle Mount

USB:

    USB /
    ├── foto.jpg
    ├── film.mp4
    └── belgeler/

Linux'ta:

`/mnt/usb`

path'i olsun.

USB buraya mount edilirse:

    USB filesystem
          │
        MOUNT
          │
          ↓
      /mnt/usb

Sonra:

`/mnt/usb/foto.jpg`

dediğimde USB'deki dosyayı görüyorum.

---

# 🚨 Mount = Copy Değil

İlk hatalı zihinsel model:

> Mount edince dosyalar target klasöre kopyalanıyor.

TIRT.

Doğrusu:

    SOURCE
       │
       │ mount
       ↓
    TARGET PATH

Mount bir copy işlemi değildir.

Source'un filesystem tree'sini target path üzerinden görünür hale getirir.

---

# 🧠 Path Neden Aynı Kalıyor?

Mount öncesi:

    /mnt/usb
       ↓
    normal directory

Mount sonrası yine:

`/mnt/usb`

yazıyorum.

Ama artık arkasında USB filesystem'i görüyorum.

> **Path aynı kalır. Path'in arkasında ne gördüğüm değişir.**

---

# 👻 Mount Point'in Altında Önceden Dosya Varsa

Mount'tan önce:

    /mnt/usb
    └── eski.txt

olsun.

USB mount edilince:

    /mnt/usb
    ├── foto.jpg
    └── film.mp4

görebilirim.

`eski.txt` otomatik silinmiş değildir.

Mounted filesystem alttaki directory'nin görünümünü örter.

Unmount edilirse alttaki dosya tekrar görünebilir.

> **Mount mevcut directory içeriğini silmez; o path üzerinde başka tree görünür hale gelir.**

---

# 🎯 SOURCE ve TARGET

Mount görünce iki şeyi arıyorum.

## SOURCE

Neyi mount ediyorum?

Örnek:

`/dev/sdb1`

## TARGET / MOUNT POINT

Nereden erişiyorum?

Örnek:

`/mnt/usb`

Şema:

    SOURCE                  TARGET

    /dev/sdb1 ──MOUNT──> /mnt/usb

Kendime soracağım soru:

> **Neyi, hangi path'e mount etmişler?**

---

# 🌳 Mount Source Sadece Disk Değil

Disk:

    disk
     ↓
    mount
     ↓
    /data

USB:

    USB
     ↓
    mount
     ↓
    /mnt/usb

Network filesystem:

    remote filesystem
          ↓
        mount
          ↓
      /mnt/share

Başka directory:

    /home/polat/proje
            ↓
        bind mount
            ↓
          /work

Mount genel mekanizma.

---

# 🆚 Bind Mount vs Named Volume

## Bind Mount

Örnek:

`.:/lab`

    SOURCE
    .
    host directory
         │
      bind mount
         │
         ↓
    TARGET
    /lab
    container path

Container `/lab/test.py` açtığında host'taki dosyayı görebilir.

## Named Volume

Örnek:

`pgdata:/var/lib/postgresql`

Burada:

`pgdata`

Docker named volume adı.

Path değil.

Sağ taraf:

`/var/lib/postgresql`

container target path.

    pgdata
    SOURCE
      │
      │ mount
      ↓
    /var/lib/postgresql
    TARGET

---

# 🐘 PostgreSQL Volume Kullandığını "Bilmez"

PostgreSQL kendi açısından:

`/var/lib/postgresql`

path'ini görüyor.

Ve:

> Database dosyalarımı buraya yazıyorum.

diyor.

Alt katmanda:

    PostgreSQL
        ↓
    /var/lib/postgresql
        ↓
    filesystem / mount
        ↓
    Docker volume

var.

---

# 🐳 Compose'ta Neden İki Tane `volumes:` Var?

İlk başta ikisini aynı şeyi tekrar yazmak gibi görüyordum.

Aslında iki farklı görev var.

## Top-Level `volumes:`

    volumes:
      pgdata:

Anlam:

> Bu Compose projesinde `pgdata` isimli named volume resource'u var.

Bu storage resource tanımı.

## Service İçindeki `volumes:`

    services:
      db:
        volumes:
          - pgdata:/var/lib/postgresql

Anlam:

> `db` service'i `pgdata` volume'ünü `/var/lib/postgresql` path'ine mount etsin.

Bu resource kullanımı.

---

# 🧠 İki `volumes:` İçin Kafaya Kazı

    COMPOSE PROJECT

    RESOURCES
    └── pgdata

    SERVICES
    └── db
        └── pgdata
             ↓ mount
           /var/lib/postgresql

> **Top-level `volumes:` = depoyu tanımla**

> **Service `volumes:` = depoyu container'a bağla**

> **Volume = storage source**

> **Path = erişim noktası**

> **Mount = ikisini bağlayan mekanizma**

---

# 🐳 PostgreSQL Compose Lab

Genel hedef:

    PostgreSQL çalışsın
          +
    database persistent olsun
          +
    host'taki SQL dosyalarını container görebilsin

Mimari:

    MAC
    ├── compose.yaml
    └── sql/
        ├── schema.sql
        └── seed.sql

             ↓ Docker

    POSTGRESQL CONTAINER
    ├── PostgreSQL process
    │
    ├── /lab/sql
    │      ↑
    │   bind mount
    │      ↑
    │    ./sql
    │
    └── /var/lib/postgresql
           ↑
         mount
           ↑
        pgdata volume

---

# 🐘 `image: postgres:18`

`db` service:

`postgres:18`

image'ından oluşturuldu.

    postgres:18 image
          ↓
    PostgreSQL container
          ↓
    PostgreSQL server process

---

# 🌱 PostgreSQL Environment Variables

Kullandığım:

`POSTGRES_USER`

`POSTGRES_PASSWORD`

`POSTGRES_DB`

Lab değerleri:

    POSTGRES_USER = coreops
    POSTGRES_PASSWORD = coreops-lab
    POSTGRES_DB = coreops

PostgreSQL user ile database aynı kavram değil.

İsimlerinin ikisinin de `coreops` olması onları aynı şey yapmıyor.

---

# 🐞 YAML'da Environment Hatası

İlk deneme:

    environment:
      - POSTGRES_USER: coreops
      - POSTGRES_PASSWORD: coreops-lab
      - POSTGRES_DB: coreops

Buradaki `-` liste item'ı anlamına geliyor.

Ben mapping istiyordum.

Doğru:

    environment:
      POSTGRES_USER: coreops
      POSTGRES_PASSWORD: coreops-lab
      POSTGRES_DB: coreops

Kafaya kazı:

    - item
    - item
    = LIST

Ama:

    key: value
    key: value
    = MAPPING

---

# 🚪 PostgreSQL Port Publishing

Kullandığım:

`127.0.0.1:15432:5432`

Parçaları:

    127.0.0.1
    → host interface

    15432
    → host port

    5432
    → container port

Akış:

    Mac
    127.0.0.1:15432
           ↓
    Docker port publishing
           ↓
    PostgreSQL container
    :5432

Container içinde PostgreSQL `5432` üzerinde.

Host'tan `15432` üzerinden erişiyorum.

---

# 📦 PostgreSQL Data Volume

Service mount:

`pgdata:/var/lib/postgresql`

    pgdata
    named volume
        ↓
      mount
        ↓
    /var/lib/postgresql

Amaç:

> PostgreSQL database dosyalarını writable layer'dan ayırıp persistent storage'da tutmak.

---

# 📁 SQL Bind Mount

Diğer mount:

`./sql:/lab/sql:ro`

Parçaları:

    ./sql
    → host directory

    /lab/sql
    → container target path

    ro
    → read-only

Akış:

    Mac
    ./sql/schema.sql
          ↓
      bind mount
          ↓
    Container
    /lab/sql/schema.sql

Aynı şekilde:

    ./sql/seed.sql
          ↓
    /lab/sql/seed.sql

---

# 🆚 İki Mount'un Amacı

`pgdata:/var/lib/postgresql`

→ database state persistent olsun.

`./sql:/lab/sql:ro`

→ host'taki SQL source dosyalarını container okuyabilsin.

Biri data persistence.

Diğeri source paylaşımı.

---

# 🐞 Top-Level Volume'u `services:` Altına Koyma Hatası

Bir noktada top-level `volumes:` bloğunu yanlış seviyeye koydum.

Docker buna benzer hata verdi:

`services.volumes additional properties 'pgdata' not allowed`

Doğru yapı:

    services:
      db:
        ...

    volumes:
      pgdata:

`services:` ve `volumes:` aynı top-level seviyede.

---

# 🧠 YAML Indentation = Yapının Kendisi

YAML'daki boşluk görsel süs değil.

Anlamı değiştiriyor.

    services:
      db:

→ `db`, `services` altında.

Ama:

    services:
      db:
        ...

    volumes:

→ `services` ve `volumes` top-level sibling.

Python indentation gibi dikkat etmem gerekiyor.

---

# 🏗️ `schema.sql`

Schema'nın görevi:

> Database yapısını oluşturmak.

Labda iki tablo oluşturdum:

`owners`

`assets`

İlişki:

    OWNER
      ├── asset
      ├── asset
      └── asset

Bir owner'ın birden fazla asset'i olabilir.

---

# 👤 `owners` Tablosu

Kolonlar:

`id`

`name`

`id`:

`GENERATED ALWAYS AS IDENTITY PRIMARY KEY`

PostgreSQL ID üretiyor.

`name`:

`text UNIQUE NOT NULL`

    text
    → metin

    UNIQUE
    → tekrar edemez

    NOT NULL
    → null olamaz

---

# 🖥️ `assets` Tablosu

Kolonlar:

- `id`
- `hostname`
- `owner_id`
- `risk`

`hostname`:

`UNIQUE NOT NULL`

`owner_id`:

`REFERENCES owners(id)`

`risk`:

`CHECK (risk BETWEEN 0 AND 100)`

---

# 🔗 Foreign Key

İlişki:

    assets.owner_id
           ↓
    owners.id

Örneğin:

    owners

    1 → Polat
    2 → Kerem

    assets

    polat_1 → owner_id 1
    polat_2 → owner_id 1
    kerem_1 → owner_id 2
    kerem_2 → owner_id 2

Asset row'u owner'ın tamamını taşımak yerine `owner_id` ile owner kaydına referans veriyor.

---

# 🛡️ `CHECK` Constraint

Risk:

`0 - 100`

Örnek:

    risk = 20   ✅
    risk = 50   ✅
    risk = 100  ✅
    risk = -1   ❌
    risk = 200  ❌

Database bu rule'u kendisi enforce ediyor.

---

# 🌱 `seed.sql`

Kısa model:

    schema.sql
    = binayı kur

    seed.sql
    = binaya başlangıç verisini koy

Schema table'ları oluşturur.

Seed başlangıç row'larını ekler.

---

# 🐞 SQL String'de Çift Tırnak Hatası

İlk deneme:

`VALUES("Polat")`

TIRT.

PostgreSQL'de text literal:

`'Polat'`

Kısa:

    'Polat'
    → string literal

    "Polat"
    → identifier gibi yorumlanabilir

---

# 🐞 `;` Unutma

SQL statement'ın tamamlandığını:

`;`

ile belirtiyorum.

Örnek:

    INSERT INTO owners(name)
    VALUES ('Polat');

Mental model:

`;` → statement bitti.

---

# 🌱 Seed Verim

Owner'lar:

- Polat
- Kerem

Asset'ler:

- `polat_1`
- `polat_2`
- `kerem_1`
- `kerem_2`

Risk:

    polat_1 → 20
    polat_2 → 10
    kerem_1 → 50
    kerem_2 → 30

Owner relation:

    polat_* → owner_id 1
    kerem_* → owner_id 2

---

# ⚠️ Hard-Coded `owner_id` Varsayımı

Temiz lab database'inde:

    Polat → id 1
    Kerem → id 2

olduğu için çalıştı.

Ama sequence ilerlemiş olsaydı:

    Polat → 7
    Kerem → 8

gibi olabilir.

Bu yüzden hard-coded `owner_id=1`, `owner_id=2` production-grade yaklaşım değil.

Lab için foreign key mantığını görmek açısından yeterliydi.

---

# 📂 Seed Dosyası Nerede?

Host:

`sql/seed.sql`

Bind mount:

`./sql:/lab/sql:ro`

Container:

`/lab/sql/seed.sql`

Dosyayı container'da yeniden oluşturmadım.

Mount sayesinde zaten görünür oldu.

---

# 🐘 `psql`

Önemli ayrım:

> `psql` PostgreSQL server değildir.

`psql` PostgreSQL server ile konuştuğum CLI client.

    psql
    CLIENT
      │
      │ SQL
      ↓
    PostgreSQL
    SERVER

---

# 👤 `psql -U coreops -d coreops`

`-U coreops`

→ `coreops` database user'ıyla bağlan.

`-d coreops`

→ `coreops` database'ine bağlan.

Aynı isim, farklı kavram.

---

# 📄 `psql -f`

`psql -f dosya.sql`

demek:

> Bu SQL dosyasındaki statement'ları çalıştır.

    schema.sql
       ↓
      psql
       ↓
    PostgreSQL
       ↓
    CREATE TABLE

Seed:

    seed.sql
       ↓
      psql
       ↓
    PostgreSQL
       ↓
    INSERT

---

# 🐞 Shell ile `psql` Prompt'unu Karıştırma

Bir noktada SQL'i:

`psql ... SELECT ...`

şeklinde CLI argümanı gibi verdim.

`psql`:

`extra command-line argument "SELECT" ignored`

gibi warning verdi.

Doğru mental ayrım:

    polat@MacBook %
    → shell

    coreops=#
    → psql prompt

Shell'de Docker/OS komutları.

`coreops=#` içinde SQL.

---

# 🔍 `SELECT`

`SELECT` sorusu:

> **Sonuçta neyi göstereceğim?**

Örneğin:

`SELECT name`

→ `name` kolonunu göster.

> **SELECT = hangi kolon/değerler?**

---

# 🐞 `SELECT FROM assets` Hatası

Bir ara:

`SELECT FROM assets WHERE ...`

yazdım.

Eksik olan:

> Neyi SELECT edeceğim?

Bütün kolonlar:

`SELECT *`

Mental model:

    SELECT
    → NEYİ?

    FROM
    → NEREDEN?

    WHERE
    → HANGİ SATIRLAR?

---

# 🎯 `WHERE`

`WHERE` sorusu:

> **Hangi satırlar?**

Lab sorgum:

`SELECT * FROM assets WHERE risk > 35;`

Seed:

    20
    10
    50
    30

Sonuç:

    kerem_1 | owner_id 2 | risk 50

> **SELECT = hangi kolonlar?**

> **WHERE = hangi satırlar?**

---

# 🐞 `risk > 50` Neden 0 Row?

En büyük değer `50`.

Ama:

`> 50`

50'yi dahil etmez.

Bu yüzden:

`0 rows`

50 dahil olsun istersem:

`>= 50`

kullanmam gerekir.

---

# 🐘 `coreops-#` Prompt'u

Normal:

`coreops=#`

→ yeni statement bekliyor.

Ama `;` unutursam:

`coreops-#`

olabiliyor.

Anlamı:

> Statement henüz bitmedi, devamını bekliyorum.

Query buffer'ı temizlemek için:

`\r`

kullanılabiliyor.

Kısa:

    coreops=#
    → yeni statement

    coreops-#
    → mevcut statement devam ediyor

---

# 🔗 `JOIN`

`assets` tablosunda:

`owner_id`

var.

Ama owner adı `owners` tablosunda.

Örneğin:

    kerem_1 | 2 | 50

Ben:

    kerem_1 | Kerem | 50

görmek istiyorum.

Bu yüzden tabloları ilişkilendiriyorum.

---

# 🧠 JOIN Relation

İlişki:

`assets.owner_id = owners.id`

Örnek:

    kerem_1
    owner_id = 2
        ↓
    owners.id = 2
        ↓
    Kerem

---

# 🆚 JOIN vs WHERE

`WHERE`:

    mevcut row set
         ↓
       filtre
         ↓
    bazı row'lar kalır

`JOIN`:

    TABLE A
       +
    TABLE B
       ↓
    eşleştirme
       ↓
    birleşmiş rows

> **WHERE = filtre**

> **JOIN = eşleştir**

---

# 🔗 `ON`

JOIN:

> Tabloyu ilişkiye kat.

`ON`:

> Hangi kurala göre satırları eşleştireceğim?

Lab:

`ON assets.owner_id = owners.id`

> **JOIN = ilişkiyi kur**

> **ON = ilişki/eşleşme kuralını belirt**

---

# 🧪 JOIN Sorgum

    SELECT assets.hostname, owners.name, assets.risk
    FROM assets
    JOIN owners
    ON assets.owner_id = owners.id;

Okuma:

    FROM assets
    → ana row source

    JOIN owners
    → owners'ı ilişkiye kat

    ON ...
    → doğru owner row'unu eşleştir

    SELECT ...
    → birleşik sonuçtan istediğim kolonları göster

Sonuç:

    polat_1 | Polat | 20
    polat_2 | Polat | 10
    kerem_1 | Kerem | 50
    kerem_2 | Kerem | 30

---

# 🐞 JOIN Sonrası Yine `owner_id` Gösterme Hatası

İlk başta:

`assets.owner_id`

seçmiştim.

Ama görev owner adı istiyordu.

Benim ihtiyacım:

`owners.name`

idi.

> JOIN yaptıktan sonra iki tablonun kolonlarından istediğimi SELECT edebilirim.

---

# 🧺 `GROUP BY`

Görev:

> Owner başına kaç asset var?

Data:

    Polat
    ├── polat_1
    └── polat_2

    Kerem
    ├── kerem_1
    └── kerem_2

Beklenen:

    Polat → 2
    Kerem → 2

`GROUP BY owners.name`

aynı owner adına ait row'ları aynı gruba koyuyor.

---

# 🔢 Aggregate

Aggregate birden fazla satırdan özet değer üretir.

`COUNT` → kaç tane?

`SUM` → toplam

`AVG` → ortalama

`MAX` → en büyük

`MIN` → en küçük

    birçok row
        ↓
    aggregate
        ↓
    özet değer

---

# 🆚 `GROUP BY` vs `COUNT(*)`

> **GROUP BY saymaz.**

GROUP BY grupları oluşturur.

`COUNT(*)` her gruptaki row sayısını sayar.

Örneğin:

    Polat group
    ├── polat_1
    └── polat_2

    COUNT(*) = 2

---

# 🧪 GROUP BY Sorgum

    SELECT owners.name, count(*)
    FROM assets
    JOIN owners
    ON assets.owner_id = owners.id
    GROUP BY owners.name;

Akış:

    assets
       ↓
    JOIN owners
       ↓
    owner relation
       ↓
    GROUP BY owners.name
       ↓
    COUNT(*)
       ↓
    owner + asset count

Sonuç:

    Polat | 2
    Kerem | 2

---

# 🆚 `WHERE` vs `HAVING`

`WHERE`

→ Gruplama öncesi normal row'ları filtreler.

`HAVING`

→ GROUP BY / aggregate sonrasında oluşan grupları filtreler.

Örnek:

`amount > 100`

→ `WHERE`

Ama:

> Toplam harcaması 1000'den büyük kullanıcıları getir.

Önce `SUM()` gerekir.

→ `HAVING`

Mental sıra:

    ROWS
      ↓
    WHERE
      ↓
    GROUP BY
      ↓
    AGGREGATE
      ↓
    HAVING

---

# 🧠 SQL İçin Yeni Düşünme Sıram

Bir query yazmadan önce:

1. Hangi tablodan başlıyorum?
2. Başka tablo lazım mı?
3. JOIN varsa eşleşme ilişkisi ne?
4. Hangi satırları filtreleyeceğim?
5. Gruplama gerekiyor mu?
6. Aggregate gerekiyor mu?
7. Sonuçta hangi kolonları göstereceğim?

Örnek:

> Owner başına asset sayısı.

    assets
      ↓
    owners ile JOIN
      ↓
    owner adına GROUP BY
      ↓
    COUNT(*)
      ↓
    owner name + count

---

# 🔄 Transaction

Transaction'ı banka transferi örneğiyle oturttum.

Başlangıç:

    Polat = 1000
    Ahmet = 500

100 transfer:

    1. Polat -100
    2. Ahmet +100

İlk işlem başarılı, ikinci işlem başarısız olursa:

    Polat = 900
    Ahmet = 500

tutarsız state oluşur.

Transaction'ın ana fikri:

> **Ya hepsi olacak ya hiçbiri olmayacak.**

---

# ▶️ `BEGIN`

`BEGIN`

demek:

> Bundan sonra yapacağım değişiklikleri transaction içinde değerlendir.

    BEGIN
      ├── operation 1
      ├── operation 2
      └── ...

---

# ✅ `COMMIT`

Her şey başarılı:

    BEGIN
      ├── Polat -100 ✅
      ├── Ahmet +100 ✅
      └── COMMIT

Sonuç:

    Polat = 900
    Ahmet = 600

`COMMIT`

→ transaction'daki değişiklikleri tamamla/kabul et.

---

# ↩️ `ROLLBACK`

Bir işlem başarısız:

    BEGIN
      ├── Polat -100 ✅
      ├── Ahmet +100 ❌
      └── ROLLBACK

Sonuç tekrar:

    Polat = 1000
    Ahmet = 500

> **COMMIT = yapılanları tut**

> **ROLLBACK = current transaction'ın değişikliklerini iptal et**

---

# ⚠️ ROLLBACK Tüm Database'i Geçmişe Sarmaz

Yanlış model:

> Database'i tamamen BEGIN anına geri götürüyor.

TIRT.

Doğrusu:

> **Current transaction'ın commit edilmemiş değişikliklerini geri alıyor.**

Başka transaction'ların commit ettiği state'i zamanda geri sarmıyor.

---

# 🚪 COMMIT Sonrası Aynı Transaction'a ROLLBACK Yok

    BEGIN
      ↓
    değişiklik
      ↓
    COMMIT

Transaction tamamlandı.

Sonradan aynı transaction'a `ROLLBACK` diyerek commit'i geri alamam.

Geri almak gerekiyorsa yeni bir işlem yapmak gerekir.

---

# 🧪 Transaction Kanıtım

Yaptığım:

`BEGIN;`

Sonra:

`rollback-owner`

isimli owner ekledim.

Transaction içindeyken SELECT'te gördüm.

Sonra:

`ROLLBACK;`

Tekrar SELECT:

`0 rows`

Bu:

> Transaction içindeki INSERT'in rollback ile iptal edildiğini

kanıtladı.

---

# 💾 Persistence Kanıtım

Database'e:

`persist-38.local`

asset'i ekledim.

Sonra:

`docker compose down`

ile container kaldırıldı.

Ardından:

`docker compose up -d`

ile tekrar ayağa kaldırıldı.

İlk sorguda yanlışlıkla:

`owners`

tablosunda `hostname` aradım.

PostgreSQL:

`column "hostname" does not exist`

dedi.

Doğru tablo:

`assets`

idi.

Doğru sorguda:

`persist-38.local`

geldi.

Bu:

> **Container silinmesine rağmen database state'in volume sayesinde yaşadığını**

kanıtladı.

---

# 📦 Volume Kanıtı

`docker volume ls`

sonucunda:

`day38-postgres_pgdata`

volume'ünü gördüm.

`docker volume inspect` içinde:

`Name = day38-postgres_pgdata`

ve Docker'ın bildirdiği:

`Mountpoint = /var/lib/docker/volumes/day38-postgres_pgdata/_data`

gibi metadata gördüm.

Burada:

> Docker volume metadata'sı bir katman.

> PostgreSQL'in container içinde gördüğü `/var/lib/postgresql` başka katman.

Mount bunları birbirine bağlıyor.

---

# 💾 PostgreSQL Backup

Database'in logical backup'ını aldım.

    PostgreSQL database
          ↓
       pg_dump
          ↓
        stdout
          ↓
           >
          ↓
    evidence/coreops.sql

---

# 🐘 `pg_dump`

`pg_dump`

→ PostgreSQL logical backup aracı.

`psql`

→ database'e SQL gönder.

`pg_dump`

→ database state'ini dışarı dök.

---

# 🧪 Backup Komutum

    docker compose exec -T db \
      pg_dump -U coreops coreops \
      > evidence/coreops.sql

Parçaları:

`docker compose exec`

→ çalışan db container'ında command çalıştır.

`-T`

→ pseudo-TTY açma.

`pg_dump`

→ logical dump al.

`-U coreops`

→ PostgreSQL user.

`coreops`

→ database.

`> evidence/coreops.sql`

→ stdout'u host'taki dosyaya yönlendir.

---

# 🧠 `>` Hangi Tarafta Çalışıyor?

`pg_dump`

container içinde çalışıyor.

Ama:

`> evidence/coreops.sql`

host shell tarafından yorumlanıyor.

    Container
    pg_dump
       ↓
    stdout
       ↓
    docker exec
       ↓
    Mac shell
       ↓
       >
       ↓
    evidence/coreops.sql

Sonuç:

> Backup dosyası host/Mac tarafında oluşuyor.

---

# 🧠 Logical Backup

Burada volume directory'sinin raw byte kopyasını almıyorum.

`pg_dump` database'in:

- schema
- table yapıları
- data
- constraints
- sequences

gibi logical state'ini yeniden oluşturulabilecek şekilde dışarı çıkarıyor.

Bu yüzden:

> **Logical backup**

---

# 🔍 Dump İçinde Ne Gördüm?

Backup'ta:

`CREATE TABLE public.assets`

`CREATE TABLE public.owners`

vardı.

Data:

`COPY public.assets ...`

`COPY public.owners ...`

ile dump edilmişti.

Dump içerisinde:

- `polat_1`
- `polat_2`
- `kerem_1`
- `kerem_2`
- `persist-38.local`

gibi veriler vardı.

Constraint'ler de dump içindeydi:

- primary key
- unique
- foreign key
- risk check

Bu backup'ın boş artifact olmadığını gösteren güçlü kanıt oldu.

---

# ⚠️ File Exists ≠ Valid Backup

Sadece:

`coreops.sql var`

demek yeterli değil.

Dosya:

`0 bytes`

olabilir.

> Dosyanın varlığı tek başına backup'ın sağlam olduğunu kanıtlamaz.

İçerik veya size gibi ikinci kanıt gerekir.

---

# 🆚 Source SQL vs Generated Backup

Source:

`schema.sql`

`seed.sql`

Generated artifact:

`evidence/coreops.sql`

Kısa:

    schema.sql / seed.sql
    = source

    coreops.sql
    = generated backup artifact

---

# 🙈 `.gitignore`

İlk pattern:

`./evidence/coreops.sql`

Sonra daha genel:

`evidence/*.sql`

Anlam:

> `evidence` klasöründeki `.sql` backup dosyalarını ignore et.

---

# ✅ `.gitignore` Kanıtı

Sadece `.gitignore` dosyasına bakmak yerine:

`git check-ignore -v evidence/coreops.sql`

çalıştırdım.

Çıktıda:

`evidence/*.sql`

rule'unun `coreops.sql` dosyasını ignore ettiğini gördüm.

Bu daha güçlü kanıt.

---

# ⚠️ `.gitignore` Daha Önce Tracked Dosyayı Otomatik Çıkarmaz

Önemli Git kuralı:

> `.gitignore`, daha önce tracked olan dosyayı otomatik olarak tracking'den çıkarmaz.

Backup dosyam yeni generated artifact olduğu için burada sorun olmadı.

---

# 📸 Staged Snapshot Mantığı

Commit öncesi kontrol:

> Backup yanlışlıkla staging area'ya girdi mi?

Git modeli:

    Working Tree
    → şu anki dosyalar

    Index / Staging Area
    → bir sonraki commit snapshot'ı

Commit öncesi staged içeriği kontrol etmek önemli.

---

# 🐧 `findmnt`

Günün Linux tarafındaki yeni aracı:

`findmnt`

Bu:

- Docker command değil
- PostgreSQL command değil

Genel Linux mount topology inspection aracı.

---

# 🔗 Docker ile `findmnt` İlişkisi

Başta:

> Bunun Docker'la alakası var mı yoksa tamamen bağımsız mı?

diye düşündüm.

Doğru model:

    Linux mount mekanizması
             ↑
             │
    Docker volume / bind mount

Docker bu temel filesystem mekanizmasından yararlanıyor.

`findmnt` ise gerçekleşmiş Linux mount state'ini gözlemliyor.

Kısa:

    mount
    → Linux filesystem mekanizması

    Docker volume
    → Docker storage resource'u

    findmnt
    → mount state'ini gözlemleme aracı

Docker mount oluşturabilir.

`findmnt` mount'u gözlemleyebilir.

Ama `findmnt` için Docker şart değil.

---

# 🍎 Mac'te Neden `findmnt` Yapmadım?

Labın Linux kısmını Ubuntu VM'de yaptım.

macOS'ta native Linux `findmnt` ortamı olmadığı için gerçek Linux tarafında denedim.

Ayrıca Ubuntu VM:

> Mac'teki Docker Desktop storage'ını veya proje dosyalarını otomatik olarak görmüyor.

Bunlar ayrı sistemler.

---

# 🖥️ Ubuntu VM'in Bomboş Olması Problem Değildi

İlk başta:

> Ubuntu VM'de proje dosyaları yok, nasıl yapacağım?

diye düşündüm.

Ama temel `findmnt` görevi proje dosyalarına bağlı değildi.

Sadece gerçek Linux path'lerini incelemek yeterliydi.

Bu yüzden:

`$PWD`

ve:

`/tmp`

üzerinde çalıştım.

---

# 🔍 `findmnt -T`

Mental model:

`findmnt -T PATH`

şunu soruyor:

> **Bu path hangi mounted filesystem üzerinde yaşıyor?**

Path'in kendisinin mount point olması şart değil.

Onu kapsayan filesystem bulunabilir.

---

# 🧪 `$PWD` Testim

Çalıştırdığım:

`findmnt -T "$PWD" -o TARGET,SOURCE,FSTYPE,OPTIONS`

Current directory:

`~/çalışma`

Çıktı:

    TARGET  /
    SOURCE  /dev/mapper/ubuntu--vg-ubuntu--lv
    FSTYPE  ext4
    OPTIONS rw,relatime ...

Anlamı:

> `~/çalışma` ayrı mount point değil; root `/` filesystem'i üzerinde yaşıyor.

---

# 🧪 `/tmp` Testim

Çalıştırdığım:

`findmnt -T /tmp -o TARGET,SOURCE,FSTYPE,OPTIONS`

Çıktı:

    TARGET  /tmp
    SOURCE  tmpfs
    FSTYPE  tmpfs
    OPTIONS rw,nosuid,nodev,...

Bu Ubuntu VM'de:

`/tmp`

ayrı bir `tmpfs` mount'u.

---

# 🧠 İki Path, İki Farklı Filesystem

`~/çalışma`:

    /
     ↓
    ext4

`/tmp`:

    /tmp
      ↓
    tmpfs

Bu sayede tek Linux directory tree içinde farklı path'lerin farklı mounted filesystem'lerde yaşayabileceğini gördüm.

---

# `findmnt` Output Alanları

## TARGET

Filesystem'in mount edildiği path.

Örnek:

`/`

`/tmp`

## SOURCE

Mount kaynağı.

Örnek:

`/dev/mapper/ubuntu--vg-ubuntu--lv`

veya:

`tmpfs`

## FSTYPE

Filesystem tipi.

Labda:

`ext4`

`tmpfs`

gördüm.

## OPTIONS

Mount runtime seçenekleri.

Örnek:

`rw`

`relatime`

`nosuid`

`nodev`

Burada amaç hepsini ezberlemek değil.

> Mount'un runtime options/state'i olduğunu anlamak.

---

# 🆚 Mac Docker ve Ubuntu VM

Mimari:

    Mac
    ├── proje dosyaları
    └── Docker Desktop
        └── kendi Linux katmanı

    Ubuntu VM
    └── ayrı Linux sistemi

Bu yüzden Ubuntu VM:

> Mac Docker Desktop volume mountpoint'ini direkt göremez.

Docker volume Mountpoint'ine `findmnt -T` uygulamak için Docker ve `findmnt`'nin aynı Linux sisteminde olması gerekir.

Benim ortamımda bu ekstra kısım yoktu.

---

# ✅ `findmnt` Görevi İçin Kanıtım

İki path inceledim:

1. `$PWD`
2. `/tmp`

Ve:

- TARGET
- SOURCE
- FSTYPE
- OPTIONS

bilgilerini okuyabildim.

Öğrenme hedefi:

> **Bir path'in Linux mount topology içindeki yerini okuyabilmek.**

---

# 🐞 Gün 38 — Hata Avı

## 1. PostgreSQL, volume ve mount aynı şey

TIRT.

Farklı katmanlar.

## 2. Mount dosyaları target'a kopyalar

TIRT.

Mount copy değildir.

## 3. Mount yapınca target path değişmeli

TIRT.

Path aynı kalabilir; arkasında görünen tree değişir.

## 4. Volume ile mount aynı şey

TIRT.

    Volume
    → storage resource

    Mount
    → resource'u path'e bağlama mekanizması

## 5. Compose'taki iki `volumes:` aynı şeyi tekrar ediyor

TIRT.

    top-level
    → volume resource tanımı

    service-level
    → volume'ü container path'ine mount et

## 6. YAML environment mapping'inde `- KEY: VALUE`

Benim kullanımım için yanlıştı.

`-` liste oluşturdu.

## 7. Top-level `volumes:` services altında olmalı

TIRT.

`services:` ile aynı top-level seviyede.

## 8. PostgreSQL string `"Polat"` şeklinde yazılır

TIRT.

Text literal:

`'Polat'`

## 9. SQL statement sonunda `;` önemsiz

TIRT.

Statement'ın tamamlandığını belirtiyor.

## 10. SQL'i `psql ... SELECT ...` şeklinde CLI argümanı olarak vermek

Interactive kullanımda yanlış.

## 11. `SELECT FROM assets`

TIRT.

SELECT sonrası neyi göstereceğimi belirtmeliyim.

## 12. `risk > 50` 50'yi içerir

TIRT.

`>` strict greater-than.

## 13. JOIN bir çeşit WHERE filtresidir

TIRT.

JOIN row source'ları relation üzerinden eşleştirir.

## 14. JOIN sonrası owner adı için `assets.owner_id` göstermeliyim

TIRT.

Görev owner adı istiyorsa:

`owners.name`

## 15. GROUP BY sayma işlemini yapar

TIRT.

GROUP BY gruplar.

`COUNT(*)` sayar.

## 16. ROLLBACK bütün database'i geçmişe sarar

TIRT.

Current transaction'ın commit edilmemiş etkilerini iptal eder.

## 17. Backup dosyası oluştuysa backup kesin sağlamdır

TIRT.

Boş olabilir.

## 18. `.gitignore` satırını yazdıysam çalıştığını kanıtladım

TIRT.

`git check-ignore -v`

ile doğrulamak daha sağlam.

## 19. `findmnt` Docker komutudur

TIRT.

Genel Linux mount inspection aracı.

## 20. Ubuntu VM'de Mac proje dosyaları yoksa `findmnt` görevini yapamam

TIRT.

Temel test için mevcut Linux path'leri yeterli.

## 21. İlk persistence sorgumda PostgreSQL bozuldu

TIRT.

Yanlış tabloya sorgu atmıştım.

`hostname` kolonu `owners` değil `assets` tablosundaydı.

---

# 🧠 Kafaya Kazı

> [!quote]
> SQL PostgreSQL'e ne yapacağını söyler.

> [!quote]
> PostgreSQL logical table state'ini fiziksel database dosyalarında tutar.

> [!quote]
> Container runtime'dır; volume storage'dır.

> [!quote]
> Mount copy değildir.

> [!quote]
> Mount'ta source başka, target başka kavramdır.

> [!quote]
> Path aynı kalabilir; path'in arkasında görünen filesystem değişebilir.

> [!quote]
> Top-level volume resource'u tanımlar; service volume onu kullanır.

> [!quote]
> Bind mount host path'ini, named volume Docker-managed storage'ı container path'ine bağlayabilir.

> [!quote]
> SELECT hangi kolonları, WHERE hangi satırları istediğimi söyler.

> [!quote]
> WHERE filtreler, JOIN eşleştirir.

> [!quote]
> JOIN ilişkiyi kurar, ON eşleşme kuralını verir.

> [!quote]
> GROUP BY gruplar, COUNT/SUM/AVG gibi aggregate'ler hesaplar.

> [!quote]
> COMMIT transaction'ı tamamlar; ROLLBACK current transaction'ın commit edilmemiş etkisini geri alır.

> [!quote]
> `psql` PostgreSQL server değil, client'tır.

> [!quote]
> `pg_dump` logical backup üretir.

> [!quote]
> `>` host shell tarafından yorumlanıyorsa container stdout'u host dosyasına yazılabilir.

> [!quote]
> `.gitignore` varsayım değil; `git check-ignore -v` ile kanıtlanabilir.

> [!quote]
> `findmnt -T PATH` o path'in hangi mounted filesystem üzerinde yaşadığını gösterir.

---

# 📌 30 Saniyelik Özet

    SQL
     ↓
    PostgreSQL
     ↓
    logical tables
     ↓
    database files
     ↓
    /var/lib/postgresql
     ↓
    MOUNT
     ↓
    pgdata
     ↓
    persistence


    schema.sql
    → database yapısını oluştur

    seed.sql
    → başlangıç verisini ekle

    psql
    → PostgreSQL ile konuşan CLI client


    SELECT
    → neyi?

    FROM
    → nereden?

    JOIN
    → başka row source'u ilişkiye kat

    ON
    → neye göre eşleşsin?

    WHERE
    → hangi row'lar?

    GROUP BY
    → hangi gruplar?

    COUNT / SUM / AVG
    → grup üzerinde hangi hesap?


    BEGIN
    → transaction başlat

    COMMIT
    → değişiklikleri tamamla

    ROLLBACK
    → current transaction değişikliklerini geri al


    pgdata:/var/lib/postgresql
    → named volume → database persistence

    ./sql:/lab/sql:ro
    → host source SQL → container'a read-only bind mount


    pg_dump
    → logical backup

    evidence/coreops.sql
    → generated artifact

    git check-ignore -v
    → ignore rule'unu kanıtla


    findmnt -T PATH
    → bu path hangi mount üzerinde?

    TARGET
    → mount point

    SOURCE
    → mount kaynağı

    FSTYPE
    → filesystem tipi

    OPTIONS
    → mount seçenekleri

---

# 🗺️ Günün Tek Büyük Mimarisi

    HOST
    │
    ├── compose.yaml
    │
    ├── sql/
    │   ├── schema.sql
    │   └── seed.sql
    │        │
    │        │ bind mount :ro
    │        ↓
    │   Container /lab/sql
    │
    └── evidence/coreops.sql
             ↑
             │ shell redirect >
             │
          pg_dump stdout
             ↑
             │

    +---------------- POSTGRESQL CONTAINER ----------------+
    |                                                      |
    |   PostgreSQL process                                 |
    |           │                                          |
    |           ↓                                          |
    |   logical database                                   |
    |           │                                          |
    |           ↓                                          |
    |   database files                                     |
    |           │                                          |
    |           ↓                                          |
    |   /var/lib/postgresql                                |
    |           │                                          |
    +-----------│------------------------------------------+
                │
              MOUNT
                │
                ↓
             pgdata
          NAMED VOLUME
                │
                ↓
       PERSISTENT DATABASE STATE

---

# ✅ Günün Kazanımları

- [x] PostgreSQL process ile logical database ayrıldı
- [x] Table ile physical database files ayrıldı
- [x] Named volume persistence mantığı oturdu
- [x] Container ve volume ayrıldı
- [x] PostgreSQL 18 storage path konusu öğrenildi
- [x] Mount'un Docker'a özgü olmadığı öğrenildi
- [x] Mount'un copy olmadığı oturdu
- [x] Source / target / mount point ayrıldı
- [x] Mount shadowing davranışı öğrenildi
- [x] Bind mount ile named volume ayrıldı
- [x] PostgreSQL'in sadece container path'ini gördüğü anlaşıldı
- [x] Compose'taki iki `volumes:` ayrıldı
- [x] YAML list vs mapping farkı gerçek hatayla öğrenildi
- [x] YAML indentation'ın yapının kendisi olduğu tekrarlandı
- [x] PostgreSQL Compose lab kuruldu
- [x] Host/container PostgreSQL port mapping kullanıldı
- [x] `schema.sql` ile tablo yapısı oluşturuldu
- [x] `seed.sql` ile başlangıç verileri eklendi
- [x] Primary key / identity mantığı kullanıldı
- [x] UNIQUE / NOT NULL constraint'leri görüldü
- [x] Foreign key relation kuruldu
- [x] CHECK constraint kullanıldı
- [x] SQL string literal quoting düzeltildi
- [x] SQL statement terminator `;` davranışı gözlemlendi
- [x] `psql` client/server ayrımı oturdu
- [x] Shell prompt ve psql prompt ayrıldı
- [x] `SELECT` mantığı oturdu
- [x] `WHERE` ile row filtering yapıldı
- [x] `>` / `>=` farkı pratikte görüldü
- [x] JOIN relation mantığı oturdu
- [x] `assets.owner_id = owners.id` relation kullanıldı
- [x] Owner adı `owners.name` üzerinden getirildi
- [x] GROUP BY mantığı oturdu
- [x] `COUNT(*)` ile group row'ları sayıldı
- [x] WHERE ve HAVING ayrıldı
- [x] Transaction mantığı öğrenildi
- [x] BEGIN / COMMIT / ROLLBACK ayrıldı
- [x] ROLLBACK gerçek experiment ile kanıtlandı
- [x] Container down/up sonrası database persistence kanıtlandı
- [x] Named volume `docker volume inspect` ile görüldü
- [x] `pg_dump` ile logical backup alındı
- [x] Container stdout'unun host redirect ile dosyaya yazılması öğrenildi
- [x] Backup dump içeriği kontrol edildi
- [x] Generated backup source dosyalarından ayrıldı
- [x] `.gitignore` pattern düzeltildi
- [x] `git check-ignore -v` ile ignore davranışı kanıtlandı
- [x] Linux `findmnt` aracı öğrenildi
- [x] Docker volume ile Linux mount mekanizması arasındaki ilişki kuruldu
- [x] `$PWD` path'inin root ext4 filesystem üzerinde olduğu gözlemlendi
- [x] `/tmp` path'inin tmpfs üzerinde olduğu gözlemlendi
- [x] TARGET / SOURCE / FSTYPE / OPTIONS alanları okundu
- [x] Mac Docker Desktop ile ayrı Ubuntu VM'in aynı Linux ortamı olmadığı anlaşıldı

---

# 🚀 Gün Sonu Sonucu

Artık database konusunu tek kutu olarak görmüyorum.

Ben SQL yazıyorum:

    SQL
     ↓
    PostgreSQL process

PostgreSQL logical state'i yönetiyor:

    owners
    assets
    relations
    constraints
    transactions

Bunun fiziksel karşılığı:

    database files

Bu dosyaların container lifecycle'ından bağımsız yaşamasını istiyorsam:

    database files
         ↓
    container path
         ↓
       mount
         ↓
    named volume

kullanıyorum.

Veriyi dışarı almak istersem:

    database
       ↓
    pg_dump
       ↓
    logical backup

Filesystem gerçeğini kontrol etmek istersem:

    PATH
      ↓
    findmnt -T
      ↓
    mounted filesystem state

Günün en kritik cümlesi:

> **SQL PostgreSQL'e ne yapacağını söyler; PostgreSQL veriyi kendi database dosyalarında tutar; mount bu dosyaların yazıldığı container path'ini persistent storage'a bağlayabilir; named volume sayesinde container recreate edilse bile database state'i yaşayabilir.**