# CoreOps V4.1 — Python / Linux / Docker staj hazırlığı

**Yürürlük: 13 Eylül 2026. Hedef değerlendirme: 21 Eylül 2026.**
Kullanıcının son isteği: geçmiş kazanımları koruyarak Python/Linux/Docker'da stajda küçük bir işi bağımsız yapabilecek deneyim kazanmak; gerçek eksiği kapatmak, bilinenleri uygulamayla pekiştirmek. İşe kabul veya üç alanda tam ustalık garantisi verilmez.
Bu metin V4 takvimi, HTTP retry/thread zorunluluğu, final kabulü ve mevcut V4-05 görevini aşağıdaki kapsamla değiştirir. V4'ün öğretim-önce ve kısa teslim kuralları korunur.

## 1. Gerçek başlangıç ve denetim

Mentor ve kanonik 13 Eylül kayıtları: V4-01, 02, 03, 04 GEÇTİ. Son tamamlanan V4-04; zorunlu telafi yok. Repo day-41..44 bu oturumların kayıtlarıdır; eski 72'lik rota bu klasör numaralarıyla otomatik ilerlemez.

| Alan | Var olan kanıt | Şimdi gereken |
|---|---|---|
| Python temeli | CLI, modül, exception, veri yapıları/JSON/CSV, venv/dependency, subprocess, parametreli SQL, logging | Bunları küçük bir yeni gereksinimde bağımsız birleştirmek; hepsini yeniden ders yapmak değil |
| Python test/streaming | Day42 fixture/parametrize/monkeypatch başarı/boş/hata; Day44 yield/JSONL ve sayfalama | Mevcut dosya okuyucusunu gerçek pytest testine bağlamak, kütüphane/CLI hata sınırını düzeltmek |
| Linux temeli | İzinler, process/signal, path/mount, shell/pipe, ağ gözlemi | Servis/dosya/kaynak teşhisinde bağımsız transfer |
| Linux servis | Day43 gerçek Ubuntu User/ExecStart/env/CWD, reload/restart, journal ve minimum izin düzeltmesi | Yeni küçük timer/oneshot uygulaması; aynı servis/PermissionError dersini tekrar etmemek |
| Docker | Day23 cache/.dockerignore; Day25 PID1/signal; Day26 volume/bind; Day37 Compose DNS/network; Day40–41 readiness | Volume geri çağırma + gerçek restore, build-time dependency kurulumu, runtime kullanıcı/yazma yolu ve kaynak limitleri |
| Entegrasyon | Day41 success/empty/connect failure, doğru event ayrımı ve temiz DB/schema kurulumu | Bu kapatılmış açıkları tekrar borç saymamak; gerçek test/CI ve temiz image çalıştırması |

Kodda doğrulanan somut noktalar (13 Eylül, commit f38a0ad):
- day-44/blok1/tests/test_records.py ve blok2/tests/test_pagination.py boş. Test mekanizması Day42'de öğrenilmiş; aktarımı henüz bu koda yapılmamış. HTTP testlerini bu dönemde ayrıca büyütmek zorunlu değil.
- day-44/blok1/src/records.py:20–22 içinde JSON hatası generator'dan sys.exit(1) ile programı kapatıyor. Day44 streaming başarısını iptal etmez; sonraki küçük refactor için gerçek Python fırsatıdır.
- day-41/day41-postgres-cli/compose.yaml:39–41 app başlangıcında pip install yapıyor. Yeni Docker dersi bu kurulumu image build aşamasına taşıyacak.
- .github/workflows/validate.yml yalnız hijyen ve py_compile içeriyor. Yeşil CI, davranış testleri geçti demek değil. Yeni seçilmiş proje testleri ve build öğrencinin uygulamasıyla eklenecek.
- Day41 yeniden üretilebilir DB ve connect/query hata ayrımı artık kapalıdır. Eski rapordaki bu açıkları geri getirme.
Bu denetim kod ve teslim okumasıdır; bütün lablar yeniden çalıştırılmadı, kalıcı bağımsızlık testi yapılmış sayılmaz.

## 2. Kapsam ve ilerleme

Eski V4-05 timeout/retry/backoff/429 + fake-sleep paketi ZORUNLU KAPSAMDAN ERTELENDİ. Yapılmadığı için başarısız/telafi değil; tamamlandı da sayılmaz. Varsa öğrencinin başladığı kod korunur; bitirmesi istenmez.
HTTP auth/timeout/pagination bilgisi korunur; mevcut kodda temel timeout/hata mesajını kaldırma. Ayrıntılı HTTP policy veya yeni ağ güvenliği dersi açma.
ThreadPoolExecutor/profiling, process/async uygulamaları, Kubernetes sonraki döneme bırakıldı.
CAASM/CVSS/EPSS/KEV, threat-model/SBOM, source-lineage ve güvenlik ürünü yok. Var olan risk/asset isimlerini sırf isim için yeniden yazdırma; yeni örnekler genel dosya/servis/veri raporu olsun.
SQL mevcut çalışma kadar kullanılır; yeni ORM/ileri DB/API server zorunlu değil.
Git/CI destekleyici, günlük ekstra komut/form borcu değil.

17 Eylül ilerleme güncellemesi COREOPS_V4_1_STAJ: V4-01..04 ve V4.1-05..08 GEÇTİ; zorunlu açık yok. V4.1-08 / Gün 48, 16 Eylül Linux ve 17 Eylül Docker CPU limiti devamıyla kapandı. RAM/OOM labı yapılmadı; mentor zorunlu açık saymadı. Sıradaki V4.1-09 / Gün 49 Blok 1A verildi, henüz tamamlanmadı. Eski V4-05 retry görevi ile V4.1-05 timer oturumunu karıştırma. Ayrıntılı gün eşlemesi için [DAY_INDEX](DAY_INDEX.md).
Eksik kanıt = otomatik beceriksizlik değil. Bilinen konuda lab içinde küçük varyantla kontrol et; bağımsız yapıyorsa geç. Yardım gerekiyorsa sadece ilgili parçayı öğret, tüm günü tekrar ettirme.

## 3. Kalan takvim ve yük

Aşağıdaki tarihler 13 Eylül'de belirlenen hedef takvimdir; gerçekleşen bitiş tarihleri değildir. Gün 48'in Docker devamı 17 Eylül'de tamamlandı. Takvim günü değişince yeni eğitim günü açılmaz; güncel durum yukarıdaki ilerleme kaydı ve gün indeksindedir.

Her net süre ders, kaynak, küçük örnek, uygulama/test dahil tahmindir; 5–6 saat kullanılabilir pencereyi doldurma kotası değildir. HackMasters ayrıca. Çoğu normal tarih iki 60–120 dakikalık çalışma parçası + kısa doğrulama/aralar şeklindedir. 13 Eylül'de V4-04 zaten yapıldı; ayrıca tam günlük yük eklenmez.

| Tarih/hedef | Oturum | Yeni öğrenme veya pekiştirme | Net tahmin |
|---|---|---|---|
| 13 Eylül kalan zaman uygunsa | V4.1-05 | Mevcut servis bilgisinden küçük Type=oneshot + timer; zamanlanan tek seferlik küçük Python dosya raporu. Uzun çalışan service'in aynısını yeniden kurma | 60–90 dk; bugün çalışmak zorunlu değil |
| 14 Eylül | V4.1-06 | Volume/bind/container kısa geri çağırma; mevcut lab DB yedeğini ayrı boş test DB'sine restore ve sorgu. Readiness/network zaten biliniyorsa yalnız uygulama | 3–4 sa |
| 15 Eylül | V4.1-07 | /proc FD + lsof, sonra tek dosya erişimini dar strace ile izle. Python mevcut JSONL okuyucuya ilk tmp_path testi; yeni fixture önce küçük örnekle | 3–4 sa |
| 16 Eylül | V4.1-08 | Linux CPU/RAM/process/disk gözlemi ve kontrollü Docker kaynak limiti. Python okuma/filtreleme fonksiyonunun hata sınırını testle düzelt | 3–4 sa |
| 17 Eylül | V4.1-09 | Var olan app için önce normal Dockerfile: paketler build sırasında; sonra küçük multi-stage. Non-root ve gerekli yazılabilir yol. Cache/PID1 temelini yeniden anlatma | 4–5 sa |
| 18 Eylül | V4.1-10 | Mevcut küçük Python rapor aracında CLI/config/girdi→işleme→çıktı; temiz venv ve gerçek testleri CI'a bağla, image build doğrula | 4–5 sa |
| 19 Eylül | Tampon | Önce açık kalan çekirdek iş, gerekirse ertelenmiş timer. Yeni konu ekleme; açık yoksa dinlenme | 0–5 sa |
| 20 Eylül | V4.1-11 | Küçük bağımsız Python değişikliği + Linux arıza çözümü + Docker config/data vakası; temiz kurulum/README | 3–4 sa |
| 21 Eylül | V4.1-12 | Üç alan finali/demo, hedefli yeniden kontrol ve dürüst beceri özeti | 3–4 sa |

13 Eylül zamanı yetmezse timer'ı sonraki uygun küçük bloğa/19 Eylül'e kaydır; her tarihi zincirleme şişirme. Tarih geldi diye tamamlandı yazma. Kritik açık kapanmazsa 21 Eylül değerlendirme tarihi korunur, başarı hükmü verilmez.

## 4. Uygulama sınırları

Amaç bir dev proje değil: mevcut Genel Veri İşleyici CLI'nin küçük yerel rapor sürümü + mevcut Docker/PostgreSQL labı.
- Python çekirdeği mevcut JSONL okuyucu/filtreleyici ve argparse bilgisinden gelişir. Girdi dosyası ve çıktı yolu seçilir, kayıtlar işlenir ve küçük JSON/CSV özet yazılır. Küçük fonksiyonlar, açıklanabilir hata davranışı ve birkaç anlamlı test. HTTP adapter veya DB'ye yeni insert/şema zorunlu değil.
- Day41 Python→PostgreSQL sorgusu ve Compose ağ bilgisi ayrı çalışan kanıt olarak kullanılabilir; her şeyi tek dosya/uygulamada birleştirme şartı yok.
- Mevcut subprocess bilgisi restore komutunu anlamakta kullanılabilir; ayrıca Python backup framework, retention sistemi, ayrı cron dersi ve ikinci CLI yazdırma.
- Timer için biten küçük iş kullan; sonsuz while/sleep service'i doğrudan tekrar başlatma labına çevrilmesin. Önce tek timer çalışması sonra küçük farklı zaman ayarı. Persistent/OnCalendar seçilirse kaçırılan bütün işleri tek tek yeniden oynatacağı söylenmez. Mevcut unit'i bozma; ayrı lab unit'i ve sonunda durdurma/temizlik bilgisi ver. Bu bir öğrencinin Linux labı, Codex otomasyonu kurma talimatı değildir.
- Restore yalnız ayrı test DB/projesinde; asıl veri/volume silinmez. Canlı PostgreSQL data dizinini tar ile kopyalamak tutarlı DB yedeği yerine geçmez. Dump'ın geri yüklenmesi ve sorgu esas.
- CPU/RAM örneği küçük ve kontrollü limitli; hostu/VM'yi tüketme, OOM korumasını kapatma. Exit137 tek başına OOM kanıtı diye öğretilmez; ilgili state/log ile doğrula.
- Docker dersinde önce normal image build ve run, sonra multi-stage; ilk kez bütün hardening seçeneklerini bir araya yığma. Wheel/build örneği gerekiyorsa ufak ve açıklamalı, yayınlama/registry zorunlu değil.
- Python testleri gerçek okuma/filtreleme fonksiyonunu çalıştırır; sadece monkeypatch etmiş olmak için fake HTTP labı yok. tmp_path ilk kez görülüyorsa kısa öğret. Geçersiz JSON, normal sonuç, seçilen sınır davranışı gibi önemli vakalar yeter; test adedi/coverage kotası yok.
- Python yorumlayıcı/dependency sürümünü gerçek koda göre seç. Day41 LoggerAdapter merge_extra gibi 3.13 özelliği varsa sırf syntax CI 3.12 diye runtime da çalışır varsayma.
- SSH/temel shell/venv/izin/Git gibi staj temelleri temiz kurulum/prova içinde gözlenir. Bildiğini tekrar anlatma; gerçek açık varsa tamponda o parçayı öğret. Gereksiz yeni uzak sunucu/hesap açtırma.

## 5. Öğretim ve değerlendirme sözleşmesi

Aynı iki sohbet: CoreOps — Kanonik Günlük Görev üretir; Günlük Koçluk ve Teslim değerlendirir. Kullanıcı istediğinde, aynı kanonik sohbette görev. Yeni sohbet veya otomasyon yok; otomatik sohbetler arası senkron iddiası yok.
Her yeni kavram: kısa açıklama → 1–2 dar resmi kaynak ve okuma amacı → küçük açıklamalı çalışan örnek → tek rehberli değişiklik → küçük bağımsız varyant. Sonra entegrasyon.
İlk mesaj yalnız ilk küçük adımı açar. Örnek, lab, broken case, varyant, test ve checklist başlıklarında aynı işi tekrar tekrar zorunlu ödeve dönüştürme. Bir örnek ve bir bağımsız uygulama yeter; hata vakası onun ilgili testinin içinde olabilir.
Öğrenci teslimi kod/commit + ilgili kısa çıktı + en fazla 2–3 cümle. Ayrı diagnosis/state/decomposition raporu yok. Koddan önce gerekirse 2–3 sözlü maddeyle parçalama; zamanlı drill değil.
Mentor yalnız verilmiş blok kapsamını değerlendirir. Day42'de düzeltilmiş hata tekrarlanmasın: henüz verilmemiş Blok2 yüzünden Blok1'e telafi yazma. Eskiden kabul edilmiş mekanizmayı yeni ölçütle geriye dönük başarısız sayma.
Yardımlı örnek öğrenme içindir; bağımsızlık farklı küçük uygulamayla ölçülür. Resmi doküman/man serbest, asıl çözümü AI yazmışsa bağımsız diye kaydetme. Öğrenciyi küçümseyen değerlendirme dili kullanma.
Aktarım kaydı mentor tarafından kısa üretilir: sürüm, oturum/blok, sonuç, kanıtlanan beceri/yardım, varsa tek açık, sıradaki. Kullanıcı bir kez kanoniğe taşır.

## 6. Staj hazırlığı bitiş ölçütü

Bu liste işe alım şirketinin doğrulanmış sınavı değil; kullanıcı tarafından aktarılan Python/Linux/Docker beklentisi için önerilen pratik yeterlilik ölçütüdür:
1. Python: kısa bir dosya/veri işini küçük fonksiyonlara ayırıp CLI üzerinden çalıştırmak; normal/bozuk girdiyi yönetmek; gerçek test yazıp başarısız testi düzeltebilmek.
2. Linux: kendi programını uygun kullanıcı/env/CWD ile çalıştırmak; service/log/process/dosya/kaynak sorununun nedenini bulup küçük düzeltme yapmak.
3. Docker: uygulamayı build edip çalıştırmak; config/network/volume ayrımını açıklamak; log/inspect ile küçük sorunu bulmak; yedeği ayrı ortama geri yüklemek.
4. Teslim: temiz ortamda çalıştırılabilir repo, birkaç gerçek test/CI, kısa README ve açıklayabildiği küçük değişiklik.
Final sadece öğretilenlerden olur; her alanda bağımsız küçük iş aranır. Aynı adımı ezberleyip tekrarlamak veya yüksek eski puan, otomatik master/staj kabul garantisi değildir.
Sonraya kalan retry/thread/async/Kubernetes veya güvenlik başlıkları final şartı olamaz.

## Kaynak dayanakları (öğrenciye toplu okuma ödevi değil)

- pytest tmp_path, dosya testi: https://docs.pytest.org/en/stable/how-to/tmp_path.html
- Python subprocess (mevcut bilgi): https://docs.python.org/3/library/subprocess.html
- systemd timer upstream: https://github.com/systemd/systemd/blob/main/man/systemd.timer.xml ; labda kurulu sürümün man systemd.timer bölümü tercih edilir.
- Docker volumes: https://docs.docker.com/engine/storage/volumes/
- PostgreSQL dump/restore: https://www.postgresql.org/docs/current/backup-dump.html
- Docker build: https://docs.docker.com/build/building/best-practices/
- Multi-stage: https://docs.docker.com/build/building/multi-stage/
- Docker kaynak limitleri: https://docs.docker.com/engine/containers/resource_constraints/

Teknik kaynaklar 13 Eylül 2026'da kontrol edildi. Öğrenme öncelikleri bu kaynakların işe alım garantisi değil, mevcut teslimlere göre eğitim değerlendirmesidir.
