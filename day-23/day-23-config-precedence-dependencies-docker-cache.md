---
title: "Gün 23 — Config Precedence, Dependency Yönetimi ve Docker Cache / Build Context"
tags:
  - coreops
  - python
  - configuration
  - config-precedence
  - environment
  - argparse
  - dependencies
  - pyproject
  - venv
  - docker
  - cache
  - build-context
  - dockerignore
aliases:
  - "Gün 23 Config Precedence Dependency Yönetimi Docker Cache ve Build Context"
status: completed
---

# ⚙️ Gün 23 — Config Precedence, Dependency Yönetimi ve Docker Cache / Build Context

> [!abstract] 🎯 Ana fikir  
> Bugün üç farklı konuda aslında aynı düşünme biçimini kullandım:
> 
> ```
> CONFIG
> → Birden fazla kaynak varsa hangisi kazanıyor?
> 
> DEPENDENCY
> → Bir paket nerede tanımlı, nerede kurulu, runtime gerçekten görüyor mu?
> 
> DOCKER CACHE
> → Bir build step hangi girdilere bağlı ve ilk cache invalidation nerede başladı?
> ```
> 
> Günün ortak prensibi:
> 
> **Bir şeyin tanımlı olması, gerçekten aktif/kurulu/kullanılan state olduğu anlamına gelmez.**

---

# ⚡ D+1 Geri Çağırma

## Parse → Normalize → Validate neden tek fonksiyona yığılmamalı?

Çünkü:

```
parse
→ formatı çöz

normalize
→ temsili standardize et

validate
→ application contract'ını kontrol et
```

ayrı sorumluluklardır.

Bunları ayırmak:

- kodu okumayı,
    
- debugging'i,
    
- test etmeyi,
    
- failure'ın hangi katmanda olduğunu anlamayı
    

kolaylaştırır.

---

## Record-Level vs File-Level Failure

Kapalı-kitap cevabımda:

```
record-level
→ logla + devam et

file-level
→ programı durdur
```

diye düşündüm.

> [!warning] Küçük düzeltme  
> **File-level failure mutlaka bütün process'i durdurur** diye evrensel kural yok.
> 
> Daha doğru model:
> 
> ```
> Record-level failure
> → tek record'un scope'u
> 
> File-level failure
> → bütün input source'un scope'u
> ```
> 
> Process'in tamamen durup durmaması uygulamanın failure policy'sine bağlıdır.
> 
> Kritik config dosyasının bozuk olması → fail-fast mantıklı olabilir.
> 
> Bağımsız iki kaynaktan yalnız birinin parse edilememesi → diğer kaynakla devam etmek de tasarıma göre mümkün olabilir.

---

# 🥇 Config Precedence

Bir uygulama aynı configuration değerini birden fazla kaynaktan alabilir.

Bugünkü örnek:

```
timeout
```

ve precedence:

```
DEFAULT
   ↓
CONFIG FILE
   ↓
ENVIRONMENT VARIABLE
   ↓
CLI ARGUMENT
```

Yani düşükten yükseğe:

> **default < config file < ENV < CLI**

Kaynak implementasyonda değer önce `30` olarak başlıyor, varsa `config.json`, sonra `APP_TIMEOUT`, en son `--timeout` ile override ediliyor.

---

# 🧠 Precedence Ne Demek?

Örneğin:

```
default = 30
config  = 60
ENV     = 15
CLI     = 5
```

sonuç:

```
5
```

olur.

Burada:

```
60 > 15 > 5
```

sayısal büyüklüğünün hiçbir önemi yok.

Kazanan:

```
en yüksek precedence'a sahip kaynak
```

olur.

---

# 🎯 Neden CLI En Yüksek?

Bu tasarımda:

```
Config file
→ daha kalıcı/genel ayar

Environment
→ çalışılan ortama özel override

CLI
→ bu spesifik invocation için açık kullanıcı tercihi
```

olarak düşünüldü.

Dolayısıyla:

```
APP_TIMEOUT=15 python day23.py --timeout 5
```

sonucu:

```
5
```

oldu. Gerçek deneyde config `60`, ENV `15`, CLI `5` sırasıyla birbirini override etti.

---

# 🧱 Config Precedence Neden Application Contract?

Çünkü aynı ayar farklı kaynaklarda bulunursa uygulamanın:

> **“Hangisi authoritative?”**

sorusuna deterministik cevap vermesi gerekir.

Bu yalnız implementation detayı değil, kullanıcının güvenebileceği davranış sözleşmesidir.

Kaynak kapalı-kitap turunda da precedence bu şekilde application contract olarak tanımlanmış.

---

# 🧯 Config Kodunda Yaptığım Hatalar

## 1. Config'teki gerçek değeri okumamak

TIRT:

```
if "timeout" in config:
    timeout = 60
```

Bu durumda config:

```
{
  "timeout": 999
}
```

olsa bile program `60` kullanır.

Doğru zihinsel model:

```
"timeout" key'i var mı?
↓
config["timeout"] ile gerçek value'yu al
```

Kaynak notta bu hardcode hatası özellikle fark edilmiş.

---

# 2. Dict'te Key Yerine Value Aramak

Soru:

```
Config dict'inde timeout ayarı var mı?
```

ise kontrol:

```
"timeout" in config
```

olmalıdır.

Ardından:

```
config["timeout"]
```

ile value alınır.

---

# 3. Environment Değeri String Gelir

```
os.getenv("APP_TIMEOUT")
```

örneğin:

```
APP_TIMEOUT=15
```

için Python'a:

```
"15"
```

döndürür.

Yani kabaca:

```
str | None
```

beklenir.

Bu yüzden:

```
"15"
↓ int()
15
```

dönüşümü gerekir.

Kaynakta ENV değerinin string olduğu özellikle öğrenilmiş.

---

# 4. `if x` vs `is not None`

Şunu kullanırsam:

```
if args.timeout:
```

aslında:

> “Değer truthy mi?”

diye sorarım.

Ama CLI:

```
--timeout 0
```

şeklinde verilmiş olabilir.

`0`:

```
falsy
```

olduğu için argüman verilmesine rağmen koşul çalışmaz.

Burada ihtiyacım:

> **“Argüman gerçekten sağlandı mı?”**

Bu yüzden:

```
args.timeout is not None
```

daha doğru.

---

# 🧠 Kısa Kural

```
if x
→ truthiness

x is not None
→ value sağlandı mı?
```

Bu ayrım kaynak notta ENV ve CLI override kontrolü için özellikle çıkarılmış.

---

# 📄 Config Yok vs Config Bozuk

Başlangıçta:

```
timeout = 30
```

default'u olsa bile doğrudan:

```
open("config.json")
```

yaparsam dosya yokken program patlar.

Yani:

```
default var
```

ama gerçekte:

```
fallback çalışamıyor
```

olur.

---

# ✅ Config Yoksa

```
os.path.isfile("config.json")
```

ile dosyanın gerçekten var ve file olup olmadığı kontrol edildi.

Sonuç:

```
config yok
→ default 30
```

---

# 💥 Config Var Ama Malformed

Gerçek deneyde config syntax'ı bozulunca:

```
JSONDecodeError: Extra data
```

oluştu.

Buradaki policy:

```
config yok
→ fallback

config var ama bozuk
→ fail-fast
```

> [!important]  
> **Config'in olmaması ile config'in mevcut olup bozuk olması aynı state değildir.**

Bozuk config'i sessizce yok saymak:

```
Kullanıcı config'in uygulandığını sanıyor
ama program default kullanıyor
```

gibi tehlikeli bir davranış yaratabilir.

---

# 🧪 Config Deneyleri

|State|Sonuç|
|---|---|
|yalnız config `60`|`60`|
|config + ENV `15`|`15`|
|config + ENV + CLI `5`|`5`|
|config yok|`30`|
|config malformed|`JSONDecodeError`|
|config var ama `timeout` yok|`30`|

Bu deneyler precedence contract'ını gerçekten doğruladı.

---

# 📦 Dependency Yönetimi

Dependency tarafındaki en önemli model:

```
SOURCE CODE
↓
DECLARED DEPENDENCIES
↓
INSTALLED ENVIRONMENT
↓
RUNTIME IMPORT
```

Bunlar aynı şey değildir.

> **declared ≠ installed ≠ runtime-visible**

Kaynak notta dependency bölümünün ana zihinsel modeli bu şekilde kurulmuş.

---

# 🐍 `venv`

```
python -m venv .venv
```

projeye özel izole Python environment oluşturur.

Aktivasyon:

```
source .venv/bin/activate
```

Sonra:

```
which python3
which pip
```

ile gerçekten `.venv` içindeki executable'ların kullanıldığı doğrulandı.

---

# ⚠️ `venv` Ne Değildir?

`venv`:

```
Python interpreter/package environment izolasyonu
```

sağlar.

Ama:

```
Docker container
tam OS izolasyonu
filesystem namespace izolasyonu
```

değildir.

Kapalı-kitap cevabındaki:

> **“venv Python package/runtime environment izolasyonudur; container değildir.”**

modeli doğru.

---

# 💥 Dependency Kurulu Değilse

Kod:

```
import rich
```

diyor.

Ama temiz `.venv` içinde `rich` yok.

Sonuç:

```
ModuleNotFoundError:
No module named 'rich'
```

Gerçek deneyde tam olarak runtime import katmanında failure oluştu.

---

# 📜 `pyproject.toml` Nedir?

Bu deneyde `pyproject.toml` proje metadata'sını ve dependency gereksinimini tanımlamak için kullanıldı.

Örnek yapı:

```
[project]
name = "day23-dependency-test"
version = "0.1.0"

dependencies = [
    "rich"
]
```

Bu:

> **“Bu projenin Rich'e ihtiyacı var.”**

demektir.

Ama:

> **“Rich şu anda environment'a kuruldu.”**

demek değildir.

---

# 🔥 En Önemli Dependency Ayrımı

Gerçek state:

```
pyproject.toml içinde rich ✅

pip show rich
→ bulunamadı ❌

import rich
→ ModuleNotFoundError ❌
```

Yani:

> **Dependency declaration ≠ installation**

Kaynak deneyde `pyproject.toml` oluşturulduktan sonra bile import başarısız olmaya devam etmiş.

---

# 📥 Dependency'yi Gerçekten Kurmak

```
python -m pip install rich
```

çalıştırılınca:

- `rich`
    
- `markdown-it-py`
    
- `pygments`
    
- `mdurl`
    

kuruldu.

Ardından:

```
pip show rich
```

paketin `.venv/.../site-packages` altında olduğunu gösterdi ve:

```
python dep_test.py
```

başarıyla:

```
runtime dependency'i gördü
```

çıktısını verdi.

---

# 🔗 Transitive Dependency

Ben doğrudan:

```
rich
```

istedim.

Ama Rich'in çalışması için başka paketler gerekti.

Bunlar:

> **Transitive dependency**

Yani:

```
Benim projem
↓
Rich
↓
Rich'in dependency'leri
```

---

# 📌 Dependency Constraint / Pinning

Üç temel yaklaşımı karşılaştırdım.

## `"rich"`

```
Belirli minimum/tam version constraint yok
```

Avantaj:

```
update esnekliği ↑
```

Dezavantaj:

```
farklı zamanlarda farklı sürüm kurulabilir
reproducibility ↓
```

---

## `"rich>=15.0.0"`

```
15.0.0 veya daha yeni
```

Avantaj:

```
yeni sürümlere geçiş kolay
```

Trade-off:

```
CI / install sonucu zamanla değişebilir
```

---

## `"rich==15.0.0"`

Sadece:

```
15.0.0
```

Avantaj:

```
reproducibility ↑
determinism ↑
```

Dezavantaj:

```
upgrade manuel
```

Kaynak notta bu trade-off'lar açıkça karşılaştırılmış.

---

# 🔧 Son Constraint Deneyi

Docker deneyinin ilerleyen kısmında dependency:

```
"rich>=15.0.0,<100"
```

şeklinde değiştirildi.

Bu:

```
minimum version
+
upper bound
```

tanımlar.

Yani tamamen açık uçlu `>=15.0.0` yerine belli bir compatibility sınırı koyulmuş olur.

---

# 🐳 Docker — Temel Zihinsel Model

```
Dockerfile
↓ docker build
Image
↓ docker run
Container
```

Kaynak Docker notunun temel modeli de bu şekilde kurulmuş.

---

# 📜 Dockerfile

Docker image'ın nasıl üretileceğini tanımlayan talimat dosyasıdır.

Instruction örnekleri:

```
FROM
WORKDIR
COPY
RUN
CMD
LABEL
```

---

# 📦 Image

Image:

```
çalışan process
```

değildir.

Kabaca:

```
filesystem layers
+
image config/metadata
```

içeren hazır şablondur.

---

# 🚀 Container

Container:

> **Image'dan başlatılmış çalışan örnektir.**

---

# 🗂️ Filesystem vs Filesystem Layer

Filesystem:

```
container/image içindeki dosya ve dizinlerin toplam görünümü
```

Filesystem layer:

```
önceki filesystem state'ine göre oluşan değişiklikler
```

Örneğin:

```
COPY app.py /app/app.py
```

kabaca:

```
“app.py eklendi/değişti”
```

farkını oluşturur.

Bütün filesystem'i tekrar yaratmak olarak düşünmemeliyim.

---

# 🔨 `RUN`

```
RUN ...
```

build sırasında gerçekten çalışır.

Örneğin:

```
RUN pip install rich
```

ise build sırasında pip çalışır ve dependency dosyaları image filesystem'ine eklenebilir.

Kısa model:

> `**RUN**` **= BUILD TIME'DA ŞİMDİ ÇALIŞTIR**

Kaynak notta `RUN` ile `CMD` arasındaki ayrım özellikle düzeltilmiş.

---

# ▶️ `CMD`

Başta:

```
CMD ne filesystem ne metadata değiştiriyor
```

diye düşündüm.

Filesystem tarafında doğrudan dosya yazmaması doğru olabilir ama metadata/config kısmı yanlış.

`CMD`:

```
build sırasında programı çalıştırmaz
```

Image config'e:

> **“Container başlatılırsa varsayılan command bu.”**

bilgisini kaydeder.

Kısa model:

> `**CMD**` **= RUNTIME İÇİN DEFAULT COMMAND'I KAYDET**

Kaynak dosyanın son kısmında bu hata tekrar açıkça düzeltilmiş.

---

# 🧠 `RUN` vs `CMD`

```
RUN
→ build time
→ gerçekten çalışır

CMD
→ runtime config
→ build sırasında çalışmaz
```

Bu yüzden:

> `CMD` çıktısı build sırasında oluşup image'da kalır

düşüncesi TIRT.

Program daha çalışmadı bile.

---

# 🗃️ Docker Cache

Docker bir build instruction'ın daha önce hesapladığı sonucu yeniden kullanabiliyorsa:

```
CACHE HIT
```

Kullanamıyorsa:

```
CACHE MISS
```

Eski cache sonucu artık girdilerle uyumlu değilse:

```
CACHE INVALIDATION
```

---

# ⚡ Cache Zinciri

Önemli:

> Bir instruction'ın cache'i invalid olursa sonraki instruction'lar da bundan etkilenebilir.

Dolayısıyla Dockerfile sırası:

```
yalnız okunabilirlik
```

değil:

```
build performance
```

açısından da önemlidir.

Kaynakta bu mekanizma özellikle vurgulanmış.

---

# 🧪 Controlled Comparison — Dockerfile A

İlk yaklaşım:

```
COPY pyproject.toml day23.py dep_test.py config.json ./

RUN dependency-install...
```

Burada:

```
dependency metadata
+
application source
```

aynı `COPY` instruction'ının input'u.

---

# İlk Build

Yaklaşık:

```
6.5 saniye
```

ve dependency install:

```
5.7 saniye
```

sürdü.

---

# Hiçbir Şey Değişmeden İkinci Build

```
WORKDIR → CACHED
COPY → CACHED
RUN dependency install → CACHED
```

Build:

```
~0.1 saniye
```

Bu gerçek cache hit kanıtıydı.

---

# 💥 Sadece `day23.py` Değişince

Dependency:

```
değişmedi
```

Ama source dosyası aynı `COPY` instruction'ında.

Sonuç:

```
day23.py değişti
↓
COPY CACHE MISS
↓
sonraki RUN da cache'den çıkıyor
↓
dependency install tekrar
```

Yaklaşık:

```
5.4 saniye
```

yeniden harcandı.

---

# 🚨 Root Cause Neydi?

İlk bakışta:

```
Dependency RUN neden tekrar çalışıyor?
```

diye bakabilirim.

Ama root cause:

```
dependency install'dan ÖNCEKİ
COPY cache boundary
```

idi.

> [!important]  
> **Tekrar çalışan step bazen root cause değil, upstream cache miss'in semptomudur.**

---

# ✅ Dockerfile B — Daha İyi Cache Boundary

Yeni yapı:

```
COPY pyproject.toml ./

RUN dependency-install...

COPY day23.py dep_test.py config.json ./
```

Burada dependency metadata source'tan ayrıldı.

Kaynak Dockerfile.B gerçekten bu sırayla oluşturulmuş.

---

# 🧪 Sadece Source Değişince

`day23.py` değiştirildi.

Bu kez:

```
COPY pyproject.toml
→ CACHED

dependency RUN
→ CACHED

source COPY
→ yeniden çalıştı
```

Build:

```
~0.2 saniye
```

sürdü.

---

# 🎯 Cache Tasarımından Çıkardığım Kural

Basit hafıza kancası:

> **Seyrek değişen ve pahalı adımları, sık değişen source'tan ayır.**

Ama bunu:

```
“dependency HER ZAMAN önce”
```

şeklinde kör ezberlememeliyim.

Asıl soru:

> **Bu instruction hangi input'lara gerçekten bağımlı?**

Kaynak notta da bu uyarı açıkça yapılmış.

---

# 🔄 Dependency Metadata Değişirse?

Sonra:

```
pyproject.toml değişti
```

Bu durumda:

```
COPY pyproject.toml
→ CACHE MISS

dependency RUN
→ tekrar çalışır

source COPY
→ downstream olduğu için yeniden işlenir
```

Bu kez dependency install'ın tekrar çalışması **doğru davranıştı**.

Çünkü dependency input'u gerçekten değişmişti.

---

# 🧠 Cache'in Amacı

Cache:

```
“Hiçbir şeyi tekrar yapma”
```

değildir.

Doğru:

> **“Girdiler değişmediyse gereksiz işi tekrar yapma.”**

---

# 🔬 Cache Debugging Refleksi

Semptom:

```
Source'ta tek satır değiştirdim
ama pip install tekrar çalıştı
```

İlk soru:

> **İlk CACHE MISS nerede?**

Değil:

> “RUN bozuk herhalde.”

Kaynak notun debugging refleksi de bu şekilde çıkarılmış.

---

# 🧪 Cache İçin Ayırıcı Deney

```
1. Hiçbir şeyi değiştirmeden iki build
   ↓
   Cache genel olarak çalışıyor mu?

2. Yalnız source değiştir
   ↓
   İlk CACHE MISS nerede?

3. Yalnız dependency metadata değiştir
   ↓
   Dependency step yeniden çalışıyor mu?
```

Böylece:

```
Semptom
↓
Hipotez
↓
Ayırıcı deney
↓
Kanıt
↓
Teknik hüküm
```

modeli kullanılır.

---

# 🕰️ `docker image history`

```
docker image history day23-cache-b
```

ile final image'ın history yapısı incelendi.

Gerçek çıktıda:

```
CMD
→ 0B

source COPY
→ ~20.5kB

dependency RUN
→ ~25.6MB

COPY pyproject.toml
→ ~12.3kB
```

görüldü.

---

# `CMD` Neden `0B`?

TIRT yorum:

```
0B
→ CMD hiçbir şey yapmıyor
```

Hayır.

Daha doğru:

```
Filesystem'e data eklemiyor
ama image config'te runtime default command tutuyor
```

---

# `RUN` Neden Büyük?

Dependency install:

```
package files
metadata
dependencies
```

gibi gerçek filesystem değişiklikleri oluşturduğu için history'de yaklaşık:

```
25.6MB
```

görüldü.

---

# 📂 `WORKDIR` Nüansı

Başta:

```
WORKDIR sadece config
```

gibi düşündüm.

Ama:

```
WORKDIR /app
```

dizin yoksa onu oluşturabilir.

Dolayısıyla:

> **“Metadata gibi görünen instruction filesystem'e asla dokunmaz.”**

gibi genel bir kural kurmak doğru değil.

---

# 📜 Build Log vs `docker history`

Bunlar farklı sorulara cevap verir.

## Build log

```
Hangi instruction CACHED?
İlk CACHE MISS nerede?
Ne yeniden çalıştı?
```

---

## `docker history`

```
Final image hangi instruction/history kayıtlarından oluşuyor?
Yaklaşık layer boyutları ne?
```

Kaynakta bu ayrım özellikle yapılmış.

---

# 📦 Build Context

```
docker build ... .
```

komutunun sonundaki:

```
.
```

build context'i belirler.

Yani Docker build'in input olarak erişebildiği dosya alanı.

---

# 🧪 `junk.bin` Deneyi

Yaklaşık:

```
20 MiB
```

dosya oluşturuldu.

`.dockerignore` yokken build log:

```
transferring context: 20.98MB
```

gösterdi.

Dockerfile:

```
COPY junk.bin /tmp/junk.bin
```

başarılı oldu.

---

# 🚫 `.dockerignore`

Sonra:

```
junk.bin
```

`.dockerignore` içine eklendi.

Yeni build:

```
transferring context: 2B
```

seviyesine düştü.

Ve:

```
CopyIgnoredFile
"/junk.bin": not found
```

ile `COPY` başarısız oldu.

---

# 🧠 Dosya Diskte Var Ama Docker Bulamıyor?

Evet.

Çünkü:

```
Host filesystem
→ junk.bin var

Docker build context
→ .dockerignore yüzünden junk.bin yok
```

Bu çok önemli.

> **Host'ta var olmak ≠ build context'te bulunmak**

---

# `.gitignore` vs `.dockerignore`

Sonra `junk.bin`:

```
.dockerignore'dan çıkarıldı
.gitignore'a eklendi
```

Build tekrar:

```
transferring context: 20.98MB
```

gösterdi ve `COPY` başarılı oldu.

Böylece:

```
.gitignore
→ Git tracking/version-control boundary

.dockerignore
→ Docker build-context boundary
```

olduğu deneyle kanıtlandı.

---

# 🔥 Çok Kritik Ayrım

```
.gitignore'da
→ Docker'ın umurunda olmak zorunda değil

.dockerignore'da
→ Git'in umurunda olmak zorunda değil
```

İki dosya farklı sistemlerin sınırını yönetiyor.

Kaynak notta bu sonuç açıkça çıkarılmış.

---

# 🧯 Yaptığım Başlıca Hatalar

## 1. `COPY`yi cache özelliği sandım

TIRT.

```
COPY
→ Dockerfile instruction

Cache
→ build sonucunu reuse eden mekanizma
```

---

## 2. `COPY` Container'a Dosya Kopyalar Dedim

Build sırasında henüz container çalışmıyor.

Doğrusu:

```
Host/build context
↓ COPY
oluşturulmakta olan image filesystem
```

Container daha sonra:

```
docker run
```

ile image'dan başlatılır.

Kaynak notta bu hata özellikle düzeltilmiş.

---

## 3. Filesystem ile Layer'ı Karıştırdım

```
Filesystem
→ toplam görünüm

Filesystem layer
→ önceki state'e göre değişiklik
```

---

## 4. `CMD` Metadata Değiştirmez Dedim

TIRT.

`CMD` image config/metadata tarafına runtime default command bilgisini kaydeder.

---

## 5. `CMD` Çıktısı Build'de Kalır Sandım

TIRT.

`CMD` içindeki program build sırasında çalışmaz.

```
RUN
→ build sırasında çalışır

CMD
→ container runtime için tanımlanır
```

Kaynak dosyanın final özetindeki düzeltme de bu.

---

# 🧠 Kafaya Kazı

> [!quote]  
> Config precedence kaynakların authoritative sırasıdır; sayıların büyüklüğü değildir.

> [!quote]  
> `default < config < ENV < CLI`.

> [!quote]  
> Config yokluğu ile malformed config aynı failure değildir.

> [!quote]  
> `if x` truthiness sorar; `is not None` sağlanmışlık durumunu sorar.

> [!quote]  
> Source dependency istemesi, dependency'nin kurulu olduğu anlamına gelmez.

> [!quote]  
> `pyproject.toml` declaration yapar; `pip` environment'ı değiştirir.

> [!quote]  
> `venv` Python environment izolasyonudur, container değildir.

> [!quote]  
> Dependency modeli: declared → installed → runtime-visible.

> [!quote]  
> Gevşek constraint update esnekliği; sıkı pin reproducibility getirir.

> [!quote]  
> `RUN` build sırasında gerçekten çalışır.

> [!quote]  
> `CMD` runtime default command bilgisini image config'e kaydeder.

> [!quote]  
> Filesystem layer bütün filesystem değildir; önceki state'e göre değişikliktir.

> [!quote]  
> Cache'in amacı her şeyi cache'lemek değil, gereksiz işi tekrar etmemektir.

> [!quote]  
> Bir step tekrar çalışıyorsa ilk CACHE MISS'i bul.

> [!quote]  
> Sık değişen source ile pahalı dependency input'unu gereksiz yere aynı cache boundary'ye bağlama.

> [!quote]  
> Build log cache debugging içindir; `docker history` final image history'sini inceler.

> [!quote]  
> Host'ta bulunan dosya `.dockerignore` nedeniyle build context'te olmayabilir.

> [!quote]  
> `.gitignore` ve `.dockerignore` farklı sistemlerin sınırlarını yönetir.

---

# 📌 30 Saniyelik Özet

```
CONFIG
default
↓
config file
↓
ENV
↓
CLI

EN YÜKSEK
→ CLI

CONFIG YOK
→ fallback

CONFIG MALFORMED
→ fail-fast

ENV
os.getenv()
→ str | None

VARLIK
is not None

TRUTHINESS
if x

DEPENDENCY
source
↓
declared dependency
↓
installed environment
↓
runtime import

pyproject.toml
→ dependency declaration

pip
→ gerçek installation

venv
→ izole Python environment

DOCKER
Dockerfile
↓ build
Image
↓ run
Container

RUN
→ build time

CMD
→ runtime default command metadata

CACHE
HIT
→ eski sonuç kullanılabilir

MISS
→ step yeniden gerekir

INVALIDATION
→ eski sonuç artık input'lara uymuyor

İYİ BOUNDARY
pyproject
↓
dependency install
↓
source COPY

DEBUG
“pip niye tekrar çalıştı?”
↓
İLK CACHE MISS NEREDE?

HISTORY
docker image history
→ final image instruction/size history

CONTEXT
docker build ... .
→ . build context

.dockerignore
→ Docker context boundary

.gitignore
→ Git tracking boundary
```

---

# ✅ Günün Kazanımları

- Config precedence application contract olarak öğrenildi
    
- `default < config < ENV < CLI` sırası uygulandı
    
- Config value hardcode etme hatası düzeltildi
    
- Dict key/value kontrolü ayrıldı
    
- ENV değerlerinin string geldiği pekiştirildi
    
- `if x` ile `is not None` ayrıldı
    
- Config yokluğu ve malformed config ayrıldı
    
- Missing config için fallback, malformed config için fail-fast politikası uygulandı
    
- Config precedence dört farklı deneyle doğrulandı
    
- Source / declared / installed / runtime dependency state'leri ayrıldı
    
- Temiz `venv` oluşturuldu
    
- `which python3` / `which pip` ile environment doğrulandı
    
- Dependency kurulu değilken runtime `ModuleNotFoundError` gözlemlendi
    
- `pyproject.toml` temel yapısı öğrenildi
    
- Dependency declaration'ın installation olmadığı deneyle kanıtlandı
    
- `pip install` ile gerçek environment state değiştirildi
    
- Transitive dependency kavramı öğrenildi
    
- Version constraint/pinning trade-off'u değerlendirildi
    
- `RUN` ve `CMD` build/runtime olarak ayrıldı
    
- Image ve container ayrımı tekrar pekiştirildi
    
- Filesystem ile filesystem layer ayrıldı
    
- Docker CACHE HIT / MISS / invalidation öğrenildi
    
- Aynı build'in ikinci çalıştırmasında gerçek cache hit gözlemlendi
    
- Kötü cache boundary nedeniyle source değişikliğinin dependency install'ı yeniden çalıştırdığı görüldü
    
- Dependency metadata source'tan ayrılarak Dockerfile cache davranışı iyileştirildi
    
- Source değişikliğinde dependency install'ın cache'de kaldığı deneyle kanıtlandı
    
- Dependency metadata değişince install'ın doğru şekilde yeniden çalıştığı görüldü
    
- Cache debugging için ilk CACHE MISS refleksi öğrenildi
    
- `docker image history` kullanıldı
    
- `CMD`nin `0B` olmasına rağmen image config etkisi olduğu öğrenildi
    
- `WORKDIR` için filesystem/config nüansı fark edildi
    
- Build log ve `docker history` ayrıldı
    
- Build context kavramı deneyle gözlemlendi
    
- 20 MiB test artifact ile context boyutu ölçüldü
    
- `.dockerignore` ile context'in küçüldüğü kanıtlandı
    
- Ignore edilen dosyanın `COPY` tarafından bulunamadığı görüldü
    
- Host filesystem ile Docker build context ayrıldı
    
- `.gitignore` ile `.dockerignore` deneyle karşılaştırıldı
    
- `.gitignore`ın Docker build context'i otomatik değiştirmediği kanıtlandı
    

> [!success] 🚀 Gün sonu sonucu  
> Gün 23'te aslında üç farklı alanda aynı debugging refleksi güçlendi:
> 
> ```
> CONFIG
> → Hangi kaynak gerçekten kazandı?
> 
> DEPENDENCY
> → Paket yalnız declared mı, gerçekten installed mı, runtime görüyor mu?
> 
> DOCKER
> → Tekrar çalışan step root cause mu,
>   yoksa daha önceki CACHE MISS'in sonucu mu?
> ```
> 
> Config tarafında:
> 
> ```
> default < config < ENV < CLI
> ```
> 
> dependency tarafında:
> 
> ```
> declared ≠ installed ≠ runtime-visible
> ```
> 
> Docker tarafında:
> 
> ```
> source değişti
> ↓
> ilk cache miss nerede?
> ↓
> downstream hangi step'leri etkiledi?
> ```
> 
> şeklinde düşünmeye başladım.
> 
> Günün en kritik cümlesi:
> 
> **Bir davranışı debug ederken yalnız başarısız olan son adıma bakma; o adımın hangi state ve upstream girdilerden üretildiğini geriye doğru takip et.**