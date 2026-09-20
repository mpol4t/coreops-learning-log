---
title: "Gün 52 — CoreOps Final | Python + systemd + Docker"
tags:
  - coreops
  - day52
  - final
  - python
  - argparse
  - pathlib
  - generator
  - islice
  - pytest
  - systemd
  - docker
  - bind-mount
  - debugging
aliases:
  - "Gün 52 CoreOps Final"
status: completed
---

# 🏁 Day 52 — CoreOps Final | Python + systemd + Docker

> [!note] 20 Eylül arşiv denetimi
> Mentor finali 19 Eylül'de GEÇTİ olarak kapattı. Öğrencinin özgün finalinde 6 test vardı. Denetimde aynı input/output dosyasının üzerine yazılabildiği bulundu; GitHub arşivine Codex tarafından koruma ve 3 regresyon testi eklendi (final: 9 test). Bu bakım öğrencinin bağımsız final kanıtına eklenmez. `islice` lazy kalır, fakat `build_report()` liste oluşturduğu için tüm akış sabit bellekli değildir.

> [!abstract] 🎯 Ana fikir
> Bugün yeni konu doldurmaktan çok mevcut sistemi **requirement değişikliği ve runtime arızaları altında doğru teşhis edip minimum değişiklikle düzeltmeye** çalıştım.
>
> Günün ortak zinciri:
>
>     requirement / symptom
>             ↓
>           kanıt
>             ↓
>       failure boundary
>             ↓
>         kök neden
>             ↓
>       minimum fix
>             ↓
>       tekrar kanıt
>
> Final üç parçaydı:
>
>     PYTHON
>     → CLI requirement değişikliği
>
>     LINUX
>     → systemd execution context arızası
>
>     DOCKER
>     → read-only bind mount arızası
>
> Finalin temel amacı da buydu.

---

# 1️⃣ Final Hazırlık — `--max-records`

Finalden önce mevcut report tool'a:

    --max-records

özelliğini ekledim.

İstenen davranış:

    flag yok
    → bütün kayıtlar

    --max-records 2
    → ilk 2 kayıt

    0 / negatif
    → CLI error

Config:

    max_records: int | None = None

Burada:

    int | None
    → kabul edilen tip

    = None
    → default değer

`None` burada:

> **limit verilmedi**

demek.

---

## Generator'ı bozmadan limit uygulamak

`iter_records()` generator döndürüyor.

Bu yüzden:

    records[:2]

kullanamam.

Generator:

    indexlenebilir sequence ❌

Bunun yerine:

    islice(records, 2)

kullandım.

Akış:

    iter_records()
         ↓
      generator
         ↓
    max_records var mı?
         ↓
      islice()
         ↓
    build_report()

`islice` bütün kayıtları önce listeye çevirmiyor.

Yani streaming mantığını koruyor.

---

## 🐞 `max-records` kısmında yaptığım hatalar

- `max_records` sadece `int` olur sandım; halbuki limit verilmemesi için `None` gerekiyor.
- `int | None` ile `= None` farkını karıştırdım.
- CLI'da parse ettiğim değeri `ReportConfig` içine aktarmayı unuttum.
- `None > 0` karşılaştırmasına gidecek yanlış validation düşündüm.
- CLI hatasında `ValueError` düşündüm; doğru sınır `parser.error()`.
- Generator'ı liste gibi slice etmeye çalıştım.
- Aynı generator'ı iki kez processing'e sokmaya çalıştım.
- `islice()` sonucunu `report` sanıp yanlış değişkeni değiştirdim.

Doğru validation:

    max_records verilmiş
    VE
    <= 0
    → parser.error()

Final pytest:

    3 passed ✅

ve:

    limit yok → 3 kayıt
    limit 2   → 2 kayıt
    limit 0   → CLI error
    limit -1  → CLI error

olarak doğrulandı.

---

# 2️⃣ PYTHON FINAL — `--output` Artık Opsiyonel

Yeni requirement:

    --output

artık zorunlu olmayacak.

Örneğin:

    input:
    data.jsonl

    format:
    json

otomatik:

    data.report.json

CSV ise:

    data.report.csv

oluşmalı.

Ama kullanıcı:

    --output benim-sonucum.json

verirse explicit seçim korunmalı.

---

# 🐞 Sadece `required=True` Kaldırmak Yetmiyor

İlk düşüncem:

    parser.add_argument("--output", required=True)

içinden sadece:

    required=True

kaldırmaktı.

Ama aşağıda:

    Path(args.output)

vardı.

Output verilmezse:

    args.output = None

olur.

Sonra:

    Path(None)

patlar.

Yani requirement değişikliği sadece argparse satırı değil:

> **Output path seçim mantığını da değiştirmeyi gerektiriyordu.**

---

# 📁 `Path.stem`

Burada `pathlib` tarafında:

    p.name
    → data.jsonl

    p.stem
    → data

    p.suffix
    → .jsonl

    p.parent
    → bulunduğu klasör

mantığını oturttum.

Önemli detay:

    Path("backup.tar.gz").stem
    → backup.tar

Çünkü sadece son suffix çıkar.

---

# 🧠 Output Path Nerede Belirlenmeli?

İlk fikir:

    ReportConfig.output_path
    → Path | None

ve sonra:

    run()
    → output yoksa üret

idi.

Daha temiz çözüm:

    CLI
     ↓
    parse_config()
     ↓
    output path KESİNLEŞİR
     ↓
    ReportConfig
     ↓
    run()

Böylece `run()`:

> Output neden böyle seçildi?

bilmek zorunda değil.

Config'e geldiğinde:

    output_path

artık kesin bir `Path`.

---

# 🧪 Test Edilebilir `parse_config`

Finalde:

    def parse_config(argv=None):

kullandım.

Normal:

    parse_config()

→ terminal argümanlarını okur.

Test:

    parse_config([
        "--input", "...",
        "--format", "json"
    ])

→ verilen listeyi okur.

Böylece `sys.argv` monkeypatch etmek zorunda kalmadım.

---

# ✅ Python Final Kanıtı

Eski davranışlar:

    CSV report
    JSON report
    max_records=2

Yeni davranışlar:

    explicit output korunuyor
    implicit JSON path
    implicit CSV path

Toplam:

    6 test

Sonuç:

    6 passed ✅

Manuel:

    --output yok
    → sample.report.json ✅

    --output benim-sonucum.json
    → benim-sonucum.json ✅

Yani requirement değişti ama processing pipeline'ı gereksiz yere yeniden yazmadım.

---

# 🐞 Python Finalde Input Hatası

İlk implicit CLI demosunda:

    ValueError:
    Gelen veri boş olmamalı!

aldım.

İlk anda yeni output değişikliğine bağlanabilirdi.

Ama traceback:

    main
      ↓
    run
      ↓
    build_report
      ↓
    iter_records
      ↓
    boş satır

diyordu.

Yani output requirement'ıyla alakası yoktu.

Mevcut reader contract'ı:

    blank line
    → ValueError

Input'u düzelttikten sonra aynı output özelliği sorunsuz çalıştı.

> **Yeni değişiklik yaptım diye çıkan her hata yeni değişiklikten kaynaklanmaz.**

---

# 3️⃣ LINUX FINAL — systemd Relative Path Fault

Senaryo:

    terminalden uygulama çalışıyor ✅
    systemd service çalışmıyor ❌

CLI baseline:

    python3 final.py \
      --input sample.jsonl \
      --output report.json

çıktısı:

    total_records = 3 ✅

Yani programın kendisi sağlam.

---

# 💥 Bilerek Bozuk Unit

Unit'te:

    WorkingDirectory=/tmp

ama:

    --input sample.jsonl

kullandım.

Input relative path.

Temel formül:

    relative path
         +
    current working directory
         =
    gerçek çözülen path

Dolayısıyla service:

    /tmp
      +
    sample.jsonl
      =
    /tmp/sample.jsonl

aramaya başladı.

Gerçek dosya ise:

    /home/polat/Masaüstü/coreops-learning/Final/sample.jsonl

idi.

---

# 🔎 Kanıt Zinciri

Service:

    failed

Status:

    FileNotFoundError:
    sample.jsonl

Journal:

    No such file or directory:
    'sample.jsonl'

Unit:

    WorkingDirectory=/tmp
    --input sample.jsonl

Böylece sorun:

    permission ❌
    Python executable ❌
    uygulama kodu ❌

değil:

    execution context / CWD ✅

oldu.

---

# 🔧 Minimum Linux Fix

Şunları yapmadım:

    Python kodunu değiştirme ❌
    chmod yağdırma ❌
    input'u absolute yapıp problemi gizleme ❌

Sadece:

    WorkingDirectory=/tmp

yerine:

    WorkingDirectory=/home/polat/Masaüstü/coreops-learning/Final

yaptım.

Sonra:

    daemon-reload
        ↓
    service start
        ↓
    Finished coreops-final.service ✅
        ↓
    report.json ✅
        ↓
    total_records = 3 ✅

---

# ⚠️ `inactive (dead)` Yine Korkutmadı

Service:

    Type=oneshot

olduğu için başarılı işlem sonrası:

    inactive (dead)

normal.

Doğru yorum:

    başladı
      ↓
    işi yaptı
      ↓
    exit 0
      ↓
    process bitti
      ↓
    inactive

Başarıyı sadece:

    Active:

satırından değil:

    journal
    exit durumu
    üretilen output

ile birlikte okuyorum.

---

# 4️⃣ DOCKER FINAL — Read-Only Bind Mount

Final container:

    USER appuser
    uid=10001

ile non-root çalışıyor.

Filesystem tasarımı:

    /lab/src
    → source code
    → yazılmamalı

    /lab/runtime
    → runtime output
    → yazılmalı

App:

    /lab/runtime/report.json

yazıyor.

---

# 💣 Bilerek Bozuk Compose

Mount:

    ./runtime:/lab/runtime:ro

Buradaki:

    :ro

mount'u read-only yapıyor.

`docker compose config` bunu:

    target: /lab/runtime
    read_only: true

olarak gösterdi.

---

# 💥 Gerçek Hata

Container log:

    output_path=/lab/runtime/report.json

ardından:

    OSError: [Errno 30]
    Read-only file system:
    '/lab/runtime/report.json'

ve:

    exited with code 1

geldi.

---

# 🐞 İlk Teşhis Hatası

İlk yorumum:

> appuser'ın permission'ı yok.

**TIRT.**

Çünkü:

    Permission denied

ile:

    Read-only file system

aynı problem değil.

İki katman:

    FILE PERMISSIONS
    ─────────────────
    owner
    group
    chmod
    user

    → bu kullanıcı yazabilir mi?


    MOUNT STATE
    ─────────────────
    rw / ro

    → filesystem'e yazmak açık mı?

Bizim hata:

    Errno 30
    Read-only file system

Yani sorun:

    appuser ❌
    chmod ❌
    owner ❌

değil:

    mount rw/ro state ✅

idi.

---

# 🔐 Root Bile Çözmez

Kafaya kazı:

    appuser + rw + doğru permission
    → yazabilir

    appuser + ro
    → yazamaz

    root + ro
    → yine yazamaz

Yani:

    USER root

yapmak çözüm değil.

Hem arızanın gerçek nedenini çözmez hem de güvenliği geriletir.

---

# 🔧 Minimum Docker Fix

Eski:

    ./runtime:/lab/runtime:ro

Yeni:

    ./runtime:/lab/runtime

Sadece:

    :ro

kaldırıldı.

Sonra container recreate edildi.

Log:

    output_path=/lab/runtime/report.json
    report_written=true
    exit code 0 ✅

Host:

    runtime/report.json ✅

İçerik:

    {
      "status": "ok",
      "total_records": 3
    }

Runtime inspect:

    destination=/lab/runtime
    rw=true ✅

Non-root:

    user=appuser ✅

Yani problemi çözmek için root'a dönmedim.

---

# 🛡️ Source Hâlâ Korunuyor mu?

Kontrol:

    uid=10001(appuser)

Sonra:

    touch /lab/src/...

çıktısı:

    Permission denied

Bu burada başarı.

Final permission modeli:

    /lab/src
    → writable değil ✅

    /lab/runtime
    → writable ✅

> **Least privilege bozulmadan runtime ihtiyacı karşılandı.**

---

# 💾 Persistence Kanıtı

Output oluştu:

    host ./runtime/report.json

Sonra:

    docker compose down

Container silindi.

Kontrol:

    docker compose ps -a
    → boş

Ama:

    runtime/report.json

hâlâ host'taydı.

Sebep:

    HOST
    ./runtime/report.json
           ↕
       bind mount
           ↕
    CONTAINER
    /lab/runtime/report.json

Dosya container writable layer'ında değil.

Host filesystem'de yaşıyor.

Bu yüzden:

    container remove
        ↓
    host dosyası kalır ✅

---

# 🐞 Günün Önemli Hataları

### Python

- `Path + str` yapmaya çalıştım.
- `stem` mantığını bilmiyordum.
- `output_path=None` kararını `run()`a taşımayı düşündüm.
- `max_records` değerini generator katmanına gömmeye yaklaştım.
- Generator'ı iki kez tüketmeye çalıştım.

### Linux

- Gerçek dosyanın bulunduğu path ile **service'in aradığı path'i** karıştırdım.
- Relative path'in CWD'ye göre çözüldüğünü tekrar kanıtladım.

### Docker

- `Read-only file system` hatasını kullanıcı permission problemi sandım.
- Root'a geçmenin mount state problemini çözmeyeceğini oturttum.

---

# 🧠 Kafaya Kazı

> [!tip]
> **`None` = limit verilmedi.**

> [!tip]
> **Generator + limit → `islice()`**

> [!danger]
> **Generator tüketildikçe ilerler; otomatik başa dönmez.**

> [!tip]
> **CLI parsing ≠ processing**

> [!tip]
> **Explicit config > automatic default**

> [!tip]
> **`stem` = son suffix çıkarılmış dosya adı**

> [!danger]
> **Relative path + WorkingDirectory = gerçek aranan path**

> [!tip]
> **Oneshot sonrası `inactive (dead)` normal olabilir.**

> [!danger]
> **Permission denied ≠ Read-only file system**

> [!tip]
> **`rw=false` = mount read-only**

> [!tip]
> **`rw=true` = mount writable**

> [!danger]
> **Root, read-only mount'u sihirli şekilde writable yapmaz.**

> [!tip]
> **Bind mount output host'ta yaşar; container silinse de kalabilir.**

---

# 📌 30 Saniyelik Özet

    PYTHON

    --output yok
        ↓
    input.stem
        ↓
    otomatik report adı
        ↓
    config kesinleşir
        ↓
    run değişmez
        ↓
    6 passed ✅


    LINUX

    CLI ✅
    systemd ❌
       ↓
    FileNotFoundError
       ↓
    WorkingDirectory=/tmp
       +
    relative sample.jsonl
       ↓
    /tmp/sample.jsonl
       ↓
    yanlış CWD
       ↓
    WorkingDirectory düzelt
       ↓
    service ✅


    DOCKER

    appuser
      +
    /lab/runtime
      +
    mount :ro
       ↓
    Errno 30
    Read-only filesystem
       ↓
    rw=false
       ↓
    :ro kaldır
       ↓
    rw=true
       ↓
    report_written=true
       ↓
    host output ✅
       ↓
    source protection ✅
       ↓
    persistence ✅

---

# ✅ Final Kanıt Zinciri

## Python

    max-records tests → 3 passed ✅
    final tests       → 6 passed ✅
    implicit output   → sample.report.json ✅
    explicit output   → kullanıcı path'i korundu ✅

## Linux

    CLI baseline ✅
    FileNotFoundError gözlendi ✅
    yanlış CWD kanıtlandı ✅
    yalnız WorkingDirectory düzeltildi ✅
    oneshot başarıyla tamamlandı ✅
    report.json oluştu ✅

## Docker

    container non-root ✅
    rw=false arızası kanıtlandı ✅
    :ro kaldırıldı ✅
    rw=true kanıtlandı ✅
    report_written=true ✅
    host output oluştu ✅
    /lab/src writable değil ✅
    container silindikten sonra output kaldı ✅

---

# 🚀 CoreOps Final

> **Bugünün asıl öğrendiğim şeyi tek cümlede:**
>
> **Bir şey çalışmıyorsa önce değiştirme. Hangi katmanda, hangi gerçek runtime state yüzünden çalışmadığını kanıtla; sonra sadece gereken yeri düzelt.**
>
>     symptom
>       ↓
>     evidence
>       ↓
>     boundary
>       ↓
>     root cause
>       ↓
>     minimum fix
>       ↓
>     regression proof
>
> **PYTHON ✅
> LINUX ✅
> DOCKER ✅
> COREOPS FINAL ✅**
