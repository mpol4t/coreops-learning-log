---
tags:
  - day48
  - linux
  - process
  - cpu
  - ram
  - proc
  - df
  - du
  - dd
  - docker
  - resources
status: devam ediyor
---

# ⚙️ Day 48 — Process Resources, Disk Kullanımı & Docker Limits

> [!info] Güncel durum — 16 Eylül 2026
> **V4.1-08 devam ediyor.** Linux CPU/RAM/process ve disk gözlem blokları mentor tarafından onaylandı. Aşağıdaki Docker limitleri bölümü şu an teorik nottur; kontrollü container uygulaması henüz tamamlanmadı. Bu, geçmiş Linux bloklarının eksik olduğu anlamına gelmez.
>
> - [x] Linux process / CPU / RAM gözlemi
> - [x] Linux disk gözlemi: df / du ve kontrollü dosya büyümesi
> - [ ] Docker --memory / --cpus uygulaması ve runtime doğrulaması

> Arşiv notu: Obsidian Gün48 notu ve mentor/kanonik ilerleme kayıtları esas alınmıştır. Ölçümler önceki Ubuntu labına aittir; bu arşivleme sırasında yeniden çalıştırılmadı. Orijinal workload dosyaları bu klasöre aktarılmış değildir. Docker uygulaması tamamlandığında aynı günün kaydı güncellenecektir.

> [!abstract] 🎯 Ana fikir
> Bugün Linux'ta iki farklı resource dünyasını gerçek ölçümlerle gözlemledim:
>
>     PROCESS
>     → CPU / RAM / state
>
>     STORAGE
>     → filesystem / dosya-dizin kullanımı
>
> Temel ayrımlar:
>
>     STAT → process ŞU AN ne yapıyor?
>     %CPU → CPU kullanım davranışı
>     RSS  → RAM'de resident kısım
>     VSZ  → virtual address space
>
>     df → filesystem ne kadar dolu?
>     du → bu alanı ne dolduruyor?

---

# 1️⃣ BLOK 1 — Process CPU / RAM Gözlemi

Kendi Python workload'umu oluşturdum:

    40 MiB memory ayır
        ↓
    20 saniye sürekli hesap yap
        ↓
    30 saniye sleep

Böylece **aynı PID'nin farklı runtime durumlarını** görebildim.

---

# 🧠 Process Alanları

Kafamdaki kısa tablo:

    PID
    → hangi process?

    PPID
    → parent kim?

    STAT
    → process şu anda ne durumda?

    RSS
    → fiziksel RAM'de resident kısım

    VSZ
    → virtual address space

    ELAPSED / etime
    → process başlayalı geçen süre

    TIME
    → CPU üzerinde gerçekten harcanan süre

En önemli:

    ELAPSED ≠ CPU TIME

ve:

    VSZ ≠ fiziksel RAM kullanımı

---

# 🟢 `STAT`: R, S ve `+`

CPU loop sırasında:

    STAT = R+

gördüm.

    R
    → running / runnable

    +
    → terminalin foreground process grubunda

CPU işi bitip:

    time.sleep(30)

başlayınca:

    STAT = S+

oldu.

    S
    → sleeping / bir olay bekliyor

Ama PID aynı kaldı.

Bu bana:

> **STAT process'in kimliğini değil, o anki durumunu gösterir.**

mantığını oturttu.

---

# 🧵 `l` ve Thread

STAT içinde:

    Sl+

gibi bir şey görürsem:

    S → sleeping
    l → multi-threaded
    + → foreground process group

Thread'i artık:

> **Process içindeki yürütme akışı**

olarak düşünüyorum.

    Process
      ├── Thread 1
      ├── Thread 2
      └── Thread 3

Thread ≠ ayrı process.

`/proc/<PID>/status` içindeki:

    Threads: N

alanı da gerçek thread sayısını gösteriyor.

---

# 🖥️ Foreground / Background / Process Group

Terminalde:

    python3 app.py

çalıştırırsam job foreground'da.

Ama:

    python3 app.py &

dersem background'a gider ve shell prompt'u geri gelir.

Process group'un neden gerektiğini pipeline üzerinden anladım:

    cat file | grep ERROR

Bu tek terminal işi gibi görünse de birden fazla process içeriyor.

    Foreground Process Group
          ├── cat
          └── grep

Bu yüzden:

    Ctrl+C
    → genellikle foreground gruba SIGINT

    Ctrl+Z
    → genellikle foreground gruba SIGTSTP

gönderilmesiyle ilişkili.

> `Ctrl+Z` process'i öldürmez; durdurabilir.

---

# 🔥 Gerçek CPU Ölçümü

40 MiB workload CPU phase sırasında:

    PID   STAT  %CPU   RSS     VSZ
    3986  R+    99.8   52284   63092

Yaklaşık:

    RSS ≈ 51 MiB
    VSZ ≈ 62 MiB

İlk hatam:

    RSS 52284
    → 61 MiB

diye okumaktı.

**TIRT.**

Doğrusu:

    52284 / 1024
    ≈ 51.1 MiB

61 MiB civarı olan VSZ'ydi.

---

# 🧠 `%CPU` Neden Sleep Başlayınca 0 Olmadı?

CPU işi bittikten sonra gerçek ölçümlerimde:

    ELAPSED   STAT   %CPU    RSS
    00:21     S+     91.7    52380
    00:27     S+     72.3    52380
    00:36     S+     54.8    52380
    00:47     S+     41.7    52380

gördüm.

Process artık sleep'te olmasına rağmen `%CPU` yavaş yavaş düştü.

Mental model:

    CPU time
    ---------
    elapsed time

Process ilk 20 saniye CPU'yu çok kullandı.

Sonra sleep:

    CPU time yaklaşık sabit
    ELAPSED büyüyor
         ↓
    oran düşüyor

Bu yüzden:

> **`ps %CPU` = "tam şu anda CPU kaç?" diye okunmamalı.**

---

# 🧠 CPU Bitti Ama RSS Neden Aynı Kaldı?

Çünkü:

    CPU işi bitti

demek:

    memory serbest bırakıldı

demek değil.

`bytearray` hâlâ hayattaydı.

Bu yüzden:

    R+ → S+
    %CPU ↓
    RSS ≈ sabit

gözledim.

Yani:

    STAT
    CPU
    RAM

üç ayrı şey.

---

# 🧪 Kontrollü RAM Deneyi

Tek değiştirdiğim şey:

    40 MiB
       ↓
    80 MiB bytearray

40 MiB case:

    RSS ≈ 51 MiB

80 MiB case:

    RSS ≈ 89 MiB

Yaklaşık fark:

    +38 MiB

Allocation:

    +40 MiB

Tam birebir sayı beklemiyorum.

Önemli olan:

    memory allocation ↑
           ↓
          RSS ↑

CPU loop aynı kaldığı için `%CPU` yine yaklaşık 100'dü.

Bu güzel bir **tek değişkenli kontrollü deney** oldu.

---

# ♾️ `yes > /dev/null`

Python'dan bağımsız CPU workload olarak:

    yes > /dev/null

kullandım.

    yes
    → sürekli çıktı üretir

    /dev/null
    → çıktıyı çöpe atar

Bu sayede terminali `y` ile doldurmadan CPU workload ürettim.

Gerçek ölçüm:

    %CPU ≈ 99.9
    RSS  ≈ 5.7 MiB

Python 80 MiB workload:

    %CPU ≈ 99
    RSS  ≈ 89 MiB

Sonuç:

> **Yüksek CPU kullanımı ≠ yüksek RAM kullanımı.**

---

# 🐞 BLOK 1 Hatalarım

### `time.monotonic()` rastgele sayı sandım

Hayır.

    başlangıç = monotonic()
    bitiş     = başlangıç + 20

Mutlak sayı önemli değil.

    bitiş - başlangıç
    → 20 saniye

Özellikle geçen süre ölçmek için uygun.

---

### `x=975579` değerine fazla anlam yükledim

CPU yüzdesi veya iteration sayısı değil.

Modulo yüzünden sürekli dönebiliyor.

Asıl işaret:

    cpu_phase_done

→ CPU phase bitti.

---

### `grep` pattern'im fazla genişti

    Pid

arayınca:

    Pid
    PPid
    TracerPid

eşleşebildi.

Daha doğru:

    ^

ile satır başını zorlamak.

---

### `elapsed` kullandım

Yanlış:

    -o elapsed

Doğru `ps` identifier:

    -o etime

Ama ekranda sütun:

    ELAPSED

olarak görünüyor.

---

### `Ctrl+Z` ile process'i kapattığımı düşündüm

Hayır.

Process durmuş halde sistemde kalabilir.

Eski `yes` process'ini:

    kill -TERM PID

ile temizledim.

---

# 2️⃣ BLOK 2 — `df`, `du`, `dd`, `sort`

> [!important]
> En kritik ayrım:
>
>     df
>     → FILESYSTEM
>
>     du
>     → DOSYA / DİZİN

Kafamdaki soru modeli:

    "Disk ne kadar dolu?"
           ↓
          df

    "Neyi silersem yer açılır?"
           ↓
          du

---

# 💽 `df`

Örneğin:

    df -h .

şunu sormuyor:

> "." dizini kaç GB?

Şunu soruyor:

> "." hangi filesystem üzerinde ve o filesystem ne durumda?

Labda:

    Size  = 58G
    Used  = 13G
    Avail = ~43G
    Use%  = 23%

gördüm.

Bu **coreops-disk klasörünün boyutu değil**, bulunduğu `/` filesystem'inin durumuydu.

---

# 📁 `du`

    du -sh .

ise:

> Mevcut dizin ve altındakiler gerçekten ne kadar disk alanı kullanıyor?

sorusuna cevap veriyor.

Labda:

    du -sh .
    → 21M

iken:

    df -h .
    → 58G filesystem

gösterdi.

Çelişki yok:

    df
    → bütün filesystem

    du
    → seçtiğim dizin ağacı

---

# 🧱 `dd`

İlk başta:

    if
    of
    bs
    count

ne bilmiyordum.

Mental model:

    KAYNAK
      ↓
     dd
      ↓
    HEDEF

    if
    → input source

    of
    → output destination

    bs
    → block size

    count
    → kaç block?

Örneğin:

    bs=1M
    count=20

→ yaklaşık:

    20 MiB

---

# 0️⃣ `/dev/zero`

Kaynak:

    /dev/zero

normal dosya gibi düşünülmemeli.

Okundukça sıfır byte üretir.

    /dev/zero
        ↓
       dd
        ↓
    sample.bin

Bu sayede kontrollü boyutta test dosyası oluşturdum.

> `dd` kullanırken özellikle `of=` hedefini iki kere kontrol et.

---

# 🐞 `dd` Hedef Yolunu Yanlış Verdim

İlk hedef:

    day48/Blok2/sample.bin

oldu.

Ama istediğim:

    day48/Blok2/coreops-disk/sample.bin

idi.

Yani:

    of=

path'inde `coreops-disk` kısmını unuttum.

Yanlış yerdeki dosyayı kaldırıp doğru yerde yeniden oluşturdum.

Bu hata önemli çünkü `dd` yanlış hedefe gerçekten veri yazabilir.

---

# 🧪 Kontrollü Disk Değişimi

İlk dosya:

    sample.bin ≈ 20 MiB

Dizin:

    du -sh .
    → 21M

Sonra:

    second.bin ≈ 10 MiB

ekledim.

Tekrar:

    du -sh .
    → 31M

Yani:

    21M
     +
    ~10M
     ↓
    31M

`du` dizinin disk kullanımındaki değişimi yakaladı.

---

# 📂 `--max-depth=1`

Dosyaları:

    coreops-disk/
    ├── a/
    │   └── sample.bin
    └── b/
        └── second.bin

şeklinde ayırdım.

Sonra:

    du -h --max-depth=1 .

çıktısı:

    21M ./a
    11M ./b
    31M .

oldu.

Buradaki fikir:

    -s
    → sadece TOPLAM

    --max-depth=1
    → birinci seviye alt klasörleri ayrı göster

Gerçek disk debug'ında çok kullanışlı:

> "Hangi ana klasör alanı yiyor?"

---

# 🐞 `cp` Yerine `mv` Kullanmalıydım

Dosyaları taşımak isterken:

    cp

kullandım.

Sonuç:

    hedefte kopya var
    +
    kaynak hâlâ var

Doğru araç:

    mv

Kafaya:

    cp
    → kopyala
    → kaynak kalır

    mv
    → taşı / rename

Sonradan kaynak kopyaları silerek düzelttim.

---

# 📊 `sort -rh`

Home dizinimde:

    du -h --max-depth=1 . | sort -rh

kullandım.

Burada:

    du -h
    → K/M/G şeklinde human-readable çıktı üretir

    sort -h
    → K/M/G boyutlarını anlayarak karşılaştırır

    sort -r
    → ters sırala
    → büyükten küçüğe

Sonuçlarda yaklaşık:

    /home/polat → 130M
    snap        → 79M
    Masaüstü    → 31M
    .cache      → 20M

gördüm.

---

# 🧠 `df` / `du` Farkı Daha Derinde Neden Olabilir?

Aynı path için rakamlar garip biçimde uyuşmuyorsa şunları da düşünebilirim:

    deleted ama hâlâ open file
    reserved blocks
    permission
    filesystem metadata
    farklı mount/filesystem

Özellikle:

    process dosyayı açtı
        ↓
    dosya rm ile silindi
        ↓
    FD hâlâ açık
        ↓
    path görünmez
        ↓
    bloklar hâlâ kullanımda

Bu durumda:

    du
    → dosyayı göremeyebilir

    df
    → alanı hâlâ kullanılmış görebilir

---

# 🧩 Inode

Diskte GB olarak boş alan olması her zaman yeterli değil.

Çok fazla küçük dosya:

    inode'ları tüketebilir

Kontrol:

    df -i

Yani:

> "Diskte yer var ama dosya oluşturamıyorum."

durumunda inode da aklıma gelmeli.

---

# 🐳 Docker Resource Limits — Teorik Notlar, Uygulama Bekliyor

Teorik tarafta ayrıca şunları ayırdım:

    --memory=256m
    → RAM limiti

    --cpus=0.5
    → ne kadar CPU kapasitesi?

    --cpuset-cpus=0
    → hangi logical CPU?

En kritik:

    --cpus
    ≠
    CPU numarası seçmek

Kısa:

    --cpus
    → QUOTA / KAPASİTE

    --cpuset-cpus
    → AFFINITY / HANGİ CPU

---

# 📈 `docker stats` vs `docker inspect`

    docker stats
    → ŞU ANDA ne tüketiyor?

CPU, memory, network, block I/O, PIDs gibi runtime kullanımı.

    docker inspect
    → nasıl ayarlanmış / state ne?

Örneğin:

    Status
    Running
    ExitCode
    OOMKilled

---

# 💥 Exit Code 137

Kafaya:

    137
    = 128 + 9
    → SIGKILL

Ama:

    ExitCode 137
    ≠
    kesin OOM

Çünkü process başka nedenle de SIGKILL alabilir.

OOM iddiası için daha spesifik kanıt:

    OOMKilled=true

gibi state bilgilerine bakmalıyım.

---

# 🧭 Debug Akışlarım

Process:

    PID'yi bul
      ↓
    STAT
      ↓
    %CPU / RSS / VSZ
      ↓
    ELAPSED / TIME
      ↓
    /proc/PID/status ile doğrula


Disk:

    df
      ↓
    hangi filesystem dolu?
      ↓
    du --max-depth=1
      ↓
    hangi klasör büyük?
      ↓
    bir seviye aşağı in
      ↓
    suçluyu bul


Container:

    limit tanımla
      ↓
    docker stats
      ↓
    runtime kullanım
      ↓
    sorun varsa inspect
      ↓
    state / ExitCode / OOMKilled

---

# 🧠 Kafaya Kazı

> [!tip]
> **R = running/runnable**

> [!tip]
> **S = sleeping / waiting**

> [!tip]
> **`+` = foreground process group**

> [!tip]
> **RSS = RAM'de resident kısım**

> [!tip]
> **VSZ = virtual address space**

> [!danger]
> **VSZ ≠ fiziksel RAM**

> [!tip]
> **ELAPSED = process yaşı**

> [!tip]
> **TIME = CPU zamanı**

> [!danger]
> **ELAPSED ≠ TIME**

> [!danger]
> **Yüksek CPU ≠ yüksek RAM**

> [!tip]
> **`df` = filesystem ne kadar dolu?**

> [!tip]
> **`du` = alanı ne yiyor?**

> [!tip]
> **`du -sh` = tek toplam**

> [!tip]
> **`du --max-depth=1` = ilk seviye karşılaştır**

> [!tip]
> **`sort -h` = K/M/G değerlerini anlayarak sırala**

> [!tip]
> **`df -i` = inode kullanımı**

> [!danger]
> **`dd` kullanırken `of=` hedefini kontrol et.**

> [!danger]
> **Exit 137 tek başına OOM kanıtı değildir.**

---

# 📌 30 Saniyelik Özet

    PROCESS

    CPU işi
      ↓
     R+
      ↓
    %CPU ≈ 100

    sleep
      ↓
     S+
      ↓
    %CPU zamanla düşer

    ama RAM tutuluyorsa:
      ↓
    RSS sabit kalabilir


    STORAGE

    df
    → FILESYSTEM

    du
    → DOSYA / DİZİN

    dd
    → kontrollü dosya üret

    du --max-depth=1
    → büyük klasörü bul

    sort -rh
    → büyükten küçüğe sırala


    DOCKER

    --memory
    → RAM

    --cpus
    → ne kadar CPU?

    --cpuset-cpus
    → hangi CPU?

    stats
    → canlı kullanım

    inspect
    → config + state

---

# ✅ Günün Kazanımları

- [x] `STAT` alanını gerçek process üzerinde gözlemledim
- [x] `R+ → S+` geçişini canlı gördüm
- [x] `ps %CPU` değerinin anlık snapshot olmadığını gördüm
- [x] RSS / VSZ farkını gerçek değerlerle doğruladım
- [x] `/proc/PID/status` ile `VmRSS` / `VmSize` karşılaştırdım
- [x] 40 MiB → 80 MiB kontrollü RAM deneyini yaptım
- [x] Yüksek CPU ile yüksek RAM'in aynı şey olmadığını kanıtladım
- [x] `yes > /dev/null` ile bağımsız CPU workload oluşturdum
- [x] `Ctrl+Z`, `SIGTERM`, `SIGINT` davranışlarını tekrar ettim
- [x] `df` ve `du` farkını gerçek dosyalarla doğruladım
- [x] `dd` içindeki `if/of/bs/count` mantığını öğrendim
- [x] `/dev/zero` ile kontrollü dosya ürettim
- [x] Yanlış `of=` path hatasını bulup düzelttim
- [x] `du` ile 21M → 31M değişimini gördüm
- [x] `cp` / `mv` farkını canlı hatayla öğrendim
- [x] `du --max-depth=1` ile alt klasörleri karşılaştırdım
- [x] `sort -rh` ile disk kullanımını büyükten küçüğe sıraladım
- [x] `df -i` ile inode kontrolünün neden önemli olduğunu öğrendim
- [x] Docker RAM / CPU limitlerinin temel mantığını ayırdım
- [x] `docker stats` ve `docker inspect` farkını oturttum
- [x] Exit 137'nin tek başına OOM kanıtı olmadığını öğrendim

---

# 🚀 Gün Sonu

> Bugünün iki ana debug sorusu:
>
> **Process için:**
> "Şu anda ne yapıyor, CPU/RAM'i ne kadar tüketiyor?"
>
> **Disk için:**
> "Filesystem ne kadar dolu ve bunu hangi dizin dolduruyor?"
>
> En kısa final:
>
>     ps / proc
>     → process kaynaklarını anla
>
>     df
>     → problemi gör
>
>     du
>     → suçluyu bul
>
>     kontrollü deney
>     → varsayımı kanıtla
