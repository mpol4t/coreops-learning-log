# Validation Report — Day 17

## Python

- PASS — `python -m py_compile day17.py`
- PASS — pozitif değer (`25`) → stdout `25`, exit `0`
- PASS — `bad.txt` içeriği `-5` → stderr `Hatalı değer!!`, exit `11`
- PASS — geçersiz integer (`abc`) → stderr `Hatalı değer!!`, exit `11`
- PASS — olmayan dosya → stderr `Girdiğiniz path bulunamadı!!`, exit `22`
- PASS — eksik positional `path` → argparse usage/error, exit `2`

## GitHub temizliği

- Bozuk YAML/frontmatter repo standardına normalize edildi.
- ChatGPT'e özgü `filecite` işaretleri nottan temizlendi.
- `bad.txt` arşivde gerçekten `-5` içerdiği için Docker deneyindeki fixture açıklaması `-5` olarak düzeltildi.
- `__MACOSX` / `._*` artefact'ları pakete alınmadı.
- Kullanıcının `day17.py` kod mantığı değiştirilmedi.

## Docker

Bu çalışma ortamında Docker executable/daemon bulunmadığı için `docker run` deneyi burada yeniden çalıştırılmadı.
Notta kullanılan yaklaşım hazır `python:3.12-slim` image + bind mount olduğu için ayrıca Dockerfile gerekmiyor.
