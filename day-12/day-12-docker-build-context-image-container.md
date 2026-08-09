---
title: "Gün 12 — Docker Build Context, Dockerfile, Image ve Container"
tags:
  - coreops
  - python
  - linux
  - docker
  - dockerfile
  - build-context
  - image
  - container
  - copy
  - cmd
aliases:
  - "Gün 12 Docker Build Context Image ve Container"
status: completed
duration_minutes: 120
---

# 🐳 Gün 12 — Docker Build Context, Dockerfile, Image ve Container

> [!abstract] 🎯 Ana fikir  
> Bugünün ana zinciri:
> 
> ```text
> HOST DOSYALARI
>       ↓
> BUILD CONTEXT
>       ↓
> Dockerfile + COPY
>       ↓
> IMAGE
>       ↓
> docker run
>       ↓
> CONTAINER
>       ↓
> CMD
>       ↓
> PROGRAM
> ```
> 
> En kritik ayrım:
> 
> ```text
> Build context → Docker build sırasında hangi dosyalara erişebilir?
> Dockerfile    → Image nasıl oluşturulacak?
> Image         → Hazır filesystem + ayarlar
> Container     → Image'dan oluşturulan çalışan/durmuş örnek
> ```

---

# ⚡ 2 Dakikalık Geri Çağırma

Host ve container absolute path'lerinin farklı olabilmesinin sebebi:

```text
Host source path
→ Container içinde farklı target path'e bind mount edilebilir.
```

Örneğin:

```text
Host:
 /Users/polat/project

Container:
 /work
```

Path string'leri farklı olsa bile aynı dosya ağacı görülebilir.

---

# 🐍 Python — `summarizer()` ve Exit Code Sözleşmesi

## `0` ve sıfır dışı exit code

CLI programlarında temel sözleşme:

```text
0      → Başarı
0 dışı → Başarısızlık / hata durumu
```

Bu yüzden:

```python
sys.exit(main())
```

yapısı programın gerçek sonucunu shell veya Docker'a taşıyabilir.

---

# 🧱 Sorumluluk Ayrımı

Temiz akış:

```text
summarizer()
→ Dosyayı okur.
→ Metni işler.
→ Sonucu return eder.

main()
→ Fonksiyonu çağırır.
→ Beklenen exception'ları yakalar.
→ stdout/stderr kararını verir.
→ Exit code döndürür.

sys.exit(main())
→ Sonucu process exit code'una çevirir.
```

> [!important]  
> Veri işleyen fonksiyonun doğrudan `sys.exit()` çağırmaması tekrar kullanım ve test edilebilirlik açısından daha temizdir.

---

# 📂 Dosyayı Doğru Okumak

Fonksiyon:

```python
def summarizer(path):
    with open(path, encoding="utf-8") as file:
        metin = file.read()
```

Burada:

```text
path
→ Dosyanın adresi

file
→ Açılmış dosya nesnesi

metin
→ Dosyadan okunan str içerik
```

ayrımı vardır.

TIRT zihinsel model:

```python
open(metin)
metin.read()
```

Çünkü `metin`, dosya yolu olarak bir string ise `.read()` metoduna sahip değildir.

Doğru akış:

```text
"input.txt"
     ↓
open()
     ↓
file object
     ↓
read()
     ↓
str
```

---

# ✂️ İlk 20 Kelimelik Basit Özet

```python
kelimeler = metin.split()
ilk_20 = kelimeler[:20]
özet = " ".join(ilk_20)
```

> [!danger] Kaynak koddaki sinsi hata  
> Kodda:
> 
> `özet = "".join(ilk_20)`
> 
> kullanılmış.
> 
> Bu durumda kelimelerin arasındaki boşluklar kaybolur:
> 
> ```text
> ["Docker", "bir", "araçtır"]
>          ↓
> "Dockerbiraraçtır"
> ```
> 
> İstenen normal metin özeti için:
> 
> `özet = " ".join(ilk_20)`
> 
> kullanılmalıdır. Kaynak notunda da doğru sürüm bu şekilde belirtilmiş.

---

# `...` Ne Zaman Eklenmeli?

Metin 20 kelimeden uzunsa gerçekten kesilmiştir:

```python
if len(kelimeler) > 20:
    return özet + "..."
```

Ama 20 veya daha az kelime varsa:

```python
return metin
```

daha doğrudur.

Çünkü:

```text
20 kelime
→ Hiçbir şey kesilmedi.
→ "..." gereksiz.

21 kelime
→ Sonrası kesildi.
→ "..." anlamlı.
```

---

# ✅ Temizlenmiş Python Yapısı

```python
import sys


def summarizer(path):
    with open(path, encoding="utf-8") as file:
        metin = file.read()

    kelimeler = metin.split()
    ilk_20 = kelimeler[:20]
    özet = " ".join(ilk_20)

    if len(kelimeler) > 20:
        return özet + "..."

    return metin


def main():
    try:
        print(summarizer("input.txt"))
        return 0

    except FileNotFoundError as hata:
        print(
            f"Dosya bulunamadı: {hata}",
            file=sys.stderr,
        )
        return 11

    except IsADirectoryError as hata:
        print(
            f"Verilen path bir dizin: {hata}",
            file=sys.stderr,
        )
        return 22


if __name__ == "__main__":
    sys.exit(main())
```

---

# 🧪 Neden Önce Hostta Test?

Önce:

```bash
python3 day12.py
echo $?
```

ile programı host ortamında doğrulamak faydalıdır.

Çünkü hostta zaten bozuk olan program Docker içinde de bozuk çalışabilir.

Zihinsel model:

```text
Önce:
Kod doğru mu?

Sonra:
Docker ortamı doğru mu?
```

> [!important]  
> Docker kötü tasarlanmış veya hatalı Python kodunu düzeltmez.
> 
> Yalnızca programın çalışma ortamını değiştirir.

---

# 🐧 Linux / Docker CLI — Build Context

```bash
docker build .
```

komutundaki son:

```text
.
```

**build context**'tir.

Burada:

```text
. = mevcut çalışma dizini
```

Dolayısıyla:

```bash
pwd
```

çıktısı:

```text
/Users/polat/CODING/Gelişim/Gelişmiş
```

ise:

```bash
docker build .
```

yaklaşık olarak:

```text
Build context =
/Users/polat/CODING/Gelişim/Gelişmiş
```

demektir.

---

# 📦 Build Context Nedir?

Build context:

> Docker'ın build sırasında kullanmasına izin verilen dosya ağacı.

Örnek:

```text
day12/
├── Dockerfile
├── day12.py
└── input.txt
```

Bu dizinde:

```bash
docker build .
```

çalıştırılırsa context:

```text
day12/
```

olur.

Docker build sırasında bu alan içindeki dosyalara erişebilir.

---

> [!danger] Kafaya kazı  
> Bir dosyanın build context içinde bulunması:
> 
> ```text
> Image içine otomatik girdi
> ```
> 
> anlamına gelmez.
> 
> Yalnızca:
> 
> ```text
> Docker build sırasında bu dosyayı kullanabilir.
> ```
> 
> anlamına gelir.

---

# 🧭 Build Context'i Ne Belirler?

`docker build` komutunun **sonundaki path**.

```bash
docker build .
```

→ Context = `.`

```bash
docker build app
```

→ Context = `app/`

---

# 📄 Dockerfile ile Build Context Aynı Şey Değil

Üç kavram:

```text
CWD
→ Terminalde ben neredeyim?

Dockerfile
→ Build talimatları nerede?

Build Context
→ Docker build sırasında hangi dosya ağacına erişebilir?
```

Örneğin:

```bash
docker build \
  -f app/Dockerfile \
  .
```

şöyle okunur:

```text
Dockerfile:
app/Dockerfile

Build context:
.
```

Dockerfile'ın bulunduğu klasör context'i otomatik belirlemez.

---

# ❌ `docker build.` Hatası

TIRT:

```bash
docker build.
```

Shell/Docker bunu:

```text
build.
```

isimli farklı bir Docker alt komutu gibi algılayabilir.

Doğru:

```bash
docker build .
```

Arada boşluk gerekir.

```text
docker
build
.
```

üç ayrı argüman/parçadır.

---

# ❌ Dockerfile Yoksa

İlk deney:

```bash
docker build .
```

sonucu:

```text
failed to read dockerfile:
open Dockerfile:
no such file or directory
```

oldu.

Sebep:

```text
Build context vardı ✅
Dockerfile yoktu ❌
```

Varsayılan olarak Docker context kökünde:

```text
Dockerfile
```

isimli dosyayı arar.

Başka yerdeyse:

```bash
docker build \
  -f başka/Dockerfile \
  .
```

kullanılabilir.

---

# 📋 `COPY` — En Kritik Noktalardan Biri

Genel biçim:

```dockerfile
COPY kaynak hedef
```

İki taraf aynı filesystem'e ait değildir.

```text
COPY day12.py .
     │        │
     │        └─ Image filesystem'i
     │
     └─ Build context
```

---

# 📍 `COPY` Kaynağı Neye Göre Çözülür?

Kaynak path:

```text
Dockerfile'ın konumuna göre değil
Build context'in köküne göre
```

çözülür.

---

## Örnek 1

Context:

```text
day12/
├── Dockerfile
├── day12.py
└── input.txt
```

Dockerfile:

```dockerfile
COPY day12.py /app/
```

çalışabilir.

---

## Örnek 2 — Context parent dizin

```text
calisma/
└── day12/
    ├── Dockerfile
    └── day12.py
```

Context:

```text
calisma/
```

ise kaynak artık:

```text
day12/day12.py
```

olarak ifade edilebilir.

---

# 🔍 `COPY` Hatasında Kontrol Sırası

```text
1. pwd
2. docker build komutunun sonundaki context ne?
3. İstenen kaynak context içinde mi?
4. COPY yolu context root'una göre doğru mu?
5. .dockerignore dosyayı dışlıyor mu?
6. Dockerfile yazımı doğru mu?
```

> [!danger]  
> `COPY` hata verince sadece Dockerfile satırını suçlamak TIRT teşhistir.
> 
> Context yanlış seçilmiş olabilir.

---

# 📁 `COPY . .`

Dockerfile:

```dockerfile
WORKDIR /work
COPY . .
```

Buradaki noktalar aynı şeyi ifade etmez.

## İlk `.`

```text
Build context'in içeriği
```

## İkinci `.`

```text
Image içindeki mevcut çalışma dizini
```

`WORKDIR /work` olduğu için:

```text
İkinci . → /work
```

Sonuç:

```text
Build context içeriği
       ↓
Image /work/
```

---

# ⚠️ `COPY . .` Her Zaman İyi mi?

Hayır.

Context'te:

```text
.git/
.env
__pycache__/
loglar/
test çıktıları
```

gibi gereksiz veya hassas dosyalar bulunabilir.

Bu yüzden:

```text
.dockerignore
```

önemlidir.

Daha kontrollü seçenek:

```dockerfile
COPY day12.py input.txt .
```

---

# 🐳 Günün Dockerfile'ı

```dockerfile
FROM python:3.12-slim

WORKDIR /work

COPY . .

CMD ["python", "day12.py"]
```

---

# 🧱 `FROM python:3.12-slim`

```dockerfile
FROM python:3.12-slim
```

Image'ın temelini seçer.

Bu temel image içinde:

- Python 3.12
    
- Minimal Debian tabanlı userspace
    
- Python'ın ihtiyaç duyduğu temel runtime bileşenleri
    

hazır gelir.

Bu yüzden Python'ı sıfırdan kurmak gerekmez.

---

# 📁 `WORKDIR /work`

```dockerfile
WORKDIR /work
```

şunu yapar:

```text
Image/container çalışma dizini → /work
```

Dosya kopyalamaz.

Sonraki relative talimatları etkiler.

Örneğin:

```dockerfile
COPY . .
```

ikinci `.` için `/work` kullanılır.

Runtime'da da:

```dockerfile
CMD ["python", "day12.py"]
```

`/work` çalışma dizininde çalışır.

---

# 📋 `COPY . .`

Build context içindeki seçili dosyaları image filesystem'ine kopyalar.

Bu build'den sonra image yaklaşık olarak:

```text
/work/
├── day12.py
├── input.txt
├── ...
```

içeriğine sahip olabilir.

> [!warning]  
> Hangi dosyaların gerçekten context'e gönderildiği `.dockerignore` tarafından da etkilenir.

---

# ▶️ `CMD`

```dockerfile
CMD ["python", "day12.py"]
```

build sırasında Python script'ini çalıştırmaz.

Image'a şu varsayılan komutu kaydeder:

```text
Bu image'dan container başlarsa:
python day12.py çalıştır.
```

Akış:

```text
docker build
     ↓
CMD bilgisi image'a kaydedilir
     ↓
IMAGE
     ↓
docker run
     ↓
CMD çalışır
```

`CMD` runtime davranışıdır.

---

# ⏱️ Build Time vs Runtime

## Build Time

```bash
docker build
```

Image hazırlanır.

Bu Dockerfile'da:

```text
FROM
WORKDIR
COPY
```

image yapısını hazırlayan talimatlardır.

## Runtime

```bash
docker run
```

Image'dan container oluşturulur.

Sonrasında:

```text
CMD
```

devreye girer.

---

# 🏗️ Image Build Etmek

```bash
docker build \
  -t day12sel \
  .
```

Parçaları:

```text
docker build
→ Image oluştur.

-t
→ Tag ver.

day12sel
→ Repository/image adı.

.
→ Build context.
```

Başka tag belirtilmezse sonuç genellikle:

```text
day12sel:latest
```

olarak görünür.

---

# 🏷️ Tag ile Container İsmi Aynı Şey Değildir

```bash
docker build -t day12sel .
```

buradaki:

```text
day12sel
```

**image tag/repository adıdır.**

Container adı değildir.

Container çalıştırmak:

```bash
docker run day12sel
```

Docker image'dan yeni bir container oluşturur.

Docker container'a otomatik isim verebilir:

```text
IMAGE       NAMES
day12sel    cool_lederberg
```

Burada:

```text
day12sel
→ Image

cool_lederberg
→ Container
```

---

# 🏷️ Container'a Kendim İsim Vermek

```bash
docker run \
  --name day12-container \
  day12sel
```

Genel yapı:

```text
docker run [OPTIONS] IMAGE [COMMAND] [ARG...]
```

Parçalama:

```text
docker
→ Docker CLI

run
→ Yeni container oluştur ve çalıştır

--name
→ Container adını ben belirleyeceğim

day12-container
→ Container'ın adı

day12sel
→ Kullanılacak image
```

Türkçesi:

> `day12sel` image'ından yeni bir container oluştur, adını `day12-container` koy ve çalıştır.

---

# 🖼️ Image vs Container

## `docker images`

veya:

```bash
docker image ls
```

bilgisayardaki **image'ları** gösterir.

Örnek:

```text
python:3.12-slim
ubuntu:24.04
day12sel
```

Image:

```text
Kalıp / şablon
```

---

## `docker ps`

Yalnız şu anda çalışan container'ları gösterir.

## `docker ps -a`

Çalışan + durmuş container kayıtlarını gösterir.

Container:

```text
Image'dan oluşturulmuş örnek
```

---

> [!danger] TIRT düşünce
> 
> ```text
> docker images
> =
> docker ps -a
> ```
> 
> Yanlış.
> 
> ```text
> images → Kalıplar
> ps -a  → O kalıplardan oluşturulmuş container örnekleri
> ```

---

# 🏭 Bir Image'dan Birden Fazla Container

```text
day12sel IMAGE
      │
      ├── Container A
      ├── Container B
      └── Container C
```

Her:

```bash
docker run day12sel
```

yeni bir container oluşturabilir.

---

# 🛑 Container Neden Hemen Duruyor?

Dockerfile:

```dockerfile
CMD ["python", "day12.py"]
```

Container başladığında:

```text
python day12.py
       ↓
Script çalışır
       ↓
Script tamamlanır
       ↓
Ana process biter
       ↓
Container durur
```

Bu yüzden:

```text
Exited (0)
```

normal olabilir.

`0`:

```text
Ana process başarıyla tamamlandı.
```

demektir.

> [!important]  
> Container'ın yaşam süresi ana process'inin yaşam süresiyle bağlantılıdır.

---

# 🧹 `--rm`

```bash
docker run --rm day12sel
```

container durunca container kaydını otomatik siler.

Bu yüzden sonrasında:

```bash
docker ps -a
```

içinde göremezsin.

---

# ♻️ Aynı Container İsmini Tekrar Kullanmak

Container durmuş olsa bile silinmediyse:

```text
day12-container
```

ismi hâlâ ona aittir.

Tekrar:

```bash
docker run \
  --name day12-container \
  day12sel
```

yaparsan isim çakışması oluşabilir.

Çözümler:

```text
Mevcut container'ı sil
veya
Başka isim ver
veya
Var olan container'ı yeniden başlat
```

---

# 🔗 Bind Mount ile `COPY` Arasındaki Kritik Fark

## Bind Mount

Runtime sırasında:

```text
HOST
 ↕
CONTAINER
```

Container host dosyalarına bağlıdır.

Host dosyası değişirse container yeni veriyi görebilir.

---

## `COPY`

Build sırasında:

```text
HOST / BUILD CONTEXT
          ↓
        COPY
          ↓
        IMAGE
          ↓
      CONTAINER
```

Dosya image'ın filesystem'ine alınır.

Runtime'da host dosyasına canlı bağ yoktur.

---

# 🔥 Neden Artık Bind Mount Gerekmiyor?

Dockerfile:

```dockerfile
COPY . .
```

ile:

```text
day12.py
input.txt
```

build sırasında image'a alınmış durumda.

Dolayısıyla runtime:

```bash
docker run day12sel
```

sırasında container dosyaları image'dan alır.

Şunlara gerek kalmaz:

```text
-v ❌
--mount ❌
```

Bu kullanımın kaynaktaki gözlemi de tam olarak buydu.

---

# 🧊 Image Snapshot Mantığı

En önemli deney:

```text
1. Image build edildi.
2. input.txt değiştirildi.
3. Aynı image tekrar docker run ile çalıştırıldı.
4. Container eski içeriği gördü.
```

Bu beklenen davranıştır.

Neden?

```text
BUILD CONTEXT
   ↓
COPY input.txt
   ↓
IMAGE içinde o anki versiyon
   ↓
docker run
   ↓
Container eski image snapshot'ını görür
```

Hostta sonradan:

```bash
nano input.txt
```

ile dosyayı değiştirmek mevcut image'ı değiştirmez.

---

# 🔄 Yeni İçeriği Nasıl Alırım?

Host dosyası değiştiyse image'ı yeniden build et:

```bash
docker build \
  -t day12sel \
  .
```

Sonra:

```bash
docker run day12sel
```

Yeni container yeni image içeriğini kullanır.

---

> [!danger] Kafaya kazı
> 
> ```text
> COPY
> → Canlı bağlantı değildir.
> 
> COPY
> → Build anındaki içeriği image'a alır.
> ```

Bind mount ile en temel fark budur.

---

# 🧹 `.dockerignore`

`COPY . .` kullanıyorsan özellikle önemlidir.

Örnek:

```text
.git
__pycache__
*.pyc
.env
.venv
output/
```

gibi içerikler build context'ten çıkarılabilir.

Amaç:

- Gereksiz build context'i küçültmek
    
- Gereksiz dosyaların image'a girmesini önlemek
    
- Hassas dosya riskini azaltmak
    
- Cache davranışını iyileştirmek
    

---

# 🌱 Her Image Başka Image'a mı Dayanır?

Hayır.

Özel:

```dockerfile
FROM scratch
```

kullanımı vardır.

`scratch`:

```text
Boş başlangıç
```

olarak düşünülebilir.

Örneğin:

```dockerfile
FROM scratch

COPY program /program

CMD ["/program"]
```

Bu image içinde:

```text
bash olmayabilir
ls olmayabilir
Python olmayabilir
package manager olmayabilir
```

Yalnızca eklediğin dosyalar bulunabilir.

---

# 🥚 Image Zincirinin Başlangıcı

Zincir sonsuza gitmek zorunda değildir.

Kavramsal olarak:

```text
Root filesystem / scratch
          ↓
Debian tabanlı filesystem
          ↓
python:3.12-slim
          ↓
day12sel
```

şeklinde düşünülebilir.

---

# 🧠 Image Linux Kernel Taşır mı?

Normal Docker image'ı kendi tam Linux kernel'ini taşımaz.

Image'ın ana içeriği:

```text
Filesystem
Programlar
Kütüphaneler
Config
Metadata
```

Container'ın system call'larını karşılayan kernel çalışma ortamından sağlanır.

---

# 🍎 Mac'te Linux Container

macOS Linux kernel olmadığı için Docker Desktop arka planda Linux ortamı sağlar.

Zihinsel model:

```text
macOS
  ↓
Docker Desktop
  ↓
Linux VM
  ↓
Linux Kernel
  ↓
Container'lar
```

Bu yüzden:

```text
python:3.12-slim image'ının içinde ayrı bir Linux kernel yoktur.
```

---

# 🧯 Hata Avı

## 1. `sys.exit(0)` her yerde kullanılır

TIRT.

Program hata verdiğinde de başarı sinyali üretme riski vardır.

---

## 2. Veri işleme fonksiyonu `sys.exit()` çağırmalıdır

TIRT.

Veri işleme ile process yönetimini birbirine bağlar.

---

## 3. `"".join(ilk_20)` normal özet üretir

TIRT.

Kelimeleri bitiştirir.

Doğru:

```python
" ".join(ilk_20)
```

---

## 4. `docker build.` doğrudur

TIRT.

Doğru:

```bash
docker build .
```

---

## 5. Dockerfile'ın bulunduğu klasör otomatik build context'tir

TIRT.

Context'i `docker build` komutunun sonundaki path belirler.

---

## 6. Context'teki her dosya image'a otomatik girer

TIRT.

Dosyaların image'a alınmasını `COPY` / `ADD` gibi talimatlar belirler.

---

## 7. `COPY` source host absolute path'idir

TIRT.

Source build context içindeki path'tir.

---

## 8. `WORKDIR` dosyaları kopyalar

TIRT.

Yalnız çalışma dizinini belirler.

---

## 9. `CMD` build sırasında çalışır

TIRT.

Image'a runtime varsayılan komutu olarak kaydedilir.

---

## 10. `docker build` container oluşturur

TIRT.

```text
docker build → IMAGE
docker run   → CONTAINER
```

---

## 11. `docker images` ile `docker ps -a` aynı şeyi gösterir

TIRT.

Image ve container farklı nesnelerdir.

---

## 12. Host dosyası değişince mevcut image da değişir

TIRT.

`COPY` build anında snapshot alır.

Image'ın güncellenmesi için yeni build gerekir.

---

## 13. Container eski içeriği görüyorsa Docker bozuk

TIRT.

Container eski image'dan oluşturuluyorsa eski build içeriğini görmesi beklenen davranıştır.

---

# 🧠 Kafaya Kazı

> [!quote]  
> Build context Docker'ın build sırasındaki malzeme kutusudur.

> [!quote]  
> Dockerfile tarif, context malzeme alanıdır.

> [!quote]  
> Context'i `docker build` komutunun sonundaki path belirler.

> [!quote]  
> `COPY` source build context'e, target image filesystem'ine aittir.

> [!quote]  
> Context içinde olmak image'a girmek anlamına gelmez.

> [!quote]  
> `WORKDIR` çalışma dizinidir; dosya kopyalamaz.

> [!quote]  
> `CMD` runtime varsayılan komutudur.

> [!quote]  
> `docker build` image üretir.

> [!quote]  
> `docker run` image'dan container oluşturur.

> [!quote]  
> Image ve container aynı şey değildir.

> [!quote]  
> Bir image'dan birçok container oluşturulabilir.

> [!quote]  
> Container ana process bittiğinde durur.

> [!quote]  
> `--rm`, durmuş container'ı otomatik temizler.

> [!quote]  
> Bind mount canlı host bağlantısıdır; `COPY` build snapshot'ıdır.

> [!quote]  
> Host dosyasını değiştirmek mevcut image'ı değiştirmez.

---

# 📌 30 Saniyelik Özet

```text
PYTHON
summarizer()       → Dosyayı işle, str döndür
main()             → Hata yönet, exit code döndür
sys.exit(main())   → Exit code'u dış dünyaya bildir
" ".join(...)      → Kelimeler arasına boşluk koy

DOCKER BUILD
docker build       → Image üret
.                  → Build context
Dockerfile         → Build tarifi
FROM               → Base image
WORKDIR            → Image/container CWD
COPY               → Context → Image filesystem
CMD                → Runtime varsayılan komutu

COPY
source             → Build context
target             → Image filesystem

IMAGE
day12sel           → Image/tag
docker images      → Image listesi

CONTAINER
docker run         → Yeni container
--name             → Container adı
docker ps          → Çalışan container'lar
docker ps -a       → Tüm container'lar
--rm               → Durunca sil

KRİTİK
Bind mount         → Runtime canlı bağlantı
COPY               → Build-time snapshot

Host dosyası değişti
≠
Mevcut image değişti
```

---

# ✅ Günün Kazanımları

-  Exit code sözleşmesi tekrar edildi
    
-  Veri işleme ile process yönetimi ayrıldı
    
-  `summarizer()` fonksiyonu oluşturuldu
    
-  `file.read()` ve path string ayrımı pekiştirildi
    
-  İlk 20 kelimelik özet mantığı kuruldu
    
-  `"".join()` ile `" ".join()` farkı düzeltildi
    
-  `main()` ile beklenen dosya hataları yönetildi
    
-  Host testi ile Docker testi katmanlara ayrıldı
    
-  Build context kavramı öğrenildi
    
-  CWD, Dockerfile ve build context ayrıldı
    
-  `docker build .` sözdizimi öğrenildi
    
-  Dockerfile bulunamadığında build hatası gözlemlendi
    
-  `COPY` source ve target filesystem'leri ayrıldı
    
-  `COPY` source'un context root'a göre çözüldüğü öğrenildi
    
-  `COPY . .` mantığı oturtuldu
    
-  `.dockerignore` ihtiyacı görüldü
    
-  `FROM python:3.12-slim` anlaşılmış oldu
    
-  `WORKDIR` ile `COPY` ayrıldı
    
-  `CMD` build/runtime ayrımı öğrenildi
    
-  Image tag mantığı öğrenildi
    
-  Bind mount kullanmadan container çalıştırıldı
    
-  Image ve container ayrıldı
    
-  `docker images`, `docker ps`, `docker ps -a` ayrıldı
    
-  Bir image'dan birden fazla container üretilebildiği görüldü
    
-  `Exited (0)` davranışı anlaşıldı
    
-  `--rm` davranışı öğrenildi
    
-  Container isimlendirme öğrenildi
    
-  `FROM scratch` ve root filesystem modeli görüldü
    
-  Docker image'ın kendi kernel'ini taşımadığı kavrandı
    
-  macOS üzerinde Docker Desktop Linux VM modeli öğrenildi
    
-  `COPY` ile bind mount arasındaki snapshot/canlı bağlantı farkı anlaşıldı
    
-  Host dosyası değişince yeniden build gerektiği deneyle doğrulandı
    

> [!success] 🚀 Gün sonu sonucu  
> Gün 12 sonunda Docker artık yalnızca:
> 
> ```text
> “Host klasörünü container'a bağlayıp Python çalıştıran araç”
> ```
> 
> olarak görülmüyor.
> 
> Asıl image üretim zinciri oturdu:
> 
> ```text
> BUILD CONTEXT
>      ↓
> Dockerfile
>      ↓
> COPY
>      ↓
> IMAGE
>      ↓
> docker run
>      ↓
> CONTAINER
>      ↓
> CMD
> ```
> 
> Günün en kritik cümlesi:
> 
> **Bind mount runtime'da host dosyasına canlı bağlantıdır; `COPY` ise build anındaki dosyayı image'ın içine alan bir snapshot mantığıdır.**
