import os 
import sys

if os.getenv("APP_MODE"):
    app_mode = os.getenv("APP_MODE")
    print(f"APP_MODE: {app_mode}")
else:
    print("Gerekli configuraiton environment değeri bulunamadı!", file=sys.stderr)
    sys.exit(1)

if os.getenv("API_TOKEN"):
    
    print("API_TOKEN mevcut!")
else:
    print("API_TOKEN eksik!")

