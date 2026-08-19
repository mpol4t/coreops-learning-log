import subprocess

def run_command(args):
    result = subprocess.run(
                            args, 
                            capture_output=True,
                            text=True
                        )
    return result.returncode, result.stdout, result.stderr

if __name__ == "__main__":
    returncode, stdout, stderr = run_command(["echo", "merhaba mehmet"])

    print("Returncode:", returncode)
    print("Stdout:", stdout.strip())
    print("Stderr:", stderr)
