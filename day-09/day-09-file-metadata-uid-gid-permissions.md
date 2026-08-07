---
title: "Gün 09 — Dosya Metadata, UID/GID, st_mode ve Docker Kimlik Farkı"
tags:
  - coreops
  - python
  - linux
  - docker
  - metadata
  - uid
  - gid
  - permissions
  - stat
  - bind-mount
aliases:
  - "Gün 9 Dosya Metadata UID GID ve İzin Kontrolü"
status: completed
duration_minutes: 100
---

# 🧠 Gün 9 — Dosya Metadata, UID/GID, `st_mode` ve Docker Kimlik Farkı

> [!abstract] 🎯 Ana fikir  
> Bir dosyaya erişimin mümkün olup olmadığını anlamak için yalnızca:
> 
> ```text
> rwx izinlerine
> ```
> 
> bakmak yeterli değildir.
> 
> Aynı zamanda:
> 
> ```text
> Dosyanın UID/GID bilgisi
> +
> Process’in UID/GID ve grup üyelikleri
> +
> Mode bitleri
> ```
> 
> birlikte değerlendirilmelidir.
> 
> Bind mount tarafında ise önemli ayrım:
> 
> ```text
> Mount → Dosya nerede görünecek?
> --user → Process hangi UID/GID ile çalışacak?
> ```

---

# ⚡ 2 Dakikalık Geri Çağırma

## `st_uid` ve `st_gid` neyi temsil eder?

```python
bilgi = os.stat("data.txt")
```

sonrasında:

```python
bilgi.st_uid
```

dosyanın **sahip kullanıcısının sayısal UID değerini** verir.

```python
bilgi.st_gid
```

ise dosyaya atanmış **sahip grubun sayısal GID değerini** verir.

> [!warning]  
> `st_gid`, kullanıcının üyesi olduğu bütün gruplar değildir.
> 
> Yalnızca dosyanın sahip grubudur.

---

## `st_mode` neden yalnızca `755` değildir?

Çünkü `st_mode` içerisinde yalnızca:

```text
rwx rwx rwx
```

bitleri bulunmaz.

Aynı zamanda:

- Dosya türü
    
- Owner/group/others izinleri
    
- `setuid`
    
- `setgid`
    
- Sticky bit
    

gibi bilgiler de bulunabilir.

Yalnızca izin kısmını almak için:

```python
mode = stat.S_IMODE(bilgi.st_mode)
```

kullanılır.

---

## Olmayan path için `os.stat()` ne üretir?

```python
os.stat("olmayan.txt")
```

genellikle:

```text
FileNotFoundError
```

üretir.

Bu hata:

```text
OSError
└── FileNotFoundError
```

ailesindedir.

---

# 🐍 Python — `open()` ile `os.stat()` Farkı

## `open()`

Dosyanın içeriğiyle çalışmak için kullanılır:

```python
with open("data.txt") as dosya:
    veri = dosya.read()
```

## `os.stat()`

Dosyanın metadata bilgilerini getirir:

```python
import os

bilgi = os.stat("data.txt")
```

Metadata örnekleri:

- UID
    
- GID
    
- Mode
    
- Boyut
    
- Modification time
    

> [!important]  
> Yalnızca dosyanın sahibi veya izinleri öğrenilecekse dosyayı `open()` ile açmaya gerek yoktur.

---

# 📦 Önemli `os.stat()` Alanları

|Alan|Anlamı|
|---|---|
|`st_uid`|Dosya owner UID|
|`st_gid`|Dosya sahip grubunun GID’si|
|`st_mode`|Dosya türü + izin/özel bitler|
|`st_size`|Byte cinsinden boyut|
|`st_mtime`|Son içerik değiştirme zamanı|

---

# 🔐 Yalnızca İzin Bitlerini Almak

```python
import os
import stat

bilgi = os.stat("data.txt")

mode = stat.S_IMODE(bilgi.st_mode)
```

Buradaki `mode`, yalnızca permission bitlerini içerir.

---

## 🚨 Neden ekranda `420` gördüm?

Kod:

```python
print(mode)
```

yapıldığında Python integer’ı **decimal** olarak yazdırır.

`0644` izinlerinin sayısal değeri:

```text
Octal   → 644
Decimal → 420
```

Yani:

```python
mode == 420
```

görmek izinlerin `420` olduğu anlamına gelmez.

İzin gösterimi için:

```python
print(oct(mode))
```

çıktısı:

```text
0o644
```

olur.

Daha okunabilir gösterim:

```python
print(stat.filemode(bilgi.st_mode))
```

çıktısı:

```text
-rw-r--r--
```

> [!danger] Kafaya kazı
> 
> ```text
> 420 decimal
> =
> 0o644 octal
> =
> rw-r--r--
> ```

---

# 🧱 Günün Python Fonksiyonu

Kaynak kod:

```python
import os
import sys
import stat


def izin_okuma(dosya):
    bilgi = os.stat(dosya)

    uid = bilgi.st_uid
    gid = bilgi.st_gid
    mode = stat.S_IMODE(bilgi.st_mode)

    return uid, gid, mode
```

Fonksiyon:

```text
Dosya içeriğini okumaz.
Metadata bilgisini alır.
UID/GID/mode döndürür.
```

---

# 🔁 Birden Fazla Dosyayı İşlemek

```python
for dosya in ["data.txt", "asd.txt"]:
    try:
        uid, gid, mode = izin_okuma(dosya)

        print(f"UID: {uid}")
        print(f"GID: {gid}")
        print(f"Mode: {oct(mode)}")

    except FileNotFoundError as hata:
        print(
            f"{dosya} okunamadı: {hata}",
            file=sys.stderr,
        )
```

Burada `try` döngünün **içinde** bulunur.

Bu önemli.

---

# 🧯 `try/except` Nereye Konmalı?

## TIRT tasarım

```python
try:
    for dosya in dosyalar:
        bilgi = os.stat(dosya)
except FileNotFoundError:
    ...
```

İkinci dosya hata verirse:

```text
Döngü sona erer.
Sonraki dosyalar işlenmez.
```

## Daha uygun tasarım

```python
for dosya in dosyalar:
    try:
        bilgi = os.stat(dosya)
    except FileNotFoundError:
        print(f"{dosya} bulunamadı.")
        continue
```

Böylece:

```text
Dosya 1 → İşlenir
Dosya 2 → Hata
Dosya 3 → Yine işlenir
```

> [!important]  
> `try`, körü körüne tek satırı değil, hata durumunda birlikte yönetilmesi gereken **en küçük anlamlı işlem grubunu** sarmalıdır.

---

# 🧮 İzin Bitlerini Kontrol Etmek

Permission bitleri bitmask olarak tutulur.

Bu nedenle:

```python
and
```

değil:

```python
&
```

yani **bitwise AND** kullanılır.

Örnek:

```python
if mode & stat.S_IRUSR:
    print("Owner okuyabilir.")
```

Burada:

```text
Sonuç = 0
→ İlgili izin biti kapalı

Sonuç ≠ 0
→ İlgili izin biti açık
```

---

# 🔑 `stat` İzin Sabitleri

|Sabit|Anlamı|
|---|---|
|`S_IRUSR`|Owner read|
|`S_IWUSR`|Owner write|
|`S_IXUSR`|Owner execute|
|`S_IRGRP`|Group read|
|`S_IWGRP`|Group write|
|`S_IXGRP`|Group execute|
|`S_IROTH`|Others read|
|`S_IWOTH`|Others write|
|`S_IXOTH`|Others execute|

Örneğin group veya others yazabiliyor mu?

```python
baskalari_yazabilir = bool(
    mode & (stat.S_IWGRP | stat.S_IWOTH)
)
```

Burada:

```text
| → Kontrol edeceğimiz bitleri birleştirir.
& → Bu bitlerden mode içinde bulunan var mı kontrol eder.
```

---

# 🔄 `chmod`, UID ve GID Değişiklikleri

## Yalnızca `chmod`

```text
st_uid  → Aynı kalır
st_gid  → Aynı kalır
st_mode → Değişir
```

## Owner değiştirilirse

```text
st_uid → Değişir
```

## Sahip grup değiştirilirse

```text
st_gid → Değişir
```

## İkisi birlikte değiştirilirse

```text
st_uid → Değişir
st_gid → Değişir
```

> [!note]  
> Bazı sistemlerde ownership değişiklikleri sırasında güvenlik nedeniyle `setuid` / `setgid` bitleri temizlenebilir. Böyle bir durumda mode da değişebilir.

---

# 🐧 Linux — UID/GID ve İzin Sınıfı Seçimi

Dosya:

```text
-rwxr-x---
```

üç permission sınıfına ayrılır:

```text
rwx | r-x | ---
 u     g     o
```

Linux üçünü toplamaz.

Yalnızca **bir tanesini seçer**.

---

# 🔐 Hangi İzin Üçlüsü Kullanılır?

Mantık kabaca:

```text
1. Process dosyanın owner'ı mı?
   ↓
   Evet → owner izinleri

2. Değilse dosyanın grubuna üye mi?
   ↓
   Evet → group izinleri

3. Hiçbiri değil
   ↓
   others izinleri
```

Teknik olarak Linux dosya sistemi erişiminde FSUID/FSGID ve supplementary groups dikkate alınır.

---

## Owner, group ve others birleşmez

Dosya:

```text
owner  → ---
group  → rwx
others → rwx
```

Process dosyanın owner’ıysa:

```text
owner → ---
```

kullanılır.

Linux:

```text
“Owner izni yok, bari group iznine bakayım.”
```

demez.

> [!danger]  
> İlk eşleşen sınıf seçildikten sonra yalnızca o izin üçlüsü değerlendirilir.

---

# 🆔 UID ile Kullanıcı Adı Aynı Şey Değildir

```text
UID 501
```

ile:

```text
polat
```

aynı kavram değildir.

```text
UID
→ Sistem tarafından kullanılan sayısal kimlik

Kullanıcı adı
→ İnsan tarafından okunabilir isim
```

Dosyanın metadata’sında esas olarak sayısal:

```text
UID
GID
```

bilgileri tutulur.

---

# 🔍 `ls -l`, `ls -ln` ve `stat`

## `ls -l`

```bash
ls -l day09.py
```

örnek:

```text
-rw-r--r-- 1 polat staff 658 day09.py
```

İnsan tarafından okunabilir kullanıcı/grup isimleri gösterilir.

## `ls -ln`

```bash
ls -ln day09.py
```

sayısal UID/GID gösterir.

## `stat`

```bash
stat day09.py
```

dosyanın ayrıntılı metadata bilgisini gösterir.

> [!important]
> 
> ```text
> id    → Process kimliği
> stat  → Dosya kimliği ve metadata
> ls -l → Metadata’nın okunabilir özeti
> ```

---

# 👥 Primary ve Supplementary Groups

Örnek:

```text
uid=1000(polat)
gid=1000(polat)
groups=1000(polat),27(sudo),998(docker)
```

Burada:

```text
Primary group      → 1000(polat)
Supplementary      → sudo, docker
```

Dosya erişiminde yalnız primary grup değerlendirilmez.

Process’in supplementary grupları da dosyanın GID’siyle eşleşebilir.

---

# 🧠 RUID, EUID ve FSUID

## RUID

```text
Real User ID
```

Process’i gerçekte hangi kullanıcının başlattığını gösterir.

## EUID

```text
Effective User ID
```

Process’in etkin yetki kimliğidir.

## FSUID

```text
Filesystem User ID
```

Linux kernel’in dosya sistemi izin kontrollerinde kullandığı kullanıcı kimliğidir.

Normal kullanımda çoğunlukla:

```text
RUID = EUID = FSUID
```

olur.

Ama `setuid` gibi özel senaryolarda farklı olabilir.

---

> [!tip]  
> Günlük öğrenmede:
> 
> ```text
> EUID ile düşünmek
> ```
> 
> genellikle yeterlidir.
> 
> Teknik olarak Linux dosya izin kontrolündeki owner karşılaştırmasında FSUID önemlidir.

---

# 🧩 Örnek Erişim Kararı

Dosya:

```text
UID  = 1000
GID  = 2000
MODE = 640
```

Mode:

```text
owner  → rw-
group  → r--
others → ---
```

## Process

```text
UID = 3000
Groups = [2000, 4000]
```

Owner eşleşmesi:

```text
3000 != 1000
```

başarısız.

Grup eşleşmesi:

```text
2000 ∈ process groups
```

başarılı.

Dolayısıyla yalnızca:

```text
group → r--
```

uygulanır.

Process:

```text
Okuyabilir ✅
Yazamaz ❌
```

---

# 🚨 Neden Yalnız `755` Bilmek Yetmez?

Şu bilgi:

```text
mode = 755
```

şunu gösterir:

```text
owner  → rwx
group  → r-x
others → r-x
```

Ama process’in hangi üçlüye düşeceğini henüz bilmiyoruz.

Bunun için:

```text
Process UID/GID/groups
+
Dosyanın UID/GID
```

bilgisi gerekir.

> [!danger]  
> “Dosya 755, erişim belli.”
> 
> TIRT.
> 
> Önce process’in owner mı, group mu, others mı olduğuna karar verilmelidir.

---

# 🐳 Docker — Aynı Dosya, Farklı Process Kimliği

Docker deneyindeki ana ayrım:

|Mekanizma|Cevapladığı soru|
|---|---|
|Bind mount|Dosya container içinde nerede?|
|`--user`|Process hangi UID/GID ile çalışıyor?|
|`-i/-t`|Terminal bağlantısı nasıl?|

> [!important]  
> Mount dosyanın konumunu, `--user` process’in kimliğini belirler.

---

# 📂 Bind Mount Dosyayı Değiştirir mi?

Hayır.

```bash
--mount type=bind,source="$PWD",target=/app
```

hosttaki dosyanın yeni bir kopyasını oluşturmaz.

Host:

```text
/proje/day09.py
```

Container:

```text
/app/day09.py
```

aynı bind mount edilmiş veriyi temsil eder.

Sırf mount işlemi yapıldı diye:

- İçerik değişmez.
    
- Permission bitleri otomatik değişmez.
    
- Ownership’in değiştirilmesi gerekmez.
    

Ancak container içindeki yetkili process:

```bash
chmod
chown
rm
write
```

gibi işlemler yaparsa host dosyası etkilenebilir.

---

# 🆔 Host ve Container `id` Çıktısı

Host:

```bash
id
```

çıktısı:

```text
uid=501(polat)
gid=20(staff)
```

Container:

```bash
docker run --rm python:3.12-slim id
```

çıktısı:

```text
uid=0(root)
gid=0(root)
```

olabilir.

Bu, dosyanın değiştiği anlamına gelmez.

> [!success]
> 
> ```text
> Değişen dosyanın kimliği değil,
> dosyaya bakan process'in kimliğidir.
> ```

---

# ⚠️ Docker Desktop / macOS Sahiplik Detayı

Deneyde host:

```text
UID = 501
GID = 20
```

gösterirken container içindeki `stat`:

```text
UID = 0
GID = 0
```

gösterdi.

Bu gözlem gerçek ve önemli.

Ancak buradan:

```text
“Bind mount her sistemde UID/GID’yi 0:0 yapar.”
```

sonucu çıkarılmaz.

> [!note] Ek teknik not  
> macOS üzerindeki Docker Desktop, Linux container’ları bir sanallaştırma/filesystem paylaşım katmanı üzerinden çalıştırır.
> 
> Bu nedenle container içinde görülen sayısal sahiplik host macOS’taki UID/GID ile birebir görünmeyebilir.
> 
> Native Linux bind mount davranışında sayısal UID/GID görünümü farklı olabilir.

Dolayısıyla:

```text
Host stat sonucu
≠
Container stat sonucu
```

olması, dosyanın otomatik olarak yeniden sahiplenildiğini kanıtlamaz.

---

# 🔐 Sayısal UID/GID Neden Önemli?

Linux erişim kontrolü kullanıcı adının metnine bakmaz.

Örneğin:

```text
-rw------- 1 501 20 veri.txt
```

dosyasında yalnız UID `501` owner izinlerine sahiptir.

Container process’i:

```text
UID = 1000
```

ile çalışıyorsa dosyayı mount sayesinde görebilir.

Fakat bu:

```text
Dosyayı okuyabileceği
```

anlamına gelmez.

> [!danger]  
> Dosyayı görmek ≠ Dosyaya erişebilmek.

---

# 👤 Docker `--user`

```bash
docker run --user UID:GID IMAGE
```

Container process’ini belirtilen sayısal kimlikle başlatır.

Host UID/GID’sini geçirmek:

```bash
docker run --rm \
  --user "$(id -u):$(id -g)" \
  --mount type=bind,source="$PWD",target=/app \
  -w /app \
  python:3.12-slim \
  id
```

Shell önce:

```bash
$(id -u)
```

ve:

```bash
$(id -g)
```

ifadelerini çözer.

Örneğin:

```text
501:20
```

Docker’a gönderilir.

---

# ❌ `--user` Ne Yapmaz?

`--user`:

- Dosyayı mount etmez.
    
- Dosyanın sahibini değiştirmez.
    
- `chmod` yapmaz.
    
- `chown` yapmaz.
    
- Yeni kullanıcı oluşturmaz.
    
- Otomatik sınırsız yetki sağlamaz.
    

Yalnızca:

```text
Container process hangi UID/GID ile başlasın?
```

sorusunu cevaplar.

---

# 🆚 `--user` ve Mount

## Mount

```bash
-v "$PWD":/app
```

sorusu:

```text
Dosya nerede görünecek?
```

## `--user`

```bash
--user 501:20
```

sorusu:

```text
Dosyaya erişmeye çalışan process kim?
```

Bunlar aynı problemi çözmez.

---

# 🧪 Günün Docker Deneyi

Container:

```bash
docker run --rm -it \
  --mount type=bind,source="$PWD",target=/app \
  -w /app \
  python:3.12-slim \
  sh
```

Container içinde:

```bash
id
```

çıktısı:

```text
uid=0(root) gid=0(root)
```

Ardından:

```bash
stat day09.py
```

çıktısında:

```text
Access: (0644/-rw-r--r--)
Uid: 0/root
Gid: 0/root
```

görüldü.

Hostta:

```bash
id
```

çıktısı:

```text
uid=501(polat)
gid=20(staff)
```

Host `stat` ise dosyayı:

```text
polat staff
```

olarak gösterdi.

> [!success] Çıkarım  
> Host ve container process kimlikleri aynı olmak zorunda değildir.
> 
> Bind mount edilmiş dosya da iki ortamda farklı sahiplik gösterimiyle sunulabilir.

---

# 🔗 Entegrasyon — Host ve Container

Host:

```bash
python3 day09.py
```

çıktısı:

```text
UID: 501
GID: 20
Mode: 420
```

Container:

```bash
docker run --rm \
  --mount type=bind,source="$PWD",target=/app \
  -w /app \
  python:3.12-slim \
  python day09.py
```

çıktısı:

```text
UID: 0
GID: 0
Mode: 420
```

Kaynak deneyde bu sonuç açıkça gözlemlendi.

---

## Burada ne değişti?

Gözlem:

```text
Host UID/GID       → 501:20
Container UID/GID  → 0:0

Mode decimal       → 420
Mode octal         → 0644
```

Mode izinleri aynı görünürken sahiplik gösterimi değişmiştir.

> [!warning]  
> Burada dikkat:
> 
> ```text
> 420 = decimal gösterim
> 0644 = octal izin gösterimi
> ```
> 
> İkisi aynı izin bitlerinin farklı sayı tabanındaki gösterimidir.

---

# 🧯 stdout / stderr Sırası Tuzağı

Container çıktısında hata mesajı:

```text
Dosya okunurken bir hata...
```

normal UID/GID çıktılarından önce görünebilir.

Bu, kodun mutlaka önce hatalı dosyayı işlediği anlamına gelmez.

Neden?

```text
stdout ve stderr
→ Ayrı akışlardır
→ Farklı buffering davranışları olabilir
```

`stderr` daha erken terminale ulaşırken `stdout` tamponda bekleyebilir.

> [!important]  
> Terminalde iki kanalın görünme sırasını kullanarak programın kesin çalışma sırasını çıkarmak risklidir.

---

# 🔒 `os.stat()` Gerçek Erişimi Kesin Kanıtlar mı?

Hayır.

Şunları bilsek bile:

```text
st_uid
st_gid
st_mode
process UID/GID
```

her zaman:

```text
“Process kesin okuyabilir.”
```

denemez.

Başka mekanizmalar devrede olabilir:

- ACL
    
- Mount seçenekleri
    
- Container isolation
    
- Security policy
    
- Başka filesystem kuralları
    

Gerçek erişimin en sağlam testi:

```python
try:
    with open("data.txt") as dosya:
        veri = dosya.read()
except PermissionError:
    print("Erişim reddedildi.")
```

olabilir.

---

# 🎯 Metadata Kontrolü Nerede Kullanılır?

## Docker

Bind mount edilmiş dosya container process’i tarafından açılamıyorsa:

```python
print("File UID:", bilgi.st_uid)
print("File GID:", bilgi.st_gid)

print("Process EUID:", os.geteuid())
print("Process EGID:", os.getegid())
print("Groups:", os.getgroups())
```

karşılaştırılabilir.

---

## Güvenlik Kontrolü

Örneğin:

```text
.env
private key
config
secret
```

dosyalarının:

- Yanlış kullanıcıya ait olup olmadığı
    
- Group tarafından yazılabilir olup olmadığı
    
- Others tarafından yazılabilir olup olmadığı
    
- Gereğinden geniş permission taşıyıp taşımadığı
    

kontrol edilebilir.

---

## Servis Deployment

Servis:

```text
www-data
```

olarak çalışıyor.

Dosya:

```text
root:root
600
```

ise:

```text
owner → rw-
group → ---
others → ---
```

olduğundan servis dosyayı okuyamayabilir.

---

# 🧯 Hata Avı

## 1. `st_gid` kullanıcının bütün gruplarıdır

TIRT.

Dosyanın sahip grubunun tek GID değeridir.

---

## 2. `st_mode = 420`, izin `420` demektir

TIRT.

```text
420 decimal = 0644 octal
```

---

## 3. Mode `755` ise erişim kesin bellidir

TIRT.

Önce process’in hangi izin sınıfına düştüğü belirlenmelidir.

---

## 4. Owner, group ve others izinleri toplanır

TIRT.

Yalnızca bir sınıf uygulanır.

---

## 5. Yalnız primary group erişimde önemlidir

TIRT.

Supplementary groups da değerlendirilir.

---

## 6. UID ile kullanıcı adı aynı şeydir

TIRT.

UID sayısal kimlik, kullanıcı adı okunabilir isimdir.

---

## 7. `id` dosyanın sahibini gösterir

TIRT.

`id`, komutu çalıştıran process/kullanıcının kimlik bilgilerini gösterir.

Dosyanın sahipliği:

```bash
stat
ls -l
```

ile incelenir.

---

## 8. Container UID farklıysa dosya değişmiştir

TIRT.

Process kimliği ile dosya kimliği farklı kavramlardır.

---

## 9. `--user` mount işlemini çözer

TIRT.

`--user` kimliği, mount dosyanın görünür konumunu belirler.

---

## 10. `os.stat()` izin veriyorsa `open()` kesin çalışır

TIRT.

ACL ve başka güvenlik katmanları devrede olabilir.

---

# 🧠 Kafaya Kazı

> [!quote]  
> `open()` içerik, `os.stat()` metadata içindir.

> [!quote]  
> `st_uid` dosyanın owner UID’sidir.

> [!quote]  
> `st_gid` dosyanın sahip grubunun GID’sidir.

> [!quote]  
> `st_mode` dosya türü ve permission bitlerini birlikte taşır.

> [!quote]  
> `stat.S_IMODE()` yalnız izin bitlerini ayırır.

> [!quote]  
> `420 decimal = 0644 octal`.

> [!quote]  
> Permission bitleri bitmask olduğu için `&` kullanılır.

> [!quote]  
> Owner/group/others izinleri birleşmez; yalnız bir sınıf seçilir.

> [!quote]  
> Dosya erişimi için process kimliği ile dosya UID/GID’si birlikte değerlendirilir.

> [!quote]  
> `id` process’i, `stat` dosyayı anlatır.

> [!quote]  
> Bind mount dosyanın konumunu, `--user` process kimliğini belirler.

> [!quote]  
> Dosyayı görmek, dosyaya erişebilmek anlamına gelmez.

> [!quote]  
> Container UID/GID farklılığı dosyayı kendiliğinden değiştirmez.

---
# 📌 30 Saniyelik Özet

```text
PYTHON
open()              → Dosya içeriği
os.stat()           → Dosya metadata
st_uid              → Owner UID
st_gid              → Owner group GID
st_mode             → Tür + izin bitleri
S_IMODE()           → Yalnız permission bitleri
filemode()          → -rw-r--r--

SAYI TABANI
420 decimal         → 0644 octal

LINUX
id                  → Process kimliği
ls -l               → İsimli owner/group
ls -ln              → Sayısal UID/GID
stat                → Ayrıntılı metadata

ERİŞİM
Owner eşleşir       → owner
Grup eşleşir        → group
Hiçbiri eşleşmez    → others
Üçlüler birleşmez

PROCESS
RUID                → Gerçek kullanıcı
EUID                → Effective kullanıcı
FSUID               → Filesystem kontrol kimliği

DOCKER
bind mount          → Dosya nerede?
--user              → Process kim?
-i/-t               → Terminal nasıl?

KRİTİK
Dosyayı görmek
≠
Dosyaya erişebilmek
```

---

# ✅ Günün Kazanımları

-  `open()` ve `os.stat()` ayrıldı
    
-  `st_uid`, `st_gid` ve `st_mode` öğrenildi
    
-  `stat.S_IMODE()` kullanıldı
    
-  Decimal `420` ile octal `0644` ilişkisi anlaşıldı
    
-  `stat.filemode()` ile okunabilir izin gösterimi öğrenildi
    
-  Permission bitleri `&` ile kontrol edildi
    
-  `FileNotFoundError` doğru katmanda yakalandı
    
-  `try/except` döngünün içine taşınarak devam davranışı korundu
    
-  `chmod`, UID ve GID değişikliklerinin etkileri ayrıldı
    
-  UID ile kullanıcı adı ayrıldı
    
-  Primary ve supplementary groups ayrıldı
    
-  Owner/group/others seçim mantığı öğrenildi
    
-  Permission üçlülerinin birleşmediği kavrandı
    
-  RUID, EUID ve FSUID ayrımı öğrenildi
    
-  `id`, `ls -l`, `ls -ln` ve `stat` rolleri ayrıldı
    
-  Bind mount ile `--user` ayrıldı
    
-  Host ve container process UID/GID’lerinin farklı olabileceği görüldü
    
-  Docker Desktop üzerinde ownership gösteriminin farklı olabileceği fark edildi
    
-  Mode bitlerinin aynı kalmasına rağmen erişimin değişebileceği anlaşıldı
    
-  Metadata incelemenin gerçek erişimi tek başına garanti etmediği öğrenildi
    

> [!success] 🚀 Gün sonu sonucu  
> Gün 9 sonunda dosya izni artık yalnızca `644`, `755` veya `rwx` olarak düşünülmüyor.
> 
> Gerçek erişim kararı:
> 
> ```text
> Process kimliği
> +
> Dosya sahipliği
> +
> Permission bitleri
> +
> Ek filesystem güvenlik mekanizmaları
> ```
> 
> birlikte değerlendirilerek veriliyor.
> 
> Docker deneyinde de en önemli ayrım netleşti:
> 
> ```text
> Aynı dosyaya farklı kimlikte process’ler bakabilir.
> Process kimliğinin değişmesi, dosyanın kendisinin değiştiği anlamına gelmez.
> ```