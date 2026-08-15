import json
import os
import argparse

timeout = 30

if os.path.isfile("config.json"):
    with open("config.json", encoding="utf-8") as file:
        içerik = json.load(file)
        if "timeout" in içerik:
            timeout = içerik["timeout"]

app_timeout = os.getenv("APP_TIMEOUT")
if app_timeout is not None:
    timeout = int(app_timeout)
    

parser = argparse.ArgumentParser()
parser.add_argument("--timeout", type=int)
args = parser.parse_args()
if args.timeout is not None:
    timeout = args.timeout
    
print(timeout)

