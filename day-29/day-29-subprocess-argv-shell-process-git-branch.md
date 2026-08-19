---
title: "Gün 29 — Subprocess, argv, shell=True, Process Modeli ve Git Branch"
tags:
  - coreops
  - day29
  - python
  - subprocess
  - argv
  - shell
  - process
  - git
  - branch
  - security
aliases:
  - "Gün 29 Subprocess Güvenli Runner ve Git Branch"
status: completed
---

# 🧠 Gün 29 — `subprocess`, argv, `shell=True`, Process Modeli ve Git Branch

> [!abstract] 🎯 Ana fikir
> Bugünün iki ana konusu vardı:
>
> 1. Python'dan başka process çalıştırırken **structured argv** ile **shell tarafından parse edilen command string** arasındaki fark.
> 2. Git'te yeni işi `main` üzerinde yapmak yerine ayrı bir feature branch üzerinde geliştirip iki branch arasındaki farkı kanıtlamak.
>
> Python tarafındaki en kritik model:
>
>     argv listesi
>     -> program + argüman yapısı zaten belli
>     -> shell gerekmez
>
>     command string + shell=True
>     -> string önce shell tarafından parse edilir
>     -> shell syntax devreye girer
>
> Git tarafındaki en kritik model:
>
>     Branch
>     !=
>     proje klasörünün kopyası
>
>     Branch
>     =
>     bir commit'i gösteren hareketli referans

---

# 🐍 Python — Yeni Process Çalıştırma

Python'dan başka bir program çalıştırırken genel olarak `subprocess` kullanıyorum.

Örneğin:

`subprocess.run(["echo", "Ali Veli"])`

Burada Python'a doğrudan şunu söylüyorum:

- executable: `echo`
- `argv[1]`: `Ali Veli`

Yani:

    argv[0] = echo
    argv[1] = Ali Veli

`"Ali Veli"` içinde boşluk olsa bile tek argüman.

Çünkü Python listesindeki her eleman zaten ayrı bir argv elemanını temsil ediyor.

---

# 📦 Argv Listesi

Örneğin:

`["python3", "app.py", "--port", "8080"]`

kafamda şöyle:

    argv[0] = python3
    argv[1] = app.py
    argv[2] = --port
    argv[3] = 8080

Burada shell'in:

> "Boşluklara bakayım, argümanları ben ayırayım."

demesine gerek yok.

Yapı zaten verilmiş durumda.

> [!important]
> **Liste kullanınca command yapısını string parsing'e bırakmıyorum.**

---

# 🧠 `["echo", user_input]` vs `"echo " + user_input`

Bu ayrım bugün bayağı oturdu.

## Structured argv

`["echo", user_input]`

Burada:

    executable = echo
    argv[1] = user_input

`user_input` ne içerirse içersin tek argv elemanı olarak programa gönderilebilir.

---

## Command string

`"echo " + user_input`

Bu sadece düz metin.

Örneğin:

    user_input = "Ali Veli"

ise:

    echo Ali Veli

stringini üretmiş olurum.

Bu stringi:

`shell=True`

ile verirsem shell bunu kendi dili olarak parse eder.

---

# 🐚 `shell=True` Ne Yapıyor?

Normal:

`subprocess.run(["echo", "Ali Veli"])`

Akış:

    Python
    ↓
    echo
    ↓
    argv[1] = Ali Veli

Shell yok.

Ama:

`subprocess.run('echo "Ali Veli"', shell=True)`

dersem:

    Python
    ↓
    Shell
    ↓
    Command string parse edilir
    ↓
    echo çalıştırılır

Yani `shell=True` kabaca:

> **"Bu metni doğrudan executable + argv olarak ele alma. Shell'e ver, shell kendi dili olarak yorumlasın."**

demek.

Bu yüzden `shell=True` sadece kısa yazım değildir.

Araya yeni bir parser giriyor.

---

# ⚠️ Shell'in Özel Anlam Verdiği Şeyler

Shell şu karakter/yapılara özel anlam verebilir:

- `;`
- `|`
- `>`
- `<`
- `&&`
- `||`
- `$VAR`
- `$(...)`
- `*`

Örneğin:

`echo safe;touch MARKER`

shell açısından:

    echo safe

ve ardından:

    touch MARKER

olabilir.

Burada `;` artık normal veri değil.

**Shell syntax.**

---

# 🔐 Neden Argv Listesi Varsayılan Olarak Daha Mantıklı?

Shell özelliklerine gerçekten ihtiyacım yoksa:

`subprocess.run(["program", "arg1", "arg2"])`

kullanmak daha temiz.

Çünkü:

    veri
    ↓
    argv elemanı
    ↓
    program

şeklinde gider.

Shell kullandığımda:

    veri
    ↓
    command string
    ↓
    shell parser
    ↓
    yorumlanmış komut
    ↓
    program/programlar

oluyor.

Yani gereksiz yere yeni yorumlama katmanı eklemiş oluyorum.

---

# 🚨 `shell=True` Her Görüldüğünde Güvenlik Açığı mı?

Hayır.

Şu düşünce yanlış:

    shell=True gördüm
    -> kesin vulnerability

Asıl soru:

> **Shell'e verilen command stringinin içine kontrolsüz veri giriyor mu?**

Örneğin tamamen sabit:

`echo hello | tr a-z A-Z`

gibi bir command bilerek shell özelliklerini kullanabilir.

Riskli model daha çok:

    kontrolsüz veri
    ↓
    command string
    ↓
    shell=True
    ↓
    shell parsing

şeklinde.

---

# 🧪 `argv_probe.py`

Görev:

- aldığı argüman sayısını görmek,
- her argümanı ayrı göstermek,
- veriyi değiştirmeden gözlemlemek.

İlk başta burada bile `subprocess` kullanmaya çalıştım.

TIRT.

Programın görevi:

> Başka process oluşturmak değil, **kendisine ne geldiğini görmekti.**

Bu yüzden ihtiyacım olan şey:

`sys.argv`

---

# `sys.argv` Nereden Geliyor?

Başta:

> "`sys.argv`yi benim doldurmam gerekmiyor mu?"

diye düşündüm.

Hayır.

Python runtime bunu otomatik dolduruyor.

Örneğin:

`python3 argv_probe.py ali veli`

çalıştırırsam:

    sys.argv[0] = argv_probe.py
    sys.argv[1] = ali
    sys.argv[2] = veli

oluyor.

Ben önceden kaç argüman geleceğini tanımlamıyorum.

---

# Neden `sys.argv[1:]`?

`sys.argv[0]`:

    script/program adı

Kullanıcı argümanları:

`sys.argv[1:]`

Örneğin:

    sys.argv =
    ["argv_probe.py", "ali", "veli", "mehmet"]

ise:

`sys.argv[1:]`

sonucu:

    ["ali", "veli", "mehmet"]

---

# 🔬 Probe Programında Normalize Etmiyorum

Bu programın amacı:

> **"Bana gerçekte ne geldi?"**

sorusunu cevaplamak.

Dolayısıyla burada gereksiz yere:

- `.strip()`
- `.lower()`
- `.split()`

yapmak istemiyorum.

Çünkü probe:

    observation

katmanında.

Normalization yapmıyor.

---

# 🗣️ Quote Testi

Şunu çalıştırdım:

`python3 argv_probe.py ali veli "mehmet can"`

Python tarafında üç kullanıcı argümanı geldi:

    ali
    veli
    mehmet can

Çünkü terminaldeki shell:

`"mehmet can"`

kısmını tek argüman olarak Python'a verdi.

---

# ⚠️ Python Quote ile Shell Quote Aynı Şey Değil

Python'da:

`x = "Ali Veli"`

yazarsam gerçek string:

    Ali Veli

Dıştaki `"` karakterleri stringin parçası değildir.

Python parser'a:

> String burada başlıyor ve burada bitiyor.

diyor.

Ama:

`cmd = 'echo "Ali Veli"'`

yazarsam dıştaki `'` Python quote'u.

Stringin gerçek içeriği:

    echo "Ali Veli"

Buradaki `"` karakterleri gerçekten string içinde.

Shell bu stringi alırsa onları görebilir.

Yani bazen iki farklı parser var:

    Python source
    ↓
    Python parser
    ↓
    string
    ↓
    shell parser
    ↓
    command

---

# 💥 Quote'suz Payload Testinde Yaptığım Hata

Şunu terminale yazdım:

`python3 argv_probe.py safe;touch SHOULD_NOT_EXIST`

Sonra `SHOULD_NOT_EXIST` oluştu.

İlk bakışta:

> argv_probe güvenli değil galiba.

diye düşünülebilir.

Ama Python'a daha ulaşmadan **zsh** `;` karakterini yorumlamıştı.

Shell bunu:

    python3 argv_probe.py safe

ve:

    touch SHOULD_NOT_EXIST

olarak iki ayrı komuta böldü.

Python yalnız:

    safe

argümanını gördü.

Doğru deney:

`python3 argv_probe.py 'safe;touch SHOULD_NOT_EXIST'`

Bu quote shell'e:

> İçerideki `;` karakterini syntax olarak kullanma, tamamını tek argüman gönder.

demiş oluyor.

Bu deney sayesinde:

> **Terminalde yazdığım komutun kendisi de önce shell tarafından parse ediliyor.**

kafama oturdu.

---

# 🏃 `runner.py`

İkinci görev:

`run_command(args)`

fonksiyonu oluşturmaktı.

Girdi:

    executable + argv listesi

Çıktı:

    return code
    stdout
    stderr

Akış:

    args listesi
    ↓
    subprocess.run()
    ↓
    child process
    ↓
    program çalışır
    ↓
    stdout / stderr / return code
    ↓
    çağıran fonksiyona geri dön

---

# ⚠️ `args` Zaten Liste

Bir ara:

`subprocess.run([args])`

yazdım.

Ama:

    args = ["echo", "merhaba"]

ise:

    [args]

şuna dönüşüyor:

    [["echo", "merhaba"]]

Yani liste içinde liste.

Doğru:

`subprocess.run(args, ...)`

---

# 📥 `capture_output=True`

`capture_output=True` child'ın:

- stdout
- stderr

çıktılarını Python içerisinde yakalamamı sağlıyor.

Kabaca:

    child stdout
    ↓
    result.stdout

    child stderr
    ↓
    result.stderr

---

# 🔤 `text=True`

`text=True` kullanınca output:

    str

olarak gelir.

Örneğin:

    "mehmet\n"

Aksi durumda bytes görebilirdim:

    b"mehmet\n"

---

# 📦 `CompletedProcess`

`subprocess.run()` tamamlandığında bana bir `CompletedProcess` nesnesi döndürüyor.

Buradan:

- `result.returncode`
- `result.stdout`
- `result.stderr`

alabiliyorum.

Akış:

    subprocess.run()
    ↓
    child başlar
    ↓
    child biter
    ↓
    CompletedProcess
    ↓
    returncode / stdout / stderr

---

# 🚪 Return Code

Bir process tamamlandığında exit status bırakıyor.

Başarılı programlarda genellikle:

    0

görürüm.

Ama:

> **Programın başlatılabilmiş olması ile başarılı tamamlanmış olması aynı şey değildir.**

Process gerçekten çalışmış olabilir ama non-zero exit code ile başarısız tamamlanabilir.

---

# stdout vs stderr

`stdout`:

> Programın normal çıktısı.

`stderr`:

> Hata veya diagnostic çıktısı.

İkisini ayrı kanallar olarak düşünüyorum.

---

# ✂️ `.strip()` Kullanımım

`echo` çıktısı:

    "mehmet\n"

şeklinde geliyor.

Bunu:

`print(stdout)`

ile basınca newline nedeniyle görüntü çirkinleşebiliyor.

Bu yüzden presentation sırasında:

`stdout.strip()`

kullandım.

Ama fonksiyon içinde gerçek çıktıyı:

    "mehmet\n"

olarak koruyorum.

Yani:

    data katmanı
    -> raw stdout

    presentation katmanı
    -> stdout.strip()

Bu daha temiz.

---

# 🔄 Fonksiyonun Return Değeri

Başta fonksiyonu:

`-> None`

gibi düşünmüştüm.

Ama fonksiyonun çağıran tarafa:

- return code
- stdout
- stderr

vermesi gerekiyor.

Dolayısıyla mantık:

    return result.returncode,
           result.stdout,
           result.stderr

Sonra:

    returncode, stdout, stderr = run_command(...)

şeklinde tuple unpacking yapabiliyorum.

---

# ⚠️ Test Kodunu Modül Altında Bırakmak

`runner.py` dosyasının altında direkt:

`run_command(...)`

çağrısı bırakırsam başka bir dosya:

`from runner import run_command`

dediğinde import sırasında test kodu da çalışabilir.

Çözüm:

- test kodunu kaldırmak
- veya `if __name__ == "__main__":` altında tutmak

---

# 🆚 `subprocess.run()` vs `Popen()`

## `run()`

Kafamdaki model:

    child başlat
    ↓
    bitmesini bekle
    ↓
    sonucu getir

Daha senkron kullanım.

---

## `Popen()`

`Popen()` child çalışırken parent'ın yaşamaya devam etmesini ve child üzerinde kontrol sahibi olmamı sağlıyor.

Örneğin:

`p = subprocess.Popen(["sleep", "10"])`

Model:

    Python parent
        │
        └── sleep child

Parent bu sırada başka şeyler yapabilir.

---

# 🔍 `poll()`

`poll()`:

> Child bitmiş mi?

diye bakıyor.

Ama bitmemişse beklemiyor.

Child hâlâ çalışıyorsa:

    None

Child bittiyse:

    return code

dönebilir.

Kısa model:

> **poll = sor ve devam et**

Örneğin:

- scanner hâlâ çalışıyor mu?
- UI güncelle
- log oku
- kullanıcı cancel yaptı mı?
- başka iş yap

gibi durumlarda kullanışlı.

---

# ⏳ `wait()`

`wait()`:

> Child bitene kadar burada bekle.

Kısa model:

    poll
    -> kapıdan bak

    wait
    -> gelene kadar kapıda bekle

Process lifecycle tarafında ayrıca:

    child
    ↓
    exit
    ↓
    parent completion bilgisini toplar
    ↓
    wait
    ↓
    exit status
    ↓
    reap

mantığıyla bağlantılı.

---

# ⚙️ Yeni Process Hangi Bilgilerle Başlar?

İlk cevabım sadece environment tarafına kaymıştı.

Daha doğru model:

Yeni process için temel olarak:

1. executable
2. argv
3. environment

önemli.

Kısa ayrım:

    argv
    -> Programa bu çağrıda ne söyledim?

    env
    -> Program hangi environment ile çalışıyor?

Environment açıkça verilmezse normalde parent environment'ı devralınabilir.

---

# 🧬 `fork()` ve `exec`

Burası düşük seviyeli process modelini anlamak için önemliydi.

## `fork()`

Kısa:

> **fork = çoğal**

Mevcut process'ten yeni child process oluşturur.

Örneğin:

    Python PID 100
    ↓ fork

    Python PID 100
        └── Python PID 101

---

## `execve()`

Kısa:

> **exec = dönüş**

Yeni process oluşturmaz.

Mevcut process'in çalıştırdığı programı başka programla değiştirir.

Örneğin:

    PID 500
    Python

`execve()` sonrası:

    PID 500
    ls

PID aynı kalabilir.

Ama artık process Python programını çalıştırmıyordur.

Bu yüzden başarılı `execve()` normal şekilde geri dönmez.

---

# 🧠 Process != Program

Program:

> Disk üzerindeki executable/kod.

Process:

> O programın çalışan instance'ı.

`exec` sırasında process aynı process olabilir ama üzerinde çalışan program image değişir.

---

# Process Image

Kabaca process'in program tarafındaki:

- code
- data
- heap
- stack

gibi runtime memory yapıları.

`exec` olduğunda eski program image yerine yeni executable'ın image'ı yüklenir.

---

# Klasik Unix Modeli

    parent process
    ↓
    fork
    ↓
    child process
    ↓
    exec
    ↓
    hedef program

Kısa:

    fork
    -> yeni process oluştur

    exec
    -> mevcut process'teki programı değiştir

---

# `posix_spawn()`

Kabaca:

    process oluşturma
    +
    gerekli hazırlıklar
    +
    executable çalıştırma

işini daha birleşik bir spawn mekanizmasıyla yapıyor.

Şu anda doğrudan kullanmam gerekmiyor.

Python `subprocess` bazı durumlarda altta bunu kullanabilir.

Benim high-level araçlarım:

- `subprocess.run()`
- `subprocess.Popen()`

---

# `vfork()`

Daha özel ve düşük seviyeli bir process creation mekanizması.

Şimdilik bilmem gereken:

> **Process oluşturma implementasyon detaylarından biri.**

Buna gömülmem şu an gereksiz.

---

# 🔎 `shutil.which()`

Bu process oluşturmaz.

Şu soruya cevap verir:

> **Bu executable PATH üzerinde nerede?**

Örneğin:

`shutil.which("python3")`

şuna benzer bir path döndürebilir:

`/opt/homebrew/bin/python3`

Dış tool kullanan programlarda çok yararlı:

    nmap kurulu mu?
    ↓
    PATH'te mi?
    ↓
    hangi nmap çalışacak?

---

# 🧪 Güvenli argv Karşılaştırması

Payload:

`safe;touch MARKER`

Structured argv ile:

`["echo", "safe;touch MARKER"]`

kullanırsam `echo` bunu tek argüman olarak görür.

Sonuç:

    safe;touch MARKER

çıktısı.

`MARKER` oluşmamalı.

Çünkü shell yok.

---

# 💥 Kontrollü `shell=True` Karşı Deneyi

Ürün kodumu değiştirmedim.

Ayrı test dosyasında aynı payload'ı command string içine koydum:

    echo safe;touch MARKER

ve shell tarafından parse edilmesini sağladım.

Shell bunu:

    echo safe

ve:

    touch MARKER

olarak yorumladı.

Sonuç:

    stdout -> safe
    MARKER -> oluştu

Bu kontrollü lab iki execution modelinin gerçekten farklı olduğunu kanıtladı.

---

# 🔥 Aynı Payload, İki Farklı Execution Modeli

## Structured argv

    Python
    ↓
    ["echo", "safe;touch MARKER"]
    ↓
    echo
    ↓
    tek argv elemanı
    ↓
    "safe;touch MARKER"

---

## Shell command string

    Python
    ↓
    "echo safe;touch MARKER"
    ↓
    shell
    ↓
    parse
    ↓
    echo safe
    +
    touch MARKER

> [!danger]
> **Veri shell parser'a girdiğinde shell syntax'ına dönüşebilir.**

---

# 🐞 Python Tarafında Yaptığım Hatalar

## Hata 1 — `argv_probe` içinde subprocess kullanmaya çalışmak

Görev bana gelen argv'yi gözlemlemekti.

Başka process oluşturmak gereksizdi.

Çözüm:

`sys.argv`

---

## Hata 2 — `sys.argv`yi kendim dolduracağımı sanmak

Python runtime zaten dolduruyor.

---

## Hata 3 — `shell=True` kullanılan listeyle normal argv'yi aynı sanmak

Shell devreye girdiğinde execution semantics değişiyor.

---

## Hata 4 — Python quote'larının shell'e aynen gittiğini sanmak

Python source quote'ları ile string içinde gerçekten bulunan quote karakterleri aynı şey değil.

---

## Hata 5 — Payload'ı terminalde quote'suz kullanmak

Shell payload'ı Python'dan önce parse etti.

Bu yüzden yanlış katmanı test etmiş oldum.

---

## Hata 6 — Yanlış `argv_probe.py` dosyasını çalıştırmak

VS Code terminalinde çalışan kod normal terminalde çalışmıyor sandım.

Gerçekte başka klasörde aynı isimli dosyayı çalıştırıyordum.

Kontroller:

`pwd`

`cat argv_probe.py`

Ders:

> **Python'u suçlamadan önce hangi dosyayı çalıştırdığını kanıtla.**

---

## Hata 7 — Runner için `argparse` veya `input()` düşünmek

Fonksiyona zaten `args` listesi geliyor.

Gereksiz bir input katmanı eklemeye çalışıyordum.

---

## Hata 8 — `subprocess.run([args])`

`args` zaten list.

Bir daha liste içine almak yanlış.

---

## Hata 9 — Fonksiyonu `None` döndürüyor gibi düşünmek

Fonksiyonun return code/stdout/stderr üretmesi gerekiyor.

---

## Hata 10 — Karşı deneyde sadece mevcut çağrıya `shell=True` eklemeyi düşünmek

Doğru karşılaştırma:

    structured argv

ile:

    shell tarafından parse edilen command string

arasında olmalı.

---

# 🌳 Git — Feature Branch Uygulaması

İkinci büyük görev Git branch mantığıydı.

Amaç:

- `main` branch'ini korumak
- yeni işi ayrı branch'te yapmak
- branch üzerinde commit oluşturmak
- tekrar `main`e dönmek
- iki branch farkını kanıtlamak
- graph üzerinde branch noktalarını görmek

Kullandığım feature branch:

`feature/secure-runner`

---

# 💥 İlk Problem — `.git` Klasörünü Yanlışlıkla Silmişim

`git status`

dediğimde:

    bir git deposu değil

hatası aldım.

`ls -a`

ile baktığımda `.git` yoktu.

Sonradan fark ettim:

Bir ara proje dosyalarını taşırken gereksiz sandığım klasörü silmişim.

Ama `.git` o klasörün içindeymiş.

---

# 🧠 "Git'i O Klasöre Kurdum" Yanılgısı

İlk düşüncem:

> Git'i o klasöre kurmuşum galiba.

TIRT.

Doğru model:

> **Git sisteme kurulu programdır. `git init` ise bulunduğum klasörü Git repository haline getirip `.git/` metadata dizini oluşturur.**

`.git` içinde kabaca:

- commits
- objects
- refs
- branches
- HEAD
- Index
- repository metadata

bulunuyor.

Proje dosyaları durup `.git` giderse:

    dosyalar var ✅
    Git repository metadata ❌

durumuna düşebilirim.

---

# ♻️ Repository Metadata'yı Geri Getirmek

Eski kopyada:

- `.git`
- `.gitignore`

bulundu.

Doğru repository root'una geri getirince:

`git status`

tekrar repository'yi gördü.

Ardından:

`git log --oneline --decorate --graph --all`

ile eski commit geçmişinin hâlâ bulunduğunu doğruladım.

Ders:

> **`.git` "gizli olduğu için önemsiz" bir klasör değil. Repository'nin metadata merkezidir.**

---

# 🌿 Branch Nedir?

Branch:

- yeni proje klasörü değil
- dosyaların fiziksel kopyası değil
- yeni repository değil

Kafamdaki model:

> **Branch = belirli bir commit'i gösteren hareketli isim/referans.**

Başlangıç:

    main -> A

Yeni branch açınca:

    main -> A
    feature -> A

Henüz fark yok.

Feature branch üzerinde commit atınca:

    main -> A
    feature -> B

Feature ilerledi.

Main aynı yerde kaldı.

---

# `master` -> `main`

Başlangıç branch'im:

    master

Görev `main` istediği için:

`git branch -m main`

ile sadece branch'in adını değiştirdim.

Bu:

- commitleri değiştirmedi
- dosyaları değiştirmedi
- history'yi değiştirmedi

Sadece:

    master

ismi:

    main

oldu.

---

# 🌱 Feature Branch Oluşturma

Komut:

`git switch -c feature/secure-runner`

Parçalarsam:

    git switch
    -> branch değiştir

    -c
    -> branch oluştur

    feature/secure-runner
    -> yeni branch adı

Yani:

> **Yeni branch oluştur ve direkt ona geç.**

---

# `HEAD`

Feature üzerindeyken:

    HEAD
    ↓
    feature/secure-runner
    ↓
    current commit

Main'e geçtiğimde:

    HEAD
    ↓
    main
    ↓
    main'in commit'i

Kısa model:

> **HEAD şu anda checkout/switch edilmiş konumu gösteren referanstır.**

---

# 📂 Day29 Zaten Untracked'mış

`git status` sonucunda Day29:

    untracked

göründü.

Yani dosyalar disk üzerinde vardı ama repository geçmişine hiç eklenmemişti.

Bu feature branch görevi için uygun oldu.

Day29'u feature üzerinde ilk kez Git'e ekledim.

---

# ⚠️ Neden `git add .` Kullanmadım?

Working Tree'de Day29 dışında başka değişiklikler de vardı.

Eğer:

`git add .`

deseydim istemediğim başka değişiklikleri de stage edebilirdim.

Bu yüzden hedefli:

`git add Day29/`

kullandım.

Kural:

> **Working Tree kirliyse önce `git status`, sonra mümkün olduğunca kontrollü staging.**

---

# 📦 Staging Area / Index

`git add Day29/`

commit oluşturmadı.

Sadece Day29'un mevcut içeriğini:

> **Bir sonraki commit'e girecek snapshot**

haline getirdi.

Akış:

    Working Tree
    ↓ git add
    Index / Staging Area
    ↓ git commit
    Commit History

---

# ✅ Feature Commit

Feature branch üzerinde:

`git commit -m "add Day29 secure runner work"`

ile commit oluşturdum.

Bu noktada:

    main -> cef871d

    feature/secure-runner -> 86a2522

oldu.

Branch'ler artık gerçekten farklı commit'leri gösteriyordu.

---

# 🗑️ MARKER Test Artığını Yanlışlıkla Commit Ettim

İlk commit içinde:

`tests/MARKER`

dosyasının da girdiğini fark ettim.

Bu önceki shell testinden kalan runtime/test artifact'iydi.

Source code gibi history'ye girmemesi gerekiyordu.

Hata:

> `git add Day29/` yaptıktan sonra staged içeriği yeterince kontrol etmedim.

Daha iyi akış:

    git status
    ↓
    git diff --staged
    ↓
    commit

---

# `git rm --cached`

MARKER'ı Git tracking/Index tarafından çıkarmak istedim ama Working Tree'deki fiziksel dosyayı korumak istiyordum.

Bunun için:

`git rm --cached Day29/secure-runner-lab/tests/MARKER`

kullandım.

Kafamdaki model:

    Git tracking/index'ten çıkar
    ↓
    Working Tree dosyasını bırak

---

# ✏️ `git commit --amend --no-edit`

Yeni bir "MARKER'ı sildim" commit'i oluşturmak yerine son commit'i düzelttim.

`git commit --amend --no-edit`

Burada:

    --amend
    -> son commit'i yeniden oluştur

    --no-edit
    -> commit mesajını değiştirme

---

# 🔢 Commit Hash Neden Değişti?

İlk commit:

    86a2522

Amend sonrası:

    4dde055

oldu.

Çünkü amend:

> Mevcut commit objesinin içine girip onu yerinde değiştirmek

değil.

Daha doğru model:

> **Değişmiş snapshot/metadata ile yeni commit oluşturup branch pointer'ını yeni commit'e taşı.**

Bu yüzden hash değişmesi normal.

---

# 🔀 Main'e Geri Dönmek

Sonra:

`git switch main`

ile main branch'e döndüm.

Bu:

    feature branch'i silmez
    feature commit'ini silmez

Sadece HEAD'i değiştirir.

Model:

    main -> cef871d
    ↑
    HEAD

    feature/secure-runner -> 4dde055

---

# ⚠️ Branch Değiştirirken Unstaged Değişiklikler

`git switch main`

sırasında daha önceden Working Tree'de olan bazı unstaged değişiklikleri de gördüm.

Buradan önemli ders:

> **Branch değiştirmek bütün kirli Working Tree state'ini otomatik yok etmek zorunda değildir.**

Çakışma yaratmayan unstaged değişiklikler branch switch sırasında kalabilir.

Bu yüzden:

    "Main'e geçtim ve M gördüm."
    !=
    "Feature commit main'e geldi."

Commit history ile mevcut Working Tree state'i ayrı.

---

# 🔍 Branch İçerik Farkı

Main üzerindeyken:

`git diff main..feature/secure-runner -- Day29`

kullandım.

Bu:

> **Main ve feature snapshot'ları Day29 açısından nasıl farklı?**

sorusunu cevapladı.

Day29 feature'da yeni olduğu için:

`new file mode`

ve:

`--- /dev/null`

gibi şeyler gördüm.

`/dev/null` burada kabaca:

> Main tarafında bu file'ın karşılığı yok.

anlamına geliyor.

---

# 📜 Branch Commit Farkı

Sonra:

`git log main..feature/secure-runner --oneline`

kullandım.

Bu:

> **Feature tarafından ulaşılabilen ama main tarafından ulaşılamayan hangi commitler var?**

sorusunu cevaplıyor.

Çıktı:

    4dde055 add Day29 secure runner work

Yani feature main'den bir commit ileride.

---

# `git diff` vs `git log`

Bunları artık ayırıyorum.

`git diff main..feature`

-> snapshot / dosya içerik farkı

`git log main..feature`

-> commit/history farkı

Aynı soruyu cevaplamıyorlar.

---

# 🌳 Git Graph

Görevdeki önemli kanıt:

`git log --oneline --decorate --graph --all`

Son model:

    4dde055  feature/secure-runner
       |
    cef871d  main, HEAD
       |
      ...

Burada:

- `main` -> `cef871d`
- `feature/secure-runner` -> `4dde055`
- `HEAD` -> `main`

durumunu gördüm.

---

# 🤔 Graph Neden Gerçekten Çatallanmış Görünmedi?

İlk başta `--graph` görünce iki kol bekliyordum.

Ama yalnız feature branch ilerledi.

Main'de branch ayrıldıktan sonra yeni commit oluşturmadım.

Bizde:

    A --- B
    ↑     ↑
    main  feature

durumu var.

Gerçek çatallanma için iki branch'in de ayrı yönlerde commit üretmesi gerekirdi:

          B --- C   feature
         /
    ----A
         \
          D --- E   main

Bizim görevde buna gerek yoktu.

---

# 🔄 Branch Switch ve Working Tree

Branch yalnız pointer olsa bile gösterdiği commit'in bir snapshot'ı var.

`git switch feature/secure-runner`

dersem Git Working Tree'yi feature snapshot'ına uygun hale getirmeye çalışır.

`git switch main`

dersem Working Tree'yi main snapshot'ına uygun hale getirir.

Dolayısıyla branch switch:

> Yalnız terminalde branch adının değişmesi değildir.

Filesystem görünümü de hedef snapshot'a göre değişebilir.

---

# 🧠 Git State Modeli

## Working Tree

Diskte şu anda gördüğüm ve düzenlediğim dosyalar.

## Index / Staging Area

Bir sonraki commit'e seçtiğim snapshot.

## Commit

Projenin geçmişteki kayıtlı snapshot'ı.

## Branch

Bir commit'i gösteren hareketli referans.

## HEAD

Şu anda hangi branch/commit üzerinde çalıştığımı gösteren referans.

Akış:

    Working Tree
    ↓
    git add
    ↓
    Index
    ↓
    git commit
    ↓
    Commit History

Branch bu commit history içerisindeki bir noktayı gösterir.

---

# 🐞 Git Tarafında Yaptığım Hatalar

## Hata 1 — `.git` bulunan klasörü silmek

Repository metadata'sını kaybettim.

Ders:

> Gizli klasör diye `.git`i önemsiz sanma.

---

## Hata 2 — "Git'i klasöre kurdum" demek

Git program olarak sisteme kurulur.

`git init` klasörü repository yapar.

---

## Hata 3 — Test artifact'i MARKER'ı stage/commit etmek

Düzeltme:

- tracking'den çıkardım
- son commit'i amend ettim

Ders:

> Commit'ten önce staged snapshot'ı kontrol et.

---

## Hata 4 — `git branch` tek başına branch farkını kanıtlar sanmak

`git branch`:

- branch isimleri
- aktif branch

konusunda iyi.

Ama commit yerleşimi için:

`git log --oneline --decorate --graph --all`

daha güçlü.

---

# 🧯 Hata Avı — Gün 29

## 1. Command string ile argv listesi aynı şey

TIRT.

    argv listesi
    -> structured data

    command string
    -> text

---

## 2. `shell=True` sadece kısa yazım

TIRT.

Yeni bir shell parser katmanı ekler.

---

## 3. `shell=True` gördüm, kesin güvenlik açığı

TIRT.

Kontrolsüz data'nın shell command stringine girip girmediğine bakmam gerekir.

---

## 4. Python source quote'ları shell'e aynen gider

TIRT.

Python parser önce kendi quote syntax'ını çözer.

---

## 5. `sys.argv`yi ben doldururum

TIRT.

Runtime doldurur.

---

## 6. `sys.argv[0]` ilk kullanıcı argümanıdır

TIRT.

Genellikle program/script adı.

---

## 7. Probe programı input'u normalize etmeli

TIRT.

Probe gerçekte ne geldiğini değiştirmeden göstermeli.

---

## 8. `subprocess.run([args])`

TIRT.

`args` zaten listeyse nested list olur.

---

## 9. `run()` child'ı başlatıp hemen döner

Eksik.

Normal kullanımda child'ın bitmesini bekler.

---

## 10. `poll()` child bitene kadar bekler

TIRT.

Kontrol eder ve beklemeden döner.

---

## 11. `wait()` yeni child oluşturur

TIRT.

Var olan child'ın completion'ını bekler.

---

## 12. `exec` yeni process oluşturur

TIRT.

Mevcut process'in program image'ını değiştirir.

---

## 13. `fork` mevcut process'i başka programa dönüştürür

TIRT.

Yeni child oluşturur.

---

## 14. `shutil.which()` program çalıştırır

TIRT.

Executable'ın PATH üzerindeki yerini bulur.

---

## 15. Branch = proje klasörünün kopyası

TIRT.

Branch commit pointer'ıdır.

---

## 16. Branch açar açmaz main ve feature farklıdır

TIRT.

İlk anda ikisi aynı commit'i gösterebilir.

---

## 17. `git add` commit oluşturur

TIRT.

Index snapshot'ını hazırlar.

---

## 18. `git switch main` feature commit'ini siler

TIRT.

HEAD'i main'e taşır.

---

## 19. `git diff main..feature` ile `git log main..feature` aynı soruyu cevaplar

TIRT.

Biri içerik, biri history/commit farkı.

---

## 20. Commit amend edilince hash aynı kalmalı

TIRT.

Yeni commit objesi oluştuğu için hash değişebilir.

---

# 🧠 Kafaya Kazı

> [!quote]
> Bir programa argv vermek ile shell'e command text vermek aynı şey değildir.

> [!quote]
> Structured argv'de Python listesinin her elemanı ayrı argv elemanıdır.

> [!quote]
> Shell devreye girdiğinde veri yeniden yorumlanabilir.

> [!quote]
> Shell'e gerçekten ihtiyacım yoksa araya shell sokma.

> [!quote]
> Terminale yazdığım komutu da önce terminalde çalışan shell parse eder.

> [!quote]
> Probe'un işi veriyi düzeltmek değil, gerçekte ne geldiğini göstermek.

> [!quote]
> `run()` başlatır ve bekler; `Popen()` daha fazla lifecycle kontrolü verir.

> [!quote]
> `poll()` bakar, `wait()` bekler.

> [!quote]
> `fork` yeni process oluşturur, `exec` mevcut process'in programını değiştirir.

> [!quote]
> Program disk üzerindeki kod, process onun çalışan instance'ıdır.

> [!quote]
> Branch başka bir proje klasörü değil, commit'e verilen hareketli referanstır.

> [!quote]
> Working Tree, Index, HEAD ve branch aynı state değildir.

> [!quote]
> Feature üzerinde commit atarsam feature ilerler; main kendiliğinden ilerlemez.

> [!quote]
> `git diff` içerik farkını, `git log A..B` commit farkını gösterir.

> [!quote]
> Commit'ten önce staged snapshot'ı kontrol et.

---

# 📌 30 Saniyelik Özet

    PYTHON PROCESS

    executable
    +
    argv
    +
    environment
    ↓
    child process


    SAFE / DEFAULT MODEL

    ["program", "arg1", "arg2"]
    ↓
    structured argv
    ↓
    shell parsing yok


    SHELL MODEL

    "program arg1; another-command"
    ↓
    shell=True
    ↓
    shell parser
    ↓
    shell syntax aktif


    subprocess.run()
    -> child başlat
    -> bekle
    -> CompletedProcess

    Popen()
    -> child başlat
    -> lifecycle kontrolü

    poll()
    -> bitti mi?
    -> bekleme

    wait()
    -> bitene kadar bekle

    fork()
    -> child oluştur

    exec()
    -> mevcut process'in programını değiştir

    shutil.which()
    -> executable PATH'te nerede?


    GIT

    Working Tree
    ↓ git add
    Index
    ↓ git commit
    Commit History

    Branch
    -> commit pointer

    HEAD
    -> şu anki konum


    Başlangıç:

    main -> A
    feature -> A

    Feature commit:

    main -> A
    feature -> B

    Main'e dön:

    HEAD -> main -> A
    feature -> B


    git diff main..feature
    -> içerik farkı

    git log main..feature
    -> feature'da olup main'de olmayan commitler

    git log --graph --all
    -> branch geçmişi / pointer konumları

---

# ✅ Günün Kazanımları

- [x] Structured argv ile command string ayrıldı
- [x] `shell=True` execution modeli öğrenildi
- [x] Shell syntax'ın veri üzerindeki etkisi kontrollü deneyle görüldü
- [x] `shell=True` ile vulnerability kavramı birbirinden ayrıldı
- [x] Python quote ile shell quote ayrıldı
- [x] `sys.argv` çalışma mantığı öğrenildi
- [x] `sys.argv[0]` ve `sys.argv[1:]` ayrıldı
- [x] Probe ile normalization görevi ayrıldı
- [x] Terminal shell'in payload'ı Python'dan önce parse edebildiği görüldü
- [x] Yanlış dosya/path incident'ı debugging ile çözüldü
- [x] `subprocess.run(args)` doğru kullanım modeli oturdu
- [x] Nested list hatası düzeltildi
- [x] `capture_output=True` öğrenildi
- [x] `text=True` öğrenildi
- [x] `CompletedProcess` öğrenildi
- [x] stdout / stderr / return code ayrıldı
- [x] `.strip()` yalnız presentation tarafında kullanıldı
- [x] Fonksiyonun tuple döndürmesi uygulandı
- [x] Import side-effect riski fark edildi
- [x] `run()` ve `Popen()` ayrıldı
- [x] `poll()` ve `wait()` ayrıldı
- [x] executable / argv / environment modeli kuruldu
- [x] `fork()` ve `exec()` arasındaki temel fark öğrenildi
- [x] Process ile program ayrıldı
- [x] Process image kavramı öğrenildi
- [x] `posix_spawn()` ve `vfork()` temel seviyede konumlandırıldı
- [x] `shutil.which()` ile executable resolution mantığı öğrenildi
- [x] Structured argv ve shell command string karşı deneyle doğrulandı
- [x] `.git` repository metadata dizininin önemi öğrenildi
- [x] Silinen `.git` metadata'sı geri getirilip history doğrulandı
- [x] Branch'in proje kopyası olmadığı öğrenildi
- [x] `master` branch `main` olarak yeniden adlandırıldı
- [x] `feature/secure-runner` branch'i oluşturuldu
- [x] Hedefli staging kullanıldı
- [x] Working Tree / Index / Commit ayrımı pekiştirildi
- [x] Feature branch üzerinde anlamlı commit oluşturuldu
- [x] Yanlışlıkla commit edilen MARKER artifact'i fark edildi
- [x] `git rm --cached` kullanıldı
- [x] `git commit --amend --no-edit` kullanıldı
- [x] Amend sonrası commit hash değişimi anlaşıldı
- [x] `HEAD` branch ilişkisi pekiştirildi
- [x] Main'e dönmenin feature commit'ini silmediği görüldü
- [x] Unstaged Working Tree state'in branch switch ile taşınabileceği fark edildi
- [x] Branch snapshot farkı `git diff` ile kanıtlandı
- [x] Branch commit farkı `git log main..feature` ile kanıtlandı
- [x] Git graph ile main ve feature pointer'ları doğrulandı
- [x] Graph'ın neden fiziksel çatallanma göstermediği anlaşıldı
- [x] Branch / commit / HEAD / Working Tree / Index modeli tek resimde birleştirildi

> [!success] 🚀 Gün sonu sonucu
> Bugün iki farklı alanda aynı prensibi gördüm:
>
> **Yapının ne olduğunu açıkça bilirsem parser'ın veya aracın benim yerime tahmin yapmasına daha az ihtiyaç duyarım.**
>
> Python'da:
>
>     structured argv
>     -> program ve argüman sınırları açık
>
> Git'te:
>
>     branch / HEAD / Index / Working Tree
>     -> hangi state'i değiştirdiğim açık
>
> Bu yüzden artık subprocess tarafında:
>
> **"Shell gerçekten gerekli mi?"**
>
> Git tarafında ise:
>
> **"Şu anda hangi branch/state üzerinde neyi değiştiriyorum?"**
>
> sorularını ilk başta sormam gerekiyor.
>
> Günün en kritik cümlesi:
>
> **Bir programa structured argv vermek ile shell'e yorumlanacak command string vermek nasıl aynı şey değilse, Git'te branch, HEAD, Index ve Working Tree de aynı şey değildir; doğru sınırı bilirsem hem güvenlik hem debugging çok daha kolaylaşır.**