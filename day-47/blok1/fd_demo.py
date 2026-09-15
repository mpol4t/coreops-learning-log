from pathlib import Path
import os

path = Path("/home/polat/Masaüstü/coreops-learning/coreops-fd-demo.txt")
path2 = Path("/home/polat/Masaüstü/coreops-learning/coreops-fd-secont.txt")

with path.open("a+", encoding="utf-8") as file1, \
     path2.open("a+", encoding="utf-8") as file2:
        print(f"pid={os.getpid()}")
        print(f"First fd={file1.fileno()}")
        print(f"Second fd={file2.fileno()}")

        input("Dosya açık kapatmak için enter...")

