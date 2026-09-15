from pathlib import Path
path = Path("/tmp/coreops-strace/input.txt")
print(path.read_text(encoding="utf-8"))
