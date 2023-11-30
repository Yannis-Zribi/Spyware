import psutil
import setproctitle
import time
import signal



def get_proc_name():
    procs_name = []

    for proc in psutil.process_iter():
        procs_name.append(proc.name())

    return procs_name



def set_proc_name():

    base_name = "SpywareServer"
    i = 0
    procs_name = get_proc_name()

    while f"{base_name}{i}" in procs_name:
        i+=1

    setproctitle.setproctitle(f"{base_name}")

set_proc_name()
print(setproctitle.getproctitle())

try:
    while True:
        time.sleep(1)
    
except:
    exit()