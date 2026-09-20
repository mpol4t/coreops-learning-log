---
title: "Gün 50 — Gerçek CLI, Clean Environment ve CI Pipeline"
tags:
  - coreops
  - day50
  - python
  - cli
  - dataclass
  - jsonl
  - generator
  - reproducibility
  - pytest
  - github-actions
  - ci
  - docker
aliases:
  - "Gün 50 CLI Clean Environment CI Pipeline"
status: completed
---

# 🚀 Day 50 — Gerçek CLI → Clean Environment → CI Pipeline

> [!note] 20 Eylül arşiv denetimi
> Reader generator olsa da `build_report()` içindeki `list(records)` tüketilen bütün kayıtları belleğe alır. Bu uygulama uçtan uca sabit bellekli streaming değildir. Aşağıdaki CI GREEN kaydı o günün koşusudur; sonraki commit'ler için son workflow sonucu ayrıca kontrol edilmelidir.

> [!abstract] 🎯 Ana fikir
> Bugün tek bir script yazmaktan çıkıp küçük bir **gerçek proje akışı** kurdum:
>
>     CLI
>      ↓
>     Config
>      ↓
>     JSONL Reader
>      ↓
>     Processing
>      ↓
>     Gerçek Output
>      ↓
>     Clean Environment
>      ↓
>     Pytest
>      ↓
>     GitHub Actions
>      ↓
>     Docker Build
>
> En önemli nokta:
>
> **"Bende çalışıyor" yetmez. Input'tan gerçek output üretmeli, temiz ortamda çalışmalı ve CI bunu otomatik kanıtlamalı.**

---

# 1️⃣ BLOK 1 — CLI + ReportConfig + JSONL Pipeline

Final uygulama akışım:

    --input / --output
            ↓
        argparse
            ↓
       ReportConfig
            ↓
        run(config)
            ↓
    iter_records(input)
            ↓
      JSONL parsing
            ↓
      build_report()
            ↓
     total_records
            ↓
      json.dumps()
            ↓
     output.write_text()

Burada hiçbir şeyi fake/hard-code etmedim.

Output gerçekten input'tan geliyor.

---

# ⚙️ `ReportConfig`

CLI ayarlarını sağa sola ayrı değişken olarak taşımak yerine:

    @dataclass(frozen=True)
    class ReportConfig:
        input_path: Path
        output_path: Path

ile tek nesnede topladım.

Mental model:

    argparse
       ↓
    string path'ler
       ↓
    Path(...)
       ↓
    ReportConfig
       ↓
    uygulamanın geri kalanı

`frozen=True`:

    config oluştur
        ↓
    değerleri kilitle
        ↓
    sonradan yanlışlıkla değiştirme

---

# 🧠 Type Annotation

Şunu:

    def run(config: ReportConfig):

ilk başta dönüşüm gibi düşündüm.

Değil.

    config
    → parametre adı

    ReportConfig
    → beklenen tip

Aynı şekilde:

    def parse_config() -> ReportConfig:

şu demek:

> Bu fonksiyonun `ReportConfig` döndürmesi bekleniyor.

---

# 📄 Reader'ı Gerçek Akışa Bağladım

Daha önce yazdığım:

    iter_records(path)

generator'ını korudum.

Akış:

    file
     ↓
    satır
     ↓
    strip
     ↓
    boş mu?
     ├─ evet → ValueError
     ↓
    json.loads()
     ↓
    dict mi?
     ├─ hayır → ValueError
     ↓
    yield

Önemli:

    records = iter_records(...)

dosyayı hemen tamamen okumuyor.

Sadece generator oluşturuyor.

Gerçek tüketim:

    record_list = list(records)

satırında başlıyor.

---

# 🔄 `yield` vs `return`

Yanlış fikir:

    return json_params

Bu:

    ilk kayıt
      ↓
    return
      ↓
    FONKSİYON BİTER

demek.

Doğru:

    yield json_params

Böylece:

    kayıt 1 → yield
    kayıt 2 → yield
    kayıt 3 → yield

devam ediyor.

---

# 💥 JSONDecodeError Boundary

Eski mantıkta exception'ı yakalayıp yutma riski vardı.

Finalde:

    json.loads(cleaned)

hatasını doğal bırakıyorum.

Akış:

    malformed JSON
         ↓
    JSONDecodeError
         ↓
    iter_records dışına
         ↓
    build_report dışına
         ↓
    run dışına
         ↓
    main / caller

Reader'ın işi:

> **Hatanın ne olduğunu bildirmek.**

Programın ne yapacağına üst katman karar verir.

---

# 📊 `build_report()`

Ham text saymak yerine artık **parse edilmiş record** sayıyorum.

    generator
       ↓
    list(records)
       ↓
    [{"id":1}, {"id":2}, ...]
       ↓
    len(...)
       ↓
    total_records

Bu yüzden:

    line_count ❌

yerine:

    total_records ✅

daha doğru semantik.

---

# 🐞 BLOK 1 Hatalarım

- `config = parse_config` yazdım → fonksiyonun kendisini atadım. Doğrusu `parse_config()`.
- `iter_records()` yazmış olmama rağmen `read_text()` ile bypass etmeye çalıştım.
- `yield` yerine `return` düşünerek generator mantığını bozuyordum.
- `JSONDecodeError`'ı yakalayıp yutuyordum.
- Dict yerine yanlışlıkla `{ "total_records", value }` şeklinde **set** oluşturdum.
- CLI'ı positional çalıştırdım ama parser `--input` ve `--output` bekliyordu.
- Eski `line_count` ismini yeni record modeline taşıdım.

---

# ✅ Gerçek CLI Testleri

İlk input:

    4 record
       ↓
    report.json
       ↓
    total_records = 4 ✅

İkinci input:

    5 record
       ↓
    farklı output path
       ↓
    total_records = 5 ✅

Kod değişmedi.

Sadece runtime config değişti.

Malformed JSON:

    list(records)
        ↓
    generator tüketildi
        ↓
    JSONDecodeError ✅

Yani gerçek pipeline baştan sona çalıştı.

---

# 2️⃣ BLOK 2 — Clean Environment / Reproducibility

> [!important]
> **Eski venv'de çalışıyor olması dependency'lerin doğru tanımlandığını kanıtlamaz.**

Eski environment:

    önceden yüklenmiş paket
            ↓
    gizli dependency
            ↓
    "bende çalışıyor"

Clean test:

    sıfır venv
       ↓
    eski paket yok
       ↓
    projeyi çalıştır
       ↓
    gerçekten reproducible mı?

---

# 🧪 Temiz Venv Kanıtı

Oluşturdum:

    python3 -m venv .venv-clean

Aktive ettim:

    source .venv-clean/bin/activate

Ama prompt'taki:

    (.venv-clean)

tek başına kanıt değil.

Asıl kontrol:

    which python3

çıktısının:

    .../Day50/.venv-clean/bin/python3

olmasıydı.

Sonra:

    python -m pip list

çıktısında sadece:

    pip

vardı.

Yani eski environment'tan paket taşınmamıştı.

---

# 📦 Dependency Kontrolü

Kod importları:

    argparse
    json
    dataclasses
    pathlib
    sys

Bunların hepsi:

    Python Standard Library

Bu yüzden:

    pip install json
    pip install argparse
    pip install pathlib

gibi işler **TIRT.**

Day50 uygulamasının third-party **runtime dependency'si yoktu**.

Ama önemli ayrım:

    runtime dependency
    ≠
    test/development dependency

Örneğin:

    pytest

test dependency olabilir.

---

# ✅ Clean Environment Testi

Temiz venv içinde:

    day50.py
       ↓
    sample2.jsonl
       ↓
    report2
       ↓
    total_records = 5

çalıştı.

Sonra:

    echo $?

çıktısı:

    0

oldu.

Kanıt:

    clean interpreter ✅
    eski paket yok ✅
    uygulama çalıştı ✅
    doğru output ✅
    exit 0 ✅

Bu blokta gerçek test suite olmadığı için:

    pytest suite geçti ❌

iddiasında bulunmadım.

Bu önemli:

> **Eksik dependency'yi kafama göre kurup sahte yeşil sonuç üretmek reproducibility testi değildir.**

---

# 🐞 BLOK 2 Hatalarım

- Venv aramasını repo yerine bütün workspace seviyesinde yaptım.
- `-name .venv` aramasının `.venv-clean` bulacağını düşündüm.
- Sadece shell prompt'una güvenmeye yaklaştım; interpreter path'ini ayrıca doğruladım.
- Runtime dependency ile test dependency kavramlarını ayırmam gerekti.
- Tek JSON object üreten output'a `.jsonl` uzantısı verdim; `.json` daha doğru olurdu.
- `cat` sonrası gördüğüm `}%` içindeki `%` karakterini dosyanın parçası sandım; aslında final newline olmadığı için zsh prompt gösterimiydi.

---

# 3️⃣ BLOK 3 — GitHub Actions: Pytest + Docker Build

Başlangıç CI:

    Repository hygiene ✅
    Python syntax ✅

Final hedef:

    Repository hygiene ──┐
    Python syntax ───────┼── PASS
    Pytest behavior ─────┘
                         ↓
                  Docker Build
                         ↓
                     CI GREEN

Buradaki en önemli ders:

> **CI green = sadece CI'a koyduğum kontroller geçti.**
>
> **CI green ≠ program kesin kusursuz.**

---

# 🆚 `py_compile` vs `pytest`

    py_compile
    → syntax / compile

    pytest
    → behavior

Örneğin:

    def add(a, b):
        return a - b

syntax olarak geçerli.

Yani:

    py_compile ✅

Ama:

    assert add(2, 3) == 5

dersem:

    pytest ❌

> **Compile olması doğru çalıştığı anlamına gelmez.**

---

# 🧪 Gerçek Pytest'i CI'a Taşıdım

Bulduğum test:

    day-47/blok3-python/tests/test_records.py

İlk:

    python -m pytest

denemesinde:

    No module named pytest

aldım.

Sonra düz:

    pytest

çalıştı ama:

    ModuleNotFoundError: No module named 'src'

geldi.

Buradan iki ayrı sorun çıktı.

---

# 🐍 `pytest` vs `python -m pytest`

Makinede:

    pytest
    → Homebrew'nun kendi Python environment'ı

    python
    → başka interpreter

kullanıyordu.

Bu yüzden:

    pytest

ile:

    python -m pytest

aynı environment olmak zorunda değil.

Kafaya:

    pytest
    → PATH'teki executable


    python -m pytest
    → seçtiğim Python'ın pytest modülü

CI'da daha kontrollü olan:

    python -m pytest

---

# 📂 Working Directory Hatası

Test:

    from src.records import iter_records

kullanıyordu.

Ama repo root'tan çalıştırınca:

    src

orada değildi.

Doğru proje kökü:

    day-47/blok3-python/

Lokal:

    cd day-47/blok3-python

CI:

    working-directory: day-47/blok3-python

Böylece import çözüldü.

Temiz environment testinde:

    python -m pytest -q tests/test_records.py

sonucu:

    2 passed ✅

oldu.

---

# 🧹 Venv Git'e Düşmesin

Test için oluşturduğum:

    .venv-ci/

`git status`ta:

    ??

olarak çıktı.

Yani untracked.

Yanlışlıkla commit edebilirdim.

Temizledim ve çalışma ağacını tekrar kontrol ettim.

> **Virtual environment repo artifact'i değildir.**

---

# 🧼 Whitespace

Workflow değişikliğinde:

    git diff --check

şunu yakaladı:

    trailing whitespace

Temizledikten sonra komut sessiz kaldı.

Kafaya:

    git diff --check
    → sessiz

demek:

    whitespace problemi yok ✅

---

# 🐳 Docker Build'i CI'a Eklemek

Hedef Dockerfile:

    day-49/Blok2/Dockerfile

Build:

    docker build \
      -f day-49/Blok2/Dockerfile \
      -t coreops-ci-check \
      day-49/Blok2

Buradaki ayrım:

    -f
    → Dockerfile nerede?

    -t
    → image adı/tag

    son path
    → BUILD CONTEXT

> [!danger]
> **Dockerfile path ≠ build context**

Context:

    day-49/Blok2

olmalıydı çünkü Dockerfile:

    COPY requirements.txt .
    COPY src/ ./src/

diyor ve bu dosyalar context'in içinde.

Lokal build:

    13/13 FINISHED ✅

ile geçti.

---

# 🔗 `needs:` ile Pipeline Sırası

Docker build job'una:

    needs:
      - repository-hygiene
      - python-syntax
      - python-tests

ekledim.

Akış:

    hygiene ───┐
    syntax ────┼── PASS
    tests ─────┘
                ↓
          docker-build

Bir tanesi fail:

    docker-build
    → skipped

Böylece pahalı build'i bozuk kod üzerinde boş yere çalıştırmıyorum.

---

# 🏃 Her Job Ayrı Dünya

İlk başta her job'da neden tekrar:

    actions/checkout

olduğunu düşündüm.

Sebep:

    python-tests runner
    ≠
    docker-build runner

Job'lar ayrı runner'larda çalışabilir.

Birbirlerinin filesystem'ini otomatik paylaşmazlar.

Bu yüzden her job kendi:

    checkout
    setup
    dependency
    command

akışına sahip olmalı.

---

# ✅ Final CI Kanıtı

GitHub Actions final sonucu:

    Repository hygiene      ✅
    Python syntax           ✅
    Python behavior tests   ✅
    Docker image build      ✅

Yani artık CI:

    Python parse oluyor ✅
    gerçek assertion'lar geçiyor ✅
    Dockerfile gerçek image üretiyor ✅

diyebiliyor.

Ama Docker build başarılı diye:

    DB bağlantısı ✅
    container runtime ✅
    business logic ✅
    deployment ✅

otomatik kanıtlanmış olmuyor.

Bu labda Docker tarafındaki contract:

    image build succeeds

ile sınırlıydı.

---

# 💥 Broken Case

Bu blokta ekstra:

    GREEN
     ↓
    assertion boz
     ↓
    RED
     ↓
    geri düzelt
     ↓
    GREEN

adımını ayrıca uygulamadım.

Testlerin gerçek GitHub runner üzerinde çalışıp geçtiğini doğruladım; ekstra broken-case bilinçli olarak atlandı.

---

# 🐞 BLOK 3 Hatalarım

- Workflow'u önce yanlış repository'de aradım.
- `validate.yml` yerine `validate.yaml` aradım.
- Seçtiğim Python'da pytest yokken `python -m pytest` çalıştırmaya çalıştım.
- Düz `pytest` komutunun başka Python kullandığını sonradan fark ettim.
- Testi yanlış working directory'den çalıştırıp `src` import hatası aldım.
- `.venv-ci` klasörünü yanlışlıkla Git'e sokma riski oluşturdum.
- Workflow'da trailing whitespace bıraktım.
- CI Python 3.12 iken Docker runtime 3.13'tü; ikisini 3.13'e hizaladım.

---

# 🧠 Kafaya Kazı

> [!tip]
> **CLI = runtime bilgisi al**

> [!tip]
> **Config = ayarları taşı**

> [!tip]
> **Reader = input'u oku/doğrula**

> [!tip]
> **Processor = veriden sonuç üret**

> [!tip]
> **run = parçaları bağla**

> [!tip]
> **main = üst seviye orchestration**

> [!danger]
> **Generator oluşturmak ≠ generator'ı tüketmek**

> [!tip]
> **`json.loads` = JSON string → Python**

> [!tip]
> **`json.dumps` = Python → JSON string**

> [!danger]
> **"Bende çalışıyor" ≠ reproducible**

> [!tip]
> **`which python` = gerçekten hangi interpreter?**

> [!tip]
> **`python -m pytest` = seçtiğim Python ile pytest**

> [!danger]
> **`py_compile` ≠ behavior test**

> [!danger]
> **Dockerfile path ≠ build context**

> [!tip]
> **`needs:` = job dependency**

> [!danger]
> **CI GREEN = sadece tanımladığım kontroller geçti**

---

# 📌 30 Saniyelik Özet

    BLOK 1

    CLI
     ↓
    ReportConfig
     ↓
    iter_records
     ↓
    generator
     ↓
    build_report
     ↓
    JSON output


    BLOK 2

    clean venv
       ↓
    interpreter doğrula
       ↓
    paketleri kontrol et
       ↓
    uygulamayı çalıştır
       ↓
    output + exit 0


    BLOK 3

    git push
       ↓
    GitHub Actions
       ↓
    hygiene ─┐
    syntax ──┼─ PASS
    pytest ──┘
       ↓
    Docker build
       ↓
    GREEN

---

# ✅ Günün Final Durumu

- [x] Gerçek CLI input/output akışı kuruldu
- [x] `ReportConfig` ile config katmanı oluşturuldu
- [x] JSONL reader gerçek uygulama akışına bağlandı
- [x] Generator lazy davranışı korundu
- [x] `JSONDecodeError` propagation doğrulandı
- [x] Farklı input/output ile kod değiştirmeden çalıştı
- [x] Clean venv sıfırdan oluşturuldu
- [x] Doğru interpreter doğrulandı
- [x] Gizli runtime dependency olmadığı kanıtlandı
- [x] Clean environment'da output üretildi
- [x] Exit code `0` doğrulandı
- [x] Gerçek pytest testi bulundu
- [x] `pytest` / `python -m pytest` environment farkı çözüldü
- [x] Import path için doğru working directory kullanıldı
- [x] Lokal gerçek test sonucu `2 passed`
- [x] Pytest GitHub Actions'a eklendi
- [x] Docker build context doğru kuruldu
- [x] Lokal Docker build `13/13 FINISHED`
- [x] Docker build job'u testlerden sonra çalışacak şekilde bağlandı
- [x] Final CI dört job ile GREEN oldu

> **Day50 final zihinsel modelim:**
>
>     Kod yaz
>       ↓
>     gerçek input/output ile kanıtla
>       ↓
>     temiz ortamda tekrar kanıtla
>       ↓
>     behavior test ile kanıtla
>       ↓
>     Docker build ile paketlenebilirliği kanıtla
>       ↓
>     CI hepsini otomatik tekrar etsin
>
> **Tek bir yeşil çıktı değil, birbirini tamamlayan kanıt zinciri.**
