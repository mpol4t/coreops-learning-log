---
title: "Gün 51 — Serializer Ayrımı ve Bağımsız Fault Debugging"
tags:
  - coreops
  - day51
  - python
  - jsonl
  - csv
  - serializer
  - pytest
  - systemd
  - docker
  - debugging
  - bind-mount
aliases:
  - "Gün 51 Serializer Fault Debugging"
status: completed
---

# 🧩 Day 51 — Serializer Ayrımı + Bağımsız Fault Debugging

> [!abstract] 🎯 Ana fikir
> Bugün iki farklı şeyi çalıştım:
>
> **Blok 1:** Aynı processing sonucunu JSON veya CSV olarak yazmak.
>
> **Blok 2:** Kod değiştirmeye atlamadan Linux/systemd ve Docker arızalarında kanıt toplayıp kök nedeni bulmak.
>
>     INPUT
>       ↓
>     PROCESS
>       ↓
>     ORTAK REPORT
>       ↓
>     JSON / CSV
>
>
>     SEMPTOM
>       ↓
>     KANIT
>       ↓
>     KÖK NEDEN
>       ↓
>     MINIMUM FIX
>       ↓
>     DOĞRULAMA
>
> Günün ortak dersi:
>
> **Katmanları birbirine karıştırma. Her katmana sadece kendi işini yaptır.**

---

# 1️⃣ BLOK 1 — JSONL → Report → JSON / CSV

Final programımda config artık üç bilgi taşıyor:

    input_path
    output_path
    output_format

`--format` için:

    json
    csv

destekleniyor.

Kod akışı:

    argparse
       ↓
    ReportConfig
       ↓
    iter_records()
       ↓
    build_report()
       ↓
    {"total_records": N}
       ↓
      / \
     /   \
   JSON  CSV

Buradaki kritik nokta:

> **Processing sonucu değişmiyor, sadece serializer değişiyor.**

Final kodda da `iter_records()`, `build_report()`, JSON writer ve CSV writer ayrı sorumluluklarda tutuldu.

---

# 🧠 Input Format ≠ Output Format

İlk kafa karışıklığım eski normalizer projesinden geldi.

Eski:

    JSON input ─┐
                ├─ process → JSONL
    CSV input ──┘

Day51:

    JSONL input
         ↓
      process
         ↓
       report
       /    \
    JSON    CSV

Yani:

    CSV → program

ile:

    program → CSV

aynı şey değil.

**TIRT.**

---

# ⚙️ `--format`

İlk denemede:

    required=True
    default="json"

ikisini birlikte kullandım.

Mantıksal olarak çelişkili:

    required=True
    → kullanıcı vermek zorunda

    default="json"
    → kullanıcı vermezse JSON kullan

Doğru:

    choices=["json", "csv"]
    default="json"

Böylece:

    --format verilmez
          ↓
        JSON

ve yanlış:

    --format xml

doğrudan CLI sınırında reddediliyor.

Broken case'te `xml` için `argparse` hata verdi ve exit code `2` döndü.

---

# 📦 Processing Format Bilmemeli

`iter_records()`un işi:

    JSONL oku
       ↓
    satırı temizle
       ↓
    json.loads()
       ↓
    dict doğrula
       ↓
    yield

`build_report()`un işi:

    records
       ↓
    processing
       ↓
    report dict

Bu iki fonksiyon:

    JSON mı yazacağız?
    CSV mi yazacağız?

bilmemeli.

Yani şöyle bir şey:

    iter_records(path, output_format)

veya:

    build_report(records, format)

gereksiz coupling olur.

---

# 📝 JSON Serializer

Akış:

    report dict
        ↓
    json.dumps()
        ↓
    JSON string
        ↓
    write_text()
        ↓
    report.json

Burada tekrar oturttuğum fark:

    json.dump()
    → file object'e yazar

    json.dumps()
    → string üretir

Ben `Path.write_text()` kullandığım için:

    json.dumps()

doğru seçim.

Bir ara yanlışlıkla:

    json.dumps(iter_records)

yazdım.

Bu fonksiyonun kendisini serialize etmeye çalışmak olurdu.

Doğrusu:

    json.dumps(report)

---

# 📊 CSV Serializer

CSV için:

    csv.DictWriter

kullandım.

Mental model:

    report.keys()
    → kolon isimleri

    writeheader()
    → header satırı

    writerow(report)
    → değer satırı

Örneğin:

    {
        "total_records": 3
    }

şuna dönüşüyor:

    total_records
    3

`newline=""` ile satır sonlarını CSV modülüne bıraktım.

---

# 🧪 Pytest

İki gerçek output testi yazdım:

    CSV output
    JSON output

CSV testinde:

    tmp_path
       ↓
    gerçek sample.jsonl
       ↓
    run(config)
       ↓
    gerçek report.csv
       ↓
    splitlines()
       ↓
    assert

JSON testinde ise string formatting'i test etmek yerine:

    output text
       ↓
    json.loads()
       ↓
    dict
       ↓
    assert

yaptım.

Bu daha sağlam çünkü:

    indent
    whitespace
    newline

değişse bile veri aynı kalabilir.

Final:

    test_csv_report PASSED
    test_json_report PASSED

    2 passed ✅

---

# 🐞 BLOK 1 Hatalarım

- CSV input ile CSV output'u karıştırdım.
- `required=True` ile `default="json"`u aynı anda kullandım.
- `json.dump()` / `json.dumps()` farkını karıştırdım.
- `report` yerine fonksiyonun kendisini serialize etmeye çalıştım.
- Test dosyasını `python test_day51.py` ile çalıştırdım.
- Pytest fonksiyonlarının normal Python tarafından otomatik çağrılacağını düşündüm.

---

# 2️⃣ BLOK 2 — Bağımsız Fault Debugging

Bu blokta iki vaka çözdüm:

    A) systemd
    CLI çalışıyor
    service çalışmıyor

    B) Docker
    container exit 0
    ama host output yok

Ana yöntem:

    semptom
       ↓
    kanıt topla
       ↓
    failure boundary
       ↓
    kök neden
       ↓
    minimum fix
       ↓
    aynı şeyi tekrar doğrula

---

# 🐧 VAKA A — systemd `203/EXEC`

Önce önemli baseline:

    .venv-current/bin/python report.py
         ↓
    report written ✅

Yani Python kodu kendi başına çalışıyor.

Sonra service:

    status=203/EXEC

ile patladı.

Journal:

    Unable to locate executable
    Failed at step EXEC
    No such file or directory

diyordu.

Bu çok net bir failure boundary:

    systemd
       ↓
    ExecStart executable
       ↓
    PATLADI
       ↓
    Python başlamadı
       ↓
    report.py hiç çalışmadı

Burada gidip Python kodunu değiştirmek **TIRT.**

---

# 🐞 İlk Gerçek Sebep — Path Typo

Gerçek klasörü yanlış oluşturmuşum:

    coreops-rehersal

Unit ise:

    coreops-rehearsal

arıyordu.

Filesystem ile kontrol edince:

    service path → yok
    gerçek typo path → var

olduğu kanıtlandı.

Yani gözle:

> "Path doğru gibi."

demek yerine:

    ls -l
    readlink -f

gibi araçlarla filesystem'e sormam gerekiyor.

---

# 💥 Asıl Fault — Eski Venv

Daha sonra service'i bilerek:

    .venv-old/bin/python

kullanacak şekilde bozdum.

Ama CLI:

    .venv-current/bin/python report.py

ile hâlâ çalışıyordu.

Kanıt:

    CLI ✅
    service ❌
    status=203/EXEC
    .venv-old yok

Sonuç:

> **Application fault değil, execution configuration fault.**

Minimum fix:

    ExecStart
    .venv-old
        ↓
    .venv-current

Sonra:

    daemon-reload
       ↓
    service start
       ↓
    report written ✅

Bu vaka service ile CLI'nın aynı programı çalıştırsa bile **aynı execution context'i kullanmak zorunda olmadığını** tekrar gösterdi.

---

# ⚙️ `Type=oneshot`

Service başarılı olduktan sonra:

    inactive (dead)

gördüm.

Bu burada problem değil.

Çünkü:

    Type=oneshot

demek:

    başla
      ↓
    işi yap
      ↓
    başarıyla çık

Asıl bakacağım:

    report written
    status=0
    Finished
    Deactivated successfully

---

# 🐳 VAKA B — Container Başarılı Ama Host Output Yok

Uygulamanın gerçek output contract'ı:

    /lab/runtime/report.json

Ama Compose'ta bilerek:

    ./runtime:/lab/output

mount ettim.

Görsel:

    HOST ./runtime
          ↓
      /lab/output

Ama app:

    /lab/runtime/report.json

yazıyor.

Bu iki path birbirinden farklı.

---

# 🧪 Semptom

Container:

    report written
    exit code 0

dedi.

Ama host:

    ./runtime
    → boş

Buradaki önemli ders:

> **Exit code 0 sadece process'in kendi açısından başarılı tamamlandığını gösterir.**
>
> Beklediğim external state'in oluştuğunu garanti etmez.

---

# 🔎 `docker inspect`

Inspect'te gerçek runtime mount'u gördüm:

    Source:
    host ./runtime

    Destination:
    /lab/output

Yani Compose config'in runtime'da gerçekten uygulandığını kanıtladım.

Sonra geçici container içinde baktım:

    /lab/runtime/report.json ✅

    /lab/output/report.json ❌

    host ./runtime/report.json ❌

Dolayısıyla:

    uygulama yanlış değil
       ↓
    mount başka yere bağlı
       ↓
    dosya writable layer'da kalıyor

Kök neden:

> **Mount destination ile uygulamanın gerçek output path'i eşleşmiyor.**

---

# 🔧 Minimum Docker Fix

İki seçenek vardı:

    A)
    uygulamayı /lab/output'a yazdır

    B)
    mount'u /lab/runtime'a taşı

B'yi seçtim.

Çünkü uygulamanın contract'ı zaten:

    /lab/runtime/report.json

Config yanlışsa uygulamayı config hatasına uydurmak yerine config'i düzeltmek daha temiz.

Yanlış:

    ./runtime:/lab/output

Doğru:

    ./runtime:/lab/runtime

Sonra container recreate edildi ve host output doğru yerde görünür hale geldi.

Bu tam olarak:

> **Kodu değiştirmeden infrastructure config'i gerçek uygulama contract'ına uydurmak**

oldu.

---

# 🐞 BLOK 2 Hatalarım

- `rehearsal` klasör adını typo yaptım.
- systemd'nin eski `.venv-old` interpreter'ına bakmasını bilerek oluşturup `203/EXEC` teşhis ettim.
- Journal'da eski ve yeni denemelerin loglarını karıştırmamak gerektiğini gördüm.
- Docker mount destination'ı app'in gerçek output path'inden farklı yaptım.
- Container exit `0` gördüğüm için ilk anda external state'in de doğru olabileceğini düşündüm.
- Kapanmış container'a `docker exec` kullanamayacağımı tekrar gördüm; inspection için `docker compose run --rm` kullandım.

---

# 🧠 Kafaya Kazı

> [!tip]
> **Processing ≠ Serialization**

> [!tip]
> **Input format ≠ Output format**

> [!tip]
> **Aynı report → JSON veya CSV**

> [!tip]
> **CLI sınırı mümkünse `argparse choices` ile CLI'da çöz.**

> [!tip]
> **`json.dumps()` → string**

> [!tip]
> **`csv.DictWriter` → dict'i kolonlara dönüştürür**

> [!danger]
> **`203/EXEC` → önce ExecStart executable'ına bak.**

> [!danger]
> **CLI çalışıyor + service çalışmıyor → hemen uygulamayı suçlama.**

> [!tip]
> **Unit değiştiyse → `daemon-reload`**

> [!tip]
> **Oneshot sonrası `inactive (dead)` normal olabilir.**

> [!danger]
> **Container exit 0 ≠ host state doğru**

> [!tip]
> **Bind mount = `HOST_PATH:CONTAINER_PATH`**

> [!danger]
> **App'in yazdığı path mount destination altında değilse dosya hostta görünmez.**

---

# 📌 30 Saniyelik Özet

    BLOK 1

    JSONL
      ↓
    iter_records
      ↓
    build_report
      ↓
    Python dict
      ↓
     / \
    /   \
 JSON   CSV

    processing aynı
    serializer farklı


    BLOK 2 / SYSTEMD

    CLI ✅
    service ❌
       ↓
    status + journal
       ↓
    203/EXEC
       ↓
    ExecStart path
       ↓
    eski/yanlış venv
       ↓
    minimum fix
       ↓
    service ✅


    BLOK 2 / DOCKER

    container exit 0 ✅
    host file ❌
       ↓
    inspect Mounts
       ↓
    app → /lab/runtime
    mount → /lab/output
       ↓
    mismatch
       ↓
    mount'u /lab/runtime yap
       ↓
    host file ✅

---

# ✅ Günün Kazanımları

- [x] JSON ve CSV output'u aynı processing'den ürettim
- [x] Serializer katmanını processing'den ayırdım
- [x] `--format` için `choices` + default kullandım
- [x] JSON ve CSV output'u manuel doğruladım
- [x] CSV için `DictWriter` kullandım
- [x] JSON testini veri seviyesinde yaptım
- [x] CSV ve JSON için pytest sonucu `2 passed`
- [x] Unsupported format için exit code `2` gördüm
- [x] systemd `203/EXEC` failure boundary'sini teşhis ettim
- [x] Path typo'yu filesystem kanıtıyla buldum
- [x] Eski interpreter path'i ile application/config farkını ayırdım
- [x] `Type=oneshot` yaşam döngüsünü tekrar ettim
- [x] Docker mount'u `inspect` ile doğruladım
- [x] Container filesystem ile host filesystem farkını kanıtladım
- [x] Mount destination mismatch'i buldum
- [x] Minimum Compose fix uyguladım
- [x] Kod değiştirmeden infrastructure fault'u çözdüm

---

# 🚀 Final Mental Model

> **Day51'in en önemli cümlesi:**
>
>     TAHMİN ETME
>          ↓
>     KATMANI BELİRLE
>          ↓
>     KANIT TOPLA
>          ↓
>     KÖK NEDENİ BUL
>          ↓
>     EN KÜÇÜK DÜZELTME
>          ↓
>     AYNI DAVRANIŞI TEKRAR TEST ET
>
> Kodda da debugging'de de aynı prensip:
>
> **Her katman kendi işini yapsın; yanlış katmanı düzeltmeye çalışma.**
