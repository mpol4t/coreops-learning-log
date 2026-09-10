def classify_rows(rows):
    if len(rows) == 0:
        return "empty"
    elif 1 <= len(rows) <= 9:
        return "normal"
    else:
        return "large"