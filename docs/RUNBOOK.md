# Çalıştırma ve doğrulama

20 Eylül 2026. Komutlar repository kökünden başlar. Python 3.13+; Docker bölümü ayrıca çalışan Docker Engine/Desktop ve Compose gerektirir.

## Python

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-test.txt
(cd day-52/Final && ../../.venv/bin/python -m pytest -q test_final.py)
```

Final uygulaması standart kütüphane kullanır; pytest yalnız test bağımlılığıdır. Çıplak pytest yerine seçilen yorumlayıcıyla python -m pytest kullanılır.

Kaynak örneğini değiştirmeden gerçek CLI demosu:

```bash
demo_dir=$(mktemp -d)
cp day-52/Final/sample.jsonl "$demo_dir/input.jsonl"
.venv/bin/python day-52/Final/final.py --input "$demo_dir/input.jsonl"
.venv/bin/python day-52/Final/final.py --input "$demo_dir/input.jsonl" --output "$demo_dir/limited.csv" --format csv --max-records 2
```

İlk çıktı input.report.json; ikinci çıktı limited.csv olur. Bu komutlar geçici dizinde yeni dosya üretir; eski günlük örneklerini değiştirmez.

## Test grupları

Her grup kendi import kökünde ayrı süreç olarak çalışır. Arşivin tamamında rastgele kökten pytest çalıştırmak önerilmez: tarihsel örneklerin modül isimleri ve kurulum beklentileri farklıdır.

```bash
(cd day-42 && ../.venv/bin/python -m pytest -q Blok1/tests)
(cd day-42/Blok2 && ../../.venv/bin/python -m pytest -q tests)
(cd day-47/blok3-python && ../../.venv/bin/python -m pytest -q tests test_tmp_path_demo.py)
(cd day-51/Blok1 && ../../.venv/bin/python -m pytest -q test_day51.py)
(cd day-52/Blok1 && ../../.venv/bin/python -m pytest -q test_day52.py)
(cd day-52/Final && ../../.venv/bin/python -m pytest -q test_final.py)
```

Beklenen sayılar: 8 + 3 + 3 + 2 + 3 + 9 = **28 test**. Bunlar repository'deki her tarihsel scriptin tam test kapsamına sahip olduğu anlamına gelmez.

## Docker

Mevcut labı değiştirmeyen, DB başlatmayan temel image doğrulaması:

```bash
docker build -t coreops-review day-49/Blok2
docker run --rm coreops-review python -c 'import os, psycopg; print(os.getuid(), psycopg.__version__)'
```

UID 10001 beklenir. CI ayrıca /lab/runtime yazma ve /lab/src yazamama davranışını sınar; final Docker örneğini build edip gerçek app.py çıktısını kontrol eder.

Compose/PostgreSQL senaryosu için day-49/Blok2 içindeki compose.yaml ve gün notunu kullan. Var olan kullanıcı volume'larını veya DB'yi silme. Bu kapanış denetiminde tam DB restore ve systemd finali yeniden çalıştırılmadı.

Final Docker örneği day-52/Final/docker-kismi altında bulunur. Native Linux'ta bind mount edilen host runtime dizininin UID/GID izinleri ayrıca kontrol edilmelidir: image içindeki chown, mount edilen host dizininin sahibini değiştirmez. chmod 777 veya root'a dönmek varsayılan çözüm değildir. CI smoke testi bind mount'u değil image'ın kendi runtime dizinini kullanır.

## Bilinen sınırlar

- JSONL okuyucusu dict olmayan kayıtları, boş satırı ve bozuk JSON'u reddeder; tamamen boş dosya 0 kayıt üretir.
- Hata library katmanından iletilir; CLI'da kullanıcı dostu tek satırlık hata yönetimi henüz yok, traceback görülebilir.
- --max-records pozitif olmalıdır. Limit sonrasındaki kayıtlar tüketilmediğinden doğrulanmaz.
- Reader/islice lazy olsa da build_report kayıtları list'e toplar; bütün pipeline sabit bellekli streaming değildir.
- Mevcut ayrı output dosyası yeniden yazılır; bu bir no-clobber aracı değildir. Input ile aynı dosya (symlink/hardlink dahil) 20 Eylül korumasıyla reddedilir.
- Output parent dizini hazır olmalıdır; araç dizin oluşturmaz, atomik output garantisi de vermez.
- Docker builder'dan /usr/local bütünü kopyalanır; bu, yalnız minimum dependency veya en küçük image elde edildiği iddiası değildir.
- psycopg[binary] ve base image tag'i kilitlenmediği için byte-for-byte tekrarlanabilir build iddiası yoktur.
