# Git and GitHub Workflow

Bu akış, Git'i yalnız “dosyaları GitHub'a yükleme aracı” olmaktan çıkarıp günlük mühendislik pratiğine dönüştürür.

## 1. Gün başlamadan

```bash
git switch main
git pull --ff-only
git switch -c learn/day-NN-short-topic
```

Örnek:

```bash
git switch -c learn/day-18-json-contract
```

Çift pakette tek branch kullanılabilir:

```bash
git switch -c learn/day-18-19-data-contracts
```

## 2. Çalışırken

Değişiklik sınırını üç görünümle kontrol et:

```bash
git status --short
git diff
git diff --staged
```

- `git diff`: working tree ile index arasındaki fark.
- `git diff --staged`: index ile `HEAD` arasındaki fark.
- Secret, `.env`, büyük ham log veya build çıktısı görürsen commit etmeden dur.

Dosyaları seçerek stage et:

```bash
git add day-NN/README.md day-NN/src day-NN/tests
```

Tüm worktree'yi düşünmeden `git add .` ile stage etmek günlük varsayılan değildir.

## 3. Commit standardı

Normal modülde bir anlamlı commit yeterlidir:

```text
feat(day18): validate JSON input contracts
fix(day18): reject boolean values as integers
test(day18): cover malformed and missing fields
docs(day18): record jq comparison and root cause
```

Bir commit tek açıklanabilir değişim taşımalıdır. Failing test → fix → refactor gerçekten ayrı aşamalarsa birkaç commit kullanılabilir; sırf sayı doldurmak için parçalanmaz.

Commit öncesi:

```bash
git diff --check
python -m compileall -q day-NN
```

Günün kendi test komutu da çalıştırılır.

## 4. Push ve pull request

```bash
git push -u origin HEAD
```

Pull request şu bilgileri taşımalıdır:

- Bugün kazanılan somut yetenek
- Çalıştırılan test/validation komutları
- Bilerek oluşturulan failure mode ve kök neden
- Alınan yardım seviyesi
- Secret veya hassas veri kontrolü

PR ilk çalışma sırasında draft açılabilir. Kanıt ve testler tamamlanınca review için hazır hâle getirilir. Gate günlerinde önceki modüllerin history'si ve açık PR'ları ayrıca kontrol edilir.

## 5. Review sonrası

Merge tamamlandıktan sonra:

```bash
git switch main
git pull --ff-only
git branch -d learn/day-NN-short-topic
```

`main` üzerinde doğrudan günlük çalışma yapma. `--force` push, `reset --hard` veya geçmişi yeniden yazma işlemleri öğrenme programının normal akışı değildir.

## 6. Repository hijyeni

Commit edilmemesi gerekenler:

- `.env`, token, parola ve private key
- `.venv/`, `__pycache__/`, `*.pyc`
- `.DS_Store`, IDE geçici dosyaları
- Büyük ham loglar ve packet capture dosyaları
- Gerçek müşteri/şirket/üçüncü taraf verisi
- Yetkisiz hedef bilgisi

Kanıt gerekiyorsa küçük, redact edilmiş ve yeniden üretilebilir parça kullan.
