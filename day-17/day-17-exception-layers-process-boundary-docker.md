---
title: "Gün 17 — Python Exception Katmanları, Raise, Process Sınırı ve Docker"
tags:
  - coreops
  - python
  - linux
  - docker
  - exceptions
  - raise
  - exit-code
  - process
  - debugging
aliases:
  - "Gün 17 Exception Katmanları Raise ve Process Sınırı"
status: completed
duration_minutes: "85-90"
---

# 🧠 Gün 17 — Python Exception Katmanları, `raise`, Process Sınırı ve Docker

> [!abstract] 🎯 Ana fikir  
> Bugünün temel zinciri:
> 
> ```
> Alt fonksiyon
> → Hatanın NE olduğunu belirler
> → exception yükseltir
> 
> main()
> → Bu hatayla NE YAPILACAĞINA karar verir
> → stderr / exit code üretir
> 
> Process
> → stdout + stderr + exit status ile dış dünyaya görünür
> 
> Docker
> → Python exception'ını değil,
>   ana process'in sonucunu görür
> ```
> 
> En kritik ayrım:
> 
> **Exception Python'ın iç mekanizmasıdır; exit code process sınırındaki sözleşmedir.**

---

# ⚡ 2 Dakikalık Geri Çağırma

Önceki günün CLI katmanından sonra artık:

```
Shell ✅
argparse ✅
path parse edildi ✅
```

ise ve verilen path/program girdisi işlenirken sorun oluşuyorsa artık uygulama mantığı katmanına gelmişizdir.

Yani hata zincirini:

```
Shell
↓
argparse
↓
uygulama
```

şeklinde takip etmek gerekir.

---

# 🐍 `return ValueError(...)` vs `raise ValueError(...)`

Bunlar tamamen farklı davranışlardır.

## `return ValueError(...)`

```
return ValueError("Geçersiz")
```

Bu:

```
Fonksiyonu normal şekilde bitirir
↓
ValueError nesnesini normal bir değer gibi döndürür
```

Exception mekanizması başlamaz.

---

## `raise ValueError(...)`

```
raise ValueError("Geçersiz")
```

Bu:

```
Normal akışı keser
↓
Exception handling mekanizmasını başlatır
↓
Uygun except aranır
```

---

> [!danger] TIRT
> 
> ```
> return ValueError(...)
> ```
> 
> yazmak hata fırlatmak değildir.

---

# 🔁 `return` ile `raise`

```
return
→ Normal fonksiyon sonucu

raise
→ Normal akışın dışına çık
→ Exception zincirine gir
```

Örneğin:

```
def read_limit(path):
    ...
    if sayı <= 0:
        raise ValueError

    return sayı
```

Burada:

```
Pozitif sayı
→ return

Geçersiz sayı
→ raise
```

sözleşmesi oluşur.

---

# 📂 Günün `read_limit()` Fonksiyonu

Kaynak implementasyon:

```
def read_limit(path):
    with open(
        path,
        encoding="utf-8",
    ) as file:
        sayı = file.read()

    sayı = sayı.strip()
    sayı = int(sayı)

    if sayı <= 0:
        raise ValueError

    return sayı
```

Fonksiyonun görevi:

```
Dosyayı oku
↓
Whitespace temizle
↓
int'e dönüştür
↓
Pozitif mi?
├─ Hayır → ValueError
└─ Evet  → int döndür
```

---

# 🎯 `read_limit()` Sözleşmesi

Kaynak notta hedef davranış şu şekilde belirlenmiş.

|Dosya içeriği|Sonuç|
|---|---|
|`25`|`25`|
|`1`|`1`|
|`0`|`ValueError`|
|`-4`|`ValueError`|
|`abc`|`ValueError`|
|Dosya yok|`FileNotFoundError`|

Ama iki farklı `ValueError` kaynağı var.

---

# 🧩 `abc` ile `-4` Aynı Hata Türü, Farklı Sebep

## `"abc"`

```
int("abc")
```

Python'ın kendi dönüşüm kuralı başarısız olur.

Python kendisi:

```
ValueError
```

üretir.

---

## `"-4"`

```
int("-4")
```

başarılıdır:

```
-4
```

Ama uygulama sözleşmesi:

```
limit > 0
```

dediği için:

```
if sayı <= 0:
    raise ValueError
```

ile hatayı **biz yükseltiyoruz**.

> [!important]  
> Aynı exception türü farklı katmanlardan doğabilir.
> 
> ```
> abc
> → parsing/dönüşüm problemi
> 
> -4
> → uygulama kuralı problemi
> ```

---

# ⬆️ Exception Nasıl Yukarı Doğru İlerler?

Bir exception oluştuğunda mevcut fonksiyonda yakalanmazsa çağıran katmana doğru çıkar.

```
read_limit()
    ↓
ValueError
    ↓
read_limit içinde except yok
    ↓
main()
    ↓
except ValueError var mı?
├─ Evet → işle
└─ Hayır
    ↓
Daha yukarı
    ↓
Python interpreter
    ↓
Traceback
```

Buna exception propagation denebilir.

---

# 🧠 Call Stack Zihinsel Modeli

```
Python Runtime
    ↑
main()
    ↑
read_limit()
    ↑
int(...)
```

Altta oluşan hata:

```
ValueError
```

uygun bir `except` bulana kadar yukarı çıkar.

---

# 🎯 Alt Katman ve Üst Katmanın Sorumluluğu

Çok önemli ayrım:

```
read_limit()
→ Ne yanlış olduğunu bilir.

main()
→ Bu hatayla ne yapılacağını bilir.
```

Örneğin:

```
read_limit()
→ ValueError

main()
→ Kullanıcıya mesaj bas
→ stderr kullan
→ exit code 11 seç
```

---

# 🧱 Neden `read_limit()` İçinde `sys.exit()` Yok?

TIRT yapı:

```
def read_limit(path):
    ...
    if sayı <= 0:
        print("Hatalı!")
        sys.exit(11)
```

Böyle olursa fonksiyon:

- Process yönetimine bağlanır.
    
- CLI'a bağımlı hâle gelir.
    
- Test edilmesi zorlaşır.
    
- Başka kod tarafından tekrar kullanılması zorlaşır.
    

Daha temiz:

```
def read_limit(path):
    ...
    if sayı <= 0:
        raise ValueError
```

Sonra process kararı:

```
def main():
    try:
        ...
    except ValueError:
        ...
        return 11
```

---

# 🎻 Yine Aynı Orkestra Şefi Modeli

```
read_limit()
→ İş fonksiyonu

main()
→ Orkestra şefi

sys.exit(main())
→ Process sınırı
```

Fonksiyonun işi:

```
Dosyayı okuyup geçerli limit üretmek.
```

Main'in işi:

```
Başarı mı?
Hangi hata?
Kullanıcıya ne gösterilecek?
Process hangi exit code ile bitecek?
```

---

# 🖥️ CLI Katmanı

Program:

```
python day17.py input.txt
```

şeklinde çalışıyor.

```
parser = argparse.ArgumentParser()
parser.add_argument("path")
args = parser.parse_args()
```

sonrasında:

```
read_limit(args.path)
```

çağrılıyor.

Bu önemli çünkü:

```
read_limit("input.txt")
```

şeklinde hardcoded path kullanmak CLI sözleşmesini anlamsızlaştırırdı.

---

# 🚨 `main()` Exception Politikası

Kaynak kodda:

```
except ValueError:
    print(
        "Hatalı değer!!",
        file=sys.stderr,
    )
    return 11

except FileNotFoundError:
    print(
        "Girdiğiniz path bulunamadı!!",
        file=sys.stderr,
    )
    return 22
```

kullanılıyor.

Sonuç:

```
Başarı
→ exit 0

Geçersiz değer
→ exit 11

Dosya yok
→ exit 22
```

---

# 🚪 `sys.exit(main())`

```
if __name__ == "__main__":
    sys.exit(main())
```

Main:

```
return 11
```

yaparsa process:

```
exit status = 11
```

ile sonlanır.

Bu köprü:

```
Python fonksiyon dönüşü
↓
Process exit status
```

arasındaki bağlantıyı kurar.

---

# 📊 Uygulamanın Exit Code Sözleşmesi

|   |   |
|---|---|
|Durum|Exit Code|
|Başarı|`0`|
|Geçersiz değer|`11`|
|Dosya bulunamadı|`22`|

Bunlar Python tarafından otomatik atanmış özel anlamlar değildir.

**Uygulamanın kendi tasarım kararıdır.**

---

# ❗ Exception Türü ile Exit Code Arasında Otomatik Eşleşme Yok

TIRT:

```
ValueError
→ kesin 1

FileNotFoundError
→ kesin 2
```

Böyle bir zorunluluk yok.

Sen istersen:

```
ValueError        → 11
FileNotFoundError → 22
```

tasarlarsın.

Başka uygulama başka kodlar seçebilir.

Kaynakta bu ayrım doğru şekilde belirtilmiş.

---

# 🚨 `except Exception:` Neden Riskli?

Örneğin:

```
try:
    ...
except Exception:
    print("Bir hata oldu")
```

çok geniştir.

Beklemediğin gerçek programlama hatalarını da gizleyebilir.

Mesela kodda yanlışlıkla:

```
IndexError
AttributeError
TypeError
```

oluştu.

Ama:

```
except Exception:
```

bunu yakalayıp yalnız:

```
Bir hata oldu
```

basarsa gerçek sebebi görmek zorlaşır.

> [!important]  
> Beklediğin ve anlamlı şekilde yönetebildiğin exception'ları mümkün olduğunca spesifik yakala.

---

# 🧹 `finally`

`finally` şu demek değildir:

> “Exception çözüldü.”

Gerçek görevi:

> “Ne olursa olsun bu çıkış kodunu çalıştır.”

Kaynak notta da bu ayrım açık şekilde verilmiş.

```
Exception
↓
finally çalışır
↓
Exception yakalanmadıysa
↓
Yukarı çıkmaya devam eder
```

---

# 📦 `finally` Nerede Kullanılır?

Genellikle cleanup için.

Örneğin kavramsal olarak:

```
try:
    kaynak_ac()
    işlem_yap()
finally:
    kaynak_temizle()
```

Ama dosya açmada çoğu durumda zaten:

```
with open(...)
```

kaynak yaşam döngüsünü daha temiz yönetir.

---

# 📖 Dosya Okuma Yöntemlerini Tekrar Ayır

Kaynak çalışmada önemli bir hata:

```
for x in file.read():
```

kullanmak olmuş.

Eğer dosya:

```
25
```

ise:

```
file.read()
```

şunu üretir:

```
"25"
```

ve:

```
for x in "25":
```

şöyle iterasyon yapar:

```
"2"
"5"
```

Yani karakter karakter.

---

# 🧠 Okuma Biçimleri

```
file.read()
```

→ Bütün kalan içerik tek `str`

```
file.readline()
```

→ Tek satır

```
file.readlines()
```

→ Satırların listesi

```
for line in file:
```

→ Satır satır iterasyon

```
for char in file.read():
```

→ Okunan string üzerinde karakter karakter iterasyon

---

# ✅ Bu Görevde Neden `file.read()`?

Dosyada tek bir sayı olması bekleniyor:

```
25
```

Bu yüzden:

```
sayı = file.read()
```

yeterli.

Sonra:

```
sayı = sayı.strip()
sayı = int(sayı)
```

---

# 🔥 V2 Fikri — Çoklu Veri

Kaynak notta daha sonra güzel bir tasarım sorusu ortaya çıkmış.

Dosya:

```
25
-4
abc
80
0
32
```

olsun.

Bu durumda ilk hatada programı kesmek yerine:

```
Uyanlar:
25, 80, 32

Uymayanlar:
-4, abc, 0
```

şeklinde bütün veriyi taramak daha anlamlı olabilir.

---

# 🎯 Çok Önemli Tasarım Dersi

> Her geçersiz veri exception olmak zorunda değildir.

Tek değer bekleyen fonksiyonda:

```
Geçersiz değer
→ işlem yapılamıyor
→ ValueError mantıklı
```

Ama dataset tarayıcısında:

```
Geçersiz satır
→ beklenen bir veri durumu olabilir
→ listeye ekle
→ sonraki satıra geç
```

daha mantıklı olabilir.

Bu tamamen uygulama sözleşmesine bağlıdır.

---

# 🐧 Linux — Process Sınırı

Python'ın iç dünyası ile shell'in gördüğü dünya farklıdır.

Kaynak notun en güçlü modeli:

```
PYTHON PROCESS
├── ValueError
├── FileNotFoundError
├── try / except
├── traceback
└── Python nesneleri
        │
        │ PROCESS BOUNDARY
        ▼
SHELL
├── stdout
├── stderr
└── exit status
```

---

# 🔥 Tek Cümlelik Model

> **Exception Python'ın iç dili; exit status process ile shell arasındaki dildir.**

---

# ❓ Shell `ValueError` Nesnesini Görür mü?

Hayır.

Shell:

```
ValueError: invalid literal...
```

yazısını görürse bu gerçek Python `ValueError` nesnesi değildir.

Python:

```
Exception nesnesi
↓
Traceback metni üretir
↓
stderr'e yazar
```

Shell yalnız metni görür.

---

# 💥 Yakalanmamış Exception

Akış:

```
ValueError
↓
read_limit yakalamadı
↓
main yakalamadı
↓
call stack'te yukarı
↓
Python interpreter
↓
Traceback stderr'e
↓
Process başarısız
```

Gerçek deneyde `asd` verisiyle traceback oluşmuş ve process exit code `1` ile bitmiş.

---

# 🛡️ Yakalanmış Exception

Akış:

```
ValueError
↓
except ValueError
↓
Programcı kontrolü ele alır
↓
Kendi mesajını üretir
↓
Kendi exit code'unu seçer
```

Gerçek deney:

```
asd
↓
Hatalı değer!!
↓
exit 11
```

şeklinde oldu.

---

# 🔀 Aynı Exception, Farklı Dış Davranış

## Yakalanmış

```
Hatalı değer!!
exit 11
```

## Yakalanmamış

```
Traceback ...
ValueError: ...
exit 1
```

İkisinde de içte:

```
ValueError
```

oluşmuş olabilir.

Ama process sınırındaki davranış farklıdır.

---

# ⚠️ Exception Oluştu = Process Kesin Başarısız Oldu mu?

Hayır.

Örneğin:

```
try:
    ...
except ValueError:
    print("Sorunu yönettim")
```

ve program sonra normal biterse:

```
exit 0
```

olabilir.

Dolayısıyla:

```
Python içinde exception oluşması
≠
Process dış dünyaya kesin failure bildirdi
```

CLI programında gerçek hata varsa genellikle non-zero exit code ile bunu dış dünyaya bildirmek gerekir.

---

# 📤 Shell'in Üç Kanıtı

Process sınırının dışına temel olarak:

```
stdout
stderr
exit status
```

çıkar.

Debug ederken bunları ayrı düşün:

```
stdout
→ Normal sonuç neydi?

stderr
→ Diagnostic/hata mesajı neydi?

$?
→ Process başarı mı failure mı bildirdi?
```

---

# 🐳 Docker — Exception Policy Değişmez

Docker:

```
ValueError
FileNotFoundError
try
except
raise
```

gibi Python mekanizmalarını yorumlamaz.

Bunları Python interpreter yönetir.

Docker'ın baktığı:

```
Ana process başladı mı?
Çalışıyor mu?
Bitti mi?
Hangi exit code ile bitti?
```

Kaynak nottaki zincir:

```
Exception
↓
Python exception policy
↓
Process sonucu
↓
Exit code
↓
Docker container state
```

---

# 📦 Container State

Ana process çalışıyorsa:

```
running
```

Ana process biterse:

```
exited
```

Process'in exit code'u da container state'ine yansır.

---

# 🎯 Python Process ile Docker Katmanını Ayır

## Application failure

```
docker run
↓
Container başladı
↓
Python başladı
↓
day17.py çalıştı
↓
ValueError / FileNotFoundError
↓
main yönetti
↓
non-zero exit
```

Bu bir **uygulama failure**'ıdır.

---

## Docker / container başlatma problemi

```
docker run
↓
Container veya komut başlatılamadı
↓
Python script başlamadı bile
```

Bu daha dış katmandaki problemdir.

Kaynak notta da bu ayrım vurgulanmış.

---

# 🔢 Docker'ın Özel Run Hata Kodları

Yaygın Docker CLI/runtime ayrımında:

```
125
→ docker run tarafında container başlatma/runtime hazırlama hatası

126
→ Komut bulundu fakat çalıştırılamadı

127
→ Komut bulunamadı
```

Ama uygulama:

```
11
22
```

gibi kendi exit code'larını üretirse Docker bunları da ana process sonucu olarak taşıyabilir.

---

# 🧪 Docker Deneyi

Host `bad.txt`:

```
-5
```

Container:

```
docker run --rm \
  --mount type=bind,source="$PWD",target=/app,readonly \
  -w /app \
  python:3.12-slim \
  python day17.py bad.txt
```

sonucunda:

```
Hatalı değer!!
```

görüldü.

Bu bize:

```
Docker çalıştı ✅
Container başladı ✅
Python başladı ✅
Script çalıştı ✅
Uygulama ValueError üretti ✅
main() bunu yönetti ✅
```

dedirtiyor.

---

# 📂 FileNotFoundError Deneyi

Container içinde:

```
python day17.py bad.txt
```

ama dosya mount içinde yoksa:

```
Girdiğiniz path bulunamadı!!
```

mesajı üretilmiş.

Yine:

```
Python başladı.
```

Çünkü uygulamanın kendi `FileNotFoundError` sözleşmesine kadar ulaşıldı.

---

# 🔗 Bind Mount Nerede?

Düzeltme:

> Bind mount image'a yapılmaz.

Akış:

```
python:3.12-slim IMAGE
↓
Container oluşturulur
↓
Host klasörü container filesystem'indeki /app'e bind mount edilir
↓
Python process başlar
```

Yani:

```
Image
≠
Bind mount yapılmış nesne

Container filesystem görünümü
→ Runtime mount'tan etkilenir
```

Kaynak notta bu ayrım açıkça düzeltilmiş.

---

# 🔒 `readonly` Exception Politikasını Değiştirir mi?

Hayır.

```
--mount ...,readonly
```

filesystem yazma yeteneğini etkiler.

Ama:

```
ValueError nasıl yakalanıyor?
main hangi exit code'u döndürüyor?
```

gibi uygulama politikalarını değiştirmez.

---

# 🧱 Docker Build Gerekiyor muydu?

Hayır.

Bu görevde hazır:

```
python:3.12-slim
```

image'ı ve bind mount kullanıldı.

Dolayısıyla yeni image üretmeye gerek yoktu.

```
docker run --rm \
  --mount type=bind,source="$PWD",target=/app \
  -w /app \
  python:3.12-slim \
  python day17.py bad.txt
```

yeterliydi.

---

# 🧩 Ustalık Kontrolündeki Kritik Senaryo

Senaryo:

```
read_limit()
→ ValueError yükseltiyor

main()
→ yalnız FileNotFoundError yakalıyor
```

Ne olur?

```
read_limit
↓
ValueError
↓
main'e çıkar
↓
except FileNotFoundError eşleşmez
↓
main'den de çıkar
↓
Python interpreter
↓
Traceback stderr
↓
Process non-zero
```

Kaynak cevabın bu mantığı doğru kurmuş.

---

# 🧯 Hata Avı

## 1. `return ValueError()` exception yükseltir

TIRT.

Normal değer döndürür.

---

## 2. `raise ValueError()` normal return'dür

TIRT.

Normal kontrol akışını keser.

---

## 3. Exception yalnız oluştuğu fonksiyonda yakalanabilir

TIRT.

Yakalanmazsa çağrı zincirinde yukarı ilerleyebilir.

---

## 4. `except Exception:` en güvenli çözümdür

TIRT.

Beklenmeyen programlama hatalarını gizleyebilir.

---

## 5. `finally` exception'ı yakalar

TIRT.

Cleanup çalıştırır; exception yakalanmadıysa exception devam eder.

---

## 6. `int("-4")` ValueError üretir

TIRT.

```
int("-4")
```

başarıyla `-4` üretir.

ValueError'ı uygulama kuralı nedeniyle biz yükseltiyoruz.

---

## 7. `int("abc")` uygulamanın elle raise ettiği hatadır

TIRT.

`int()` kendisi `ValueError` üretir.

---

## 8. `for x in file.read()` satır satır okur

TIRT.

Okunan string üzerinde karakter karakter dolaşır.

---

## 9. Exception türü exit code'u otomatik belirler

TIRT.

Exit code uygulama/process politikasıdır.

---

## 10. Shell gerçek `ValueError` Python nesnesini görür

TIRT.

Shell yalnızca process'in çıktılarını ve exit status'ünü görür.

---

## 11. Exception yakalanırsa process otomatik non-zero olur

TIRT.

Programcı non-zero dönmezse process başarıyla bitebilir.

---

## 12. Traceback görmek shell'in Python exception sistemini anladığı anlamına gelir

TIRT.

Python traceback'i metin olarak stderr'e yazmıştır.

---

## 13. Docker `ValueError`'ı yorumlar

TIRT.

Python yorumlar; Docker ana process sonucunu gözlemler.

---

## 14. Container başladıktan sonra Python hata verdiyse bu Docker run-time hazırlama hatasıdır

TIRT.

Python başladıysa uygulama katmanına kadar gelinmiştir.

---

## 15. Bind mount image'ın içine uygulanır

TIRT.

Runtime sırasında image'dan oluşturulan container'ın filesystem görünümüne uygulanır.

---

# 🧠 Kafaya Kazı

> [!quote]  
> `return` normal sonuçtur; `raise` exception akışıdır.

> [!quote]  
> `return ValueError()` hata fırlatmaz.

> [!quote]  
> Exception yakalanmazsa çağıran katmana doğru ilerler.

> [!quote]  
> Alt fonksiyon neyin yanlış olduğunu, üst katman bununla ne yapılacağını bilir.

> [!quote]  
> İş fonksiyonunun `sys.exit()` bilmesine gerek yoktur.

> [!quote]  
> `main()` uygulamanın process sözleşmesini yönetebilir.

> [!quote]  
> `"abc"` dönüşüm hatasıdır; `-4` uygulama kuralı hatasıdır.

> [!quote]  
> `finally` cleanup yapar, exception'ı otomatik çözmez.

> [!quote]  
> Exception türü ile exit code arasında zorunlu eşleşme yoktur.

> [!quote]  
> Shell Python exception nesnelerini görmez.

> [!quote]  
> Process sınırından stdout, stderr ve exit status çıkar.

> [!quote]  
> Yakalanmış exception'ın dış davranışını programcı belirler.

> [!quote]  
> Yakalanmamış exception genellikle traceback üretir.

> [!quote]  
> Docker Python exception politikasını değiştirmez.

> [!quote]  
> Docker ana process'in çalışıp çalışmadığını ve nasıl sonlandığını izler.

> [!quote]  
> Application failure ile container başlatma failure'ı farklı katmanlardır.

---

# 📌 30 Saniyelik Özet

```
PYTHON
return
→ Normal fonksiyon sonucu

raise
→ Exception başlat

read_limit()
→ Dosya oku
→ strip
→ int
→ sayı > 0 kontrolü
→ int return / ValueError

ERROR
"abc"
→ int() ValueError

-4 / 0
→ int() başarılı
→ uygulama raise ValueError

PROPAGATION
Alt fonksiyon
↓
Çağıran fonksiyon
↓
main
↓
Python runtime

MAIN
ValueError
→ stderr
→ return 11

FileNotFoundError
→ stderr
→ return 22

Başarı
→ return 0

PROCESS
sys.exit(main())
→ main dönüşünü exit status yapar

SHELL
Python nesnesi görmez
↓
stdout
stderr
exit status

YAKALANMIŞ
ValueError
→ özel mesaj
→ özel exit code

YAKALANMAMIŞ
ValueError
→ traceback
→ non-zero process

DOCKER
Exception
→ Python işler
→ Process biter
→ Exit code
→ Container state

KRİTİK
Python hata türünü bilir.
main dış davranışı belirler.
Docker process sonucunu taşır.
```

---

# ✅ Günün Kazanımları

- `return ValueError()` ile `raise ValueError()` ayrıldı
    
- Normal control flow ile exception flow ayrıldı
    
- Exception propagation / call stack modeli öğrenildi
    
- Alt fonksiyon ile `main()` arasında hata sorumluluğu ayrıldı
    
- `read_limit()` için açık bir davranış sözleşmesi kuruldu
    
- `int("abc")` kaynaklı doğal `ValueError` gözlemlendi
    
- Negatif/0 değer için uygulamanın kendi `ValueError`'ı yükseltildi
    
- İş fonksiyonunda `sys.exit()` kullanmama prensibi pekiştirildi
    
- Spesifik `except` blokları kullanıldı
    
- Geniş `except Exception:` kullanımının riski anlaşıldı
    
- `finally` ile exception handling ayrıldı
    
- `file.read()` ile karakter iterasyonu arasındaki fark tekrar edildi
    
- Çoklu veri için exception yerine veri sınıflandırma fikri geliştirildi
    
- Python exception sistemi ile shell process modeli ayrıldı
    
- Shell'in `ValueError` nesnesini değil stderr metnini gördüğü kavrandı
    
- Yakalanmış ve yakalanmamış exception davranışı karşılaştırıldı
    
- Traceback gerçek deneyle gözlemlendi
    
- Exit code'un exception türünden bağımsız tasarlanabileceği öğrenildi
    
- Process sınırında stdout / stderr / exit status modeli oturdu
    
- Docker'ın Python exception'ını yorumlamadığı öğrenildi
    
- Container state ile ana process yaşam süresi ilişkilendirildi
    
- Application failure ile Docker/container başlatma failure'ı ayrıldı
    
- Hazır Python image + bind mount ile build yapmadan görev çalıştırıldı
    
- Bind mount'un image'a değil container filesystem'ine uygulandığı netleşti
    

> [!success] 🚀 Gün sonu sonucu  
> Gün 17 sonunda hata yönetimi artık yalnız:
> 
> ```
> try / except yazıp hata mesajı basmak
> ```
> 
> olarak değil, katmanlı bir sözleşme olarak düşünülmeye başlandı:
> 
> ```
> read_limit()
> → Hatanın ne olduğunu belirler.
> 
> main()
> → Hatayla ne yapılacağını belirler.
> 
> sys.exit()
> → Sonucu process seviyesine taşır.
> 
> Shell
> → stdout / stderr / exit status görür.
> 
> Docker
> → Ana process'in sonucunu container state olarak taşır.
> ```
> 
> Günün en kritik cümlesi:
> 
> **Exception uygulamanın iç kontrol mekanizmasıdır; process sınırından dış dünyaya exception nesnesi değil, gözlemlenebilir çıktı ve exit status çıkar.**