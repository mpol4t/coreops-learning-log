def depo_durumu(doluluk):
    if doluluk == 0:
        return "bos"
    elif 0 < doluluk <= 20:
        return "kritik"
    elif 20 < doluluk <= 80:
        return "normal"
    elif 80 < doluluk <= 100:
        return "dolu"
    else:
        raise ValueError

assert depo_durumu(0) == "bos"
assert depo_durumu(20) == "kritik"
assert depo_durumu(80) == "normal"
# assert depo_durumu(100) == "normal" -> AssertionError yükseliyor!
assert depo_durumu(100) == "dolu"
# depo_durumu(101) -> ValueError yükseliyor!
# depo_durumu(-1) -> ValueError yükseliyor!