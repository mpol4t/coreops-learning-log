---
title: "Gün 35 — TLS Foundation, Docker Port Publishing ve HTTP Client"
tags:
  - coreops
  - day35
  - tls
  - ssl
  - tcp
  - certificate
  - docker
  - pid1
  - volume
  - bind-mount
  - port-publishing
  - http
  - python
aliases:
  - "Gün 35 TLS Foundation Docker Port Publishing HTTP Client"
status: completed
---

# 🧠 Gün 35 — TLS Foundation + Docker Port Publishing + HTTP Client

> [!abstract] 🎯 Günün ana fikri
> Bugün iki büyük katmanı birbirine bağladım:
>
> **35A:** TCP bağlantısının üzerine TLS güvenliği ve server identity verification eklemek.
>
> **35B:** Bir container içindeki HTTP servisini host'a publish edip Python client ile gerçekten request/response zincirini gözlemlemek.
>
> Büyük resim:
>
>     DNS
>      ↓
>     TCP
>      ↓
>     TLS
>      ↓
>     HTTP
>      ↓
>     Application
>
> Her katmanın başarılı olması yalnızca kendi katmanını kanıtlıyor.

---

# 🔐 35A — TLS Foundation

## Ana Hedef

Bugünkü sınırım:

    DNS
     ↓
    TCP Connection
     ↓
    TLS Handshake
     ↓
    Certificate Verification
     ↓
    Verified TLS Socket

HTTP henüz bu bölümün konusu değil.

En önemli öğrendiğim şey:

> **TCP bağlantısının başarılı olması, karşımdaki server'ın gerçekten istediğim server olduğunu kanıtlamaz.**

TCP yalnızca transport bağlantısını kurar.

TLS bunun üzerine:

- confidentiality
- integrity
- authentication

ekler.

---

# 🚚 TCP'nin Görevi

TCP'nin sorusu:

> Bu IP:port endpoint'i ile bağlantı kurabiliyor muyum?

Örneğin:

    www.python.org:443

TCP başarılıysa:

> İlgili endpoint connection'ımı kabul etti.

diyebilirim.

Ama henüz şunları kanıtlamadım:

- Gerçekten `www.python.org` mu?
- Certificate güvenilir mi?
- Certificate doğru hostname'e mi ait?
- Trafik şifreli mi?
- Server identity doğrulandı mı?

Kısaca:

    TCP = taşıma bağlantısı

    TLS = güvenli + doğrulanmış iletişim

---

# 🧱 TLS Neden TCP'den Sonra Geliyor?

TLS handshake mesajlarının da bir taşıma kanalına ihtiyacı var.

Bu yüzden:

    TCP connection
         ↓
    connected TCP socket
         ↓
    TLS handshake
         ↓
    TLS socket

TLS handshake sırasında gönderilen veriler TCP üzerinden taşınır.

> [!important]
> `wrap_socket()` yeni bir TCP connection açmaz.
>
> Mevcut TCP connection'ı kullanır.

Katman modeli:

    Application
        ↓
       TLS
        ↓
       TCP
        ↓
        IP

---

# 🛡️ TLS Bize Ne Kazandırıyor?

## Confidentiality

Trafiğin başkaları tarafından okunmasını engellemeye çalışır.

## Integrity

Verinin yolda değiştirilip değiştirilmediğini tespit etmeyi sağlar.

## Authentication

Konuştuğum server'ın gerçekten konuşmak istediğim server olup olmadığını doğrulamaya çalışır.

Sadece:

> Bağlantı şifreli.

demek yeterli değil.

Asıl istediğim:

> **Şifreli + kimliği doğrulanmış bağlantı.**

Çünkü yanlış kişiyle şifreli konuşmak hâlâ yanlış kişiyle konuşmaktır.

---

# 🤝 TLS 1.3 Handshake Mental Modeli

Basitleştirilmiş akış:

    CLIENT                         SERVER

    ClientHello  -------------------->

                 <-------------- ServerHello
                 <-------------- Certificate
                 <-------------- CertificateVerify
                 <-------------- Finished

    Finished     -------------------->

    Sonrasında encrypted application data

ClientHello içerisinde client kabaca:

- Desteklediği TLS sürümleri
- Crypto seçenekleri
- Key exchange bilgileri
- SNI hostname

gibi bilgileri gönderebilir.

---

# 📜 Certificate Neden Var?

Client'ın problemi:

> Bir server cevap verdi ama sen gerçekten kimsin?

Server certificate göndererek kimliğini kanıtlamaya çalışır.

Basit chain:

    www.python.org certificate
              ↓
       Intermediate CA
              ↓
        Trusted Root CA

Root CA çoğunlukla server tarafından gönderilmez.

Çünkü client'ın işletim sistemindeki trusted certificate store içerisinde bulunabilir.

---

# 🔍 Certificate Verification

Kabaca şu kontroller yapılır:

1. Certificate chain güvenilir mi?
2. İmzalar geçerli mi?
3. Certificate zaman açısından geçerli mi?
4. Certificate istediğim hostname için mi?
5. Certificate kullanım amacı uygun mu?

Önemli ayrım:

    Certificate trust
    ≠
    Hostname verification

Certificate güvenilir bir CA tarafından imzalanmış olabilir.

Ama certificate:

    example.com

içinse ve ben:

    python.org

istiyorsam yine kabul etmemeliyim.

Mental model:

    certificate trust
           +
    hostname verification
           ↓
    server identity verification

---

# ⚙️ `ssl.create_default_context()`

Bugünkü en önemli kafa karışıklıklarımdan biri buradaydı.

Kod:

`context = ssl.create_default_context()`

Başta kafamda:

    context = TCP connection

gibi bir düşünce oluşmuştu.

TIRT.

Doğrusu:

    SSLContext
    =
    TLS policy / configuration

`create_default_context()` herhangi bir server'a bağlanmaz.

Sadece TLS için güvenli varsayılan ayarları hazırlar.

Mental model:

    context
      ├── hangi CA'lara güveniyorum?
      ├── certificate verification nasıl olacak?
      ├── hostname kontrolü nasıl olacak?
      ├── hangi TLS sürümleri kullanılabilir?
      └── diğer TLS güvenlik ayarları

Yani:

> **SSLContext bağlantı değil, bağlantıya uygulanacak kurallar kümesidir.**

---

# 🔌 TCP Socket vs SSLContext

Artık net ayrımım:

    tcp_sock
    =
    gerçek TCP connection

    context
    =
    TLS güvenlik kuralları

Sonra:

    TCP socket
        +
    SSLContext
        ↓
    wrap_socket()
        ↓
    TLS handshake
        ↓
    SSLSocket

---

# 🎁 `wrap_socket()` Ne Yapıyor?

Mantık:

`context.wrap_socket(tcp_sock, server_hostname=host)`

Burada:

`context`

→ TLS kurallarım

`tcp_sock`

→ mevcut TCP connection

`server_hostname`

→ TLS tarafında beklediğim server identity

Başarılı akış:

    Plain TCP socket
          ↓
    wrap_socket()
          ↓
    TLS handshake
          ↓
    Certificate verification
          ↓
    Hostname verification
          ↓
    Verified TLS socket

Teknik olarak kendime kurduğum doğru cümle:

> `SSLContext.wrap_socket()`, mevcut TCP socket üzerinde TLS kullanmamı sağlar ve handshake başarılı olduğunda TLS üzerinden güvenli communication sağlayan bir socket elde ederim.

---

# 🧠 `create_default_context()` vs `wrap_socket()`

`create_default_context()`

→ Kuralları hazırla.

`wrap_socket()`

→ Bu kuralları mevcut connection üzerinde kullanarak TLS'e geç.

Kısaca:

    SSLContext = kurallar

    TCP Socket = bağlantı

    SSLSocket = TLS uygulanmış bağlantı

---

# 🪪 `server_hostname` Neden Önemli?

Python'da:

`server_hostname=host`

TLS tarafında önemlidir.

İki kavramla ilişkilidir:

1. SNI
2. Hostname verification

Ama:

> **SNI ≠ Hostname Verification**

---

# 📣 SNI — Server Name Indication

Bir IP'nin arkasında birden fazla hostname olabilir.

Örneğin:

    203.0.113.10
         ├── site-a.com
         ├── site-b.com
         ├── site-c.com
         └── site-d.com

TCP endpoint hepsi için aynı olabilir:

    203.0.113.10:443

Client TLS ClientHello sırasında:

    SNI = site-c.com

gönderebilir.

Bunun anlamı kabaca:

> Ben bu hostname için geldim.

Server buna göre doğru TLS configuration/certificate seçebilir.

---

# ✅ Hostname Verification

Client certificate'i aldıktan sonra kendi tarafında şunu sorar:

> Bu certificate gerçekten istediğim hostname için mi?

Örneğin:

`server_hostname="www.python.org"`

ise certificate içerisindeki hostname bilgileriyle karşılaştırma yapılabilir.

Modern certificate'lerde bu bilgi çoğunlukla SAN alanındadır:

    Subject Alternative Name

Örnek:

    DNS:www.python.org
    DNS:python.org

---

# 🆚 SNI vs Hostname Verification

## SNI

Yön:

    Client → Server

Anlam:

> Hangi hostname için geldiğimi söylüyorum.

## Hostname Verification

Client tarafında yapılır.

Anlam:

> Bana gelen certificate gerçekten istediğim hostname'e ait mi?

Aynı hostname kullanılabilir.

Ama görevleri farklıdır.

---

# 🌐 TCP Destination ≠ TLS Server Identity

TCP tarafında:

    IP + Port

önemlidir.

TLS tarafında:

    Hostname / service identity

doğrulanabilir.

Örneğin:

    TCP destination:
    192.0.2.25:443

Ama TLS identity:

    www.python.org

olabilir.

Bir IP'nin arkasında birden fazla hostname bulunabilir.

Bu yüzden:

> **Adres ile kimlik aynı şey değildir.**

TCP:

> Paketleri nereye göndereceğim?

TLS:

> Gerçekte kiminle konuştuğumu nasıl doğrulayacağım?

---

# 💥 TCP OK, TLS FAIL Olabilir

Kesinlikle olabilir.

Örneğin:

    TCP Connect
         ↓
        OK

    TLS Handshake
         ↓
    Certificate geldi
         ↓
    Hostname verification
         ↓
        FAIL

Sonuç:

    TCP = OK
    TLS = FAIL

Çünkü TCP yalnızca taşıma connection'ının kurulabildiğini kanıtlar.

---

# ❌ Yanlış `server_hostname`

TCP ile doğru endpoint'e bağlanmış olabilirim.

Ama TLS sırasında:

`server_hostname="yanlis.example"`

verirsem certificate bu kimliğe göre değerlendirilebilir.

Certificate farklı hostname'e aitse:

`ssl.SSLCertVerificationError`

gibi bir hata görebilirim.

Labda bunu gerçekten gördüm:

    TCP: OK

ama:

    CERTIFICATE_VERIFY_FAILED
    Hostname mismatch

aldım.

Bu bana katmanların bağımsızlığını direkt gösterdi.

---

# ⚠️ Yanlış Hostname Her Zaman Aynı Şekilde Fail Olmaz

Burada önemli nüans var.

Aynı IP'nin arkasında:

    a.com
    b.com

bulunabilir.

Ben `server_hostname="b.com"` gönderirsem server bana `b.com` için geçerli bir certificate sunabilir.

TLS başarılı olabilir.

Ama bu durumda ben:

    a.com

kimliğini doğrulamış olmam.

Doğru kural:

> TLS tarafında belirttiğim server identity neyse doğrulama ona göre gerçekleşir.

---

# 🚨 TLS Failure = Certificate Hatası Demek Değildir

TLS şu sebeplerle başarısız olabilir:

- Certificate chain problemi
- Hostname mismatch
- Expired certificate
- TLS version uyuşmazlığı
- Protocol problemi
- Handshake failure
- Cipher/crypto uyuşmazlığı

Bu yüzden:

> TLS patladı → hostname yanlış.

demek TIRT.

Exception'ı incelemeliyim.

---

# 🧪 35A Python Lab

Program akışı:

    URL
     ↓
    urlparse()
     ↓
    host + port
     ↓
    getaddrinfo()
     ↓
    TCP connection
     ↓
    getpeername()
     ↓
    SSLContext oluştur
     ↓
    wrap_socket()
     ↓
    TLS handshake
     ↓
    TLS OK / FAIL

Normal test:

    Host: www.python.org
    Port: 443
    Peer ip: 151.101.128.223
    TCP: OK
    TLS: OK

Exit:

    0

---

# 🧪 Controlled TLS Failure

TCP yine başarılı:

    TCP: OK

Ama yanlış TLS server identity kullandığım testte:

    CERTIFICATE_VERIFY_FAILED
    Hostname mismatch

aldım.

Bunun anlamı:

    TCP ✅
    TLS verification ❌

---

# 🧪 TCP Daha Kurulmadan Failure

Test:

`https://127.0.0.1:65432/`

Sonuç:

    Connection refused

Burada:

    TCP ❌
    TLS = NOT STARTED

Yani TLS'i suçlayamam çünkü o katmana ulaşmadım.

---

# 🔬 OpenSSL ile İkinci Kanıt

Python'daki TLS sonucunu bağımsız araçla doğrulamak için:

`openssl s_client`

kullandım.

Temel seçenekler:

## `-connect`

TCP endpoint.

Örnek:

`-connect www.example.com:443`

Soru:

> Nereye TCP bağlantısı kuracağım?

## `-servername`

SNI.

Örnek:

`-servername www.example.com`

Soru:

> Server'a hangi hostname için geldiğimi söyleyeceğim?

## `-verify_hostname`

Certificate hostname verification.

Soru:

> Certificate gerçekten bu hostname için geçerli mi?

## `-verify_return_error`

Verification hatasını fatal hata olarak değerlendir.

---

# 🧠 OpenSSL Ayrımı

    -connect
    =
    TCP endpoint

    -servername
    =
    TLS SNI

    -verify_hostname
    =
    Certificate hostname verification

    -verify_return_error
    =
    Verification failure'ı fatal yap

Bunlar aynı şey değil.

---

# 🧪 OpenSSL Sonucum

Gözlem:

    CONNECTION ESTABLISHED
    Protocol version: TLSv1.3
    Ciphersuite: TLS_AES_256_GCM_SHA384
    Peer certificate: CN=example.com
    Verification: OK

Burada:

    TCP ✅
    TLS handshake ✅
    Certificate verification ✅

kanıtladım.

---

# 🧪 Temiz Test Prensibi

Debugging sırasında aynı anda birden fazla değişkeni değiştirmemeliyim.

Örneğin sadece hostname verification test ediyorsam:

    TCP endpoint = aynı
    SNI = aynı
    verification hostname = değiştir

gibi küçük bir experiment daha güçlü kanıt üretir.

> [!important]
> **Bir deneyde mümkün olduğunca tek değişken değiştir.**

---

# 🐞 35A Hata Avı

## `context` TCP bağlantısıdır

TIRT.

`context` TLS configuration/policy'dir.

---

## `wrap_socket()` yeni TCP connection açar

TIRT.

Mevcut TCP socket'i kullanır.

---

## TCP 443 başarılıysa TLS de başarılıdır

TIRT.

---

## Trusted certificate varsa hostname kesin doğrudur

TIRT.

Trust ile hostname verification farklı kontrollerdir.

---

## SNI = hostname verification

TIRT.

---

## TCP destination = server identity

TIRT.

---

## TLS failure her zaman certificate mismatch'tir

TIRT.

---

# 🧠 35A Kafaya Kazı

> `SSLContext` ≠ TCP socket

> TCP connection ≠ TLS connection

> TCP destination ≠ TLS server identity

> SNI ≠ hostname verification

> Trusted certificate ≠ doğru hostname certificate'i

> TCP success ≠ TLS success

> TLS success ≠ HTTP success

> `create_default_context()` ≠ bağlantı kurmak

> `wrap_socket()` ≠ yeni TCP connection açmak

> `-servername` ≠ hostname verification

---

# 🐳 35B — Docker Retrieval

## PID 1 ve `docker stop`

Container içinde ana uygulamamın doğrudan PID 1 olması önemli.

Exec form:

`CMD ["python", "day25.py"]`

Shell form:

`CMD python day25.py`

shell form kullanıldığında araya `/bin/sh -c` girebilir.

Bu durumda PID 1 gerçek uygulamam yerine shell olabilir.

Signal davranışı karışabilir.

---

# PID 1 Testi

Container process'lerini kontrol ettiğimde:

    PID  PPID  COMMAND
    1    0     python day25.py

gördüm.

Yani uygulamam gerçekten PID 1.

---

# `docker stop` Akışı

Kabaca:

    docker stop
         ↓
    PID 1'e SIGTERM
         ↓
    graceful shutdown için süre
         ↓
    kapanmazsa SIGKILL

Lab sonucum:

    status=exited
    exit=0

Bu temiz kapanışı gösterdi.

---

# 🗄️ Writable Layer

Container oluşturulduğunda image'ın read-only katmanlarının üstüne container'a özel writable layer gelir.

Normal yazılan dosyalar burada tutulabilir.

Önemli:

    docker stop
    → container durur ama hâlâ vardır
    → writable layer kalır

    docker rm
    → container silinir
    → writable layer gider

Mental model:

    Image = read-only template

    Container =
    Image
      +
    writable layer

---

# 📁 Bind Mount

Bind mount:

> Host'ta benim seçtiğim gerçek path'i container'a bağla.

Örneğin:

    Host:
    /tmp/coreops-bind

           ↕

    Container:
    /data

Container içinde:

    /data/marker.txt

oluşturmak host tarafında:

    /tmp/coreops-bind/marker.txt

oluşturabilir.

Container silinse de host dosyası kalabilir.

---

# 📦 Named Volume

Named volume:

> Storage alanını Docker oluştursun ve yönetsin.

Örneğin:

`docker volume create coreops35-data`

Container A volume'a veri yazdı.

Container A silindi.

Volume kaldı.

Container B aynı volume'u mount ettiğinde eski dosyayı gördü.

Yani:

> **Container lifecycle ≠ Volume lifecycle**

---

# 🆚 Writable Layer / Bind / Named Volume

## Writable Layer

    Container'a özel
    docker rm → gider

## Bind Mount

    Host path
    Path'i ben seçerim
    Container silinse bile veri kalabilir

## Named Volume

    Docker-managed storage
    Docker yönetir
    Container silinse bile volume kalabilir

Yanlış ezber:

    Bind = geçici
    Volume = kalıcı

TIRT.

Bind de kalıcı veri tutabilir.

Asıl fark ownership / management modelidir.

---

# 🌐 35B — Docker Port Publishing

İkinci büyük konu:

> Container içindeki HTTP servisine host'tan nasıl ulaşırım?

Ana zincir:

    Python Client / curl
           ↓
    Host IP:Host Port
           ↓
    Docker Port Publishing
           ↓
    Container Port
           ↓
    HTTP Server

---

# 🚪 `-p HOST_PORT:CONTAINER_PORT`

Örnek:

`-p 18080:8000`

Anlam:

    Host:18080
         ↓
    Container:8000

En kısa ezber:

    DIŞARI : İÇERİ

    HOST : CONTAINER

Yani container:

    18080

portunda çalışmıyor.

Container servisi hâlâ:

    8000

portunda.

`18080` host tarafındaki giriş kapısı.

---

# 🎯 Host ve Container Port Aynı Olmak Zorunda Değil

Container app:

    8000

portunda çalışırken:

    -p 8000:8000

veya:

    -p 18080:8000

veya:

    -p 5000:8000

yapabilirim.

Container açısından uygulama yine:

    :8000

dinliyor.

Sadece host giriş portu değişiyor.

---

# 🏠 `127.0.0.1:18080:8000`

Tam syntax:

`HOST_IP:HOST_PORT:CONTAINER_PORT`

Örneğim:

`-p 127.0.0.1:18080:8000`

Parçalarsam:

    127.0.0.1
    → host IP / loopback

    18080
    → host port

    8000
    → container port

Akış:

    127.0.0.1:18080
             ↓
           Docker
             ↓
      Container:8000

---

# 🔐 Neden `127.0.0.1`?

`127.0.0.1` loopback.

Yani host'un kendisi.

Bu yüzden servis host üzerinde yalnızca local erişim için publish edilmiş oluyor.

Host'tan:

`http://127.0.0.1:18080`

ile erişebilirim.

---

# 🌍 IP Yazmazsam

Örneğin:

`-p 18080:8000`

Docker bunu uygun host interface'lerinde publish edebilir.

`docker ps` içerisinde örneğin:

    0.0.0.0:18080->8000/tcp

görülebilir.

Burada:

`0.0.0.0`

kabaca tüm IPv4 interface'lerinde dinleme anlamına gelir.

Dolayısıyla:

    127.0.0.1:18080
    ≠
    0.0.0.0:18080

---

# 🆚 `EXPOSE` vs `-p`

Dockerfile:

`EXPOSE 8000`

tek başına host'a gerçek port publishing yapmaz.

Kabaca:

> Bu image/container'daki uygulama bu portu kullanmayı bekliyor.

bilgisidir.

Gerçek mapping:

`-p`

ile oluşturulur.

Mental model:

    EXPOSE
    → metadata / intended container port

    -p
    → host-container port publishing

---

# 🔎 Mapping'i Kanıtlamak

Container çalışırken:

`docker ps`

çıktısı:

    127.0.0.1:18080->8000/tcp

gösterdi.

Ayrıca:

`docker port coreops-http`

sonucu:

    8000/tcp -> 127.0.0.1:18080

Buradan mapping'i ikinci kez doğruladım.

---

# 🌐 HTTP Server Lab

Host klasöründe:

`index.html`

oluşturdum.

İçerik:

`<h1>coreops-35b</h1>`

Container'ı şu mantıkla başlattım:

    docker run
      ↓
    host klasörünü /site'a bind mount et
      ↓
    host 18080 → container 8000 publish et
      ↓
    python http.server başlat
      ↓
    /site klasörünü servis et

---

# 📁 Bind Mount

Kullandığım:

`-v "$PWD":/site:ro`

Anlam:

    Host current directory
             ↓
         bind mount
             ↓
    Container /site

`:ro`

→ read-only

Örneğin:

    Host:
    http-target/index.html

Container'da:

    /site/index.html

olarak görülüyor.

---

# `--directory /site`

Bu Docker parametresi değil.

`python -m http.server`

parametresi.

Anlamı:

> `/site` klasöründeki dosyaları HTTP üzerinden yayınla.

Önemli ayrım:

    -v "$PWD":/site:ro
    → Dosyayı container'a görünür yap

    --directory /site
    → HTTP server hangi klasörü servis etsin?

---

# `-w` ile Farkı

Docker:

`-w /site`

→ Process'in current working directory'sini belirler.

Python:

`--directory /site`

→ HTTP server'ın document root'unu belirler.

Aynı sonucu bazı durumlarda üretebilirler.

Ama aynı kavram değiller.

Kısa:

    -w
    → Process nerede çalışıyor?

    --directory
    → HTTP server neyi yayınlıyor?

---

# 🌐 `--bind 0.0.0.0`

Bu da Docker değil, Python `http.server` parametresi.

Anlam:

> Container içindeki tüm uygun interface'lerden gelen connection'ları kabul et.

Container server:

    0.0.0.0:8000

dinliyor.

---

# 🤯 `127.0.0.1` ve `0.0.0.0` Neden Çelişmiyor?

Çünkü farklı network taraflarını ifade ediyorlar.

Host:

`-p 127.0.0.1:18080:8000`

→ Host yalnız loopback üzerinden publish ediyor.

Container:

`--bind 0.0.0.0`

→ Container içindeki server tüm container interface'lerinde dinliyor.

Tam akış:

    Host
    127.0.0.1:18080
           ↓
    Docker Port Mapping
           ↓
    Container interface:8000
           ↓
    Python Server
    0.0.0.0:8000

Çelişki yok.

Biri host tarafı.

Diğeri container tarafı.

---

# ✅ HTTP İsteğiyle Kanıt

Kullandığım:

`curl -i http://127.0.0.1:18080/`

Sonuç:

    HTTP/1.0 200 OK

ve body:

    <h1>coreops-35b</h1>

Bu tek test ile zincirin birçok bölümünü kanıtladım:

- Bind mount çalışıyor
- `index.html` container tarafından görülüyor
- HTTP server çalışıyor
- Container çalışıyor
- Container 8000 dinliyor
- Docker port publishing çalışıyor
- Host 18080 üzerinden servise erişiyorum
- HTTP response geri geliyor

---

# 🧪 Mikro Alıştırma

Host'ta:

`hello.txt`

oluşturdum.

Container:

`docker exec coreops-http ls /site`

çıktısında:

    hello.txt
    index.html

gördüm.

Sonra:

`curl http://127.0.0.1:18080/hello.txt`

sonucu:

    hello-from-container

Bu bind mount + server document root + port mapping zincirini tekrar doğruladı.

---

# 🐞 `docker port` Hatasında Yaptığım Yanlış Teşhis

İlk olarak:

`docker port coreops-http`

çalışmadığında:

    No such container

aldım.

İlk düşüncem:

> `docker port`ta sorun var.

Ama gerçek problem daha önceydi.

Container kapanmıştı.

Üstelik:

`--rm`

kullandığım için container kapanınca otomatik silinmişti.

Doğru çıkarım:

> `docker port` problemi yaratmadı; daha önce oluşmuş container lifecycle problemini görünür hale getirdi.

---

# 🕵️ Debug Sırasında `--rm -d`

İlk denemede:

    --rm
    -d

birlikte kullandım.

Bu debug için kötü oldu.

`-d`

→ çıktıyı arka plana attı.

`--rm`

→ process ölünce container'ı sildi.

Akış:

    Container hata verdi
          ↓
    Process kapandı
          ↓
    Container stopped
          ↓
    --rm container'ı sildi
          ↓
    Sonradan baktım
          ↓
    "No such container"

Debug için bunları kaldırıp foreground çalıştırmak hatayı görünür hale getirdi.

---

# 🧠 Container Lifecycle

Foreground'da:

`python -m http.server`

çalışırken terminal prompt'unun geri gelmemesi normal.

Çünkü server uzun yaşayan process.

Temel Docker modeli:

    Main process çalışıyor
            ↓
    Container çalışıyor

    Main process bitti
            ↓
    Container bitti

Container bağımsız küçük bir VM gibi kendi başına yaşamaz.

Ana process lifecycle çok önemlidir.

---

# 🐞 Küçük Typo

Bir denemede:

`cdocker run`

yazdım.

Sonuç:

    zsh: command not found: cdocker

Bu Docker problemi değildi.

Sadece shell'e yanlış command verdim.

Ders:

> Hata mesajının hangi katmandan geldiğini önce ayır.

---

# 🐍 Python HTTP Client

Kaynağımda önce `urllib.request.urlopen()` tarafındaki response object kavramlarını çalıştım.

Ama gerçek lab kodunda:

`http.client.HTTPConnection`

kullandım.

Bunları birbirine karıştırmamalıyım.

---

# 📚 `urllib.request` Tarafında Öğrendiğim Response Bilgileri

Başarılı bir response nesnesinden kabaca:

- status
- reason
- headers
- URL
- body

okunabilir.

Kısa:

    STATUS
    REASON
    HEADERS
    URL
    BODY

`read()`

body'yi okur.

Body:

    bytes

olarak gelir.

Metin olarak kullanmak için:

    bytes
      ↓
    decode()
      ↓
    str

---

# ⚠️ `HTTPError` vs `URLError`

`urllib.request` tarafındaki mental model:

## HTTPError

Server'a ulaşılmış ve HTTP-level problem response'u alınmış olabilir.

Örneğin:

- 403
- 404
- 500

## URLError

Daha çok:

- DNS
- Connection
- URL
- Network

tarafındaki problemlerde görülebilir.

Kısa:

    HTTPError
    → HTTP level

    URLError
    → URL/network/connectivity level

---

# ⚠️ Ama Gerçek Lab `http.client` Kullanıyor

Actual Python lab kodum:

`http.client.HTTPConnection`

kullandı.

Bu yüzden 404 testinde response nesnesini normal şekilde aldım:

    status=404
    body_bytes=335
    body_preview=<!DOCTYPE HTML> ...

Bu testte exception çıkmadı.

Bu ayrımı API'leri karıştırmamak için özellikle kafamda tutmam gerekiyor.

---

# 🐍 Actual Python HTTP Lab

Program:

    CLI URL
      ↓
    urlparse()
      ↓
    scheme kontrolü
      ↓
    hostname
      ↓
    port
      ↓
    path + query
      ↓
    HTTPConnection
      ↓
    GET
      ↓
    getresponse()
      ↓
    read()
      ↓
    status + body bilgileri

Yalnız:

`http://`

destekliyor.

Default port:

    80

---

# 🎯 Path + Query

Örneğin URL:

    http://host:18080/items?page=2

ise HTTP target:

    /items?page=2

olmalı.

Bu yüzden path ile query gerektiğinde birleştiriliyor.

---

# 📦 HTTP Response

Gerçek labda:

`response = connection.getresponse()`

sonrasında:

`response.status`

ile status code aldım.

`response.read()`

ile body aldım.

Body:

    bytes

tipinde.

---

# 🔡 Body Decode

Kodda:

`body.decode(errors="replace")`

kullandım.

Sonra ilk 100 karakteri preview olarak yazdırdım.

Bu daha önce öğrendiğim:

    encode
    decode

konusunun gerçek network kullanım alanı oldu.

Network'ten gelen body bytes olabilir.

Ben bunu metin olarak göstermek için decode ediyorum.

---

# ✅ HTTP 200 Testi

İstek:

`http://127.0.0.1:18080/hello.txt`

Sonuç:

    status=200
    body_bytes=21
    body_preview=hello-from-container

Burada:

    TCP ✅
    HTTP request ✅
    Resource bulundu ✅
    HTTP response ✅

---

# ❌ HTTP 404 Testi

İstek:

`http://127.0.0.1:18080/does-not-exist`

Sonuç:

    status=404

ve body içerisinde HTML error response geldi.

Bu çok önemli.

404 gördüysem:

    TCP connection KURULDU
            ↓
    HTTP request SUNUCUYA ULAŞTI
            ↓
    HTTP response GERİ GELDİ
            ↓
    İstenen resource BULUNAMADI

Yani:

> **404 TCP failure değildir.**

---

# 🌉 Docker + Python Client Büyük Resim

Container içindeki server:

    Container:8000

Docker mapping:

    127.0.0.1:18080
           ↓
    Container:8000

Python host üzerinde çalıştığı için bağlandığı adres:

    http://127.0.0.1:18080

Tam akış:

    Python Client
         ↓
    Host TCP connection
         ↓
    127.0.0.1:18080
         ↓
    Docker port publishing
         ↓
    Container:8000
         ↓
    Python http.server
         ↓
    /site/...
         ↓
    HTTP Response
         ↓
    Python response object

---

# 🐞 35B Hata Avı

## `-p 18080:8000` → container 18080'de çalışır

TIRT.

Container service hâlâ `8000`.

---

## `EXPOSE 8000` host'a gerçek port açar

TIRT.

---

## `127.0.0.1:18080` ile `0.0.0.0:8000` çelişir

TIRT.

Biri host, biri container tarafı.

---

## `-w` ile `--directory` aynı şey

TIRT.

---

## `docker port` container'ı bozdu

TIRT.

Container daha önce kapanmıştı.

---

## Foreground server terminali geri vermiyorsa takılmıştır

TIRT.

Long-running server'ın normal davranışı olabilir.

---

## Container durunca named volume da silinir

TIRT.

---

## Bind mount geçici, volume kalıcıdır

TIRT.

İkisi de container lifecycle'dan bağımsız veri tutabilir.

---

## HTTP 404 gördüysem TCP başarısızdır

TIRT.

Tam tersi, response alabildiğim için TCP ve HTTP request/response zincirinin önemli bölümü çalışmıştır.

---

# 🧠 35B Kafaya Kazı

> `-v` → Dosya nereden geliyor?

> `-w` → Process hangi directory'de çalışıyor?

> `--directory` → HTTP server hangi klasörü yayınlıyor?

> `--bind` → Server container içinde hangi interface'lerde dinliyor?

> `-p` → Host'tan container'a hangi port mapping'i var?

> PID 1 → Container'ın ana process'i kim?

> `--rm` → Container durunca kaydı silinsin mi?

> Bind mount → Host path'i ben yönetiyorum.

> Named volume → Storage'ı Docker yönetiyor.

> HTTP 404 → HTTP response aldım, resource bulunamadı.

---

# 📌 30 Saniyelik Özet

## TLS

    TCP Socket
        +
    SSLContext
        ↓
    wrap_socket()
        ↓
    TLS Handshake
        ↓
    Certificate Verification
        ↓
    Hostname Verification
        ↓
    SSLSocket

    create_default_context()
    → TLS kuralları

    wrap_socket()
    → mevcut TCP connection üzerinde TLS

    server_hostname
    → TLS server identity ile ilişkili

    SNI
    ≠
    Hostname Verification


## Docker

    Host 127.0.0.1:18080
             ↓
       Docker Mapping
             ↓
    Container :8000
             ↓
       HTTP Server


## Storage

    Writable Layer
    → container'a bağlı

    Bind
    → host-managed path

    Named Volume
    → Docker-managed storage


## HTTP

    HTTPConnection
          ↓
        GET
          ↓
    HTTP Response
          ↓
    status + body

    200
    → resource geldi

    404
    → TCP ve HTTP çalıştı, resource bulunamadı

---

# ✅ Günün Kazanımları

- [x] TCP ile TLS arasındaki sınır netleşti
- [x] TLS'nin TCP üzerinde çalıştığı öğrenildi
- [x] `SSLContext` ile TCP socket ayrıldı
- [x] `create_default_context()` mantığı oturdu
- [x] `wrap_socket()` mantığı oturdu
- [x] SNI ve hostname verification ayrıldı
- [x] TCP destination ve server identity ayrıldı
- [x] Certificate chain mental modeli öğrenildi
- [x] TCP OK / TLS FAIL deneyle kanıtlandı
- [x] `SSLCertVerificationError` gözlemlendi
- [x] OpenSSL ile TLS bağımsız doğrulandı
- [x] `-connect`, `-servername`, `-verify_hostname` ayrıldı
- [x] Tek değişkenli debugging experiment prensibi pekiştirildi
- [x] Docker PID 1 tekrarlandı
- [x] `docker stop` signal lifecycle tekrarlandı
- [x] Writable layer / bind / named volume ayrıldı
- [x] Host port ve container port ayrıldı
- [x] `127.0.0.1:18080:8000` syntax'ı oturdu
- [x] `EXPOSE` ile `-p` ayrıldı
- [x] Bind mount + HTTP server birlikte kullanıldı
- [x] `-w` ve `--directory` ayrıldı
- [x] Host bind ile container bind ayrıldı
- [x] `docker port` ile mapping doğrulandı
- [x] `curl` ile HTTP zinciri doğrulandı
- [x] `--rm -d` kullanımının debugging'i nasıl zorlaştırdığı görüldü
- [x] Container lifecycle'ın main process'e bağlı olduğu tekrarlandı
- [x] Python `http.client` ile HTTP GET gönderildi
- [x] Path + query target oluşturuldu
- [x] Response body bytes olarak okundu
- [x] Decode gerçek network verisinde kullanıldı
- [x] HTTP 200 ve 404 durumları karşılaştırıldı
- [x] 404'ün TCP failure olmadığı netleşti

---

# 🚀 Gün Sonu Sonucu

Bugünün büyük resmi benim için artık şu:

    HOSTNAME
       ↓
      DNS
       ↓
    IP:PORT
       ↓
      TCP
       ↓
      TLS
       ↓
     HTTP
       ↓
    APPLICATION

Docker tarafında ise:

    HOST FILESYSTEM
          ↓
       BIND MOUNT
          ↓
    CONTAINER FILESYSTEM

ve:

    HOST NETWORK
    127.0.0.1:18080
          ↓
    DOCKER PORT PUBLISHING
          ↓
    CONTAINER NETWORK
          :8000
          ↓
    HTTP SERVER

En kritik iki cümlem:

> **TCP connection bana adres erişimini kanıtlar; TLS ise konuştuğum server'ın kimliğini ve güvenli iletişimi ayrıca doğrulamaya çalışır.**

> **Docker'da bir parametrenin ne yaptığını anlamak için önce hangi katmana ait olduğunu bulmalıyım: host mu, container mı, filesystem mi, process mi, network mü, application mı?**