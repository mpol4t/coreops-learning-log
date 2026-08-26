---
title: "Gün 37 — Docker Compose Foundation, Service DNS ve Container-to-Container Network"
tags:
  - coreops
  - day37
  - docker
  - docker-compose
  - compose
  - service
  - environment
  - lifecycle
  - networking
  - service-dns
  - localhost
  - port-mapping
  - troubleshooting
aliases:
  - "Gün 37 Docker Compose ve Service DNS"
status: completed
---

# 🐳 Gün 37 — Docker Compose Foundation + Service DNS + Container-to-Container Network

> [!abstract] 🎯 Günün ana fikri
> Bugün Docker Compose'u ayrı ve gizemli bir Docker dünyası gibi düşünmeyi bıraktım.
>
> Compose'un altında hâlâ bildiğim yapı var:
>
>     IMAGE
>       ↓
>     CONTAINER
>       ↓
>     PROCESS
>
> Compose bunun üstüne:
>
>     SERVICE TANIMI
>          +
>     compose.yaml
>          +
>     lifecycle yönetimi
>          +
>     service-to-service network
>
> ekliyor.
>
> Günün iki büyük mental modeli:
>
> **37A**
>
>     compose.yaml
>          ↓
>       SERVICE
>          ↓
>      CONTAINER
>          ↓
>       PROCESS
>
> **37B**
>
>     CLIENT
>       ↓
>     service name: api
>       ↓
>     Docker DNS
>       ↓
>     API container IP
>       ↓
>     TCP :8000
>       ↓
>     HTTP

---

# 🧩 Gün 37A — Docker Compose Foundation

## Compose Neden Var?

Normal Docker'da zamanla şöyle uzun komutlar oluşuyor:

    docker run
        --name ...
        -p ...
        -v ...
        -e ...
        IMAGE
        COMMAND

Burada tek komutta:

- hangi image?
- hangi environment?
- hangi port?
- hangi volume?
- hangi command?

gibi bütün runtime configuration'ı anlatıyorum.

Compose'un fikri:

> Bunları uzun bir `docker run` komutunda taşımak yerine bir dosyada tarif et.

Bu dosya:

    compose.yaml

Benim için en basit tanım:

> **Compose = uzun docker run tariflerini dosyaya taşıyıp yönetme sistemi.**

---

# 🧱 Image ≠ Container

Normal Docker modeli:

    IMAGE
    python:3.13-slim
         │
         │ docker run
         ↓
    CONTAINER

Image:

> Container oluşturmak için kullanılan kalıp.

Container:

> Image'dan oluşturulan gerçek runtime instance.

Bir image'dan:

    IMAGE
      ├── container-1
      ├── container-2
      └── container-3

oluşturulabilir.

Dolayısıyla:

> **IMAGE ≠ CONTAINER**

---

# 📄 `compose.yaml`

Örnek yapı:

    services:
      app:
        image: python:3.13-slim
        environment:
          APP_MODE: lab
        command: ["python", "show_env.py"]

Türkçesi:

> `app` adında bir service tanımla.

> Container'ını `python:3.13-slim` image'ından oluştur.

> Process environment'ına `APP_MODE=lab` ver.

> Başlarken belirtilen Python command'ini çalıştır.

---

# 🏷️ `services: app:` İçindeki `app` Nedir?

Bu bugün özellikle oturttuğum bir ayrım.

    services:
      app:

Buradaki:

    app

şunlardan hiçbiri değil:

- image adı
- container ID
- Python script'i

Bu:

> **Compose service name**

İsmini ben belirliyorum.

İstersem:

    backend
    api
    worker
    kopek

bile diyebilirim.

---

# 🧠 Service Nedir?

Benim için en net tanım:

> **Service = container'ın nasıl çalışacağının tarifi.**

Örneğin:

    SERVICE: app
        │
        ├── image
        │    └── python:3.13-slim
        │
        ├── environment
        │    └── APP_MODE=lab
        │
        └── command
             └── python show_env.py

Sonra:

    SERVICE TANIMI
          ↓
    docker compose up
          ↓
       CONTAINER

Dolayısıyla:

> **SERVICE ≠ CONTAINER**

Service rol/tanım.

Container gerçek runtime instance.

---

# 🧱 Bütün Yapı

    compose.yaml
         │
         ↓
      SERVICE
       "app"
         │
     ┌───┼──────────────┐
     │   │              │
    image environment command
     │   │              │
     └───┼──────────────┘
         │
         ↓
    docker compose up
         │
         ↓
     CONTAINER
         │
         ↓
      PROCESS

Başka mental model:

    IMAGE
    "neyden?"
       ↓
    SERVICE
    "nasıl çalışsın?"
       ↓
    CONTAINER
    "gerçek runtime"
       ↓
    PROCESS
    "çalışan program"

---

# 🖼️ `image:`

Örnek:

    image: python:3.13-slim

Cevapladığı soru:

> Bu service'in container'ı hangi image'dan oluşturulacak?

Eski Docker:

    docker run python:3.13-slim

Compose:

    image: python:3.13-slim

Aynı temel image bilgisini ifade ediyor.

---

# 🌱 `environment:`

Örnek:

    environment:
      APP_MODE: lab

Bunun anlamı:

> Container içinde çalışacak process'in environment'ına `APP_MODE=lab` koy.

Akış:

    compose.yaml
        ↓
    environment:
        ↓
    CONTAINER
        ↓
    PROCESS ENVIRONMENT
        ↓
    os.environ

Python isterse:

    os.environ.get("APP_MODE")

ile okuyabilir.

Önemli:

> `environment:` Python variable oluşturmaz.

Container process environment'ına environment variable verir.

---

# 🧠 `APP_MODE` vs `lab`

    APP_MODE: lab

Burada:

    APP_MODE
    → environment variable adı

    lab
    → benim verdiğim value

Docker'da önceden yaratılmış özel bir:

    lab environment

yok.

Ben yalnızca:

> `APP_MODE` isimli environment variable'ın değeri `lab` olsun.

diyorum.

Program bu değeri ister kullanır, ister kullanmaz.

---

# 🧪 Gerçek Environment Testim

Compose içinde:

    APP_MODE: compose-lab
    WORKER_NAME: polat

verdikten sonra uygulama:

    APP_MODE = compose-lab
    WORKER_NAME = polat

bastı.

Bu zinciri pratikte doğruladı:

    compose.yaml
         ↓
    environment
         ↓
    container
         ↓
    Python process
         ↓
    os.environ

---

# ⚙️ `command:`

Compose'taki:

    command:

service container başladığında kullanılacak command davranışını belirleyebilir.

Image'ın default command'i varsa bunu o service için değiştirebilir.

Mental model:

    IMAGE
      └── default command

Ama Compose:

    command: başka_command

verirse service o command ile çalışabilir.

---

# 📄 `compose.yaml` Container Değildir

Dosyayı yazmak:

    compose.yaml

tek başına container oluşturmaz.

    compose.yaml
       │
       │ sadece config/tarif
       X
    container

Tarifi runtime'a uygulamak için:

    docker compose up

gerekir.

---

# 🚀 `docker compose up`

Mental model:

> `compose.yaml` dosyasını oku ve tanımladığım sistemi ayağa kaldır.

Akış:

    compose.yaml
        ↓
    service config
        ↓
    image
        ↓
    container oluştur
        ↓
    process başlat

Kısaca:

> **up = tarifi runtime'a uygula.**

---

# 🔎 `docker compose ps`

Sorduğu soru:

> Bu Compose projesindeki container'lar şu an ne durumda?

Örneğin:

    docker compose up
         ↓
    container oluştu
         ↓
    docker compose ps
         ↓
    çalışıyor mu?

---

# 📜 `docker compose logs`

Service/container process'inin stdout/stderr çıktısını görebiliyorum.

Akış:

    PROCESS
      ↓
    stdout / stderr
      ↓
    Docker
      ↓
    docker compose logs

Örneğin:

    APP_MODE = compose-lab

çıktısını buradan gördüm.

---

# 🧹 `docker compose down`

Mental model:

    docker compose up
          ↓
    sistemi kur

    docker compose down
          ↓
    sistemi sök

Benim testimde:

- container kaldırıldı
- Compose default network kaldırıldı

Sonrasında:

    docker compose ps

boş çıktı.

Önemli:

> **`docker compose down` = bütün image'ları sil**

TIRT.

Image sistemde kalabilir.

---

# 🔁 Compose Lifecycle

Kısa zincirim:

    up
    ↓
    ayağa kaldır

    ps
    ↓
    state'e bak

    logs
    ↓
    process ne yapıyor?

    down
    ↓
    Compose runtime'ını sök

Kafama kazı:

> **up → ps → logs → down**

---

# 🔍 `docker compose config`

Bugün anlamını oturttuğum önemli command.

`cat compose.yaml`

şunu soruyor:

> Dosyaya ne yazdım?

`docker compose config`

şunu soruyor:

> Compose bu dosyadan ne anladı?

Kısa:

    cat compose.yaml
    → SOURCE CONFIG

    docker compose config
    → EFFECTIVE / RESOLVED CONFIG

---

# 🧪 `docker compose config` Testim

Kaynak Compose dosyamda:

    volumes:
      - .:/lab:ro

vardı.

Ama `docker compose config` bunu daha açık şekilde:

    type: bind
    source: /Users/.../day37a
    target: /lab
    read_only: true

olarak gösterdi.

Ayrıca:

    networks:
      default:
        name: day37a_default

gibi Compose'un implicit oluşturduğu config'i de gördüm.

Bu bana:

> Source YAML ile Compose'un efektif yorumu aynı presentation olmak zorunda değil.

mantığını gösterdi.

---

# 🆚 `cat` vs `docker compose config`

    cat compose.yaml
        ↓
    "Ben ne yazdım?"

    docker compose config
        ↓
    "Compose ne anladı?"

Debugging açısından önemli ayrım.

---

# 🌱 `.env` vs `environment:`

Bunlar aynı şey değil.

`.env`

→ Compose configuration interpolation/değer kaynağı olabilir.

`environment:`

→ Container process environment'ına değer verir.

Mental model:

    .env
      ↓
    Compose config çözümleme

Buna karşılık:

    environment:
       ↓
    container
       ↓
    process environment

Önemli:

> `.env` içinde variable olması onun otomatik olarak container environment'ına girdiğini kanıtlamaz.

---

# 🔄 Compose Dosyasını Değiştirince Çalışan Container Anında Değişmez

İlk config:

    APP_MODE=compose-lab

Container bu config ile oluşturuldu.

Sonra dosyayı:

    APP_MODE=changed

yaptım.

Sadece dosyayı değiştirmek:

    source config = changed

yapar.

Çalışan mevcut container'ın runtime state'ini sihirli şekilde değiştirmez.

Doğru mental model:

    compose.yaml değişti
          ↓
          X
    mevcut container anında değişmez

Yeni config'i runtime'a uygulamak için tekrar:

    docker compose up

gerekebilir.

Compose gerektiğinde container'ı recreate eder.

---

# 🧪 Environment Değişikliğini Kanıtladım

İlk değer:

    APP_MODE = compose-lab

Sonra Compose config'i:

    APP_MODE: changed

yaptım.

Tekrar `docker compose up` sonrasında log:

    APP_MODE = changed

geldi.

Bu zinciri doğruladım:

    source config değişti
          ↓
    Compose config
          ↓
    up
          ↓
    runtime
          ↓
    process yeni env'i gördü

---

# 🧠 Config Değişikliğini Kanıtlama Zinciri

Sadece:

> compose.yaml içinde yeni değer yazıyor.

demek runtime kanıtı değil.

Daha sağlam model:

    compose.yaml
        ↓
    docker compose config
        ↓
    "Compose yeni değeri gördü mü?"
        ↓
    docker compose up
        ↓
    "Yeni config runtime'a uygulandı mı?"
        ↓
    process
        ↓
    logs / env
        ↓
    "Gerçekte yeni değer var mı?"

---

# 💥 Gün 37A — Controlled Broken Case

Program artık:

    WORKER_NAME

environment variable'ını required kabul ediyor.

Mantık:

    WORKER_NAME var
        ↓
    program devam

    WORKER_NAME yok
        ↓
    missing required config
        ↓
    exit 1

Compose'tan `WORKER_NAME` kaldırdığımda:

    service started
    APP_MODE = compose-lab
    missing required config: WORKER_NAME

ve:

    app-1 exited with code 1

gördüm.

Bu bana şunu kanıtladı:

> Compose container'ı başlatabilir ama uygulamanın kendi configuration contract'ı başarısız olabilir.

Yani:

    Compose up ✅
    Container creation ✅
    Process başladı ✅
    Required application config ❌
    Process exit = 1

---

# 🧪 WORKER_NAME Testleri

## Test 1

    WORKER_NAME=worker-01

Sonuç:

    WORKER_NAME = worker-01
    exit code 0

## Test 2

    WORKER_NAME=worker-02

Sonuç:

    WORKER_NAME = worker-02
    exit code 0

## Test 3

`WORKER_NAME` yok.

Sonuç:

    missing required config: WORKER_NAME
    exit code 1

Bu environment → process contract'ını net şekilde test etti.

---

# 🧠 Gün 37A'da En Çok Zorlandığım Yer

Başta kavramları tek tek tanımlamaya çalışınca havada kaldılar:

- service
- image
- container
- environment
- compose.yaml
- config
- lifecycle

Konu şu eski bilgiye bağlanınca oturdu:

    docker run
        ↓
    container runtime config

Compose:

    docker run'daki config
        ↓
    compose.yaml

Yani yeni şeyi bildiğim modele bağlamam gerekiyormuş.

---

# 🧠 Gün 37A Kafaya Kazı

> `app` = service name.

> Service = çalışma tarifi.

> Container = service tarifinden oluşturulan runtime instance.

> Image = container'ın kalıbı.

> `environment:` = process environment state'i.

> `compose.yaml` = runtime nesnesi değil, config.

> `docker compose up` = config'i runtime'a uygula.

> `docker compose config` = Compose ne anladı?

> `docker compose logs` = process ne söylüyor?

> `docker compose down` = runtime ortamını sök.

> Source config değişikliği ≠ çalışan container anında değişti.

---

# 🌐 Gün 37B — Compose Service DNS ve Container-to-Container Network

## Ana Konu

Bugün iki Compose service'in birbirine nasıl ulaştığını öğrendim.

Service'ler:

    api
    client

API container içinde:

    :8000

dinliyor.

Client'ın hedefi:

    http://api:8000

Burada Mac'in:

    localhost

adresine gitmiyorum.

Host'a publish edilmiş portu da kullanmıyorum.

---

# 🌐 Compose Default Network

Compose dosyasında ayrıca:

    networks:

tanımlamasam bile service'ler networksüz kalmıyor.

Compose implicit:

    <project>_default

network oluşturuyor.

Örneğin:

    day37b_default
        /       \
      api      client

Dolayısıyla:

> `networks:` yazmadım = network yok

TIRT.

---

# 🔎 Gerçek Default Network Testim

`docker compose up -d` sonrasında:

    Network day37b_default Created

gördüm.

Aynı anda:

    day37b-api-1
    day37b-client-1

çalışıyordu.

Bu Compose'un implicit default network davranışını runtime'da gördüğüm kanıtlardan biri oldu.

---

# 🧭 Service Name DNS

Compose:

    services:
      api:

tanımladığında aynı network'teki başka service:

    api

adını hostname gibi kullanabiliyor.

Akış:

    client
       ↓
    "api nerede?"
       ↓
    Docker internal DNS
       ↓
    api'nin mevcut IP'si
       ↓
    TCP :8000
       ↓
    API

Önemli:

> `api` IP değildir.

Bu:

> **Compose service name**

Docker internal DNS bunu container'ın o anki IP'sine çözer.

---

# 🧪 Service DNS'i Gerçekten Kanıtladım

Client container içinde:

    getent hosts api

çalıştırdım.

Sonuç:

    172.20.0.2 api

Başka bir çalışma durumunda:

    172.20.0.3 api

gördüm.

Bu bana:

> Client container içerisindeki resolver `api` service name'ini Docker network içindeki bir IP'ye çözebiliyor.

kanıtını verdi.

Ama bu tek başına HTTP'nin çalıştığını kanıtlamaz.

---

# 🆚 Service Name vs Container IP

Hard-coded:

    http://172.20.0.2:8000

kullanmak sağlam değil.

Çünkü container recreate olduğunda IP değişebilir.

Mental model:

    container IP
    → geçici location

    service name
    → mantıksal/stabil isim

Daha sağlam hedef:

    http://api:8000

Docker yeni connection kurulurken service name'i mevcut endpoint'e çözebilir.

---

# ⚠️ Recreate Testimde Önemli Nüans

Ben:

    docker compose up -d --force-recreate --no-deps api

ile API container'ını recreate ettim.

Öncesinde resolver:

    172.20.0.3 api

döndürüyordu.

Recreate sonrasında da:

    172.20.0.3 api

döndürdü.

Yani bu spesifik çalıştırmada:

> **API'nin IP'sinin değiştiğini kanıtlamadım.**

IP aynı kaldı.

Ama recreate sonrasında:

    client.py
    → status: 200

çalışmaya devam etti.

Dolayısıyla bu testin gerçek kanıtı:

> **API recreate edildi ve service-name üzerinden iletişim çalışmaya devam etti.**

Genel olarak container IP'sinin recreate sonrasında değişebilmesi mümkün olsa da benim bu spesifik experiment'imde değişmedi.

---

# 🔌 DNS Mevcut TCP Bağlantısını Taşımaz

Service name çözümlemesi yeni IP'ye gidebilir.

Ama:

> DNS mevcut açık TCP connection'ı başka container'a teleport etmez.

Eski container giderse mevcut connection kopabilir.

Client yeni connection açarken tekrar:

    api

adını resolve edip güncel endpoint'e bağlanmalıdır.

---

# 🚪 Host Port vs Container Port

Örnek publish:

    127.0.0.1:18080:8000

Parçaları:

    127.0.0.1
    → host bind address

    18080
    → host port

    8000
    → container port

Host'tan:

    localhost:18080

kullanırım.

Ama aynı network'teki client container:

    api:8000

kullanır.

Kafaya kazı:

> **Host → container = host port**

> **Container → container = container port**

---

# 🆚 `api:8000` vs `api:18080`

`18080` API container'ın portu değil.

O host tarafındaki publish port.

Şema:

    HOST
    :18080
       ↓
    port publishing
       ↓
    API
    :8000

Client zaten Docker network içerisinde olduğundan:

    client
       ↓
    api:8000

ile direkt gider.

Dolayısıyla:

    api:18080

yanlış network katmanlarını birbirine karıştırmak olur.

---

# 🔓 `ports:` Container-to-Container İletişim İçin Zorunlu Değil

`ports:` temel olarak:

> Docker network'ünün dışından container servisine erişim yolu publish etmek.

Örneğin:

    Mac curl
       ↓
    localhost:18080
       ↓
    Docker publish
       ↓
    api:8000

Ama:

    client container
         ↓
       api:8000

aynı Docker network içerisindeyse host publishing'e ihtiyaç duymaz.

---

# 🧠 Publish Edilmemiş Port ≠ Kapalı Port

`ports:` kaldırıldığında:

> API artık 8000 portunda dinlemiyor.

sonucunu çıkaramam.

API container içinde hâlâ:

    :8000

dinliyor olabilir.

Sadece:

    HOST
      X
    publish path yok

olur.

Ama:

    client
      ↓
    api:8000

çalışmaya devam edebilir.

---

# 🏠 `localhost` Nedir?

Bugünün en kritik mental modellerinden biri.

`localhost`:

> **İçinde bulunduğum network namespace'in kendisi.**

Mac terminalindeysem:

    localhost
       ↓
    Mac

Client container içindeysem:

    localhost
       ↓
    client container

API container içindeysem:

    localhost
       ↓
    api container

Dolayısıyla:

> `localhost = Docker host`

TIRT.

Asıl soru:

> **Bu command nerede çalışıyor?**

---

# ❌ Client İçinden `localhost:8000`

Client container içindeyken:

    http://localhost:8000

dersem aslında:

> Client'ın kendi 8000 portunda servis var mı?

diye soruyorum.

API'ye gitmek için:

    http://api:8000

kullanmalıyım.

---

# 🧠 Üç Farklı Adres

Aynı API'ye nereden bağlandığıma göre target değişebilir.

| İstemci | Target |
| --- | --- |
| Mac / Host | `localhost:18080` |
| client container | `api:8000` |
| API'nin kendisi | `localhost:8000` |

Bu tablo bugünkü konunun merkezinde.

---

# 🔗 Container-to-Container HTTP Akışı

Client:

    http://api:8000/hello

istediğinde:

    URL
    http://api:8000/hello
          ↓
    host = api
    port = 8000
    path = /hello
          ↓
    Docker DNS
          ↓
    api → 172.x.x.x
          ↓
    TCP connection
          ↓
    client → API_IP:8000
          ↓
    HTTP GET /hello
          ↓
    API
          ↓
    HTTP Response

Yani Docker eski network bilgisini iptal etmedi.

Yine:

    DNS
     ↓
    TCP
     ↓
    HTTP

çalışıyor.

Sadece hostname çözümlemesini Docker network/service discovery sağlıyor.

---

# 🧪 Gerçek HTTP Testim

Client container içinde:

    python client.py

çalıştırdım.

Sonuç:

    status: 200
    body: <h1>hello-from-api-service</h1>

Bu bana yalnız DNS'i değil, çok daha ileriyi kanıtladı:

    service name resolution ✅
    Docker network ✅
    TCP connection ✅
    API server'a ulaşma ✅
    HTTP request ✅
    HTTP response ✅

---

# 👂 API Hangi Interface'e Bind Ediyor?

API:

    127.0.0.1:8000

üzerinde dinliyorsa yalnız kendi loopback interface'inden connection kabul eder.

Client:

    api:8000

ile Docker network interface'inden geldiği için erişemeyebilir.

Container-to-container erişimde server'ın çoğunlukla:

    0.0.0.0:8000

dinlemesi gerekir.

Mental model:

    127.0.0.1
    → yalnız kendi loopback'im

    0.0.0.0
    → uygun tüm IPv4 interface'leri

---

# 🏷️ Service Name vs Container Name

Compose service:

    api

Gerçek container name:

    day37b-api-1

olabilir.

Uygulama iletişiminde:

    day37b-api-1

gibi implementation/runtime adına bağlanmak yerine:

    api

service name'ini kullanmak daha doğru Compose modelidir.

---

# 🔍 `docker network inspect` Neyi Kanıtlar?

Network inspect sonucunda aynı network içerisinde:

    day37b-api-1
    IPv4Address = 172.20.0.3/16

ve:

    day37b-client-1
    IPv4Address = 172.20.0.2/16

gördüm.

Bu bana:

> **API ve client aynı Docker network'e bağlı.**

kanıtını verir.

Ama:

> HTTP kesin çalışıyor.

kanıtını vermez.

Çünkü network membership doğru olsa bile:

- API process çalışmıyor olabilir
- yanlış portta dinleyebilir
- yanlış interface'e bind olabilir
- TCP reject olabilir
- HTTP tarafı problemli olabilir

---

# 🧠 Kanıt Katmanlarını Ayırmak

    docker network inspect
    → network membership kanıtı

    getent hosts api
    → service name çözümleme kanıtı

    client.py → status 200
    → TCP + HTTP iletişiminin de çalıştığına dair ileri katman kanıtı

Tek bir aracı bütün sistemin kanıtı gibi kullanmamalıyım.

---

# 🔧 Container-to-Container Debugging Sıram

`client → api:8000` çalışmıyorsa:

    1. Aynı network'teler mi?
           ↓
    2. `api` resolve oluyor mu?
           ↓
    3. Hangi IP'ye resolve oluyor?
           ↓
    4. TCP :8000 kuruluyor mu?
           ↓
    5. API process gerçekten çalışıyor mu?
           ↓
    6. Gerçekten :8000 dinliyor mu?
           ↓
    7. 127.0.0.1 yerine uygun interface'e bind edilmiş mi?
           ↓
    8. HTTP response geliyor mu?
           ↓
    9. Status code ne?

Rastgele Compose satırlarını değiştirmek yerine failure boundary bulmalıyım.

---

# 🧪 `404` Alırsam Ne Kanıtlarım?

Client:

    http://api:8000/birsey

isteğinde:

    404

alıyorsa:

    service name çözümleme ✅
    Docker network ✅
    TCP ✅
    HTTP server ✅
    HTTP response ✅
    resource/path ❌

Yani:

> **404 bağlantı kurulamadı demek değildir.**

HTTP responder'a kadar ulaştım.

---

# 💥 Gün 37B Broken Case — `Connection refused`

Client tarafındaki hedefi bozduğum testte:

    ConnectionRefusedError
    [Errno 111] Connection refused

ve ardından:

    urllib.error.URLError

gördüm.

Burada önemli olan:

> Bu HTTP 404 gibi application response'u değil.

HTTP response seviyesine ulaşmadan TCP connection başarısız olmuş.

Sonra `client.py` düzeltildikten ve ortam tekrar ayağa kaldırıldıktan sonra:

    status: 200
    body: <h1>hello-from-api-service</h1>

geldi.

Yani broken ve healthy davranışları birbirinden ayırdım.

---

# ⚠️ `down → up` Testinde Gördüğüm `Connection refused`

Bir testte:

    docker compose down
    docker compose up -d
    docker compose exec client python client.py

zincirinin hemen ardından:

    Connection refused

gördüm.

Bu log tek başına root cause'un ne olduğunu kanıtlamıyor.

Kaynak çıktısından kesin söyleyebildiğim:

    Compose container'ları başlattı
          ↓
    client request denedi
          ↓
    TCP connection refused

Sonrasında `client.py` üzerinde değişiklik ve yeniden `down/up` sonrasında:

    status: 200

geldi.

Dolayısıyla bu spesifik failure için eldeki kanıt:

> **Client TCP connection kuramadı.**

Ama sadece bu logdan:

> "Kesin startup race'ti"

veya:

> "Kesin yanlış URL'ydi"

demem doğru olmaz.

---

# 🧠 `depends_on` ile Network'ü Karıştırmamak

`depends_on`:

> Docker DNS yaratır.

değil.

`depends_on`:

> İki container'ın iletişim kurmasını sağlar.

da değil.

Service discovery/network ayrı mekanizma.

`depends_on` başlangıç dependency/order tarafındaki başka bir Compose konusu.

---

# 🐞 Gün 37'de Düşmemem Gereken TIRT Modeller

## 1. `app` image adıdır

TIRT.

Compose service name.

---

## 2. Service ile container aynı şey

TIRT.

    service
    → tarif

    container
    → runtime instance

---

## 3. `environment:` Python variable oluşturur

TIRT.

Process environment'a environment variable aktarır.

---

## 4. `APP_MODE: lab` içindeki `lab` önceden oluşturulmuş Docker environment'ıdır

TIRT.

Sadece `APP_MODE` variable'ına benim verdiğim string value.

---

## 5. Compose dosyasını değiştirince çalışan container anında değişir

TIRT.

Config'in runtime'a yeniden uygulanması gerekir.

---

## 6. `docker compose down` image'ı kesin siler

TIRT.

---

## 7. `.env` içine yazılan her variable otomatik container'a girer

TIRT.

---

## 8. `networks:` yazmadıysam container networksüzdür

TIRT.

Compose implicit default network oluşturur.

---

## 9. `localhost` her zaman Mac'i gösterir

TIRT.

Bulunduğum network namespace'i gösterir.

---

## 10. Container'ların iletişimi için `ports:` zorunlu

TIRT.

Aynı network'te service name + container port yeterli olabilir.

---

## 11. `18080:8000` varsa client container `api:18080` kullanmalı

TIRT.

Doğru:

    api:8000

---

## 12. Publish edilmemiş port kapalıdır

TIRT.

Container içinde hâlâ dinleniyor olabilir.

---

## 13. Container IP'sini hard-code etmek daha güvenilir

TIRT.

Container IP runtime/recreate ile değişebilir.

---

## 14. `api` resolve oluyorsa HTTP kesin çalışıyor

TIRT.

Sadece DNS/service discovery katmanını kanıtlar.

---

## 15. `docker network inspect`te container göründüyse uygulama kesin çalışıyor

TIRT.

Sadece network membership.

---

## 16. Force recreate yaptım, demek IP değişti

TIRT.

Benim gerçek testimde recreate sonrası IP yine:

    172.20.0.3

olarak kaldı.

Recreate'i kanıtladım ama IP değişimini kanıtlamadım.

---

## 17. Connection refused gördüysem DNS bozuk

TIRT.

İsim çözümleme geçmiş olabilir; TCP connection reject edilmiş olabilir.

---

# 🧠 Host Port / Container Port Karar Modelim

Bir adres gördüğümde:

    http://X:Y

önce üç soru:

## 1. Client nerede?

- Mac/host?
- Container?

## 2. `X` kimi gösteriyor?

- localhost?
- service name?
- IP?

## 3. `Y` ne?

- host port?
- container port?

Örnek:

    client container
        ↓
    http://api:8000

Analiz:

    client
    → Docker container

    api
    → Compose service name

    8000
    → API container port

Sonuç:

> Doğru container-to-container adresleme.

---

# 🗺️ Bütün Günün Tek Resmi

                         MAC / HOST

                      localhost:18080
                             │
                             │ port publishing
                             ↓

             +------ COMPOSE DEFAULT NETWORK ------+
             |                                      |
             |                                      |
             |     CLIENT                    API    |
             |   172.20.0.2             172.20.0.3 |
             |                               │      |
             |                               │8000  |
             |                               │      |
             |       api                     │      |
             |        │                      │      |
             |        ↓                      │      |
             |   Docker DNS                  │      |
             |        │                      │      |
             |        └────→ API IP ─────────┘      |
             |                                      |
             | client → http://api:8000 → API       |
             |                                      |
             | client → localhost                   |
             |              ↓                       |
             |        CLIENT'IN KENDİSİ             |
             |                                      |
             +--------------------------------------+

---

# 📌 30 Saniyelik Özet

## Compose

    compose.yaml
        ↓
    service
        ↓
    docker compose up
        ↓
    container
        ↓
    process

## Environment

    environment:
        ↓
    container process environment
        ↓
    os.environ

## Lifecycle

    config
    → Compose ne anladı?

    up
    → uygula

    ps
    → runtime state

    logs
    → process output

    down
    → Compose runtime'ını sök

## Networking

    client
      ↓
    api
      ↓
    Docker DNS
      ↓
    container IP
      ↓
    TCP :8000
      ↓
    HTTP

## Adresleme

    Host → API
    localhost:18080

    Client container → API
    api:8000

    API → kendisi
    localhost:8000

## Kanıt

    network inspect
    → aynı network mü?

    getent hosts api
    → service DNS çalışıyor mu?

    HTTP 200
    → DNS + network + TCP + HTTP zinciri çalıştı

---

# ✅ Günün Kazanımları

- [x] Compose'un Docker'ın yerine geçmediği anlaşıldı
- [x] `docker run` ile Compose arasında zihinsel bağlantı kuruldu
- [x] Image ve container ayrıldı
- [x] Service ve container ayrıldı
- [x] Service name kavramı oturdu
- [x] `image:` görevi öğrenildi
- [x] `environment:` process environment ile bağlandı
- [x] Environment variable name/value ayrıldı
- [x] `command:` mantığı oturdu
- [x] `compose.yaml` ile runtime ayrıldı
- [x] `docker compose up` kullanıldı
- [x] `docker compose ps` kullanıldı
- [x] `docker compose logs` kullanıldı
- [x] `docker compose down` kullanıldı
- [x] `docker compose config` effective config olarak öğrenildi
- [x] `cat` ile `compose config` ayrıldı
- [x] `.env` ile `environment:` ayrıldı
- [x] Compose config değişikliğinin runtime'a otomatik geçmediği görüldü
- [x] Environment değişikliği runtime loglarıyla kanıtlandı
- [x] Required `WORKER_NAME` config failure test edildi
- [x] Exit 0 ve exit 1 davranışları gözlemlendi
- [x] Compose implicit default network öğrenildi
- [x] `day37b_default` runtime'da gözlemlendi
- [x] Service-name DNS mantığı oturdu
- [x] `getent hosts api` ile DNS doğrulandı
- [x] Container IP ile service name ayrıldı
- [x] Host port ve container port ayrıldı
- [x] `localhost` network namespace mantığı oturdu
- [x] Container-to-container iletişimde `api:8000` kullanıldı
- [x] Port publishing'in container-to-container iletişim için zorunlu olmadığı anlaşıldı
- [x] `0.0.0.0` ve `127.0.0.1` bind farkı tekrarlandı
- [x] Service name ve container name ayrıldı
- [x] API recreate edildi
- [x] Recreate sonrası service-name iletişimi test edildi
- [x] Recreate testinde IP'nin aslında değişmediği doğru yorumlandı
- [x] `docker network inspect` ile network membership kanıtlandı
- [x] Network inspect'in HTTP'yi kanıtlamadığı anlaşıldı
- [x] Client → API HTTP 200 testi yapıldı
- [x] Broken TCP connection testi yapıldı
- [x] `ConnectionRefusedError` / `URLError` gözlemlendi
- [x] 404'ün TCP failure olmadığı tekrarlandı
- [x] Docker network debugging için katmanlı sıra oluşturuldu

---

# 🚀 Gün Sonu Sonucu

Bugün Docker Compose konusunda iki şeyi birleştirdim.

Birincisi runtime/config tarafı:

    IMAGE
      ↓
    SERVICE
      ↓
    CONTAINER
      ↓
    PROCESS

İkincisi network tarafı:

    SERVICE NAME
         ↓
    DOCKER DNS
         ↓
    CONTAINER IP
         ↓
        TCP
         ↓
        HTTP

Artık Compose dosyasına bakarken sadece YAML satırları görmüyorum.

Şunu görüyorum:

    "Bu service hangi image'dan oluşacak?"
    "Process hangi environment ile başlayacak?"
    "Hangi command çalışacak?"
    "Runtime config gerçekten uygulandı mı?"
    "Client şu anda hangi network namespace'te?"
    "`localhost` burada kimi gösteriyor?"
    "Hedef service name mi, IP mi?"
    "Host port mu kullanıyorum, container port mu?"
    "DNS çalıştıysa TCP de çalıştı mı?"
    "Network membership var diye HTTP'yi kanıtlamış oldum mu?"

Günün en kritik iki cümlesi:

> **Compose, container değildir; container'ların nasıl oluşturulup çalıştırılacağını tarif eden ve bu tarifi Docker'a uygulatan yönetim katmanıdır.**

> **Aynı Compose network'ündeki container'lar birbirlerine genellikle service name + container port ile ulaşır; `localhost` ise her zaman komutun çalıştığı network namespace'in kendisini gösterir.**