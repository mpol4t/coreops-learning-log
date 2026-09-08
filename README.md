# CoreOps Learning Log

> Python, Linux and Docker — learning through small lessons, practical code and repeatable tests.

[![Validate learning log](https://github.com/mpol4t/coreops-learning-log/actions/workflows/validate.yml/badge.svg)](https://github.com/mpol4t/coreops-learning-log/actions/workflows/validate.yml)

Bu repository uygulamalı gelişim günlüğümdür. Eski 72 modüllük rota tarihsel referanstır; güncel odak Python/Linux/Docker, Git ve CI ise destekleyici iş akışıdır.

## Güncel durum — 8 Eylül 2026

| Alan | Durum |
| --- | --- |
| Mentor ve kanonik son onay | Gün 40 GEÇTİ — 97/100; zorunlu telafi yok |
| Sıradaki oturum | V4-01: önceki becerilerden kısa bağımsız kontrol; henüz tamamlanmadı |
| Hedef bitiş/değerlendirme | 21 Eylül 2026 |
| Final ürün | Genel Veri İşleyici CLI |
| Yürürlükteki plan | [CoreOps V4](docs/ROADMAP_V4.md) |

Mentorun onayı ile kodun repoya yüklenmesi farklı kayıtlardır. Bu doküman güncellemesi Day 40 kodunun yüklenmiş olduğunu iddia etmez. Geçmiş başarılar korunur; ertelenen konular tamamlanmış sayılmaz.

## Üç ana alan

- Python: CLI/fonksiyon tasarımı, JSON/HTTP/SQL, test, streaming, küçük thread I/O uygulaması.
- Linux: gerçek Ubuntu üzerinde service, log, process, izin, dosya tanıtıcıları ve kaynak teşhisi.
- Docker: image/layer/cache, process, volume, network, Compose readiness, restore, limits ve multi-stage.
- Git/CI: kısa diff/commit/PR akışı ve gerçek test/build otomasyonu.

Güvenlik alan projesi, CVSS/EPSS/KEV, threat model ve SBOM bu dönemin zorunlu kapsamı değildir. Ayrıntılı multiprocessing/asyncio ve Kubernetes sonrasına bırakılmıştır.

## Öğrenme yöntemi

Kısa açıklama → 1–2 dar resmi kaynak → açıklamalı çalışan örnek → rehberli küçük değişiklik → bağımsız mini lab → mevcut projeye ekleme.

İlk kez görülen kütüphane doğrudan büyük labda kullanılmaz. İlerleme süre doldurmaya değil küçük bağımsız uygulamaya dayanır. Ders ve araştırma günlük süreye dahildir.

## Teslim ve repository yapısı

Kod/commit + kısa ilgili test çıktısı + en fazla 2–3 cümle yeterlidir. [Kısa günlük şablonu](templates/day/README.md) isteğe bağlıdır. Her gün ayrı rapor veya bütün klasörleri oluşturmak gerekmez.

Mevcut day-NN dizinleri tarihsel çalışmaları korur. Yeni çalışmalar ilgili küçük src/tests/fixtures yapısını yalnız ihtiyaç halinde kullanır. Büyük loglar, build çıktıları, sanal ortamlar, parolalar ve .env dosyaları commit edilmez.

[Git çalışma akışı](docs/GIT_WORKFLOW.md) destekleyici referanstır, ayrıca günlük form ödevi değildir.

## Kanıtlı temel ve sıradaki öğrenmeler

Geçmiş çalışmalar Python akışı/exception/CLI/parsing, Linux path/izin/process, Git staging/merge, Docker cache/PID 1/volume ve Compose service DNS, SQL/Python PostgreSQL entegrasyonu içerir. Mentor Gün 40 structured logging ve correlation çalışmasını da onaylamıştır.

Pagination/retry, pytest kapsamı, restore, multi-stage ve diğer V4 başlıkları için tamamlanma iddiası ilgili gerçek teslimle güncellenir; bu listeye planlandı diye eklenmez.

## Final ürün

Mevcut koddan büyüyen küçük veri işleyici: JSONL veya kontrollü HTTP kaynağı → doğrulama → mevcut PostgreSQL katmanı → CLI raporu. Gerçek test/CI, tekrar kurulabilir Docker/Compose ve kısa README ile tamamlanır. Yeni API sunucusu, UI veya güvenlik risk motoru zorunlu değildir.

Deneyler yalnız kendi/izinli lab ortamında yapılır. Bu repo bütün eski 72 modülde uzmanlık iddiası değildir; neyin bağımsız yapılabildiğini ve nelerin sonraya kaldığını gösterir.

Eski kapsam için [arşiv V3.7 rotası](docs/ROADMAP_V3.md) saklanmıştır; aktif görev kaynağı değildir.
