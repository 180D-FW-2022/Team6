import os
import threading
import time

x = 5
g = 0

def f(x,a):
    global g
    for _ in range(5):
        x = x + 1
        print(a, " ",x)
        g = x
        time.sleep(0.01)

def h(x,a):
    for _ in range(5):
        # x = x + 1
        # print(a, " ",x)
        global g 
        print(g)
        time.sleep(0.01)

    

if __name__ == "__main__":
    time_start = time.time()

    t1 = threading.Thread(target=f, args=(x,"f"))
    t2 = threading.Thread(target=h, args=(g,"h"))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    time_end = time.time()

    print(f"Time elapsed: {round(time_end - time_start, 2)}s")
