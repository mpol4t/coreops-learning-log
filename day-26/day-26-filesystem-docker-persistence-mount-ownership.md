---
title: "Gün 26 — Filesystem Gözlemi, Docker Persistence, Mount, Ownership ve Disk State"
tags:
  - coreops
  - linux
  - filesystem
  - stat
  - du
  - df
  - docker
  - persistence
  - bind-mount
  - volume
  - ownership
  - permissions
  - git
aliases:
  - "Gün 26 Filesystem Docker Persistence Mount ve Ownership"
status: completed
---

# 💾 Gün 26 — Filesystem Gözlemi, Docker Persistence, Mount, Ownership ve Disk State

> [!abstract] 🎯 Ana fikir  
> Bugün filesystem tarafında en önemli öğrendiğim şey:
> 
> **Önce hangi state'i ölçmek istediğimi belirlemem gerekiyor.**
> 
> ```
> stat
> → tek filesystem nesnesinin metadata state'i
> 
> du
> → belirli file/directory tree'nin disk tüketimi
> 
> df
> → path'in bulunduğu filesystem'in capacity state'i
> 
> mount
> → bu path'i şu anda hangi filesystem görünümü sağlıyor?
> ```
> 
> Docker tarafında ise asıl soru:
> 
> ```
> “Dosya container'da mı?”
> ```
> 
> değil:
> 
> ```
> “Bu verinin gerçek backing storage'ı nerede
> ve lifecycle sahibi kim?”
> ```
> 
> Bunun cevabı:
> 
> ```
> image filesystem
> container writable layer
> bind mount / host filesystem
> named volume
> ```
> 
> seçeneklerinden biri olabilir.

---

# 🐳 İlk Persistence Deneyi — Mount Yok

İlk container'ı:

```
docker run -dit --name persist-test alpine sh
```

ile oluşturdum.

İlk çalıştırmada Alpine image localde olmadığı için Docker image'ı çekti ve container başladı.

Container içinde:

```
/test.txt
```

oluşturdum.

İçeriği:

```
ben runtime verisiyim
```

idi.

---

# 🛑 Stop → Start

Sonra:

```
docker stop
↓
docker start
```

yaptım.

Dosya hâlâ vardı.

Buradan çıkardığım sonuç:

> `**docker stop**` **container'ı silmez.**

Aynı container object ve aynı writable layer durmaya devam eder.

```
Container A
├── image filesystem
└── writable layer
    └── /test.txt
```

Stop:

```
running
↓
stopped
```

state değişimidir.

Storage object ortadan kalkmadığı için runtime verisi hâlâ bulunabilir.

---

# 💥 Remove → Recreate

Sonra:

```
docker rm -f persist-test
```

ile container'ı kaldırdım ve aynı Alpine image'dan yeniden:

```
persist-test
```

adında başka container oluşturdum.

Yeni container'da:

```
/test.txt
```

yoktu.

Ana ayrım:

```
STOP
→ container object kalır
→ writable layer kalır

REMOVE
→ container object gider
→ ona ait writable layer da gider
```

> [!important]  
> Aynı image'dan yeni container oluşturmak, eski container'ın writable layer'ını geri getirmez.

---

# 🧠 Container Writable Layer Lifecycle

Kafamdaki model:

```
IMAGE
↓
Container A
└── Writable Layer A

Container A remove
↓
Writable Layer A da gider
```

Yeni:

```
IMAGE
↓
Container B
└── Writable Layer B
```

Bu yeni layer boş bir runtime state ile başlar.

---

# ⚠️ Image Rebuild Meselesi

Şunu söylemek eksik:

> “Image rebuild olunca runtime veri gider.”

Daha doğru:

```
image rebuild
≠
mevcut container'ın writable layer'ını geriye dönük silmek
```

Ama:

```
image rebuild
+
old container remove
+
new container create
```

olursa yeni container eski writable-layer runtime verisini doğal olarak içermez.

Kaynak notta bu nüans özellikle ayrılmış.

---

# 🧩 `-dit`

Başta `-dit` bana tek seçenek gibi geliyordu.

Aslında:

```
-d
→ detached

-i
→ stdin açık tut

-t
→ pseudo-TTY ayır
```

Yani:

```
-dit = -d -i -t
```

Kaynak notta bu birleşim açık şekilde çıkarılmış.

---

# 🔗 Bind Mount

Bind mount'ta doğrudan gerçek bir host path'ini container filesystem'inde belirli bir path'e bağlıyorum.

Deney:

```
Host:
$PWD/bind-data

Container:
/data
```

Mount:

```
--mount type=bind,source="$PWD/bind-data",target=/data
```

Container içinden:

```
/data/test.txt
```

oluşturduğumda host tarafında:

```
bind-data/test.txt
```

olarak aynı içeriği gördüm.

---

# 🔄 Host Değiştirirse Container Ne Görür?

Host:

```
bind-data/test.txt
→ "host değiştirdi"
```

olarak değiştirdim.

Container:

```
/data/test.txt
```

okuduğunda yeni içeriği gördü.

Bu:

> Docker'ın dosyayı mount başında bir kere kopyalayıp bırakmadığını

gösteriyor.

Daha doğru model:

```
Host namespace:
.../bind-data/test.txt

Container namespace:
/data/test.txt

        ↓
aynı backing storage
```

---

# ♻️ Container Silinince Bind Data

Container'ı kaldırdım:

```
docker rm -f bind-test
```

ama hostta:

```
bind-data/test.txt
```

hâlâ vardı.

Aynı host path'i yeni container'a bağladığımda veri yine görüldü.

Dolayısıyla:

> **Bind mount verisinin lifecycle sahibi container değil, host-backed storage'dır.**

---

# 📦 Named Volume

Sonra:

```
docker volume create day26-data
```

ile Docker tarafından yönetilen ayrı bir storage object oluşturdum.

`docker volume inspect` çıktısında volume adı, driver'ı ve Docker-managed mountpoint'i görüldü.

---

# 🧠 Named Volume Modeli

```
Docker Volume
    day26-data
       ↑
       │
Container A
       │
Container B
```

Volume container'dan ayrı bir object.

Dolayısıyla:

```
Container A remove
≠
volume otomatik remove
```

---

# 🧪 Named Volume Persistence

Container:

```
volume-test
```

içinde volume'a:

```
named volume verisi
```

yazdım.

Container'ı kaldırdıktan sonra aynı volume'u yeni container'a mount ettim ve veri hâlâ vardı.

Bu şu lifecycle'ı kanıtlıyor:

```
Container lifecycle
≠
Named volume lifecycle
```

---

# ⚖️ Bind Mount vs Named Volume

## Bind mount

Source'u **ben host pathname olarak seçiyorum**.

Örneğin:

```
$PWD/project
→ /app
```

İyi kullanım:

- Source code
    
- Hosttan edit edeceğim dosyalar
    
- Host ve container aynı dosyaları doğrudan görsün istediğim durumlar
    

---

## Named volume

Source:

```
Docker-managed volume object
```

İyi kullanım:

- Database data
    
- Persistent application state
    
- Host üzerinde belirli pathname contract'ına bağlanmak istemediğim veri
    

Kaynak notun kısa kararı da aynı: host path paylaşımı için bind mount, Docker-managed persistent application data için named volume.

---

# 📌 Kısa Karar

```
Belirli HOST PATH önemli
→ bind mount

Container'dan bağımsız APPLICATION DATA önemli
→ named volume
```

---

# 👻 Mount Shadowing

Bugünün en güzel filesystem derslerinden biri.

Image build sırasında:

```
/data/image.txt
```

oluşturdum.

Mount olmadan:

```
image icindeki dosya
```

görünüyordu.

Sonra hosttaki boş:

```
empty-data/
```

directory'sini container'ın:

```
/data
```

path'ine bind mount ettim.

Bu kez `/data` boş görünüyordu.

---

# 🚨 İlk Yanlış Hüküm

TIRT:

> “Mount edince image.txt silindi.”

Hayır.

Dosya image layer içinde hâlâ bulunabilir.

Ama runtime path resolution:

```
/data
```

için artık mounted tree öne geçiyor.

Model:

```
IMAGE VIEW
/data/
└── image.txt

RUNTIME
empty-data/
      │
      └──── mount ───→ /data
```

Sonuç:

```
/data
→ mounted tree'yi gösterir
```

Alttaki image içeriği görünümde **obscured/shadowed** olur.

Kaynakta bu kavram açık biçimde “shadowed / obscured” olarak tanımlanmış.

---

# 🔥 Ana Soru

Dosya görünmüyorsa:

> “Silindi mi?”

diye atlama.

Önce:

> **Şu anda bu path'i hangi filesystem görünümü sağlıyor?**

sorusunu sor.

---

# 📊 `stat`

`stat`:

> **Tek bir filesystem nesnesinin metadata state'i nedir?**

sorusuna cevap verir.

Görebildiğim şeyler:

```
file type
logical size
blocks
inode
UID
GID
permission
link count
timestamps
```

Kaynak notta `stat` bu object-metadata sorusuyla tanımlanmış.

---

# 📏 Size vs Blocks

```
Size
→ logical file size

Blocks
→ filesystem'in gerçekten ayırdığı bloklarla ilişkili state
```

Özellikle sparse file gibi yapılarda:

```
logical size
≠
allocated storage
```

olabilir.

---

# 👤 UID/GID

Örneğin:

```
Uid: 501 / polat
Gid: 20 / staff
```

görüyorsam filesystem açısından asıl state:

```
501
20
```

numeric kimlikleridir.

`polat` ve `staff` isim resolution sonucudur.

> **Ownership'ın temel kimliği numeric UID/GID'dir.**

---

# 🔐 Ownership ≠ Permission

Örneğin:

```
0755
→ rwxr-xr-x
```

üç permission sınıfı:

```
owner → rwx
group → r-x
other → r-x
```

Ama önce process'in:

```
UID/GID
```

değerlerine bakıp hangi sınıfa düştüğünü belirlemeliyim.

Sonra o sınıfın permission bitleri uygulanır.

---

# 🍎 Mac + Docker Desktop Ownership Nüansı

Hostta bind-mounted file:

```
UID 501
GID 20
```

görünürken container içinden aynı file:

```
UID 0
GID 0
```

görüldü.

Bu deneydeki önemli ders:

> Mac + Docker Desktop arasında Linux VM / file-sharing / mapping katmanı bulunduğu için ownership görünümü host ve container arasında birebir aynı olmak zorunda değildir.

Kaynak not da bu sonucu özellikle vurgulamış.

Dolayısıyla bind mount permission debug ederken sadece:

```
username
```

karşılaştırmam.

Hangi namespace/environment'tan baktığımı da bilirim.

---

# 🚫 Ownership Failure Lab

Named volume:

```
perm-lab
```

state'i:

```
owner UID = 0
group GID = 0
mode = 0755
```

olarak ayarlandı.

Sonra process:

```
UID = 10001
GID = 10001
```

ile çalıştırıldı.

`touch /data/test.txt`:

```
Permission denied
```

verdi.

---

# 🧠 İlk Hipotezler

Semptom:

> UID 10001 process `/data` içine yazamıyor.

Hipotezler:

```
1. Mount read-only olabilir.

2. Process identity ile directory owner/group uyuşmuyor olabilir.

3. Process'in düştüğü permission class'ta write olmayabilir.
```

Kaynak debugging incident'ında bu üç hipotez ayrı kurulmuş.

---

# 🔬 En Küçük Ayırıcı Deney

Aynı volume'a:

```
UID 0
GID 0
```

ile yazdım.

Root başarılı şekilde:

```
root-can-write.txt
```

oluşturdu.

Böylece:

> **Mount tamamen read-only**

hipotezi ciddi şekilde zayıfladı.

---

# 🧮 Permission Kararı

State:

```
Directory:
UID=0
GID=0
mode=0755

Writer:
UID=10001
GID=10001
```

Writer:

```
owner değil
group değil
↓
other sınıfı
```

Other:

```
r-x
```

Write:

```
❌
```

Sonuç:

```
Permission denied
```

---

# ❌ `chmod 777` Basmak

En kolay:

```
chmod 777
```

olabilirdi.

Ama bu:

```
owner → rwx
group → rwx
other → rwx
```

yaparak problemi identity açısından çözmek yerine permission sınırını gereksiz yere gevşetir.

TIRT.

---

# ✅ Doğru Fix

Gerçek writer:

```
10001:10001
```

ise storage ownership'i:

```
chown 10001:10001 /data
```

yapıldı.

Sonra:

```
UID=10001
GID=10001
mode=0755
```

oldu.

Writer artık:

```
owner class
→ rwx
```

üzerinden write hakkı aldı.

Test:

```
yazabiliyorum
```

başarılı oldu.

---

# 🎯 Permission Debugging Refleksi

```
Permission denied
↓
chmod 777
```

değil.

Doğru sıra:

```
Process UID/GID ne?
↓
Target owner/group kim?
↓
Mode ne?
↓
Process hangi class'a düşüyor?
↓
O class'ta gereken permission var mı?
↓
Mount RW mi?
```

---

# 👤 `UNKNOWN` UID

`stat` içinde:

```
Uid: (10001/UNKNOWN)
```

görülmesi:

> Ownership bilinmiyor.

demek değil.

Numeric ownership:

```
10001
```

gayet belli.

Sadece Alpine içinde:

```
/etc/passwd
```

dosyasında UID 10001 için isim kaydı yok.

Dolayısıyla:

```
UNKNOWN username
≠
unknown UID
```

Kaynak notta bu ayrım açıkça yapılmış.

---

# 📦 `du`

`du`:

> **Verdiğim file/directory tree ne kadar disk alanı tüketiyor?**

sorusunu cevaplar.

Deney:

```
du -sh disk-lab
```

çıktı:

```
4.0K
```

idi.

Bu:

```
disk-lab tree
→ 4K
```

demektir.

Filesystem'in tamamı değil.

---

# 💽 `df`

`df`:

> **Bu path'in bulunduğu filesystem'in kapasitesi ne durumda?**

sorusuna cevap verir.

Aynı `disk-lab` için:

```
filesystem total ≈ 229G
used ≈ 178G
available ≈ 51G
```

görüldü.

Bu:

```
disk-lab = 178GB
```

demek değildir.

---

# 🔥 `du` vs `df`

Kısa:

```
du
→ TREE CONSUMPTION

df
→ FILESYSTEM CAPACITY
```

Bu yüzden:

```
du disk-lab → 4K

df disk-lab → filesystem 178G used
```

çelişmez.

Ölçülen nesne farklı.

Kaynak notun düzgün cevabı da bu ayrımı aynen kuruyor.

---

# 🐞 Directory Küçük ama Filesystem Dolu

Direkt:

> "`du` yanlış ölçüyor."

demek TIRT.

Hipotezler:

```
1. Alanı başka directory/file'lar tüketiyor olabilir.

2. Silinmiş ama hâlâ bir process tarafından açık tutulan büyük file olabilir.

3. Baktığım tree bütün filesystem'i kapsamıyor olabilir.
```

---

# 👻 Deleted-but-open File

Bu önemli Linux vakası:

```
File pathname
→ silindi
```

ama process'in file descriptor'ı hâlâ açıksa:

```
filesystem blocks
→ hemen serbest kalmayabilir
```

Bu durumda:

```
du
→ pathname üzerinden file'ı artık görmeyebilir

df
→ disk alanını hâlâ kullanılmış görebilir
```

Kaynak notta bu olasılık ayrıca belirtilmiş.

---

# 🗂️ Mount Zihinsel Modeli

Mount'u yalnız:

> “Disk takmak.”

diye düşünmek yetersiz.

Daha doğru:

> **Bir filesystem/tree'yi filesystem namespace'inin belirli bir path'inde görünür yapmak.**

Örneğin:

```
filesystem/tree
↓
/data
```

Buradaki:

```
/data
```

mount point.

Mount edilen kaynak fiziksel disk olmak zorunda değil.

Örneğin:

```
tmpfs
procfs
network filesystem
bind mount
Docker volume
```

olabilir.

Kaynak notta mount bu namespace görünürlüğü modeliyle tanımlanmış.

---

# 🔎 Mount Debugging

Runtime mount state için:

```
mount
/proc/mounts
/proc/self/mountinfo
```

gibi kaynaklara bakabilirim.

Docker tarafında ise:

```
docker inspect CONTAINER
```

özellikle `Mounts` state'i için çok değerlidir.

---

# 🐞 Incident — Yeni Container'da Veri Yok

Semptom:

> Yeni container oluşturuldu ve beklediğim file görünmüyor.

Direkt:

> “Volume bozuldu.”

yok.

---

# Hipotez 1 — Writable Layer

```
Veri eski container writable layer'daydı
↓
old container remove edildi
↓
data onunla birlikte gitti
```

---

# Hipotez 2 — Yanlış / Eksik Mount

```
Doğru volume bağlanmadı
veya
bind mount hiç yok
```

---

# Hipotez 3 — Yanlış Target Path

Storage doğru olabilir ama:

```
volume → /wrong/path
```

mount edilmiş olabilir.

Uygulama ise:

```
/expected/path
```

okuyor olabilir.

Kaynak incident'ında bu üç ana hipotez açık şekilde ayrılmış.

---

# 🧱 Verinin Sahip Katmanları

Debug ederken önce veriyi bir katmana yerleştir:

```
IMAGE FILESYSTEM

CONTAINER WRITABLE LAYER

BIND MOUNT
→ host filesystem

NAMED VOLUME
→ Docker-managed storage

OWNERSHIP / PERMISSION STATE
```

---

# 🔬 İlk Ayırıcı Deney

```
docker inspect CONTAINER
```

ile:

```
Type
Source
Destination
RW
```

alanlarına bak.

Soru:

> Beklediğim storage gerçekten beklediğim container path'ine bağlı mı?

Kaynak final debugging modelinde de ilk güçlü kontrol bu.

---

# 🧪 İkinci Bağımsız Kanıt

Şüpheli volume'u uygulama container'ından bağımsız başka küçük container'a bağla.

```
volume
↓
temporary container
↓
file gerçekten var mı?
```

## Varsa

```
Storage sağlam
↓
mount/path/application config tarafına dön
```

## Yoksa

```
yanlış volume
veya
veri writable layer'a gitmiş
veya
veri hiç volume'a yazılmamış
```

ihtimalleri güçlenir.

Kaynak notta bu ikinci bağımsız deney de önerilmiş.

---

# 🌳 Git — Pre-Commit Smoke Check

Filesystem labları sırasında:

```
bind-data/
empty-data/
disk-lab/
```

gibi runtime/test artifact'leri oluşabilir.

Bunları yanlışlıkla commit etmek istemem.

---

# Working Tree

```
git diff
```

→ Working Tree ile Index arasındaki unstaged değişiklik.

---

# Index / Stage

```
git diff --staged
```

→ HEAD ile staged snapshot arasındaki fark.

---

# Commit'e Gerçekte Hangi Dosyalar Girecek?

En pratik smoke check:

```
git diff --staged --name-only
```

Çünkü:

> Commit Working Tree'nin tamamını değil, **Index snapshot'ını** kaydeder.

Kaynak pre-commit bölümünde bu ayrım özellikle vurgulanmış.

---

# 🧯 Hata Avı

## 1. Container stop edilince runtime data gider

TIRT.

Aynı container ve writable layer kalır.

---

## 2. Container remove ile stop aynı persistence olayıdır

TIRT.

```
stop
→ state değişimi

remove
→ container object + writable-layer lifecycle sonu
```

---

## 3. Image rebuild mevcut container runtime verisini otomatik siler

TIRT.

Mevcut writable layer ayrı state'tir.

---

## 4. Bind mount file'ları başta container'a kopyalar

TIRT.

Mount aktif olduğu sürece host-backed verinin farklı namespace görünümünü kullanırım.

---

## 5. Bind mount data container'a aittir

TIRT.

Backing data host storage'a aittir.

---

## 6. Named volume container remove edilince otomatik gider

TIRT.

Ayrı storage object'tir.

---

## 7. Bind mount ve named volume aynı şeydir

TIRT.

Lifecycle ve source ownership modelleri farklıdır.

---

## 8. Mount yapılan yerde image file görünmüyorsa file silinmiştir

TIRT.

Mount shadowing olabilir.

---

## 9. `stat`, `du`, `df` üç farklı biçimde aynı disk bilgisini gösterir

TIRT.

```
stat → object metadata
du → tree consumption
df → filesystem capacity
```

---

## 10. `Size` ve allocated blocks her zaman aynıdır

TIRT.

Sparse file gibi durumlarda farklı olabilir.

---

## 11. Ownership username üzerinden belirlenir

TIRT.

Numeric UID/GID asıl filesystem kimliğidir.

---

## 12. Hostta UID 501 ise bind mount container'da da kesin 501 görünür

TIRT.

Özellikle macOS + Docker Desktop mapping katmanında birebir görünüm garanti değildir.

---

## 13. Permission denied → `chmod 777`

TIRT.

Önce identity + ownership + mode + mount state ölç.

---

## 14. UID `10001/UNKNOWN` ownership bilinmiyor demektir

TIRT.

Numeric UID belli; yalnız username resolution yok.

---

## 15. `du` küçük, `df` büyük → araçlardan biri yanlış

TIRT.

Scope'ları farklı.

---

## 16. File silindiyse disk alanı mutlaka anında boşalır

TIRT.

Deleted-but-open file hâlâ blocks tutabilir.

---

## 17. Yeni container'da veri yok → volume bozuk

TIRT.

Önce storage ownership ve mount state'i ayır.

---

## 18. Commit bütün Working Tree değişikliklerini kaydeder

TIRT.

Commit Index'teki staged snapshot'ı alır.

---

# 🧠 Kafaya Kazı

> [!quote]  
> Önce hangi state'i ölçtüğümü belirle, sonra aracı seç.

> [!quote]  
> `stat` object metadata, `du` tree consumption, `df` filesystem capacity.

> [!quote]  
> Stop ile remove persistence açısından aynı olay değildir.

> [!quote]  
> Container writable layer container instance'ın lifecycle'ına bağlıdır.

> [!quote]  
> Bind-mounted data host storage lifecycle'ına bağlıdır.

> [!quote]  
> Named volume Docker'ın ayrı yönettiği storage object'tir.

> [!quote]  
> Persistence sorusunun özü: backing storage nerede ve sahibi kim?

> [!quote]  
> Mount dosyayı silmek zorunda değildir; path'in görünen filesystem tree'sini değiştirebilir.

> [!quote]  
> Görünmeyen image file shadowed olabilir.

> [!quote]  
> Ownership'ın gerçeği numeric UID/GID'dir.

> [!quote]  
> Permission kontrolünde önce process'in hangi owner/group/other sınıfına düştüğünü bul.

> [!quote]  
> `chmod 777` teşhis değildir.

> [!quote]  
> Doğru identity'yi doğru ownership state'ine bağlamak least-privilege açısından daha temizdir.

> [!quote]  
> `du` ile `df` aynı scope'u ölçmez.

> [!quote]  
> Yeni container'da veri yoksa önce `docker inspect` ile gerçek mount state'ini kanıtla.

> [!quote]  
> Commit Working Tree'yi değil Index'teki staged snapshot'ı kaydeder.

---

# 📌 30 Saniyelik Özet

```
FILESYSTEM TOOLS

stat
→ object metadata

du
→ directory/file tree consumption

df
→ filesystem capacity


DOCKER STORAGE

IMAGE
→ immutable-ish image filesystem

CONTAINER
→ writable runtime layer

STOP
→ same container
→ writable layer kalır

REMOVE
→ container gider
→ writable layer gider


BIND MOUNT

host path
↕
container path

data lifecycle
→ host storage


NAMED VOLUME

Docker-managed storage object
↕
container

container remove
≠
volume remove


MOUNT SHADOWING

image:
 /data/image.txt

runtime:
 empty-dir → /data

sonuç:
image.txt silinmedi
→ runtime görünümünde shadowed


PERMISSION

process UID/GID
↓
target UID/GID
↓
owner/group/other class
↓
mode bits
↓
allow / deny


UID 10001
target 0:0 0755
↓
other = r-x
↓
write denied

chown 10001:10001
↓
writer = owner
↓
owner = rwx
↓
write OK


DISK

du küçük
+
df dolu
≠ çelişki

deleted-but-open file
→ possible hidden consumption


DEBUG

“Yeni container'da data yok”
↓
image mı?
writable layer mı?
bind mi?
volume mü?
↓
docker inspect Mounts
↓
Type / Source / Destination / RW
↓
bağımsız container ile storage kontrolü
```

---

# ✅ Günün Kazanımları

- `stat`, `du` ve `df` farklı state scope'larına ayrıldı
    
- `stat` metadata alanları öğrenildi
    
- Logical size ile allocated blocks ayrıldı
    
- Numeric UID/GID'nin ownership açısından temel kimlik olduğu pekiştirildi
    
- Ownership ve permission ayrıldı
    
- `du` ile tree consumption ölçüldü
    
- `df` ile filesystem capacity ölçüldü
    
- `du` / `df` rakamlarının doğrudan kıyaslanamayacağı öğrenildi
    
- Deleted-but-open file senaryosu öğrenildi
    
- Mount'un filesystem namespace görünürlüğü olduğu oturdu
    
- Mount debugging kaynakları öğrenildi
    
- Mount olmadan container writable-layer persistence deneyle gözlemlendi
    
- Stop/start sonrası runtime data'nın kaldığı görüldü
    
- Remove/recreate sonrası writable-layer data'nın kaybolduğu görüldü
    
- Image rebuild ile container writable layer lifecycle'ı ayrıldı
    
- `-dit` flag birleşimi öğrenildi
    
- Bind mount oluşturuldu
    
- Container tarafından yazılan bind verisi hostta görüldü
    
- Host tarafından değiştirilen bind verisi container'da görüldü
    
- Bind-mounted data'nın container removal'dan bağımsız olduğu kanıtlandı
    
- Docker Desktop host/container ownership mapping nüansı gözlemlendi
    
- Named volume oluşturuldu ve inspect edildi
    
- Named volume'un container-independent persistence'ı deneyle doğrulandı
    
- Bind mount ile named volume kullanım alanları ayrıldı
    
- Image file üzerinde mount shadowing deneyle gösterildi
    
- “File görünmüyor = file silindi” zihinsel modeli düzeltildi
    
- Controlled permission failure üretildi
    
- Writer UID/GID ile target UID/GID karşılaştırıldı
    
- Owner/group/other permission sınıfı uygulandı
    
- Root ile yazma testi sayesinde read-only hipotezi elendi
    
- `chmod 777` yerine ownership düzeltmesi uygulandı
    
- `chown 10001:10001` sonrası non-root writer'ın yazabildiği doğrulandı
    
- `UNKNOWN` username ile numeric UID ayrıldı
    
- Git pre-commit Working Tree / Index / staged snapshot kontrolü tekrarlandı
    
- `git diff --staged --name-only` smoke check öğrenildi
    
- “Yeni container'da veri yok” incident'ı storage katmanlarına ayrıldı
    
- `docker inspect` ile gerçek mount state'ini ölçme modeli kuruldu
    
- Şüpheli volume'u bağımsız container ile test etme yöntemi öğrenildi
    

> [!success] 🚀 Gün sonu sonucu  
> Bugün filesystem ve Docker persistence tarafında artık:
> 
> ```
> “Dosya var mı yok mu?”
> ```
> 
> seviyesinde düşünmüyorum.
> 
> Gerçek sorular:
> 
> ```
> Bu path'i şu anda hangi filesystem görünümü sağlıyor?
> ↓
> Verinin backing storage'ı nerede?
> ↓
> Storage'ın lifecycle sahibi kim?
> ↓
> Container stop mu edildi, remove mu edildi?
> ↓
> Doğru mount gerçekten bağlı mı?
> ↓
> Process hangi UID/GID ile çalışıyor?
> ↓
> Target'ın ownership + permission state'i ne?
> ↓
> Ölçmeye çalıştığım şey object metadata mı,
> tree usage mı,
> filesystem capacity mi?
> ```
> 
> Artık özellikle:
> 
> ```
> veri kayboldu
> file görünmüyor
> permission denied
> disk dolu
> ```
> 
> gibi semptomlarda tek komuta atlamak yerine **storage → mount → identity → permission → capacity** katmanlarını ayırmam gerekiyor.
> 
> Günün en kritik cümlesi:
> 
> **Önce hangi state'i ve hangi storage katmanını ölçtüğümü belirle; sonra doğru aracı seç. Tahmin ederek katman atlama.**