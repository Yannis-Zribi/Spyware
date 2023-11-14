import time

try:
    for i in range(10):
        print(i)
        time.sleep(1)
except KeyboardInterrupt as e:
    print("ctrl c")
    continue

except Exception as e:
    print("feur")