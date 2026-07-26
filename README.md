# CoreOps Learning Log

> 72-step hands-on Python, Linux and Docker practice.
> Hedef: Konu tüketmek değil; çalışan, test edilen, açıklanabilen ve yeniden üretilebilen teknik kanıt üretmek.

## Proje Hakkında

Bu repository, Python, Linux ve Docker alanlarında uyguladığım **72 çalışma modülünden oluşan gelişim programının** teknik günlüğüdür.

Buradaki `Day` numaraları takvim tarihini değil, programdaki çalışma modüllerini temsil eder. Aynı gün içerisinde birden fazla modül tamamlanabilir veya bir modül birden fazla güne yayılabilir.

Repository yalnızca tamamlanmış çözümleri değil; yazdığım uygulamaları, ilk ve hatalı yaklaşımlarımı, debugging sürecini, kök neden analizlerini, testleri ve terminal kanıtlarını da içerir.

> **Çalışması tek başına yeterli değildir.**
> Neden çalıştığını açıklayamıyorsam, hata yolunu test edemiyorsam veya farklı bir senaryoya aktaramıyorsam görev tamamlanmış sayılmaz.
> Açıklanamayan hazır çözüm: **TIRT.**

## Hedeflenen Yetkinlikler

### Python

- Test edilebilir fonksiyon ve modüller tasarlamak
- CLI uygulamaları geliştirmek
- Dosya, JSON ve CSV verisi işlemek
- Configuration, logging, exception ve exit code sözleşmeleri kurmak
- `subprocess`, type hint ve dataclass kullanmak
- Unit, integration ve mock testleri yazmak
- Concurrency ve profiling araçlarını doğru yerde kullanmak

### Linux

- Path, izin, ownership ve kullanıcı modelini anlamak
- `stdout`, `stderr` ve exit code davranışlarını yorumlamak
- Process, PID, signal ve environment yönetmek
- `/proc`, file descriptor ve socket bilgilerini incelemek
- Port, DNS ve HTTP sorunlarını katmanlarına ayırmak
- `systemd`, `journalctl` ve `strace` ile teşhis yapmak

### Docker

- Image, container ve process ayrımını uygulamak
- Dockerfile ve Compose yapıları oluşturmak
- Bind mount ve named volume kullanmak
- Container exit code, log ve network problemlerini teşhis etmek
- Healthcheck ve environment configuration kullanmak
- Non-root ve tekrar üretilebilir image hazırlamak

## Çalışma Yaklaşımı

```text
Problem
   ↓
İlk yaklaşım
   ↓
Hata veya eksik davranış
   ↓
Hipotez ve kanıt
   ↓
Kök neden
   ↓
En küçük düzeltme
   ↓
Test ve regresyon kontrolü
```

## Repository Yapısı

```text
coreops-learning-log/
├── README.md
├── day-01/
│   ├── day-01-return-and-exit-codes.md
│   └── day01.py
├── day-02/
│   ├── day-02-assertions-and-command-chains.md
│   └── day02.py
├── day-03/
│   ├── day-03-data-structures-and-bind-mounts.md
│   ├── day03.py
│   └── services.txt
├── day-04/
│   ├── day-04-path-cwd-bind-mount.md
│   └── data.txt
└── ...
```

Her klasör, ilgili modülün kapsamına göre Python dosyalarını, teknik notları, testleri, örnek verileri ve terminal kanıtlarını içerebilir.

> Aşağıdaki yol haritası programın planlanan kapsamını gösterir.
> Gerçek ilerleme repository içerisindeki dosyalar ve Git commit geçmişiyle kanıtlanır.

# 72 Modüllük Yol Haritası

## Hafta 1 — Temel Davranış ve Kanıt

| Gün | Ana konu |
| --- | --- |
| [01](day-01/day-01-return-and-exit-codes.md) | Şartname, checklist ve `return` |
| [02](day-02/day-02-assertions-and-command-chains.md) | Fonksiyon edge case’leri ve `assert` |
| [03](day-03/day-03-data-structures-and-bind-mounts.md) | `list`, `dict` ve `set` seçimi |
| [04](day-04/day-04-path-cwd-bind-mount.md) | Path, CWD, relative path ve bind mount |
| 05 | `stdout`, `stderr`, exit code ve `docker run` |
| 06 | Hafta 1 entegrasyon sınavı |
| 07 | Toparlanma 1 ve hata kapatma |

## Hafta 2 — Dosya Sistemi, İzinler ve İlk Image

| Gün | Ana konu |
| --- | --- |
| 08 | `rwx` ve minimum `chmod` |
| 09 | Ownership, group ve UID |
| 10 | Context manager ve metin dosyaları |
| 11 | `pathlib` ve `find` |
| 12 | İlk Dockerfile |
| 13 | Mastery Gate G1 |
| 14 | Toparlanma 2 ve regresyon çalışması |

## Hafta 3 — Modüler Python ve CLI Temelleri

| Gün | Ana konu |
| --- | --- |
| 15 | Modül, import ve `src/` yapısı |
| 16 | `argparse` ile CLI |
| 17 | Exception ve exit code sözleşmesi |
| 18 | JSON okuma, yazma ve doğrulama |
| 19 | CSV ve logging |
| 20 | Hafta 3 entegrasyon sınavı |
| 21 | Toparlanma 3 ve hata kapatma |

## Hafta 4 — Configuration, Process ve Kalıcı Veri

| Gün | Ana konu |
| --- | --- |
| 22 | Environment variables ve `PATH` |
| 23 | Configuration precedence |
| 24 | Process ve PID |
| 25 | Signal yönetimi |
| 26 | Named volume ve bind mount |
| 27 | Mastery Gate G2 |
| 28 | Toparlanma 4 ve regresyon çalışması |

## Hafta 5 — Subprocess ve Sistem Sınırları

| Gün | Ana konu |
| --- | --- |
| 29 | `subprocess.run` |
| 30 | Subprocess `stdout` ve `stderr` modeli |
| 31 | Timeout ve process cleanup |
| 32 | Dataclass ve type hints |
| 33 | Port, socket, DNS ve HTTP |
| 34 | Hafta 5 entegrasyon sınavı |
| 35 | Toparlanma 5 ve hata kapatma |

## Hafta 6 — Docker Compose ve Entegrasyon

| Gün | Ana konu |
| --- | --- |
| 36 | Docker Compose service modeli |
| 37 | Docker Compose network |
| 38 | Persistent data yönetimi |
| 39 | Integration test |
| 40 | Log korelasyonu |
| 41 | Mastery Gate G3 |
| 42 | Toparlanma 6 ve regresyon çalışması |

## Hafta 7 — Test Tasarımı ve Refactoring

| Gün | Ana konu |
| --- | --- |
| 43 | Pytest fixture tasarımı |
| 44 | Mocking sınırı |
| 45 | Dependency injection |
| 46 | Characterization test |
| 47 | Refactoring ve typing |
| 48 | Hafta 7 entegrasyon sınavı |
| 49 | Toparlanma 7 ve hata kapatma |

## Hafta 8 — Linux Teşhis Araçları

| Gün | Ana konu |
| --- | --- |
| 50 | `systemd` unit kavramı |
| 51 | `journalctl` filtreleri |
| 52 | `/proc` filesystem |
| 53 | File descriptor |
| 54 | `strace` ile sistem çağrısı teşhisi |
| 55 | Mastery Gate G4 |
| 56 | Toparlanma 8 ve regresyon çalışması |

## Hafta 9 — Concurrency, Mimari ve Ölçüm

| Gün | Ana konu |
| --- | --- |
| 57 | Generator ve kontrollü veri akışı |
| 58 | Thread tabanlı I/O ve final kapsamı |
| 59 | Process tabanlı CPU işleri ve ADR |
| 60 | `asyncio` ve final veri modeli |
| 61 | Profiling ve ölçüme dayalı optimizasyon |
| 62 | Mastery Gate G5 |
| 63 | Toparlanma 9 ve final açıklarını kapatma |

## Final Aşaması — CoreOps Toolkit

| Gün | Ana konu |
| --- | --- |
| 64 | Final package, CLI, config ve logging |
| 65 | Final subprocess runner ve collector |
| 66 | Deterministik JSON ve insan raporu |
| 67 | Final unit, integration ve mock testleri |
| 68 | Final Dockerfile, Compose, healthcheck ve non-root |
| 69 | Failure injection, benchmark ve final prova |
| 70 | Toparlanma 10 ve kritik açıkları kapatma |
| 71 | Code freeze, temiz kurulum ve adversarial prova |
| 72 | Final sınavı, demo ve teknik savunma |

# Final Projesi — CoreOps Toolkit

Programın final çıktısı; yerel Linux sisteminden izin verilen operasyonel bilgileri toplayan, normalize eden ve raporlayan modüler bir CLI aracıdır.

Planlanan kapsam; modüler Python paketi, CLI, configuration precedence, structured logging, custom exceptions, güvenli subprocess yönetimi, deterministik raporlar, testler, Dockerfile, Compose, healthcheck, non-root container, failure injection ve profiling çalışmalarını içerir.

## Not

Bu repository, “72 modülde uzman oldum” iddiası değildir.

Ne çalıştığımı, nerede hata yaptığımı, hataları nasıl teşhis ettiğimi ve kod yaklaşımımın zaman içinde nasıl değiştiğini gösteren açık bir gelişim kaydıdır.
