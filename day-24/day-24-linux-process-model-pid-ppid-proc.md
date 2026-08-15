---
title: "Gün 24 — Linux Process Modeli, PID/PPID, ps, pgrep, pstree ve /proc"
tags:
  - coreops
  - linux
  - process
  - pid
  - ppid
  - ps
  - pgrep
  - pstree
  - proc
  - cpu
  - rss
aliases:
  - "Gün 24 Linux Process Modeli PID PPID ve proc"
status: completed
---

# Gün 24 — Linux Process Modeli, PID/PPID, `ps`, `pgrep`, `pstree`, `/proc`, CPU & RSS

## Ana Zihinsel Model

Bugün öğrendiğim en önemli şey şu:

> Bir process'i debug ederken rastgele komut çalıştırmak yerine önce **hangi soruya cevap aradığımı** belirlemeliyim.

Farklı araçlar farklı sorulara cevap veriyor:

| Araç / Kaynak | Temel soru |
|---|---|
| `pgrep` | Adını bildiğim process'in PID'si ne? |
| `ps` | Bu process kim, parent'ı kim, state/resource durumu ne? |
| `pstree` | Kim kimi oluşturmuş? Process hiyerarşisi nasıl? |
| `/proc/<PID>` | Kernel bu process hakkında hangi detaylı runtime bilgilerini tutuyor? |

---

# 1. Program ile Process Arasındaki Fark

**Program**, diskte duran çalıştırılabilir kod veya script'tir.

**Process**, o programın çalışan bir instance'ıdır.

Örneğin:

`process.py`

diskte duran bir dosyadır.

Ama:

`python process.py`

çalıştırdığımda artık çalışan bir **Python process'i** oluşur.

Aynı programı iki kez çalıştırırsam:

- aynı executable kullanılabilir,
- aynı script kullanılabilir,
- ama iki ayrı process oluşur,
- PID'leri farklı olur,
- runtime state'leri farklı olabilir.

### Kafama kazınacak

> Program = kod  
> Process = o kodun çalışan instance'ı

---

# 2. PID ve PPID

## PID

**PID (Process ID)** process'in kernel tarafından verilen sayısal kimliğidir.

Şu soruyu cevaplar:

> **Bu process hangisi?**

PID'yi önceden kesin tahmin edemem. Kernel atar.

Ayrıca PID kalıcı bir kimlik değildir. Process bittikten sonra aynı sayı gelecekte başka bir process için tekrar kullanılabilir.

---

## PPID

**PPID (Parent Process ID)** process'i oluşturan parent process'in PID'sidir.

Şu soruyu cevaplar:

> **Bu process'i kim oluşturdu?**

Labda örneğin:

`zsh → python`

ilişkisini gördüm.

Python'ın:

`PPID = zsh'ın PID'si`

oldu.

### PID ve PPID hangi iki farklı soruyu cevaplar?

- **PID → “Bu process kim?”**
- **PPID → “Bu process'in parent'ı kim?”**

---

# 3. Controlled Process Lab

İlk olarak uzun yaşayan ama CPU'yu boşuna sömürmeyen bir Python process oluşturdum.

Mantık:

`while True` ile process hayatta kalıyor.

`time.sleep(5)` ile çoğunlukla bekliyor.

Burada ilk hatam `sleep()`'i doğrudan kullanmaya çalışmaktı.

`NameError` aldım çünkü `sleep` kendiliğinden tanımlı değildi.

Sonra `time.sleep()` yazdım ama argüman vermedim:

`TypeError`

aldım.

Doğru zihinsel model:

`time.sleep(5)`

→ mevcut Python process'ini 5 saniye bekletir.

---

## Process State Tahminindeki Hatam

İlk tahminim:

> process state = running

idi.

Bu **yanlıştı**.

Process zamanının çoğunu `sleep()` içinde geçirdiği için beklediğimiz state:

`S`

yani **sleeping**.

Ölçümde:

`S+`

gördüm.

- `S` → sleeping
- `+` → foreground process group içinde

### `+` ne demek?

Process bağlı olduğu terminalde foreground job'ın parçası.

Örneğin terminalde `python process.py` çalışırken shell prompt'u geri gelmiyorsa Python terminalin foreground tarafında çalışıyor.

---

# 4. Process Name: `python` mı `process.py` mi?

Başta process name'in dosya adı olabileceğini düşündüm.

Burada önemli ayrım:

`python process.py`

içinde:

- `python` → çalışan executable/interpreter
- `process.py` → Python'a verilen argüman/script

Bu yüzden:

`comm` → `python`

gördüm.

Ama:

`args` → `python process.py`

gösterdi.

### Kafama kazınacak

`comm`:

> Hangi executable/process adı?

`args`:

> Nasıl ve hangi argümanlarla çalıştırılmış?

Örneğin:

`python server.py`

ve:

`python process.py`

process'lerinin `comm` değeri ikisinde de `python` olabilir.

Sadece `comm` ile hangi script olduğunu ayıramam.

---

# 5. `ps` ile Özel Alan Seçme

Başta düz `ps` çalıştırdığımda başka terminaldeki Python process'i görünmedi.

Burada öğrendiğim:

> Düz `ps` her zaman sistemdeki bütün process'leri göstermez.

Belirli PID için:

`ps -p <PID>`

kullanabilirim.

Çıktıda istediğim alanları kendim seçmek için:

`-o`

kullanılır.

`o`yu **output** diye hatırlıyorum.

Örneğin kullandığım alanlar:

`pid,ppid,stat,comm`

### Alanlar

- `pid` → process kimliği
- `ppid` → parent PID
- `stat` → process state
- `comm` → process adı
- `args` → full command/arguments
- `%cpu` → CPU kullanımı
- `rss` → resident memory

Bir hatam da:

`ps -o ppid`

çalıştırıp Python'ın PPID'sini göreceğimi sanmaktı.

Burada **hangi process'i istediğimi belirtmemiştim**.

Doğru zihinsel model:

> `-p` → kimi inceleyeceğim?  
> `-o` → onun hakkında ne görmek istiyorum?

---

# 6. `pgrep`

`pgrep` şu durumda çok işe yarıyor:

> Process'in adını biliyorum ama PID'sini bilmiyorum.

Örneğin:

`pgrep python`

ile çalışan `python` process'lerini buldum.

İlk typo'm:

`psgrep python`

yazmaktı.

`psgrep` diye bir araç yok; doğru araç `pgrep`.

---

## Birden Fazla PID Dönmesi

İkinci terminalden aynı Python script'ini tekrar çalıştırdım.

Sonra `pgrep python` iki PID döndürdü.

Bu bir bug değildi.

Çünkü:

> Aynı executable'dan birden fazla ayrı process instance çalışabilir.

İkisi de `python` adını taşıyordu ama PID'leri farklıydı.

### `pgrep` ile `ps` hangi durumda farklı fayda sağlar?

**`pgrep`:**

> “Adını biliyorum ama PID'yi bilmiyorum.”

**`ps`:**

> “PID'yi/process'i buldum; şimdi PID, PPID, state, CPU, RSS, command gibi özelliklerini incelemek istiyorum.”

Yani:

> `pgrep` = discovery  
> `ps` = inspection

---

# 7. Parent–Child Process Modeli

Controlled olarak şu ağacı oluşturmak istedim:

`zsh`
→ `python`
→ `sleep`

Python parent process içinde child oluşturmak için:

`subprocess`

modülünü kullandım.

---

## `run()` vs `Popen()`

İlk olarak `run()` seçtim.

Ama bu lab için `Popen()` daha uygundu.

`Popen()`:

- child process başlatır,
- parent'a kontrolü geri verir,
- child process nesnesini/PID'sini takip etmeyi kolaylaştırır.

---

## `time.sleep()` ile Linux `sleep` Aynı Şey Değil

Bu ayrım çok önemli.

`time.sleep(5)`:

> mevcut Python process'ini uyutur.

Yeni process oluşturmaz.

Ama `Popen()` ile Linux'taki `sleep` executable'ını başlatırsam:

> ayrı bir child process oluşur.

---

## `Popen` Hatalarım

İlk düşüncem:

`subprocess.Popen(sleep, 60)`

gibi bir şeydi.

Yanlıştı.

Program ve argüman tek command-list içinde verilmeliydi.

Ayrıca:

`sleep`

Python değişkeni değil, executable adı olduğu için string olmalı.

`60` da child programa verilen argüman olduğu için string olarak geçirildi.

Bir diğer ciddi hata:

`Popen()` çağrısını `while True` içine koymuştum.

Bu yapılırsa Python:

> child oluştur → child oluştur → child oluştur → ...

diye sürekli yeni process spawn eder.

Bu labda istediğim:

> **1 parent + 1 child**

idi.

Bu yüzden child bir kere oluşturuldu.

---

## `wait()`

Python parent hemen sonlanırsa process ağacını inceleyemem.

Bu yüzden child process nesnesi üzerinde:

`wait()`

kullanıldı.

Mantık:

> Parent, child process bitene kadar bekliyor.

---

## `pstree`

Tahmin ettiğim yapı:

`zsh`
→ `python`
→ `sleep`

İlk sefer `pstree` ile baktığımda sadece `zsh` gördüm.

Sebep araçta hata olması değildi.

`sleep 60` bitmişti.

Sonra:

- `sleep` bitmiş,
- `wait()` dönmüş,
- Python'da başka iş kalmamış,
- Python da bitmişti.

Yani process tree'yi yakalamaya geç kalmıştım.

Süreyi uzatınca gerçek ağaç:

`zsh → python → sleep`

olarak görüldü.

Bir üst katmanda terminal emulator'ü de gördüm:

`qterminal → zsh → python → sleep`

---

## PID/PPID ile İkinci Kanıt

`pstree` görsel kanıttı.

Sonra `sleep` process'i için:

`PID` ve `PPID`

alanlarını ölçtüm.

`sleep PPID = python PID`

çıktı.

Böylece parent-child ilişkisini iki farklı şekilde kanıtladım:

1. `pstree`
2. `ps` ile PID/PPID

### Kafama kazınacak

> PPID rastgele bir metadata değildir; process hiyerarşisini temsil eder.

---

# 8. `/proc/<PID>`

`/proc/<PID>` normal bir disk klasörü/arşivi gibi düşünülmemeli.

Kernel'in yaşayan process hakkındaki runtime bilgisini kullanıcı alanına sunduğu **pseudo-filesystem görünümüdür**.

Labdaki Python process için `/proc/<PID>` altına baktım.

---

## `exe`

`exe` çalışan executable'a giden symlink.

Labda:

`exe -> /usr/bin/python3.13`

gibi gerçek Python executable yolunu gördüm.

---

## `cmdline`

Process'in nasıl çağrıldığını gösteriyor.

Burada:

`python process.py`

bilgisi vardı.

Düz `cat` ile bakarken kelimelerin yapışık görünmesinin sebebi:

> argümanların boşluk değil NUL (`\0`) karakterleriyle ayrılması.

Bir ara:

`cd cmdline`

denedim.

Bu yanlıştı çünkü `cmdline` directory değil, pseudo-file.

---

## `status`

Process hakkında insan tarafından daha rahat okunabilir runtime bilgiler verdi.

Örneğin:

- `Name`
- `State`
- `Pid`
- `PPid`
- `VmRSS`

gördüm.

Burada önce `stat` ile `status` arasında düşündüm.

Bu görev için `status` daha okunabilir olanıydı.

---

## `cwd`

`cwd`, process'in current working directory'sine symlink.

Labda:

`cwd -> /home/polat/process_lab`

gördüm.

---

## `/proc` neden production debugging'de değerlidir?

`ps` bana hızlı ve işlenmiş bir özet verir.

Ama bazen şunların daha detaylı kanıtını isterim:

- gerçek executable tam olarak hangisi?
- process hangi argümanlarla çalıştırılmış?
- current working directory neresi?
- process state tam olarak ne?
- memory bilgileri ne?
- environment/file descriptor gibi runtime bilgiler ne?

Bu durumda `/proc/<PID>` daha derin ikinci kanıt sağlar.

Ben ilk başta:

> "`/proc/<PID>` kernel dizini"

diye tarif etmiştim.

Bu yeterince doğru değildi.

Daha doğru ifade:

> `/proc/<PID>`, kernel'in process hakkındaki runtime bilgisini kullanıcı alanına sunduğu pseudo-filesystem görünümüdür.

### Zihinsel model

> `ps` = summary  
> `/proc/<PID>` = daha detaylı kernel-backed runtime evidence

---

# 9. CPU ve RSS

İki process'i karşılaştırdım.

## Düşük aktiviteli process

`process.py`

çoğunlukla `sleep()` yapıyordu.

Ölçüm yaklaşık:

`STAT = S+`

`%CPU = 0.0`

`RSS = 12348 KiB`

---

## CPU ağırlıklı process

Bir değişkeni sonsuz döngü içinde sürekli artıran process oluşturdum.

`sleep()` yoktu.

İlk başta `print()` bırakmıştım.

Bu deney için iyi değildi çünkü artık sadece CPU değil, terminal I/O da oluşturuyordum.

Saf CPU testi için:

> sonsuz hesaplama var, `sleep` yok, `print` yok.

Ölçüm yaklaşık:

`STAT = R+`

`%CPU = 99.9`

`RSS = 9000 KiB`

---

## Buradan Çıkardığım Sonuç

CPU process:

> yaklaşık `%99.9 CPU`

kullanmasına rağmen RSS'si diğer Python process'ten daha düşüktü.

Bu, önemli bir şeyi doğrudan deneyle gösterdi:

> **Yüksek CPU kullanımı otomatik olarak yüksek RAM kullanımı anlamına gelmez.**

CPU ve memory iki farklı resource eksenidir.

---

# 10. RSS Nedir?

**RSS (Resident Set Size)** process'in şu anda fiziksel RAM'de resident bulunan memory miktarı hakkında fikir verir.

Ama:

> RSS yüksek = memory leak

demek **yanlıştır**.

Örneğin bir database process'i doğal olarak birkaç GB RAM kullanıyor ve bu seviyede stabil kalıyor olabilir.

Memory leak için daha önemli olan **trend**.

Örneğin aynı workload tekrarlandıkça:

`200 MB → 350 MB → 500 MB → 700 MB → 1 GB → ...`

şeklinde sürekli büyüyor,

ve:

- anlamlı şekilde geri düşmüyor,
- plateau'ya oturmuyor,
- workload ile açıklanamıyorsa

memory leak hipotezim güçlenir.

### RSS yüksekliği neden tek başına memory leak kanıtı değildir?

Çünkü tek bir RSS ölçümü sadece process'in o andaki resident memory miktarını gösterir.

Leak diyebilmek için en azından:

- zaman içindeki RSS trendine,
- aynı workload tekrarlandığında ne olduğuna,
- workload bittikten sonra memory davranışına,
- gerekirse heap/object seviyesindeki ölçümlere

bakmam gerekir.

### Kafama kazınacak

> High RSS ≠ memory leak.

> Aynı workload tekrarlandıkça RSS sürekli büyüyor, anlamlı şekilde geri düşmüyor ve plateau yapmıyorsa leak hipotezim güçlenir.

---

# 11. Process Exit ve `/proc`

Yaşayan process'in PID'sini aldım.

Process'i `Ctrl+C` ile kapattım.

Sonra eski:

`/proc/<PID>`

yoluna baktım.

Sonuç:

`No such file or directory`

Bu beklenen davranıştı.

Çünkü `/proc/<PID>` process history arşivi değildir.

> Process'in runtime varlığına bağlı canlı bir görünümüdür.

Process ortadan kalkınca ilgili `/proc/<PID>` görünümü de ortadan kalkar.

---

# 12. PID Reuse ve Stale PID

Bir process öldüğü zaman PID'si sonsuza kadar ona ayrılmış kalmaz.

Örneğin bugün:

`36514 → python`

olabilir.

Process öldükten sonra gelecekte:

`36514 → başka bir process`

olabilir.

Buna **PID reuse** denir.

Bu yüzden:

> “Logumda PID 36514 vardı ve sistemde şimdi de PID 36514 var, demek ki aynı process.”

demek güvenli değildir.

Bu bir **stale assumption** olabilir.

Daha güçlü identity kanıtları:

- PID
- executable
- `cmdline` / `args`
- process start time
- gerekirse başka runtime metadata

birlikte kullanılmalıdır.

---

# 13. Ayırıcı Debugging Incident

Incident:

> Uygulamanın hâlâ çalıştığını düşünüyorum çünkü elimde eski PID var fakat beklenen işi yapmıyor.

İlk hipotezlerim:

- `wait()` içinde olabilir,
- zombie olabilir,
- başka process bekliyor olabilir.

Bunlar tamamen saçma değildi ama hipotezlerimin çoğu aynı **waiting/state ailesine** yığılmıştı.

Daha iyi ve birbirinden ayrılan hipotezler:

### H1 — Process ölmüş, elimdeki PID stale

Katman:

**Lifecycle**

---

### H2 — PID reuse edilmiş ve artık başka process'e ait

Başta bunu:

> process hierarchy

diye sınıflandırdım.

Bu yanlıştı.

Doğrusu:

**Process identity**

Çünkü soru:

> “Bu PID'nin parent'ı kim?”

değil.

Soru:

> “Bu PID hâlâ aynı process'e mi ait?”

---

### H3 — Doğru process yaşıyor ama çalışmıyor/bekliyor

Örneğin:

- `S`
- `D`
- `Z`
- başka bir runtime wait/block durumu

Katman:

**State / runtime behaviour**

---

# 14. En Küçük Ayırıcı Deney

Debugging sırasında hemen bütün araçları çalıştırmak yerine hipotezleri en ucuz şekilde ayırmalıyım.

İlk soru:

> PID hâlâ var mı?

Bunun için:

`ps -p <PID>`

yeterli olabilir.

### Hiç çıktı yoksa

H1 güçlenir:

> process ölmüş, PID stale.

### PID varsa

Henüz:

> “Aynı process.”

diyemem.

PID reuse olabilir.

Bu yüzden devamında:

`comm,args,stat`

alanlarına bakabilirim.

- `comm` → process adı
- `args` → gerçekten hangi command/script
- `stat` → state

Böylece:

### Bambaşka executable/args varsa

→ H2: **PID reuse**

### Aynı process fakat `S`, `D`, `Z` vb. varsa

→ H3: **state/runtime problemi**

---

# 15. Neden `pstree` ile Başlamadım?

Başta semptom:

> “Eski PID hâlâ doğru process'e mi ait ve neden iş yapmıyor?”

Burada ilk ihtiyacım:

> “Anası babası kim?”

değil. :)

`pstree` daha çok:

> parent-child hierarchy nedir?

sorusunu cevaplar.

Benim incident'ımda önce identity/lifecycle/state çözülmeliydi.

Bu yüzden `pstree` ile başlamak:

> **yanlış katmandan kanıt toplamak**

olurdu.

---

# Final Soru-Cevap

## Program ile process arasındaki fark nedir?

Program diskte duran executable/koddur. Process ise bu programın çalışan runtime instance'ıdır. Aynı program aynı anda birden fazla ayrı process oluşturabilir.

---

## PID ve PPID hangi iki farklı soruyu cevaplar?

**PID:**

> “Bu process hangisi?”

**PPID:**

> “Bu process'in parent'ı kim?”

---

## `pgrep` ile `ps` hangi durumda farklı fayda sağlar?

`pgrep`:

> Process'in adını biliyorum ama PID'sini bilmiyorum.

`ps`:

> Process/PID belli; PID, PPID, state, CPU, RSS, command gibi özelliklerini incelemek istiyorum.

Kısaca:

> `pgrep` → bul  
> `ps` → incele

---

## `/proc` neden production debugging'de değerlidir?

Çünkü `ps` gibi araçların verdiği özetin arkasına geçip process'in:

- executable,
- command line,
- CWD,
- state,
- memory,
- file descriptor,
- environment

gibi daha detaylı runtime bilgilerini kernel-backed bir görünümden inceleyebilirim.

Özellikle bir gözlemi **ikinci bağımsız kanıtla doğrulamak** için çok değerlidir.

---

## RSS yüksekliği neden tek başına memory leak kanıtı değildir?

Çünkü yüksek RSS normal workload, cache veya uygulamanın doğal memory ihtiyacından kaynaklanabilir.

Memory leak şüphesini güçlendiren asıl şey:

> aynı workload tekrarlandıkça memory'nin kontrolsüz şekilde büyümesi, anlamlı şekilde geri düşmemesi ve bir plateau'ya oturmamasıdır.

Tek snapshot değil, **zaman içindeki trend** önemlidir.

---

# Bugünkü Hatalarım

1. Process state'i ilk başta `running` tahmin ettim.  
   → `sleep()` ağırlıklı process çoğunlukla `S` durumunda olur.

2. Process name'in script adı olabileceğini düşündüm.  
   → `comm` tarafında executable/interpreter (`python`) görünür; script `args/cmdline` tarafındadır.

3. Parent olarak `bash` tahmin ettim.  
   → Gerçek shell'im `zsh` çıktı. Tahmin yerine ortamı ölçmek gerekiyor.

4. `psgrep` yazdım.  
   → Doğrusu `pgrep`.

5. `ps -o ppid` ile direkt hedef process'in PPID'sini alacağımı düşündüm.  
   → `-p` ile hangi process'i inceleyeceğimi de seçmeliyim.

6. Process adını bulmak isterken `stat` düşündüm.  
   → `stat` state; `comm` process adı.

7. Python sleep için `os` düşündüm.  
   → `time.sleep()` kullanılır.

8. `time.sleep()` içine süre vermeyi unuttum.  
   → Süre argümanı gerekiyor.

9. `subprocess.Popen(sleep, 60)` gibi düşündüm.  
   → Program ve argüman command list olarak ve string biçiminde verilmeliydi.

10. `Popen()` çağrısını `while True` içine koydum.  
    → Her döngüde yeni child spawn edecekti.

11. `pstree` ile bakmaya geç kaldım.  
    → `sleep 60` bitmiş, ardından Python parent da bitmişti.

12. `ps` ile Python'ın PPID'sini doğrulayıp parent-child deneyinin tamamlandığını sandım.  
    → Asıl kontrol `sleep PPID == python PID` ilişkisiydi.

13. CPU testinde `print()` bıraktım.  
    → CPU deneyine terminal I/O karıştırıyordu.

14. `/proc/<PID>` için “kernel dizini” dedim.  
    → Daha doğrusu kernel-backed pseudo-filesystem/runtime görünümü.

15. PID reuse problemini process hierarchy olarak sınıflandırdım.  
    → Bu hierarchy değil, **process identity** problemidir.

---

# Günün Final Zihinsel Modeli

`program`
→ diskteki kod

`process`
→ kodun çalışan instance'ı

`PID`
→ bu process kim?

`PPID`
→ parent kim?

`pgrep`
→ adı biliyorum, PID'yi bul

`ps`
→ process hakkında seçilmiş özet bilgiyi ölç

`pstree`
→ process ilişkilerini/hiyerarşisini gör

`/proc/<PID>`
→ process'in daha ayrıntılı kernel-backed runtime görünümü

`STAT`
→ process şu an ne yapıyor?

`%CPU`
→ CPU zamanını ne kadar tüketiyor?

`RSS`
→ ne kadar resident memory tutuyor?

`PID reuse`
→ PID process'in sonsuza kadar değişmeyen kimliği değildir

`debugging`
→ önce hipotez kur, sonra en küçük ayırıcı ölçümü yap

## En önemli ders

> Araç ezberlemem değil, **hangi soruya hangi araçla kanıt toplayacağımı bilmem** gerekiyor.