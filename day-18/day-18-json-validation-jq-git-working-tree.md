---
title: "Gün 18 — JSON Parse, Validation, JQ ve Git Working Tree / Index Mantığı"
tags:
  - coreops
  - python
  - json
  - validation
  - normalization
  - jq
  - git
  - staging
  - working-tree
  - index
aliases:
  - "Gün 18 JSON Validation JQ ve Git Temelleri"
status: completed
---

# 🧠 Gün 18 — JSON Parse, Validation, `jq` ve Git Working Tree / Index Mantığı

> [!abstract] 🎯 Ana fikir  
> Bugün iki önemli veri akışı öğrendim:
> 
> ```
> JSON
> ↓
> Parse
> ↓
> Validate
> ↓
> Normalize
> ↓
> Kullan
> ```
> 
> ve:
> 
> ```
> Working Tree
> ↓ git add
> Index / Staging Area
> ↓ git commit
> Local Git History
> ↓ git push
> Remote Repository
> ```
> 
> İkisinin ortak fikri:
> 
> **Bir verinin bir aşamadan geçmiş olması, sonraki aşamanın şartlarını da otomatik sağladığı anlamına gelmez.**

---

# ⚡ 2 Dakikalık Geri Çağırma

JSON tarafında:

```
Geçerli JSON syntax'ı
≠
Uygulama açısından geçerli veri
```

Örneğin:

```
{
  "port": "443"
}
```

JSON olarak tamamen geçerlidir.

Ama uygulama:

```
port → gerçek int
```

bekliyorsa validation başarısız olur.

Kaynak çalışmada da malformed JSON ile yanlış veri tipi/range ayrı katmanlarda değerlendirilmiş.

---

# 🐍 Python — Büyük Veri Akışı

Günün programı:

```
JSON dosyası
     ↓
parse_json()
     ↓
Python nesnesi
     ↓
validation()
     ↓
normalization()
     ↓
Temiz dict
     ↓
print
```

Kaynak implementasyonda bu üç sorumluluk ayrı fonksiyonlara bölünmüş.

---

# 1️⃣ Parse — “Bu Gerçekten JSON mu?”

```
def parse_json(dosya):
    with open(
        dosya,
        encoding="utf-8",
    ) as file:
        return json.load(file)
```

`json.load()` açık dosya nesnesindeki JSON'u parse edip Python nesnelerine çevirir.

---

# 🔄 JSON → Python Temel Dönüşümleri

|JSON|Python|
|---|---|
|object|`dict`|
|array|`list`|
|string|`str`|
|number|`int` / `float`|
|`true`|`True`|
|`false`|`False`|
|`null`|`None`|

Kaynak notta bu dönüşüm tablosu doğru şekilde çıkarılmış.

---

# 📄 `json.load()` vs `json.loads()`

```
json.load(file)
```

→ Açık **file object** içinden JSON okur.

```
json.loads(text)
```

→ JSON içeren **string** parse eder.

Kafada:

```
load  → file
loads → string
```

---

# 💥 `JSONDecodeError`

Malformed:

```
{
  "port": 443,
```

gibi syntax'ı yarım veya bozuk JSON:

```
json.JSONDecodeError
```

üretebilir.

Bu soru yalnızca:

> **“JSON syntax'ı geçerli mi?”**

ile ilgilidir.

---

# ⚠️ Geçerli JSON İçindeki Yanlış Tip Neden `JSONDecodeError` Değil?

Örneğin:

```
{
  "port": "443"
}
```

JSON syntax'ı geçerlidir.

Parser açısından:

```
"443"
→ geçerli JSON string'i ✅
```

Ama bizim schema:

```
port → int
```

diyor.

Dolayısıyla hata:

```
JSON parse katmanı ❌ değil
Uygulama validation katmanı ✅
```

tarafındadır.

---

# 2️⃣ Validation — “Bu Benim İstediğim Veri mi?”

Uygulama sözleşmesi:

```
asset_id
→ boş olmayan str

hostname
→ boş olmayan str

port
→ gerçek int
→ 1..65535

active
→ bool

tags
→ list
→ bütün elemanları str
```

Kaynakta bu sözleşme açık şekilde uygulanmış.

---

# 🧱 Önce Ana Nesnenin Tipini Kontrol Et

```
if not isinstance(loaded, dict):
    raise ValueError
```

Çünkü uygulama en üst seviyede JSON object bekliyor.

Mesela bu da geçerli JSON'dur:

```
["a", "b"]
```

ama bizim uygulamamız için geçersiz olabilir.

Yine:

```
Parse ✅
Validation ❌
```

---

# 🔑 Required Key Kontrolü

```
required = [
    "asset_id",
    "hostname",
    "port",
    "active",
    "tags",
]
```

Sonra:

```
for key in required:
    if key not in loaded:
        raise ValueError(
            f"{key} eksik!"
        )
```

Dict üzerinde:

```
"hostname" in loaded
```

doğrudan **key var mı?** sorusuna cevap verir.

---

# ♻️ Aynı Kurala Sahip Alanları Birlikte Kontrol Et

```
same_str_rule = [
    "asset_id",
    "hostname",
]
```

İkisi de:

```
str olmalı
+
strip sonrası boş olmamalı
```

sözleşmesine sahip.

Bu yüzden iki ayrı blok yazmak yerine:

```
for key in same_str_rule:
    ...
```

kullanmak mantıklıdır.

---

# 🧼 `" "` Neden Geçerli Sayılmıyor?

Bu:

```
isinstance("   ", str)
```

için:

```
True
```

verir.

Ama:

```
"   ".strip()
```

sonucu:

```
""
```

olur.

Dolayısıyla:

```
if not loaded[key].strip():
    raise ValueError
```

ile:

```
String tipi doğru ✅
Anlamlı içerik yok ❌
```

ayrımı yapılır.

---

> [!important]  
> Validation içindeki `.strip()` burada veriyi normalize etmek için değil:
> 
> **“Whitespace temizlenince geriye gerçekten bir şey kalıyor mu?”**
> 
> sorusunu sormak için kullanılıyor.

---

# 🔢 `port` Kontrolü ve Python'ın `bool` Sürprizi

Python'da:

```
isinstance(True, int)
```

sonucu:

```
True
```

olur.

Bu yüzden:

```
isinstance(port, int)
```

tek başına:

```
"port": true
```

değerini istemeden kabul edebilir.

Bu görevde:

```
type(loaded["port"]) is not int
```

kontrolü kullanılmasının sebebi **tam olarak gerçek** `**int**` **tipini istemek**.

> [!success]  
> Burada `type(...) is int` bilinçli bir tercih.

---

# 📏 Port Range

Tip doğru olduktan sonra:

```
1 <= port <= 65535
```

kontrol edilir.

Yani:

```
0       ❌
-1      ❌
1       ✅
443     ✅
65535   ✅
65536   ❌
```

---

# ✅ `active=False` Tamamen Geçerli

Burada:

```
if type(loaded["active"]) is not bool:
    raise ValueError
```

kontrol edilen:

```
Değer True mı?
```

değildir.

Kontrol edilen:

```
Gerçek boolean mı?
```

sorusudur.

Dolayısıyla:

```
"active": false
```

tamamen geçerlidir.

---

# 🏷️ `tags`

İki aşama gerekir.

Önce container tipi:

```
if type(loaded["tags"]) is not list:
    raise ValueError
```

Sonra elemanlar:

```
for tag in loaded["tags"]:
    if type(tag) is not str:
        raise ValueError
```

Çünkü:

```
"tags": ["prod", 123]
```

bir JSON array'dir ama bizim:

```
list[str]
```

sözleşmemizi bozuyor.

---

# 🧠 Validation Fonksiyonunun Return Etmesi Şart mı?

Hayır.

Güzel sözleşme:

```
Geçersizse
→ raise

Geçerliyse
→ sessizce tamamlan
```

Bu durumda normal dönüş:

```
None
```

olabilir.

Sonra `main()`:

```
validation(json_verisi)
normalize = normalization(
    json_verisi
)
```

şeklinde devam eder.

---

# 3️⃣ Normalization — “Geçerli Veriyi Hangi Standart Biçimde Kullanacağım?”

Validation:

```
Bu veri kullanılabilir mi?
```

Normalization:

```
Kullanılabilir veriyi hangi temiz formatta kullanacağım?
```

sorusudur.

---

# 🧹 Uygulanan Normalizasyon

```
asset_id → strip()
hostname → strip()
tags     → her eleman strip()
port     → aynen
active   → aynen
```

Kaynakta orijinal dict'i değiştirmek yerine yeni bir temiz dict oluşturulmuş.

---

# ♻️ Neden Yeni Dict?

```
temiz_dict = {}
```

kullanılarak:

```
Raw parsed data
≠
Normalized data
```

ayrımı korunuyor.

Bu debugging açısından da iyidir:

```
Ne geldi?
↓
Ne ürettik?
```

karşılaştırması yapılabilir.

---

# ⚠️ `strip()` Yerinde Değiştirmez

```
tag.strip()
```

orijinal string'i mutate etmez.

Yeni bir string üretir.

Bu yüzden:

```
temiz = tag.strip()
temiz_tagler.append(temiz)
```

gibi sonucu saklamak gerekir.

---

# 🔑 Dict Döngüsü ile Liste Döngüsü Farkı

```
for x in veri:
```

veya key listesi üzerinde dönerken `x` bir **key** olabilir:

```
veri[x]
```

ile value alınır.

Ama:

```
for x in veri["tags"]:
```

kullanıldığında `x` doğrudan tag değeridir.

Bu küçük ayrım birçok bug'ın kaynağı olabilir.

---

# 🎻 `main()` Orkestra Şefi

```
parse
↓
validate
↓
normalize
↓
print
```

Main'in işi algoritmaların iç detaylarını yapmak değil, katmanları sırayla çalıştırmaktır.

---

# 💥 Exception Sırası Neden Önemli?

Çok kritik Python detayı:

```
JSONDecodeError
↓
ValueError'ın subclass'ıdır.
```

Bu yüzden:

```
except json.JSONDecodeError:
    ...

except ValueError:
    ...
```

sırası doğrudur.

Kaynak notta bu detay doğru şekilde fark edilmiş.

---

## TIRT sıra

```
except ValueError:
    ...

except json.JSONDecodeError:
    ...
```

Genel `ValueError`:

```
JSONDecodeError'ı da yakalayabilir
```

ve özel parse failure ile schema failure birbirine karışır.

---

# 👤 Shadowing — `json` İsmini Ezme

Şunu yaparsan:

```
import json

json = parse_json(...)
```

artık:

```
json
```

adı modülü değil yeni değişkeni gösterebilir.

Bu yüzden:

```
loaded
data
json_verisi
```

gibi isimler daha güvenlidir.

---

# ✅ Gerçek Python Deneyleri

Geçerli veri:

```
python day18.py geçerli.json
```

→ parse + validation + normalization başarılı.

Malformed:

```
python day18.py malformed.json
```

→ `JSONDecodeError` yolu.

Range hatası:

```
python day18.py range_yanlış.json
```

→ validation `ValueError`.

Bu üç davranış gerçek çalıştırmada gözlemlenmiş.

---

# 🧠 JSON İçin Kafaya Kazınacak Model

```
PARSE
“Bu JSON mu?”

VALIDATE
“Bu benim sözleşmeme uyuyor mu?”

NORMALIZE
“Doğru veriyi hangi standart biçimde kullanacağım?”
```

---

# 🐧 Linux — `jq`

`jq`, yalnız JSON pretty-print aracı değildir.

Aynı zamanda:

```
Parse
Sorgulama
Tip kontrolü
Key kontrolü
Filtreleme
Exit status üretme
```

için kullanılabilir.

---

# ✅ JSON Syntax Kontrolü

```
jq . file.json
```

Geçerliyse JSON parse edilir.

Malformed ise:

```
parse error
```

oluşur.

Gerçek malformed deneyinde `jq` syntax hatasını yakalamış.

---

# 🐈 `cat` vs `jq`

```
cat file.json
```

şunu cevaplar:

> “Dosyada hangi karakterler yazıyor?”

Ama:

```
jq . file.json
```

şunu da test eder:

> “Bu metin gerçekten parse edilebilir JSON mu?”

> [!important]  
> Ekranda JSON'a benziyor olması, geçerli JSON olduğu anlamına gelmez.

---

# 🔎 Bir Alanın Tipini Sormak

```
jq '.port | type' file.json
```

Akış:

```
.port
↓
port değerini seç

|
↓
çıktıyı sonraki filtreye gönder

type
↓
JSON tipini söyle
```

Örneğin:

```
"port": 443
```

→

```
"number"
```

Ama:

```
"port": "443"
```

→

```
"string"
```

---

# 🔑 `has("hostname")`

```
jq 'has("hostname")' file.json
```

sorusu:

> Object içinde `hostname` **key'i mevcut mu?**

Key varsa:

```
true
```

yoksa:

```
false
```

Gerçek eksik alan deneyinde `false` sonucu alınmış.

---

# ⚠️ `has()` Değerin Kalitesini Kontrol Etmez

Şu:

```
{
  "hostname": null
}
```

için:

```
jq 'has("hostname")' file.json
```

yine:

```
true
```

verebilir.

Çünkü soru:

```
hostname var mı?
```

Değil:

```
hostname dolu, string ve geçerli mi?
```

---

# 🔬 `select(...)`

```
select(condition)
```

bir filtre gibi düşünülebilir.

```
Condition true
→ Veri geçer

Condition false
→ Çıktı üretilmez
```

Örneğin:

```
select(
  has("hostname")
  and
  (.port | type == "number")
)
```

şuna benzer basit bir sözleşme kurar:

```
hostname key'i var mı?
VE
port JSON number mı?
```

---

# 🚪 `jq -e`

`jq -e` özellikle otomasyon açısından güçlüdür.

```
jq -e '...' file.json
```

yalnızca çıktı üretmek yerine sonucu exit status davranışına da bağlar.

Bu:

```
shell
CI
Docker
script
```

içinde programatik kontrol yapmayı kolaylaştırır.

---

# ❓ `jq` Python Koduna Ne Ekliyor?

Kapalı-kitap sorusunda karışan nokta buydu.

`jq`:

> **Python kodunun içine hiçbir şey eklemiyor.**

Asıl katkısı:

```
Python'dan bağımsız ikinci bir araçla
aynı veri üzerinde kanıt üretmek.
```

Yani:

```
Python:
“Port int gibi düşünüyorum.”

jq:
“JSON tarafında port gerçekten number.”
```

Bu **bağımsız doğrulama** sağlar.

> [!success]  
> `jq` Python'ın parçası değil; Python sonucunu veya girdisini başka bir parser ile çapraz kontrol eden bağımsız araçtır.

---

# 🧠 `jq` Kısa Formül

```
jq .
→ Parse et

.port
→ Alan seç

type
→ JSON tipini söyle

has("x")
→ Key var mı?

select(...)
→ Koşulu sağlayanı geçir

-e
→ Sonucu exit status ile otomasyona uygun hâle getir
```

---

# 🌳 Git — İlk Büyük Zihinsel Model

Bugün en çok oturtulması gereken konu Git olmuş.

Ana zincir:

```
WORKING TREE
     │
     │ git add
     ▼
INDEX / STAGING AREA
     │
     │ git commit
     ▼
LOCAL REPOSITORY
     │
     │ git push
     ▼
REMOTE REPOSITORY
```

Kaynak notun Git bölümündeki temel model bu şekilde kurulmuş.

---

# 📁 Working Tree Nedir?

Burada küçük ama önemli düzeltme:

> Working Tree yalnızca “mevcut çalışma dizini/CWD” değildir.

Daha doğru:

```
Git repository'sinin
diskte checkout edilmiş,
şu anda üzerinde çalıştığın dosya hâli
```

Örneğin:

```
project/
├── main.py
└── test.txt
```

dosyalarının diskte şu an gördüğün/değiştirdiğin hâli Working Tree'dedir.

---

# 📦 Index / Staging Area Nedir?

Index:

> **Bir sonraki commit'e girmesini hazırladığın snapshot.**

Şunu yapınca:

```
git add test.txt
```

Git:

```
Working Tree'deki test.txt'nin
O ANKİ hâlini
↓
Index'e alır
```

---

> [!danger] TIRT
> 
> ```
> git add
> → commit oluşturur
> ```
> 
> Yanlış.

`git add` yalnızca staging yapar.

---

# 💾 Commit Nedir?

```
git commit
```

Index'teki hazırlanmış durumu Git geçmişine kaydeder.

Yani:

```
Working Tree'yi direkt commit etmez.
Index'i commit eder.
```

Bu ayrım kritik.

---

# 🎯 En Önemli Git Örneği

Şöyle düşün:

```
HEAD         = A
INDEX        = B
WORKING TREE = C
```

Şimdi:

```
git commit
```

dersen:

```
B
```

commit'e girer.

`C` hâlâ Working Tree'de unstaged değişiklik olarak kalabilir.

---

# 🧭 `HEAD` Nedir?

HEAD bir proje snapshot'ının kendisi değil:

> **Şu anda bulunduğun commit/branch konumuna işaret eden referanstır.**

Normal durumda:

```
HEAD
 ↓
main
 ↓
son commit
```

gibi düşünülebilir.

---

# 🏁 İlk Commit Yoksa?

Yeni:

```
git init
```

sonrasında henüz commit yoktur.

Dolayısıyla HEAD bir branch adına bağlı olabilir ama henüz gerçekten işaret edilecek commit oluşmamıştır.

Kaynak deneyde repository ilk commit öncesi durumdaydı.

---

# 🔧 `git init`

Normal klasörde:

```
git init
```

çalıştırıldığında:

```
.git/
```

dizini oluşturulur.

Bu klasör Git'in repository metadata'sını tutar:

```
refs
objects
HEAD
index
config
...
```

Bu noktadan sonra klasör Git repository'sidir.

---

# 🔎 `git diff`

Temel karşılaştırma:

```
INDEX
↕
WORKING TREE
```

Yani:

> Stage edilmiş snapshot'a göre Working Tree'de sonradan ne değiştirdim?

---

# 🔎 `git diff --staged`

Temel karşılaştırma:

```
HEAD
↕
INDEX
```

Yani:

> Bir sonraki commit'e hangi değişiklikleri hazırladım?

Kaynak notta iki diff türü doğru şekilde ayrılmış.

---

# ⚠️ İlk Commit Öncesi Küçük Nüans

İlk commit henüz yoksa gerçek bir HEAD commit snapshot'ı bulunmaz.

Bu durumda `git diff --staged` staged dosyayı:

```
önceden yoktu
→ şimdi eklenecek
```

şeklinde gösterebilir.

Bu yüzden kaynak deneyinde:

```
/dev/null
→ test.txt
```

görülmüş.

---

# 🧪 Günün Git Deneyi

İlk:

```
test.txt = ASD
```

oluşturuldu.

`git status`:

```
untracked
```

gösterdi.

Normal:

```
git diff
```

boş çıktı.

Neden?

> Normal `git diff`, henüz untracked olan dosyanın içeriğini staged/working-tree değişikliği olarak göstermez.

---

# ➕ `git add test.txt`

Sonra:

```
git add test.txt
```

yapıldı.

Durum:

```
INDEX        WORKING TREE
ASD          ASD
```

Bu yüzden:

```
git diff
```

yine boş.

Çünkü:

```
Index ile Working Tree aynı.
```

Ama:

```
git diff --staged
```

şunu gösterdi:

```
+ASD
```

Çünkü yeni dosya commit'e hazırlanmıştı.

---

# 🔥 Stage Ettikten Sonra Dosyayı Değiştirirsem

Stage:

```
ASD
```

iken Working Tree:

```
ABC
```

yapıldı.

Şimdi:

```
INDEX        WORKING TREE
ASD          ABC
```

Bu yüzden:

```
git diff
```

şunu gösterdi:

```
-ASD
+ABC
```

Gerçek deneyde tam olarak bu olmuş.

---

# 🤯 Aynı Dosya Nasıl Hem Staged Hem Unstaged Olabiliyor?

Çünkü aynı dosyanın **iki ayrı snapshot'ı** var.

```
INDEX
→ ASD

WORKING TREE
→ ABC
```

Git açısından:

```
Staged:
önceki kayıt → ASD

Unstaged:
ASD → ABC
```

aynı anda bulunabilir.

> [!important]  
> Bunun olması için önceden commit edilmiş bir sürüm şart değildir.
> 
> Senin ilk-commit-öncesi deneyinde bile aynı dosya hem staged hem unstaged hâle geldi.

Bu kapalı-kitap cevabındaki önemli düzeltme.

---

# 📊 Üç Katmanla Düşün

Genel durumda:

```
HEAD          INDEX          WORKING TREE

A             B              C
```

Burada:

```
HEAD → Index
A → B
= staged değişiklik

Index → Working Tree
B → C
= unstaged değişiklik
```

---

# 🔍 Komutların Baktığı Yer

```
git diff
→ Index ↔ Working Tree

git diff --staged
→ HEAD ↔ Index

git commit
→ Index'teki snapshot'ı kaydet

git add
→ Working Tree'deki seçilen güncel hâli Index'e getir
```

---

# 🔄 Tekrar `git add`

Şu durum:

```
INDEX        WORKING TREE
ASD          ABC
```

ise:

```
git add test.txt
```

sonrası:

```
INDEX        WORKING TREE
ABC          ABC
```

olur.

Dolayısıyla:

```
git diff
```

yeniden boş kalır.

Ama staged değişiklik:

```
git diff --staged
```

tarafında artık `ABC` bulunur.

---

# ⚠️ `git diff -staged`

Deneyde:

```
git diff -staged
```

yazılmış ve hata oluşmuş.

Doğru:

```
git diff --staged
```

Çünkü:

```
--staged
```

uzun option'dır ve iki tire kullanır.

Alternatif:

```
git diff --cached
```

de aynı temel amaç için kullanılabilir.

---

# 🚀 `git push`

```
git add
→ Index

git commit
→ Local Git history

git push
→ Local commit'leri remote'a gönder
```

Yani:

```
Değiştir
   ↓
git add
   ↓
git commit
   ↓
git push

Working Tree
   ↓
Index
   ↓
Local Repository
   ↓
Remote Repository
```

Kaynak notta bu zincir doğru kurulmuş.

---

# 🧯 Hata Avı

## 1. JSON parse olduysa veri doğrudur

TIRT.

```
Parse
→ Syntax

Validation
→ Uygulama sözleşmesi
```

---

## 2. `"port": "443"` `JSONDecodeError` üretmelidir

TIRT.

JSON string olarak tamamen geçerlidir.

Validation hatasıdır.

---

## 3. `null` Python'da `"null"` string olur

TIRT.

```
null → None
```

---

## 4. `isinstance(True, int)` False'dur

TIRT.

Python'da:

```
isinstance(True, int)
```

`True` verir.

Bu yüzden port için exact type kontrolü gerekebilir.

---

## 5. Validation `.strip()` yaptıysa veri normalize olmuştur

TIRT.

Sonucu saklamıyorsan yalnızca kontrol amacıyla kullanmış olabilirsin.

---

## 6. `JSONDecodeError` ile `ValueError` catch sırası önemli değildir

TIRT.

`JSONDecodeError`, `ValueError` alt sınıfıdır.

Özel olan önce yakalanmalıdır.

---

## 7. `jq` Python koduna özellik ekliyor

TIRT.

Bağımsız bir araçtır; ikinci kanıt üretir.

---

## 8. `cat` JSON syntax'ını doğrular

TIRT.

Metni gösterir.

`jq` gerçekten parse etmeye çalışabilir.

---

## 9. `has("hostname")` hostname'in geçerli değer olduğunu kanıtlar

TIRT.

Yalnız key'in varlığını kontrol eder.

---

## 10. Working Tree = CWD

Tam doğru değil.

Working Tree, Git repository'sinin diskte üzerinde çalıştığın checkout edilmiş dosya durumudur.

---

## 11. `git add` commit oluşturur

TIRT.

Index'i günceller.

---

## 12. `git commit` Working Tree'nin o anki her şeyini kaydeder

TIRT.

Temel olarak **Index'te hazırlanmış snapshot'ı** commit eder.

---

## 13. `git diff` staged değişiklikleri gösterir

TIRT.

Normal:

```
Index ↔ Working Tree
```

karşılaştırır.

---

## 14. `git diff --staged` Working Tree ile Index'i karşılaştırır

TIRT.

```
HEAD ↔ Index
```

karşılaştırmasıdır.

---

## 15. Aynı dosyanın hem staged hem unstaged olması için eski commit şarttır

TIRT.

İlk commit öncesinde bile:

```
git add
↓
dosyayı yeniden değiştir
```

ile oluşabilir.

---

# 🧠 Kafaya Kazı

> [!quote]  
> Parse edilebilir olmak, uygulama açısından geçerli olmak değildir.

> [!quote]  
> Parse syntax'ı, validation sözleşmeyi, normalization standart biçimi belirler.

> [!quote]  
> Geçerli JSON içindeki yanlış tip `JSONDecodeError` değildir.

> [!quote]  
> `null → None`.

> [!quote]  
> Validation başarılıysa fonksiyonun değer döndürmesi şart değildir.

> [!quote]  
> Python'da `bool`, `int` ile özel bir miras ilişkisine sahiptir; exact type gereken yerlerde dikkat et.

> [!quote]  
> `JSONDecodeError`, `ValueError` alt sınıfıdır.

> [!quote]  
> `jq` Python'ın içine eklenmez; bağımsız ikinci kanıttır.

> [!quote]  
> `cat` metni gösterir, `jq` JSON'u parse eder.

> [!quote]  
> Working Tree şu anda diskte üzerinde çalıştığın Git dosya hâlidir.

> [!quote]  
> Index bir sonraki commit'in hazırlık snapshot'ıdır.

> [!quote]  
> `git add` Working Tree'den Index'e snapshot alır.

> [!quote]  
> `git commit` Index'i kaydeder.

> [!quote]  
> `git diff` Index ↔ Working Tree.

> [!quote]  
> `git diff --staged` HEAD ↔ Index.

> [!quote]  
> Aynı dosyanın staged ve unstaged kısmı aynı anda bulunabilir.

---

# 📌 30 Saniyelik Özet

```
JSON
json.load(file)
→ JSON parse et

MALFORMED
→ JSONDecodeError

PARSE
→ “Bu JSON mu?”

VALIDATE
→ “Benim schema'ma uyuyor mu?”

NORMALIZE
→ “Hangi temiz formatta kullanacağım?”

SCHEMA
asset_id → non-empty str
hostname → non-empty str
port     → exact int, 1..65535
active   → bool
tags     → list[str]

JQ
jq .
→ JSON parse

.port | type
→ alan tipi

has("x")
→ key var mı?

select(...)
→ koşullu filtre

-e
→ exit-status odaklı kullanım

JQ'NUN ROLÜ
Python'a özellik eklemez
→ bağımsız ikinci kanıt

GIT
Working Tree
→ diskte üzerinde çalıştığım hâl

Index
→ bir sonraki commit'e hazırlanan hâl

HEAD
→ mevcut commit konumuna referans

git add
Working Tree → Index

git diff
Index ↔ Working Tree

git diff --staged
HEAD ↔ Index

git commit
Index → Local history

git push
Local commits → Remote

KRİTİK
HEAD = A
Index = B
Working Tree = C

A → B = staged
B → C = unstaged
```

---

# ✅ Günün Kazanımları

- JSON syntax ile application schema validation ayrıldı
    
- `json.load()` ve `json.loads()` farkı öğrenildi
    
- JSON → Python tip dönüşümleri pekiştirildi
    
- Malformed JSON için `JSONDecodeError` kullanıldı
    
- Geçerli JSON ile geçerli uygulama verisi ayrıldı
    
- Required key kontrolleri yapıldı
    
- Aynı kurala sahip string alanlar tek döngüde doğrulandı
    
- Whitespace-only string kontrolü uygulandı
    
- `bool` / `int` tip nüansı fark edildi
    
- Port için exact type ve range validation yapıldı
    
- `tags` hem container hem eleman tipi açısından doğrulandı
    
- Validation ve normalization ayrıldı
    
- Orijinal veri yerine yeni normalize dict oluşturuldu
    
- `strip()` sonucunun saklanması gerektiği pekiştirildi
    
- `JSONDecodeError` / `ValueError` exception sırası öğrenildi
    
- Module shadowing riski fark edildi
    
- `jq` ile JSON bağımsız olarak parse edildi
    
- `jq type` ile veri tipi doğrulandı
    
- `has()` ile key varlığı test edildi
    
- `select()` mantığı öğrenildi
    
- `jq -e` ile exit-code odaklı doğrulama fikri öğrenildi
    
- `jq`'nun Python'a bir şey eklemediği, bağımsız doğrulama sağladığı netleşti
    
- Git repository `git init` ile oluşturuldu
    
- Working Tree kavramı öğrenildi
    
- Index / Staging Area kavramı öğrenildi
    
- `git add` ile commit arasındaki fark anlaşıldı
    
- HEAD kavramı öğrenildi
    
- `git diff` ve `git diff --staged` ayrıldı
    
- Untracked dosyanın normal `git diff`te görünmemesi gözlemlendi
    
- İlk commit öncesi staged yeni dosya diff'i incelendi
    
- Stage sonrası dosyayı değiştirme deneyi yapıldı
    
- Aynı dosyanın aynı anda staged + unstaged olabileceği görüldü
    
- `git commit`'in Index'i kaydettiği öğrenildi
    
- `git push`'ın local commit'leri remote'a taşıdığı öğrenildi
    

> [!success] 🚀 Gün sonu sonucu  
> Gün 18'de iki çok önemli **katman modeli** oturdu.
> 
> JSON:
> 
> ```
> Parse
> ↓
> Validate
> ↓
> Normalize
> ```
> 
> Git:
> 
> ```
> Working Tree
> ↓
> Index
> ↓
> Commit
> ↓
> Remote
> ```
> 
> İkisinde de aynı düşünme biçimi geçerli:
> 
> **“Şu anda hangi katmandayım ve elimdeki veri/snapshot hangi aşamanın gerçeğini temsil ediyor?”**
> 
> Özellikle Git için kafada tutulması gereken tek şema:
> 
> ```
> HEAD          INDEX          WORKING TREE
>   A             B                 C
> 
> A → B = staged
> B → C = unstaged
> ```
> 
> Bu şema oturduğunda `git add`, `git diff`, `git diff --staged` ve `git commit` davranışları birbirine karışmaz.