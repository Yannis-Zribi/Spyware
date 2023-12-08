import time
from threading import Thread


def fill_file():

    with open("./file", "a") as f:
            
        for i in range(10):
            f.write(f"{i}-")
            time.sleep(1)



def print_file():

    with open("./file", "r") as file:
        for i in range(10):
            print(file.read())
            time.sleep(1)




t1 = Thread(target=fill_file, args=())

t1.start()

t2 = Thread(target=print_file, args=())

t2.start()

t1.join()
t2.join()


