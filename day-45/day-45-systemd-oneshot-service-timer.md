---
title: "Gün 45 — systemd Oneshot Service + Timer"
tags:
  - coreops
  - day45
  - systemd
  - service
  - timer
  - oneshot
  - journalctl
  - linux
aliases:
  - "Gün 45 systemd Oneshot Service Timer"
status: completed
---

# Systemd — Oneshot Service + Timer

## Ne yaptık?

Bugün `systemd` üzerinde iki şeyi birleştirdim:

- Bir işi çalıştırıp biten **oneshot service** yazdım.
    
- Bu service'i belirli bir süre sonra otomatik çalıştıran **systemd timer** yazdım.
    

Temel mantık:

```
.timer
  ↓ zamanı gelince
.service
  ↓
ExecStart
  ↓
Python script
  ↓
işini yapar ve biter
```

Buradaki önemli ayrım:

- `.service` → **ne çalışacak?**
    
- `.timer` → **ne zaman çalışacak?**
    

---

# 1. Çalıştırılacak Python işi

Önce systemd olmadan çalışan basit bir Python script'im vardı.

Örnek konum:

```
/opt/coreops-report/report.py
```

Script'in amacı basit bir rapor üretmekti.

Systemd'ye geçmeden önce bunu direkt:

```
python3 report.py
```

ile çalıştırıp kodun kendi başına düzgün çalıştığını doğruladım.

Bu önemli çünkü program zaten bozuksa sonradan systemd hatasıyla uygulama hatasını birbirine karıştırabilirim.

---

# 2. Service dosyası

Kendi system-wide unit dosyamı şuraya koydum:

```
/etc/systemd/system/coreops-report.service
```

Örnek yapı:

```
[Unit]
Description=CoreOps report job

[Service]
Type=oneshot
User=ubuntu
WorkingDirectory=/opt/coreops-report
Environment=REPORT_MODE=lab
ExecStart=/usr/bin/python3 /opt/coreops-report/report.py

[Install]
WantedBy=multi-user.target
```

## Bölümlerin anlamı

### `[Unit]`

Unit hakkında genel bilgiler.

```
Description=CoreOps report job
```

Servisin ne olduğunu açıklıyor.

---

### `Type=oneshot`

```
Type=oneshot
```

Bu service sürekli çalışan daemon değil.

Mantığı:

```
başla
↓
işi yap
↓
exit
↓
bitti
```

Yani oneshot service çalıştıktan sonra sürekli `active (running)` durumda kalmak zorunda değil.

Benim Python rapor işi için uygun model buydu.

---

### `User=`

```
User=ubuntu
```

Python process'inin hangi Linux kullanıcısıyla çalışacağını belirliyor.

Önemli:

```
sudo systemctl start ...
```

kullanmam, Python uygulamasının root çalıştığı anlamına gelmiyor.

Runtime kullanıcısını `User=` belirliyor.

---

### `WorkingDirectory=`

```
WorkingDirectory=/opt/coreops-report
```

Process'in çalışma dizinini belirliyor.

Terminalde kabaca:

```
cd /opt/coreops-report
```

yapmışım gibi düşünebilirim.

Python içinde:

```
os.getcwd()
```

ile bunu görebiliyorum.

---

### `Environment=`

```
Environment=REPORT_MODE=lab
```

Process'e environment variable veriyor.

Python tarafından:

```
os.environ.get("REPORT_MODE")
```

ile okunabiliyor.

Sonradan farklı environment değerleri ekleyip service'in yeni process'e bunları verdiğini de gördüm.

---

### `ExecStart=`

```
ExecStart=/usr/bin/python3 /opt/coreops-report/report.py
```

Asıl çalışacak process burada belirtiliyor.

Mantık:

```
systemd
↓
/usr/bin/python3
↓
report.py
```

---

# 3. Service'i systemd'ye tanıtmak

`.service` dosyasını yazmak tek başına yetmiyor.

Unit dosyasını oluşturduktan veya değiştirdikten sonra:

```
sudo systemctl daemon-reload
```

çalıştırdım.

Mantığı:

```
.service dosyası değişti
↓
daemon-reload
↓
systemd yeni unit tanımını okudu
```

## Önemli ayrım

```
daemon-reload ≠ restart
```

`daemon-reload`:

> systemd unit tanımlarını tekrar oku.

`restart`:

> çalışan process'i yeniden başlat.

---

# 4. Service'i çalıştırmak

Service'i manuel olarak çalıştırmak için:

```
sudo systemctl start coreops-report.service
```

Durumunu görmek için:

```
systemctl status coreops-report.service --no-pager
```

Kayıtlarını görmek için:

```
sudo journalctl \
  -u coreops-report.service \
  -n 20 \
  --no-pager
```

Python'ın `print()` çıktılarının journal'a geldiğini gördüm.

Yani evidence zinciri:

```
.service
↓
systemd
↓
ExecStart
↓
Python
↓
journal
```

---

# 5. start / enable farkı

Bu ayrımı özellikle öğrendim.

## start

```
sudo systemctl start coreops-report.service
```

Anlamı:

> Servisi şimdi çalıştır.

---

## enable

```
sudo systemctl enable coreops-report.service
```

Anlamı:

> `[Install]` bölümüne göre unit'i systemd'nin gelecekteki activation/boot mekanizmasına bağla.

Yani:

```
start ≠ enable
```

Bir service:

```
started + disabled
```

veya:

```
stopped + enabled
```

olabilir.

İkisini birlikte yapmak istersem:

```
sudo systemctl enable --now coreops-report.service
```

kullanılabilir.

---

# 6. Temel systemctl komutları

```
sudo systemctl daemon-reload
```

Unit dosyalarını tekrar okut.

```
sudo systemctl start SERVIS
```

Şimdi çalıştır.

```
sudo systemctl stop SERVIS
```

Durdur.

```
sudo systemctl restart SERVIS
```

Yeniden başlat.

```
systemctl status SERVIS
```

Runtime durumunu gör.

```
sudo systemctl enable SERVIS
```

Boot/activation bağlantısını oluştur.

```
sudo systemctl disable SERVIS
```

Enable bağlantısını kaldır.

```
systemctl is-enabled SERVIS
```

Enable durumunu gör.

```
journalctl -u SERVIS
```

Servis loglarını gör.

---

# 7. Timer kısmı

Service çalışınca timer'a geçtim.

Timer dosyası:

```
/etc/systemd/system/coreops-report.timer
```

Örnek:

```
[Unit]
Description=Run CoreOps report after timer starts

[Timer]
OnActiveSec=30s

[Install]
WantedBy=timers.target
```

---

# `OnActiveSec`

```
OnActiveSec=30s
```

şu anlama geliyor:

> Timer aktive edildikten 30 saniye sonra ilişkili service'i çalıştır.

Burada Python script'i timer çalıştırmıyor.

Zincir:

```
coreops-report.timer
↓
30 saniye
↓
coreops-report.service
↓
ExecStart
↓
report.py
```

---

# 8. Timer ile service nasıl eşleşti?

Dosyalar:

```
coreops-report.timer
coreops-report.service
```

aynı basename'e sahip.

Bu yüzden timer varsayılan olarak:

```
coreops-report.service
```

unit'ini aktive ediyor.

Yani timer'ın görevi:

```
ne zaman?
```

Service'in görevi:

```
ne çalışacak?
```

---

# 9. Timer'ı çalıştırmak

Timer dosyasını yazdıktan sonra:

```
sudo systemctl daemon-reload
```

çalıştırdım.

Ardından timer'ı aktive ettim:

```
sudo systemctl start coreops-report.timer
```

Burada önemli nokta:

```
systemctl start coreops-report.service
```

demedim.

Service'i artık **timer tetikliyor**.

---

# 10. Timer'ı kontrol etmek

Durum:

```
systemctl status coreops-report.timer --no-pager
```

Asıl güzel kontrol:

```
systemctl list-timers coreops-report.timer
```

Burada kabaca:

```
NEXT
LEFT
LAST
UNIT
ACTIVATES
```

alanlarını görebiliyorum.

Özellikle:

```
ACTIVATES
```

bana timer'ın hangi service'i çalıştıracağını gösteriyor.

Mental model:

```
coreops-report.timer
        ↓
ACTIVATES
        ↓
coreops-report.service
```

---

# 11. Timer gerçekten çalıştırdı mı?

Timer'ın aktif görünmesi tek başına yetmez.

Asıl Python işi gerçekten çalışmış mı diye service journal'ına baktım:

```
sudo journalctl \
  -u coreops-report.service \
  -n 20 \
  --no-pager
```

Burada yeni timestamp / rapor çıktısını gördüm.

Yani kanıt:

```
timer schedule vardı
↓
zaman geldi
↓
service tetiklendi
↓
Python çalıştı
↓
yeni output oluştu
```

---

# 12. Timer ve service logları farklı

Timer logu:

```
journalctl -u coreops-report.timer
```

Service logu:

```
journalctl -u coreops-report.service
```

Fark:

```
.timer
→ scheduling / activation tarafı

.service
→ uygulamanın gerçek execution tarafı
```

Bir iş neden çalışmadı diye bakarken bu ayrım önemli.

---

# 13. Timer süresini değiştirdim

Önce:

```
OnActiveSec=30s
```

kullandım.

Sonra:

```
OnActiveSec=45s
```

ve bağımsız varyant olarak daha farklı bir süre uyguladım.

Dosyayı değiştirdikten sonra sadece kaydetmek yetmedi.

Uyguladığım mantık:

```
timer unit değişti
↓
aktif timer'ı durdur
↓
daemon-reload
↓
timer'ı tekrar başlat
↓
list-timers ile doğrula
```

Komut mantığı:

```
sudo systemctl stop coreops-report.timer
sudo systemctl daemon-reload
sudo systemctl start coreops-report.timer
```

Sonra:

```
systemctl list-timers coreops-report.timer
```

ile yeni schedule'ın runtime'a geçtiğini doğruladım.

---

# 14. Timer için enable

Timer'ı:

```
sudo systemctl start coreops-report.timer
```

ile başlatırsam bu runtime aktivasyonu.

Boot sonrası systemd tarafından tekrar devreye alınmasını istersem:

```
sudo systemctl enable coreops-report.timer
```

kullanabilirim.

Yine aynı ayrım:

```
start
→ şimdi

enable
→ sonraki systemd activation/boot ilişkisi
```

Bugünkü labda enable ilişkisini de gözlemledim.

---

# 15. Benim çıkardığım ana mental model

```
Python işi
   ↓
ExecStart
   ↓
.service
   ↑
.timer
   ↑
schedule
```

Biraz daha detaylı:

```
.timer
│
│ zaman geldi
▼
.service
│
│ ExecStart
▼
Python process
│
│ işini yapar
▼
exit
```

Oneshot olduğu için process sürekli yaşamıyor.

Timer'ın aktif olması da Python'ın sürekli çalıştığı anlamına gelmiyor.

---

# En önemli farklar

## `.service` vs `.timer`

```
.service = NE çalışacak?
.timer   = NE ZAMAN çalışacak?
```

## `daemon-reload` vs `restart`

```
daemon-reload
→ systemd unit tanımını yeniden oku

restart
→ process lifecycle'ını yeniden başlat
```

## `start` vs `enable`

```
start
→ şimdi aktive et

enable
→ boot/target activation bağlantısını oluştur
```

## long-running service vs oneshot

```
long-running:
start → process sürekli çalışır

oneshot:
start → işi yap → exit
```

---

# Kullanışlı komut özeti

### Service

```
sudo systemctl daemon-reload

sudo systemctl start coreops-report.service
sudo systemctl stop coreops-report.service
sudo systemctl restart coreops-report.service

systemctl status coreops-report.service --no-pager

sudo journalctl \
  -u coreops-report.service \
  -n 20 \
  --no-pager
```

### Enable

```
sudo systemctl enable coreops-report.service
sudo systemctl disable coreops-report.service

systemctl is-enabled coreops-report.service
```

### Timer

```
sudo systemctl start coreops-report.timer

systemctl status coreops-report.timer --no-pager

systemctl list-timers coreops-report.timer

sudo journalctl \
  -u coreops-report.timer \
  -n 20 \
  --no-pager
```

### Timer config değişince

```
sudo systemctl stop coreops-report.timer
sudo systemctl daemon-reload
sudo systemctl start coreops-report.timer

systemctl list-timers coreops-report.timer
```

---

# Kendime kısa özet

Bugün systemd'de **oneshot bir işi service olarak tanımlamayı ve timer ile zamanlamayı** öğrendim.

Service tarafında `User`, `WorkingDirectory`, `Environment` ve `ExecStart` ile process'in execution context'ini belirledim. Unit değiştiğinde `daemon-reload`, çalıştırmak için `start`, boot ilişkisi için `enable` gerektiğini ayırdım.

Timer tarafında `.timer` dosyasının programı doğrudan çalıştırmadığını; zamanı geldiğinde ilgili `.service` unit'ini aktive ettiğini gördüm. `OnActiveSec` ile farklı süreler denedim, `list-timers` ile runtime schedule'ı ve `journalctl` ile gerçek service execution'ını doğruladım.

## Tek cümlelik ezber

> **Service neyin/nasıl çalışacağını, timer ise ne zaman çalıştırılacağını belirler.**