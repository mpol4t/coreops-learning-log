---
title: "Gün 30 — Child Contract, Timeout, Process Group ve Cleanup Lifecycle"
tags:
  - coreops
  - day30
  - python
  - subprocess
  - process
  - process-group
  - session
  - timeout
  - signals
  - sigterm
  - sigkill
  - wait
  - reap
  - linux
aliases:
  - "Gün 30 Child Contract Timeout ve Process Group Cleanup"
status: completed
---

# 🧠 Gün 30 — Child Contract, Timeout, Process Group ve Cleanup Lifecycle

> [!abstract] 🎯 Ana fikir
> Bugün `subprocess` tarafında bir tık daha ileri gidip şunu öğrendim:
>
> **Bir child process başlatmak yetmiyor. Başlattığım işin bütün yaşam döngüsünden de sorumlu olmam gerekebilir.**
>
> Özellikle child kendi child'larını oluşturuyorsa:
>
>     main
>       ↓
>     child
>       ↓
>     grandchild
>
> sadece `child` PID'sini yönetmek yeterli olmayabilir.
>
> Bir runner'ın gerçek lifecycle'ı:
>
>     spawn
>     ↓
>     wait
>     ↓
>     timeout
>     ↓
>     TERM
>     ↓
>     grace period
>     ↓
>     gerekirse KILL
>     ↓
>     wait / reap
>
> Eğer process ağacı oluşuyorsa bunun üstüne:
>
>     process group
>
> yönetimi de ekleniyor.

---

# 🌳 İlk Lab — Process Ağacı Oluşturdum

Üç program:

    main.py
      ↓
    child.py
      ↓
    grandchild.py

`main.py` child'ı başlatıyor.

`child.py` grandchild'ı başlatıyor.

`grandchild.py` ise uzun süre yaşayan process olarak sürekli bekliyor.

Amaç:

> Parent-child ilişkisini, timeout'u ve cleanup davranışını gerçekten gözlemlemek.

---

# ⚠️ İlk Hata — `Popen()` Yaptım Ama Parent'lar Bitiyordu

İlk başta kafamda:

    Popen(child)
    -> child başlar
    -> parent da orada kalır

gibi bir model vardı.

TIRT.

`Popen()`:

> **Child process'i başlatır ve parent'a geri döner.**

Yani tek başına parent'ı bekletmez.

Şu durum oluşabilir:

    main
    -> child başlatır
    -> main biter

    child
    -> grandchild başlatır
    -> child biter

    grandchild
    -> yaşamaya devam eder

Halbuki benim görmek istediğim:

    main
      └── child
            └── grandchild

üçünün de aynı anda yaşamasıydı.

---

# ⏳ Çözüm — `wait()`

`main.py` içinde:

    child = Popen(...)
    child.wait()

`child.py` içinde de:

    grandchild = Popen(...)
    grandchild.wait()

mantığını kullandım.

Kısa model:

    Popen()
    -> child başlat

    wait()
    -> o child bitene kadar parent burada beklesin

Önemli:

> `wait()` child öldüğünde parent'ı öldürmez.

Sadece:

    wait blokajı kalkar
    ↓
    parent sonraki satıra geçer

Eğer aşağıda başka kod yoksa parent dosya sonuna gelir ve normal şekilde exit eder.

---

# 🔍 Process Tree'yi Kanıtladım

Programlar çalışırken PID'leri yazdırdım.

Sonra:

`pstree -p MAIN_PID`

ile:

    main
      └── child
            └── grandchild

yapısını gördüm.

Ardından:

`ps -o pid,ppid,pgid,sid,stat,cmd -p PIDLER`

ile daha detaylı baktım.

---

# 🪪 PID / PPID / PGID / SID

Bugün bu dört kavramı aynı tabloda gördüm.

## PID

> Process'in kendi kimliği.

## PPID

> Parent process'in PID'si.

## PGID

> Process'in hangi process group'a ait olduğunu gösterir.

## SID

> Process'in hangi session'a ait olduğunu gösterir.

> [!important]
> **Process tree ile process group aynı şey değil.**

Tree:

    kim kimi oluşturdu?

Group:

    hangi process'ler birlikte yönetilen bir gruba ait?

sorusunu cevaplıyor.

---

# 👥 İlk Process Group Durumu

İlk labda yaklaşık şu yapı çıktı:

    main        PID 4299   PGID 4299
    child       PID 4305   PGID 4299
    grandchild  PID 4306   PGID 4299

PID'ler farklı.

Ama PGID aynı.

Yani child normalde parent'ın process group bilgisini miras alabiliyor.

Grandchild da child'dan miras alıyor.

---

# 💥 Bunun Sorunu Ne?

Diyelim timeout oldu ve ben:

> "Bu işin bütün process group'una SIGTERM göndereyim."

dedim.

Ama:

    main
    child
    grandchild

üçü de aynı PGID'deyse group signal atınca **main de hedef olur.**

Bu benim runner tasarımım için kötü.

Çünkü istediğim:

    RUNNER
    main
    -> ayrı

    WORKLOAD
    child
      └── grandchild
    -> ayrı process group

Böylece main dışarıdan yöneten taraf olur.

---

# 🧱 `start_new_session=True`

Bunu çözmek için:

`start_new_session=True`

kullandım.

Kafamda:

    subprocess(..., setsid())

gibi garip bir şey yapacağımı düşünmüştüm.

Gerek yokmuş.

Python `Popen` bunu benim için sağlıyor.

POSIX tarafındaki temel fikir:

    child
    ↓
    yeni session
    ↓
    yeni process group

---

# Yeni Boundary

Örneğin:

    main
    PID  = 4468
    PGID = 4468
    SID  = 4058

    child
    PID  = 4472
    PGID = 4472
    SID  = 4472

    grandchild
    PID  = 4473
    PGID = 4472
    SID  = 4472

Tam istediğim şey:

    main
    -> ayrı

    child + grandchild
    -> aynı process group

Child yeni session/process-group leader olduğu için burada:

    child PID
    =
    child PGID
    =
    child SID

oldu.

Grandchild da özel bir değişiklik yapmadığı için group/session bilgisini child'dan aldı.

---

# 🎯 Neden Tek PID Yerine Process Group?

Şu yapı varsa:

    main
      └── child
            └── grandchild

ve sadece:

`kill -TERM CHILD_PID`

yaparsam yalnız child hedeflenir.

Ama:

> **Parent ölünce child da kesin ölür**

diye bir Unix kuralı yok.

Dolayısıyla child ölürken grandchild yaşamaya devam edebilir.

Bu yüzden tek bir "işe" ait process'leri aynı group altında toplamak çok daha yönetilebilir.

---

# 🎯 PID Signal vs Process Group Signal

Tek PID:

`kill -TERM 4472`

anlamı:

    PID 4472
    -> TERM

Yani yalnız child.

Process group:

`kill -TERM -- -4472`

anlamı:

    PGID 4472
    -> TERM

Böylece:

    child
    +
    grandchild

ikisi de signal alır.

---

# ➖ Neden `-4472`?

Negatif değer:

> **Tek PID yerine process group hedefle.**

mantığında kullanılıyor.

Yani:

    4472
    -> PID

    -4472
    -> PGID

---

# `--` Ne İşe Yarıyor?

Komut:

`kill -TERM -- -4472`

Burada:

    -TERM
    -> signal seçimi

    --
    -> optionlar burada bitti

    -4472
    -> artık option değil, hedef argümanı

Unix CLI araçlarında genel olarak:

> **`--` sonrasını option olarak yorumlama.**

---

# 🧪 Process Group Cleanup Testi

Child ve grandchild aynı PGID altındayken:

`kill -TERM -- -4472`

gönderdim.

Sonra `ps` ile baktığımda process'ler kalmamıştı.

Akış:

    SIGTERM
    ↓
    child process group
    ↓
    child sonlanır
    grandchild sonlanır

Main ise farklı PGID'de olduğu için signal almadı.

---

# 🤔 Main Neden Sonra Kapandı?

Main'in içinde:

`child.wait()`

vardı.

Child ölünce:

    child.wait()
    ↓
    tamamlandı

Main sonraki satıra geçti.

Aşağıda kod yoktu.

Dolayısıyla:

    main
    -> normal exit

etti.

Önemli ayrım:

> Main process group signal yüzünden ölmedi.

Main kendi normal control flow'u nedeniyle sonlandı.

---

# 🟡 TERM Neden KILL'den Önce?

`SIGTERM`:

> **Kontrollü kapanma isteği.**

Program bunu handle ederse:

- yaptığı mevcut işi bitirebilir
- dosyaları kapatabilir
- buffer flush edebilir
- temporary state temizleyebilir
- child'larını kapatabilir
- normal exit yapabilir

---

# 🔴 SIGKILL

`SIGKILL` geldiğinde uygulama:

> "Dur cleanup yapayım."

diyemez.

Handler çalıştıramaz.

Kernel process'i zorla sonlandırır.

Bu yüzden lifecycle policy:

    TERM
    ↓
    biraz bekle
    ↓
    hâlâ kapanmadı mı?
    ↓
    KILL

olmalı.

Kısa:

> **TERM = fırsat ver.  
> KILL = zorla bitir.**

---

# ⏱️ Timeout Contract

Sonra main'i yalnızca sonsuza kadar bekleyen parent olmaktan çıkarıp gerçek runner mantığına yaklaştırdım.

Yeni lifecycle:

    child başlat
    ↓
    belli süre bekle
    ↓
    tamamlandı mı?
       ├── evet -> normal devam
       └── hayır -> TimeoutExpired
                      ↓
                     TERM
                      ↓
                   grace period
                      ↓
                    KILL?
                      ↓
                  wait / reap

---

# `wait(timeout=3)`

Kullandığım mantık:

`child.wait(timeout=3)`

Child üç saniye içinde tamamlanmazsa:

`subprocess.TimeoutExpired`

oluşuyor.

Buradaki kritik nokta:

> **Timeout olması child'ın otomatik öldürüldüğü anlamına gelmiyor.**

`wait(timeout=3)` bana:

> "Üç saniye geçti ve child hâlâ tamamlanmadı."

bilgisini veriyor.

Sonraki lifecycle kararını **runner olarak ben veriyorum.**

---

# 🐍 Python'dan Process Group'a Signal

Terminalde:

`kill -TERM -- -PGID`

yaptığım şeyin Python tarafında karşılığı:

`os.killpg(pgid, signal.SIGTERM)`

Ben `start_new_session=True` kullandığım için child process group leader oldu.

Bu yüzden labda:

    child.pid
    =
    PGID

olarak kullanabildim.

---

# 🔄 Timeout Lifecycle

Kullandığım sözleşme:

    child.wait(timeout=3)
    ↓
    TimeoutExpired
    ↓
    process group'a SIGTERM
    ↓
    grace period
    ↓
    grup hâlâ yaşıyorsa SIGKILL
    ↓
    child.wait()
    ↓
    reap

Bu artık basit:

    timeout oldu

mantığından daha fazlası.

> **Timeout sonrasında ne yapılacağı da runner'ın contract'ıdır.**

---

# 🧹 Signal ile `wait()` Aynı Şey Değil

Signal:

> Process'e bir olay gönder.

`wait()`:

> Child'ın tamamlanmasını bekle ve termination sonucunu topla.

Yani:

    TERM veya KILL
    ↓
    process sonlanır
    ↓
    wait / reap

şeklinde düşünmeliyim.

Signal göndermek:

> "Lifecycle tamamen bitti."

demek değildir.

---

# 👻 Reap

Child sonlandığında parent açısından completion bilgisi hâlâ toplanmayı bekleyebilir.

Kabaca:

    child running
    ↓
    child exit
    ↓
    exit status
    ↓
    parent wait()
    ↓
    reap

Bu yüzden direct child için `wait()` tarafını unutmamam gerekiyor.

---

# 🧟 Zombie Nüansı

Bir noktada:

`os.killpg(pgid, 0)`

ile:

> "Process group hâlâ var mı?"

diye kontrol ettim.

Ama burada küçük bir lifecycle tuzağı var.

TERM alan child sonlanmış olsa bile henüz parent tarafından `wait()` edilmediyse kısa süre zombie state bulunabilir.

Bu yüzden:

    killpg(pgid, 0)
    -> group var

sonucu:

> **TERM kesin başarısız oldu.**

anlamına gelmeyebilir.

---

# ✅ Daha Temiz Timeout Yaklaşımı

Daha temiz lifecycle şu olabilir:

    TERM
    ↓
    child.wait(timeout=grace)
    ↓
    grace içinde bitti mi?
       ├── evet -> tamam
       └── hayır -> KILL
                     ↓
                  child.wait()

Bu sayede direct child'ın gerçek completion'ını `wait()` üzerinden takip etmek daha temiz olur.

> [!warning]
> Labdaki `killpg(..., 0)` yaklaşımı process'leri temizledi ama production seviyesinde zombie/reap nüansına dikkat etmem gerekiyor.

---

# 👻 Eski Process'ler Arkada Kalmış

Bir deneyde main'i `Ctrl+C` ile kapatmıştım.

Sonra:

`pgrep -af 'child.py|grandchild.py'`

yaptığımda hâlâ child ve grandchild gördüm.

İlk düşüncem:

> Yeni timeout cleanup'ı çalışmamış.

Ama PID'leri kontrol edince bunların **eski çalıştırmadan kalan process'ler** olduğunu gördüm.

Bu da aslında bugünün konusunu gerçek şekilde kanıtladı:

> **Parent'ın ölmesi descendant'ların otomatik olarak ölmesini garanti etmiyor.**

Eski process group'u ayrıca temizledim.

---

# 🔬 Son Kanıt

Final testte runner:

1. child'ı başlattı
2. timeout'u tespit etti
3. process group'a TERM gönderdi
4. gerektiğinde KILL aşamasına geçti
5. direct child'ı wait/reap etti

Sonra:

`pgrep -af 'child.py|grandchild.py'`

çalıştırdım.

Hiçbir çıktı gelmedi.

Yani:

    child yok ✅
    grandchild yok ✅
    arkada kalan descendant yok ✅

---

# 🐞 Tek Debugging Vakası

Semptom:

> Main kapandı ama grandchild hâlâ yaşıyor.

Direkt:

> "Signal bozuk."

demem.

İlk hipotezim:

> Parent'ın ölmesi grandchild'ın otomatik ölmesini garanti etmiyor.

İlk ölçümler:

`pstree -p MAIN_PID`

ve:

`ps -o pid,ppid,pgid,sid,stat,cmd -p PIDLER`

Sorular:

    Grandchild gerçekten hâlâ yaşıyor mu?
    ↓
    PPID'si ne?
    ↓
    Hangi PGID'de?
    ↓
    Child ile aynı group'ta mı?
    ↓
    Runner bu group'u gerçekten hedefliyor mu?

Böylece problemi:

    identity
    tree
    process-group
    signal targeting

katmanlarına ayırabilirim.

---

# 🧯 Hata Avı

## 1. `Popen()` child bitene kadar parent'ı bekletir

TIRT.

`Popen()` başlatır ve geri döner.

Beklemek için `wait()` gerekir.

---

## 2. `wait()` child'ı öldürür

TIRT.

Child'ın tamamlanmasını bekler.

---

## 3. Parent ölürse bütün descendant'lar kesin ölür

TIRT.

Grandchild yaşamaya devam edebilir.

---

## 4. Process tree ile process group aynı şey

TIRT.

Tree parent-child ilişkisi.

Group birlikte signal/yönetim boundary'si.

---

## 5. Aynı parent altında olan her process farklı PGID'dedir

TIRT.

Group bilgisi miras alınabilir.

---

## 6. Runner ve workload'un aynı PGID'de olması her zaman sorun değildir

Timeout sırasında bütün workload group'una signal göndermek istiyorsam runner'ın da aynı grupta olması sıkıntı çıkarabilir.

---

## 7. `start_new_session=True` sadece isim değiştirme gibi bir şey

TIRT.

Yeni session/process-group boundary kurmamı sağlar.

---

## 8. `kill -TERM PID` bütün process tree'yi öldürür

TIRT.

Tek PID hedeflenir.

---

## 9. `kill -TERM -- -PGID` tek PID hedefler

TIRT.

Negatif hedef process group anlamına gelir.

---

## 10. `--` process group oluşturur

TIRT.

Sadece CLI option parsing'in bittiğini belirtir.

---

## 11. Timeout olunca `wait(timeout=...)` child'ı otomatik öldürür

TIRT.

Yalnız timeout bilgisini üretir.

Cleanup policy bana aittir.

---

## 12. TERM gönderdiğim anda bütün cleanup tamamlanmıştır

TIRT.

Process'in shutdown yapması zaman alabilir.

---

## 13. TERM işe yaramadıysa hemen KILL

TIRT.

Önce bir grace period vermek gerekir.

---

## 14. KILL de TERM gibi handler çalıştırabilir

TIRT.

SIGKILL handle edilemez.

---

## 15. Signal gönderince `wait()` gereksiz olur

TIRT.

Signal delivery ve child reap farklı lifecycle olaylarıdır.

---

## 16. `killpg(pgid, 0)` yaşıyor diyorsa kesin application hâlâ aktif çalışıyor

TIRT.

Zombie/reap gibi lifecycle detayları sonucu etkileyebilir.

---

## 17. `pgrep` sonucu gördüğüm her process yeni testime aittir

TIRT.

Eski çalıştırmalardan kalan process'ler olabilir.

PID ve process tree/group bilgisini kontrol etmeliyim.

---

# 🧠 Kafaya Kazı

> [!quote]
> `Popen()` process başlatır; beklemek ayrı karardır.

> [!quote]
> `wait()` child completion'ını bekler ve reap lifecycle'ıyla ilişkilidir.

> [!quote]
> Parent'ın ölmesi descendant'ların ölmesini garanti etmez.

> [!quote]
> PID tek process'i, PGID process group üyeliğini gösterir.

> [!quote]
> Process tree ile process group farklı yapılardır.

> [!quote]
> Runner ile workload arasında bilinçli lifecycle boundary kurmak gerekir.

> [!quote]
> `start_new_session=True` child tarafında yeni session/process group oluşturmak için güçlü bir araçtır.

> [!quote]
> Child group leader ise labda `PID == PGID == SID` olabilir.

> [!quote]
> `kill -TERM PID` tek process'i, negatif PGID group'u hedefler.

> [!quote]
> Timeout sadece süre dolması değildir; sonrasında uygulanacak policy de contract'ın parçasıdır.

> [!quote]
> Doğru escalation sırası: TERM -> grace -> gerekirse KILL.

> [!quote]
> Signal göndermek ile child'ı reap etmek farklı lifecycle aşamalarıdır.

> [!quote]
> Bir runner başlattığı process ağacının yaşam döngüsünün sahibi olmalıdır.

---

# 📌 30 Saniyelik Özet

    main
      ↓
    child
      ↓
    grandchild


    Popen
    -> process başlatır

    wait
    -> child bitene kadar bekler


    PID
    -> tek process

    PPID
    -> parent PID

    PGID
    -> process group

    SID
    -> session


    PROBLEM

    main + child + grandchild
    aynı PGID
    ↓
    group'a TERM
    ↓
    runner da signal alabilir


    ÇÖZÜM

    child = Popen(
        ...,
        start_new_session=True
    )

    main
    -> kendi group

    child + grandchild
    -> ayrı group


    SIGNAL

    kill -TERM PID
    -> tek process

    kill -TERM -- -PGID
    -> bütün process group


    TIMEOUT CONTRACT

    spawn
    ↓
    wait(timeout)
    ↓
    TimeoutExpired
    ↓
    TERM group
    ↓
    grace period
    ↓
    hâlâ bitmedi?
    ↓
    KILL group
    ↓
    wait / reap


    ANA PRENSİP

    Parent ölür
    !=
    bütün descendants ölür


    RUNNER

    yalnız process başlatmaz

    spawn
    wait
    timeout
    signal
    escalation
    cleanup
    reap

    lifecycle'ını yönetir

---

# ✅ Günün Kazanımları

- [x] `Popen()` ile `wait()` tekrar ayrıldı
- [x] Parent'ların neden erken bittiği anlaşıldı
- [x] Main -> child -> grandchild process tree kuruldu
- [x] `pstree` ile process ağacı doğrulandı
- [x] PID / PPID / PGID / SID aynı deneyde incelendi
- [x] Process tree ile process group ayrıldı
- [x] Child'ın parent process group'unu miras alabildiği görüldü
- [x] Grandchild'ın process group bilgisini child'dan alabildiği görüldü
- [x] Runner ile workload'un aynı PGID'de olmasının riski görüldü
- [x] `start_new_session=True` kullanıldı
- [x] Child + grandchild ayrı process group'a alındı
- [x] Child'ın group/session leader olduğu gözlemlendi
- [x] PID signal ile process-group signal ayrıldı
- [x] Negatif PGID kullanımı öğrenildi
- [x] `--` option parsing separator mantığı öğrenildi
- [x] Process group'a SIGTERM kontrollü olarak gönderildi
- [x] Main'in group signal almadan normal exit ettiği gözlemlendi
- [x] Tek child PID'sini öldürmenin neden yetersiz olabileceği öğrenildi
- [x] TERM -> grace -> KILL escalation modeli kuruldu
- [x] `wait(timeout=...)` ile timeout contract uygulandı
- [x] `TimeoutExpired` davranışı öğrenildi
- [x] Timeout'un process'i otomatik öldürmediği öğrenildi
- [x] `os.killpg()` ile Python'dan process group signal gönderildi
- [x] Signal delivery ile wait/reap ayrıldı
- [x] Eski çalıştırmadan kalan orphan/descendant process'ler gözlemlendi
- [x] Parent ölümünün descendant ölümünü garanti etmediği canlı olarak doğrulandı
- [x] `killpg(..., 0)` kontrolündeki zombie nüansı fark edildi
- [x] Daha temiz TERM -> timed wait -> KILL -> final wait modeli öğrenildi
- [x] `pgrep` ile cleanup sonrası leftover process kontrol edildi
- [x] Runner'ın yalnız spawn değil lifecycle ownership sorumluluğu taşıdığı oturdu

> [!success] 🚀 Gün sonu sonucu
> Bugün subprocess tarafındaki düşüncem:
>
>     "Process'i başlattım, görev tamam."
>
> seviyesinden çıktı.
>
> Artık bir child başlatınca şunları düşünmem gerekiyor:
>
>     Bu child kendi child'larını oluşturabilir mi?
>     ↓
>     Workload için ayrı bir process group gerekli mi?
>     ↓
>     Ne kadar bekleyeceğim?
>     ↓
>     Timeout olduğunda ne yapacağım?
>     ↓
>     TERM kime gidecek?
>     ↓
>     Ne kadar grace period vereceğim?
>     ↓
>     Kapanmazsa KILL uygulanacak mı?
>     ↓
>     Direct child'ı kim reap edecek?
>     ↓
>     Arkada descendant kaldı mı?
>
> Günün en kritik cümlesi:
>
> **Runner sadece child process'i başlatan program değildir; başlattığı işin process-group, timeout, signal, escalation ve reap yaşam döngüsünün sahibidir.**