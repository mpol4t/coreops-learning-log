# CoreOps Learning Log

> Python, Linux and Docker — learning through small lessons, practical code and repeatable tests.

[![Validate learning log](https://github.com/mpol4t/coreops-learning-log/actions/workflows/validate.yml/badge.svg)](https://github.com/mpol4t/coreops-learning-log/actions/workflows/validate.yml)

Bu repository uygulamalı gelişim günlüğümdür. Eski 72 modüllük rota tarihsel referanstır; güncel odak Python/Linux/Docker, Git ve CI ise destekleyici iş akışıdır.

## Güncel durum — 13 Eylül 2026

| Alan | Durum |
| --- | --- |
| Mentor ve kanonik son onay | V4-04 GEÇTİ; V4-01..04 tamamlandı, zorunlu telafi yok |
| Sıradaki oturum | V4.1-05: küçük systemd timer / oneshot uygulaması; henüz tamamlanmadı |
| Hedef bitiş/değerlendirme | 21 Eylül 2026 |
| Final ürün | Genel Veri İşleyici CLI |
| Yürürlükteki plan | [CoreOps V4.1 — staj hazırlığı](docs/ROADMAP_V4_1.md) |

Mentorun onayı ile kodun repoya yüklenmesi farklı kayıtlardır. V4-01..04 çalışmaları day-41..44 dizinlerinde bulunur. Geçmiş başarılar korunur; eski V4-05 retry görevi ertelenmiştir, tamamlandı veya başarısız sayılmaz.

## Üç ana alan

- Python: CLI/fonksiyon tasarımı, dosya/veri işleme, mevcut HTTP/SQL bilgisi, gerçek testler ve streaming; küçük işi bağımsız teslim etme.
- Linux: gerçek Ubuntu üzerinde service, log, process, izin, dosya tanıtıcıları ve kaynak teşhisi.
- Docker: image/layer/cache, process, volume, network, Compose readiness, restore, limits ve multi-stage.
- Git/CI: kısa diff/commit/PR akışı ve gerçek test/build otomasyonu.

Güvenlik alan projesi, CVSS/EPSS/KEV, threat model ve SBOM kapsam dışıdır. Ayrıntılı HTTP retry/429, thread/profiling, multiprocessing/asyncio ve Kubernetes sonraya bırakılmıştır. Hedef Python/Linux/Docker'da pratik staj hazırlığıdır; işe kabul veya tam ustalık garantisi değildir.

## Öğrenme yöntemi

Kısa açıklama → 1–2 dar resmi kaynak → açıklamalı çalışan örnek → rehberli küçük değişiklik → bağımsız mini lab → mevcut projeye ekleme.

İlk kez görülen kütüphane doğrudan büyük labda kullanılmaz. İlerleme süre doldurmaya değil küçük bağımsız uygulamaya dayanır. Ders ve araştırma günlük süreye dahildir.

## Teslim ve repository yapısı

Kod/commit + kısa ilgili test çıktısı + en fazla 2–3 cümle yeterlidir. [Kısa günlük şablonu](templates/day/README.md) isteğe bağlıdır. Her gün ayrı rapor veya bütün klasörleri oluşturmak gerekmez.

Mevcut day-NN dizinleri tarihsel çalışmaları korur. Yeni çalışmalar ilgili küçük src/tests/fixtures yapısını yalnız ihtiyaç halinde kullanır. Büyük loglar, build çıktıları, sanal ortamlar, parolalar ve .env dosyaları commit edilmez.

[Git çalışma akışı](docs/GIT_WORKFLOW.md) destekleyici referanstır, ayrıca günlük form ödevi değildir.

## Kanıtlı temel ve sıradaki öğrenmeler

Geçmiş çalışmalar Python akışı/exception/CLI/parsing, Linux path/izin/process, Git staging/merge, Docker cache/PID 1/volume ve Compose service DNS, SQL/Python PostgreSQL entegrasyonu içerir. Mentor Gün 40 structured logging ve correlation çalışmasını da onaylamıştır.

V4-01'de DB temiz kurulum ve bağlantı hatası ayrımı; V4-02'de pytest fixture/parametrize/monkeypatch; V4-03'te gerçek Ubuntu systemd/journal/izin teşhisi; V4-04'te JSONL generator ve iki sayfalı pagination mentor tarafından onaylandı. Day44 test dosyaları henüz boş; testlerin bu uygulamaya aktarımı ve CI'da çalışması sonraki pratik hedeflerdir. Restore/multi-stage/limits planlanmış olması tamamlandıkları anlamına gelmez.

## Final ürün

Mevcut JSONL kodundan küçük veri raporu CLI'si: girdi → doğrulama/filtreleme → dosya çıktısı; gerçek test/CI ve temiz kurulum. Mevcut Python/PostgreSQL/Compose labı ayrıca veri kalıcılığı, network ve restore kanıtı sağlar. Her mekanizmayı tek dev projeye toplama, yeni HTTP adapter/API sunucusu, UI veya güvenlik risk motoru zorunlu değildir.

Deneyler yalnız kendi/izinli lab ortamında yapılır. Bu repo bütün eski 72 modülde uzmanlık iddiası değildir; neyin bağımsız yapılabildiğini ve nelerin sonraya kaldığını gösterir.

Eski kapsam için [arşiv V3.7 rotası](docs/ROADMAP_V3.md) saklanmıştır; aktif görev kaynağı değildir.
