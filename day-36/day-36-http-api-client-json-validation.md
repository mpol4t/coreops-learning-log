---
title: "Gün 36 — HTTP/API Client, Request State, Bearer Token, JSON Parse ve Validation"
tags:
  - coreops
  - day36
  - http
  - api-client
  - urllib
  - request
  - bearer-token
  - json
  - validation
  - dns
  - tcp
  - tls
  - timeout
  - exceptions
  - debugging
  - git
aliases:
  - "Gün 36 HTTP API Client ve Validation"
status: completed
---

# 🌐 Gün 36 — HTTP/API Client, Request State, Bearer Token, JSON Parse ve Validation

> [!abstract] 🎯 Günün ana fikri
> Bugün önceki günlerde tek tek kurduğum network zincirinin üzerine gerçek bir API client mantığını oturttum.
>
> Artık zincirim:
>
>     URL / Request State
>            ↓
>           DNS
>            ↓
>           TCP
>            ↓
>           TLS
>            ↓
>      HTTP Request
>            ↓
>      HTTP Response
>            ↓
>         Status
>            ↓
>      Content-Type
>            ↓
>          Body
>            ↓
>       JSON Parse
>            ↓
>      Python Object
>            ↓
>       Validation
>            ↓
>     Application Data
>
> Günün en önemli düşüncesi:
>
> **"Çalıştı / çalışmadı" diye tek bitlik düşünmek yerine, hangi katmana kadar başarıyla geldiğimi ve ilk hangi contract'ın kırıldığını bulmalıyım.**

---

# 🧠 Gün 36A — HTTP Client ve Katman Bazlı Hata Ayrımı

## HTTP Katmanına Çıkmak

Önceki günlerde:

    DNS
     ↓
    TCP
     ↓
    TLS

zincirini ayrı ayrı inceliyordum.

Bugün bunun üzerine:

    HTTP Request
        ↓
    HTTP Response
        ↓
    Application / API Data

katmanlarını koydum.

Artık bir problem olduğunda:

> "Network bozuk."

demek yerine:

> **"İlk başarısız katman hangisi?"**

diye bakıyorum.

---

# 📡 HTTP Nedir?

HTTP application layer'da çalışan request/response protokolüdür.

Client:

    GET /users HTTP/1.1

gibi bir request gönderir.

Server:

    HTTP/1.1 200 OK

gibi bir response döndürür.

HTTP'nin ilgilendiği sorular artık:

- Hangi resource'u istiyorum?
- Hangi işlemi yapmak istiyorum?
- Hangi header'ları gönderiyorum?
- Body var mı?
- Server bana hangi status'u döndürdü?
- Response body ne içeriyor?

---

# 📤 HTTP Request'in Parçaları

Temel model:

    METHOD
      +
    REQUEST TARGET
      +
    HEADERS
      +
    OPTIONAL BODY

Örnek:

    GET /assets?id=10 HTTP/1.1
    Host: api.example.com
    Authorization: Bearer abc
    Accept: application/json

Burada:

`GET`

→ Ne yapmak istiyorum?

`/assets?id=10`

→ Hangi resource'u istiyorum?

Headers

→ Request metadata'sı

Body

→ Gerekirse gönderdiğim veri

---

# 🐞 Status Code Request'in Parçası Değil

Bugün düzelttiğim önemli noktalardan biri:

    status code = request'in parçası

TIRT.

Doğrusu:

    REQUEST
    ├── method
    ├── target
    ├── headers
    └── optional body

    RESPONSE
    ├── status code
    ├── headers
    └── optional body

Örnek:

    Request:
    GET /users HTTP/1.1

    Response:
    HTTP/1.1 200 OK

Buradaki:

    200

server'ın response bilgisidir.

---

# 🔧 HTTP Method

Method resource üzerinde ne yapmak istediğimi belirtir.

Temel methodlar:

- `GET` → veri getir
- `POST` → veri gönder / işlem oluştur
- `PUT` → resource'u oluştur veya tamamen değiştir
- `PATCH` → belirli kısmını değiştir
- `DELETE` → sil
- `HEAD` → GET benzeri, body istemez
- `OPTIONS` → desteklenen özellik/metotlar hakkında bilgi

Bir endpoint'in var olması bütün methodları kabul ettiği anlamına gelmez.

Örneğin:

    GET /users
    → çalışıyor

ama:

    POST /users
    → desteklenmiyor

ise:

    405 Method Not Allowed

gelebilir.

---

# 🔗 URL ile Request Target Aynı Şey Değil

Örnek:

    https://api.example.com:443/users?id=10#profile

Parçaları:

    scheme   → https
    host     → api.example.com
    port     → 443
    path     → /users
    query    → id=10
    fragment → profile

HTTP request-target:

    /users?id=10

olabilir.

Fragment:

    #profile

normal HTTP request ile server'a gönderilmez.

---

# 🏷️ HTTP Header

Header:

> HTTP request veya response hakkında metadata taşır.

Örnek:

    Accept: application/json
    Authorization: Bearer TOKEN
    Content-Type: application/json
    User-Agent: my-client/1.0

Header ile body aynı şey değildir.

---

# 🍽️ `Accept` vs `Content-Type`

## `Accept`

    Accept: application/json

Client'ın söylediği:

> Response'u mümkünse JSON formatında istiyorum.

## `Content-Type`

Örneğin response'ta:

    Content-Type: application/json

Server'ın söylediği:

> Gönderdiğim body'nin media type'ı JSON.

Kısaca:

    Accept
    → ne almak istiyorum?

    Content-Type
    → gönderilen body ne tür?

---

# ⚠️ `Accept: application/json` JSON Garantisi Değil

Client:

    Accept: application/json

gönderse bile server:

    Content-Type: text/html

ve HTML body döndürebilir.

Hatta:

    Content-Type: application/json

deyip bozuk JSON bile gönderebilir.

Bu yüzden client tek bir header'a körlemesine güvenmemeli.

Doğru model:

    Header kontrolü
          ↓
    Body
          ↓
    JSON Parse
          ↓
    Validation

---

# 🔐 Authorization Header

Protected endpoint'e credential göndermek için:

    Authorization: Bearer TOKEN

kullanılabilir.

Burada:

    Authorization
    → header adı

    Bearer
    → authentication scheme

    TOKEN
    → credential

Bearer token'ı credential olarak görmem gerekiyor.

---

# 🔑 Bearer Token

Kısa mental model:

> **Bearer token = taşıyan tarafa erişim sağlayabilen credential.**

Bu yüzden gerçek token'ı:

- source code'a gömmemeliyim
- Git'e commit etmemeliyim
- loglara basmamalıyım
- screenshot'larda göstermemeliyim

Labdaki:

    coreops-demo-token

gerçek secret değil, demo token.

---

# 🚨 Token'ı Query Parametresine Koymamak

Kötü örnek:

    https://api.example.test/assets?token=abc123

Normal Bearer kullanımı:

    Authorization: Bearer abc123

Query parametresindeki credential:

- loglara
- browser history'ye
- proxy kayıtlarına
- monitoring sistemlerine
- debug/error kayıtlarına

daha kolay taşınabilir.

Doğru cümlem:

> **Bearer token için standart/tercih edilen yer Authorization header'ıdır; credential'ı URL/query içine koymak kötü pratiktir.**

---

# 📦 Body ve Network Verisi

Python tarafında bir:

    dict

olabilir.

Ama network üzerinden doğrudan Python dict geçmez.

JSON örneğinde:

    Python dict
         ↓
    JSON string
         ↓
      encode
         ↓
       bytes
         ↓
      network

Response:

    network
       ↓
      bytes
       ↓
     decode
       ↓
     string
       ↓
    JSON parse
       ↓
    Python object

---

# 📥 HTTP Response

Response temel olarak:

- HTTP version
- status code
- headers
- optional body

içerebilir.

Örnek:

    HTTP/1.1 200 OK
    Content-Type: application/json

    {"id":10,"name":"Ali"}

---

# 🔢 HTTP Status Sınıfları

    1xx → informational
    2xx → success
    3xx → redirect
    4xx → request/client sınıfı
    5xx → server sınıfı

Örnekler:

    200 OK
    201 Created
    204 No Content

    301 Moved Permanently
    302 Found

    400 Bad Request
    401 Unauthorized
    403 Forbidden
    404 Not Found
    405 Method Not Allowed
    409 Conflict
    429 Too Many Requests

    500 Internal Server Error
    502 Bad Gateway
    503 Service Unavailable
    504 Gateway Timeout

---

# ✅ `200 OK` Her Şeyin Doğru Olduğunu Kanıtlamaz

200 yalnızca HTTP seviyesinde success'tir.

Örneğin:

    HTTP 200

ama body:

    {"success": false}

olabilir.

Ya da JSON beklerken:

    Content-Type: text/html

gelebilir.

Bu yüzden:

    HTTP success
    ≠
    API contract success

---

# ⚠️ `204 No Content`

204 başarılı bir 2xx response'dur.

Ama body beklenmez.

Bu yüzden:

    2xx
    → kesin JSON parse et

TIRT.

---

# ❌ `404 Not Found`

404:

> Server / HTTP responder request'i aldı ama istediğim resource/route bulunamadı.

Örneğin:

    /users

var.

Ben:

    /userrrr

istedim.

Sonuç:

    404

Bu noktada:

    DNS ✅
    TCP ✅
    TLS ✅   (HTTPS ise)
    HTTP ✅
    Resource ❌

---

# 🆚 TCP Failure vs HTTP 404

## TCP Failure

Örneğin:

    Connection refused

veya:

    Connection timed out

Burada HTTP konuşmasına bile geçememiş olabilirim.

HTTP status yoktur.

## HTTP 404

Request HTTP responder'a ulaştı.

Karşı taraf:

    404 Not Found

cevabı gönderdi.

Mental model:

    TCP failure
    → "Konuşacağım endpoint'e ulaşamadım."

    HTTP 404
    → "Ulaştım ve konuştum ama istediğim resource bulunamadı."

---

# ⚠️ 404 İçin Nüans

404 gördüğümde:

> Backend application kesin çalışıyor.

dememeliyim.

404 response'u:

- reverse proxy
- load balancer
- web server
- application

üretmiş olabilir.

Ama en azından:

> **Bir HTTP responder'a ulaşıp geçerli HTTP response aldım.**

---

# 💥 `500 Internal Server Error`

500 de geçerli HTTP response'dur.

Örneğin:

    DNS ✅
    TCP ✅
    TLS ✅
    HTTP Request ✅
    Server Processing ❌
    HTTP 500

Dolayısıyla:

    500 = TCP failure

TIRT.

---

# 🧭 Katmana Göre Hata Modelim

| Durum | İlk bakacağım katman |
| --- | --- |
| Hostname çözülemedi | DNS |
| Connection refused | TCP |
| Connection timeout | TCP / Network |
| Certificate verify failed | TLS |
| HTTP 401 | HTTP / Authentication |
| HTTP 404 | HTTP / Resource |
| HTTP 500 | HTTP / Server |
| 200 ama HTML geldi | Representation / API |
| 200 + JSON ama parse olmuyor | JSON Syntax |
| JSON parse oldu ama alan yanlış | Validation / API Contract |

---

# 🐍 `urllib.request`

Bugün daha yüksek seviyeli HTTP client abstraction'ına geçtim.

Kullandığım yapılar:

    Request
    urlopen

Önemli:

> `urllib` kullanmam DNS/TCP/TLS katmanlarını yok etmiyor.

Sadece:

    DNS
     ↓
    TCP
     ↓
    TLS
     ↓
    HTTP

işlerini daha yüksek seviyeli bir API arkasına saklıyor.

---

# 🆚 `urlparse()` vs `urlopen()`

## `urlparse()`

URL'yi analiz eder.

Request göndermez.

## `urlopen()`

Request'i gerçekten gerçekleştirir.

Kısa:

    urlparse()
    → URL'yi parçala

    urlopen()
    → URL'ye git / request'i gerçekleştir

---

# 📋 `Request` Ne İşe Yarıyor?

Önceden:

    urlopen(url)

ile yalnız URL üzerinden istek gönderebiliyordum.

Ama gerçek API request state'i daha zengin.

`Request` ile açıkça:

- URL
- method
- headers
- data/body

tanımlayabiliyorum.

Mental model:

> **Request = göndereceğim HTTP request'in state'i.**

---

# 🧠 Request State

Örneğin:

    URL           = /assets
    Method        = GET
    Accept        = application/json
    Authorization = Bearer ...

bunların hepsi request state'in parçaları.

Aynı URL'ye:

    GET

ile gitmek ve:

    DELETE

ile gitmek aynı request değildir.

Aynı şekilde tokenlı ve tokensız request de aynı request değildir.

> **URL request'in tamamı değil, yalnızca bir parçasıdır.**

---

# 🌊 `response.read()` ve Bytes

Network body:

    bytes

olarak gelir.

`response.read()`:

    bytes

döndürür.

Örneğin:

    b'{"id":10}'

Sonra:

    bytes
      ↓
    decode()
      ↓
     str

yapabilirim.

---

# ⚠️ `response.read()` Stream'i Tüketir

İlk:

    response.read()

body'yi okuyup stream'i ilerletir.

Sonra tekrar:

    response.read()

yaparsam:

    b''

görebilirim.

Bu yüzden body'yi bir kere okuyup değişkende tutmak daha mantıklı.

---

# 🧹 Context Manager

Response:

    with urlopen(...) as response:

şeklinde kullanılabilir.

Akış:

    resource aç
        ↓
       kullan
        ↓
    bloktan çık
        ↓
      cleanup

Socketlerde öğrendiğim lifecycle mantığının aynısı.

---

# ⏱️ Timeout

Önemli fark:

    time.sleep(5)
    ≠
    timeout=5

## Sleep

Programı bilerek bekletir.

## Timeout

Network operation'ın sınırsız süre bloklanmasını engeller.

Mental model:

> **Belirlediğim süre sınırı içinde operation ilerlemezse başarısız kabul et.**

Timeout koymazsam remote sistemdeki problem benim client'ın da uzun süre bloklanmasına sebep olabilir.

---

# ⚠️ `timeout=5` Bütün İşlem Kesin 5 Saniyede Biter Demek Değil

Daha gelişmiş sistemlerde:

- connect timeout
- read timeout
- overall deadline

ayrı olabilir.

Bu labdaki ana fikir:

> **Sonsuz bekleme yok.**

---

# 🚨 `urllib` Tuzaklarından Biri — HTTP Error Response Exception Olarak Gelebilir

İlk düşüncem:

    404 geldi
    → response.status == 404

Ama `urlopen()` bazı 4xx/5xx cevaplarını:

    HTTPError

olarak yükseltebilir.

Bu:

> HTTP response gelmedi.

demek değildir.

Tam tersine:

> **HTTP response geldi ama urllib error status'u exception mekanizmasından sundu.**

---

# 🔴 `HTTPError`

HTTPError bana gerçek HTTP hata response'u hakkında bilgi verebilir.

Örneğin:

    401
    403
    404
    500

Normal response'ta:

    response.status
    response.read()

HTTPError tarafında:

    hata.code
    hata.read()

kullanabilirim.

---

# 🌐 `URLError`

URLError request'in gerçekleştirilmesi sırasında daha genel problemlerde görülebilir.

Örneğin:

- DNS
- TCP
- TLS
- network
- URL/protocol tarafı

Buradaki önemli property:

    hata.reason

---

# 🧬 `HTTPError` ve `URLError` Sırası

Önemli inheritance ilişkisi:

    HTTPError
        ↓
    URLError

Yani `HTTPError`, `URLError` subclass'ı.

Bu yüzden:

    except HTTPError:
        ...

önce.

    except URLError:
        ...

sonra.

Genel kural:

> **Spesifik exception önce, genel exception sonra.**

---

# 🐞 `.reason` İçinde `"DNS"` Arama Hatası

İlk düşüncem:

> `.reason` içinde "TCP", "DNS", "TLS" kelimesi mi arayacağım?

TIRT.

`.reason` underlying exception instance'ını taşıyabilir.

Örneğin:

    gaierror
    → DNS

    ConnectionRefusedError
    → TCP

    SSLCertVerificationError
    → TLS verification

Dolayısıyla string aramak yerine exception type'ına bakmalıyım.

---

# 🐞 `is` vs `isinstance`

Yanlış:

    reason is gaierror

Çünkü:

    gaierror
    → class

    reason
    → exception instance

Benim sorum:

> Bu nesne şu class'ın instance'ı mı?

Doğru:

    isinstance(reason, gaierror)

Aynı şekilde:

    isinstance(reason, ConnectionRefusedError)

    isinstance(reason, SSLCertVerificationError)

---

# 🧪 Gün 36A Gerçek Hata Testleri

## DNS Failure

Test:

    https://this-host-does-not-exist.invalid/

Sonuç:

    gaierror

Model:

    DNS ❌
    TCP başlamadı
    TLS başlamadı
    HTTP başlamadı

---

## TCP Failure

Test:

    http://127.0.0.1:1/

Sonuç:

    Connection refused

Model:

    TCP ❌
    HTTP başlamadı

---

## TLS Failure

Test:

    https://expired.badssl.com/

Sonuç:

    CERTIFICATE_VERIFY_FAILED
    certificate has expired

Model:

    DNS ✅
    TCP ✅
    TLS ❌

---

## HTTP 404

Test:

    https://example.com/robot.txt

Sonuç:

    Response status: 404

ve HTML body.

Model:

    DNS ✅
    TCP ✅
    TLS ✅
    HTTP ✅
    Resource ❌

---

## Happy Path

Test:

    https://example.com

Sonuç:

    Response status: 200

ve body geldi.

---

# 🔢 2xx Kontrolünde Yaptığım TIRT

İlk yaklaşım:

    str(status).startswith("2")

Çalışsa bile gereksiz.

Status zaten integer.

Doğru soru:

> 200–299 arasında mı?

Daha temiz:

    200 <= status < 300

---

# 🚪 HTTP Status ≠ Process Exit Code

Bunları ayrı tutmam gerekiyor.

## HTTP Status

Remote server'ın cevabı:

    404

## stdout / stderr

Benim CLI programımın output kanalları.

## Process Exit Code

Programın OS'e sonucu:

    0
    non-zero

Örneğin mümkün:

    HTTP status = 404

ama program bunu stdout'ta gösterebilir ve:

    exit 47

ile bitebilir.

Bunlar farklı contract'lar.

---

# 🧪 Controlled Broken Case

Sadece:

    doğru endpoint → 200

test etmek yetersiz.

Bilerek:

    yanlış endpoint → 404

oluşturmak error path'i test ediyor.

Tek bozuk vaka için hipotezim:

> Server'a ulaşıyorum fakat yanlış endpoint/path istediğim için HTTP hata response'u geliyor; bu yüzden beklediğim JSON yerine HTML/text body görüyorum.

Ayırıcı deney:

    aynı server
    aynı network
    aynı client

yalnız:

    endpoint değişsin

Doğru endpoint:

    2xx + beklenen response

Yanlış endpoint:

    404

ise problemin path/endpoint tarafında olduğunu daha güçlü şekilde kanıtlarım.

---

# 🆚 404 vs 405

    GET /usres
    → 404

Resource/route bulunamadı.

    POST /users
    → 405

Resource olabilir ama method desteklenmiyor.

---

# 🧠 API Contract

API contract:

> Client ve server'ın request/response yapısı üzerinde yaptığı anlaşma.

Örneğin `/assets` contract'ı:

## Request

- Method = GET
- Authorization zorunlu
- Accept = application/json

## Successful Response

- HTTP status = 200
- Content-Type = application/json
- JSON root = object
- asset_id zorunlu ve string
- hostname zorunlu ve string

Her aşama ayrı kontrol.

---

# 🧩 Gün 36B — Gerçek API Client

36A'da:

    status + body

seviyesine kadar geldim.

36B'de artık client'ın işi:

    Request oluştur
         ↓
    Header'ları ekle
         ↓
    Request'i gönder
         ↓
    HTTP response
         ↓
    Status
         ↓
    Content-Type
         ↓
    Body
         ↓
    JSON Parse
         ↓
    Python Object
         ↓
    Validation
         ↓
    Output Contract

haline geldi.

En önemli sonuç:

> **HTTP isteğinin başarılı olması, API çağrısının tamamen başarılı olduğu anlamına gelmez.**

---

# 🧪 Server 200 Döndü ama Body Geçerli JSON Değilse?

Bu durumda network zincirini geçtim.

HTTP 200 alabildiysem:

    DNS ✅
    TCP ✅
    HTTP ✅

HTTPS olsaydı gerekli TLS akışı da geçmiş olurdu.

Ama JSON parse:

    ❌

Hata artık network katmanında değil.

Response representation / payload / API contract tarafında.

Server yanlış yapılandırılmış veya hatalı payload üretiyor olabilir.

---

# 🏗️ `fetch_asset(url, token)`

İlk fonksiyon ismim daha genel:

    request_json()

gibiydi.

Sonra:

    fetch_asset()

kullandım.

Çünkü fonksiyon yalnız JSON çekmiyor.

Ayrıca:

- request oluşturuyor
- asset endpoint'ine gidiyor
- response kontrol ediyor
- JSON parse ediyor
- asset contract'ını validate ediyor

Daha açıklayıcı isim oldu.

---

# 🧱 CLI ile HTTP Logic'i Ayırma

`argparse` dışarıda kaldı.

Akış:

    CLI
     ↓
    url + token
     ↓
    fetch_asset(url, token)
     ↓
    API logic

Bu şekilde CLI parsing ile request logic birbirinden ayrılmış oldu.

---

# 📋 Request Nesnesini Oluşturma

Request içerisinde:

    Accept: application/json

ve:

    Authorization: Bearer <token>

header'larını kullandım.

Burada teoriyi pratiğe çevirdim:

> **Token URL/query içinde değil, Authorization header state'i içinde.**

---

# ⏱️ `urlopen(request, timeout=3)`

Request'i:

    urlopen(request, timeout=3)

ile gönderdim.

Response lifecycle:

    with urlopen(...) as response:

ile yönetildi.

---

# 🐞 `response.status()` Hatası

İlk düşüncem:

    response.status()

olmuştu.

TIRT.

`status` method değil attribute.

Doğru:

    response.status

Ama:

    response.read()

method.

Kısa:

    status
    → değer / attribute

    read()
    → operation / method

---

# ✅ 2xx Kontrolü

Kullandığım:

    200 <= status < 300

Bu bütün 2xx success ailesini kapsıyor.

Ama önemli:

> `urllib` bazı 4xx/5xx status'larını bu kontrole gelmeden `HTTPError` olarak yükseltebilir.

---

# 🏷️ Content-Type Kontrolü

Ham olarak:

    Content-Type == "application/json"

karşılaştırmak yerine:

    response.headers.get_content_type()

kullandım.

Sebep:

Server:

    Content-Type: application/json; charset=utf-8

döndürebilir.

Ham string karşılaştırması sorun çıkarabilir.

Ama:

    get_content_type()

media type kısmını:

    application/json

olarak verir.

---

# 📥 Body Okuma

Content-Type doğruysa:

    response.read()

ile body'yi aldım.

Akış:

    response body
         ↓
       bytes
         ↓
    decode("utf-8")
         ↓
        str

---

# 🔄 JSON Parse

Text body:

    json.loads(body)

ile Python nesnesine dönüştü.

Ama:

> `json.loads()` başarılı olması yalnızca JSON parse'ın başarılı olduğunu gösterir.

API contract'ı henüz doğrulanmış değildir.

---

# 🆚 JSON Parse Success vs Validation Success

Örnek:

    {"asset_id": 42}

Bu geçerli JSON.

Yani:

    json.loads()
    → ✅

Ama contract:

    asset_id = str
    hostname = str

bekliyorsa:

    asset_id type ❌
    hostname missing ❌

Yani:

    JSON syntax ✅
    API contract ❌

---

# 🧱 Root Validation

Geçerli JSON her zaman object olmak zorunda değil.

Bunların hepsi geçerli JSON olabilir:

    ["a", "b"] → list
    "hello"    → str
    42         → int
    true       → bool
    null       → None

Ama benim contract:

> Root JSON object olmalı.

Bu yüzden:

    isinstance(data, dict)

kontrolü yaptım.

---

# 🐞 İlk Field Validation Hatası

İlk yaklaşım:

    if not data["asset_id"]:

Buradaki problem:

`asset_id` hiç yoksa:

    data["asset_id"]

doğrudan:

    KeyError

üretir.

Yani kendi hata mesajımı vermeden önce Python patlar.

Doğru sıra:

    "asset_id" in data
          ↓
    sonra data["asset_id"]

---

# 🐞 `is None` Field Presence Kontrolü Değil

Bir ara:

    data["asset_id"] is None

düşündüm.

Ama bu:

> Field var mı?

sorusunu cevaplamıyor.

Field yoksa yine:

    KeyError

oluşur.

Ayrı durumlar:

    "asset_id" not in data
    → field yok

    data["asset_id"] is None
    → field var ama value null

    data["asset_id"] == ""
    → field var ama empty string

Bunlar aynı şey değil.

---

# ✅ Doğru Field Validation Sırası

    data dict mi?
         ↓
    asset_id var mı?
         ↓
    asset_id str mi?
         ↓
    hostname var mı?
         ↓
    hostname str mi?

Önce presence.

Sonra value/type.

---

# ⚠️ Spec'te Olmayan Validation Kuralı Eklememek

Başarılı örnekte:

    asset_id=asset-01
    hostname=lab.local

değerleri dolu.

Buradan:

> Boş string kesin yasak olmalı.

sonucunu çıkaramam.

Görev contract'ı yalnızca:

- field var
- type string

diyorsa onunla sınırlı kalmalıyım.

> **Example value spec değildir.**

Eğer contract ayrıca:

> boş olamaz

deseydi ayrı kontrol eklerdim.

---

# 📤 Output da Bir Contract

İlk düşündüğüm:

    200
    asset-01
    lab.local

değer açısından doğru.

Ama görev:

    status=200
    asset_id=asset-01
    hostname=lab.local

istiyor.

Bu yüzden:

> **Output formatı da API/CLI contract'ın parçası olabilir.**

Otomatik test açısından değerlerin doğru olması tek başına yeterli değil.

---

# ✅ Happy Path

Komut:

    python3 asset_client.py \
      "http://127.0.0.1:18081/assets" \
      "coreops-demo-token"

Sonuç:

    status=200
    asset_id=asset-01
    hostname=lab.local

Exit code:

    0

Mock API:

    GET /assets HTTP/1.1" 200

gösterdi.

Tam başarılı zincir:

    Request
      ↓
    Authorization Header
      ↓
    HTTP 200
      ↓
    Content-Type JSON
      ↓
    Body
      ↓
    JSON Parse
      ↓
    Root Dict
      ↓
    Field Presence
      ↓
    Type Validation
      ↓
    Success Output

---

# 🔐 Wrong Token Testi

Komut:

    python3 asset_client.py \
      "http://127.0.0.1:18081/assets" \
      "wrong-token"

İlk çalıştırmada uzun traceback geldi.

Sonunda:

    HTTP Error 401: Unauthorized

vardı.

Bu traceback aslında şunu gösteriyordu:

    DNS ✅
    TCP ✅
    HTTP Request ✅
    Server Response ✅
    Authentication ❌

Yani 401:

- DNS problemi değil
- TCP problemi değil
- TLS problemi değil
- HTTP/Auth problemi

Asıl client hatam:

> `HTTPError` yakalamadığım için kullanıcıya traceback saçıyordum.

---

# 🧹 401 Hatasını Temizleme

`HTTPError` handling ekledikten sonra:

    HTTP error: 401 Unauthorized

şeklinde temiz çıktı aldım.

Process:

    non-zero

ile kapandı.

Böylece hem kullanıcı çıktısı düzeldi hem de error doğru katmanda raporlandı.

---

# 🧬 `HTTPError` vs `URLError` Gün 36B'de Tekrar Karşıma Çıktı

## HTTPError

    Server'a ulaştım
          ↓
    HTTP response aldım
          ↓
    HTTP status error

Örnek:

    401 Unauthorized

## URLError

Daha genel:

- DNS
- bağlantı
- host'a ulaşma
- request gerçekleştirme

problemlerini kapsayabilir.

Exception sırası:

    HTTPError
       ↓
    URLError

olduğu için daha spesifik olan önce yakalanmalı.

---

# 💣 Malformed JSON Testi

Bu testin amaçlanan response'u:

    HTTP status = 200
    Content-Type = application/json

ama body:

    {"asset_id":

gibi bozuk JSON.

Katmanlar:

    Network ✅
    HTTP ✅
    Content-Type ✅
    JSON Syntax ❌

Yani problem:

> Response payload / JSON syntax contract.

---

# ⚠️ Malformed JSON Testindeki İki Aşama

İlk çalıştırmalardan birinde:

    /broken

endpoint'i:

    HTTP 404

döndürdü.

Bu durumda client JSON parse aşamasına ulaşmadı.

Yani o çalışma aslında malformed JSON davranışını test etmedi; HTTP 404 path'ini test etmiş oldu.

Final durumda server:

    200
    Content-Type: application/json
    malformed body

döndürdüğünde:

    JSON parse FAIL

branch'i gerçekten doğrulandı.

Bu ayrım önemli:

> **Test etmek istediğim failure layer'a gerçekten ulaştığımı kanıtlamam lazım.**

---

# 💥 `JSONDecodeError`

Bozuk JSON:

    json.loads(body)

üzerinde failure oluşturuyor.

Bunu:

    json.JSONDecodeError

ile yakaladım.

Artık traceback yerine:

    JSON parse FAIL

basılıyor.

Akış:

    HTTP 200
       ↓
    Content-Type JSON
       ↓
    Body
       ↓
    json.loads()
       ↓
      FAIL

Burada network ve HTTP zaten başarılı.

---

# 🧪 Üç Ana Testin Final Durumu

## 1. Valid Request

    status=200
    asset_id=asset-01
    hostname=lab.local

    exit=0

Sonuç:

    HTTP ✅
    JSON ✅
    Domain Validation ✅

---

## 2. Wrong Token

    HTTP error: 401 Unauthorized

Sonuç:

    Network ✅
    HTTP ✅
    Authentication ❌

---

## 3. Malformed JSON

    JSON parse FAIL

Sonuç:

    Network ✅
    HTTP ✅
    Content-Type ✅
    JSON Parse ❌

---

# 🧩 Validation Katmanları

Validation'ı bile tek kontrol olarak düşünmemeliyim.

## Shape Validation

Gerekli field'lar var mı?

Örneğin:

- asset_id
- hostname

## Type Validation

Field tipleri doğru mu?

Örneğin:

    asset_id → str
    hostname → str

## Constraint Validation

Değer range'e uyuyor mu?

Örneğin başka bir contract'ta:

    port = 70000

JSON açısından:

    ✅

integer açısından:

    ✅

port constraint açısından:

    ❌

## Domain Validation

Uygulamaya özel kurala uyuyor mu?

Örneğin:

    asset_id

`asset-` ile başlamalı gibi ek bir contract varsa ayrıca kontrol edilmesi gerekir.

---

# 🧱 Başarıların Birbirinden Ayrılması

Şunlar farklı başarılar:

    HTTP Success
    JSON Parse Success
    Validation Success

Örnekler:

| Durum | HTTP | JSON Parse | Domain |
| --- | --- | --- | --- |
| 200 + doğru JSON + doğru alanlar | ✅ | ✅ | ✅ |
| 200 + HTML | ✅ | ❌ | — |
| 200 + bozuk JSON | ✅ | ❌ | — |
| 200 + valid JSON + yanlış field tipi | ✅ | ✅ | ❌ |
| 401 + JSON error body | HTTP success path değil | ✅ olabilir | Success değil |

---

# 🧭 Client Failure Zincirim

Artık bir API client'a şu sırayla bakıyorum:

    1. Input / URL
          ↓
    2. DNS
          ↓
    3. TCP
          ↓
    4. TLS
          ↓
    5. HTTP
          ↓
    6. Representation / Content-Type
          ↓
    7. JSON Parsing
          ↓
    8. Shape Validation
          ↓
    9. Type Validation
          ↓
    10. Constraint / Domain Validation
          ↓
    11. Application

Her adımda sormam gereken:

> **İlk bozulan contract hangisi?**

---

# 🧠 Gün 36'da Yaptığım Hatalar

## 1. Status code request'in parçasıdır

TIRT.

Status response'a aittir.

---

## 2. `urlopen()` kullanınca TCP/TLS artık yok

TIRT.

Yalnızca abstraction arkasında çalışıyorlar.

---

## 3. `404` aldım, network bozuk

TIRT.

HTTP response almışım.

---

## 4. `500` aldım, TCP bozuk

TIRT.

HTTP/server response'u.

---

## 5. Exception varsa HTTP response gelmemiştir

TIRT.

`HTTPError` gerçek HTTP response'u temsil edebilir.

---

## 6. `200` geldiyse API tamamen başarılıdır

TIRT.

Representation, parse ve validation hâlâ fail olabilir.

---

## 7. `Accept: application/json` gönderirsem kesin JSON gelir

TIRT.

Client tercihi/beklentisi.

---

## 8. `Content-Type: application/json` varsa body kesin valid JSON

TIRT.

Header beyanını parser ile doğrulamam gerekir.

---

## 9. Gelen response body'ye `json.dump/dumps` uygulamak

TIRT.

Network body önce bytes/text olarak gelir.

JSON parse gerekiyorsa `json.loads()` tarafına giderim.

---

## 10. `.reason` içinde `"DNS"` veya `"TCP"` kelimesi aramak

TIRT.

Underlying exception type'ını incelemeliyim.

---

## 11. `reason is gaierror`

TIRT.

Class/instance için:

    isinstance(...)

kullanmalıyım.

---

## 12. `response.status()`

TIRT.

Doğru:

    response.status

---

## 13. Field var mı diye direkt `data["asset_id"]` erişmek

Riskli.

Field yoksa:

    KeyError

Önce presence kontrolü.

---

## 14. `data["asset_id"] is None` ile key presence kontrol etmek

TIRT.

Bu value'nun `None` olup olmadığını kontrol eder.

Key'in varlığını değil.

---

## 15. Example değerlerden yeni validation kuralı üretmek

TIRT.

Örnek:

    asset_id=asset-01

gördüm diye:

> asset_id boş olamaz

kuralını spec söylemeden ekleyemem.

---

## 16. Output'ta yalnızca değerleri basmak yeterlidir

TIRT.

Output formatı da contract olabilir.

---

## 17. 401 görünce client tamamen bozuk sanmak

TIRT.

401 bana HTTP/Auth seviyesine ulaştığımı gösteriyor.

Asıl problem client'ın bunu temiz handle etmemesiydi.

---

## 18. Malformed JSON testinde 404 alıp JSON parser'ı test ettiğimi sanmak

TIRT.

404'te parse aşamasına ulaşmadım.

JSON parser'ı gerçekten test etmek için:

    HTTP 200
    +
    Content-Type JSON
    +
    malformed body

gerekti.

---

# 🧠 Kafaya Kazı

> [!quote]
> HTTP success ≠ API success.

> [!quote]
> HTTP 200 yalnızca HTTP katmanındaki success'i gösterir.

> [!quote]
> Accept client'ın isteğidir, Content-Type gelen body'nin türünü bildirir.

> [!quote]
> Bearer token request header state'idir.

> [!quote]
> Credential'ı URL/query içine koymak kötü pratiktir.

> [!quote]
> JSON parse success ≠ validation success.

> [!quote]
> `json.loads()` JSON syntax'ını bilir, benim business contract'ımı bilmez.

> [!quote]
> Presence, null, empty string ve yanlış type aynı problem değildir.

> [!quote]
> Example output spec değildir.

> [!quote]
> Output formatı da contract olabilir.

> [!quote]
> HTTPError gördüysem HTTP response gelmiş olabilir.

> [!quote]
> Daha spesifik exception önce, daha genel exception sonra.

> [!quote]
> Test etmek istediğim failure layer'a gerçekten ulaştığımı kanıtlamalıyım.

> [!quote]
> İlk sorum her zaman: "İlk hangi katman kırıldı?"

---

# 📌 30 Saniyelik Özet

    Request State
        ↓
    URL + Method + Headers + Body
        ↓
       DNS
        ↓
       TCP
        ↓
       TLS
        ↓
    HTTP Response
        ↓
      Status
        ↓
    Content-Type
        ↓
       Body
        ↓
    JSON Parse
        ↓
    Python Object
        ↓
    Shape Validation
        ↓
    Type Validation
        ↓
    Constraint / Domain Validation
        ↓
    Application


    Request
    → Ne göndereceğim?

    urlopen
    → Request'i gerçekleştir.

    Accept
    → Ne tür response istiyorum?

    Content-Type
    → Gelen body ne tür?

    Authorization
    → Credential burada.

    HTTPError
    → HTTP response geldi, status error olabilir.

    URLError
    → Daha alt request/network problemi olabilir.

    JSONDecodeError
    → Body JSON syntax olarak parse edilemedi.

    isinstance()
    → Nesnenin type/class ilişkisini kontrol et.

    200 <= status < 300
    → HTTP 2xx success ailesi.


    401
    → HTTP/Auth failure

    404
    → HTTP resource failure

    200 + HTML
    → Representation failure

    200 + JSON Content-Type + malformed JSON
    → JSON syntax failure

    200 + valid JSON + wrong field type
    → Validation failure

---

# 🌳 Git Uygulaması

Gün 36 çalışmasını ayrı feature branch'e aldım.

Branch:

    feature/http-client

Day36 dosyalarını stage ettim:

    git add Day36

Commit:

    Gün 36 feature/http-client dalına eklendi

Commit hash:

    fd186c7

Branch graph'ta:

    fd186c7 (HEAD -> feature/http-client)
        ↓
    eb984dd (feature/secure-runner)
        ↓
    ...

şeklinde gördüm.

Burada:

    HEAD
    → feature/http-client

üzerindeydi.

Ayrıca branch değiştirirken:

    M Gate2/git_duty

görmem Working Tree'deki mevcut değişikliğin branch switch ile otomatik kaybolmadığını tekrar gösterdi.

---

# ✅ Günün Kazanımları

- [x] HTTP request/response sınırı netleşti
- [x] Status code'un response'a ait olduğu oturdu
- [x] Method / request-target / header / body ayrıldı
- [x] URL ile request-target ayrıldı
- [x] Accept ve Content-Type ayrıldı
- [x] Authorization header mantığı öğrenildi
- [x] Bearer token'ın credential olduğu netleşti
- [x] Query yerine Authorization header kullanım nedeni öğrenildi
- [x] `Request` ile request state oluşturuldu
- [x] `urlopen()` abstraction mantığı öğrenildi
- [x] Abstraction altında DNS/TCP/TLS'nin hâlâ çalıştığı görüldü
- [x] Timeout ile sleep ayrıldı
- [x] HTTP 404 ile TCP failure ayrıldı
- [x] HTTP 500'ün network failure olmadığı netleşti
- [x] `HTTPError` ve `URLError` ayrıldı
- [x] Exception inheritance sırası öğrenildi
- [x] `.reason` içindeki underlying exception incelendi
- [x] `is` ve `isinstance` farkı gerçek hatayla öğrenildi
- [x] DNS/TCP/TLS/HTTP failure testleri yapıldı
- [x] Response body bytes → str dönüşümü kullanıldı
- [x] `response.read()` stream davranışı öğrenildi
- [x] JSON parse ile validation ayrıldı
- [x] `json.loads()` contract sınırı öğrenildi
- [x] JSON root `dict` validation yapıldı
- [x] Field presence ve field value ayrıldı
- [x] `KeyError` oluşturan validation yaklaşımı düzeltildi
- [x] asset_id type validation yapıldı
- [x] hostname type validation yapıldı
- [x] Spec'te olmayan validation eklememe prensibi öğrenildi
- [x] Content-Type media type düzgün kontrol edildi
- [x] Success output contract birebir uygulandı
- [x] `fetch_asset()` fonksiyonlaştırması yapıldı
- [x] Wrong-token / 401 kontrollü test edildi
- [x] `HTTPError` traceback'i temizlendi
- [x] Malformed JSON için `JSONDecodeError` yakalandı
- [x] Broken testin gerçekten hangi katmanı test ettiği ayırt edildi
- [x] Valid / Auth Fail / JSON Fail senaryoları birbirinden ayrıldı
- [x] Day36 feature branch'e commit edildi

---

# 🚀 Gün Sonu Sonucu

Bugün client konusunda zihinsel modelim ciddi şekilde genişledi.

Eskiden:

    URL
     ↓
    Request
     ↓
    Response

diye bakıyordum.

Şimdi:

    REQUEST STATE
         ↓
    URL / METHOD / HEADERS / BODY
         ↓
        DNS
         ↓
        TCP
         ↓
        TLS
         ↓
       HTTP
         ↓
    STATUS / HEADERS / BODY
         ↓
    REPRESENTATION
         ↓
     JSON PARSE
         ↓
    PYTHON OBJECT
         ↓
     VALIDATION
         ↓
    API CONTRACT
         ↓
    APPLICATION

diye düşünüyorum.

Günün en kritik cümlesi:

> **Bir API client'ın işi yalnızca server'dan `200` almak değildir; doğru request state'ini oluşturmak, response'un gerçekten beklenen representation'da olduğunu doğrulamak, payload'ı parse etmek, çıkan veriyi contract'a göre validate etmek ve hata olduğunda ilk kırılan katmanı doğru sınıflandırmaktır.**