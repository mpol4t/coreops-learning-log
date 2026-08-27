---
title: "Gün 39 — Python ↔ PostgreSQL Integration Test"
tags:
  - coreops
  - day39
  - python
  - postgresql
  - psycopg
  - integration-test
  - sql
  - transaction
  - docker
aliases:
  - "Gün 39 Python PostgreSQL Integration Test"
status: completed
---

# 🐘 Gün 39 — Python ↔ PostgreSQL Integration Test

> [!abstract] 🎯 Ana fikir  
> Bugün Python kodumun **gerçek PostgreSQL ile konuşmasını** ve bu zinciri integration test ile doğrulamayı öğrendim.
> 
> Ana zincir:
> 
> ```
> Python Repository
>        ↓
>     Psycopg
>        ↓
>      TCP
>        ↓
>   PostgreSQL
>        ↓
>       SQL
>        ↓
>    Result Set
>        ↓
>      Python
> ```
> 
> **Integration testte tek bir fonksiyonu değil, gerçek parçaların birlikte çalışmasını test ediyorum.**

---

# 🧪 Unit Test vs Integration Test

## Unit Test

Bir parçayı izole test ederim.

```
Repository
    ↓
  Mock DB
```

Gerçek PostgreSQL olmak zorunda değildir.

## Integration Test

Gerçek bileşenleri birbirine bağlarım.

```
Repository
    ↓
  Psycopg
    ↓
PostgreSQL
```

> [!important]  
> **Mock DB ile repository fonksiyonunu test edebilirim ama PostgreSQL entegrasyonunu test etmiş olmam.**

Kısa:

```
Unit Test
→ parçayı test et

Integration Test
→ parçaların birlikte çalışmasını test et
```

---

# 🐍 Psycopg Mental Modeli

Psycopg, Python ile PostgreSQL arasındaki katman.

Bugün öğrendiğim temel üçlü:

```
connect()
   ↓
execute()
   ↓
fetch...
```

### `connect()`

PostgreSQL ile bir **database session** açar.

### `execute()`

SQL'i PostgreSQL tarafında çalıştırır.

### `fetchone()`

Result set'ten sıradaki tek row'u getirir.

### `fetchall()`

Result set'te kalan bütün row'ları getirir.

> [!warning]  
> `fetchall()` bütün database'i getirmez.
> 
> Sadece mevcut sorgunun ürettiği result set'in kalanını getirir.

---

# 🔌 Connection ve Cursor

Başta `conn` nesnesini TCP bağlantısı gibi düşünmek kolay ama tam olarak öyle değil.

```
Connection
    ↓
  Psycopg
    ↓
PostgreSQL Protocol
    ↓
   TCP
```

**Connection** → PostgreSQL ile açılmış database session.

**Cursor** → SQL çalıştırma ve result set üzerinde ilerleme tarafındaki nesne.

Psycopg 3 sayesinde:

`conn.execute(...)`

kullanabiliyorum.

Bu, cursor mekanizmasının ortadan kalktığı anlamına gelmiyor; Psycopg bazı adımları benim için kısaltıyor.

---

# 🔐 SQL Parameter Binding

Bugünün en önemli noktalarından biri buydu.

Kullanıcı/değişken datasını f-string ile SQL'in içine gömmek:

```
SQL CODE
   +
USER DATA
   ↓
tek string
```

**TIRT.**

Problem sadece SQL injection değil.

Asıl problem:

> **SQL kodu ile data arasındaki sınırı yok etmiş oluyorum.**

Doğru model:

```
SQL TEMPLATE ─────┐
                 ├──→ Psycopg → PostgreSQL
PARAMETERS ───────┘
```

Örneğin:

`WHERE name = %s`

ve değer:

`(owner_name,)`

şeklinde ayrı gider.

---

## `%s` ile öğrendiğim şeyler

- Psycopg'daki `%s`, klasik Python string formatting değildir.
    
- Integer için `%d` kullanmam; normal value binding'de yine `%s` kullanırım.
    
- `%s` etrafına elle `' '` koymam.
    
- Psycopg değerin quoting/type adaptation işini kendisi yapar.
    
- Tek parametre gönderiyorsam `(owner_name,)` şeklindeki virgül tek elemanlı tuple oluşturur.
    

Örneğin:

`O'Reilly`

gibi içinde `'` bulunan bir değer parameter binding ile **SQL kodu olarak değil data olarak** ele alınır.

---

# ⚠️ VALUE vs IDENTIFIER

Burada bir ayrım daha öğrendim:

```
"Polat"
80
True
  ↓
VALUE
```

Ama:

```
assets
owners
hostname
  ↓
IDENTIFIER
```

`%s` normal **value binding** içindir.

Bu yüzden table adını:

`SELECT * FROM %s`

şeklinde normal parameter olarak geçemem.

---

# 🔄 Transaction — COMMIT / ROLLBACK

Database işlemleri transaction içinde ilerleyebilir.

Mental model:

```
             Transaction
                 │
           işlemler yapılır
              /       \
             /         \
         başarılı       hata
            ↓            ↓
         COMMIT       ROLLBACK
```

### COMMIT

Yaptığım değişiklikleri kesinleştirir.

### ROLLBACK

Transaction sırasında yapılan değişiklikleri geri alır.

`with psycopg.connect(...) as conn:`

kullandığımda connection lifecycle'ını context manager ile yönetebiliyorum.

> [!note]  
> Transaction sadece `INSERT / UPDATE / DELETE` konusu değil.
> 
> Normal non-autocommit kullanımında `SELECT` bile transaction başlatabilir.

---

# 🐳 Docker'da `localhost` Tuzağı

Compose içindeki iki servis:

```
app
db
```

olsun.

`app` container'ının içinden:

`localhost`

dersem:

```
localhost
   =
app container
```

PostgreSQL başka container'daysa genellikle:

`db:5432`

gibi **service name** üzerinden giderim.

Ama Mac üzerinden published porta bağlanıyorsam yol farklı:

```
Mac
 ↓
127.0.0.1:15432
 ↓
PostgreSQL Container
```

Yani:

> **Host'tan PostgreSQL'e gitmek ile başka container'dan PostgreSQL'e gitmek aynı network yolu değil.**

---

# 🧪 Bugünkü Integration Test

Test için gerçek `coreops_test` PostgreSQL database'ini kullandım.

Test başlangıcında:

`TRUNCATE TABLE assets, owners RESTART IDENTITY CASCADE`

ile önceki testlerden kalmış verileri temizledim.

Sonra kontrollü test datası oluşturdum:

```
owner:
test-team

assets:
alpha.local → risk 80
beta.local  → risk 20
```

Repository fonksiyonumu:

`test-team`

için çalıştırdım.

Beklediğim:

```
[
    ("alpha.local", 80),
    ("beta.local", 20)
]
```

Sonra:

`assert rows == expected`

ile gerçek PostgreSQL sonucunu kontrol ettim.

---

# ✅ Test Sonucu

Çalıştırdığım:

`PYTHONPATH=. python tests/integration_check.py`

Sonuç:

```
PASS
```

Tekrar çalıştırdım:

```
PASS
```

Yani testin state'i önceki çalışmadan bozulmadı ve aynı başlangıç koşullarında aynı sonucu aldım.

Bu PASS ile sadece assert'i değil, kabaca şu zinciri doğrulamış oldum:

```
Python
  ↓
Psycopg
  ↓
TCP
  ↓
PostgreSQL
  ↓
Database
  ↓
Tables
  ↓
SQL
  ↓
Result
  ↓
Assert
  ↓
PASS
```

---

# 🐞 Hata Avı / Karıştırmamam Gerekenler

## 1. Mock DB = PostgreSQL integration test

**TIRT.**

Mock kullanırsam gerçek PostgreSQL sınırını test etmiyorum.

---

## 2. `conn` direkt TCP socket

**TIRT.**

Connection bir PostgreSQL session nesnesi; TCP bunun altında.

---

## 3. `execute()` sonucu Python'a getirir

**TIRT.**

```
execute()
   ↓
SQL çalışır
   ↓
result set
   ↓
fetch...
   ↓
Python
```

---

## 4. SQL'e f-string ile data gömmek

**TIRT.**

SQL ve data ayrı gitmeli.

---

## 5. Integer → `%d`

**TIRT.**

Psycopg normal value parameter'larında `%s` kullanır.

---

## 6. `'%s'` yazmak

**TIRT.**

Doğrusu:

`%s`

Quoting Psycopg'un işi.

---

## 7. `(owner)` tek elemanlı tuple

**TIRT.**

`(owner,)` tek elemanlı tuple'dır.

---

## 8. Table adı da `%s` ile gider

**TIRT.**

Value ile identifier farklı şeyler.

---

# 🧭 Integration Test Patlarsa Debug Sıram

Rastgele kod değiştirmek yerine:

```
PostgreSQL ayakta mı?
        ↓
    host doğru mu?
        ↓
    port doğru mu?
        ↓
   TCP kuruluyor mu?
        ↓
authentication tamam mı?
        ↓
 doğru database mi?
        ↓
 table/schema var mı?
        ↓
    SQL doğru mu?
        ↓
   veri geliyor mu?
        ↓
Python doğru işliyor mu?
```

> [!important]  
> **Integration testte hata gördüğümde direkt "kod bozuk" demem. Önce hangi katmanın patladığını bulurum.**

---

# 🧠 Kafaya Kazı

> [!quote]  
> **Unit test parçayı, integration test parçaların birlikte çalışmasını test eder.**

> [!quote]  
> **`connect()` oturum açar, `execute()` SQL'i çalıştırır, `fetch...()` sonucu getirir.**

> [!quote]  
> **Connection database session'dır; çıplak TCP socket değildir.**

> [!quote]  
> **SQL CODE ile USER DATA'yı birbirine karıştırmam.**

> [!quote]  
> **Psycopg parameter binding'de value'ları `%s` ile ayrı gönderirim.**

> [!quote]  
> **Başarı → COMMIT, hata → ROLLBACK.**

> [!quote]  
> **Integration test patladıysa önce failure layer'ı bul.**

---

# 📌 30 Saniyelik Özet

```
Python Repository
        ↓
     Psycopg
        ↓
  PostgreSQL
        ↓
       SQL
        ↓
    Result Set
        ↓
      Python


connect()
→ database session

execute()
→ SQL çalıştır

fetchone()
→ sıradaki row

fetchall()
→ kalan rowlar


SQL CODE
   +
USER DATA
→ BİRLEŞTİRME

SQL TEMPLATE
   +
PARAMETERS
→ Psycopg binding


SUCCESS
→ COMMIT

ERROR
→ ROLLBACK


TEST
→ gerçek PostgreSQL
→ gerçek SQL
→ gerçek result
→ PASS
```

---

# ✅ Günün Kazanımları

-  Unit test ve integration test ayrıldı
    
-  Gerçek PostgreSQL integration mantığı öğrenildi
    
-  Psycopg'un rolü oturdu
    
-  `connect()` / `execute()` / `fetch...()` zinciri öğrenildi
    
-  Connection ve Cursor ayrıldı
    
-  SQL parameter binding öğrenildi
    
-  F-string ile SQL üretmenin problemi anlaşıldı
    
-  `%s`, tuple ve quoting mantığı öğrenildi
    
-  Value ve identifier ayrıldı
    
-  Transaction / COMMIT / ROLLBACK oturdu
    
-  Docker `localhost` / service-name farkı tekrarlandı
    
-  Gerçek test datasıyla repository integration testi yapıldı
    
-  Integration testi iki kez `PASS` verdi
    
-  Integration debugging sırası oluşturuldu
    

---

# 🚀 Gün Sonu

Bugünün en net mental modeli:

> **Python kodumun tek başına doğru olması yetmez. Psycopg, network, PostgreSQL, schema, SQL ve result zincirinin gerçek ortamda birlikte çalıştığını integration test ile kanıtlamam gerekir.**