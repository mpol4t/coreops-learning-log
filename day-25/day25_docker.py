import os
import signal
import time

stop_request = False
pid = os.getpid()
ppid = os.getppid()

print("PID:", pid)
print("PPID", ppid)
print("STATE: Running")

def handler(signum,frame):
    global stop_request 
    stop_request = True

signal.signal(signal.SIGTERM, handler)

while stop_request is False:
    time.sleep(1)
    
with open("cleanup.log", "w", encoding="utf-8") as file:
    file.write("Cleanup yapıldı!\n")