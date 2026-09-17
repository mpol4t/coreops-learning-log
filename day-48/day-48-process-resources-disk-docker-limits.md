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
status: tamamlandı
---

# ⚙️ Day 48 — Process Resources, Disk Kullanımı & Docker Limits

> [!info] Güncel durum — 17 Eylül 2026
> **Gün 48 / V4.1-08 GEÇTİ.** Linux CPU/RAM/process ve disk blokları 16 Eylül'de, Docker CPU limiti devamı 17 Eylül'de tamamlandı. Mentor oturumu kapattı; kanonik kayıt da kapanışı kabul etti. Takvim günü değişse de bu çalışma Gün 48'e aittir.
>
> - [x] Linux process / CPU / RAM gözlemi
> - [x] Linux disk gözlemi: df / du ve kontrollü dosya büyümesi
> - [x] Docker CPU limiti: --cpus, docker stats ve inspect/NanoCpus doğrulaması
>
> RAM limiti / OOM uygulaması yapılmadı; ilgili bölüm teorik not olarak korunur. Mentor bunu bu oturum için zorunlu açık saymadı. Sıradaki oturum Gün 49 / V4.1-09: Dockerfile ile build-time dependency kurulumu; ardından küçük multi-stage ve non-root/yazılabilir yol.

> Arşiv notu: 16 Eylül Obsidian Gün48 notu ile 17 Eylül mentora teslim edilen Docker CPU lab notu aynı günün tek dosyasında birleştirildi. Linux ölçümleri önceki Ubuntu labına, Docker ölçümleri teslim edilen CPU labına aittir; arşivleme sırasında deneyler yeniden çalıştırılmadı. Bu gün yalnız not olarak yayımlanır; orijinal Ubuntu çalışma dosyalarının yüklenmemesi teslim eksiği değildir.

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

# 🐳 Docker Resource Limits — 16 Eylül Teorik Hazırlık

CPU limiti uygulaması 17 Eylül'de tamamlandı ve bu dosyanın son bölümüne eklendi. Aşağıdaki RAM/OOM açıklamaları uygulama kanıtı değildir.

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

---

## 17 Eylül devamı — Docker CPU limiti labı (Gün 48 / V4.1-08)

Aşağıdaki öğrenme notu mentora yapılan teslimden alınmıştır. Bu devam ayrı Gün 49 değildir. Mentor sonucu: **GEÇTİ; V4.1-08 kapandı; zorunlu açık yok.**

### V4.1-08 — Docker Resource Limit / `--cpus`

#### Ana fikir

Bu labda bir container'ın CPU kullanımını Docker üzerinden nasıl sınırlandırdığımı ve verdiğim limitin gerçekten uygulanıp uygulanmadığını iki farklı şekilde doğruladım.

Kullandığım iki ana araç:

```bash
docker stats
```

→ Container çalışırken **runtime'da gerçekten ne kadar kaynak kullandığını** gösteriyor.

```bash
docker inspect
```

→ Container'ın **hangi ayarlarla configure edildiğini** gösteriyor.

Kısaca:

```text
docker inspect
→ "Ne ayarladım?"

docker stats
→ "Çalışırken gerçekte ne oluyor?"
```

Buradaki en önemli mantık:

```text
CONFIG
+
RUNTIME OBSERVATION
=
KANIT
```

Sadece `--cpus=0.50` yazıp “herhalde uygulanmıştır” demek yerine hem config'i hem de runtime davranışını doğruladım.

---

#### 1. Limitsiz baseline

İlk olarak container'a herhangi bir CPU sınırı vermeden CPU-bound bir workload çalıştırdım.

Kullandığım komut:

```bash
docker run --rm --name coreops-cpu \
  python:3.13-slim \
  python -c 'x=0
while True:
    x=(x+1)%1000003'
```

Container içinde çalışan Python kodunun mantığı:

```python
x = 0

while True:
    x = (x + 1) % 1000003
```

Bu kod:

- sürekli hesap yapıyor
- dosya beklemiyor
- network beklemiyor
- kullanıcı input'u beklemiyor
- `sleep` yapmıyor

Yani CPU sürekli iş yapıyor.

Bu yüzden workload **CPU-bound**.

##### CPU-bound ne demek?

Bir programın çalışmasını esas olarak CPU kapasitesi sınırlıyorsa o iş CPU-bound'dur.

Kabaca:

```text
CPU
████████████████████

RAM
█

Disk
-

Network
-
```

Bu workload'da ana kaynak CPU.

---

#### 2. `docker stats` ile baseline gözlemi

İkinci terminalde:

```bash
docker stats coreops-cpu
```

çalıştırdım.

Gözlediğim değerler:

```text
CPU %      ≈ 99.90%
MEM         13.65 MiB / 7.748 GiB
MEM %       ≈ 0.17%
PIDS        1
```

Buradaki yaklaşık `%100 CPU`, Mac'in bütün işlemcisinin `%100` kullanıldığı anlamına gelmiyor.

Burada kabaca:

```text
1 CPU kapasitesi ≈ %100
```

olarak düşünebilirim.

Bu değer sonraki deneyler için baseline oldu:

```text
Limitsiz CPU-bound workload
→ ~%99.90 CPU
```

---

#### 3. Container'ı kapatma

`docker stats` ekranından çıkmak için:

```text
Ctrl + C
```

kullandım.

Bu sadece `docker stats` komutunu kapatıyor.

Container'ın kendisini durdurmak için:

```bash
docker stop coreops-cpu
```

kullandım.

Önemli ayrım:

```text
Ctrl + C
→ stats ekranından çıkmak

docker stop
→ container'ı durdurmak
```

---

#### 4. `--cpus=0.50` ile CPU limiti

Aynı workload'u bu sefer yarım CPU limitiyle çalıştırdım.

```bash
docker run --rm --cpus="0.50" --name coreops-cpu-limited \
  python:3.13-slim \
  python -c 'x=0
while True:
    x=(x+1)%1000003'
```

Buradaki:

```text
--cpus="0.50"
```

şu anlama geliyor:

```text
Container yaklaşık 0.5 CPU kapasitesi kadar CPU zamanı kullanabilir.
```

Şu anlama GELMİYOR:

```text
Bir fiziksel CPU çekirdeğinin yarısını container'a kalıcı olarak ayır.
```

Daha doğru düşünce:

```text
CPU scheduler
      ↓
container'a çalışma zamanı veriyor
      ↓
maksimum yaklaşık 0.50 CPU kapasitesi
```

Python workload'u değişmedi.

Program hâlâ sürekli hesap yapmak istiyor ama Docker CPU kullanımını sınırlıyor.

---

#### 5. `0.50 CPU` runtime sonucu

İkinci terminalde:

```bash
docker stats coreops-cpu-limited
```

çalıştırdım.

Gözlediğim:

```text
CPU ≈ 49.71%
MEM ≈ 5.184 MiB
PIDS = 1
```

Karşılaştırma:

```text
Limitsiz
→ %99.90

--cpus=0.50
→ %49.71
```

Yani aynı Python workload'u çalışmasına rağmen CPU kullanımı yaklaşık yarıya düştü.

Bu bize runtime tarafında CPU limitinin etkisini gösterdi.

---

#### 6. `docker inspect` ile config doğrulaması

Sadece `docker stats` çıktısına bakmak istemedim.

Container gerçekten `0.50 CPU` ile configure edilmiş mi diye:

```bash
docker inspect coreops-cpu-limited
```

çalıştırdım.

Çıktı çok büyüktü.

CPU ile ilgili kısımları ararken şu satırı buldum:

```json
"NanoCpus": 500000000
```

Bu değer verdiğim `--cpus=0.50` ayarının config'e gerçekten işlendiğini gösterdi.

---

#### 7. NanoCPU mantığı

Docker CPU değerini config tarafında NanoCPU cinsinden tutabiliyor.

Temel ilişki:

```text
1 CPU = 1,000,000,000 NanoCPU
```

Dolayısıyla:

```text
0.50 CPU
=
500,000,000 NanoCPU
```

Benim `docker inspect` çıktım:

```text
NanoCpus = 500000000
```

olduğu için:

```text
--cpus=0.50
```

ayarının config'e doğru işlendiğini doğruladım.

---

#### 8. `docker inspect --format` ile sadece istediğim alanı alma

Full `docker inspect` çıktısı gereksiz derecede büyüktü.

Sadece `NanoCpus` değerini almak için:

```bash
docker inspect \
  --format '{{.HostConfig.NanoCpus}}' \
  coreops-cpu-limited
```

çalıştırdım.

Çıktı:

```text
500000000
```

Bu kullanım çok daha temiz.

Kısaca:

```text
docker inspect
→ bütün config

docker inspect --format ...
→ sadece istediğim alan
```

---

#### 9. Config + runtime kanıtı

`0.50 CPU` için elimde iki ayrı kanıt oluştu.

##### Config kanıtı

```bash
docker inspect \
  --format '{{.HostConfig.NanoCpus}}' \
  coreops-cpu-limited
```

çıktı:

```text
500000000
```

Yani:

```text
container config
→ 0.50 CPU
```

##### Runtime kanıtı

```bash
docker stats coreops-cpu-limited
```

çıktı:

```text
CPU ≈ %49.71
```

Yani:

```text
CONFIG
NanoCpus = 500000000

+

RUNTIME
CPU ≈ %49.71

=

CPU limiti gerçekten uygulanıyor
```

---

### 10. `--cpus=0.25` deneyi

Sonra limiti:

```text
0.50
```

değerinden:

```text
0.25
```

değerine düşürdüm.

Komutu çalıştırmadan önce tahmin yaptım.

##### Tahmin

```text
0.50 CPU → yaklaşık %50

0.25 CPU → yaklaşık %25
```

NanoCPU hesabı:

```text
0.25 × 1,000,000,000
=
250,000,000
```

Beklentim:

```text
CPU ≈ %25
NanoCpus = 250000000
```

---

#### 11. `0.25 CPU` gerçek sonucu

Container'ı `--cpus="0.25"` ile çalıştırdıktan sonra:

```bash
docker stats coreops-cpu-limited
```

ile:

```text
CPU = %24.93
```

gördüm.

Ardından:

```bash
docker inspect \
  --format '{{.HostConfig.NanoCpus}}' \
  coreops-cpu-limited
```

çıktısı:

```text
250000000
```

oldu.

Karşılaştırma:

```text
Tahmin CPU
≈ %25

Gerçek CPU
= %24.93
```

ve:

```text
Tahmin NanoCpus
= 250000000

Gerçek NanoCpus
= 250000000
```

Tahmin ile gerçek sonuç uyuştu.

---

### 12. Exact CPU yüzdesine takılmamak

İlk başta:

```text
0.25 CPU için belki %24.85 çıkar
```

gibi gereğinden fazla spesifik tahmin yaptım.

Bu düşünce doğru değil.

CPU kullanımında:

- scheduler
- host üzerindeki diğer işler
- Docker Desktop ortamı
- ölçüm anı

gibi faktörlerden dolayı küçük oynamalar olabilir.

Bu yüzden doğru düşünce:

```text
0.25 CPU
→ yaklaşık %25 CPU
```

Yanlış düşünce:

```text
kesin %24.85 çıkmalı
```

Gerçekte:

```text
%24.93
```

çıktı.

Ama önemli olan `%25` civarında olması.

---

### 13. Bağımsız varyant

Sonraki aşamada kendi iki CPU limitimi seçtim.

Seçimlerim:

```text
A = 0.20 CPU
B = 0.75 CPU
```

Amaç aynı workload'u iki farklı CPU limitiyle çalıştırıp sonucu önceden tahmin etmekti.

---

### 14. A — `0.20 CPU`

Önce tahmin yaptım.

CPU tahmini:

```text
≈ %20
```

NanoCPU hesabı:

```text
0.20 × 1,000,000,000
=
200,000,000
```

Beklentim:

```text
CPU ≈ %20
NanoCpus = 200000000
```

Container'ı `--cpus="0.20"` ile çalıştırdım.

`docker stats` sonucu:

```text
CPU = %19.94
```

`docker inspect` sonucu:

```text
NanoCpus = 200000000
```

Karşılaştırma:

```text
Tahmin CPU
≈ %20

Gerçek CPU
= %19.94
```

NanoCPU değeri de tam tahmin ettiğim gibi çıktı:

```text
200000000
```

---

### 15. B — `0.75 CPU`

Sonra ikinci bağımsız limit olarak:

```text
0.75 CPU
```

seçtim.

CPU tahmini:

```text
≈ %75
```

NanoCPU hesabı:

```text
0.75 × 1,000,000,000
=
750,000,000
```

Beklentim:

```text
CPU ≈ %75
NanoCpus = 750000000
```

Container'ı `--cpus="0.75"` ile çalıştırdım.

`docker stats` sonucu:

```text
CPU = %74.86
```

`docker inspect` sonucu:

```text
NanoCpus = 750000000
```

Karşılaştırma:

```text
Tahmin CPU
≈ %75

Gerçek CPU
= %74.86
```

NanoCPU değeri:

```text
750000000
```

olarak tam doğru çıktı.

---

### Tüm deney sonuçları

| CPU limiti | Beklenen CPU | Gerçek CPU | NanoCpus |
|---|---:|---:|---:|
| Limitsiz | ~%100 | `%99.90` | limit yok |
| `0.50` | ~%50 | `%49.71` | `500000000` |
| `0.25` | ~%25 | `%24.93` | `250000000` |
| `0.20` | ~%20 | `%19.94` | `200000000` |
| `0.75` | ~%75 | `%74.86` | `750000000` |

Bu tablo labın ana sonucu oldu.

CPU limitini azalttıkça CPU-bound workload'un runtime'daki CPU kullanımı da yaklaşık aynı oranda azaldı.

```text
1.00 CPU → ~%100
0.75 CPU → ~%75
0.50 CPU → ~%50
0.25 CPU → ~%25
0.20 CPU → ~%20
```

---

### Hatalar / Takıldığım Yerler

#### 1. İlk workload'un gerçekten çalışıp çalışmadığını anlayamadım

İlk komutu çalıştırdıktan sonra terminal prompt'u geri gelmedi.

İlk tepkim:

```text
"Bunu mu çalıştıracağım?"
```

oldu.

Ama aslında bu hata değildi.

Kodun içinde:

```python
while True:
```

olduğu için program sonsuza kadar çalışıyordu.

Foreground process çalıştığı için terminal prompt'u geri vermiyordu.

Buradan öğrendiğim:

```text
Prompt geri gelmedi
≠
program bozuldu
```

Çalışan foreground process varsa terminalin beklemesi normal.

---

#### 2. `docker inspect` çıktısı çok büyüktü

İlk olarak:

```bash
docker inspect coreops-cpu-limited
```

çalıştırdım.

Çıktı devasa geldi.

CPU ile ilgili alanları arayıp:

```text
NanoCpus
```

satırını buldum.

Daha sonra daha temiz yöntem olarak:

```bash
docker inspect \
  --format '{{.HostConfig.NanoCpus}}' \
  coreops-cpu-limited
```

kullandım.

Böylece sadece ihtiyacım olan değeri aldım.

---

#### 3. CPU yüzdesini gereğinden fazla kesin tahmin ettim

Bağımsız varyantta başlangıçta:

```text
0.20 → %19.87
0.75 → %74.78
```

gibi exact değerler tahmin etmeye çalıştım.

Bu gereksiz.

Doğru tahmin biçimi:

```text
0.20 CPU → yaklaşık %20
0.75 CPU → yaklaşık %75
```

Gerçek ölçümler:

```text
0.20 CPU → %19.94
0.75 CPU → %74.86
```

çıktı.

Yani trendi doğru tahmin etmek önemli, ondalık basamakları değil.

---

### Kafaya kazı

#### `--cpus=0.50` ne demek?

```text
Container'a yaklaşık yarım CPU kapasitesi kadar CPU zamanı kullanma hakkı vermek.
```

Şu değildir:

```text
Bir fiziksel çekirdeğin yarısını container'a özel ayırmak.
```

---

#### CPU yüzdesini hızlı tahmin etme

CPU-bound bir workload için kabaca:

```text
--cpus=1.00 → ~%100
--cpus=0.75 → ~%75
--cpus=0.50 → ~%50
--cpus=0.25 → ~%25
--cpus=0.20 → ~%20
```

---

#### NanoCPU hesabı

Temel değer:

```text
1 CPU = 1,000,000,000 NanoCPU
```

Formül:

```text
NanoCpus
=
CPU limiti × 1,000,000,000
```

Örnek:

```text
0.50 × 1,000,000,000
=
500,000,000
```

Başka örnekler:

```text
0.25 CPU
→ 250000000 NanoCPU

0.20 CPU
→ 200000000 NanoCPU

0.75 CPU
→ 750000000 NanoCPU
```

---

#### `docker stats`

Şu soruyu cevaplıyor:

```text
Container şu anda gerçekte ne kadar kaynak kullanıyor?
```

Yani runtime gözlem aracı.

Örnek:

```bash
docker stats coreops-cpu-limited
```

---

#### `docker inspect`

Şu soruyu cevaplıyor:

```text
Container nasıl configure edilmiş?
```

Örnek:

```bash
docker inspect coreops-cpu-limited
```

Sadece istediğim alan:

```bash
docker inspect \
  --format '{{.HostConfig.NanoCpus}}' \
  coreops-cpu-limited
```

---

#### `stats` ile `inspect` farkı

```text
docker stats
→ runtime

docker inspect
→ config/state
```

Örnek:

```text
docker inspect
→ NanoCpus = 500000000

docker stats
→ CPU = %49.71
```

Bunlar birbirini tamamlıyor.

---

#### En güçlü doğrulama

Sadece:

```text
flag yazdım
```

demek yeterli değil.

Daha güçlü yöntem:

```text
1. Config'i doğrula
   ↓
docker inspect

2. Runtime davranışını gözle
   ↓
docker stats
```

İkisi uyuşuyorsa:

```text
resource limit gerçekten uygulanıyor
```

diyebilirim.

---

### Mini sınav

#### 1. `--cpus=0.40` verirsem CPU-bound bir workload'da yaklaşık kaç CPU yüzdesi beklerim?

Yaklaşık:

```text
%40
```

Tam `%40.00` olmak zorunda değil.

---

#### 2. `--cpus=0.40` için NanoCpus kaç olur?

```text
0.40 × 1,000,000,000
=
400000000
```

---

#### 3. `docker stats` ile `docker inspect` arasındaki fark nedir?

```text
docker stats
→ runtime'daki gerçek kaynak kullanımını gösterir

docker inspect
→ container'ın config/state bilgisini gösterir
```

---

#### 4. `docker stats` üzerinde `%49.8` gördüm. Bu tek başına container'ın `--cpus=0.50` ile configure edildiğini kesin kanıtlar mı?

Hayır.

Bu sadece runtime gözlemidir.

Config'i doğrulamak için:

```bash
docker inspect
```

kullanmalıyım.

---

#### 5. CPU-bound ne demek?

Programın iş yapma hızının esas olarak CPU kapasitesi tarafından sınırlandırılması.

Program CPU'yu sürekli kullanmak istiyor ve ana darboğaz CPU.

---

#### 6. Neden `--cpus=0.25` verdiğimde tam `%25.00` görmek zorunda değilim?

Çünkü:

- scheduler
- host yükü
- Docker ortamı
- ölçüm anı

küçük sapmalara neden olabilir.

Önemli olan değerin yaklaşık `%25` civarında olmasıdır.

---

### Kısa özet

Bu labda CPU-bound bir Docker container'ının CPU kullanımını `--cpus` ile sınırlandırdım.

İlk limitsiz baseline:

```text
CPU ≈ %99.90
```

Daha sonra:

```text
--cpus=0.50
→ %49.71

--cpus=0.25
→ %24.93

--cpus=0.20
→ %19.94

--cpus=0.75
→ %74.86
```

sonuçlarını aldım.

Config tarafında:

```text
0.50 CPU
→ NanoCpus = 500000000

0.25 CPU
→ NanoCpus = 250000000

0.20 CPU
→ NanoCpus = 200000000

0.75 CPU
→ NanoCpus = 750000000
```

değerlerini doğruladım.

Kafama kazınması gereken temel ilişki:

```text
1 CPU
=
1,000,000,000 NanoCPU
```

Ayrıca:

```text
docker inspect
→ ne configure edilmiş?

docker stats
→ runtime'da gerçekte ne oluyor?
```

ayrımını öğrendim.

En önemli çıkarım:

```text
CONFIG
+
RUNTIME OBSERVATION
=
KANIT
```

---

### Final durum

Lab sonunda:

- CPU-bound workload'un ne olduğunu gözlemledim.
- Limitsiz baseline aldım.
- `--cpus` ile container CPU kullanımını sınırladım.
- `0.50`, `0.25`, `0.20` ve `0.75` CPU limitlerini test ettim.
- `docker stats` ile runtime kaynak kullanımını gözlemledim.
- `docker inspect` ile CPU limitinin config'e işlendiğini doğruladım.
- `--format` ile inspect çıktısından tek alan çekmeyi kullandım.
- NanoCPU mantığını öğrendim.
- `1 CPU = 1,000,000,000 NanoCPU` ilişkisini öğrendim.
- CPU limiti düştükçe CPU-bound workload'un kullanımının da yaklaşık aynı oranda düştüğünü deneyle gördüm.
- Exact yüzdelere değil yaklaşık beklenen değere bakmam gerektiğini öğrendim.
- Config ve runtime doğrulamasını birlikte kullanmanın neden daha güçlü olduğunu öğrendim.

**V4.1-08 — Docker Resource Limit labı tamamlandı.**
