---
title: "Gün 33 — DNS, Routing, TCP, TLS, HTTP ve Python Network Probe"
tags:
  - coreops
  - day33
  - network
  - dns
  - routing
  - tcp
  - tls
  - http
  - openssl
  - curl
  - python
  - troubleshooting
aliases:
  - "Gün 33 Network Troubleshooting"
status: completed
---

# 🌐 Gün 33 — DNS, Routing, TCP, TLS, HTTP ve Python Network Probe

> [!abstract] 🎯 Günün ana fikri
> Bugün bir URL'ye istek atmanın tek bir olay olmadığını, birbirinden bağımsız katmanlardan oluşan bir zincir olduğunu öğrendim.
>
>     URL
>      ↓
>     Name Resolution
>      ↓
>     Routing
>      ↓
>     TCP
>      ↓
>     TLS
>      ↓
>     HTTP
>      ↓
>     Application
>
> Kafama kazımam gereken denklem:
>
> **DNS success ≠ TCP success ≠ TLS success ≠ HTTP success**
>
> Troubleshooting yaparken amaç tahmin etmek değil, problemin ilk hangi katmanda çıktığını kanıtlamak.

---

# 🧠 Araştırma Rotası

## Hostname IP'ye çözülüyor ama 443 bağlantısı kurulamıyor. DNS mi bozuk?

Hayır.

Hostname zaten IP'ye başarıyla çözülmüşse name resolution çalışmıştır.

Problem bundan sonraki katmanlarda olabilir:

- Routing
- Firewall
- TCP
- Servis

Yani:

    hostname
       ↓
    IP bulundu ✅
       ↓
    TCP 443 ❌

Bu durumda DNS'e dönüp bakmak yanlış katmanı suçlamak olur.

---

## TCP 443 kuruldu ama certificate verification başarısız. HTTP request gönderilmiş midir?

Gönderilmiş olmak zorunda değil.

TCP bağlantısı başarılı olabilir:

    TCP ✅

Ama TLS sırasında sertifika doğrulaması patlayabilir:

    TLS ❌

Normal HTTPS istemcisi bu durumda HTTP request göndermeden bağlantıyı kesebilir.

Yani:

    TCP success
    ≠
    TLS success
    ≠
    HTTP request gönderildi

---

## HTTP 500 aldıysam ne çıkarabilirim?

HTTPS isteğinde gerçekten `HTTP 500` cevabı gördüysem istek HTTP katmanına kadar ulaşmıştır.

Minimum olarak zincirin isteğin sunucuya ulaşmasını sağlayacak kadar çalıştığını biliyorum:

- Name resolution yeterince çalıştı
- Routing gerçekleşti
- TCP bağlantısı kuruldu
- TLS HTTP isteğinin gönderilebileceği kadar kuruldu
- HTTP request gönderildi
- Sunucu HTTP response üretti

Ama `500` bana uygulamadaki hatanın tam sebebini söylemez.

Sadece artık ilk şüphelimin DNS veya TCP olmadığını söyler.

---

# 🌍 1. IP ve CIDR

Örnek:

`192.168.10.37/24`

Burada:

- `192.168.10.37` → cihazın IP adresi
- `/24` → CIDR prefix

IPv4 toplam 32 bittir.

`/24` demek:

- İlk 24 bit → network kısmı
- Son 8 bit → host kısmı

Örneğin:

`192.168.10.0/24`

tek bir cihazı değil bütün subneti ifade eder.

Bu örnekte genel kullanılabilir host aralığı:

`192.168.10.1 - 192.168.10.254`

---

# 🧪 LAB 1 — Interface, IP, CIDR ve Gateway

Makinemde gözlemlediğim:

- Aktif interface → `en0`
- IPv4 + CIDR → `10.22.33.217/16`
- Default gateway → `10.22.0.1`

Kullandığım:

`ip -br addr`

Çıktıda önemli satır:

    en0    UP    ...    10.22.33.217/16

Buradan:

> `en0` aktif ve IPv4 adresim `10.22.33.217/16`.

sonucunu çıkardım.

Routing tablosu:

`ip route`

Önemli satır:

    default via 10.22.0.1 dev en0

Bunun anlamı:

> Daha spesifik bir route yoksa trafiği `en0` üzerinden `10.22.0.1` gateway'ine gönder.

---

# 🧭 2. Routing

Bir hedefin IP adresini bilmek, paketin oraya hangi yoldan gideceğini bildiğim anlamına gelmez.

Kernel ayrıca şunlara karar verir:

- Hangi interface?
- Hangi gateway?
- Hangi source IP?

Genel route'ları görmek:

`ip route`

Belirli hedef için kernel'in seçimini görmek:

`ip route get HEDEF`

Örneğin:

`ip route get 8.8.8.8`

Lab çıktım:

    8.8.8.8 via 10.22.0.1 dev en0 src 10.22.33.217

Bunu şöyle okuyorum:

- Hedef → `8.8.8.8`
- Gateway → `10.22.0.1`
- Interface → `en0`
- Source IP → `10.22.33.217`

> [!important]
> IP ve route aynı state değildir.
>
> **IP:** Ben ağda kimim?
>
> **Route:** Bu hedefe hangi yoldan giderim?

---

# 🧮 CIDR Mini Uygulaması

Adresim:

`10.22.33.217/16`

`/16` olduğu için ilk iki octet network kısmı:

`10.22`

Dolayısıyla:

`10.22.33.210`

aynı `/16` subnet içerisinde.

Ama:

`10.23.33.210`

farklı subnet.

Aynı şekilde:

`92.32.124.2`

açıkça farklı bir network.

---

# 🔎 3. DNS ve Name Resolution

DNS'i ilk başta sadece:

    hostname → IP

olarak düşünüyordum.

Temel kullanım bu olsa da farklı record tipleri vardır:

- `A` → IPv4
- `AAAA` → IPv6
- `MX` → mail server
- `TXT` → metinsel kayıtlar
- `CNAME` → başka hostname'e alias

Bir hostname'in IP'ye çözülmesi bana sadece şunu kanıtlar:

> Hostname için bir IP elde edebildim.

Şunu kanıtlamaz:

> O IP'nin 443 portuna bağlanabiliyorum.

---

# ⚠️ `getent` Sadece DNS Değildir

Başta:

`getent = DNS`

diye düşünüyordum.

Bu eksikmiş.

Örneğin:

`getent hosts example.com`

sistemin normal name resolution mekanizmasını kullanır.

Kaynak:

- `/etc/hosts`
- DNS
- LDAP
- diğer NSS kaynakları

olabilir.

Bu kaynakların sırası genellikle:

`/etc/nsswitch.conf`

tarafından belirlenir.

Doğru model:

> **getent = sistem seviyesindeki name resolution**

DNS bunun kaynaklarından yalnızca biri olabilir.

---

# 🧪 LAB 2 — Name Resolution + Route

Kali'de:

`getent ahostsv4 example.com`

çalıştırdım.

IPv4 sonuçlarından bazıları:

    104.20.23.154
    172.66.147.243

Sonra belirli IP için route'a baktım:

`ip route get 104.20.23.154`

Çıktı:

    104.20.23.154 via 192.168.64.1 dev eth0 src 192.168.64.15

Buradan:

- Hedef IP → `104.20.23.154`
- Gateway → `192.168.64.1`
- Interface → `eth0`
- Source IP → `192.168.64.15`

sonuçlarını çıkardım.

---

# 🤝 4. TCP

DNS'den IP'yi elde ettikten sonraki soru:

> Hedef IP'nin istediğim portuna TCP bağlantısı kurabiliyor muyum?

HTTPS için genellikle:

`443/tcp`

kullanılır.

TCP bağlantısının başında 3-way handshake bulunur:

    Client → SYN
    Server → SYN-ACK
    Client → ACK

Bundan sonra TCP connection kurulmuş olur.

---

# TCP Başarılıysa Ne Biliyorum?

Sadece:

> İlgili IP:port ikilisine TCP bağlantısı kurulabildi.

Henüz şunları bilmiyorum:

- TLS başarılı mı?
- Sertifika doğru mu?
- HTTP çalışıyor mu?
- Uygulama düzgün mü?

---

# TCP Hatalarını Yorumlama

## Connection refused

Genellikle hedefe ulaşılmış ama port bağlantıyı kabul etmiyor olabilir.

Olası sebepler:

- Servis çalışmıyor
- Port kapalı
- Firewall aktif reject yapıyor

## Connection timed out

Cevap gelmemiştir.

Olası sebepler:

- Firewall DROP
- Routing problemi
- Host erişilemiyor
- Başka bir network problemi

> [!warning]
> Tek bir hata mesajından gereğinden fazla sonuç çıkarmamalıyım.

---

# 🧪 LAB 3 — TCP Connection'ı `ss` ile Görmek

Bir terminalde:

`openssl s_client -connect example.com:443 -servername example.com`

ile bağlantı açtım.

Diğer terminalde:

`ss -tn`

çalıştırdım.

Gördüğüm connection:

    ESTAB  192.168.64.15:49902  104.20.23.154:443

Buradan:

- Local address → `192.168.64.15`
- Local ephemeral port → `49902`
- Peer IP → `104.20.23.154`
- Peer port → `443`
- TCP state → `ESTAB`

sonuçlarını çıkardım.

Yani o anda TCP connection gerçekten canlıydı.

---

# 🔐 5. TLS

HTTPS kabaca:

    HTTP
      +
     TLS

TLS, TCP connection üzerinde çalışır.

Temel görevleri:

- Şifreleme
- Sunucu kimliğinin sertifikayla doğrulanması
- Veri bütünlüğü

Zincir:

    TCP connection
         ↓
    TLS handshake
         ↓
    HTTP

---

# TCP Çalışırken TLS Neden Patlayabilir?

Çünkü ikisi farklı problemleri çözüyor.

TCP'nin sorusu:

> Bu IP:port ile bağlantı kurabilir miyim?

TLS'in sorusu:

> Bu bağlantı üzerinde güvenli ve doğrulanmış bir oturum kurabilir miyim?

TLS şu sebeplerle başarısız olabilir:

- Sertifika süresi dolmuş
- Sertifika henüz geçerli değil
- Hostname uyuşmuyor
- CA güvenilmiyor
- Certificate chain eksik
- TLS versiyonları uyuşmuyor
- Cipher uyuşmazlığı
- Server yanlış yapılandırılmış
- SNI problemi

Bu yüzden:

`TCP 443 OK`

görüp:

> HTTPS kesin çalışıyor.

demek TIRT.

---

# 🔬 6. `openssl s_client`

TLS katmanını doğrudan gözlemlemek için kullandım.

Temel komut:

`openssl s_client -connect example.com:443`

SNI vermek için:

`openssl s_client -connect example.com:443 -servername example.com`

Buradan görebildiğim şeyler:

- Certificate
- Certificate chain
- TLS protocol
- Cipher
- Handshake
- Verification sonucu

---

# 🧪 LAB 4 — TLS'i Kısa Çıktıyla Kontrol Etmek

Kullandığım:

`openssl s_client -connect example.com:443 -servername example.com -verify_return_error -brief`

Sonuç:

    CONNECTION ESTABLISHED
    Protocol version: TLSv1.3
    Ciphersuite: TLS_AES_256_GCM_SHA384
    Peer certificate: CN=example.com
    Verification: OK

Buradan:

- Connection kuruldu ✅
- TLS → `TLSv1.3`
- Cipher → `TLS_AES_256_GCM_SHA384`
- Sertifika → `CN=example.com`
- Verification → başarılı ✅

sonuçlarını çıkardım.

> [!important]
> `-verify_return_error`, certificate verification başarısızsa bunu gerçek hata gibi ele almak açısından önemli.

---

# 📜 Certificate Verification

`certificate verify failed`

görürsem:

DNS başarılı olabilir.

TCP başarılı olabilir.

Ama:

TLS verification başarısızdır.

Bu durumda gidip DNS'i suçlamak yanlış olur.

---

# 📡 7. HTTP

TLS başarılı olduktan sonra HTTP konuşulmaya başlanabilir.

Örneğin istemci:

    GET / HTTP/1.1
    Host: example.com

gönderebilir.

Sunucu:

    HTTP/1.1 200 OK

gibi bir response döndürebilir.

---

# HTTP Status Kodları

Temel örnekler:

- `200` → başarılı
- `401` → authentication gerekli / başarısız
- `403` → istek anlaşıldı ama izin verilmiyor
- `404` → resource bulunamadı
- `500` → server tarafında hata

En önemli nokta:

> HTTP status code gördüysem HTTP katmanına ulaşmışım demektir.

`404` veya `500` görmek network request'in hiç gerçekleşmediği anlamına gelmez.

Tam tersine bunlar geçerli HTTP response'lardır.

---

# 🔍 8. `curl -v`

Network zincirinin büyük bölümünü tek çıktıda görmek için:

`curl -v https://example.com`

kullanabiliyorum.

Verbose çıktıda:

`*`

→ curl'ün connection/protocol bilgileri

`>`

→ istemciden gönderilen bilgiler

`<`

→ server'dan alınan bilgiler

Örneğin:

    > GET / HTTP/2

request.

    < HTTP/2 200

response.

---

# 🧪 LAB 5 — `curl -v` Çıktısını Katman Katman Okumak

Kullandığım:

`curl -v --connect-timeout 5 https://example.com/ -o /dev/null`

İlk olarak hostname resolve edildi.

IPv6 ve IPv4 adresleri bulundu.

IPv6 bağlantı denemesinde:

    Network is unreachable

çıktı.

Ardından curl IPv4'e geçti:

    Trying 172.66.147.243:443...

Bu bana önemli bir şey gösterdi:

> Bir bağlantı denemesinin başarısız olması bütün request'in başarısız olduğu anlamına gelmez.

Sonra TLS handshake başladı:

    Client hello
    Server hello
    Certificate
    CERT verify
    Finished

Ardından:

    SSL connection using TLSv1.3 / TLS_AES_256_GCM_SHA384

ve:

    SSL certificate verified via OpenSSL.

gördüm.

Sonra HTTP request:

    > GET / HTTP/2
    > Host: example.com
    > User-Agent: curl/8.18.0

Son olarak:

    < HTTP/2 200

geldi.

Yani bu tek trace içerisinde:

    DNS ✅
    TCP ✅
    TLS ✅
    Certificate verification ✅
    HTTP request ✅
    HTTP response ✅

aşamalarını gözlemledim.

---

# 🔐 Güvenlik Notu — `curl -v`

Verbose çıktıyı körlemesine paylaşmamam gerekiyor.

Çünkü içinde:

- Authorization token
- Cookie
- Session bilgisi
- API key
- Credential benzeri bilgiler

bulunabilir.

Gerçek credential bulunan verbose log'u internete yapıştırmak TIRT.

Önce hassas bilgileri temizlemeliyim.

---

# 🐍 9. Python `network_probe.py`

Labın son bölümünde yalnız Python stdlib kullanarak basit HTTPS probe yazdım.

Kullandığım standart modüller:

- `urllib.parse`
- `socket`
- `http.client`
- `ssl`
- `sys`

Ekstra:

`pip install`

veya:

`brew install`

gerekmiyor.

Programın zinciri:

    CLI URL
       ↓
    URL parse
       ↓
    hostname
       ↓
    DNS resolve
       ↓
    IP
       ↓
    HTTPS connection
       ↓
    HTTP GET
       ↓
    HTTP response
       ↓
    status code

---

# URL Parse

Kullandığım:

`urlparse()`

Örneğin:

`https://example.com:8443/test`

parse edilince:

- `scheme` → `https`
- `netloc` → `example.com:8443`
- `hostname` → `example.com`
- `port` → `8443`
- `path` → `/test`

DNS çözümlemesinde ihtiyacım olan:

`hostname`

çünkü DNS'e:

`https://example.com/test`

vermem.

Sadece:

`example.com`

veririm.

---

# `hostname` Neden `str | None`?

VS Code:

`sonuc.hostname`

için `str | None` gösterebilir.

Çünkü parse edilen her input'un hostname içermesi garanti değildir.

Bu yüzden doğrudan:

`socket.gethostbyname(sonuc.hostname)`

demeden önce:

`sonuc.hostname is None`

durumunu kontrol ettim.

Önemli ayrım:

    hostname yok
    → URL/input problemi

    hostname var ama çözülemiyor
    → name resolution problemi

---

# DNS Resolve

Kullandığım:

`socket.gethostbyname(hostname)`

Mantık:

    example.com
         ↓
    gethostbyname()
         ↓
    IPv4 adresi

Bu fonksiyonla yaptığım lab özelinde IPv4 resolve ediyorum.

---

# DNS Failure

Gerçek failure testi için:

`this-host-should-not-exist.invalid`

kullandım.

Aldığım hata:

    socket.gaierror

Bunu ayrı yakaladım.

Program çıktısı:

    Hata meydana geldi: [Errno 8] nodename nor servname provided, or not known

Sonra:

`echo $?`

çıktısı:

    47

Böylece:

- Traceback kullanıcıya saçılmadı
- Hata stderr'e gitti
- Program başarısızlığı non-zero exit ile bildirdi

---

# 😂 `exapmle.com` Neden Patlamadı?

Yanlışlıkla:

`exapmle.com`

ile DNS failure test etmeye çalıştım.

Ama çıktı:

    host=exapmle.com
    resolved_ip=103.224.182.243
    status=200

oldu.

Buradaki ders:

> Benim domain'i yanlış yazmış olmam, o domain'in gerçekten var olmadığı anlamına gelmez.

DNS:

> "Sen example.com mu demek istedin?"

diye düşünmez.

Sadece:

> "`exapmle.com` için kayıt var mı?"

diye bakar.

Bu yüzden deterministic DNS failure testi için `.invalid` kullandım.

---

# HTTP / HTTPS Request

Kullandığım:

`http.client`

Akış:

    connection oluştur
        ↓
    request gönder
        ↓
    response al
        ↓
    response.status

Önemli:

Status connection'ın değil response'un özelliğidir.

Yanlış düşünce:

`connection.status`

Doğru:

    response = connection.getresponse()
    status = response.status

---

# 🚨 En Kritik Kod Hatam — `HTTPConnection`

Bir aşamada:

`http.client.HTTPConnection`

kullanmışım.

Ama görev HTTPS.

Bu yüzden doğrusu:

`http.client.HTTPSConnection`

Çünkü:

    HTTPConnection
    → düz HTTP

    HTTPSConnection
    → HTTP + TLS

`HTTPConnection` kullanıp ardından:

`ssl.SSLError`

beklemek mantıksızdı çünkü TLS katmanını kullanmıyordum.

Bu labdaki en önemli kod düzeltmelerimden biri buydu.

---

# Timeout

Connection oluştururken:

`timeout=5`

kullandım.

Amaç:

> Server cevap vermiyorsa sonsuza kadar beklememek.

Timeout durumunu:

`TimeoutError`

ile ayrı ele aldım.

---

# Connection Failure

Başta:

`ConnectionError`

kullandım.

Bu bazı bağlantı problemlerini kapsıyor.

Notumda ayrıca daha geniş network/OS hataları için:

`OSError`

gibi daha genel bir sınırın düşünülebileceğini öğrendim.

Buradaki önemli exception prensibi:

> **Özel exception önce, genel exception sonra.**

---

# Neden `except Exception:` Kullanmadım?

Çünkü:

    except Exception:
        ...

yazarsam bana yalnızca:

> Bir şey patladı.

der.

Ama bu labda öğrenmek istediğim:

- DNS mi?
- TCP mi?
- Timeout mı?
- TLS mi?
- HTTP response mu?

ayrımı.

Yani exception'ları katmanlara göre ayırmak troubleshooting açısından çok daha değerli.

---

# Path Problemi

URL:

`https://example.com/`

ise path `/`.

Ama:

`https://example.com`

gibi bir URL'de parsed path boş olabilir.

Bu yüzden:

`path = sonuc.path or "/"`

kullandım.

Yani:

    path varsa
    → onu kullan

    path boşsa
    → "/"

---

# CLI Argümanı

Başta URL'yi hardcoded kullanıyordum.

Sonra programı:

`python network_probe.py https://example.com/`

şeklinde çalıştırmak için `sys.argv` kullandım.

Mantık:

- `sys.argv[0]` → script adı
- `sys.argv[1]` → URL

Ama kullanıcı argüman vermezse `sys.argv[1]` patlayacağı için önce:

`len(sys.argv)`

kontrolü yaptım.

---

# stdout ve stderr

Başarılı normal çıktı:

    host=...
    resolved_ip=...
    status=...

→ `stdout`

Hata/diagnostic:

    DNS failure
    TLS failure
    Timeout
    Connection failure

→ `stderr`

Bu ayrım özellikle shell pipeline'larında ve programlar birbirleriyle konuşurken önemli.

---

# Exit Code

Başarılı execution:

    0

Hata:

    non-zero

Labda kullandıklarım:

- DNS → `47`
- TLS → `74`
- Timeout → `75`
- Connection → `76`

Buradaki asıl fikir numaraların kendisinden çok:

> Başarısız durumda `0` dönmemek.

Kontrol:

`echo $?`

---

# 🧱 Failure Boundary Modelim

## DNS Failure

    URL parse ✅
    hostname ✅
    DNS ❌
    TCP başlamadı
    TLS başlamadı
    HTTP başlamadı

## TCP / Connection Failure

    URL parse ✅
    hostname ✅
    DNS ✅
    TCP ❌
    TLS başlamadı
    HTTP başlamadı

## TLS Failure

    URL parse ✅
    hostname ✅
    DNS ✅
    TCP ✅
    TLS ❌
    HTTP request normal akışta başlamayabilir

## HTTP 404

    URL parse ✅
    hostname ✅
    DNS ✅
    TCP ✅
    TLS ✅
    HTTP ✅
    status=404

`404` burada failure boundary'nin HTTP/application tarafında olduğunu gösteriyor; network exception değildir.

---

# 🐞 Bugün Yaptığım Hatalar

## 1. `getent = DNS` sanmak

TIRT.

`getent` sistemin normal name resolution mekanizmasını kullanır.

---

## 2. DNS çalışıyorsa connection da çalışır sanmak

TIRT.

DNS sadece hostname çözümlemesidir.

---

## 3. TCP 443 başarılıysa HTTPS tamamen çalışıyor sanmak

TIRT.

TLS hâlâ başarısız olabilir.

---

## 4. TLS başarılıysa application da çalışıyor sanmak

TIRT.

HTTP/application hâlâ `404`, `500`, `503` vb. döndürebilir.

---

## 5. Problemi tek parça görmek

Yanlış düşünce:

> Network bozuk.

Doğru düşünce:

> İlk başarısız katman hangisi?

---

## 6. `stdlib` kavramını bilmemek

Başta ekstra package gerekiyor sandım.

Ama kullanılan modüller Python Standard Library içerisindeydi.

---

## 7. `hostname` değerini direkt kullanmak

`sonuc.hostname` teknik olarak `None` olabilir.

Önce input state'ini kontrol etmem gerekiyor.

---

## 8. Hostname yok ile DNS failure'ı karıştırmak

Bunlar aynı şey değil.

    hostname yok
    → parse/input problemi

    hostname var ama resolve olmuyor
    → name resolution problemi

---

## 9. `exapmle.com` ile DNS failure test etmek

Yanlış yazılmış domain gerçekten var olabilir.

Deterministic failure testi için `.invalid` kullandım.

---

## 10. `.status`u connection üzerinde aramak

Status:

`response.status`

üzerindedir.

---

## 11. HTTPS görevinde `HTTPConnection` kullanmak

Günün en kritik kod hatalarından biri.

Doğrusu:

`HTTPSConnection`

---

# 🧠 Troubleshooting Sıram

Artık bir servis çalışmadığında şu sırayla gideceğim:

## 1. Local Interface / IP

Makinenin doğru IP'si var mı?

`ip address`

## 2. Routing

Kernel doğru yolu seçiyor mu?

`ip route`

`ip route get HEDEF`

## 3. Name Resolution

Hostname çözülebiliyor mu?

`getent hosts HOSTNAME`

## 4. TCP

Hedef IP:port connection kuruluyor mu?

## 5. TLS

Handshake ve certificate verification başarılı mı?

`openssl s_client`

## 6. HTTP

Request gerçekten gönderildi mi?

Hangi status geldi?

`curl -v`

---

# 🧠 Kafaya Kazı

> [!quote]
> DNS success sadece isim çözümlemesini kanıtlar.

> [!quote]
> IP adresini bilmek route'u bildiğim anlamına gelmez.

> [!quote]
> TCP success sadece IP:port connection'ın kurulduğunu kanıtlar.

> [!quote]
> TCP 443 success, TLS success demek değildir.

> [!quote]
> TLS success, application success demek değildir.

> [!quote]
> HTTP 404 ve 500 network exception değildir; HTTP response'dur.

> [!quote]
> `getent` yalnız DNS değildir, sistem name resolution mekanizmasını kullanır.

> [!quote]
> Status connection'ın değil response'un özelliğidir.

> [!quote]
> HTTPS kullanıyorsam `HTTPSConnection` ile TLS katmanını gerçekten devreye sokmalıyım.

> [!quote]
> Hata mesajından önce hangi katmana kadar ulaştığımı kanıtlamalıyım.

---

# 📌 30 Saniyelik Özet

    URL
     ↓
    hostname
     ↓
    name resolution
     ↓
    IP
     ↓
    routing
     ↓
    TCP
     ↓
    TLS
     ↓
    HTTP
     ↓
    application


    ip addr
    → Ben ağda kimim?

    ip route
    → Hangi yollar mevcut?

    ip route get HEDEF
    → Kernel bu hedef için hangi yolu seçer?

    getent
    → Sistem name resolution

    ss -tn
    → TCP connection state

    openssl s_client
    → TLS / certificate / cipher / verification

    curl -v
    → DNS + connection + TLS + HTTP trace


    socket.gethostbyname()
    → hostname → IPv4

    socket.gaierror
    → name resolution failure

    HTTPSConnection
    → HTTPS / TLS connection

    response.status
    → HTTP status

    stderr
    → diagnostic

    non-zero exit
    → program başarısız

---

# ✅ Günün Kazanımları

- [x] IP ve CIDR mantığı tekrarlandı
- [x] Interface ve source IP gözlemlendi
- [x] Default gateway bulundu
- [x] `ip route` ile routing table okundu
- [x] `ip route get` ile kernel route seçimi gözlemlendi
- [x] IP ve route'un farklı state'ler olduğu anlaşıldı
- [x] DNS ile name resolution ayrımı netleşti
- [x] `getent` ve NSS mantığı öğrenildi
- [x] DNS success'in TCP success olmadığı anlaşıldı
- [x] TCP 3-way handshake tekrarlandı
- [x] TCP connection `ss` ile bağımsız doğrulandı
- [x] Local/peer address ve portlar okundu
- [x] `ESTAB` state'i gözlemlendi
- [x] TCP ile TLS sınırı netleşti
- [x] `openssl s_client` kullanıldı
- [x] SNI'nin `-servername` ile verilebildiği görüldü
- [x] TLSv1.3 ve cipher gözlemlendi
- [x] Certificate verification bağımsız kontrol edildi
- [x] `curl -v` çıktısı katmanlara ayrılarak okundu
- [x] IPv6 failure sonrası IPv4 fallback gözlemlendi
- [x] HTTP/2 GET request gözlemlendi
- [x] HTTP `200` response gözlemlendi
- [x] `404` ve `500`ün network exception olmadığı anlaşıldı
- [x] Python stdlib ile network probe yazıldı
- [x] `urlparse()` kullanıldı
- [x] `hostname`, `netloc`, `path` farkı öğrenildi
- [x] `hostname is None` kontrolü öğrenildi
- [x] `socket.gaierror` ayrı failure olarak ele alındı
- [x] `.invalid` ile deterministic DNS failure testi yapıldı
- [x] `HTTPConnection` / `HTTPSConnection` farkı öğrenildi
- [x] `response.status` mantığı oturdu
- [x] Timeout ve connection failure ayrıldı
- [x] stdout / stderr ayrımı kullanıldı
- [x] Non-zero exit code ile failure bildirildi
- [x] Network troubleshooting katman bazlı düşünülmeye başlandı

---

# 🚀 Gün Sonu Sonucu

Bugün öğrendiğim en önemli şey tek tek komutlardan çok **failure boundary** mantığı oldu.

Artık:

> "Network çalışmıyor."

demek yerine şunu soracağım:

    URL doğru mu?
       ↓
    Hostname var mı?
       ↓
    Name resolution çalıştı mı?
       ↓
    Route var mı?
       ↓
    TCP connection kuruldu mu?
       ↓
    TLS handshake geçti mi?
       ↓
    Certificate verification geçti mi?
       ↓
    HTTP request gönderildi mi?
       ↓
    Hangi status geldi?

Günün en kritik cümlesi:

> **Bir katmanı suçlamadan önce o katmana gerçekten ulaşıp ulaşmadığımı kanıtlamam gerekiyor.**