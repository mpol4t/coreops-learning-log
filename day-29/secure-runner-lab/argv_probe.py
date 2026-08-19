import sys

argüman_sayısı = len(sys.argv) - 1
print("Aldığımız argüman sayısı:", argüman_sayısı)

for x in sys.argv[1:]:
    print(x)