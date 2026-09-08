# CoreOps V3.7 Roadmap

> Tarihsel arşiv — 8 Eylül 2026'dan itibaren [V4 planı](ROADMAP_V4.md) geçerlidir. Aşağıdaki durum, tarih ve kapsam güncel görev talimatı değildir.

Bu yol haritası Gün 34'ten itibaren geçerlidir. İlk kez görülen yoğun konular gerektiğinde A/B oturumlarına ayrılır; B basamağı en erken sonraki çalışma gününde tamamlanır. Konu listesi değil, bağımsız uygulama ve kanıt kapanışı esastır.

## Güncel durum

- Son tamamlanan oturum: **Gün 37B — Compose network ve service DNS**
- Aktif paket: **Gün 38+39 — SQL/persistence ve API–DB entegrasyonu**
- Kesin hedef: Aksama veya zorunlu telafi olmazsa **20 Eylül 2026**
- Gün 34B–37B foundation oturumları tek çalışılır; geriye dönük birleştirilmez.

İzin verilen çift paketler:

```text
38+39   42+43   44+45   46+47
49+50   51+52   53+54   56+57
58+59   60+61   63+64   65+66
67+68
```

Çift pakette iki modül ayrı başarı kriteri ve ayrı değerlendirme kaydı taşır. İlk modül kapanmadan ikincisi kanonik ilerleme sağlamaz. Gate, prova ve final başka modülle birleşmez. Kritik açık oluşursa paket bölünür; üçlü paket yapılmaz.

## Gün 34–41 — Network, API, Compose ve veri tabanı

| Gün/oturum | Ana öğrenme | Linux hattı | Docker/Compose hattı |
| ---: | --- | --- | --- |
| 34A | URL parçaları, `urlparse`, `getaddrinfo`, `gaierror` | `getent hosts` ile resolver kanıtı | — |
| 34B | Minimal TCP bağlantısı, timeout, peer ve socket cleanup | `ss -tnp` | — |
| 35A | TLS handshake ve TCP/TLS hata ayrımı | `openssl s_client` | — |
| 35B | Minimal HTTP ve dört katmanlı failure isolation | `curl -v`, kontrollü packet gözlemi | PID 1/volume tekrarı, yerel HTTP hedefi, port publishing |
| 36A | Tek HTTP isteği, header, status ve JSON cevap | `curl` ile ikinci kanıt | — |
| 36B | Auth, timeout, pagination, retry/backoff ve 429 | ENV/token sınırı | — |
| 37A | Compose YAML, service, image/build, environment ve lifecycle | Compose loglarını süzme | İlk gerçek Compose servisi |
| 37B | Service DNS, user-defined network ve port ayrımı | Host/container DNS ve socket kanıtı | Compose network/service discovery |
| 38 | SQLite/PostgreSQL, sorgular ve transaction | DB dosyası/UID/ownership | DB service, named volume, backup/restore |
| 39 | API–DB integration ve contract test | Test process/port kanıtı | İzole test DB/Compose profili |
| 40 | Structured log ve correlation ID | `jq`, `grep`, `tail` | `docker compose logs` |
| 41 | Gate G3 | Network/API/SQL canlı teşhis | Compose arıza vakası |

## Gün 42–49 — Test, secure SDLC ve CI

| Gün | Birincil konu | Zorunlu bağlantı |
| ---: | --- | --- |
| 42 | Küçük sistem tasarımı | Adapter/data-flow/trust-boundary; process/env/file/service sınırları |
| 43 | Pytest fixture/parametrize/coverage | Boundary ve malicious-input testleri |
| 44 | External API mocking ve contract | Timeout, 429, 5xx, invalid JSON, pagination |
| 45 | Dependency injection ve threat modeling | Trust boundary, token/secret, non-root/read-only ve least privilege |
| 46 | Characterization/refactor ve static analysis | `ruff`, `mypy`, `bandit`, `pip-audit` |
| 47 | GitHub Actions ve supply chain | Test+lint+type+scan+Docker build; SBOM temeli |
| 48 | Secure-SDLC sınavı | Bozuk CI/log ve Git conflict canlı vaka |
| 49 | Kalite toparlanması | En düşük iki beceriyi yeni kanıtla kapatma |

## Gün 50–56 — Production Linux ve Docker incident

| Gün | Birincil konu | Docker bağlantısı |
| ---: | --- | --- |
| 50 | `systemd` unit ve least privilege | User/group, env file, restart ve sandbox seçenekleri |
| 51 | `journalctl` ve log lifecycle | `docker logs`, rotation ve disk etkisi |
| 52 | `/proc`, cgroup ve resource gözlemi | CPU/memory limits, throttling ve OOM modeli |
| 53 | File descriptor, socket ve `lsof` | Container içi socket/FD görünürlüğü |
| 54 | Katmanlı production teşhisi | Namespace bağlamında `strace`, `curl`, `openssl`, `tcpdump` |
| 55 | Gate G4 | Linux incident + Docker runtime/resource arızası |
| 56 | Mock interview ve hedefli toparlanma | Yalnız kanıtlanan açıklar |

## Gün 57–63 — Performans, concurrency ve orkestrasyon

| Gün | Birincil konu | Zorunlu bağlantı |
| ---: | --- | --- |
| 57 | Generator/streaming ile büyük veri | Büyük JSONL/CSV, memory ölçümü, backpressure |
| 58 | Thread ile paralel API I/O | Thread safety, shared state, connection pool |
| 59 | Process ile CPU işi | Asset normalization/dedup, IPC maliyeti |
| 60 | Bounded `asyncio` ve rate limiting | Semaphore, cancellation, retry budget |
| 61 | Profiling ve benchmark | CPU/RSS ölçümü; ölçmeden optimizasyon yapmama |
| 62 | Gate G5 | Sync/thread/async tasarım savunması |
| 63 | Kubernetes okuryazarlığı | Pod, Deployment, Service, ConfigMap, Secret, logs/describe |

## Gün 64–72 — Final Asset Intelligence Collector

| Gün | Final parçası | Linux/Docker/Git kanıtı |
| ---: | --- | --- |
| 64 | Final package/CLI/config/log | Collector iskeleti, ADR ve branch planı |
| 65 | Final API/subprocess adapter | Auth, pagination, retry, rate limit, source lineage |
| 66 | Normalize/dedup/correlate/prioritize | SQL + CVSS/EPSS/KEV/business criticality |
| 67 | Tests/mock/CI/security scans | Coverage, contract tests ve quality gates |
| 68 | Production Docker/Compose | Multi-stage, health/readiness, non-root, read-only, limits |
| 69 | Final prova ve mock interview | Live coding + Linux + Git + Docker + system design |
| 70 | Prova açıklarını kapatma | Yalnız bulunan eksikler üzerinde çalışma |
| 71 | Hardening/code freeze/release | Threat model, SBOM, changelog, tag, runbook |
| 72 | Final sınav | Demo, failure diagnosis ve 45 dakikalık teknik görüşme |

## Süreklilik kuralı

Linux hattı network araçlarıyla, log korelasyonuyla, Gün 50–55 production teşhisiyle ve performans ölçümleriyle devam eder. Docker/Compose hattı DB persistence, integration test, CI build/scan, cgroup/resource incident, Kubernetes eşlemesi ve production image/release aşamalarına ilerler. Sırf container çalıştırmış olmak için Docker kullanılmaz; buna karşılık beş öğretim oturumundan uzun süre yeni Linux veya Docker mekanizması görülmeden geçilmez.

## Mastery kapısı

Bir beceri, yalnız komut çalıştı diye tamamlanmaz:

- **Bağımsız:** Yeni veride yardımsız uygulanır.
- **Transfer:** Farklı bağlam veya failure mode'da doğru araç seçilir.
- **Usta:** Mekanizma, trade-off, karşıt koşul ve doğrulama savunulur.

Her gate; canlı Python, Linux teşhisi, Git/Docker senaryosu ve kısa security/system-design savunması içerir.
