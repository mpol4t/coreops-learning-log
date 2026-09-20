# CoreOps Learning Log

> Python, Linux and Docker — practical internship preparation through code, tests and troubleshooting.

[![Validate learning log](https://github.com/mpol4t/coreops-learning-log/actions/workflows/validate.yml/badge.svg)](https://github.com/mpol4t/coreops-learning-log/actions/workflows/validate.yml)

## Program tamamlandı

**COREOPS_V4_1_STAJ finali 19 Eylül 2026'da mentor tarafından GEÇTİ olarak değerlendirildi; zorunlu açık yok.** Hedef 21 Eylül'dü. Bu arşiv 20 Eylül'de yeniden denetlendi.

Bu depo bir öğrenme günlüğüdür; üretime hazır ürün, bütün eski 72 modülün tamamlandığı veya üç alanda uzmanlık iddiası değildir. Siber güvenlik alan dersleri, ileri retry/thread/async ve Kubernetes son zorunlu kapsamda değildir.

- [Tamamlanma ve doğrulama raporu](docs/COMPLETION_REPORT.md)
- [Gün / oturum dizini](docs/DAY_INDEX.md)
- [Tamamlanan V4.1 planı](docs/ROADMAP_V4_1.md)
- [Çalıştırma ve test rehberi](docs/RUNBOOK.md)

## İncelenecek çalışmalar

| Alan | Çalışma | Kanıt |
| --- | --- | --- |
| Python | [Final JSONL rapor CLI](day-52/Final/final.py) | JSON/CSV, opsiyonel output yolu, kayıt limiti; [gerçek dosya testleri](day-52/Final/test_final.py) |
| Linux | [systemd final teşhisi](day-52/day-52-coreops-final-python-systemd-docker.md) | WorkingDirectory / relative path arızası, journal/status, minimum düzeltme |
| Docker image | [Multi-stage ve non-root](day-49/Blok2/) | Build-time dependency, UID 10001, kaynak kodu ve yazılabilir runtime yolu ayrımı |
| Docker data | [PostgreSQL backup/restore](day-46/) | Ayrı test DB'sine restore ve sorgu; [final mount vakası](day-52/Final/docker-kismi/) |
| Kaynak gözlemi | [Gün 48](day-48/day-48-process-resources-disk-docker-limits.md) | Linux CPU/RAM/disk; Docker CPU quota, stats ve inspect |
| Git / CI | [Workflow](.github/workflows/validate.yml) | Altı test grubu, Python syntax, repository hijyeni, iki Docker image build ve kısa runtime kontrolleri |

Python CLI, PostgreSQL/Compose ve Docker finali ayrı küçük lablardır; tek entegre ürün gibi sunulmaz. Linux unit dosyalarının bazıları yalnız notlarda arşivlidir. Gün 48 bilinçli olarak yalnız not teslimidir.

## Hızlı başlangıç

Repo kökünden, Python 3.13+ ile:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-test.txt
(cd day-52/Final && ../../.venv/bin/python -m pytest -q test_final.py)
```

Finalin özgün öğrenci teslimi **6 test** içeriyordu. 20 Eylül denetiminde Codex kaynak dosyanın üzerine yazmayı önleyen koruma ve **3 regresyon testi** ekledi; final dosyası artık **9 test** içerir. Bu bakım katkısı öğrencinin bağımsız sınav başarısı diye sayılmaz.

Gerçek CLI örnekleri, diğer testler, Docker önkoşulları ve bilinen sınırlar [çalıştırma rehberinde](docs/RUNBOOK.md).

## Arşiv ve kapsam

day-NN klasörleri eğitim oturumudur, takvim günü değildir. Örneğin Gün 48'in Linux kısmı 16 Eylül, Docker CPU devamı 17 Eylül'de tamamlandı; aynı günün tek notunda tutulur.

Eski [V3](docs/ROADMAP_V3.md) ve [V4](docs/ROADMAP_V4.md) belgeleri tarihsel referanstır. Day44'teki başlangıç test dosyaları boştur; sonraki gerçek testler Day47 ve final oturumlarında bulunur. Lab örneklerindeki yerel DB parolaları üretim kullanımına uygun değildir.

Kodlar ve geçmiş öğrenme hataları korunur. Sanal ortamlar, gerçek parolalar, büyük loglar ve build çıktıları commit edilmez. Deneyler yalnız kendi/izinli lab ortamında yapılır. İşe kabul garantisi verilmez.
