# CoreOps V3 Roadmap

Bu yol haritası Gün 18'den itibaren geçerlidir. Önceki planla çelişen konularda bu belge üstündür.

## Hızlandırılmış çalışma düzeni

22 Eylül hedefi için izin verilen çift paketler:

```text
18+19   21+22   23+24   25+26
29+30   31+32   35+36   37+38
43+44   45+46   50+51   52+53
57+58
```

Çift pakette iki modül ayrı başarı kriteri ve ayrı değerlendirme kaydı taşır. Gate ve final günleri başka modülle birleştirilmez. Kritik açık oluşursa paket bölünür; mastery hedef tarihten önceliklidir.

## Gün 18–27 — Data, Git ve sistem temeli

| Gün | Birincil konu | Zorunlu bağlantı |
| ---: | --- | --- |
| 18 | JSON syntax/semantik; parse → validate → output | `jq`; working tree–index–`HEAD`; `diff --staged` |
| 19 | CSV/JSONL ve structured logging | `tee`, `tail`, `grep -E`, temel `awk`; `git log/show` |
| 20 | Veri sözleşmesi entegrasyon sınavı | Bozuk veri teşhisi ve kapalı-kitap sözlü tur |
| 21 | CAASM ve asset-intelligence girişi | Asset, inventory, attack surface, exposure ve vulnerability |
| 22 | Environment, `PATH` ve secret sınırı | `env`, `printenv`, `command -v`, `type`, `.gitignore` |
| 23 | Config, dependency yönetimi ve image cache | `venv`, `pip`, `pyproject.toml`; layer/cache, `docker history`, `.dockerignore` |
| 24 | Process/PID ve kaynak gözlemi | `ps`, `pgrep`, `pstree`, `/proc`, parent-child |
| 25 | Signal, job control ve graceful shutdown | `jobs`, `wait`, `kill -TERM`, Docker PID 1 |
| 26 | Filesystem/persistence ve named volume | `stat`, `du`, `df`, mount/ownership, bind vs named volume |
| 27 | Gate G2 | Python + Linux + Git + Docker canlı teşhis |

## Gün 28–41 — Subprocess, network, API, SQL ve Compose

| Gün | Birincil konu | Zorunlu bağlantı |
| ---: | --- | --- |
| 28 | Gate toparlanması ve mock interview | En zayıf iki beceriyi yeni vakada kapatma |
| 29 | Güvenli `subprocess` ve argv | `shell=True`/injection karşıtı deney; branch/switch |
| 30 | Child process contract ve cleanup | Timeout, process group ve kontrollü sonlandırma |
| 31 | Git branch/merge/conflict ve geri alma | `restore`, `revert`, kayıpsız conflict çözümü |
| 32 | Data model, type hints ve package kalitesi | Dataclass/schema, `ruff`, `mypy` |
| 33 | IP/CIDR, route, DNS, TCP, HTTP ve TLS | `ip`, `ss`, `curl`, `dig/getent`, `openssl s_client` |
| 34 | Network/API entegrasyon sınavı | DNS–TCP–TLS–HTTP hata katmanları |
| 35 | Packet gözlemi ve ağ mülakatı | Kontrollü `tcpdump` ve HTTP trace |
| 36 | HTTP API client ve Compose service/config | Token, pagination, timeout, retry/backoff, rate limit |
| 37 | Docker network, port ve service discovery | Compose DNS; refused/timeout/DNS ayrımı |
| 38 | SQLite/PostgreSQL ve persistent volume | `SELECT`, `WHERE`, `JOIN`, `GROUP BY`, transaction, backup |
| 39 | API/database integration tests | Contract test ve pull-request/review akışı |
| 40 | Log correlation ve güvenlik verisi | Correlation ID, SIEM; CVE/CVSS/EPSS/KEV |
| 41 | Gate G3 | API + network + SQL + Compose + Git canlı vaka |

## Gün 42–55 — Test, secure SDLC ve production Linux

| Gün | Birincil konu | Zorunlu bağlantı |
| ---: | --- | --- |
| 42 | Sistem tasarımı ve toparlanma | Adapter/data-flow/trust-boundary çizimi |
| 43 | Pytest fixture/parametrize/coverage | Boundary ve malicious-input testleri |
| 44 | External API mocking ve contract | Timeout, 429, 5xx, invalid JSON, pagination |
| 45 | Dependency injection ve threat modeling | Trust boundary, token/secret, least privilege |
| 46 | Characterization/refactor ve static analysis | `ruff`, `mypy`, `bandit`, `pip-audit` |
| 47 | GitHub PR/review/CI ve supply chain | Test+lint+type+scan+Docker build; SBOM |
| 48 | Secure-SDLC sınavı | Bozuk CI/log ve Git conflict canlı vaka |
| 49 | Kalite toparlanması | En düşük iki beceriyi yeni kanıtla kapatma |
| 50 | `systemd` unit ve least privilege | User/group, env file, restart ve sandbox seçenekleri |
| 51 | `journalctl` ve log lifecycle | Filtre, zaman aralığı, follow, rotation, disk etkisi |
| 52 | `/proc`, cgroup ve resource gözlemi | CPU/memory ve container limitleri |
| 53 | File descriptor, socket ve `lsof` | FD leak/open file/listening socket ayrımı |
| 54 | Katmanlı production teşhisi | `strace`, `curl`, `openssl`, `tcpdump` |
| 55 | Gate G4 | Linux incident + Docker teşhis + sözlü savunma |

## Gün 56–72 — Performans, final ürün ve mülakat

| Gün | Birincil konu | Zorunlu bağlantı |
| ---: | --- | --- |
| 56 | Toparlanma ve mock interview | 30 dakikalık karma teknik görüşme |
| 57 | Generator/streaming ile büyük veri | Büyük JSONL/CSV, memory ölçümü, backpressure |
| 58 | Thread ile paralel API I/O | Thread safety, shared state, connection pool |
| 59 | Process ile CPU işi | Asset normalization/dedup, IPC maliyeti |
| 60 | Bounded `asyncio` ve rate limiting | Semaphore, cancellation, retry budget |
| 61 | Profiling ve benchmark | CPU/RSS ölçümü; ölçmeden optimizasyon yapmama |
| 62 | Gate G5 | Sync/thread/async tasarım savunması |
| 63 | Kubernetes okuryazarlığı | Pod, Deployment, Service, ConfigMap, Secret, logs/describe |
| 64 | Final package/CLI/config/log | Collector iskeleti, ADR ve branch planı |
| 65 | Final API/subprocess adapter | Auth, pagination, retry, rate limit, source lineage |
| 66 | Normalize/dedup/correlate/prioritize | SQL + CVSS/EPSS/KEV/business criticality |
| 67 | Tests/mock/CI/security scans | Coverage, contract tests ve quality gates |
| 68 | Production Docker/Compose | Multi-stage, health/readiness, non-root, read-only, limits |
| 69 | Final prova ve mock interview | Live coding + Linux + Git + Docker + system design |
| 70 | Prova açıklarını kapatma | Yalnız bulunan eksikler üzerinde çalışma |
| 71 | Hardening/code freeze/release | Threat model, SBOM, changelog, tag, runbook |
| 72 | Final sınav | Demo, failure diagnosis ve 45 dakikalık teknik görüşme |

## Mastery kapısı

Bir beceri, yalnız komut çalıştı diye tamamlanmaz:

- **Bağımsız:** Yeni veride yardımsız uygulanır.
- **Transfer:** Farklı bağlam veya failure mode'da doğru araç seçilir.
- **Usta:** Mekanizma, trade-off, karşıt koşul ve doğrulama savunulur.

Her gate; canlı Python, Linux teşhisi, Git/Docker senaryosu ve kısa security/system-design savunması içerir.
