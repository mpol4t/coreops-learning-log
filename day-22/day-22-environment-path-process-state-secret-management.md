---
title: "Gün 22 — Environment, PATH, Process State, Clean Env ve Git Secret Yönetimi"
tags:
  - coreops
  - linux
  - environment
  - path
  - process
  - executable-resolution
  - python
  - configuration
  - secrets
  - git
  - gitignore
aliases:
  - "Gün 22 Environment PATH Process State ve Secret Yönetimi"
status: completed
---

# 🧠 Gün 22 — Environment, `PATH`, Process State, Clean Env ve Git Secret Yönetimi

> [!abstract] 🎯 Ana fikir  
> Bugünün ana konusu:
> 
> **Programın davranışını sadece kod belirlemez; process'in çalıştığı environment da program state'inin bir parçasıdır.**
> 
> Kafamdaki temel model:
> 
> ```
> Parent Shell
> ├── Environment
> │   ├── PATH
> │   ├── APP_MODE
> │   └── API_TOKEN
> │
> └── Child Process
>     └── Başlatılırken export edilmiş environment'ın kopyasını alır
> ```
> 
> Bir komut yanlış çalışıyorsa:
> 
> ```
> Kod mu yanlış?
> PATH mi yanlış?
> Alias/function mı?
> CWD mi?
> Config eksik mi?
> ```
> 
> diye katman katman ayırmam gerekiyor.

---

# 🌍 Environment Variable Nedir?

Environment variable:

```
Python global variable
```

veya:

```
diskteki config dosyası
```

değildir.

**Process environment state'inin bir parçasıdır.**

Örneğin shell process'im:

```
PATH=...
HOME=...
APP_MODE=production
API_TOKEN=...
```

gibi değerler taşıyabilir.

Child process başlatıldığında parent'ın **export edilmiş** environment'ının bir kopyasını alır.

---

# 👨‍👦 Parent → Child Environment

Kritik model:

```
Parent process
    ↓ process oluştur
Child process
```

Child başlatılırken:

```
export edilmiş environment
→ child'a aktarılır
```

Ama sonrasında child kendi environment'ını değiştirirse:

```
Child değişti
≠
Parent geriye dönük değişti
```

Yani environment inheritance **tek yönlü başlangıç kopyası** gibi düşünülebilir.

---

# ⚠️ Shell Variable ile Exported Environment Farkı

Shell içinde variable tanımlamak:

```
APP_MODE=production
```

ile onu child process'e export etmek aynı kavram değildir.

Child'a geçmesi için tipik olarak:

```
export APP_MODE=production
```

veya tek komutluk:

```
APP_MODE=production python3 app.py
```

kullanılabilir.

> [!important]  
> Python `os.getenv()` parent shell'in iç değişken tablolarını sihirli biçimde okumaz.
> 
> **Kendi process environment'ını okur.**

---

# 📍 `PWD` vs `PATH`

Bugünün önemli ayrımlarından biri:

```
PWD
→ Ben şu anda hangi dizindeyim?

PATH
→ Shell bir executable adı verdiğimde hangi dizinlerde arasın?
```

Kaynak notta bu iki state özellikle ayrılmış.

---

# 🔎 `PATH` Nasıl Çalışır?

Örneğin:

```
/bin_a:/bin_b:/usr/bin
```

gibi bir `PATH` varsa shell komut adını sırayla arar:

```
bin_a
↓
bin_b
↓
usr/bin
```

İlk uygun eşleşme kazanır.

Bu yüzden sıra önemlidir.

---

# 🧪 Path Shadowing Deneyi

İki executable:

```
bin_a/asset-tool
→ A sürümü

bin_b/asset-tool
→ B sürümü
```

İlk durumda:

```
PATH
→ bin_a önce
```

ve:

```
asset-tool
```

çıktısı:

```
A sürümü
```

oldu.

Sonra:

```
export PATH="$PWD/bin_b:$PWD/bin_a:$PATH"
```

yapıldı.

Bu kez:

```
asset-tool
```

çıktısı:

```
B sürümü
```

oldu.

`command -v` ve `type` sonuçları da resolution'ın `bin_b/asset-tool` olarak değiştiğini gösterdi.

---

# 🌑 Path Shadowing Nedir?

Aynı komut adına sahip birden fazla implementation varsa:

```
PATH'in solundaki
```

diğerini gölgeleyebilir.

Örneğin:

```
/custom/bin/python
/usr/bin/python
```

ve custom dizin önceyse shell ilkini çalıştırabilir.

Bu:

```
Beklediğim executable
≠
Gerçekte çalışan executable
```

durumuna yol açabilir.

---

# ⚠️ PATH'i Güncellerken Eski `$PATH`'i Silme

Yanlış zihinsel model:

```
export PATH="$PWD/bin_a:$PWD/bin_b:$PWD"
```

Böyle yaparsam mevcut sistem executable yollarını yanlışlıkla kaldırabilirim.

Daha güvenli temel yaklaşım:

```
export PATH="$PWD/bin_a:$PWD/bin_b:$PATH"
```

Yani:

```
Yeni yollar
+
Eski PATH
```

---

# 🔍 `command -v`

```
command -v foo
```

şu soruya cevap verir:

> **Mevcut shell** `**foo**` **ismini neye resolve ediyor?**

Yani:

```
foo yazarsam
shell ne çalıştıracak?
```

sorusunun kanıtıdır.

Kaynak araştırmada da `command -v` mevcut command resolution'ı ölçen araç olarak doğru tanımlanmış.

---

# 🧩 `type`

```
type foo
```

daha açıklayıcı olabilir.

Çünkü bir komut adı yalnız executable dosya olmak zorunda değildir.

Shell açısından:

```
alias
function
builtin
external executable
```

olabilir.

Örneğin sistemde:

```
command -v python
```

sonucu alias gösterebilirken:

```
command -v python3
```

gerçek executable yolunu gösterebilir.

Kaynak deneyde `python` alias, `python3` ise `/opt/homebrew/bin/python3` olarak çözülmüş.

---

# 🧠 `command -v` vs `type`

Kısa model:

```
command -v
→ “Bu isim neye resolve oluyor?”

type
→ “Bu isim shell açısından NE tür bir şey?”
```

`type` özellikle:

```
alias mı?
function mı?
builtin mi?
dosya mı?
```

sorusunda çok değerlidir.

---

# 📦 `bin` Nedir?

`bin` ismi tarihsel olarak **binary** kelimesinden gelir.

Sık görülen dizinler:

```
/bin
/usr/bin
/usr/local/bin
```

Ama:

> `bin` içindeki her executable mutlaka derlenmiş machine-code binary olmak zorunda değildir.

Executable script de bulunabilir.

---

# 🔬 Binary ve Disassembly

`/bin/ls` gibi derlenmiş executable'ı reverse engineering aracında açınca:

```
ARM64 assembly instructions
```

görmek normal.

Çünkü baktığım şey:

```
ls source code
```

değil:

```
derlenmiş executable'ın disassembly'si
```

---

# `#!` Shebang

Script'in başındaki:

```
#!/bin/sh
```

satırına **shebang** denir.

Temel görevi:

> Script doğrudan çalıştırıldığında hangi interpreter kullanılmalı?

Örnek:

```
#!/bin/sh
→ sh

#!/bin/bash
→ bash

#!/bin/zsh
→ zsh

#!/usr/bin/env python3
→ PATH üzerinden python3
```

---

# 🔐 Execute Permission ≠ Shebang

```
chmod +x
→ Bu dosyayı execute etmeye iznim var mı?

shebang
→ Execute edildiğinde hangi interpreter yorumlayacak?
```

İkisi farklı sorular.

---

# 💻 Terminal ≠ Shell

```
Terminal
→ Yazdığım ve çıktıyı gördüğüm arayüz

Shell
→ Komutları parse edip çalıştıran process/program
```

Örneğin terminal uygulamamın içinde:

```
zsh
```

çalışıyor olabilir.

---

# 🧼 Clean Environment — `env -i`

```
env -i ...
```

mevcut environment inheritance'ını büyük ölçüde temizleyerek komutu minimal/boş bir environment ile başlatmak için kullanılabilir.

Bu çok değerli bir ayırıcı deneydir.

Normal environment'ta çalışan program clean env'de bozuluyorsa:

```
environment dependency
```

olduğuna dair güçlü sinyal elde ederim.

---

# 🧩 Clean Environment Failure Hipotezleri

Kaynak çalışmada üç ayrı katman kurulmuş.

## Hipotez 1 — `PATH`

```
Normal shell
→ asset-tool PATH'te

Clean env
→ PATH yok/değişik

Sonuç
→ command resolve edilemiyor
```

Katman:

```
shell / executable resolution
```

---

## Hipotez 2 — Config Environment

Program:

```
APP_MODE
CONFIG_PATH
API_TOKEN
```

gibi bir environment variable bekliyor olabilir.

Clean environment:

```
variable yok
```

Sonuç:

```
Program başladı
ama configuration katmanında failure
```

---

## Hipotez 3 — CWD / Relative Path

Program:

```
config.json
```

gibi relative path kullanıyor olabilir.

Farklı CWD:

```
aynı relative path
→ farklı absolute hedef
```

anlamına gelir.

Katman:

```
filesystem path resolution
```

---

# 🧠 PATH vs CWD

Bunları özellikle karıştırma:

```
PATH
→ executable nereden bulunacak?

CWD
→ relative dosya path'i nereden çözülecek?
```

Örneğin:

```
python3 app.py
```

içindeki `python3`:

```
PATH / shell resolution
```

ile ilgilidir.

Ama Python içindeki:

```
open("asset.json")
```

şu anki:

```
CWD
```

ile ilgilidir.

---

# 🔬 En Küçük Ayırıcı Deney

Clean env'de uygulamanın kendisini çalıştırıp her şeyi aynı anda test etmek yerine önce:

```
Sadece Python başlıyor mu?
```

sorusunu ayırmak mantıklı.

Kaynakta bu amaçla Python'ın absolute executable path'i kullanılmış:

```
env -i \
  /opt/homebrew/bin/python3 \
  day22.py
```

Böylece shell'in `python3` resolution'ı bypass edildi.

---

# 🎯 Bu Deney Ne Kanıtladı?

Sonuç:

```
Python başladı ✅

APP_MODE yok ❌

Uygulama explicit config failure verdi ✅

exit code = 1 ✅
```

Dolayısıyla:

```
Problem Python executable bulunamaması değil.
```

Hata katmanı:

```
application / configuration
```

olarak ayrıldı.

---

# 🐍 Python — `os.getenv()`

```
os.getenv("APP_MODE")
```

Python process environment'ındaki:

```
APP_MODE
```

değerini okur.

Variable yoksa:

```
None
```

döndürür.

---

# ⚡ Truthy / Falsy

Python `if` yalnız literal:

```
True
False
```

değerlerine bakmaz.

Falsy örnekler:

```
None
False
0
""
[]
{}
()
```

Dolayısıyla:

```
if os.getenv("APP_MODE"):
```

şu iki durumu da başarısız sayar:

```
APP_MODE hiç yok
→ None

APP_MODE var ama boş
→ ""
```

Kaynak notta bu davranış özellikle fark edilmiş.

---

# ⚙️ Config Policy — Default mı Explicit Failure mı?

Günün teknik kararı:

```
APP_MODE zorunlu
```

olsun.

Eksikse:

```
development
```

gibi otomatik default kullanmak yerine explicit failure tercih edildi.

Neden?

Çünkü yanlış configuration:

```
sessizce gizlenebilir
```

ve geliştiriciye özel davranışlar yanlış ortamda açılabilir.

---

# ⚖️ Trade-off

Explicit failure:

```
+ Yanlış config gizlenmez
+ Production daha belirgin davranır
- Variable unutulursa program hiç başlamaz
```

Default:

```
+ Kolay kullanım
- Yanlış configuration sessizce devam edebilir
```

---

# 🔐 Secret Invariant

Programın kritik invariant'ı:

> `**API_TOKEN**` **gerçek değeri stdout veya log'a asla basılmamalı.**

Program yalnız:

```
API_TOKEN mevcut
```

veya:

```
API_TOKEN eksik
```

bilgisi verebilir.

Kaynak görevde başarı ölçütlerinden biri secret değerinin stdout/log'a hiçbir şekilde sızmaması olarak tanımlanmış.

---

# 🚨 Secret Varlığını Loglamak vs Secret'ı Loglamak

Bunlar farklı:

```
API_TOKEN mevcut
→ metadata/state

API_TOKEN=abc123...
→ secret disclosure
```

İkincisi yapılmamalı.

---

# 🚪 Exit Code

Config zorunluysa ve eksikse:

```
sys.exit(1)
```

ile process failure açıkça dış dünyaya bildirilmiş.

Kaynak deney:

```
APP_MODE eksik
→ stderr mesajı
→ exit 1
```

şeklinde sonuçlanmış.

---

# 🌳 Git — `.env` Güvenlik Deneyi

Bugün `.gitignore` konusunda iki ayrı state deneyle ayrıldı:

```
1. .env hiç tracked olmamış
2. .env önce commit edilmiş
```

Bu iki senaryo tamamen farklı davranır.

---

# ✅ Senaryo 1 — `.env` Hiç Tracked Olmadı

Dosya:

```
.env
```

Working Tree'de var.

`.gitignore`:

```
.env
```

içeriyor.

Kanıtlar:

```
git check-ignore -v .env
```

→ ignore rule eşleşiyor.

```
git ls-files .env
```

→ çıktı yok.

Yani `.env` Index/tracked dünyasında yok.

```
git show HEAD:.env
```

→ HEAD snapshot'ında da yok.

Kaynak deneyde bu dört state ayrı ayrı doğrulanmış.

---

# 🧠 State

```
Working Tree
→ .env var

Ignore
→ eşleşiyor

Index
→ .env yok

HEAD
→ .env yok
```

Bu `.gitignore` için ideal senaryo.

---

# 💥 Senaryo 2 — `.env` Önceden Commit Edildi

Önce:

```
git add .env
git commit ...
```

yapıldı.

Sonra:

```
.env
```

`.gitignore` içine eklendi.

Ama:

```
git ls-files .env
```

hâlâ `.env` gösterdi.

Ve:

```
git show HEAD:.env
```

dosyanın commit snapshot'ında hâlâ bulunduğunu kanıtladı.

---

# 🔥 `.gitignore` Neden Yetmedi?

Çünkü:

```
.gitignore
→ Daha önce tracked olmayan dosyaların
  tracking'e alınmasını önlemeye yardım eder.
```

Ama:

```
Tracked file
→ Index zaten biliyor
→ HEAD/history zaten içeriyor
```

`.gitignore`:

```
Index'i temizle
history'yi sil
```

komutu değildir.

---

# 🧠 State — Tracked Secret

Kaynakta doğru state modeli çıkarılmış.

```
Working Tree
→ .env var

Index
→ .env tracked

HEAD
→ .env mevcut

Older History
→ .env eski commitlerde mevcut

.gitignore
→ .env pattern'iyle eşleşiyor
```

Bunların hepsi aynı anda doğru olabilir.

---

# ⚠️ `git check-ignore --no-index`

Tracked dosyalar normal ignore davranışında farklı ele alınabildiği için deneyde:

```
git check-ignore -v --no-index .env
```

kullanılarak:

> “Index durumunu hesaba katmadan pattern bu path ile eşleşiyor mu?”

sorusu ayrıca test edilmiş.

Bu:

```
Ignore pattern eşleşiyor ✅
Tracked state devam ediyor ✅
```

ayrımını görünür yaptı.

---

# 🔐 Commit Edilmiş Secret İçin `.gitignore` Çözüm Değil

Gerçek credential commit edildiyse:

```
.env'i .gitignore'a ekledim
```

demek yeterli değildir.

Çünkü secret:

```
HEAD
ve/veya
older Git history
```

içinde yaşamaya devam edebilir.

Kaynak notta bu durumda credential'ın sızmış kabul edilip revoke/rotate edilmesi gerektiği özellikle belirtilmiş.

---

# 🚨 Secret Incident Mantığı

Gerçek secret commit edildiyse:

```
1. Secret sızmış kabul et
2. Credential'ı revoke/rotate et
3. Current tracking durumunu düzelt
4. Gerekliyse history cleanup değerlendir
```

Önemli:

> History temizlemek secret'ı tekrar güvenli yapmaz.

Credential zaten dışarı çıkmış olabilir.

Bu yüzden **rotation/revocation** kritik.

---

# ⚖️ History Rewrite Trade-off

History rewrite:

```
commit hash'lerini değiştirebilir
```

Bu nedenle ekipte:

- Existing clones
    
- Branch'ler
    
- Open PR'lar
    
- Remote history
    

gibi durumları etkileyebilir.

Yani yalnız teknik değil, repository coordination kararıdır.

---

# 🐞 Ayırıcı Incident — Yanlış `asset-tool` Çalışıyor

Semptom:

```
asset-tool çalışıyor
ama beklediğim implementation değil
```

Direkt kodu değiştirmek TIRT.

Önce resolution katmanını ölç.

Kaynakta üç hipotez kurulmuş.

---

# Hipotez 1 — PATH Shadowing

```
PATH'te birden fazla asset-tool
↓
Soldaki farklı implementation
↓
Yanlış sürüm çalışıyor
```

---

# Hipotez 2 — Alias / Function / Builtin

```
asset-tool
```

belki executable file bile değil.

Shell-level:

```
alias
function
```

olabilir.

Bu yüzden:

```
type asset-tool
```

çok değerlidir.

---

# Hipotez 3 — Shell Resolution Cache

Shell daha önce executable konumunu cache/hash etmiş olabilir.

PATH değişmiş olsa bile mevcut shell state'inde eski resolution etkisi araştırılabilir.

---

# 🔬 En Küçük Ayırıcı Deney

Önce:

```
type asset-tool
```

ardından:

```
command -v asset-tool
```

Sonra:

```
asset-tool
```

gerçek outputuyla karşılaştır.

Böylece:

```
İsim neye resolve oluyor?
↓
Gerçek çalışan davranış ne?
```

kanıt zinciri oluşur.

---

# 🎯 Yeni Debugging Hükmüm

> **“Yanlış implementation çalışıyor” semptomunda önce program kodunu değil executable resolution state'ini ölç.**

Katman:

```
Shell / executable resolution
```

ise uygulama kodunu değiştirmek gereksizdir.

---

# 🧯 Hata Avı

## 1. Environment variable Python global'idir

TIRT.

Process environment state'idir.

---

## 2. Parent'ın bütün shell variable'ları child'a gider

TIRT.

Export edilmiş environment aktarılır.

---

## 3. Child environment değişirse parent da değişir

TIRT.

Child kendi process state'ini değiştirir.

---

## 4. `PWD` executable arama listesidir

TIRT.

`PWD` çalışma dizini.

`PATH` executable arama listesi.

---

## 5. PATH sırasının önemi yoktur

TIRT.

İlk uygun eşleşme kazanır.

---

## 6. `command -v` yalnız binary dosya yolu göstermek için vardır

TIRT.

Shell command resolution'ını sorgular.

---

## 7. `type` yalnız executable path döndürür

TIRT.

Alias/function/builtin gibi türleri açıklayabilir.

---

## 8. `bin` içindeki her şey machine-code binary olmak zorundadır

TIRT.

Executable script de olabilir.

---

## 9. Shebang execute permission verir

TIRT.

Shebang interpreter seçer.

Permission ayrı konudur.

---

## 10. Terminal ile shell aynı şeydir

TIRT.

Terminal arayüz, shell komut yorumlayan process'tir.

---

## 11. Clean env'de program patladıysa kesin PATH sorunudur

TIRT.

Config veya CWD problemi de olabilir.

---

## 12. Absolute Python path ile çalıştırınca PATH resolution testi yapmış olurum

Hayır.

Tam tersine Python executable resolution'ını **bypass etmiş** olurum.

Bu sayede iç application/config davranışını daha temiz izole ederim.

---

## 13. `os.getenv()` parent shell'i direkt okur

TIRT.

Python process'in kendi environment'ını okur.

---

## 14. `if os.getenv("APP_MODE")` yalnız variable yokluğunu kontrol eder

TIRT.

`None` yanında boş string de falsy olduğu için iki state'i birlikte reddeder.

---

## 15. Secret değerini debug log'a basmak sorun değildir

TIRT.

Secret invariant'ını ihlal eder.

---

## 16. `.gitignore` tracked `.env` dosyasını otomatik untrack eder

TIRT.

Index/HEAD/history state'i değişmez.

---

## 17. `.env` `.gitignore` ile eşleşiyorsa HEAD'de bulunamaz

TIRT.

Daha önce commit edilmişse bulunabilir.

---

## 18. Commit edilmiş token'ı `.gitignore'a eklemek olayı çözer

TIRT.

Credential rotate/revoke edilmelidir.

---

## 19. Yanlış program çalışıyorsa ilk iş kodu değiştirmektir

TIRT.

Önce:

```
type
command -v
PATH
```

ile executable resolution ölçülmelidir.

---

# 🧠 Kafaya Kazı

> [!quote]  
> Environment variable process state'inin parçasıdır.

> [!quote]  
> Parent export edilmiş environment'ını child'a aktarır.

> [!quote]  
> Child environment değişikliği parent'ı geriye dönük değiştirmez.

> [!quote]  
> `PWD` nerede olduğumu, `PATH` executable'ın nerede aranacağını söyler.

> [!quote]  
> PATH soldan sağa çözülür; ilk uygun eşleşme kazanır.

> [!quote]  
> `command -v` mevcut shell resolution'ını ölçer.

> [!quote]  
> `type` komut adının alias/function/builtin/executable olduğunu açıklayabilir.

> [!quote]  
> CWD relative filesystem path'lerini, PATH executable isimlerini etkiler.

> [!quote]  
> `env -i` environment bağımlılıklarını ayırmak için güçlü bir deneydir.

> [!quote]  
> Absolute executable path kullanmak PATH resolution'ını bypass eder.

> [!quote]  
> `os.getenv()` mevcut Python process environment'ını okur.

> [!quote]  
> Config eksikliği sessiz default yerine explicit failure gerektirebilir.

> [!quote]  
> Secret'ın değeri log veya stdout'a asla sızmamalı.

> [!quote]  
> `.gitignore` tracked state'i veya history'yi otomatik değiştirmez.

> [!quote]  
> Secret history'ye girdiyse secret sızmış kabul edilmelidir.

> [!quote]  
> Yanlış executable semptomunda önce resolution state'ini ölç.

---

# 📌 30 Saniyelik Özet

```
ENVIRONMENT
→ process state

PARENT
→ export edilmiş env
↓
CHILD
→ başlangıç kopyasını alır

PWD
→ process nerede?

PATH
→ executable nerede aransın?

PATH
dir_a:dir_b:...
→ soldan sağa
→ ilk eşleşme

DEBUG
command -v foo
→ neye resolve oluyor?

type foo
→ alias/function/builtin/file?

CLEAN ENV
env -i
→ inherited environment'ı temizle

HİPOTEZLER
PATH
config env
CWD

PYTHON
os.getenv("APP_MODE")
→ process environment

APP_MODE eksik
→ stderr
→ exit non-zero

SECRET
API_TOKEN değeri
→ ASLA output/log yok

GIT
.env hiç tracked değil
→ ignore işe yarar

.env önce commit edildi
→ .gitignore tracking'i kaldırmaz

STATE
Working Tree → var
Index        → tracked
HEAD         → var
History      → var
Ignore rule  → yine eşleşebilir

SECRET COMMIT
→ revoke / rotate
→ tracking düzelt
→ gerekiyorsa history cleanup

INCIDENT
yanlış asset-tool
↓
type
↓
command -v
↓
PATH
↓
gerçek implementation
```

---

# ✅ Günün Kazanımları

- Environment variable'ın process state olduğu öğrenildi
    
- Parent / child environment inheritance modeli kuruldu
    
- Export edilmiş shell variable ile normal shell variable ayrıldı
    
- `PWD` ve `PATH` kesin olarak ayrıldı
    
- PATH'in soldan sağa resolution yaptığı deneyle doğrulandı
    
- Aynı isimli iki executable ile path shadowing gözlemlendi
    
- `$PATH` korunmadan PATH overwrite etme riski öğrenildi
    
- `command -v` ile executable resolution ölçüldü
    
- `type` ile alias/function/builtin/executable ayrımı öğrenildi
    
- `bin` kavramı öğrenildi
    
- Derlenmiş binary ile disassembly ayrıldı
    
- Shebang mantığı öğrenildi
    
- Execute permission ile interpreter selection ayrıldı
    
- Terminal ve shell ayrıldı
    
- `env -i` ile clean environment deneyi yapıldı
    
- PATH/config/CWD failure hipotezleri ayrıldı
    
- Absolute Python executable ile PATH katmanı bypass edildi
    
- Clean env failure'ın application/config katmanında olduğu kanıtlandı
    
- `os.getenv()` davranışı öğrenildi
    
- Truthy/falsy üzerinden eksik/boş config davranışı anlaşıldı
    
- Eksik zorunlu config için explicit failure kararı verildi
    
- Default config kullanımının trade-off'u değerlendirildi
    
- Secret değeri için output/log invariant'ı oluşturuldu
    
- Config failure stderr + non-zero exit ile dışarı taşındı
    
- `.env` hiç tracked değil senaryosu test edildi
    
- `.env` önce tracked senaryosu ayrı repo ile test edildi
    
- `git check-ignore -v` kullanıldı
    
- `git ls-files` ile tracked state ölçüldü
    
- `git show HEAD:.env` ile HEAD snapshot kanıtlandı
    
- `.gitignore` ile tracked state'in bağımsız olduğu deneyle doğrulandı
    
- Commit edilmiş secret için rotation/revocation gerekliliği öğrenildi
    
- History rewrite trade-off'u fark edildi
    
- Yanlış executable incident'ı için üç hipotez üretildi
    
- `type` + `command -v` ile en küçük ayırıcı deney kuruldu
    
- “Önce state'i ölç → sahip katmanı bul → sonra fix” debugging modeli pekiştirildi
    

> [!success] 🚀 Gün sonu sonucu  
> Gün 22 sonunda program davranışını artık yalnız:
> 
> ```
> kaynak kod
> ```
> 
> üzerinden düşünmüyorum.
> 
> Gerçek çalışma state'i:
> 
> ```
> SHELL
> ├── environment
> ├── PATH
> ├── aliases/functions
> └── CWD
>       ↓
> CHILD PROCESS
> ├── inherited environment
> ├── executable
> ├── config
> └── application
> ```
> 
> Dolayısıyla:
> 
> ```
> “Benim program yanlış çalışıyor.”
> ```
> 
> demeden önce:
> 
> ```
> Hangi executable çalıştı?
> ↓
> PATH neydi?
> ↓
> Komut alias/function mı?
> ↓
> Child hangi environment'ı aldı?
> ↓
> CWD neydi?
> ↓
> Gerekli config var mıydı?
> ```
> 
> sorularını cevaplamam gerekiyor.
> 
> Git tarafındaki aynı prensip de:
> 
> ```
> “.gitignore'a yazdım.”
> ```
> 
> diye varsaymak yerine:
> 
> ```
> Working Tree'de var mı?
> Index takip ediyor mu?
> HEAD'de var mı?
> History'de var mı?
> Ignore rule gerçekten eşleşiyor mu?
> ```
> 
> diye state'i ayrı ayrı ölçmek.
> 
> Günün en kritik cümlesi:
> 
> **Önce gözlenen davranışın hangi state ve katmana ait olduğunu kanıtla; ancak ondan sonra kodu veya configuration'ı değiştir.**