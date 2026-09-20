def normalize_hostname(value):
    hostname = value.strip().lower()

    if not hostname:
        raise ValueError("hostname is required")

    return hostname
