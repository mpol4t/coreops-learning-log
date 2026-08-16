---
title: "Gün 25 — Linux Signals, Graceful Shutdown, Job Control, Wait ve Docker PID 1"
tags:
  - coreops
  - linux
  - process
  - signals
  - sigterm
  - sigkill
  - job-control
  - wait
  - lifecycle
  - docker
  - pid1
  - graceful-shutdown
aliases:
  - "Gün 25 Linux Signals Job Control Wait ve Docker PID 1"
status: completed
---

# 🧠 Gün 25 — Linux Signals, Graceful Shutdown, Job Control, `wait` ve Docker PID 1

> [!abstract] 🎯 Ana fikir  
> Bugün birbirinden ayrı sandığım birkaç konu aslında aynı process lifecycle modelinde birleşti:
> 
> ```
> SIGNAL
> → çalışan process'e olay bildir
> 
> JOB CONTROL
> → shell'in process/process-group çalışmalarını yönetmesi
> 
> WAIT
> → parent'ın child completion'ını beklemesi ve exit status tarafını toplaması
> 
> DOCKER PID 1
> → container'ın ana process'i ve signal delivery sınırı
> ```
> 
> En kritik düşünme zincirim artık:
> 
> ```
> Signal'ı kim üretti?
> ↓
> Hedef kim?
> ↓
> Hangi signal?
> ↓
> Hedefe ulaştı mı?
> ↓
> Disposition ne?
> ↓
> Handler çalıştı mı?
> ↓
> Shutdown state değişti mi?
> ↓
> Cleanup yapıldı mı?
> ↓
> Process nasıl sonlandı?
> ```

---

# ⚡ D+3 Retrieval — Process Tarafı

## PID bana neyi kanıtlar?

PID:

> O anda yaşayan belirli bir process'in kernel tarafından verilen process kimliğidir.

Tek başına şunları kanıtlamaz:

```
Process'in adı ne?
Ne çalıştırıyor?
State'i ne?
Parent'ı kim?
Ne kadar RAM kullanıyor?
```

Bunları ayrıca gözlemlemem gerekir.

---

# Eski PID'ye Neden Güvenmem?

PID'ler zaman boyunca sonsuza kadar eşsiz değildir.

```
PID 1010
→ Process A
→ Process A öldü
→ PID serbest kaldı
→ Daha sonra Process B
→ PID 1010
```

olabilir.

Dolayısıyla:

> **Eski PID = aynı process**

diye varsayamam.

---

# `pgrep` vs `ps`

Bunlar aynı soruyu cevaplamaz.

```
pgrep
→ belirli bir isim/pattern'e uyan process kimliklerini bulmaya yarar

ps
→ process'ler hakkında snapshot halinde bilgi gösterir
```

Kaynak geri çağırmada `pgrep`, `ps`, `pstree` ve PPID kanıtları bu şekilde ayrılmış.

---

# Parent-Child İlişkisini Nasıl Kanıtlamıştım?

İki bağımsız gözlem:

```
pstree -p
```

→ process ağacını gör.

ve:

```
ps -p CHILD_PID -o pid,ppid,command
```

→ child'ın gerçek PPID'sini gör.

Sonra PPID'yi ayrıca sorgulayarak parent'ı doğrulayabilirim.

---

# RSS Yüksek → Memory Leak mi?

Hayır.

Yüksek RSS yalnızca process'in o anda ciddi miktarda resident memory kullandığını gösterebilir.

Örneğin doğal olarak çok RAM isteyen bir uygulamada RSS sürekli yüksek olabilir.

Daha şüpheli davranış:

```
zaman
↓
RSS
100 MB
200 MB
400 MB
800 MB
...
```

şeklinde açıklanamayan büyüme olabilir.

Ama:

> **Sürekli artış bile tek başına memory leak'in kesin ispatı değildir; yalnız güçlü bir şüphe üretir.**

---

# 📡 Linux Signal Nedir?

Signal:

> Bir process'e veya process group'a bir olay meydana geldiğini bildiren asenkron mekanizmadır.

Signal yalnızca:

```
“process öldür”
```

mekanizması değildir.

Bir signal:

- process'i terminate ettirebilir,
    
- stop ettirebilir,
    
- devam ettirebilir,
    
- custom handler çalıştırabilir,
    
- ignore edilebilir.
    

Kaynak teoride signal sonucu terminate dışında stop/continue/handler gibi davranışların da mümkün olduğu özellikle ayrılmış.

---

# 🧠 Signal İçin Ana Debugging Modelim

```
1. Signal'ı KİM üretti?
          ↓
2. HEDEF kim?
   process mi?
   process group mu?
          ↓
3. Hangi SIGNAL?
          ↓
4. Signal delivery gerçekleşti mi?
          ↓
5. Disposition ne?
   default / ignore / handler
          ↓
6. Handler varsa ne yaptı?
          ↓
7. Cleanup gerçekleşti mi?
          ↓
8. Son lifecycle sonucu ne?
   exit / stop / continue / çalışmaya devam
```

Bu modeli kullanınca:

```
Ctrl+C
kill
job control
docker stop
```

aynı altyapının farklı kullanımları hâline geliyor.

---

# 🎛️ Signal Disposition

Bir signal geldiğinde process'in o signal için davranış şekline **signal disposition** diyebilirim.

Temelde:

```
DEFAULT
IGNORE
CUSTOM HANDLER
```

---

## Default

Kernel ilgili signal'ın varsayılan davranışını uygular.

---

## Ignore

Process signal'a özel olarak tepki vermez.

---

## Handler

Programcı kendi davranışını tanımlar.

Örneğin:

```
SIGTERM
↓
handler
↓
shutdown requested
↓
yeni iş alma
↓
mevcut işi tamamla
↓
cleanup
↓
exit
```

> [!important]  
> Cleanup'ı signal yapmaz.
> 
> **Cleanup uygulamanın shutdown tasarımıdır.**

---

# 📬 Generated → Pending → Delivered

Signal lifecycle içinde üç ayrı kavram:

```
Generated
→ signal oluşturuldu

Pending
→ oluşturuldu ama henüz process tarafından işlenmedi

Delivered
→ target tarafından işlenmek üzere teslim edildi
```

Bu yüzden:

> **“Signal gönderdim” ≠ “handler kesin çalıştı.”**

Arada:

- targeting,
    
- blocking,
    
- delivery,
    
- disposition
    

katmanları bulunabilir.

---

# 🟡 SIGTERM

Kafamdaki kısa anlamı:

> **“Düzgün şekilde kapanmanı istiyorum.”**

SIGTERM'in default davranışı termination olabilir ama program handler tanımlayabilir.

Örneğin:

```
SIGTERM
↓
handler
↓
shutdown state
↓
yeni request alma
↓
mevcut requestleri bitir
↓
buffer/file/socket/DB cleanup
↓
exit
```

---

# ⚠️ `kill -TERM PID` = Graceful Shutdown Değil

Bu çok kritik.

```
kill -TERM PID
```

yalnızca:

> **SIGTERM isteğini gönderir.**

Graceful shutdown:

```
SIGTERM
+
uygun handler
+
uygun application shutdown logic
+
cleanup
+
controlled exit
```

sonucudur.

Kaynak controlled signal lab'ın en önemli sonucu da bu olmuş.

---

# 🟠 SIGINT

SIGINT:

> **Interrupt**

Terminalde klasik kaynak:

```
Ctrl+C
↓
terminal driver
↓
SIGINT
↓
foreground process group
```

Burada kritik kelime:

> **process group**

Ctrl+C'nin modeli yalnız:

```
tek PID
```

değildir.

Bir foreground pipeline birden fazla process içeriyorsa terminal foreground process group'a signal üretebilir.

---

# 🔴 SIGKILL

SIGKILL çok farklı.

Process:

```
SIGKILL'ı catch edemez
ignore edemez
block edemez
handler çalıştıramaz
```

Akış:

```
SIGKILL
↓
kernel
↓
process doğrudan terminate
```

---

# SIGKILL İçin Yaptığım İfade Düzeltmesi

İlk düşüncem:

> “Program handler'a yetişemeden kapandı.”

Bu tam doğru teknik ifade değil.

Doğrusu:

> **SIGKILL için uygulama handler'ının çalışma ihtimali zaten yoktur.**

Yani mesele:

```
handler yavaştı
```

değil.

Handler devreye giremez.

Kaynak karşıt vakada bu ifade özellikle düzeltilmiş.

---

# ⚖️ SIGTERM vs SIGKILL

|Özellik|SIGTERM|SIGKILL|
|---|---|---|
|Uygulama handle edebilir|Evet|Hayır|
|Ignore edilebilir|Olabilir|Hayır|
|Graceful shutdown fırsatı|Var|Yok|
|Application cleanup|Yapılabilir|Güvenilemez|
|Amaç|Kontrollü kapanış talebi|Zorla termination|

Kafamdaki kısa model:

```
SIGTERM
→ “Kapanışı sen yönetebilirsin.”

SIGKILL
→ “Artık kapanışı sen yönetmiyorsun.”
```

---

# 🧹 Cleanup Nedir?

Cleanup Python'a özgü özel bir komut değil.

Program kapanmadan önce:

- buffer flush,
    
- dosya kapatma,
    
- socket kapatma,
    
- DB connection bırakma,
    
- transaction tamamlama/rollback,
    
- lock bırakma,
    
- temporary file temizleme,
    
- child process yönetme
    

gibi yaptığı düzenli kapanış işlemlerinin genel adı.

---

# `cleanup.log` Gerçek Cleanup mı?

Hayır.

Labda:

```
cleanup.log
→ “cleanup aşamasına ulaştım”
```

kanıtı olarak kullandım.

Bu bir **kanıt artifact'i**.

Gerçek production cleanup'ın kendisi olmak zorunda değil.

Kaynak notta bu ayrım açıkça yapılmış.

---

# 🐍 Controlled Signal Lab

Kullandığım temel state:

```
stop_request = False
```

Handler:

```
SIGTERM geldi
↓
stop_request = True
```

Ana loop:

```
stop_request False
→ çalışmaya devam et

stop_request True
→ loop'tan çık
```

Sonra cleanup ve normal program sonu.

---

# 🧠 Handler'ı Küçük Tutmak

İki model düşündüm.

## Model A

```
SIGTERM
→ handler
→ bütün cleanup
→ exit
```

## Model B

```
SIGTERM
→ handler shutdown state değiştirir
→ main loop state'i fark eder
→ normal flow
→ cleanup
→ exit
```

Lab için Model B daha temizdi.

Handler:

> **“Shutdown istendi.”**

bilgisini iletiyor.

Ana program:

> **“Shutdown nasıl yapılacak?”**

politikasını yürütüyor.

---

# Handler Registration vs Handler

Bunları başta birbirine karıştırdım.

## Handler

> Signal geldiğinde ne yapılacak?

## Registration

> Hangi signal hangi handler'a bağlı?

Örneğin:

```
signal.signal(signal.SIGTERM, handler)
```

şunu kurar:

```
SIGTERM
→ handler
```

Handler'ın içinde tekrar `signal.signal()` çağırmam gerekmez.

---

# `signum` ve `frame`

Python signal handler'a parametreleri kendisi verir.

```
signum
→ hangi signal geldi?

frame
→ signal geldiği sıradaki execution frame bilgisi
```

Ben handler'ı manuel çağırırken vermiyorum.

---

# `global` Hatası

TIRT:

```
global stop_request = True
```

Doğru model:

```
global stop_request
→ Bu isim dış scope'taki global değişkeni ifade ediyor.

stop_request = True
→ Gerçek assignment.
```

`global` değer atamaz.

Scope davranışını bildirir.

---

# Kod Sırası Hatası

Python yukarıdan aşağı ilerliyor.

Şöyle yazarsam:

```
stop_request = False
↓
sonsuz loop
↓
handler definition
```

program handler tanımına hiç ulaşmayabilir.

Doğru lifecycle:

```
imports
↓
state
↓
handler definition
↓
signal registration
↓
PID bilgisi
↓
running
↓
main loop
↓
cleanup
↓
exit
```

---

# PID'yi Loop İçinde Almama Gerek Yok

Bir process yaşadığı sürece PID'si değişmez.

Dolayısıyla:

```
pid = os.getpid()
```

başlangıçta bir kere yeterli.

Bu PID üzerinden başka terminalden exact process'i gözlemlemek:

```
ps -p PID ...
```

çok daha güçlü kanıt.

---

# 🧪 SIGTERM Deneyinin Kanıtları

Program:

```
PID: 33748
STATE: Running
```

çıktısını verdi.

Başka terminal:

```
ps -p 33748 -o pid,comm,stat,args
```

→ process vardı.

Sonra:

```
kill -TERM 33748
```

Gönderildi.

Tekrar:

```
ps -p 33748
```

→ process artık yok.

Ardından:

```
cat cleanup.log
```

→

```
Cleanup yapıldı!
```

Kaynak deneyde process'in kaybolması ve cleanup artifact'i iki bağımsız kanıt olarak kullanılmış.

---

# ✅ Bu Deney Ne Kanıtladı?

```
SIGTERM üretildi
↓
doğru PID hedeflendi
↓
handler çalıştı
↓
shutdown state değişti
↓
main loop bitti
↓
cleanup path çalıştı
↓
normal program sonu
↓
process process tablosundan çıktı
```

---

# 🧪 SIGKILL Karşı Deneyi

Eski `cleanup.log` önce silindi.

Bu önemli çünkü:

```
eski artifact
→ yeni deneyde false positive
```

üretebilirdi.

Program başladı:

```
PID: 38528
```

Process:

```
ps -p 38528
```

ile doğrulandı.

Sonra:

```
kill -KILL 38528
```

Process artık yoktu.

Ama:

```
cleanup.log
```

oluşmadı.

Kaynak karşı deney doğrudan SIGTERM ve SIGKILL yollarını karşılaştırmış.

---

# 🆚 İki Deneyi Yan Yana Koy

## SIGTERM

```
SIGTERM
↓
handler
↓
stop_request=True
↓
loop exit
↓
cleanup
↓
cleanup.log
↓
normal exit
```

## SIGKILL

```
SIGKILL
↓
handler yok
↓
shutdown state değişmedi
↓
normal shutdown flow yok
↓
cleanup'a ulaşılamadı
↓
cleanup.log yok
↓
forced termination
```

---

# 💾 Graceful Shutdown Ne Zaman Veri Bütünlüğü Problemi Olur?

Graceful shutdown yapılamaması örneğin:

```
dosyanın yarısının yazılması
transaction'ın yarıda kalması
buffer'ın flush edilememesi
state'in yarım persist edilmesi
```

gibi durumlara sebep olabiliyorsa konu artık yalnız:

```
“program kaba kapandı”
```

değildir.

Gerçek:

> **data integrity**

problemi olabilir.

Kaynak mülakat kısmında da yarım yazılmış dosya ve tamamlanmamış transaction örnekleri verilmiş.

---

# 🚨 `kill -9` Neden İlk Çözüm Değil?

Çünkü:

```
SIGKILL
↓
application handler çalışamaz
↓
normal shutdown yolu devre dışı
↓
application cleanup yapamaz
```

Bu yüzden operasyon sıram:

```
SIGTERM
↓
bekle
↓
exact PID'yi gözlemle
↓
shutdown devam ediyor mu?
↓
gerekiyorsa escalation
```

olmalı.

---

# ⚠️ TERM Gönderdim, 0.1 Saniye Sonra Hâlâ Yaşıyor

Bu:

> “TERM çalışmadı.”

kanıtı değildir.

Şunlar olmuş olabilir:

```
SIGTERM geldi ✅
handler çalıştı ✅
shutdown başladı ✅
cleanup hâlâ devam ediyor ⏳
```

Bu sırada SIGKILL gönderirsem çalışan graceful shutdown'ı ben kesmiş olurum.

Kaynak notta doğru operasyon sırası `request → bekle → gözlemle → doğrula → gerekirse escalate` olarak çıkarılmış.

---

# 🎮 Bash / Zsh Job Control

Buradaki büyük ayrım:

> **Shell job ≠ Linux process**

---

# Process

Kernel'in yönettiği çalışan varlık.

Kimliği:

```
PID
```

---

# Job

Shell'in yönettiği mantıksal çalışma birimi.

Kimliği:

```
%1
%2
%3
```

gibi job ID.

Bir job:

```
tek process
```

içerebilir.

Ama pipeline nedeniyle:

```
birden fazla process
```

de içerebilir.

Kaynak teoride bu ayrım açıkça kurulmuş.

---

# 🧠 Neden Farklı Kavramlar?

Çünkü sahipleri farklı.

```
Kernel
→ process
→ PID
→ process state

Shell
→ job
→ Job ID
→ foreground/background/current/previous
```

Dolayısıyla:

```
1 job
≠
her zaman 1 process
```

Kaynak mülakat cevabında da job'ın shell tarafından process veya process grubunu yönetmek için kullanılan mantıksal birim olduğu belirtilmiş.

---

# `jobs` vs `ps`

```
jobs
→ bu shell'in job-control tablosu

ps
→ OS/kernel process görünümü
```

Başka terminalde oluşturulmuş process:

```
ps'te görülebilir
```

ama:

```
benim mevcut shell'imin jobs çıktısında
```

olmak zorunda değildir.

---

# `&` — Background Job

```
python day25_job.py &
```

örneğin:

```
[1] 41101
```

çıktısını verdi.

Burada:

```
[1]
→ job ID

41101
→ PID
```

Aynı programı üç kez çalıştırınca:

```
3 job
+
3 ayrı process
```

oluştu.

Kaynak gerçek job-control deneyinde bu ayrım doğrudan gözlemlenmiş.

---

# `jobs` İçindeki `+` ve `-`

Başta bunları process state gibi düşünmeye yaklaşmışım.

TIRT.

```
+
→ current job

-
→ previous job
```

Process'in CPU state'i değil.

State ayrıca:

```
running
suspended
```

gibi görünür.

---

# Foreground

Foreground job terminal kontrolüne sahiptir.

Genellikle shell prompt'u geri dönmez.

---

# Background

Background job ilerlemeye devam edebilirken shell prompt verir.

```
program çalışıyor
+
shell yeni komut kabul ediyor
```

---

# `fg`

```
fg %3
```

mevcut job'ı foreground'a getirir.

> Yeni process oluşturmaz.

Aynı process/job devam eder.

---

# Ctrl+Z

Foreground job üzerinde:

```
Ctrl+Z
↓
tipik olarak SIGTSTP
↓
process/job stop/suspend
```

Bu:

> **terminate değildir.**

Process hâlâ yaşar.

---

# `bg`

Stopped job:

```
bg %3
```

ile background'da devam ettirilir.

Bu:

> Yeni process başlatmaz.

Aynı PID devam eder.

Signal tarafında `SIGCONT` ile ilişkilidir.

---

# 🧠 Shell Job State ≠ Kernel Process State

Bu bölümdeki en önemli hata:

> “`jobs` running diyorsa `ps` de `R` olmalı.”

TIRT.

Kaynak deneyde:

```
jobs
→ running

ps
→ S
```

aynı anda görülmüş.

---

# `S` — Sleeping

Örneğin program:

```
time.sleep(2)
```

yapıyor.

Kernel tarafında:

```
S
```

görülebilir.

Anlamı:

```
Process yaşıyor.
Stop edilmedi.
İlerlemesine izin var.
Ama şu anda bir olay/timer/I/O vb. bekliyor.
```

Shell ise hâlâ:

```
running
```

diyebilir.

Çünkü job **stop edilmiş değildir**.

---

# `T` — Stopped

Ctrl+Z sonrası:

```
jobs
→ suspended

ps
→ T
```

görüldü.

Burada:

```
process yaşıyor
ama yürütülmesi durdurulmuş
```

---

# 🔥 `S` vs `T`

```
S
→ İlerlemesine izin var
→ Şu an bir şey bekliyor
→ Beklediği şey olduğunda devam edebilir

T
→ Dışarıdan stop edilmiş
→ İlerlemesine izin verilmiyor
→ Devam ettirilmesi gerekiyor
```

Bu yüzden:

> `**wait hangi state geçişini yönetir?**` **sorusunun cevabı** `**S**` **veya** `**T**` **değildir.**

---

# ⏳ `wait`

`wait`, shell'in mevcut child/job'larının tamamlanmasını beklemek için kullandığı mekanizmadır.

Kaynak teoride de `wait` child/job completion ve reap/exit-status tarafıyla ilişkilendirilmiş.

---

# 🧪 `sleep 20 &` + `wait %4`

Önce:

```
sleep 20 &
```

çıktı:

```
[4] 44640
```

Burada:

```
Job ID = 4
PID = 44640
```

Child **burada** oluşturuldu.

Sonra:

```
wait %4
```

çalıştırıldı.

---

# `wait` Ne Yapmadı?

```
Yeni child oluşturmadı.
Child'ı öldürmedi.
Child'ı foreground'a getirmedi.
PID değiştirmedi.
```

Kaynak deneyde yeni PID oluşmadığı ve `sleep`in normal 20 saniyesini tamamladığı gözlemlenmiş.

---

# `wait` Ne Yaptı?

```
sleep background'da çalışıyor
↓
shell wait builtin'e giriyor
↓
shell kendi ilerleyişini bekletiyor
↓
child tamamlanıyor
↓
child'ın completion / exit status bilgisi alınabiliyor
↓
wait dönüyor
↓
shell tekrar prompt veriyor
```

---

# ⚠️ Prompt Yok → Child Foreground mı?

Hayır.

Benim gerçek hatam:

```
wait sırasında prompt yok
↓
“sleep foreground oldu”
```

diye düşünmekti.

Yanlış.

`sleep` background job olarak kaldı.

Prompt yoktu çünkü:

> **Shell'in kendisi** `**wait**` **içinde bekliyordu.**

Kaynak notta bu hata özellikle düzeltilmiş.

---

# 🧬 `wait` Hangi Lifecycle Geçişini Yönetir?

Kapalı-kitap mülakatta:

```
wait hangi state geçişini yönetir?
→ S
```

cevabı verilmiş.

> [!danger] TIRT  
> `wait` bir `S → ?` veya `T → ?` scheduler state geçişi yönetmez.

Doğru lifecycle modeli:

```
Parent shell
   │
   ├── child çalışıyor
   │
   └── wait(child)
            ↓
      child tamamlanana kadar bekle
            ↓
      child terminate olur
            ↓
      exit status oluşur
            ↓
      parent completion/status bilgisini toplar
            ↓
      child kernel bookkeeping'i reap edilir
```

Yani `wait`in konusu:

> **child completion + exit-status collection + reap**

tarafıdır.

`S`, `T`, `R` ise kernel scheduler/process state kodlarıdır.

---

# 👻 Zombie / Reap Mantığı

Child process sona erdiğinde kernel parent'ın alması gereken bazı completion bilgilerini tutabilir.

Kavramsal:

```
child running
↓
child exit
↓
termination bilgisi / exit status parent için tutulur
↓
parent wait eder
↓
status alınır
↓
reap
↓
child'ın kalan process-table bookkeeping'i kaldırılır
```

Bu yüzden:

> **Child'ın programı bitmiş olması ile parent'ın onun completion bilgisini toplamış olması ayrı lifecycle olaylarıdır.**

Shell'ler kendi SIGCHLD/job-control mekanizmalarıyla detayları yönetebilir; benim için önemli model `wait`in scheduler `S/T` state'i değil **parent-child completion contract'ı** olması.

---

# 🔢 `wait` ve Exit Status

Child:

```
exit 0
```

veya başka status ile biter.

Parent `wait` üzerinden bu completion sonucunu kullanabilir.

Dolayısıyla:

```
child bitti
→ parent açısından “nasıl bitti?” bilgisi de önemlidir
```

Yalnız child'ın yok olması değil.

---

# 🧠 `wait` İçin Kısa Model

```
command &
→ child oluştur

wait
→ o child'ı bekle

child exit
→ status hazır

parent
→ status'u al / reap et

wait döner
→ shell devam eder
```

Kaynak dosyanın kalan bölümündeki nihai job-control özeti de `wait`in child oluşturmadığını/öldürmediğini, shell'in kendi ilerleyişini beklettiğini vurguluyor.

---

# 🐳 Docker ve PID 1

Container kendi PID namespace'ine sahiptir.

Bu namespace içindeki ilk process:

```
PID 1
```

olur.

Container lifecycle ana process'in lifecycle'ıyla yakından bağlantılıdır.

---

# PID 1'i “Başlatma Biçimi” Sanma

İlk ifadem:

> “Programı PID 1 biçiminde başlatırım.”

Teknik olarak yanlış.

Doğru:

> **PID 1, seçtiğim process-entry yapısının sonucudur.**

Örneğin uygulamayı doğrudan çalıştırırsam uygulama PID 1 olabilir.

Araya shell koyarsam shell PID 1 olabilir.

Kaynak Docker deneyinde bu ifade açıkça düzeltilmiş.

---

# 🧪 Docker Deney A — Uygulama Doğrudan

Container:

```
container
└── python day25_docker.py
    PID = 1
```

Python çıktısı:

```
PID: 1
PPID: 0
STATE: Running
```

Kaynak deneyde Python'ın gerçekten PID 1 olduğu gözlemlenmiş.

---

# `PPID 0` Ne Demek?

Bunu:

```
“Dünyada parent'ı yok.”
```

gibi düşünmemeliyim.

Container PID namespace perspektifinde PID 1'in parent'ı namespace içinde görünmeyebilir.

---

# 🛑 Direkt Entry + `docker stop`

Labdaki/default stop modeli:

```
docker stop
↓
SIGTERM
↓
container PID 1
```

PID 1 Python ise:

```
SIGTERM
↓
Python
↓
handler
↓
stop_request=True
↓
loop biter
↓
cleanup
↓
exit
```

Deney sonunda:

```
cleanup.log
→ Cleanup yapıldı!
```

oluştu.

Kaynak direkt-entry testinde bu graceful zincir gözlemlenmiş.

---

# 📂 Bind Mount ve Cleanup Artifact'i

Container:

```
--mount type=bind,source="$PWD",target=/app
```

ile açılmıştı.

Bu yüzden:

```
container /app/cleanup.log
```

aslında host tarafındaki bind-mounted klasöre yazıldı.

Container `--rm` ile silinse bile host artifact'i kaldı.

---

# 🐚 Docker Deney B — Araya Shell

Komut:

```
sh -c "python -u day25_docker.py & wait"
```

Process ağacı:

```
PID 1 = sh
        │
        └── Python
            PID 7
            PPID 1
```

Python:

```
PID: 7
PPID: 1
```

çıktısını verdi.

Kaynak deneyde shell'in PID 1, Python'ın onun child'ı olduğu doğrulandı.

---

# `/proc` ile Bağımsız Kanıt

Yalnız Python'ın bastığı PPID'ye güvenilmedi.

Container içinde:

```
tr "\0" " " < /proc/1/cmdline
```

sonucu:

```
sh -c python -u day25_docker.py & wait
```

oldu.

İki kanıt:

```
Python:
PID 7
PPID 1

/proc/1/cmdline:
sh -c ...
```

Birleşince:

```
PID 1 = sh
└── PID 7 = Python
```

kanıtlandı.

---

# `ps` Neden Container'da Yoktu?

Şunu denedim:

```
docker exec ... ps ...
```

ama:

```
ps: executable not found
```

benzeri hata geldi.

Problem process teorim değildi.

Kullandığım slim image'da `ps` aracı yoktu.

Bu yüzden `/proc` kullanıldı.

> [!important]  
> Minimal container image = bütün alıştığım debugging araçları kurulu olacak demek değil.

---

# 🚦 Docker Signal Delivery Katmanı

Asıl zincir:

```
docker stop
↓
container main process / PID 1
↓
sonraki davranış PID 1'in kim olduğuna bağlı
```

Direkt:

```
PID 1 = Python
→ SIGTERM Python'a gelir
```

Shell'li:

```
PID 1 = sh
→ SIGTERM önce sh'a gelir
```

Docker'ın:

```
“Process tree'de Python'ı bulayım ve ona ayrıca SIGTERM göndereyim.”
```

diye varsayılmaması gerekir.

---

# 🧨 Shell'li Deneyin Sonucu

Bu spesifik yapı:

```
sh -c "python ... & wait"
```

Python'a gerekli SIGTERM'i forward etmedi.

Sonuç:

```
SIGTERM
↓
sh
↓
Python handler çalışmadı
↓
stop_request False
↓
cleanup yok
↓
timeout
↓
forced termination
```

Kaynakta shell'li deneyde `cleanup.log` oluşmadığı ve stop süresinin timeout'u tükettiği ölçülmüş.

---

# ⏱️ Timeout'u Ölçmek

Daha sağlam kanıt:

```
time docker stop -t 3 pid1-shell
```

Yaklaşık:

```
3.158 total
```

sürdü.

Bu:

```
SIGTERM sonrası hemen graceful exit olmadı
↓
3 saniyelik grace period tüketildi
↓
forced termination aşamasına gidildi
```

modelini destekledi.

---

# ⚠️ “Shell Varsa Signal Gitmez” Genellemesi

TIRT.

Bu labda:

```
sh -c 'python ... & wait'
```

forward etmedi.

Ama bundan:

> “Bütün shell'ler her zaman signal yutar.”

sonucu çıkmaz.

Doğru model:

> **Araya giren process'in forwarding veya** `**exec**` **davranışını bilmiyorsam uygulamanın signal'ı aldığını varsayamam.**

Kaynak notta bu aşırı genelleme özellikle geri alınmış.

---

# `exec` Neden Önemli Olabilir?

Shell kendisini uygulama ile replace edecek biçimde `exec` kullanırsa:

```
önce:
PID 1 = shell

exec application
↓
PID 1 artık application
```

gibi bir yapı oluşabilir.

Bu nedenle mesele:

```
shell var/yok
```

kadar basit değil.

Asıl:

```
Process tree nedir?
PID 1 kim?
Forwarding nasıl?
exec kullanılıyor mu?
```

---

# `--rm`

Başta container durduktan sonra tekrar `docker exec` ile inceleyebileceğimi düşündüm.

Ama:

```
container running
→ docker exec mümkün

docker stop
→ container stopped

--rm
→ container kaydı otomatik kaldırılır
```

Yani:

> `**--rm**` **= container durduktan sonra otomatik sil.**

Çalışırken anında sil demek değil.

---

# 🎯 Docker İçin Teknik Kararım

Varsayılan tercihim:

> Uygulamayı doğrudan container ana process'i olarak çalıştır.

Böylece labda:

```
SIGTERM
→ application
→ handler
→ cleanup
→ exit
```

zinciri doğrudan kurulmuş oldu.

---

# ⚖️ Trade-off

“Bunun trade-off'u yok.” demiştim.

TIRT.

Shell kullanmazsam shell'in:

- pipe,
    
- redirection,
    
- `&&`,
    
- expansion,
    
- shell scripting
    

özelliklerini doğrudan entry command içinde kullanamam.

Karar:

```
Signal/lifecycle sadeliği
vs
shell özellikleri
```

trade-off'u içerir.

---

# 🔄 Karşı Koşul

Direkt uygulama entry'si hangi durumda en iyi tercih olmayabilir?

> **Başlangıç akışında gerçekten shell özelliklerine ihtiyacım olduğunda.**

Ama o zaman:

```
signal forwarding
exec davranışı
PID 1
child reaping
```

tasarımını bilinçli yapmak gerekir.

---

# 🧬 Docker PID 1 ve Child Reaping

PID 1 container namespace içinde init rolüne özgü bazı lifecycle sorumluluklarıyla karşılaşabilir.

Özellikle child oluşturan uygulamalarda:

```
child terminate
↓
parent completion bilgisi
↓
reap
```

önemli olur.

Bu nedenle:

```
docker run --init ...
```

gibi küçük init process kullanan modeller child reaping ve signal forwarding tarafında yardımcı olabilir.

Kaynak teoride `--init` bu iki sorumlulukla ilişkilendirilmiş.

---

# 🐞 Ayırıcı Debugging Incident

Semptom:

> `docker stop` verdim ama beklediğim graceful shutdown artifact'i oluşmadı.

Direkt:

```
“Docker bozuk.”
```

demek TIRT.

Üç katman:

```
1. PID katmanı
→ Uygulamam gerçekten PID 1 mi?

2. Signal delivery
→ SIGTERM gerçekten uygulamaya ulaşıyor mu?

3. Application handler
→ Ulaştıysa uygulama doğru işliyor mu?
```

Kaynak debugging incident'ında bu üç hipotez ayrı ayrı kurulmuş.

---

# 🔬 En Küçük Ayırıcı Deney

Docker'ı aradan çıkar.

Programı host üzerinde çalıştır:

```
application
↓
doğrudan SIGTERM gönder
↓
cleanup var mı?
```

## Doğrudan SIGTERM başarılıysa

```
handler/application büyük ölçüde çalışıyor
↓
Docker PID 1 / forwarding / delivery tarafına dön
```

## Doğrudan SIGTERM'de de başarısızsa

```
application handler/shutdown logic hipotezi güçlenir
```

Bu çok güzel bir layer-isolation deneyi.

---

# 🧯 Hata Avı

## 1. Signal = process öldürme komutu

TIRT.

Signal genel bir asynchronous event mechanism.

---

## 2. `kill` komutunun tek amacı öldürmek

TIRT.

Temel işi signal göndermek.

---

## 3. SIGTERM geldiyse process anında kaybolmalı

TIRT.

Handler + cleanup devam ediyor olabilir.

---

## 4. SIGKILL handler'a yetişemeden kapanır

Teknik olarak TIRT.

SIGKILL **handle edilemez**.

---

## 5. Cleanup signal'ın kendi yaptığı iştir

TIRT.

Application shutdown logic yapar.

---

## 6. `cleanup.log` gerçek cleanup'ın kendisidir

TIRT.

Bu labda cleanup path'ine ulaşıldığının artifact kanıtıdır.

---

## 7. Ctrl+C yalnız bir PID'ye gider

TIRT.

Terminal foreground process group ile çalışabilir.

---

## 8. Ctrl+Z process'i öldürür

TIRT.

Stop/suspend eder.

---

## 9. Job ID = PID

TIRT.

Job ID shell'e, PID kernel'e aittir.

---

## 10. Bir job her zaman tek process'tir

TIRT.

Pipeline bir job altında birden fazla process içerebilir.

---

## 11. `jobs running` → `ps R`

TIRT.

Farklı state katmanları.

---

## 12. `S` process dışarıdan durduruldu demektir

TIRT.

`S` sleeping/waiting.

---

## 13. `T` process kendi isteğiyle sleep ediyor demektir

TIRT.

`T` stopped.

---

## 14. Prompt gelmiyorsa child kesin foreground'dadır

TIRT.

Shell kendisi `wait` içinde bekliyor olabilir.

---

## 15. `wait` child oluşturur

TIRT.

Child daha önce oluşturulmuştur.

---

## 16. `wait` child'ı öldürür

TIRT.

Child'ın completion'ını bekler.

---

## 17. `wait` background job'ı foreground'a getirir

TIRT.

Shell'i bekletir; job'ın foreground/background kimliğini değiştirmez.

---

## 18. `wait`in yönettiği state `S`'dir

TIRT.

`wait` scheduler `S/T/R` state geçişi yönetmez.

**Child completion → exit status → reap** lifecycle'ı ile ilgilidir.

---

## 19. Docker signal'ı Python dosyasına gönderir

TIRT.

Dosya signal alamaz.

Signal **process'e** gider.

---

## 20. Container'da Python çalışıyorsa kesin PID 1'dir

TIRT.

Arada shell/init/başka process olabilir.

---

## 21. Shell varsa signal kesin kaybolur

TIRT.

Forwarding/`exec` davranışına bağlı.

---

## 22. `docker stop` Python'ı process tree'de arayıp SIGTERM yollar

TIRT.

Container main process / PID 1 sınırı önemlidir.

---

## 23. `--rm` container çalışırken onu siler

TIRT.

Container sonlandıktan sonra otomatik kaldırır.

---

## 24. Minimal image'da `ps` kesin bulunur

TIRT.

Slim/minimal image diagnostic tool içermeyebilir.

---

## 25. `docker stop` sonrası cleanup yoksa direkt uygulama handler'ı bozuktur

TIRT.

Önce:

```
PID 1
signal delivery
handler
```

katmanlarını ayır.

---

# 🧠 Kafaya Kazı

> [!quote]  
> Signal bir “öldürme komutu” değil, process'e olay bildirme mekanizmasıdır.

> [!quote]  
> Signal gönderilmiş olması handler'ın çalıştığını kanıtlamaz.

> [!quote]  
> SIGTERM kontrollü kapanış için fırsat verir; graceful shutdown'ı uygulamanın tasarımı gerçekleştirir.

> [!quote]  
> SIGKILL catch/ignore/handle edilemez.

> [!quote]  
> Cleanup uygulama politikasının parçasıdır.

> [!quote]  
> TERM sonrası process'in kısa süre daha yaşaması failure kanıtı değildir.

> [!quote]  
> Request → bekle → gözlemle → doğrula → gerekirse escalate.

> [!quote]  
> PID kernel kimliğidir; job ID shell kimliğidir.

> [!quote]  
> Shell job dünyası ile kernel process dünyası bağlantılı ama aynı değildir.

> [!quote]  
> `jobs running` process'in o anda `R` state'inde olduğu anlamına gelmez.

> [!quote]  
> `S` = ilerlemesine izin var ama şu anda bekliyor.

> [!quote]  
> `T` = process stop edilmiş.

> [!quote]  
> `wait` child oluşturmaz, child'ı öldürmez, foreground'a taşımaz.

> [!quote]  
> `wait`, parent-child completion / exit-status / reap lifecycle'ı ile ilgilidir.

> [!quote]  
> Prompt yokluğu foreground kanıtı değildir.

> [!quote]  
> Docker signal'ı dosyaya değil container ana process'ine gönderir.

> [!quote]  
> PID 1 bir başlatma biçimi değil, process-entry tasarımının sonucudur.

> [!quote]  
> Aradaki process'in forwarding davranışını bilmeden uygulamanın signal aldığını varsayma.

> [!quote]  
> Graceful shutdown debugging: PID 1 → delivery → handler → cleanup → exit.

---

# 📌 30 Saniyelik Özet

```
SIGNAL
sender
↓
target process / process group
↓
signal
↓
delivery
↓
disposition
↓
default / ignore / handler
↓
lifecycle sonucu

SIGTERM
→ kontrollü kapanma isteği
→ handle edilebilir

SIGKILL
→ forced termination
→ handle edilemez

GRACEFUL
SIGTERM
↓
handler
↓
shutdown state
↓
loop exit
↓
cleanup
↓
normal exit

JOB CONTROL
kernel
→ process
→ PID
→ R/S/T...

shell
→ job
→ %1/%2...
→ foreground/background
→ jobs/fg/bg/wait

S
→ sleeping/waiting

T
→ stopped

WAIT
child zaten var
↓
parent wait eder
↓
child tamamlanır
↓
exit status
↓
reap
↓
shell devam eder

DOCKER
container
↓
PID 1
↓
docker stop signalı
↓
PID 1 kim?

DIRECT
PID 1 = Python
→ handler
→ cleanup
→ exit

SHELL-LAB
PID 1 = sh
↓
Python child
↓
signal forward edilmedi
↓
cleanup yok
↓
timeout
↓
forced termination

DEBUG
PID 1 kim?
↓
signal uygulamaya ulaştı mı?
↓
handler çalıştı mı?
↓
shutdown state değişti mi?
↓
cleanup oldu mu?
↓
process nasıl exit etti?
```

---

# ✅ Günün Kazanımları

- Signal'ın genel asynchronous mechanism olduğu öğrenildi
    
- Signal sender / target / type / delivery / disposition modeli kuruldu
    
- Generated / pending / delivered ayrıldı
    
- Default / ignore / custom handler ayrıldı
    
- SIGTERM davranışı öğrenildi
    
- SIGINT ve foreground process group ilişkisi öğrenildi
    
- SIGKILL'in catch/ignore/block edilemediği öğrenildi
    
- SIGTERM ile SIGKILL mekanizma farkı deneyle gözlemlendi
    
- Cleanup kavramı öğrenildi
    
- Cleanup artifact'i ile gerçek cleanup kavramı ayrıldı
    
- Shutdown state modeli kuruldu
    
- Handler registration ile handler logic ayrıldı
    
- `signum` / `frame` parametreleri öğrenildi
    
- `global` syntax/scope hatası düzeltildi
    
- Handler registration sırasının program lifecycle'ındaki önemi görüldü
    
- PID'nin process boyunca sabit kaldığı pekiştirildi
    
- Exact PID ile process gözlemi yapıldı
    
- SIGTERM → cleanup → exit zinciri iki bağımsız kanıtla doğrulandı
    
- SIGKILL karşı deneyinde cleanup'ın oluşmadığı doğrulandı
    
- `kill -9` kullanımının neden son escalation olması gerektiği öğrenildi
    
- Graceful shutdown'ın data-integrity etkisi anlaşıldı
    
- Shell job ile Linux process kesin olarak ayrıldı
    
- Job ID ile PID ayrıldı
    
- `jobs` ile `ps` farklı katmanlara yerleştirildi
    
- `+` / `-` current/previous job işaretleri öğrenildi
    
- Foreground/background modeli öğrenildi
    
- `fg` ve `bg`nin yeni process oluşturmadığı öğrenildi
    
- Ctrl+Z'nin terminate değil stop yaptığı gözlemlendi
    
- Shell `running` ile kernel `S` state'inin çelişmediği öğrenildi
    
- `S` ve `T` lifecycle farkı netleşti
    
- Prompt yokluğu ile foreground olmanın aynı şey olmadığı öğrenildi
    
- `sleep 20 &` ile child/job oluşturuldu
    
- `wait`in yeni child oluşturmadığı gözlemlendi
    
- `wait`in child'ı öldürmediği gözlemlendi
    
- `wait`in shell'in kendi ilerleyişini beklettiği öğrenildi
    
- `wait` scheduler state değil child completion / exit-status / reap modeliyle oturtuldu
    
- Docker PID namespace ve PID 1 kavramı öğrenildi
    
- Uygulamanın doğrudan PID 1 olduğu deney yapıldı
    
- Shell'in PID 1 olduğu karşı deney yapıldı
    
- Python PID / PPID ile process tree ölçüldü
    
- `/proc/1/cmdline` ile bağımsız PID 1 kanıtı üretildi
    
- Slim container'da `ps` bulunmaması gözlemlendi
    
- `docker stop` signal delivery sınırı öğrenildi
    
- Direkt entry'de graceful shutdown doğrulandı
    
- Shell'li entry'de signal forwarding failure gözlemlendi
    
- Stop timeout'u ölçülerek escalation davranışı doğrulandı
    
- “Shell varsa signal kesin kaybolur” genellemesi düzeltildi
    
- `exec` / forwarding davranışının önemi öğrenildi
    
- `--rm` lifecycle davranışı netleştirildi
    
- PID 1'in “başlatma biçimi” değil sonuç olduğu düzeltildi
    
- Direct entry kararının trade-off'u çıkarıldı
    
- Docker graceful-shutdown incident'ı üç katmana ayrıldı
    
- Docker'ı çıkararak handler'ı test eden en küçük ayırıcı deney tasarlandı
    

> [!success] 🚀 Gün sonu sonucu  
> Bugün sonunda signal/process tarafını artık:
> 
> ```
> “kill attım → process öldü”
> ```
> 
> seviyesinde düşünmüyorum.
> 
> Gerçek lifecycle modeli:
> 
> ```
> SIGNAL ÜRETİLDİ
> ↓
> doğru target seçildi mi?
> ↓
> signal delivered mı?
> ↓
> disposition ne?
> ↓
> handler ne yaptı?
> ↓
> application state değişti mi?
> ↓
> cleanup oldu mu?
> ↓
> process nasıl sonlandı?
> ```
> 
> Shell tarafında da:
> 
> ```
> JOB
> ≠
> PROCESS
> ```
> 
> ve özellikle:
> 
> ```
> wait
> ≠ S state
> ≠ child oluşturmak
> ≠ child öldürmek
> ≠ foreground'a taşımak
> 
> wait
> =
> parent'ın child completion'ını beklemesi
> + exit-status tarafını toplaması
> + reap lifecycle'ı
> ```
> 
> Docker tarafındaki son model:
> 
> ```
> docker stop
> ↓
> PID 1 kim?
> ↓
> Signal gerçekten application'a ulaşıyor mu?
> ↓
> Handler doğru mu?
> ↓
> Cleanup gerçekten oldu mu?
> ↓
> Grace period içinde exit var mı?
> ```
> 
> Günün en kritik cümlesi:
> 
> **Process debugging'de görünen son sonucu değil, lifecycle zincirinde ilk kırılan katmanı bulmam gerekiyor.**