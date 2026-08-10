from pathlib import Path


def scanner(root):
    root = Path(root)

    if not root.exists():
        raise FileNotFoundError

    if not root.is_dir():
        raise NotADirectoryError

    dosyalar = []

    for path in sorted(root.rglob("*.txt")):
        if path.is_file():
            relative = path.relative_to(root)
            dosyalar.append(relative)

    return dosyalar
