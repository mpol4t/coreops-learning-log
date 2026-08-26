import os
import time
import sys

print("service started")
print("APP_MODE =", os.environ.get("APP_MODE"))
worker_name = os.environ.get("WORKER_NAME")

if not worker_name:
    print("missing required config: WORKER_NAME")
    sys.exit(1)

print("WORKER_NAME =", worker_name)

time.sleep(5)
