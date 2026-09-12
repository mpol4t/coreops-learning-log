---
title: "Gün 43 — systemd Execution Context, Journal ve Permission Debugging"
tags:
  - coreops
  - day43
  - systemd
  - journalctl
  - linux
  - permissions
  - debugging
  - services
aliases:
  - "Gün 43 systemd Journal Permission Debugging"
status: completed
---

# ⚙️ systemd — Execution Context, Journal & Permission Debugging

> [!abstract] 🎯 Ana fikir
> Bugün systemd'nin sadece bir programı başlatmadığını; process'in **hangi kullanıcıyla, hangi klasörde, hangi environment ile ve hangi executable üzerinden** çalışacağını da belirlediğini öğrendim.
>
> Sonra journal üzerinden servisin davranışını takip edip bilinçli bir permission hatasını kanıtlarla teşhis ettim.

---

# 🧠 systemd Execution Context

Bir service process'i için dört temel soru:

    ExecStart=
    → NE çalışacak?

    User=
    → KİM olarak çalışacak?

    WorkingDirectory=
    → NEREDE çalışacak?

    Environment=
    → HANGİ config ile çalışacak?

Mental model:

    .service
       ↓
    systemd
       ↓
    execution context
       ↓
    User
    WorkingDirectory
    Environment
    ExecStart
       ↓
    process

Örneğin:

    [Service]
    User=polat
    WorkingDirectory=/opt/coreops-v4-03
    Environment=APP_MODE=systemd-lab
    ExecStart=/usr/bin/python3 /opt/coreops-v4-03/app.py

şu anlama geliyor:

    kullanıcı → polat
    CWD      → /opt/coreops-v4-03
    config   → APP_MODE=systemd-lab
    process  → python3 app.py

---

# 🔄 `daemon-reload` vs `restart`

Buradaki ayrımı netleştirdim:

    .service dosyası değişti
            ↓
      daemon-reload
            ↓
    systemd yeni config'i öğrendi
            ↓
         restart
            ↓
    yeni context ile yeni process

Ama yalnızca:

    app.py

gibi application code değiştiyse genellikle:

    restart

yeterli.

> [!important]
> **`daemon-reload` systemd'nin unit bilgisini günceller.**
>
> **`restart` ise yeni process oluşturur.**

Çalışan eski process'in environment'ı unit dosyasını değiştirdiğim anda sihirli şekilde değişmiyor.

---

# 🌍 Environment Lab

Yeni config olarak:

    RUN_LABEL=day42

ekledim.

İlk düşüncem unit içine direkt:

    RUN_LABEL=day42

yazmaktı.

Bu eksikti.

Doğrusu:

    Environment=RUN_LABEL=day42

Akış:

    .service
       ↓
    Environment=RUN_LABEL=day42
       ↓
    systemd
       ↓
    process environment
       ↓
    os.environ.get("RUN_LABEL")
       ↓
    day42

Process çıktısında:

    uid=1000
    cwd=/opt/coreops-v4-03
    APP_MODE=systemd-lab
    RUN_LABEL=day42

görerek context'in gerçekten uygulandığını doğruladım.

Ayrıca:

    systemctl show ...

ile systemd tarafındaki config'i de kontrol ettim.

Yani iki farklı kanıtım vardı:

    systemctl show
    → systemd ne ayarladı?

    process çıktısı
    → process gerçekte ne gördü?

---

# ▶️ `start` vs `enable`

Bunu da karıştırmamam gerekiyor:

    start
    → servisi ŞİMDİ çalıştır

    enable
    → boot/target zincirine bağla

Bu yüzden aynı anda:

    disabled
    active (running)

görmek mümkündür.

Servis şu anda çalışıyor olabilir ama boot için enable edilmemiş olabilir.

`WantedBy=multi-user.target` da tek başına enable anlamına gelmez.

    WantedBy=
    → enable edilirse nereye bağlanacağını tarif eder

    systemctl enable
    → bağlantıyı gerçekten oluşturur

---

# 📜 Journal Mental Modeli

systemd service'in normal terminali olmadığı için programın stdout/stderr çıktıları journal'a gider.

    Python process
       │
       ├── stdout
       └── stderr
            ↓
    systemd-journald
            ↓
         journal
            ↓
       journalctl
            ↓
           ben

Ayrım:

    journald
    → logları toplar

    journal
    → kayıtların tutulduğu yer

    journalctl
    → kayıtları okur / filtreler

---

# 🔎 `journalctl` Filtreleri

| İhtiyaç | Filtre |
|---|---|
| Hangi servis? | `-u` |
| Hangi zamandan beri? | `--since` |
| Kaç kayıt? | `-n` |
| Canlı takip? | `-f` |
| Pager istemiyorum | `--no-pager` |
| Bu boot | `-b` |

Örneğin:

    journalctl \
      -u coreops-v4-03.service \
      --since "5 minutes ago" \
      --no-pager

Mental model:

    -u
    → KİM?

    --since
    → NE ZAMANDAN BERİ?

    -n
    → KAÇ KAYIT?

    -f
    → CANLI MI?

> [!warning]
> `-n 20`
>
> **son 20 dakika değil, son 20 kayıttır.**

---

# 🆚 `status` vs `journalctl`

    systemctl status
    → NE OLDU?

    journalctl
    → NEDEN OLDU?

`status` bana:

- active / failed
- PID
- exit code
- birkaç yakın log

gibi hızlı durum bilgileri verir.

Gerçek hata araştırmasında:

    journalctl -u ...

ile journal'a inerim.

---

# 💣 Permission Broken Case

Önce çalışan bir baseline oluşturdum.

Dosya:

    runtime.conf

Durum:

    root:root 644

Service:

    User=polat

`644`:

    owner  → rw-
    group  → r--
    others → r--

`polat`, owner veya root group olmadığı için:

    others = r--

üzerinden dosyayı okuyabiliyordu.

Sonuç:

    config=worker-mode=active
    service active ✅

---

# 🔥 Sistemi Bilerek Bozdum

Permission'ı:

    644

yerine:

    600

yaptım.

Yeni durum:

    -rw------- root root

Yani:

    owner  → rw-
    group  → ---
    others → ---

Service hâlâ:

    User=polat

olduğu için artık dosyayı okuyamadı.

Akış:

    systemd
       ↓
    User=polat
       ↓
    app.py
       ↓
    open(runtime.conf)
       ↓
    root:root 600
       ↓
    read permission yok
       ↓
    PermissionError 💥
       ↓
    Python exit 1
       ↓
    service failed

Journal'da gerçek hata:

    PermissionError:
    [Errno 13] Permission denied

olarak göründü.

---

# 🧠 Sebep vs Sonuç

Buradaki kritik ayrım:

    Active: failed

ve:

    status=1/FAILURE

**root cause değil.**

Bunlar sonuç.

Gerçek zincir:

    PermissionError
          ↓
    process başarısız
          ↓
       exit 1
          ↓
    systemd unit failed

> [!danger]
> **`service failed` gördüğümde "systemd bozuk" demeyeceğim.**
>
> Soracağım:
>
> **Process neden başarısız oldu?**

---

# 🔬 Evidence Üçlüsü

Permission problemini üç ayrı kanıtla doğruladım.

### 1. Application

    journalctl
       ↓
    PermissionError

### 2. Filesystem

    ls -l runtime.conf
       ↓
    root:root 600

### 3. Process identity

    systemctl show SERVICE -p User
       ↓
    User=polat

Üçünü birleştirince:

    process = polat
          +
    file = root:root 600
          +
    read sırasında PermissionError
          ↓
    ROOT CAUSE
    filesystem permission

Teşhis:

    last_known_good:
    root:root 644
    service active

    first_failed_operation:
    runtime.conf read

    error_type:
    PermissionError

    failure_boundary:
    application startup / filesystem access

---

# 🐞 Yaptığım Hatalar

## 1. Permission'ı group üzerinden aldığımı sandım

Yanlış düşündüm:

    root:root 644
    ↓
    polat group read kullanıyor

Hayır.

`polat` root grubunda olmadığı için kullandığı:

    others = r--

idi.

Doğru permission seçim mantığı:

    owner eşleşiyor mu?
         ↓
       evet → owner bits

    değilse group eşleşiyor mu?
         ↓
       evet → group bits

    değilse
         ↓
       others bits

---

## 2. "Okuma, açma, çalıştırma yetkisi gitti" dedim

Fazla genel söyledim.

Bu case'te ihtiyacım olan şey:

    read (r)

permission'ıydı.

Config dosyasının executable (`x`) olmasına ihtiyacım yoktu.

Doğru teşhis:

> **Service user'ın dosyaya read permission'ı yok.**

---

## 3. `failed` durumunu hata sebebi gibi düşündüm

Yanlış:

    service failed
    → sebep

Doğru:

    gerçek hata
       ↓
    process failed
       ↓
    service failed

---

## 4. Permission sorununu `777` ile çözmek

Bu **TIRT**.

    chmod 777

problemi çözebilir ama gereksiz yetki dağıtır.

Doğru soru:

> Kim erişecek?  
> Ne yapması gerekiyor?  
> Bunun için minimum permission ne?

---

# 🔐 Minimum Fix

Service'in ihtiyacı yalnızca dosyayı okumaktı.

Bu yüzden:

    root:polat 640

kullandım.

`640`:

    owner root   → rw-
    group polat  → r--
    others       → ---

Sonuç:

    service user
       ↓
    group read
       ↓
    runtime.conf okunuyor
       ↓
    config=worker-mode=active
       ↓
    service active ✅

Bu:

> **Principle of Least Privilege**

mantığı.

Gerektiği kadar yetki, fazlası değil.

---

# 🧪 İkinci Bağımsız Case

Aynı çözümü ezberden uygulamadığımı görmek için:

    labels.txt

dosyasıyla aynı mekanizmayı tekrar test ettim.

Dosyayı:

    root:root 600

yaptım.

Journal sırası:

    config=worker-mode=active ✅
           ↓
    labels.txt read
           ↓
    PermissionError ❌

Bu bana ilk başarısız operasyonu net gösterdi:

    runtime.conf read ✅
    labels.txt read   ❌

Yani failure boundary:

    application startup
           ↓
    labels.txt filesystem access

Sonra yine minimum fix:

    root:polat 640

uyguladım.

Final journal:

    config=worker-mode=active
    label=production-label

✅ İki filesystem dependency de başarıyla geçti.

---

# 🧭 Bundan Sonraki Debug Sıram

    last known good
          ↓
    ne değişti?
          ↓
       failure
          ↓
    first failed operation
          ↓
      error type
          ↓
    supporting evidence
          ↓
    failure boundary
          ↓
     minimum fix
          ↓
       restart
          ↓
    başarı kanıtı

> [!important]
> **Debug = rastgele komut basmak değil.**
>
> **İlk başarısız operasyonu bulup evidence ile root cause'u kanıtlamak.**

---

# 🧠 Kafaya Kazı

> [!tip]
> **ExecStart = ne çalışacak?**

> [!tip]
> **User = kim olarak?**

> [!tip]
> **WorkingDirectory = nerede?**

> [!tip]
> **Environment = hangi config ile?**

> [!tip]
> **Unit değişti → daemon-reload + restart.**

> [!tip]
> **Application code değişti → genelde restart yeterli.**

> [!tip]
> **status → ne oldu?**

> [!tip]
> **journalctl → neden oldu?**

> [!tip]
> **`failed` root cause değildir.**

> [!tip]
> **Permission debug = process user + file mode/owner + application error.**

> [!tip]
> **777 basma; minimum gerekli permission'ı ver.**

---

# 📌 30 Saniyelik Özet

    .service
       ↓
    systemd
       ↓
    execution context
       ↓
    process


    STATUS
      ↓
    ne oldu?


    JOURNAL
      ↓
    neden oldu?


    User=polat
       +
    root:root 600
       +
    open(file)
       ↓
    PermissionError
       ↓
    exit 1
       ↓
    service failed


    FIX
       ↓
    root:polat 640
       ↓
    yalnızca gerekli READ
       ↓
    service active ✅

---

# ✅ Günün Kazanımları

- [x] systemd execution context mantığını oturttum
- [x] `ExecStart`, `User`, `WorkingDirectory`, `Environment` ayrımını öğrendim
- [x] `daemon-reload` ve `restart` farkını ayırdım
- [x] Environment değerini process içinde doğruladım
- [x] `start` ve `enable` farkını tekrar ettim
- [x] journald / journal / journalctl ayrımını öğrendim
- [x] `-u`, `--since`, `-n`, `-f`, `-b`, `--no-pager` filtrelerini kullandım
- [x] `status` ile `journalctl` farkını oturttum
- [x] Çalışan baseline oluşturdum
- [x] Permission'ı bilerek bozup gerçek failure ürettim
- [x] `PermissionError` root cause'unu buldum
- [x] `failed` ile root cause arasındaki farkı gördüm
- [x] Linux owner / group / others seçim mantığını düzelttim
- [x] Evidence üçlüsüyle teşhis yaptım
- [x] Failure boundary çıkardım
- [x] `777` yerine least privilege ile `640` kullandım
- [x] Aynı problemi ikinci dosyada bağımsız olarak tekrar çözdüm

---

# 🚀 Gün Sonu

> **Bugün systemd'de sadece service başlatmayı değil, process'in hangi context ile çalıştığını doğrulamayı; journal üzerinden ilk başarısız operasyonu bulmayı ve permission hatasını minimum yetkiyle düzeltmeyi öğrendim.**