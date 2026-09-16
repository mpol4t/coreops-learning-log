# Gün, oturum ve klasör eşlemesi

Kontrol tarihi: 16 Eylül 2026. Gün numarası klasör/portföy etiketidir; çalışma tarihi değildir. Bir oturum birkaç takvim gününde bitebilir. Klasör eksikliği tek başına dersin yapılmadığı anlamına gelmez.

| Gün | Eğitim oturumu | Konu | Yerel çalışma klasörü | Bu repo | Son doğrulanmış durum |
| --- | --- | --- | --- | --- | --- |
| 41 | V4-01 | PostgreSQL CLI ve tekrar kurulabilir test DB | Gelişim/Day41/day41-postgres-cli | [day-41](../day-41/) | GEÇTİ |
| 42 | V4-02 | pytest fixture, parametrize, monkeypatch | Gelişim/Day42 | [day-42](../day-42/) | GEÇTİ |
| 43 | V4-03 | systemd, journal, izin teşhisi | Gelişim/Day43 — arşiv notu | [day-43](../day-43/) | GEÇTİ; Linux unit/script dosyaları ayrıca arşivlenmiş değil |
| 44 | V4-04 | JSONL generator ve pagination | Gelişim/Day44 | [day-44](../day-44/) | GEÇTİ; tarihsel başlangıç sürümü |
| 45 | V4.1-05 | Oneshot ve timer | Gelişim/Day45 — arşiv notu | [day-45](../day-45/) | GEÇTİ; Linux unit/script dosyaları ayrıca arşivlenmiş değil |
| 46 | V4.1-06 | Volume/bind ve PostgreSQL restore | Gelişim/Day46 | [day-46/day46](../day-46/day46/) | GEÇTİ |
| 47 | V4.1-07 | FD/lsof, strace, tmp_path, library hata sınırı | Gelişim/Day47 — Python kısmı | [day-47](../day-47/) | GEÇTİ; Linux ve Python bölümleri aşağıda |
| 48 | V4.1-08 | Kaynak gözlemi ve Docker limitleri | Henüz oluşturulmamış | Henüz oluşturulmamış | Blok 1A verilmiş; tamamlanma onayı yok |

## Gün 47'nin parçaları

- [blok1](../day-47/blok1/): Linux FD / proc / lsof.
- [blok2](../day-47/blok2/): Linux strace dosya erişimi.
- [blok3-python](../day-47/blok3-python/): 16 Eylül'de tamamlanan gerçek JSONL dosyası testleri ve sys.exit yerine exception iletimi.
- [Linux notu](../day-47/day-47-file-descriptors-proc-lsof-strace.md): önceki Linux bloklarının tarihsel kaydı.
- [Genel Gün 47 kaydı](../day-47/README.md): Python devamının konumu ve test komutu.

Python devamı ertesi takvim gününde yapıldığı için Gün 48 sayılmaz. Gün 44 kodu başlangıç örneği olarak korunur; Gün 47'deki refactor onun devamıdır. Eski boş Day44 test dosyaları tamamlanmış yeni testin yok olduğu anlamına gelmez.

## İki Git deposunun farkı

Gelişim çalışma alanı ve coreops-learning-log arşivi ayrı Git depolarıdır. 16 Eylül kontrolünde çalışma alanı feature/http-client dalında ve uzak bağlantısız; bu arşiv main dalında GitHub'a bağlıdır. Otomatik senkron yoktur. Bir dosyanın çalışma alanında untracked olması GitHub arşivinde bulunmadığı anlamına gelmez.

Day40/Day44 çalışma kodu ile arşiv sürümleri farklıdır; topluca üst üste kopyalanmaz. Day40'taki yerel Compose check_owner.py referansı ayrıca onay bekleyen bir düzeltmedir; bu düzenlemede değiştirilmedi.

## Kayıt kuralı

Bir ders için yeni gün klasörü açmadan önce bu eşlemeye bak. Aynı oturumun devamı mevcut günün içinde kalır. Mentorun son oturum/blok kaydı başarı durumunu belirler; klasör adı, dosya oluşturma tarihi veya commit tarihi tek başına başarı değildir.
