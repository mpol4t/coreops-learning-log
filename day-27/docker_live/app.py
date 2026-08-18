import sys
from pathlib import Path

data_file = Path("/data/state.txt")

if sys.argv[1] == "write":
    data_file.write_text("ESKI VERI\n")
    print("Veri yazildi:", data_file)

elif sys.argv[1] == "read":
    if data_file.exists():
        print("Bulunan veri:", data_file.read_text())
    else:
        print("VERI BULUNAMADI")
