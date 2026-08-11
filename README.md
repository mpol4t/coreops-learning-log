# CoreOps Learning Log

> Python engineering, Linux diagnostics, Git/CI, Docker/Compose and cybersecurity product engineering — learned through reproducible experiments.

[![Validate learning log](https://github.com/mpol4t/coreops-learning-log/actions/workflows/validate.yml/badge.svg)](https://github.com/mpol4t/coreops-learning-log/actions/workflows/validate.yml)

Bu repository, 72 mantıksal modülden oluşan uygulamalı gelişim programımın teknik günlüğüdür. Amacım konu listesi tüketmek değil; çalışan kod, bozuk karşı örnek, terminal kanıtı, test ve açıklanabilir mühendislik kararları üretmektir.

## Güncel durum

| Alan | Durum |
| --- | --- |
| Tamamlanan modül | **17 / 72** |
| Aktif paket | **Gün 18+19 — veri sözleşmeleri ve ilk Git temeli** |
| Son gate | **G1 tamamlandı** |
| Final proje | **Asset Intelligence Collector** |

Gün numarası takvim tarihi değildir. Bir modül birden fazla güne yayılabilir; uyumlu iki modül aynı çalışma oturumunda tamamlanabilir. Her modül kendi kanıtı ve değerlendirmesiyle kapanır.

## Programın altı hattı

- **Python engineering:** CLI/package tasarımı, API istemcileri, veri doğrulama, SQL, test ve concurrency.
- **Linux diagnostics:** filesystem, process, signal, network/TLS, service, log ve sistem çağrısı teşhisi.
- **Git, GitHub and CI:** staging modeli, anlamlı history, branch/merge, pull request, review ve otomasyon.
- **Docker and Compose:** layer/cache, process modeli, persistence, network, health, hardening ve supply chain.
- **Cybersecurity domain:** asset inventory, exposure, vulnerability correlation, prioritization ve threat modeling.
- **Technical communication:** kapalı-kitap anlatım, canlı kodlama, incident teşhisi ve sistem tasarımı.

Tam Gün 18–72 planı için [V3 yol haritasına](docs/ROADMAP_V3.md) bakılabilir.

## Öğrenme yöntemi

```text
Semptom
   ↓
Katman ve hipotez
   ↓
Çalıştırmadan önce tahmin
   ↓
En küçük ayırıcı deney
   ↓
Kanıt ve kök neden
   ↓
En küçük düzeltme
   ↓
Test ve karşıt vaka
   ↓
Kısa teknik savunma
```

Bir komutun çalışması tek başına ustalık kanıtı değildir. Yeni girdide bağımsız uygulama, farklı failure mode'a transfer ve kararın trade-off'larını açıklama aranır.

## Repository yapısı

Gün 1–17 tarihsel hâliyle korunur. Gün 18'den itibaren aşağıdaki tutarlı yapı kullanılır:

```text
day-NN/
├── README.md          # hedef, tahmin, deney, kritik kanıt ve öğrenme notu
├── src/               # modüle ait uygulama kodu
├── tests/             # otomatik kontroller
└── fixtures/          # küçük ve güvenli örnek girdiler
```

Her gün dört zorunlu dosya üretmek yerine yalnız probleme gerçekten hizmet eden dosyalar eklenir. Büyük loglar, build çıktıları, sanal ortamlar, tokenlar ve `.env` dosyaları commit edilmez.

Yeni modül başlangıcında [günlük çalışma şablonu](templates/day/README.md) kullanılabilir. Branch, commit ve PR kuralları [Git çalışma akışında](docs/GIT_WORKFLOW.md) açıklanmıştır.

## Tamamlanan temel

- Python return/exception/main/exit sınırları
- Edge case ve assertion deneyleri
- Liste, sözlük ve set seçimi
- CWD, relative/absolute path ve import path ayrımı
- stdout, stderr ve process exit gözlemi
- Linux permission, UID/GID ve ownership modeli
- `pathlib`, recursive arama ve `find` karşılaştırması
- Docker image/container, build context, `COPY`, `CMD`, bind mount ve workdir
- Modüler Python ve `argparse` CLI
- Exception propagation ve application/runtime hata katmanları

Günlük çalışmalar [`day-01`](day-01/) ile [`day-17`](day-17/) arasındaki dizinlerde görülebilir.

## Final proje — Asset Intelligence Collector

Final ürün, farklı kaynaklardan gelen varlık ve zafiyet kayıtlarını toplayan küçük fakat üretime yakın bir sistem olacaktır:

```text
JSON / CSV / HTTP API adapters
              ↓
validation + source lineage
              ↓
normalization + deterministic deduplication
              ↓
asset ↔ vulnerability correlation
              ↓
CVSS + EPSS + KEV + business criticality
              ↓
SQL persistence + CLI/API reports
              ↓
tests + CI + secure Docker/Compose
```

Kabul kriterleri arasında bozuk API/pagination/timeout testleri, structured logging, secret güvenliği, multi-stage image, non-root çalışma, health/readiness, SBOM, threat model ve incident runbook bulunur.

## Güvenlik sınırı

Network ve güvenlik deneyleri yalnızca sahip olduğum veya açıkça izin verilmiş yerel laboratuvar ortamlarında yapılır. Gerçek token, parola, özel anahtar, müşteri verisi veya yetkisiz hedef bilgisi bu repoya eklenmez.

## Bu repository nasıl incelenebilir?

1. README'den aktif kapsamı kontrol edin.
2. İlgili `day-NN/` dizinindeki tahmin ve karşıt vakayı okuyun.
3. Kod/test ile teknik notun aynı sonucu destekleyip desteklemediğine bakın.
4. Commit geçmişinden yaklaşımın nasıl geliştiğini inceleyin.
5. Gate ve final çalışmalarında farklı becerilerin tek vaka üzerinde nasıl birleştiğini takip edin.

Bu repository “72 modülde uzman oldum” iddiası değil; neyi gerçekten uyguladığımı, nerede yanıldığımı ve zihinsel modelimi kanıtla nasıl düzelttiğimi gösteren açık bir gelişim kaydıdır.
