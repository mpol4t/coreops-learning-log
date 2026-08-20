---
title: "Gün 31 — Git Merge Conflict, Restore, Revert ve Reset"
tags:
  - coreops
  - day31
  - git
  - branch
  - merge
  - conflict
  - restore
  - revert
  - reset
  - staging
  - index
  - head
aliases:
  - "Gün 31 Git Merge Conflict Restore Revert ve Reset"
status: completed
---

# Gün 31 — Git Merge Conflict, Restore, Revert ve Reset

## 🎯 Günün Ana Fikri

Bugün Git komutlarını ezberlemek yerine Git'in arkasındaki state modelini anlamaya çalıştım.

Ana soru:

"Bu komut ne yapıyor?" değil:

"Bu komut Git'in hangi state'ini değiştiriyor?"

Git'in temel state modeli:

HEAD  
↓  
STAGING AREA  
↓  
WORKING TREE


---

# 🌿 Branch Mantığı

Başta branch'i:

"Projenin ayrı bir kopyası"

olarak düşünüyordum.

Bu yanlış.

Doğru model:

Branch = Bir commit'i gösteren hareketli pointer/reference

Branch:

- Yeni klasör değildir.
- Repository kopyası değildir.
- Dosyaların fiziksel kopyası değildir.

Örnek:

A --- B
      ↑
    main


Yeni branch oluşturunca:

A --- B
    ↑   ↑
  main feature


İki farklı proje oluşmaz.

İki farklı isim aynı commit'i gösterir.


---

# 🔀 Merge Mantığı

Merge:

Bir branch'teki değişiklikleri bulunduğum branch'e almaktır.

Önemli:

Merge diğer branch'i değiştirmez.

Örneğin:

git merge feature

çalıştırınca:

- Bulunduğum branch ilerler.
- Diğer branch aynı yerde kalır.


---

# ⚔️ Conflict Neden Çıkar?

Git en yeni değişikliği otomatik seçmez.

Çünkü:

Yeni olan her zaman doğru değildir.

Git şunları bilemez:

- Hangisi güvenli?
- Hangisi istenen davranış?
- İki değişiklik birleşmeli mi?
- Eski değer bilinçli mi bırakıldı?

Bu yüzden conflict:

Git'in bozulması değil, insan kararı gereken noktadır.


---

# 🧩 Conflict Nasıl Oluşur?

Git sadece son değere bakmaz.

Şuna bakar:

Ortak atadan sonra iki taraf aynı bölgeyi farklı değiştirdi mi?


## Conflict Olmayan Durum

Başlangıç:

timeout = 15

Feature:

timeout = 20

Master:

timeout = 15


Git:

"Master bu satıra dokunmamış, feature değişikliğini alabilirim."

der.

Sonuç:

Automatic merge


---

## Gerçek Conflict

Başlangıç:

timeout = 10


Feature:

timeout = 20


Master:

timeout = 30


Git:

BASE:

timeout = 10


OURS:

timeout = 30


THEIRS:

timeout = 20


İki taraf aynı bölgeyi değiştirdiği için karar veremez.

Sonuç:

Conflict


---

# 🏷️ Conflict Marker

Conflict sırasında:

<<<<<<< HEAD
timeout = 30
=======
timeout = 20
>>>>>>> feature


HEAD:

Bulunduğum branch.


THEIRS:

Merge ettiğim branch.


---

# 🛠️ Conflict Çözme Akışı

1. Merge başlatılır:

git merge feature


2. Conflict oluşur.


3. Dosya düzenlenir.


4. Çözüm stage edilir:

git add dosya


5. Merge tamamlanır:

git merge --continue


---

# 📦 Conflict Sırasında git add

Normalde:

git add

şunu yapar:

Working Tree
↓
Staging Area


Yani:

"Bu değişiklik sonraki commit'e hazır."


Ama conflict sırasında:

"Bu dosyanın çözülmüş son halini kabul ettim."

anlamına gelir.


Çünkü Git'in elinde:

- BASE
- OURS
- THEIRS

vardır.

git add sonrası:

3 farklı durum

↓

1 kesin sonuç


haline gelir.


---

# 🔍 git diff ve git diff --staged

Git state modeli:

HEAD

↓

STAGING AREA

↓

WORKING TREE


---

# git diff

Karşılaştırır:

STAGING AREA

ile

WORKING TREE


Soru:

Henüz stage edilmemiş değişiklik ne?


Örnek:

STAGE:

timeout = 50


WORKTREE:

timeout = 999


---

# git diff --staged

Karşılaştırır:

HEAD

ile

STAGING AREA


Soru:

Commit edersem ne gidecek?


Örnek:

HEAD:

timeout = 50


STAGE:

timeout = 999


---

# 🧹 git merge --abort

Conflict sırasında vazgeçmek için kullanılır.

git merge --abort


Anlamı:

Başlayan merge operasyonunu iptal et.


Yaptığı:

- Merge durumunu geri alır.
- Conflict sürecinden çıkarır.


Yapmadığı:

- Commit silmez.
- History değiştirmez.
- Eski commitleri yok etmez.


---

# 🧹 git restore

Restore:

Dosya state'i ile ilgilenir.

Commit history ile ilgilenmez.


Örnek:

Başlangıç:

timeout = 50


Değişiklik:

timeout = 999


Commit yok.


Durum:

HEAD:

50


STAGE:

50


WORKTREE:

999


Komut:

git restore app.py


Sonuç:

HEAD:

50


STAGE:

50


WORKTREE:

50


Yani:

Commit edilmemiş dosya değişikliğini geri alır.


---

# 📤 git restore --staged

Stage alanını etkiler.


Örnek:

HEAD:

50


STAGE:

999


WORKTREE:

999


Komut:

git restore --staged app.py


Sonuç:

HEAD:

50


STAGE:

50


WORKTREE:

999


Yani:

Değişikliği stage'den çıkarır ama dosyaya dokunmaz.


Buna:

unstage

denir.


---

# ↩️ git revert

Revert:

Commit'i silmez.

Yeni bir commit oluşturur.


Örnek:

Önce:

A --- B


B hatalı.


Revert sonrası:

A --- B --- C


C:

B commit'inin yaptığı değişikliğin tersini uygular.


Örneğin:

B:

timeout = 999


C:

timeout = 50


Ama B history'de kalır.


---

# ⏪ git reset

Reset:

Branch pointer'ını hareket ettirir.


Örnek:

A --- B --- C
          ↑
        HEAD


Reset sonrası:

A --- B


HEAD başka noktayı gösterir.


---

# Reset Türleri


## --soft

Commit geri alınır.

Ama:

Değişiklikler stage'de kalır.


---

## --mixed

Commit geri alınır.

Stage temizlenir.

Ama:

Dosya değişikliği kalır.


---

## --hard

Commit gider.

Stage gider.

Working Tree de geri döner.


Yani:

Her şeyi temizler.


---

# Restore vs Revert vs Reset

## restore

Dosya state'iyle ilgilenir.

"Dosyadaki değişikliği geri al."


## revert

Commit history ile ilgilenir.

"Yanlış commit'in etkisini geri al."


## reset

Branch pointer ile ilgilenir.

"HEAD'i başka yere taşı."


---

# 🐞 Yaptığım Hatalar


## Hata 1 — Conflict neden çıkmadığını anlamamak

İlk denemede conflict bekledim ama çıkmadı.

Sebep:

İki taraf aynı bölgeyi değiştirmemişti.


Ders:

Conflict için ortak atadan sonra aynı bölgenin farklı değiştirilmesi gerekir.


---

## Hata 2 — Merge sonrası branch'lerin eşitleneceğini düşünmek

Yanlış.

Merge:

Bulunduğun branch'i ilerletir.


Diğer branch aynı kalır.


---

## Hata 3 — Reset'i düşünmeden kullanmak

Çözüm:

Önce:

git log --graph --all

ile history görmek.


---

# 🧠 Kafaya Kazı


Branch proje kopyası değildir.

Branch commit pointer'ıdır.


Merge diğer branch'i değiştirmez.

Bulunduğun branch'i ilerletir.


Conflict hata değildir.

Git'in insan kararı istediği noktadır.


Git en yeni değişikliği seçmez.

Çünkü yeni olan her zaman doğru değildir.


git add conflict sırasında çözülmüş sonucu kabul etmek anlamına gelir.


git diff stage edilmemiş değişiklikleri gösterir.


git diff --staged commit'e girecek değişiklikleri gösterir.


Restore dosya state'iyle ilgilenir.


Revert commit history ile ilgilenir.


Reset branch pointer'ını hareket ettirir.


Git öğrenirken komut değil state değişimi öğrenmek gerekir.


---

# 📌 30 Saniyelik Özet


HEAD

↓

STAGING AREA

↓

WORKING TREE



Conflict:

BASE

↓

OURS

THEIRS



Aynı bölge iki tarafta değişirse:

Conflict



Restore:

Dosya değişikliğini geri alır.



Revert:

Yeni commit oluşturup eski commit etkisini tersine çevirir.



Reset:

Branch pointer taşır.



Merge:

Bulunduğun branch'i ilerletir.


---

# ✅ Günün Kazanımları

- Branch'in proje kopyası olmadığı öğrenildi.
- Branch'in commit pointer olduğu anlaşıldı.
- Merge mantığı öğrenildi.
- Conflict neden çıktığı öğrenildi.
- Git'in neden otomatik seçim yapmadığı anlaşıldı.
- Conflict marker yapısı öğrenildi.
- Conflict çözme akışı uygulandı.
- git add conflict sırasında farklı anlamıyla öğrenildi.
- HEAD / Stage / Working Tree modeli oturdu.
- git diff ve git diff --staged ayrıldı.
- git merge --abort öğrenildi.
- git restore öğrenildi.
- git restore --staged öğrenildi.
- git revert öğrenildi.
- git reset ve türleri öğrenildi.
- Restore, revert ve reset farkı anlaşıldı.


---

# 🚀 Gün Sonu Sonucu

Bugün Git'i komut ezberi olarak değil, state yönetimi olarak düşünmeye başladım.

Artık bir sorun çıktığında:

Yanlış soru:

"Hangi komutu yazacağım?"


Doğru soru:

"Şu anda hangi state değişti ve ben hangisini değiştirmek istiyorum?"


Günün en kritik cümlesi:

Git'te güçlü olmak çok komut bilmek değil, hangi komutun hangi state'i değiştirdiğini bilmektir.