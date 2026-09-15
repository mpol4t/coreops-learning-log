---
title: "Gün 47 — File Descriptor, /proc, lsof ve strace"
tags:
  - coreops
  - day47
  - linux
  - file-descriptor
  - proc
  - lsof
  - strace
  - syscall
  - debugging
aliases:
  - "Gün 47 File Descriptor proc lsof strace"
status: completed
---

# 🔍 Day 47 — File Descriptor, `/proc`, `lsof` & `strace`

> [!abstract] 🎯 Ana fikir
> Bugün process'in dosya erişimini iki farklı açıdan incelemeyi öğrendim:
>
>     /proc/PID/fd + lsof
>     → process ŞU ANDA neyi açık tutuyor?
>
>     strace
>     → process kernel'dan NE İSTEDİ ve kernel NE CEVAP VERDİ?
>
> Ana zincirim:
>
>     PATH
>       ↓
>     openat()
>       ↓
>      FD
>       ↓
>     read / write
>       ↓
>     close
>
> Ve hata olduğunda:
>
>     syscall
>       ↓
>     kernel errno
>       ↓
>     Python exception
>       ↓
>     exit code

---

# 1️⃣ BLOK 1 — File Descriptor

File Descriptor'ı artık:

> **Process'in açık tuttuğu bir kaynağa ulaşmak için kullandığı küçük integer numara**

olarak düşünüyorum.

Örnek:

    FD 0 → stdin
    FD 1 → stdout
    FD 2 → stderr
    FD 3 → dosya
    FD 4 → socket
    FD 5 → pipe

Ama:

> **FD = dosyanın kendisi değildir.**

Doğru model:

    Process
       ↓
    FD Table
       ↓
      FD 3
       ↓
    Kernel'deki açık kaynak
       ↓
    dosya / socket / pipe / ...

Ayrıca FD process'e özeldir:

    Process A → FD 3 → a.txt
    Process B → FD 3 → b.txt

Yani tek başına:

    FD 3

çok anlamlı değil.

Asıl anlamlı ikili:

    PID + FD

---

# 🐧 `/proc/<PID>/fd`

Bir process'in mevcut açık FD'lerini:

    /proc/<PID>/fd

üzerinden görebiliyorum.

Örneğin gerçek labımda:

    0 → /dev/pts/0
    1 → /dev/pts/0
    2 → /dev/pts/0
    3 → coreops-fd-demo.txt

gördüm.

Ayrıca:

    readlink /proc/PID/fd/3

ile FD'nin bağlı olduğu gerçek hedefi görebildim.

Kısa:

    /proc/PID/fd
    → FD neye bağlı?

    /proc/PID/fdinfo/FD
    → offset / flags gibi daha ayrıntılı bilgi

---

# 📊 `lsof`

`lsof` = **list open files**

Ama sadece normal dosya göstermez.

Şunları da görebilir:

- socket
- pipe
- directory
- device
- başka kernel kaynakları

Mental model:

    /proc/PID/fd
    → kernel'in daha ham görünümü

    lsof
    → daha okunabilir görünüm

Örneğin:

    tail ... 6r REG ... coreops-tail.txt

Burada:

    6r
    ↓
    FD 6
    read

    REG
    ↓
    regular file

---

# 🧪 İlk Python FD Labı

Dosyayı açıp process'i `input()` ile beklettim.

Akış:

    file açılır
       ↓
    FD oluşur
       ↓
    input() bekler
       ↓
    process yaşamaya devam eder
       ↓
    dosya açık kalır
       ↓
    başka terminalden /proc incelenir

`file.fileno()` bana gerçek OS FD numarasını verdi.

Örneğin:

    pid=312567
    fd=3

Sonra `/proc/312567/fd/3` üzerinden gerçekten aynı dosyayı gördüm.

Yani:

    Python file object
         ↓
    file.fileno()
         ↓
       FD 3
         ↓
    Linux /proc
         ↓
    gerçek kaynak

---

# 🐞 İki Dosyayı Aynı Anda Açma Hatası

İlk denemem:

    with file1:
        ...

    with file2:
        ...

Bu yapıda:

    file1 açılır
       ↓
    ilk with biter
       ↓
    file1 kapanır
       ↓
    file2 açılır

Yani iki dosya **aynı anda açık değildi**.

Düzeltme:

    with file1, file2:
        ...

Akış:

    file1 açık
       +
    file2 açık
       ↓
    input bekliyor
       ↓
    /proc içinde iki FD de mevcut

Bu bana önemli bir şey öğretti:

> **`with` bloğunun scope'u kaynağın ne kadar süre açık kalacağını belirler.**

---

# 🔢 FD Her Zaman 3 Değil

Python örneğinde dosya:

    FD 3

oldu.

Ama `tail -f` deneyinde:

    FD 6

oldu.

Çünkü process zaten:

    0 → stdin
    1 → stdout
    2 → stderr
    3 → inotify
    4 → eventpoll
    5 → eventfd
    6 → coreops-tail.txt

kullanıyordu.

Yani:

> **FD numarası dosyanın özelliği değil, process'in o andaki FD tablosuna bağlıdır.**

---

# 🐞 BLOK 1 Hatalarım

## 1. İki ayrı `with` ile iki dosyanın aynı anda açık olduğunu düşündüm

Yanlış.

İlk `with` bitince ilk dosya kapanıyordu.

---

## 2. PID'yi yanlış yazdım

Gerçek:

    312567

Ben:

    312456

yazdım.

Sonuç:

    No such file or directory

Problem `/proc` değildi.

**PID yanlıştı.**

> Runtime değerlerini ezberden değil çıktıya bakarak kullan.

---

## 3. FD'nin hep 3 olacağını düşünmeye yaklaştım

**TIRT.**

    FD 3

sadece sık görülen ilk uygun numara.

`tail` labında gerçek dosya:

    FD 6

oldu.

---

# 2️⃣ BLOK 2 — `strace`

> [!important]
> `strace` bana:
>
> **Program kernel'dan ne istedi ve kernel ne cevap verdi?**
>
> sorusunun cevabını gösteriyor.

Yüksek seviye:

    Path.read_text()

Alt taraf:

    Python runtime
          ↓
       openat()
          ↓
        Kernel

Ben `strace` ile bu alt katmanı görüyorum.

---

# 🆚 `/proc` — `lsof` — `strace`

    /proc/PID/fd
    → ŞU ANDA hangi FD'ler açık?


    lsof
    → ŞU ANDA hangi kaynaklar açık?


    strace
    → Program ne yapmaya ÇALIŞTI?
      Kernel ne cevap verdi?

Çok önemli fark:

Bir dosyayı açmaya çalışırsam:

    openat(...) = -1 ENOENT

FD hiç oluşmaz.

Bu yüzden `/proc/PID/fd` içinde göremem.

Ama `strace`:

> "Process bunu açmaya çalıştı ve başarısız oldu."

diye gösterebilir.

---

# 🚪 `openat()` Nasıl Okunur?

Örnek:

    openat(
        AT_FDCWD,
        "/tmp/a.txt",
        O_RDONLY
    ) = 3

Türkçesi:

> `/tmp/a.txt` dosyasını okumak için açtım ve kernel bana FD 3 verdi.

Parçalar:

    openat
    → syscall

    AT_FDCWD
    → relative path varsa CWD baz alınabilir

    "/tmp/a.txt"
    → hedef path

    O_RDONLY
    → read-only

    = 3
    → SUCCESS + FD 3

Başarısız:

    openat(...) = -1 ENOENT

Burada:

    -1
    → failure

    ENOENT
    → path bulunamadı

Ve:

    FD YOK

---

# 🔍 `%file`, `%desc` ve `-P`

Başta burada bayağı karıştırdım.

## `%file`

    -e trace=%file

şu demek:

> Path / filename ile ilgili syscall kategorisini göster.

Bu:

    %.py

gibi dosya uzantısı filtresi **değil**.

---

## `%desc`

FD üzerinden çalışan syscall'ları düşünürüm:

    read()
    write()
    close()

---

## `-P`

    -P /tmp/a.txt

şu demek:

> Bu specific path ile ilgili syscall'ları göster.

Kafaya:

    %file
    → HANGİ TÜR syscall?


    -P
    → HANGİ PATH?

Mental model:

    bütün syscall'lar
          ↓
    -e trace=%file
          ↓
    path kullanan syscall'lar
          ↓
    -P /tmp/a.txt
          ↓
    özellikle bu path

---

# 🌉 PATH Dünyasından FD Dünyasına

En önemli strace resmi:

    "/tmp/a.txt"
         ↓
      openat()
         ↓
        FD 3
         ↓
    ┌────┼─────┐
    ↓    ↓     ↓
   read write close

Yani:

    openat()
    → PATH ile çalışıyor

sonrasında:

    read(3, ...)
    close(3)

gibi işlemler FD üzerinden devam ediyor.

Kabaca:

    openat → %file

    read   → %desc
    close  → %desc

---

# 📖 `read()` Kafa Karışıklığım

Şunu gördüm:

    read(3, "hello", 5) = 5

ve ilk başta:

> `"hello"`yu ben nasıl önceden biliyorum?

diye düşündüm.

Çünkü bu satırı benim yazdığım kod sandım.

**TIRT.**

Gerçek mantık:

    read(fd, buffer, count)

Program kabaca:

    read(3, buffer, 5)

diyor.

Yani:

> FD 3'ten en fazla 5 byte oku, sonucu buffer'a koy.

Kernel okuyor:

    hello

Buffer'a koyuyor.

`strace` syscall bittikten sonra sonucu gösteriyor:

    read(3, "hello", 5) = 5

> **`"hello"`yu ben vermedim. Kernel okudu, strace bana gösterdi.**

---

# 📦 Buffer Neden Gerekli?

Bir ara:

    read(3,,5)

olabilir mi diye düşündüm.

Hayır.

Kernel'ın okuduğu veriyi koyacağı bellek alanı lazım.

Mental model:

    read(
        FD,
        NEREYE,
        EN_FAZLA_NE_KADAR
    )

Yani:

    read(3, buffer, 5)

---

# 🔢 `read()` Sonundaki Sayılar

    read(3, buffer, 5)

buradaki:

    5
    → EN FAZLA 5 byte oku

Kesin 5 byte gelmek zorunda değil.

Örneğin yalnız 2 byte varsa:

    read(3, "hi", 5) = 2

---

# 🏁 EOF

Şunu görürsem:

    read(3, "", 5) = 0

bu:

    EOF
    End Of File

demek.

Yani:

> Okuyacak veri kalmadı.

---

# 🚪 `close()`

    close(3) = 0

demek:

> Process artık FD 3'ü kullanmayacak.

Bu:

    dosyayı diskten sil ❌

değildir.

Sadece:

    Process
       ↓
      FD 3
       ↓
      close
       ↓
    bağlantı kapandı

Geçersiz FD:

    close(99) = -1 EBADF

    EBADF
    → Bad file descriptor

---

# 💥 Gerçek strace Labı

Önce çalışan baseline:

    input.txt
    → hello-coreops

`strace`:

    openat(... input.txt ..., O_RDONLY|O_CLOEXEC) = 3

Program:

    hello-coreops

ve:

    +++ exited with 0 +++

Yani:

    path bulundu
       ↓
    openat başarılı
       ↓
    FD oluştu
       ↓
    dosya okundu
       ↓
    exit 0 ✅

---

# 🐞 İlk Gerçek Lab Hatalarım

## 1. Path string'inde quote hatası yaptım

İlk Python kodunda path string'ini yanlış yazıp:

    SyntaxError:
    unterminated string literal

aldım.

Bu kernel / filesystem problemi değildi.

Daha Python kodu parse edilirken patlıyordu.

Düzelttikten sonra:

    hello-coreops

çıktısını aldım.

---

## 2. Veri dosyasını Python programı olarak çalıştırdım

Yanlış:

    python3 input.txt

Halbuki:

    input.txt
    → VERİ

    read_file.py
    → PROGRAM

Doğru model:

    python3 read_file.py
              ↓
          input.txt

Yanlış denemede Python `hello-coreops` metnini kod sanıp hata verdi.

---

# 💣 Broken Case 1 — Dosya Yok

Script:

    olmayan_input.txt

dosyasını okumaya çalıştı.

`strace`:

    openat(... "olmayan_input.txt", ...)
    = -1 ENOENT

Python:

    FileNotFoundError

Program:

    exit 1

Tam zincir:

    Path.read_text()
          ↓
      openat()
          ↓
    Kernel path'i bulamadı
          ↓
      -1 ENOENT
          ↓
       FD YOK
          ↓
    FileNotFoundError
          ↓
       exit 1

Buradaki en önemli nokta:

    openat() = -1
         ↓
      FD oluşmaz

---

# 💣 Broken Case 2 — Dosya Var Ama İzin Yok

Dosya başlangıçta:

    664
    rw-rw-r--

idi.

Lab için:

    chmod 000 input.txt

yaptım.

Sonra:

    ---------- input.txt

oldu.

Doğru `strace` çıktısı:

    openat(... "input.txt", ...)
    = -1 EACCES

Python:

    PermissionError

Program:

    exit 1

Akış:

    path VAR
      ↓
    openat()
      ↓
    kernel permission kontrolü
      ↓
    erişim reddedildi
      ↓
    -1 EACCES
      ↓
    FD YOK
      ↓
    PermissionError
      ↓
    exit 1

---

# 🆚 `ENOENT` vs `EACCES`

Bunu artık ezber değil, gerçek lab çıktısıyla ayırıyorum:

    DOSYA/PATH YOK              PATH VAR AMA İZİN YOK

    openat()                    openat()
       ↓                           ↓
    -1 ENOENT                   -1 EACCES
       ↓                           ↓
    FD YOK                      FD YOK
       ↓                           ↓
    FileNotFoundError           PermissionError
       ↓                           ↓
    exit 1                      exit 1

Kafaya:

    ENOENT
    → "Aradığın şey yok."


    EACCES
    → "Nerede olduğunu biliyorum ama giremezsin."

Bu iki case dosyada da doğrudan doğrulandı.

---

# ❓ EACCES Olduğunda Neden `read()` Yok?

Çünkü:

    openat()
       ↓
    -1 EACCES
       ↓
    FD YOK

FD yoksa:

    read(FD, ...)

yapacak geçerli descriptor da yok.

Normal:

    openat()
       ↓
      FD 3
       ↓
    read(3,...)

Permission failure:

    openat()
       ↓
    -1 EACCES
       ↓
    STOP

---

# 🐞 En Öğretici Hata — Yanlış Dosyayı Test Ettim

Ben:

    chmod 000 input.txt

yaptım.

Sonra EACCES bekledim.

Ama hâlâ:

    FileNotFoundError / ENOENT

geliyordu.

Sebep?

`read_file.py` içinde hâlâ:

    olmayan_input.txt

vardı.

Yani ben:

    input.txt permission
    ↓
    değiştirdim

ama program:

    olmayan_input.txt
    ↓
    okumaya çalışıyordu

İki olayın birbirine alakası yoktu.

Düzeltme:

    script target
    → input.txt

yaptım.

Sonra gerçekten:

    EACCES
    PermissionError

geldi.

> [!danger]
> **Debug ederken önce programın gerçekten hangi resource'a eriştiğini doğrula.**
>
> Yoksa doğru şeyi bozup yanlış şeyi gözlemleyebilirsin.

---

# 🔤 Escaped UTF-8 Path Hatası

`strace` çıktısında:

    Masa\303\274st\303\274

gördüm.

Bunun gerçek shell path'i olduğunu düşünüp `-P` içine koydum.

Yanlış.

Gerçek path:

    Masaüstü

`strace`, `ü` karakterini escaped byte biçiminde gösteriyordu.

Yani:

    strace gösterimi
    → Masa\303\274st\303\274

    gerçek shell path
    → Masaüstü

`-P` kullanırken gerçek path'i vermeliyim.

Bu hata yüzünden bir denemede beklediğim syscall filtrede görünmedi.

---

# 🎯 Python Path vs `strace -P`

Aynı path iki yerde geçebilir ama görevleri farklı.

Python:

    Path("/.../input.txt")

demek:

> **PROGRAM hangi dosyaya erişecek?**

`strace`:

    -P /.../input.txt

demek:

> **STRACE hangi path'e ait syscall'ları bana gösterecek?**

Kısa:

    Python path
    → HEDEF

    strace -P
    → FİLTRE

---

# 🧪 Bağımsız `report.json` Case

Aynı mantığı farklı dosyada tekrar yaptım.

Permission case:

    report.json
       ↓
    chmod 000
       ↓
    openat(...) = -1 EACCES
       ↓
    PermissionError

Missing case:

    olmayan_report.json
       ↓
    openat(...) = -1 ENOENT
       ↓
    FileNotFoundError

Böylece aynı teşhisi başka dosyada da yapabildiğimi doğruladım.

---

# 🐞 Diğer Hatalarım

## `python` kullandım

Sistemde:

    python

executable'ı yoktu.

Sonuç:

    Cannot find executable 'python'

Doğrusu:

    python3

---

## Missing case'te alakasız dosyanın permission'ını değiştirdim

Script:

    olmayan_report.json

okuyordu.

Ben:

    chmod 644 report.json

yaptım.

Bu testin sonucunu değiştirmez.

Çünkü hedef başka dosya.

> **Her zaman gerçek target'ı takip et.**

---

## Permission'ı eski haline tam döndürmedim

Başlangıç:

    664

Lab:

    000

Sonra sadece okunabilir olsun diye:

    644

vermek mümkün.

Ama exact rollback istiyorsam:

    664

vermeliyim.

Kısa:

> **"Çalışıyor" ile "eski state'e döndü" aynı şey değil.**

---

## Görevdeki exact path'i kullanmadım

Talimat:

    /tmp/coreops-strace/report.json

Ben ise:

    ~/Masaüstü/.../report.json

üzerinde aynı mantığı uyguladım.

Teknik sonuç:

    ENOENT ✅
    EACCES ✅

doğruydu.

Ama lab disiplini açısından:

> **Mantığı doğru uygulamak başka, verilen görevi birebir takip etmek başka.**

---

# 🧭 Bundan Sonraki `strace` Okuma Algoritmam

Bir satır görünce:

    1. Hangi syscall?

    2. Hangi path / FD?

    3. Argümanlar ne?

    4. Return value ne?

    5. Success mı failure mı?

    6. Failure ise errno ne?

    7. FD oluştu mu?

    8. Python bunu hangi exception olarak gösterdi?

    9. Program hangi exit code ile bitti?

Özellikle dosya açma problemi:

    openat(...)
       ↓
    return değerine bak

    >= 0
    → FD
    → SUCCESS

    -1 ENOENT
    → path yok

    -1 EACCES
    → permission yok

---

# 🧠 Kafaya Kazı

> [!tip]
> **PID process'i bulur.**

> [!tip]
> **FD process'in açık kaynağına erişim numarasıdır.**

> [!tip]
> **FD process'e özeldir; her zaman 3 değildir.**

> [!tip]
> **`/proc/PID/fd` = process şu anda neyi açık tutuyor?**

> [!tip]
> **`lsof` = açık kaynakları okunabilir göster.**

> [!tip]
> **`strace` = process kernel'dan ne istedi, kernel ne cevap verdi?**

> [!tip]
> **`%file` = syscall kategorisi.**

> [!tip]
> **`-P` = path filtresi.**

> [!tip]
> **PATH → `openat()` → FD**

> [!tip]
> **FD → `read()` / `write()` / `close()`**

> [!tip]
> **`read(...)=0` → EOF**

> [!tip]
> **`close()` FD'yi kapatır, dosyayı silmez.**

> [!danger]
> **ENOENT = YOK**

> [!danger]
> **EACCES = VAR AMA ERİŞEMİYORSUN**

> [!danger]
> **`openat()` başarısızsa FD yoktur; FD yoksa o dosya için `read()` aşamasına geçilemez.**

---

# 📌 30 Saniyelik Özet

    PROCESS
       ↓
      PID
       ↓
    FD TABLE
       ↓
      FD
       ↓
    DOSYA / SOCKET / PIPE


    ŞU ANKİ DURUM:

    /proc/PID/fd
         +
        lsof


    DAVRANIŞ:

       strace
         ↓
      syscall
         ↓
       kernel


    SUCCESS:

    openat(path) = 3
          ↓
        FD 3
          ↓
        read
          ↓
        close
          ↓
       exit 0


    MISSING:

    openat(path)
          ↓
      -1 ENOENT
          ↓
       FD YOK
          ↓
    FileNotFoundError
          ↓
       exit 1


    PERMISSION:

    openat(path)
          ↓
      -1 EACCES
          ↓
       FD YOK
          ↓
     PermissionError
          ↓
       exit 1

---

# ✅ Günün Kazanımları

- [x] File Descriptor mental modelini oturttum
- [x] FD'nin dosyanın kendisi olmadığını öğrendim
- [x] FD'nin process'e özgü olduğunu gördüm
- [x] `0 / 1 / 2` stdin-stdout-stderr ayrımını uyguladım
- [x] `/proc/<PID>/fd` ile açık kaynakları gözlemledim
- [x] `readlink` ile FD hedefini doğruladım
- [x] `lsof` ile ikinci kanıt aldım
- [x] `3r / 3w / 3u` mantığını öğrendim
- [x] Aynı anda iki dosyayı açık tutmayı uyguladım
- [x] `tail -f` process'inde gerçek FD 6 gördüm
- [x] inotify / eventpoll / eventfd gibi kaynakların da FD kullandığını gördüm
- [x] `/proc` ve `strace` farkını ayırdım
- [x] `openat()` satırını okumayı öğrendim
- [x] `%file`, `%desc` ve `-P` farkını oturttum
- [x] `read(fd, buffer, count)` mantığını öğrendim
- [x] `read() = 0` → EOF olduğunu öğrendim
- [x] `close()` işleminin dosyayı silmediğini öğrendim
- [x] Başarılı `openat(...) = FD` case'ini gördüm
- [x] `ENOENT → FileNotFoundError` zincirini canlı gördüm
- [x] `EACCES → PermissionError` zincirini canlı gördüm
- [x] Başarısız `openat()` sonrası FD oluşmadığını anladım
- [x] Yanlış target path yüzünden yanlış teşhis yapabileceğimi gördüm
- [x] Escaped UTF-8 path gösterimini gerçek path'ten ayırdım
- [x] `python` / `python3` executable farkını debug ettim
- [x] Aynı broken case'leri `report.json` üzerinde bağımsız tekrar ettim
- [x] Kernel errno → Python exception → exit code zincirini oturttum

---

# 🚀 Gün Sonu

> **Bugün dosya hatasına artık sadece Python tarafından bakmamayı öğrendim.**
>
> Bir `FileNotFoundError` veya `PermissionError` gördüğümde kafamda artık şu zincir çalışıyor:
>
>     Python exception
>           ↑
>     Python runtime
>           ↑
>       kernel errno
>           ↑
>        syscall
>
> Yani sorum artık sadece:
>
> **"Python neden hata verdi?"**
>
> değil:
>
> **"Hangi syscall hangi resource üzerinde başarısız oldu, kernel hangi errno'yu döndürdü ve bundan sonra FD oluştu mu?"**
>
> Bu soruları cevaplayabiliyorsam gerçekten teşhis yapıyorum.