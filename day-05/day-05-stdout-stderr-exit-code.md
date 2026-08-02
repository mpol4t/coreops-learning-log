---
title: "Gün 05 — stdout, stderr, Exception ve Exit Code Sözleşmesi"
tags:
  - coreops
  - python
  - linux
  - docker
  - stderr
  - exit-code
  - file-descriptor
  - exception
aliases:
  - "Gün 5 stderr Exit Code ve Docker Akışları"
status: completed
duration: "100-110 dakika"
---

# 🚦 Gün 5 — `stdout`, `stderr`, Exception ve Exit Code Sözleşmesi

> [!abstract] 🎯 Ana fikir  
> Bir programda şu üç konu birbirinden ayrılmalıdır:
> 
> 1. **Ne yazıldı?** → Mesajın içeriği
>     
> 2. **Nereye yazıldı?** → `stdout` veya `stderr`
>     
> 3. **Program nasıl tamamlandı?** → Exit code
>     
> 
> ```text
> stderr’a hata mesajı yazmak
> ≠
> programı başarısız exit code ile bitirmek
> ```

---

# ⚡ 2 Dakikalık Geri Çağırma

## `os.path.abspath()` dosyanın varlığını kanıtlar mı?

Hayır.

```python
os.path.abspath("olmayan.txt")
```

yalnızca mevcut çalışma dizinine göre mutlak bir path üretir.

```text
CWD + relative path = üretilen absolute path
```

Dosyanın gerçekten bulunup bulunmadığını kontrol etmek için:

```python
os.path.exists(path)
```

veya:

```python
os.path.isfile(path)
```

gibi ayrı kontroller gerekir.

---

# 🐍 Python — Çıktı Kanalları ve Process Sonucu

## 1. Normal `print()` nereye yazar?

```python
print("İşlem tamamlandı")
```

varsayılan olarak:

```python
import sys

print("İşlem tamamlandı", file=sys.stdout)
```

ile aynı kanala yazar.

Yani normal `print()`:

```text
stdout → standart çıktı
```

kanalını kullanır.

---

## 2. `file=sys.stderr` ne yapar?

```python
import sys

print("Dosya bulunamadı", file=sys.stderr)
```

Mesajı:

```text
stderr → standart hata/teşhis kanalı
```

üzerinden gönderir.

> [!danger] Kafaya kazı  
> `file=sys.stderr`:
> 
> ```text
> “Hata oluşursa bunu yaz.”
> ```
> 
> demek değildir.
> 
> Şu demektir:
> 
> ```text
> “Kod bu satıra ulaştığında mesajı stderr kanalına yaz.”
> ```

`stderr`:

- Hata algılamaz.
    
- Exception yakalamaz.
    
- Programı durdurmaz.
    
- Exit code’u değiştirmez.
    

---

## 3. `stderr` ve exit code bağımsızdır

```python
import sys

print("Ölümcül hata!", file=sys.stderr)
print("Program çalışmaya devam etti.")
```

Program normal tamamlanırsa:

```text
stdout    → Program çalışmaya devam etti.
stderr    → Ölümcül hata!
exit code → 0
```

Mesajın içinde `"hata"` yazması işletim sistemi için hiçbir şey ifade etmez.

Tersine:

```python
import sys

sys.exit(7)
```

şu sonucu üretebilir:

```text
stdout    → boş
stderr    → boş
exit code → 7
```

> [!important]  
> `stderr` insana açıklama verir.
> 
> Exit code shell, Docker ve otomasyon sistemlerine sonuç bildirir.

---

# 🔢 `sys.exit()`

## `sys.exit(2)`

```python
import sys

print("İşlem başladı")
sys.exit(2)
print("İşlem bitti")
```

Sonuç:

```text
stdout    → İşlem başladı
exit code → 2
```

`sys.exit(2)` sonrasındaki satır çalışmaz.

Python bunu kabaca:

```python
raise SystemExit(2)
```

şeklinde gerçekleştirir.

---

## `sys.exit("mesaj")`

```python
import sys

sys.exit("Dosya açılamadı")
```

Genellikle:

- Mesajı `stderr` kanalına yazar.
    
- Process’i exit code `1` ile bitirir.
    

```text
stderr    → Dosya açılamadı
exit code → 1
```

Bu kullanım mümkündür ancak mesaj ile kodu ayrı yönetmek daha açıktır:

```python
print("Dosya açılamadı", file=sys.stderr)
sys.exit(2)
```

---

## Fonksiyondan `return 1` dönmek

```python
def main():
    return 1


main()
```

Buradaki `1`, yalnızca fonksiyonun dönüş değeridir.

Program sonucu kullanmadan normal sona ererse shell yine:

```text
exit code 0
```

görebilir.

Fonksiyon sonucunu process exit code’una çevirmek için:

```python
import sys


def main():
    return 1


sys.exit(main())
```

kullanılır.

> [!success] Kafaya kazı
> 
> ```text
> return 1
> → Fonksiyon seviyesinde değer
> 
> sys.exit(1)
> → Process seviyesinde exit code
> 
> sys.exit(main())
> → main() dönüşünü process exit code’una dönüştürür
> ```

---

# 🧹 `finally`

`finally`, `try` bloğundan nasıl çıkılırsa çıkılsın çalıştırılması gereken bölümdür.

```python
try:
    print("İşlem başladı")
finally:
    print("Temizlik yapıldı")
```

Şu durumlarda da çalışabilir:

- Normal tamamlanma
    
- Exception
    
- `return`
    
- `sys.exit()`
    

Örnek:

```python
import sys

try:
    print("İşlem başladı")
    sys.exit(2)
finally:
    print("Temizlik yapılıyor")
```

Akış:

```text
İşlem başladı
      ↓
SystemExit(2)
      ↓
finally çalışır
      ↓
Temizlik yapılıyor
      ↓
process 2 ile biter
```

> [!tip]  
> `finally`, normal sonuç üretmekten çok:
> 
> - Dosya kapatma
>     
> - Bağlantı sonlandırma
>     
> - Geçici kaynak temizleme
>     
> 
> işleri için kullanılır.

---

# 📂 `with` ve Kaynak Temizliği

Açılan dosyanın hata olsa bile kapatılması gerekir:

```python
dosya = open("data.txt")

try:
    içerik = dosya.read()
finally:
    dosya.close()
```

Daha temiz Python kullanımı:

```python
with open("data.txt") as dosya:
    içerik = dosya.read()
```

`with` bloğu bittiğinde dosya otomatik kapatılır.

Kavramsal olarak kaynak temizliği açısından `try/finally` güvencesi sağlar.

---

# 🧺 Buffer ve `flush=True`

Çıktı her zaman anında terminale ulaşmayabilir.

```text
print()
   ↓
Python buffer’ı
   ↓
İşletim sistemi
   ↓
Terminal, dosya veya pipe
```

Buffer, çıktının geçici olarak bekletildiği alandır.

## Neden kullanılır?

Veriyi karakter karakter göndermek yerine biriktirerek toplu göndermek daha verimlidir.

---

## `flush=True`

```python
print("Başlıyor...", end="", flush=True)
```

Tamponda bekleyen çıktının hemen hedefe gönderilmesini ister.

Özellikle şu kullanımda faydalıdır:

```python
import time

print("İşlem başladı...", end="", flush=True)
time.sleep(3)
print(" bitti")
```

`flush=True` kullanılmazsa ilk mesaj bazı ortamlarda hemen görünmeyebilir.

---

## `flush=False`

Varsayılan davranıştır.

```python
print("Mesaj", flush=False)
```

Şu anlama gelmez:

```text
“Mesajı gösterme.”
```

Şu anlama gelir:

```text
“Bu print çağrısı nedeniyle buffer’ı zorla boşaltma.”
```

---

# 📁 Satır Sayma Uygulaması

## Fonksiyonun amacı

Verilen path’teki dosyayı açmak ve satır sayısını döndürmek.

Başarılı durumda:

```text
int
```

Hata durumunda:

- Mesaj `stderr` kanalına yazılır.
    
- Fonksiyon `None` döndürür.
    
- Process exit code’una çağıran bölüm karar verir.
    

---

## Temizlenmiş yapı

```python
import sys


def dosya_satır_sayısı(path):
    try:
        satır_sayısı = 0

        with open(path) as dosya:
            for satır in dosya:
                satır_sayısı += 1

        return satır_sayısı

    except IsADirectoryError as hata:
        print(
            f"Path bir dosya değil, dizin: {hata}",
            file=sys.stderr,
        )

    except FileNotFoundError as hata:
        print(
            f"Dosya bulunamadı: {hata}",
            file=sys.stderr,
        )


sonuç = dosya_satır_sayısı("data.txt")

if sonuç is None:
    sys.exit(1)

print(sonuç)
```

---

# 🔄 `for satır in dosya`

```python
for satır in dosya:
    satır_sayısı += 1
```

Dosya nesnesi üzerinde dönüldüğünde her turda bir satır alınır.

Şu kontrol gereksizdir:

```python
if satır:
    satır_sayısı += 1
```

Çünkü:

- Dosya boşsa döngü hiç çalışmaz.
    
- Boş görünen bir satır genellikle `"\n"` içerir.
    
- Döngüye girilmişse Python okunacak bir satır bulmuştur.
    

---

# 🧭 Parametreyi Gerçekten Kullanmak

TIRT kullanım:

```python
def dosya_satır_sayısı(path):
    with open("data.txt") as dosya:
        ...
```

Fonksiyon `path` almasına rağmen sabit dosya açarsa parametre anlamsızlaşır.

Doğru:

```python
def dosya_satır_sayısı(path):
    with open(path) as dosya:
        ...
```

---

# 💥 Dosya Exception’ları

|Durum|Exception|
|---|---|
|Path mevcut değil|`FileNotFoundError`|
|Path mevcut ama dizin|`IsADirectoryError`|
|Oluşturulmak istenen path zaten mevcut|`FileExistsError`|

Bir dizini dosya gibi açmak:

```python
open(".")
```

genellikle:

```text
IsADirectoryError
```

üretir.

> [!danger] TIRT varsayım  
> “Path zaten mevcut olduğu için `FileExistsError` gelir.”
> 
> Yanlış.
> 
> `FileExistsError`, genellikle zaten var olan bir şeyi yeniden oluşturmaya çalışırken ortaya çıkar.
> 
> Var olan dizini dosya olarak açmaya çalışmak ise `IsADirectoryError` üretir.

---

## `as hata`

```python
except FileNotFoundError as hata:
```

Buradaki `hata`, oluşturulan exception nesnesini tutar.

```python
print(hata)
```

exception’ın insan tarafından okunabilir mesajını gösterir.

`hata` yalnızca düz bir string değildir; exception nesnesidir.

---

# 🐍 EAFP Yaklaşımı

Dosyanın varlığını önceden sürekli kontrol etmek yerine işlemi deneyip beklenen hatayı yakalamak mümkündür:

```python
try:
    with open(path) as dosya:
        ...
except FileNotFoundError:
    ...
```

Bu yaklaşım Python’da:

```text
EAFP
Easier to Ask Forgiveness than Permission
```

olarak bilinir.

Önceden kontrol yapmak her zaman yanlış değildir ancak kontrol ile gerçek işlem arasında path’in durumu değişebilir.

---

# 🧱 Fonksiyon ve Çalıştırma Bölümü Sorumlulukları

## Fonksiyon

Fonksiyonun görevi:

- Dosyayı açmak
    
- Satırları saymak
    
- Normal sonucu döndürmek
    
- Beklenen dosya hatalarını yönetmek
    

## Çalıştırma bölümü

Çalıştırma bölümünün görevi:

- Fonksiyonu çağırmak
    
- Sonucu kontrol etmek
    
- Normal sonucu `stdout`’a yazmak
    
- Hata durumunu process exit code’una çevirmek
    

```python
sonuç = dosya_satır_sayısı(path)

if sonuç is None:
    sys.exit(1)

print(sonuç)
```

---

## Neden `is None`?

Tercih edilen:

```python
if sonuç is None:
```

Yerine genellikle kullanılmaması gereken:

```python
if sonuç == None:
```

`None`, Python’daki tekil özel bir nesnedir. `is`, nesnenin gerçekten `None` olup olmadığını kontrol eder.

---

# 🚨 Exit Code `131` Kullanımı

Kodda:

```python
sys.exit(131)
```

kullanılmıştı.

Bu teknik olarak mümkündür fakat özel bir sözleşme yoksa TIRT bir seçimdir.

Neden?

- `131` sayısının program için anlamı açıklanmıyor.
    
- Okuyan kişi neden `1`, `2` veya `3` yerine `131` kullanıldığını anlayamaz.
    
- Bazı sistemlerde yüksek exit code’lar sinyal tabanlı sonlanmalarla karıştırılabilir.
    

Örneğin Unix dünyasında:

```text
128 + sinyal numarası
```

biçimindeki kodlarla sık karşılaşılır.

`131`:

```text
128 + 3
```

olarak da yorumlanabilir.

Bu nedenle küçük ve belgelenmiş kodlar daha temizdir:

|Kod|Örnek anlam|
|--:|---|
|`0`|Başarı|
|`1`|Genel hata|
|`2`|Geçersiz kullanım|
|`3`|Dosya bulunamadı|
|`4`|Path bir dizin|

Örnek:

```python
FILE_NOT_FOUND = 3
IS_DIRECTORY = 4
```

> [!important]  
> Exit code seçimi rastgele yapılmaz.
> 
> Bir sözleşme oluşturulur ve belgelenir.

---

# 🐧 Linux — File Descriptor ve Yönlendirme

Bir process genellikle üç standart file descriptor ile başlar:

|FD|Kanal|Görevi|
|--:|---|---|
|`0`|`stdin`|Girdi|
|`1`|`stdout`|Normal çıktı|
|`2`|`stderr`|Hata ve teşhis çıktısı|

Başlangıçta:

```text
FD 0 → terminal
FD 1 → terminal
FD 2 → terminal
```

`stdout` ve `stderr` aynı terminalde görünse bile ayrı kanallardır.

---

# ➡️ `>` Yönlendirmesi

```bash
python3 day05.py > stdout.txt
```

`>` varsayılan olarak:

```bash
1>
```

anlamına gelir.

Yani:

```bash
python3 day05.py 1> stdout.txt
```

ile aynıdır.

Sonuç:

```text
FD 1 → stdout.txt
FD 2 → terminal
```

`stderr` varsayılan olarak yönlendirilmez çünkü `>` yalnızca FD `1`i hedefler.

---

# ❗ `2>`

```bash
python3 day05.py 2> stderr.txt
```

Buradaki `2`, `stderr` file descriptor’ını temsil eder.

Sonuç:

```text
FD 1 → terminal
FD 2 → stderr.txt
```

---

# 📂 İki Kanalı Ayrı Dosyalara Yazmak

```bash
python3 day05.py data.txt \
  > stdout.txt \
  2> stderr.txt
```

Başarılı senaryo:

```text
stdout.txt → satır sayısı
stderr.txt → boş
exit code  → 0
```

Hata senaryosu:

```text
stdout.txt → boş
stderr.txt → hata açıklaması
exit code  → sıfır dışı
```

---

# 🔗 `2>&1`

```bash
python3 day05.py > all.txt 2>&1
```

İşlem sırası:

```text
1. FD 1 → all.txt
2. FD 2 → FD 1’in mevcut hedefi
3. FD 2 → all.txt
```

Böylece hem `stdout` hem `stderr` aynı dosyaya gider.

> [!warning]  
> `2>&1`, stderr metnini stdout verisine dönüştürmez.
> 
> Yalnızca iki descriptor’ın hedefini aynı yapar.

---

# 🔄 Yönlendirme Sırası Önemlidir

## İkisi de dosyaya

```bash
komut > output.txt 2>&1
```

Son durum:

```text
stdout → output.txt
stderr → output.txt
```

## Yalnız stdout dosyaya

```bash
komut 2>&1 > output.txt
```

İşlem:

```text
1. stderr → stdout’un o anki hedefi → terminal
2. stdout → output.txt
```

Son durum:

```text
stdout → output.txt
stderr → terminal
```

> [!danger] Kafaya kazı  
> Shell yönlendirmeleri soldan sağa uygular.

---

# 🧪 Gerçek Yönlendirme Deneyleri

## Başarılı dosya

```bash
python3 day05.py data.txt \
  > stdout.txt \
  2> stderr.txt

echo $?
```

Sonuç:

```text
exit code: 0
stdout.txt: 2
stderr.txt: boş
```

---

## Olmayan dosya

```bash
python3 day05.py day06.txt \
  > stdout.txt \
  2> stderr.txt

echo $?
```

Sonuç:

```text
exit code: sıfır dışı
stdout.txt: boş
stderr.txt: Dosya bulunamadı...
```

---

## İki kanalı aynı dosyada toplamak

```bash
python3 day05.py \
  > all.txt \
  2>&1
```

Hata mesajı artık `all.txt` içinde görünür.

Eski `stderr.txt` dosyasının boş olması normaldir çünkü bu komutta FD `2`, `stderr.txt` dosyasına yönlendirilmemiştir.

---

# 🚦 Yönlendirme Exit Code’u Değiştirir mi?

Hayır.

```bash
python3 day05.py olmayan.txt > out.txt 2> err.txt
echo $?
```

Program dosyaları farklı hedeflere yazsa da exit code programın sonucudur.

Yönlendirme yalnızca:

```text
“Çıktı nereye gidecek?”
```

sorusunu değiştirir.

---

# 🐳 Docker — Exit Code ve Akışlar

## Foreground çalışma

```bash
docker run --rm alpine sh -c 'exit 7'
echo $?
```

Shell:

```text
7
```

görür.

Akış:

```text
Container ana process’i 7 ile biter
           ↓
Docker sonucu alır
           ↓
docker run shell’e 7 döndürür
```

---

## Exit Code’u Hemen Saklamak

```bash
docker run --rm alpine sh -c 'exit 7'
kod=$?

echo "$kod"
```

Araya başka komut girerse `$?` değişir:

```bash
docker run --rm alpine sh -c 'exit 7'
echo "Container bitti"
echo $?
```

Son `echo $?`, `docker run` yerine önceki `echo` komutunun sonucunu gösterir.

---

# 🌙 Detached Mod

```bash
docker run -d alpine sh -c 'sleep 2; exit 7'
```

Shell, container’ın daha sonra üreteceği `7` kodunu beklemez.

Gerçek sonucu almak için:

```bash
cid=$(docker run -d alpine sh -c 'sleep 2; exit 7')
kod=$(docker wait "$cid")

echo "$kod"

docker rm "$cid"
```

`docker wait`, container’ın durmasını bekler ve exit code’unu çıktı olarak verir.

---

# 🗑️ `--rm` ve Exit Code

```bash
docker run --rm alpine sh -c 'exit 7'
kod=$?
```

`--rm`, exit code’un shell’e ulaşmasını engellemez.

Sıralama:

```text
1. Container process’i biter.
2. Docker exit code’u öğrenir.
3. Container nesnesi silinir.
4. Exit code shell’e döndürülür.
```

Ancak container silindiği için sonradan:

```bash
docker inspect CONTAINER
```

çalışmaz.

---

# 🚨 Docker’ın Özel Kodları

|Kod|Docker sözleşmesindeki anlam|
|--:|---|
|`125`|Docker container’ı çalıştıramadı|
|`126`|Komut bulundu fakat çalıştırılamadı|
|`127`|Çalıştırılmak istenen komut bulunamadı|

## `127` örneği

```bash
docker run --rm busybox kesinlikle_böyle_bir_şey_yok
echo $?
```

Container içinde çalıştırılmak istenen executable bulunmadığı için:

```text
127
```

döner.

---

## Yanlış image adı hangi kodu üretir?

> [!danger] TIRT ustalık cevabı  
> “Image adı yanlışsa Docker komutu bulamaz ve `127` döndürür.”
> 
> Yanlış.

`127`, genellikle container içinde çalıştırılacak komutun bulunamamasıyla ilgilidir.

Image adı yanlışsa Docker:

- Image’ı registry’de bulamayabilir.
    
- Image’ı çekemeyebilir.
    
- Container’ı başlatamayabilir.
    

Bu durum Docker çalıştırma katmanına aittir ve çoğunlukla:

```text
125
```

gibi bir Docker hatası üretir.

Örneğin:

```bash
docker run kesinlikle-olmayan-image
```

Python programı hiç başlamayabilir.

Dolayısıyla shell’de görülen kod Python’a değil Docker katmanına aittir.

---

# ⚠️ `125–127` Kodlarında Bağlam

Uygulamanın kendisi de bilinçli olarak:

```bash
exit 127
```

diyebilir.

Bu yüzden yalnızca sayıya bakarak kesin teşhis yapılmaz.

Kontrol edilecekler:

```bash
docker ps -a
docker logs CONTAINER
docker inspect CONTAINER
```

Özellikle:

```bash
docker inspect \
  --format '{{json .State}}' \
  CONTAINER
```

Sorulacak sorular:

- Container oluşturuldu mu?
    
- Ana process başladı mı?
    
- Uygulamanın başlangıç logları var mı?
    
- Docker’ın kendi hata mesajı var mı?
    
- `.State.Error` alanı dolu mu?
    
- Uygulama kodu bilinçli olarak bu değeri döndürmüş olabilir mi?
    

---

# 📡 Container Akışları Terminale Nasıl Ulaşır?

Foreground çalışan `docker run`, container’ın standart akışlarına bağlanır.

```text
Container process
├── stdout
└── stderr
      ↓
Docker runtime
      ↓
Docker CLI
      ↓
Shell / terminal
```

Örnek:

```bash
docker run --rm python:3.12-slim \
  python -c "
import sys
print('normal çıktı')
print('hata mesajı', file=sys.stderr)
"
```

Normal mesaj `stdout`, hata mesajı `stderr` üzerinden terminale ulaşır.

---

# 📜 `docker logs`

`docker logs`, container ana process’inin `stdout` ve `stderr` çıktılarını gösterir.

```bash
docker logs CONTAINER
docker logs -f CONTAINER
docker logs --tail 20 CONTAINER
```

Ancak uygulama yalnızca container içindeki bir dosyaya yazarsa bu çıktı `docker logs` içinde görünmeyebilir.

Container uygulamalarında gözlemlenebilirlik için:

```python
print("Normal bilgi")
print("Hata bilgisi", file=sys.stderr)
```

kullanmak genellikle daha uygundur.

---

# 🖥️ Pseudo-Terminal — PTY

## Terminal, shell ve process

```text
Terminal uygulaması → Görsel arayüz
PTY                 → Sanal terminal bağlantısı
Shell               → Komut yorumlayıcısı
Process             → Çalıştırılan uygulama
```

Bunlar aynı şey değildir.

---

## PTY nedir?

Pseudo-terminal, fiziksel terminal davranışını yazılımla taklit eden işletim sistemi mekanizmasıdır.

Şunları sağlar:

- İnteraktif prompt
    
- Backspace ve ok tuşları
    
- Terminal boyutu
    
- Renkli çıktı
    
- Parola girişinde gizleme
    
- `Ctrl+C`
    
- `vim`, `nano`, `top` gibi uygulamalar
    

---

# 🔌 Pipe ve PTY Farkı

## Pipe

```text
Program A → Ham veri → Program B
```

Örnek:

```bash
echo "merhaba" | python3 program.py
```

Burada programın stdin’i terminal değil pipe’dır.

## PTY

```text
Kullanıcı ↔ Sanal terminal ↔ Program
```

PTY yalnız veri taşımaz; terminal davranışı da sağlar.

```text
Pipe → Ham veri borusu
PTY  → Sanal terminal ortamı
```

---

# 🎮 Docker `-i`, `-t` ve `-it`

|Seçenek|Görevi|
|---|---|
|`-i`|stdin’i açık tutar|
|`-t`|Pseudo-terminal oluşturur|
|`-it`|İkisini birlikte sağlar|

İnteraktif shell:

```bash
docker run -it alpine sh
```

> [!warning]  
> `-i` ve `-t` aynı şey değildir.
> 
> ```text
> -i → Girdi kanalı açık
> -t → Terminal ortamı var
> ```

---

## Otomasyonda `-t`

İnsanla etkileşim için faydalıdır.

Ancak:

- CI
    
- Script
    
- Çıktı ayrıştırma
    
- `stdout`–`stderr` ayırma
    

işlerinde gereksiz `-t` kullanmak TIRT olabilir.

PTY iki akışı tek terminal ekranına bağlayarak ayrımı bozabilir.

---

# 🔗 Host ve Docker Entegrasyonu

## Host

```bash
python3 day05.py data.txt \
  > host-out.txt \
  2> host-err.txt

echo $?
```

Başarılı durumda:

```text
host-out.txt → satır sayısı
host-err.txt → boş
exit code    → 0
```

---

## Docker

Script komut satırı argümanı bekliyorsa argüman container komutuna da verilmelidir:

```bash
docker run --rm \
  -v "$PWD":/app:ro \
  -w /app \
  python:3.12-slim \
  python day05.py data.txt \
  > container-out.txt \
  2> container-err.txt
```

> [!warning] Sinsi tutarsızlık  
> Host çalıştırmasında:
> 
> ```bash
> python3 day05.py data.txt
> ```
> 
> kullanıp Docker çalıştırmasında:
> 
> ```bash
> python day05.py
> ```
> 
> kullanmak aynı testi yapmak değildir.
> 
> Program argüman bekliyorsa iki ortamda da aynı argüman verilmelidir.

---

## Çıktıları karşılaştırmak

```bash
diff host-out.txt container-out.txt
diff host-err.txt container-err.txt
```

Aynı test girdileriyle aynı çıktıların üretilmesi beklenir.

Exit code’lar ayrıca kaydedilmelidir:

```bash
python3 day05.py data.txt > host-out.txt 2> host-err.txt
host_code=$?

docker run --rm \
  -v "$PWD":/app:ro \
  -w /app \
  python:3.12-slim \
  python day05.py data.txt \
  > container-out.txt \
  2> container-err.txt
container_code=$?

echo "Host: $host_code"
echo "Container: $container_code"
```

---

# 🧯 Hata Avı

## 1. Hata mesajı yazıldıysa program başarısızdır

TIRT.

Başarı durumunu belirleyen asıl sinyal exit code’dur.

---

## 2. Fonksiyon `return 1` döndürürse process `1` olur

TIRT.

Dönen değerin `sys.exit()` ile process seviyesine taşınması gerekir.

---

## 3. `sys.exit(131)` iyi bir hata kodudur

Sözleşme yoksa TIRT.

Exit code küçük, anlamlı ve belgelenmiş olmalıdır.

---

## 4. Dizin verildiğinde `FileExistsError` oluşur

TIRT.

Bir dizini dosya gibi açmak genellikle `IsADirectoryError` üretir.

---

## 5. `2>&1` stderr’i stdout verisine çevirir

TIRT.

Yalnızca iki FD’nin hedefini aynı yapar.

---

## 6. Yönlendirme exit code’u değiştirir

TIRT.

Yönlendirme çıktı hedeflerini değiştirir, programın başarı sonucunu değil.

---

## 7. Yanlış Docker image adı `127` üretir

TIRT.

Yanlış veya çekilemeyen image Docker çalıştırma katmanında problem oluşturur ve çoğunlukla `125` sınıfında değerlendirilir.

`127`, container içinde çalıştırılmak istenen komut bulunamadığında görülür.

---

# 🧠 Kafaya Kazı

> [!quote]  
> `stdout` normal sonuç, `stderr` hata ve teşhis mesajı kanalıdır.

> [!quote]  
> Mesajın kanalı ile process exit code’u birbirinden bağımsızdır.

> [!quote]  
> `return`, fonksiyondan; `sys.exit()`, process’ten çıkar.

> [!quote]  
> `sys.exit(main())`, fonksiyon sonucunu process exit code’una taşır.

> [!quote]  
> `finally`, çıkış yolu ne olursa olsun temizlik için çalışabilir.

> [!quote]  
> `>` aslında `1>` anlamına gelir.

> [!quote]  
> `2>` yalnızca `stderr` kanalını yönlendirir.

> [!quote]  
> `2>&1`, FD 2’yi FD 1’in o anki hedefine bağlar.

> [!quote]  
> Shell yönlendirmeleri soldan sağa uygular.

> [!quote]  
> Docker foreground çalışmada container exit code’unu shell’e taşır.

> [!quote]  
> Yanlış image ile container içindeki yanlış komut aynı hata değildir.

> [!quote]  
> `-i` stdin’i açık tutar, `-t` PTY oluşturur.

---

# 📌 30 Saniyelik Özet

```text
PYTHON
print()                  → stdout
print(..., file=stderr)  → stderr
return 1                 → fonksiyon değeri
sys.exit(1)              → process exit code
sys.exit(main())         → return değerini exit code yap
finally                  → kesin temizlik
flush=True               → buffer’ı hemen boşalt

DOSYA
FileNotFoundError        → path yok
IsADirectoryError        → path dizin
for satır in dosya       → satır say
is None                  → None kontrolü

LINUX
0                        → stdin
1                        → stdout
2                        → stderr
>                        → 1>
2>                       → stderr yönlendirme
2>&1                     → stderr’i stdout hedefine bağla
yönlendirme              → exit code’u değiştirmez

DOCKER
foreground               → process kodunu shell’e taşır
--rm                     → container kaydını siler
125                      → Docker çalıştıramadı
126                      → komut var, çalıştırılamadı
127                      → komut bulunamadı
-i                       → stdin açık
-t                       → PTY
-it                      → interaktif terminal
```

---

# ✅ Günün Kazanımları

-  `stdout` ve `stderr` ayrıldı
    
-  `file=sys.stderr` davranışı anlaşıldı
    
-  Fonksiyon dönüşü ile process exit code’u ayrıldı
    
-  `sys.exit(main())` modeli kavrandı
    
-  `finally` ve kaynak temizliği öğrenildi
    
-  Buffer ve `flush=True` anlaşıldı
    
-  Dosya satırları doğru şekilde sayıldı
    
-  `FileNotFoundError` ve `IsADirectoryError` ayrıldı
    
-  `as hata` ile exception nesnesi kullanıldı
    
-  Fonksiyon ve çalıştırma bölümü sorumlulukları ayrıldı
    
-  `>`, `2>` ve `2>&1` uygulandı
    
-  Yönlendirme sırasının önemi görüldü
    
-  Docker foreground exit code davranışı test edildi
    
-  Docker `125`, `126` ve `127` kodları ayrıldı
    
-  Yanlış image ile yanlış container komutu ayrıldı
    
-  `--rm` sonrası exit code’un korunabildiği görüldü
    
-  Pipe ve pseudo-terminal ayrıldı
    
-  `-i`, `-t` ve `-it` seçenekleri öğrenildi
    

> [!success] 🚀 Gün sonu sonucu  
> Gün 5 sonunda bir programın yalnızca doğru mesajı yazmasının yeterli olmadığı öğrenildi.
> 
> Sağlam bir komut satırı programı:
> 
> - Normal sonucu `stdout`’a,
>     
> - Hata açıklamasını `stderr`’a,
>     
> - Başarı veya başarısızlık bilgisini exit code’a
>     
> 
> doğru ve tutarlı biçimde yerleştirmelidir.