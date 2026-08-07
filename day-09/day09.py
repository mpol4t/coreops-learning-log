import os
import sys
import stat

def izin_okuma(dosya):
    bilgi = os.stat(dosya)
    uid = bilgi.st_uid
    gid = bilgi.st_gid
    mode= stat.S_IMODE(bilgi.st_mode)
    
    return uid, gid, mode

def main():
    for dosya in ["data.txt", "asd.txt"]:
        try:
            uid, gid, mode= izin_okuma(dosya)
            print(f"Kullanıcı UID: {uid}")
            print(f"Kullanıcı GID: {gid}")
            print(f"Dosyanın sahiplik bitleri: {mode}")
            
        except FileNotFoundError as hata:
            print(f"Dosya okunurken bir hata meydana geldi: {hata}", file=sys.stderr)

if __name__ == "__main__":
    sys.exit(main())        
