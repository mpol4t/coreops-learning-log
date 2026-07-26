def kargo_ucreti(sepet_tutari):
    sepet_tutari = float(sepet_tutari)

    if sepet_tutari < 0:
        raise ValueError("Sepet tutarı negatif olamaz!")

    if sepet_tutari >= 500:
        return sepet_tutari

    return sepet_tutari + 49.90


print(kargo_ucreti(0))      # 49.9
print(kargo_ucreti(500))    # 500.0

try:
    print(kargo_ucreti(-1))
except ValueError:
    print("ValueError")