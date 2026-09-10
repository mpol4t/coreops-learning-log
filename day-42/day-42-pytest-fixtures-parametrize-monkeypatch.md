---
title: "Gün 42 — Pytest Fixtures, Parametrize, Monkeypatch ve Where to Patch"
tags:
  - coreops
  - day42
  - pytest
  - fixture
  - parametrize
  - monkeypatch
  - fake
  - testing
  - dependency
  - debugging
aliases:
  - "Gün 42 Pytest Monkeypatch ve Where to Patch"
status: completed
---

# 🐒 Blok 2 — Pytest Monkeypatch, Fake & Where to Patch

> [!abstract] 🎯 Ana fikir
> Bugün `monkeypatch` ile gerçek dış bağımlılıkları çalıştırmadan kendi kodumu kontrollü senaryolar altında test etmeyi öğrendim.
>
> Kafamdaki zincir:
>
>     FAKE
>       ↓
>     kontrollü senaryo üret
>       ↓
>     MONKEYPATCH
>       ↓
>     dependency bağlantısını fake'e çevir
>       ↓
>     GERÇEK TEST EDİLEN KOD
>       ↓
>     ASSERT / pytest.raises
>
> En kritik kural:
>
> **Fonksiyonun nerede yazıldığına değil, test ettiğim kodun o fonksiyonu nereden aradığına bakıp orayı patch etmeliyim.**

---

# 🎭 Fake, Patch ve Assert

Başta fake ile patch'i aynı şey gibi düşünüyordum.

Aslında görevleri farklı:

| Parça | Görevi |
|---|---|
| **Fake** | Dış sistemin kontrollü sahte davranışını üretir |
| **Monkeypatch** | Gerçek dependency bağlantısını geçici olarak fake'e yönlendirir |
| **Test edilen fonksiyon** | Gerçek koduyla çalışmaya devam eder |
| **Assert** | Gerçek kodumun sonucunu kontrol eder |

Mental model:

    Gerçek dependency
           ↓
         PATCH
           ↓
          FAKE

Ama:

    test ettiğim ana fonksiyon
           ↓
       GERÇEK çalışır ✅

> [!important]
> **Monkeypatch kendi başına test yapmaz.**
>
> Sadece test ortamındaki bağlantıyı değiştirir. Kontrolü yine `assert` veya `pytest.raises()` yapar.

---

# 🔧 `monkeypatch.setattr()` Nasıl Okuyorum?

Örneğin:

    monkeypatch.setattr(
        service,
        "load_assets",
        fake_load_assets
    )

Bunu artık şöyle okuyorum:

> **`service` içindeki `load_assets` bağlantısını bu test boyunca `fake_load_assets` fonksiyonuna yönlendir.**

Akış:

    TEST ÖNCESİ

    service.load_assets
           ↓
         GERÇEK


    TEST SIRASINDA

    service.load_assets
           ↓
          FAKE


    TEST BİTİNCE

    service.load_assets
           ↓
         GERÇEK

Monkeypatch değişikliği kaynak dosyaya kalıcı yazmıyor; pytest test sonunda eski bağlantıyı geri getiriyor.

---

# 👑 En Önemli Konu — Where to Patch?

Burada en büyük kafa karışıklığım:

> "Fonksiyon `client.py` içinde yazılmış, o zaman kesin `client.load_assets` patch ederim."

**TIRT.**

Doğru soru:

> **Test ettiğim kod bu fonksiyonu çalışırken NEREDEN buluyor?**

Benim `service.py` tarafında:

    from src.client import load_assets

    def get_owner_summary(owner):
        assets = load_assets(owner)

var.

Burada `service.py`, import sırasında kendi `load_assets` ismini oluşturuyor.

Kabaca:

    client.load_assets ──────► GERÇEK

    service.load_assets ─────► GERÇEK

Başlangıçta ikisi aynı fonksiyonu gösterebilir.

Ama iki ayrı **name binding** var.

Sadece:

    client.load_assets → FAKE

yaparsam:

    service.load_assets → GERÇEK

olarak kalabilir.

`get_owner_summary()` içinde çağrı:

    load_assets(owner)

olduğu için Python `service` içindeki isme bakıyor.

Dolayısıyla doğru patch:

    service.load_assets ✅

Yanlış patch:

    client.load_assets ❌

> [!danger]
> ## Patch where it is looked up.
>
> **Fonksiyonun doğduğu yere değil, çağrı sırasında Python'ın o ismi aradığı yere patch at.**

---

# 🆚 Import Şekline Göre Patch Hedefi

### Durum 1

    from client import load_assets

    load_assets()

Python:

    service.load_assets

ismine bakar.

Patch:

    service.load_assets ✅

---

### Durum 2

    import client

    client.load_assets()

Python doğrudan:

    client.load_assets

ismine bakar.

Patch:

    client.load_assets ✅

Kısa karar kuralım:

> **Çağrı satırında ne yazıyor? Python o ismi hangi namespace'te arıyor?**

---

# 🧪 Kurduğum Küçük Test Sistemi

Yapım:

    client.py
       ↓
    load_assets()
    DIŞ DEPENDENCY


    service.py
       ↓
    get_owner_summary()
    ASIL TEST ETTİĞİM KOD


    test_service.py
       ↓
    fake + monkeypatch + assert

`load_assets()` gerçek haliyle çalışırsa bilerek:

    RuntimeError(
        "real dependency should not run in this test"
    )

fırlatıyor.

Bu benim alarmım:

    patch doğru
       ↓
    gerçek dependency çalışmaz ✅


    patch yanlış
       ↓
    gerçek dependency çalışır
       ↓
    RuntimeError 💥

---

# ✅ Success / Empty / Error Senaryoları

Aynı gerçek:

    get_owner_summary()

fonksiyonunu üç farklı dış dünya senaryosunda test ettim.

## ✅ Success

Fake:

    return [asset, asset]

Akış:

    fake
      ↓
    2 asset
      ↓
    get_owner_summary()
      ↓
    count = 2
    status = ok
      ↓
    PASS

---

## 📭 Empty

Başta `"empty"` demek:

> "Fake fonksiyonun içini boş bırak."

sandım.

Bu yanlış.

Şunu yaparsam:

    def fake_load_assets(owner):
        pass

Python:

    None

döndürür.

Benim istediğim senaryo:

> Dependency düzgün çalıştı ama hiç asset bulamadı.

Yani:

    return []

Akış:

    fake
      ↓
     []
      ↓
    get_owner_summary()
      ↓
    count = 0
    status = empty
      ↓
    PASS

---

## 💥 Error

Bu kez fake veri döndürmüyor:

    raise ConnectionError

Test edilen fonksiyon exception'ı yakalamadığı için dışarı çıkıyor.

Bu yüzden normal:

    result == ...

assert'i kullanmak yerine:

    pytest.raises(ConnectionError)

mantığını kullandım.

Mental model:

    fake
      ↓
    ConnectionError 💥
      ↓
    gerçek fonksiyon yarıda kesilir
      ↓
    pytest.raises
      ↓
    "Bu hatayı zaten bekliyordum."
      ↓
    PASS ✅

Sonuçta üç kontrollü senaryoyu da geçtim:

    SUCCESS ✅
    EMPTY   ✅
    ERROR   ✅

---

# 💣 Broken Case — Yanlış Namespace'i Patch Ettim

En öğretici deney buydu.

Bilerek:

    client.load_assets

üzerine fake bağladım.

Ama `service.py`:

    from src.client import load_assets

ile kendi `load_assets` bağlantısını zaten oluşturmuştu.

Patch sonrası:

    client.load_assets
          ↓
         FAKE ✅


    service.load_assets
          ↓
        GERÇEK ❌

Sonra:

    service.get_owner_summary("blue-team")

çalıştı.

İçeride:

    load_assets(owner)

çağrısı `service.load_assets` üzerinden gerçek dependency'ye gitti.

Sonuç:

    RuntimeError:
    real dependency should not run in this test

Pytest:

    ...F

    3 passed
    1 failed

verdi.

Bu failure bana fake'in devreye girmediğini açıkça kanıtladı.

---

# ❓ Broken Case'te Neden `result` Oluşmadı?

Burada ayrıca şunu oturttum:

    result = get_owner_summary(...)

Python önce sağ tarafı tamamen çalıştırır.

Ama sağ tarafta:

    get_owner_summary()
          ↓
      load_assets()
          ↓
      RuntimeError 💥

olursa fonksiyon tamamlanamaz.

Dolayısıyla:

    result = ...

ataması da tamamlanmaz.

Akış:

    SAĞ TARAFI ÇALIŞTIR
           ↓
       exception 💥
           ↓
    atama gerçekleşmez
           ↓
    aşağıdaki assert'e ulaşılmaz

Bu yüzden broken case'te normal result kontrolü yapmam gerekmiyordu.

---

# 🐞 Hatalarım ve Nasıl Düzelttim

## 1. Empty durumda sadece `"empty"` döndürdüm

Fonksiyonun contract'ı dictionary iken bir branch'te string döndürüyordum.

### Düzelttiğim

Success ve empty durumlarında aynı çıktı yapısını korudum:

    owner
    count
    status

> **Fonksiyon contract'ı branch'e göre kafasına göre şekil değiştirmemeli.**

---

## 2. `"blue-team"` değerini hardcode ettim

Fonksiyona zaten:

    owner

geliyordu.

Hardcode kullanırsam:

    get_owner_summary("red-team")

çağrısında bile yanlış owner dönebilirdi.

Düzelttiğim:

    gelen owner
        ↓
    sonuçtaki owner

---

## 3. Status'a `"200"` yazdım

Bu bir HTTP response testi değildi.

Business contract:

    asset varsa → ok
    asset yoksa → empty

şeklindeydi.

HTTP mantığını alakasız yere taşıdığımı fark ettim.

---

## 4. Test ettiğim fonksiyonun kendisini patch ettim

İlk başta:

    get_owner_summary

üzerine fake bağlamaya çalıştım.

Bu **TIRT**.

Çünkü zaten test etmek istediğim şey `get_owner_summary()`.

Doğru yapı:

    get_owner_summary()   → GERÇEK ✅
           ↓
    load_assets()         → FAKE ✅

> **Test ettiğim şeyi değil, onun dış bağımlılığını patch ederim.**

---

## 5. Assert'i fonksiyon contract'ına göre yazmadım

Bir ara:

    "found:2"

gibi string bekledim.

Ama gerçek fonksiyon dict dönüyordu.

Artık assert yazmadan önce:

> **Bu fonksiyon gerçekte ne döndürüyor?**

diye bakacağım.

---

## 6. Empty fake'in içini boş bırakmayı düşündüm

    pass

→ `None`

Benim istediğim:

    return []

→ başarılı dependency çağrısı ama sıfır kayıt.

---

## 7. Empty testini success testinden kopyalayıp assert'i değiştirmedim

Fake:

    []

döndürürken hâlâ:

    count = 2
    status = ok

bekliyordum.

Test datasını değiştirince expected sonucu da tekrar hesaplamam gerektiğini gördüm.

---

## 8. Yanlış namespace'i patch ettim

En önemli hatam.

    client.load_assets → FAKE

yaptığımda:

    service.load_assets

otomatik değişir sandım.

Değişmedi.

> **Aynı gerçek fonksiyonu göstermek, aynı isim bağlantısı olmak demek değildir.**

Doğru çözüm:

    service.load_assets → FAKE

---

# 🧭 Monkeypatch Testi Yazarken Algoritmam

Artık direkt `monkeypatch.setattr()` yazmaya saldırmayacağım.

    1. Asıl test ettiğim fonksiyon ne?
              ↓
       get_owner_summary()

    2. Dış dependency ne?
              ↓
         load_assets()

    3. Hangi senaryo?
              ↓
       success / empty / error

    4. Fake nasıl davranmalı?
              ↓
       success → return [...]
       empty   → return []
       error   → raise ...

    5. Kod dependency'yi nereden arıyor?
              ↓
       service.load_assets

    6. O bağlantıyı patch et
              ↓
       monkeypatch.setattr(...)

    7. GERÇEK ana fonksiyonu çalıştır
              ↓
       get_owner_summary()

    8. Contract'ı kontrol et
              ↓
       assert / pytest.raises

---

# 🧠 Kafaya Kazı

> [!tip]
> **Fake = dış dünyanın kontrollü sahte davranışı.**

> [!tip]
> **Patch = gerçek bağlantıyı geçici olarak fake'e yönlendirmek.**

> [!tip]
> **Monkeypatch test yapmaz; test ortamını değiştirir.**

> [!tip]
> **Test ettiğim ana fonksiyon gerçek koduyla çalışmaya devam eder.**

> [!tip]
> **Success → fake değer döndürür.**

> [!tip]
> **Empty → fake `[]` döndürür.**

> [!tip]
> **Error → fake exception fırlatır.**

> [!danger]
> **Test ettiğim fonksiyonun kendisini patch etmem. Dependency'sini patch ederim.**

> [!danger]
> **PATCH WHERE IT IS LOOKED UP.**
>
> Fonksiyon nerede yazılmış diye değil:
>
> **Kod onu nereden arıyor?**
>
> diye bakarım.

---

# 📌 30 Saniyelik Özet

    TEST
      │
      ├── fake oluştur
      │
      ├── senaryoyu seç
      │
      ▼
    dependency'nin
    LOOKUP NOKTASINI bul
      │
      ▼
    MONKEYPATCH
      │
      ▼
    GERÇEK ANA FONKSİYON
      │
      ▼
    fake dependency
      │
      ├── success → veri
      ├── empty   → []
      └── error   → exception
      │
      ▼
    assert / pytest.raises
      │
      ▼
    PASS


    from client import load_assets
    load_assets()
          ↓
    service.load_assets PATCH


    import client
    client.load_assets()
          ↓
    client.load_assets PATCH

---

# ✅ Günün Kazanımları

- [x] Fake ile patch arasındaki farkı ayırdım
- [x] Monkeypatch'in gerçek fonksiyonu kalıcı değiştirmediğini öğrendim
- [x] Test edilen ana fonksiyonun gerçek çalışmaya devam ettiğini oturttum
- [x] Dış dependency'yi kontrollü fake ile değiştirdim
- [x] Success senaryosunu test ettim
- [x] Empty senaryosunu `return []` ile test ettim
- [x] Error senaryosunu `pytest.raises()` ile test ettim
- [x] Test edilen fonksiyonun kendisini patch etme hatasını düzelttim
- [x] Function contract'a göre assert yazmayı tekrar oturttum
- [x] Hardcode owner hatasını fark ettim
- [x] `pass → None` ile `return []` farkını gördüm
- [x] `from ... import ...` durumunda ayrı name binding oluştuğunu anladım
- [x] **Where to patch?** kuralını uyguladım
- [x] Bilerek yanlış namespace'i patch edip broken case oluşturdum
- [x] Gerçek dependency'nin çalışıp `RuntimeError` üretmesini traceback'ten takip ettim
- [x] Broken case'te `3 passed, 1 failed` sonucunu gördüm

---

# 🚀 Gün Sonu

> **Fake senaryoyu üretir → Monkeypatch doğru bağlantıyı fake'e çevirir → Test ettiğim gerçek kod normal çalışır → Assert veya `pytest.raises()` sonucu doğrular.**
>
> En kritik dersim ise:
>
> **Fonksiyonun nerede tanımlandığını değil, çağrı sırasında Python'ın o ismi nereden lookup ettiğini takip et.**