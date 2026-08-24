---
title: "Gün 34 — DNS Candidate IP'ler, TCP Connect ve Actual Peer"
tags:
  - coreops
  - day34
  - network
  - dns
  - tcp
  - socket
  - getaddrinfo
  - create-connection
  - getpeername
  - troubleshooting
  - python
aliases:
  - "Gün 34 TCP Candidate ve Actual Peer"
status: completed
---

# 🌐 Gün 34 — DNS Candidate IP'ler, TCP Connect ve Actual Peer

> [!abstract] 🎯 Günün ana fikri
> Bugün DNS'in bana verdiği **candidate IP'ler** ile TCP bağlantısında **gerçekte bağlandığım remote endpoint** arasındaki farkı öğrendim.
>
> En önemli mental model:
>
> **DNS candidate ≠ actual connected peer**
>
> Akış:
>
>     URL
>      ↓
>     hostname + port
>      ↓
>     getaddrinfo()
>      ↓
>     candidate IP'ler
>      ↓
>     create_connection()
>      ↓
>     connected socket
>      ↓
>     getpeername()
>      ↓
>     actual peer

---

# 🧠 Hızlı Anlayış

## Resolver A, B, C döndürdüyse neden "A'ya bağlandım" diyemem?

Çünkü:

    A
    B
    C

yalnızca bağlantı için kullanılabilecek candidate adreslerdir.

Resolver'ın ilk döndürdüğü adresin gerçekten kullanılacağını garanti edemem.

Örneğin:

    A → bağlantı başarısız
    B → bağlantı başarısız
    C → bağlantı başarılı

olabilir.

Bu durumda actual peer:

    C

olur.

Dolayısıyla:

> **Candidate adres tahmin/olasılık state'idir. Actual peer ise gerçekleşmiş connection state'idir.**

---

## TCP başarılıysa TLS veya HTTP hakkında ne kanıtlamadım?

Katmanlar:

    DNS
     ↓
    TCP
     ↓
    TLS
     ↓
    HTTP

TCP başarılıysa yalnızca:

> Remote IP:port ile TCP bağlantısı kurabildim.

kanıtlanmıştır.

Henüz:

    TLS = ?
    HTTP = ?

durumundadır.

Yani:

> **TCP success ≠ TLS success ≠ HTTP success**

---

# 🔎 1. URL'den Host ve Port Çıkarmak

Program CLI'dan URL alıyor:

`python resolve_url.py "https://example.com/"`

URL:

`urlparse()` ile parçalanıyor.

İlgilendiğim temel alanlar:

- `url.scheme`
- `url.hostname`
- `url.port`

Örneğin:

`https://example.com:8443/`

için:

    scheme   → https
    hostname → example.com
    port     → 8443

---

# 🚦 Scheme Kontrolü

Program yalnız:

- `http`
- `https`

kabul ediyor.

Bunun dışındaki scheme'lerde kontrollü şekilde hata veriyorum.

Bu aşama henüz DNS veya TCP değildir.

Bu:

> **Input / URL validation aşamasıdır.**

---

# 🚪 Default Port Mantığı

URL'de açıkça port yoksa scheme'e göre default port belirliyorum.

HTTP:

    80

HTTPS:

    443

Örnek:

`http://example.com/`

→ `80`

`https://example.com/`

→ `443`

Ama:

`https://example.com:8443/`

gelirse:

    8443

kullanılır.

Burada önemli nokta:

> URL'de explicit port varsa default port onu ezmemeli.

---

# 🧭 2. `getaddrinfo()` Ne Yapıyor?

Kullandığım:

`socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)`

Bu fonksiyonun görevi bağlantı kurmak değildir.

Bana:

> "Bu host:port için kullanılabilecek socket adresleri bunlar."

der.

Yani:

    hostname + port
           ↓
      getaddrinfo()
           ↓
      candidate'ler

---

# 🧩 `getaddrinfo()` Sonucu

Her result içerisinde kabaca:

    family
    socktype
    proto
    canonname
    sockaddr

bilgileri bulunuyor.

Ben özellikle:

`sockaddr[0]`

ile IP adresini alıyorum.

Unique IP'leri toplamak için:

`set`

kullandım.

Mantık:

    results
       ↓
    her result
       ↓
    sockaddr[0]
       ↓
    ips set

Örneğin:

    {
        "104.20.23.154",
        "172.66.147.243"
    }

---

# 🎯 Candidate IP Ne Demek?

Candidate:

> Bağlantı için kullanılabilecek olası hedef.

Candidate:

> Gerçekten bağlanılmış hedef.

demek değildir.

Kısa:

    candidate IP
    → olası hedef

    actual peer
    → gerçekten bağlandığım hedef

---

# ⚠️ Resolver Sırasını Connection Kanıtı Sanmamak

Resolver şunu döndürürse:

    A
    B
    C

şu sonucu çıkaramam:

> "A'ya bağlandım."

Çünkü resolver sonucu ile connection sonucu farklı state'lerdir.

Bunu artık şöyle ayırıyorum:

    DNS state
    ≠
    TCP connected state

---

# 🔌 3. TCP Connection

TCP bağlantısını:

`socket.create_connection((host, port), timeout=3)`

ile kurdum.

Burada target:

    host + port

şeklinde.

Çünkü aynı IP üzerinde:

    1.2.3.4:22
    1.2.3.4:80
    1.2.3.4:443

farklı servisler olabilir.

---

# 🤔 TCP Connect'i `for` İçinde mi Yapmalıyım?

Başta bunu düşündüm.

Ama benim `for` döngümün görevi yalnız:

> Candidate IP'leri toplamak.

Doğru akış:

    getaddrinfo()
         ↓
    for result in results
         ↓
    candidate IP'leri topla
         ↓
       FOR BİTTİ
         ↓
    create_connection()

Bu labda amacım her candidate'e manuel bağlanmak değil.

Amaç:

    Resolver ne söyledi?
           vs
    Connection gerçekte nereye gitti?

sorusunu cevaplamak.

---

# 🔗 4. `create_connection()` Ne Döndürüyor?

Başarılı olduğunda:

- `True`
- IP string'i

döndürmüyor.

Bana:

> **Connected socket object**

döndürüyor.

Mental model:

    create_connection()
          ↓
    TCP connection kur
          ↓
    connected socket

Bu socket artık gerçek aktif TCP bağlantısını temsil ediyor.

---

# 👤 5. `getpeername()` — Gerçekte Kime Bağlandım?

Connected socket oluştuktan sonra:

`sock.getpeername()`

kullandım.

Bunun sorduğu soru:

> Bu socket'in remote endpoint'i ne?

Örneğin:

    ('104.20.23.154', 443)

dönerse:

    peer[0] → remote IP
    peer[1] → remote port

Dolayısıyla:

    connected_peer_ip
    connected_peer_port

bilgilerini çıkarabiliyorum.

---

# 🧠 `getpeername()` DNS Yapmaz

Önemli nokta:

`getpeername()` tekrar resolver'a gidip:

> "Bu hostname hangi IP?"

diye sormaz.

Socket zaten connected durumdadır.

Kernel mevcut bağlantının:

- local endpoint
- remote endpoint
- TCP state

bilgilerini zaten bilir.

Bu yüzden:

`getaddrinfo()`

→ Nereye bağlanabilirim?

`getpeername()`

→ Gerçekte nereye bağlıyım?

---

# 🪞 `getpeername()` vs `getsockname()`

Bunları karıştırmamalıyım.

## `getpeername()`

> Karşı taraf kim?

Örnek:

    104.20.23.154:443

## `getsockname()`

> Ben bu connection'da hangi local endpoint'im?

Örnek:

    192.168.1.20:53142

Bir TCP connection:

    LOCAL                              REMOTE

    192.168.1.20:53142  <-------->  104.20.23.154:443

Sol:

    local endpoint

Sağ:

    peer / remote endpoint

---

# 🔍 6. Actual Peer Candidate Listesinde mi?

DNS aşamasından:

`ips`

seti var.

TCP aşamasından:

`connected_peer_ip`

var.

Sonra:

`connected_peer_ip in ips`

ile şu soruyu soruyorum:

> Gerçek bağlantı kurduğum IP, resolver'ın candidate olarak verdiği IP'ler arasında mı?

Lab sonucum:

    DNS candidates:
    {'104.20.23.154', '172.66.147.243'}

    Connected peer:
    104.20.23.154:443

    Peer in candidates:
    True

Bu test bugünkü ana mental modeli pratikte kanıtladı.

---

# ⏱️ 7. Timeout Mantığı

Connection:

`timeout=3`

ile oluşturuluyor.

Ama bunu:

> Program kesin toplam 3 saniyede biter.

şeklinde düşünmemeliyim.

Amaç:

> Socket operasyonunun süresiz bloklanmasını önlemek.

Ayrıca `create_connection()` farklı candidate adresleri deneyebildiği için bu timeout değerini fonksiyonun mutlak toplam çalışma süresi gibi düşünmemeliyim.

---

# ❌ DNS OK, TCP FAIL Olabilir

DNS'in başarılı olması:

    hostname
       ↓
    IP candidate'leri

elde edebildiğim anlamına gelir.

Ama TCP'nin sorusu farklıdır:

    IP + port
       ↓
    Connection kurulabiliyor mu?

Örneğin:

    DNS = OK
    TCP = FAIL

gayet mümkündür.

Labda bunu localhost üzerinde boş porta bağlanarak gördüm.

---

# 🧪 Closed Local Port Testi

Test:

`http://127.0.0.1:65432/`

Sonuç:

    TCP bağlantı hatası:
    Connection refused

Burada:

    IP / adres bilgisi ✅
    TCP connection ❌

Yani:

> **DNS/IP state ile TCP state aynı şey değildir.**

---

# ✅ Custom Port Testi

Test:

`http://127.0.0.1:8080/`

Sonuç:

    Host: 127.0.0.1
    Port: 8080
    DNS candidates: {'127.0.0.1'}
    Peer ip: 127.0.0.1
    Peer port: 8080
    Peer in candidates: True
    TCP: OK

Burada URL'deki explicit:

`8080`

portunun kullanıldığını doğruladım.

---

# 🔐 8. TCP Success, HTTPS Success Değildir

443 portuna TCP connection kurabilmek bile:

> HTTPS çalışıyor.

demek değildir.

Çünkü HTTPS tarafında sırada:

    TCP ✅
     ↓
    TLS ?
     ↓
    HTTP ?

vardır.

TCP'nin başarı kriteri ile TLS'in başarı kriteri farklıdır.

---

# 🧹 9. Socket Resource Yönetimi

Başta:

`sock = socket.create_connection(...)`

kullanıyordum.

Burada işim bittiğinde:

`sock.close()`

çağırmam gerekir.

Çünkü socket işletim sistemi tarafında resource tutar.

Mental model:

    resource aç
        ↓
      kullan
        ↓
      kapat

---

# ✅ `with` Kullanımı

Daha temiz çözüm:

`with socket.create_connection((host, port), timeout=3) as sock:`

Bu durumda:

    with'e gir
       ↓
    socket açık
       ↓
    işlemleri yap
       ↓
    bloktan çık
       ↓
    socket kapanır

Arada exception meydana gelse bile resource cleanup açısından daha güvenli.

Kendime sormam gereken soru:

> **Bu resource'u kim kapatacak?**

---

# 🚨 10. Bare `except:` Hatası

Başta TCP kısmında:

`except:`

kullanmıştım.

Bu fazla geniş.

Problem:

- Network hatasını yakalar.
- Programlama hatasını da gizleyebilir.
- Debugging zorlaşır.
- Failure boundary kaybolur.

DNS için:

`socket.gaierror`

daha anlamlı.

TCP/network sınırında:

`OSError`

daha net kullanılabilir.

Dosyadaki kodumda:

`socket.error`

kullandım.

Modern Python'da bu `OSError` ile aynı exception ailesi/alias yapısıyla ilişkilidir.

Daha açık mental model:

    DNS / resolution
    → socket.gaierror

    TCP / socket / OS
    → OSError

---

# 🚫 Connection Refused

Örneğin:

`127.0.0.1:65432`

üzerinde hiçbir listener yoksa:

`ConnectionRefusedError`

gelebilir.

Bu:

`OSError`

alt sınıfıdır.

Anlamı kabaca:

> Hedefe ulaştım ama bu connection kabul edilmedi.

---

# ⌛ Timeout

Connection belirtilen sürede kurulamazsa:

`TimeoutError`

oluşabilir.

Bu:

> Sunucu kesin kapalı.

demek değildir.

Kanıtladığı şey:

> Connection belirlenen süre sınırı içinde tamamlanmadı.

---

# 🛣️ Network Unreachable

Hedef ağa route olmayabilir.

Bu tip problemler de socket / OS seviyesinde failure üretir.

Yani yine:

> Tek exception'dan gereğinden fazla sonuç çıkarmamalıyım.

---

# 🧱 11. Failure Policy

## DNS Failure

Örnek:

`http://coreops-day34.invalid/`

Beklenen state:

    dns=FAIL
    tcp=NOT_ATTEMPTED

DNS başarısızsa TCP aşamasına geçmemeliyim.

Ayrıca:

- Hata stderr'e gitmeli
- Traceback kullanıcıya saçılmamalı
- Program non-zero exit ile bitmeli

---

## TCP Failure

DNS başarılı olabilir.

Ama connection kurulamayabilir.

Örneğin:

`http://127.0.0.1:65432/`

State:

    dns/ip=OK
    tcp=FAIL

Yine kontrollü hata vermeliyim.

---

# 🧭 12. Programın Son Akışı

    argparse
       ↓
    URL al
       ↓
    urlparse()
       ↓
    scheme kontrolü
       ↓
    hostname kontrolü
       ↓
    host + port
       ↓
    port yoksa default port
       ↓
    getaddrinfo()
       ↓
    candidate IP'ler
       ↓
    DNS failure?
       │
       ├── evet → stderr + non-zero exit
       │
       └── hayır
              ↓
    unique candidate set
              ↓
    create_connection()
              ↓
    TCP failure?
       │
       ├── evet → stderr + non-zero exit
       │
       └── hayır
              ↓
    connected socket
              ↓
    getpeername()
              ↓
    actual peer IP + port
              ↓
    actual IP candidate listesinde mi?
              ↓
    output
              ↓
    with sonu
              ↓
    socket cleanup

---

# 🧹 13. Kullanılmayan State

Önceki URL görevinden:

`path = url.path or "/"`

ve:

`query = url.query`

satırlarını taşımıştım.

Ama bu program HTTP request göndermiyor.

Sadece:

- resolve
- TCP connect

yapıyor.

Dolayısıyla `path` ve `query` burada kullanılmıyor.

Ders:

> **Kullanmadığım state'i gereksiz yere taşımamalıyım.**

---

# 📤 14. Output Contract

Geliştirme sırasında şu formatı kullandım:

    Host: example.com
    Port: 443
    DNS candidates: {...}
    Peer ip: ...
    Peer port: ...
    Peer in candidates: True
    TCP: OK

Ama görev başka bir format istiyorsa buna birebir uymam gerekir.

Örneğin:

    host=example.com
    port=443
    dns_candidates=[...]
    connected_peer_ip=...
    connected_peer_port=443
    peer_in_candidates=True
    tcp=OK

İnsan açısından:

    Host: example.com

ile:

    host=example.com

aynı bilgi olabilir.

Ama otomatik test açısından aynı değildir.

> [!important]
> **Kodun mantığının doğru olması, output contract'ın doğru olduğu anlamına gelmez.**

---

# 🐧 15. `ss -tn` ile İkinci Kanıt

Python bana:

`getpeername()`

ile actual peer'i gösteriyor.

İşletim sistemi tarafında:

`ss -tn`

ile aynı TCP connection'ı görebiliyorum.

`-t`

→ TCP

`-n`

→ adres ve portları numeric göster.

Örneğin:

    State   Local Address:Port      Peer Address:Port
    ESTAB   192.168.1.20:53142      104.20.23.154:443

Python:

    getpeername()
    → 104.20.23.154:443

Kernel:

    ss -tn
    → 104.20.23.154:443

Aynı bilgiyi iki farklı kaynaktan doğrulamış olurum.

---

# ⏳ 16. Connection'ı `ss` ile Görebilmek

Program normalde:

    connect
      ↓
    getpeername
      ↓
    exit

şeklinde çok hızlı çalışıyor.

Bu yüzden program bittikten sonra `ss -tn` çalıştırırsam socket çoktan kapanmış olabilir.

Bu:

> Kod çalışmadı.

demek değildir.

Connection yalnızca çok kısa süre yaşamış olabilir.

---

# 🧪 TCP Socket'i Birkaç Saniye Açık Tutma

Bunu gözlemlemek için demo sürümünde socket açıkken:

`time.sleep(10)`

kullandım.

Önemli nokta:

Sleep:

`with` bloğunun içerisinde.

Çünkü:

    with socket... as sock:
        connection açık
        getpeername()
        time.sleep(10)

şeklinde olduğunda `sleep` sırasında socket hâlâ açıktır.

Eğer `sleep`:

`with`

bloğunun dışına konulsaydı socket önce kapanırdı.

---

# 🔍 `ss` ile Gerçek Test

Demo çalışırken diğer terminalde:

`ss -tn`

çalıştırdım.

Gördüğüm:

    tcp4 ESTAB 0 0 10.3.223.117:58874 104.20.23.154:443

Python tarafında:

    Peer ip: 104.20.23.154
    Peer port: 443

Kernel tarafında:

    104.20.23.154:443

Aynı endpoint'i gördüm.

Bu benim için ikinci bağımsız kanıt oldu.

---

# 🧪 17. Yaptığım Testler

## Normal Connection

`https://example.com/`

Sonuç:

    Host: example.com
    Port: 443
    DNS candidates: {'104.20.23.154', '172.66.147.243'}
    Peer ip: 104.20.23.154
    Peer port: 443
    Peer in candidates: True
    TCP: OK

---

## DNS Failure

`https://coreops-day34.invalid/`

Sonuç:

    DNS hatası meydana geldi

Burada TCP başlamadı.

---

## Closed Local Port

`http://127.0.0.1:65432/`

Sonuç:

    Connection refused

Burada address state başarılı ama TCP başarısız.

---

## Custom Port

`http://127.0.0.1:8080/`

Sonuç:

    Port: 8080
    Peer ip: 127.0.0.1
    Peer port: 8080
    TCP: OK

Explicit port'un korunduğunu doğruladım.

---

# 🐞 Hata Avı

## 1. Resolver'ın ilk IP'sine kesin bağlanırım

TIRT.

Resolver candidate listesi verir.

Actual peer ancak connection sonrasında kanıtlanır.

---

## 2. `getaddrinfo()` connection kurar

TIRT.

Address resolution yapar.

Connection:

`create_connection()`

ile kurulur.

---

## 3. `create_connection()` True döndürür

TIRT.

Connected socket object döndürür.

---

## 4. `getpeername()` yeniden DNS resolve eder

TIRT.

Mevcut connected socket'in remote endpoint'ini verir.

---

## 5. TCP connection'ı candidate topladığım `for` içinde kurmam gerekir

Bu labın amacı açısından gereksiz.

Candidate state'i topladıktan sonra TCP state'ine geçiyorum.

---

## 6. DNS başarılıysa TCP de başarılıdır

TIRT.

    DNS ✅
    TCP ❌

gayet mümkündür.

---

## 7. TCP 443 başarılıysa HTTPS kesin çalışır

TIRT.

    TCP ✅
    TLS ?
    HTTP ?

---

## 8. Socket'i kapatmayı düşünmeme gerek yok

TIRT.

Socket bir OS resource'udur.

Cleanup sahibi belli olmalı.

---

## 9. Bare `except:` yeterlidir

TIRT.

Failure boundary'yi gizler.

---

## 10. Program bittikten sonra `ss` connection göstermiyorsa TCP hiç kurulmamıştır

TIRT.

Socket program çıkarken kapanmış olabilir.

---

## 11. Socket'i `ss` ile görebilmek için `sleep`i herhangi bir yere koyabilirim

TIRT.

Connection'ın açık kalmasını istiyorsam `sleep`, socket'in açık olduğu `with` bloğunun içinde olmalı.

---

## 12. Kod doğruysa output formatı önemsiz

TIRT.

Otomatik test exact output contract bekleyebilir.

---

# 🧠 Kafaya Kazı

> [!quote]
> `getaddrinfo()` connection kurmaz; candidate adresleri üretir.

> [!quote]
> Resolver'ın ilk verdiği IP'yi actual peer sanamam.

> [!quote]
> `create_connection()` başarılı olursa bana connected socket verir.

> [!quote]
> `getpeername()` actual remote endpoint'i verir.

> [!quote]
> `getpeername()` DNS sorgusu değildir.

> [!quote]
> Candidate state ile connected state farklıdır.

> [!quote]
> DNS success, TCP success demek değildir.

> [!quote]
> TCP success, TLS veya HTTP success demek değildir.

> [!quote]
> Socket bir resource'dur; cleanup sahibini bilmeliyim.

> [!quote]
> `with` resource lifecycle yönetimini temizleştirir.

> [!quote]
> Network debugging'de tahmin ile observation'ı birbirine karıştırmamalıyım.

> [!quote]
> İkinci bağımsız kanıt debugging'i güçlendirir.

---

# 📌 30 Saniyelik Özet

    URL
     ↓
    urlparse()
     ↓
    host + port
     ↓
    getaddrinfo()
     ↓
    {candidate A, candidate B, candidate C}
     ↓
    create_connection()
     ↓
    connected socket
     ↓
    getpeername()
     ↓
    actual peer B
     ↓
    B in {A, B, C}
     ↓
    True

Candidate:

    "Buraya bağlanabilirsin."

Actual peer:

    "Gerçekte buraya bağlandın."

Katmanlar:

    DNS
     ↓
    TCP
     ↓
    TLS
     ↓
    HTTP

Her katmanın başarı kriteri farklıdır.

---

# ✅ Günün Kazanımları

- [x] Resolver candidate ile actual peer ayrıldı
- [x] `getaddrinfo()` mantığı oturdu
- [x] Candidate IP'ler set içerisinde toplandı
- [x] Default HTTP/HTTPS portları uygulandı
- [x] Explicit custom port korundu
- [x] `create_connection()` ile TCP bağlantısı kuruldu
- [x] `create_connection()`ın socket döndürdüğü öğrenildi
- [x] `getpeername()` ile actual remote endpoint bulundu
- [x] `getpeername()`ın DNS sorgusu yapmadığı anlaşıldı
- [x] `getsockname()` ile farkı öğrenildi
- [x] Actual peer candidate listesiyle karşılaştırıldı
- [x] DNS OK / TCP FAIL senaryosu test edildi
- [x] Connection refused gözlemlendi
- [x] Timeout'un gerçek anlamı öğrenildi
- [x] Socket resource lifecycle öğrenildi
- [x] `with` ile otomatik cleanup kullanıldı
- [x] Bare `except` probleminin nedeni anlaşıldı
- [x] DNS ve TCP failure boundary ayrıldı
- [x] Output contract'ın önemi görüldü
- [x] `ss -tn` ile kernel connection state'i gözlemlendi
- [x] `time.sleep(10)` ile socket gözlem için açık tutuldu
- [x] Python `getpeername()` sonucu ile `ss` sonucu karşılaştırıldı
- [x] Aynı TCP connection iki farklı kaynaktan doğrulandı

---

# 🚀 Gün Sonu Sonucu

Bugünün en önemli değişimi şu oldu:

Eskiden:

> Resolver IP verdi, demek ki ona bağlandım.

diye düşünebilirdim.

Artık:

    Resolver
       ↓
    candidate state

ve:

    Connected socket
       ↓
    actual connection state

ayrımını yapıyorum.

Kendime soracağım en önemli soru:

> **Şu anda elimde olası hedef bilgisi mi var, yoksa gerçekleşmiş connection kanıtı mı var?**

Final mental model:

    DNS candidates
         ≠
    actual TCP peer

ve:

    DNS success
         ≠
    TCP success
         ≠
    TLS success
         ≠
    HTTP success