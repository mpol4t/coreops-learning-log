import time
def cleaned_names(names):
    for name in names:
        cleaned = name.strip().lower()

        if cleaned:
            time.sleep(2)
            yield cleaned


source = [
    "  API-01.LOCAL ",
    "",
    " DB-02.LOCAL ",
]

for hostname in cleaned_names(source):
    print(hostname)
