# CoreOps V4 — 21 Eylül 2026 yürürlük planı

> 13 Eylül 2026: Güncel kapsam ve kalan takvim [V4.1 staj odaklı plan](ROADMAP_V4_1.md) içindedir. V4-01..04 tamamlandı; aşağıdaki eski retry/thread zorunlulukları ve başlangıç durumu artık geçerli değildir. Bu belge geçmiş referanstır.

Kullanıcı onayı: 8 Eylül 2026. Bu belge yeni görev ve değerlendirmelerde eski V2/V3/V3.7 rota, süre, güvenlik kapsamı, 04.30 şartı ve uzun teslim şablonlarının yerine geçer. Eski belgeler tarihsel referanstır; sources/ değiştirilmez.

## Başlangıç ve roller

8 Eylül canlı kontrolünde iki sohbet de Gün 40 GEÇTİ, 97/100, zorunlu telafi yok kaydını doğruladı. Gün 39'a geri dönülmez. Logging/LoggerAdapter/correlation ve aynı UndefinedColumn labı tekrarlanmaz. Readiness kullanımı da kanıtlıdır; bağımsızlık gerekirse küçük varyantla kontrol edilir. db_connect_failed ile db_query_failed ayrımı küçük ileriki iyileştirmedir, telafi borcu değildir.

Tek görev üretici: CoreOps — Kanonik Günlük Görev (6a5b2c73-b248-83ed-a501-bef4f0a715ec).
Tek mentor: Günlük Koçluk ve Teslim (6a53a0eb-f524-83eb-b808-10327c1988cf).
Görev kullanıcı istediğinde aynı kanonik sohbette verilir; yeni sohbet, zamanlanmış görev, üçüncü kontrol katmanı yok. Kullanıcı mentorun kısa sonucunu bir kez kanoniğe aktarır. Sohbetler otomatik birbirini okuyor/senkronluyor varsayılmaz.

Eski Gün 41 henüz geçmedi. Sıradaki oturum V4-01: eski 34–40 kapsamında 30–45 dakikalık küçük bağımsız uygulama kontrolü; yeni araç/kütüphane yok. Uzun eski gate paketi uygulanmaz; eski tam gate geçildi iddiası kurulmaz. Sonra ihtiyaç varsa mevcut test DB kurulumunu yeniden üretilebilir hale getir. Gün 40 bugün yapıldığı için 8 Eylül'e ayrıca 4–5 saat ödev ekleme. Kalan işi 19 Eylül tamponuna kaydet.

Yeni ilerleme V4 oturum kimliği + tarih + gerçek kapsamla izlenir. Eski 42–72 numaralarını sırayla GEÇTİ yazma. Tamamlanan 1–40 korunur; kaldırılan/ertelenen başlıklar başarısızlık değildir.

## Süre ve kapsam

Hedef 21 Eylül 2026. CoreOps için günlük 5–6 saatlik pencere var; HackMasters bunun dışında. Plan çoğu tarihte 4–5 saat net ders/uygulama/test tahminidir; tek eski modülün beş saate şişirilmesi değildir. 1–2 saatlik parçalar halinde sunulur. Kaynak okuma ve öğretim bu süreye dahildir. Hızlı ve bağımsız bitirene süre doldurma ödevi yok.

Ana alanlar Python, Linux, Docker. Git/CI yalnız küçük destek akışı.
CAASM, CVSS/EPSS/KEV, ağ güvenliği/CTF, threat model, SBOM, source-lineage, risk motoru, ayrı speed/decomposition/cross-layer drill kaldırıldı.
Parametreli SQL, sırları loglamama, non-root ve gerekli DNS/HTTP/port kavramları ilgili uygulamanın parçasıdır; ayrı güvenlik dersi değil.
Detaylı multiprocessing/IPC, asyncio/cancellation, Kubernetes, ileri profiling ve kernel/cgroup teorisi bu hedef sonrasına ertelendi.

## Her yeni konuda zorunlu öğretim

1. Kısa ve somut açıklama: ne, neden, mevcut bilgilerle ilişkisi.
2. Bir–iki resmi kaynak, tam bölüm/link ve neyi öğrenmek için okunacağı. Kaynak listesini açıklamanın yerine koyma.
3. Küçük çalışan, açıklamalı örnek; yalnız yeni kavramı göstersin.
4. Öğrencinin tek değişiklik yaptığı rehberli alıştırma.
5. Küçük farklı girdili bağımsız uygulama.
6. Ancak oturduktan sonra mevcut projeye entegrasyon.

İlk mesajda günlük iki bloğu birer cümleyle özetle, sadece ilk bloğun dersini ve küçük alıştırmasını ayrıntılandır. İkinci büyük labı peşinen yığma. Örnek kod öğretimde serbest; bağımsız labın tam çözümünü baştan verme. Takılınca önce ipucu ve hedefli açıklama. Tam çözüm desteği aldıysa yargılamadan benzer küçük bağımsız varyantla öğrenmeyi doğrula.
Bilinen konuda aynı başlangıç dersini tekrar etme. Günlük en çok iki yeni kavram kümesi; anlamadıysa ikinci blok pekiştirmeye dönüşür. Takvim için anlamadan ilerletme.

## Takvim

| Tarih | Net süre tahmini | Öğrenme/uygulama |
|---|---|---|
| 8 Eylül | Gün 40 çalışmasına ek yalnız 30–45 dk kontrol; kurulum gerekirse sonraya | V4-01 kısa bağımsız önceki-beceri kontrolü; test DB yeniden kurulum açığını belirle |
| 9 Eylül | 4,5 sa | pytest basit test, fixture, parametrize; tek dış bağımlılığa fake/monkeypatch; başarı/boş/hata |
| 10 Eylül | 4,5 sa | Gerçek Ubuntu systemd unit/ExecStart/user/env/CWD; journalctl; bir config/izin hatası |
| 11 Eylül | 4,5 sa | Önce yield/JSONL streaming; ayrı küçük blokta mevcut HTTP client iki sayfalı pagination |
| 12 Eylül | 4,5 sa | Timeout, sınırlı GET retry/backoff ve 429; sahte cevap/bekleme testleri; concurrency yok |
| 13 Eylül | 4,5 sa üst sınır | Bilinen Compose readiness'e kısa farklı vaka; volume/bind/image/container kısa hatırlatma; yeni konu izole test DB'ye restore ve sorgu |
| 14 Eylül | 4,5 sa | /proc, FD, lsof; dar strace dosya/izin hatası |
| 15 Eylül | 4,5 sa | Linux CPU/RAM/process ölçümü; Docker kaynak limitleri kontrollü küçük workload; bilinen beceride kısa kontrol |
| 16 Eylül | 5 sa | Küçük multi-stage Dockerfile/cache; ayrı küçük non-root ve gerekli yazma yolu/read-only uygulaması |
| 17 Eylül | 4,5 sa | Küçük sabit I/O listesinde ThreadPoolExecutor, sonuç/hata; seri/thread süre; temel cProfile |
| 18 Eylül | 5 sa | Birikmiş veri CLI'sini birleştir; gerçek testleri CI'da çalıştır, Docker build, kısa kurulum notu |
| 19 Eylül | 0–5 sa | Gerçek tampon/telafi; açık yoksa dinlenme, yeni konu ekleme |
| 20 Eylül | 4 sa | Bağımsız Python/Linux/Docker prova, düzeltme, temiz kurulum ve README/tag hazırlığı |
| 21 Eylül | 4 sa | Üç alan finali, demo, geri bildirim ve hedefli tekrar kontrol |

9–21 Eylül planlı net süre 54 saattir; 19 Eylül için ayrıca en çok 5 sa rezerv vardır. 8 Eylül'de zaten tamamlanmış çalışma tekrar bütçelenmez. Her süre tahmindir, doldurulması gereken kota değildir. Kayma varsa tampon kullanılır; kritik açık bitiş tarihinde otomatik başarılı sayılmaz.

## Teknik sınırlar ve proje

Final: Genel Veri İşleyici CLI. Mevcut JSON/HTTP/PostgreSQL kodu büyütülür; yeni API sunucusu, UI, ORM, ikinci DB ve güvenlik ürünü yok. Mevcut tablo isimlerini zorunlu yeniden adlandırma yok.
Küçük ders çıktıları birikir, 18 Eylül'de sıfırdan dev proje verilmez.
- Test DB/schema temiz kurulumla üretilebilsin; çalışma/kişisel DB silinmesin.
- JSONL satır satır okunsun, bozuk kayıt davranışı açık olsun.
- HTTP pagination sonlansın; retry sınırlı olsun. 401 veya bozuk veriye kör retry yok; timeout toplam süre garantisi diye sunulmaz.
- SQL parametreli; tekrar girdi davranışı açık.
- Başarı/sınır/hata testleri gerçekten davranışı ölçsün, CI test ve image build çalıştırsın.
- Multi-stage image, non-root, yazma yolu, Compose readiness/volume/restore anlaşılabilsin.
- Restore yalnız ayrı boş test DB'sine; asıl veri/volume silme yok.
- Linux service/log/FD/resource küçük vaka gerçek Linux'ta çalışılsın; macOS'ta systemd varmış gibi yapılmasın.
- Thread uygulaması küçük sabit listeyle; max_workers sınırsız kuyruk/bellek çözümü diye öğretilmesin. Paralel DB yazımı zorunlu değil.
- Kısa README: kurulum, kullanım, test, kalanlar. Uzun mimari rapor yok.

## Teslim ve değerlendirme

Normal teslim: kod veya commit bağlantısı + kısa ilgili test/çıktı + en çok 2–3 cümle. Her gün tahmin tablosu, hipotez formu, Git raporu, mülakat, öğrenme günlüğü, ayrı güvenlik kanıtı istenmez. Problem parçalama kodun yanında gerekirse 2–3 maddede rehberliktir; ayrı zamanlı drill değil.

Mentor yalnız verilen ve öğretilen kapsamı değerlendirir. Eski security/Git/yenilik borçları veya 72-modül şartı kullanılamaz. Öğretim yetersizse bunu öğrenci kusuru diye puanlama. Sadece önemli ve kanıtlanmış açık için küçük hedefli telafi; bütün günü tekrar ettirme.

Mentor kısa değerlendirme ve şu kısa aktarım kaydını üretir:
- Sürüm: COREOPS_V4_21_EYLUL
- Oturum/tarih:
- Sonuç: GEÇTİ / HEDEFLİ TELAFİ / DEVAM
- Kanıtlanan beceri ve yardım seviyesi: bir satır
- Zorunlu açık: yok veya somut küçük eksik
- Sıradaki oturum/kapsam:

Başlangıç kaydı: son eski gün 40 GEÇTİ 97; zorunlu telafi yok; V4-01 henüz açık. Yeni tarih geçti diye başarı kaydı üretme.
Final 4 sa: Python 60 dk, Linux 45, Docker 45, demo/Git-CI 30, açıklama/geri bildirim 30, hedefli yeniden kontrol 30. Yalnız öğretilen beceriler. İleri ertelenen konular veya eski güvenlik kapsamı sınava girmez.

## Kaynak seçimi

Ders için 1–2 dar resmi bölüm seç; hepsi toplu ödev değildir:
- pytest: https://docs.pytest.org/en/stable/how-to/fixtures.html ve /how-to/monkeypatch.html
- systemd: https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html
- Python generator: https://docs.python.org/3/howto/functional.html#generators
- Compose: https://docs.docker.com/compose/how-tos/startup-order/
- PostgreSQL restore: https://www.postgresql.org/docs/current/backup-dump.html
- strace: https://man7.org/linux/man-pages/man1/strace.1.html
- Docker limits: https://docs.docker.com/engine/containers/resource_constraints/
- Multi-stage: https://docs.docker.com/build/building/multi-stage/
- Thread: https://docs.python.org/3/library/concurrent.futures.html
- Profiling: https://docs.python.org/3/library/profile.html

Örnekleri kurulu sürüme göre seç; sürüm yükseltmeyi gereksiz ders yükü yapma.
