import subprocess

payload = 'safe;touch MARKER'

subprocess.run("echo " + payload, shell=True)