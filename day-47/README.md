# Gün 47 — V4.1-07

Son mentor onayı: 16 Eylül 2026, V4.1-07 GEÇTİ; zorunlu açık yok. Sıradaki oturum V4.1-08 (Gün 48) kaynak gözlemi / Docker limitleridir.

| Bölüm | Konu | Dizin |
| --- | --- | --- |
| Linux 1 | FD, /proc, lsof | [blok1](blok1/) |
| Linux 2 | strace: dosya erişimi / ENOENT / EACCES | [blok2](blok2/) |
| Python devamı | tmp_path normal/malformed JSONL testleri, library/CLI hata sınırı | [blok3-python](blok3-python/) |

[Linux çalışma notu](day-47-file-descriptors-proc-lsof-strace.md) 15 Eylül arşividir. Python devamı 16 Eylül'de yerel Day47 altında yapıldı; başka takvim gününde yapılması onu Gün 48'e taşımaz.

## Python devamını çalıştırma

Python ve pytest bulunan bir ortamda, repo kökünden:

```bash
cd day-47/blok3-python
python -m pytest -q
```

Testler ilgili alt proje kökünden çalıştırılır; arşivde farklı günlerin src isimlerini tek global pakette birleştirmez.

- src/records.py: gerçek JSONL okuyucusu; parse exception'ını caller'a iletir.
- tests/test_records.py: normal iki kayıt ve malformed JSON davranışı.
- test_tmp_path_demo.py: tmp_path mekanizması için küçük ders örneği.

Gün 44 başlangıç sürümü değiştirilmedi. Bu klasör aynı mekanizmanın testli refactor devamını saklar; yerel çalışma dosyaları taşınmadı. Yeni kopyalarda yalnız boşluk/satır sonları normalize edildi, Python davranışı değiştirilmedi.
